import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from os import listdir, makedirs
from os.path import join, exists
import json
import pickle
import argparse
from copy import deepcopy
from scipy.spatial.distance import pdist, squareform

###########################################
# for Docker
#from pyclusterbdm.algorithms import H2SOM
#import pyclusterbdm.core as core
###########################################
# For testing
#from pycluster.algorithms import H2SOM
#import pycluster.core as core
from pyclusterbdmseed.algorithms import H2SOM
import pyclusterbdmseed.core as core
############################################

path_to_dataset = 'datasets/'
path_to_json = 'json/'
path_to_h2som_data = 'h2som/'


h5 = '.h5'

def plot_poincare_structure(h2som):
    plt.plot(h2som._pos[:,0], h2som._pos[:,1], "ro")
    tuples = []
    for key, vals in h2som._childs.items():
        tuples = tuples + [(key, v) for v in vals]
    tuples = np.array(tuples)
    for tup in tuples:
        pos1 = h2som._pos[tup[0]]
        pos2 = h2som._pos[tup[1]]
        pos = list(zip(pos1, pos2))
        plt.plot(pos[0], pos[1])
    plt.show()



# Reads hdf5 file and returns a numpy array
def read_data(path):
    dframe = pd.read_hdf(path)
    # Rows = pixel, Columns = m/z channels
    data = dframe.values
    #print(data.shape)
    return dframe, data


def calc_h2som(data, eps, sig, niter):
    ### Important H2SOM Properties
    ## hierachical ring index intervals
    # print(h2som._rings)
    # Child node indices of each node as dict. Key = node, value = list of child indices.
    # Indices which are not included: parent index, index of both same level hierarchy neighbors
    ## 2D positions in on poincare disc
    # print(h2som._pos)
    ## Cluster Centroids
    #print(h2som._centroids.shape)
    ## H2SOM Parameters
    # Sigma: Neihborhood bell function [start_value, decrease_value]
    # Epsilon: Learning step size [start_value, decrease_value]
    # Learning steps based on n_iter
    # For each step (n_iter) the neighborhood (sigma) and learning step size (epsilon)
    # will decrease to allow for more and more specialization and fine tuning.
    # Therefore sigma and epsilon decrease value depend strongly on n_iter!
    # H2SOM initialization
    h2som = H2SOM(data, epsilon=[float(eps[0]), float(eps[1])], sigma=[float(sig[0]), float(sig[1])], n_iter=float(niter))
    # H2SOM training
    h2som.cluster()
    return h2som


def position_optimization(h2som, prototypes, variant, ring):
    def posdist_adjust(dist):
        return 1/(1+dist)
    h2som_cp = deepcopy(h2som)
    distances = 1 - squareform(pdist(prototypes, metric="correlation"))
    # Consider only distances of neighboring prototypes
    dist = np.diag(distances, k=1)
    # add last proto to first proto distance
    dist = np.append(dist,distances[0][-1])
    # Neighbors from the other side
    dist_rev = np.roll(dist,1)
    changes = []
    for i, d in enumerate(dist):
        ring_start = h2som_cp._rings[ring-1][0]
        ring_end = h2som_cp._rings[ring-1][1]+1
        pos_in_ring = h2som_cp._pos[ring_start:ring_end]
        d_next = d
        d_prev = dist_rev[i]
        if variant in ["winnertakeall", "winnertakealldulled"]:
            # A: let only the stronger similarity drag
            if d_next > d_prev:
                if i == len(dist)-1:
                    j = 0
                else:
                    j = i+1

                pos_dist = np.sqrt(((pos_in_ring[j] - pos_in_ring[i])**2).sum())
                if variant == "winnertakealldulled":
                    dullfactor = posdist_adjust(pos_dist)
                else:
                    dullfactor = 1

                if d_next < posdist_adjust(pos_dist):
                    change = np.array([0,0])
                else:
                    change = (pos_in_ring[j] - pos_in_ring[i]) * d_next * dullfactor
            else:
                if i == 0:
                    j = len(dist)-1
                else:
                    j = i-1

                pos_dist = np.sqrt(((pos_in_ring[j] - pos_in_ring[i])**2).sum())
                if variant == "winnertakealldulled":
                    dullfactor = posdist_adjust(pos_dist)
                else:
                    dullfactor = 1

                if d_prev < posdist_adjust(pos_dist):
                    change = np.array([0,0])
                else:
                    change = (pos_in_ring[j] - pos_in_ring[i]) * d_prev * dullfactor

        elif variant in ["tugofwar", "tugofwardulled"]:
            # B: let both forces drag against each other
            if i == 0:
                j = i+1
                k = len(dist)-1
            elif i == len(dist)-1:
                j = 0
                k = i-1
            else:
                j = i+1
                k = i-1

            pos_dist_ij = np.sqrt(((pos_in_ring[j] - pos_in_ring[i])**2).sum())
            pos_dist_ik = np.sqrt(((pos_in_ring[k] - pos_in_ring[i])**2).sum())
            if variant == "tugofwardulled":
                dullfactor_ij = posdist_adjust(pos_dist)
                dullfactor_ik = posdist_adjust(pos_dist)
            else:
                dullfactor_ij = 1
                dullfactor_ik = 1

            if d_next < posdist_adjust(pos_dist_ij):
                change_next = np.array([0,0])
            else:
                change_next = (pos_in_ring[j] - pos_in_ring[i]) * d_next * dullfactor_ij

            if d_prev < posdist_adjust(pos_dist_ik):
                change_prev = np.array([0,0])
            else:
                change_prev = (pos_in_ring[k] - pos_in_ring[i]) * d_prev * dullfactor_ik

            change = [change_next, change_prev]

        else:
            raise ValueError("Wrong variant!")

        changes.append(change)

    changes = np.array(changes)

    if variant in ["winnertakeall", "winnertakealldulled"]:
        h2som_cp._pos[ring_start:ring_end] = h2som_cp._pos[ring_start:ring_end] + (changes/2)
    elif variant in ["tugofwar", "tugofwardulled"]:
        h2som_cp._pos[ring_start:ring_end] = h2som_cp._pos[ring_start:ring_end] + (np.array(changes)[:,0,:]/2)
        h2som_cp._pos[ring_start:ring_end] = h2som_cp._pos[ring_start:ring_end] + (np.array(changes)[:,1,:]/2)

    return h2som_cp, np.sum(np.abs(changes))


def calc_memb(data, h2som, ring_idx):
    ring_idx = ring_idx-1
    # Find best matching unit (prototype) for each data point
    # index in bmu_matches = data point index; value in bmu_matches = prototype index
    bmu_matches = core.bmus(data, h2som._centroids[h2som._rings[ring_idx][0]:h2som._rings[ring_idx][1]+1])
    prototypes = h2som._centroids[h2som._rings[ring_idx][0]:h2som._rings[ring_idx][1]+1]
    return bmu_matches, prototypes


def getPixelsForRing(data, bmu_matches, dframe):
    grid_x = np.array(dframe.index.get_level_values("grid_x")).astype(int)
    grid_y = np.array(dframe.index.get_level_values("grid_y")).astype(int)

    proto_idx = np.array(range(np.amax(bmu_matches+1)))
    #Creat empty pixels List for the ID of each pixel
    pixels = {}
    #Creat empty pixels_dict for the Position of each pixel
    pixels_dict = {}
    for i in proto_idx:
        # Find indices in bmu that matches a specific prototype, i.e. indices of pixels that match a specific prototype
        idx = np.where(bmu_matches == i)[0]
        # Get x and y coordinates of the matching pixels
        seg_x = grid_x[idx]
        seg_y = grid_y[idx]
        #Zip X-Values and Y-Values to one List [(x1,y1),(x2,y2),...]
        result = list(zip(seg_x, seg_y))
        pixelIDs = []
        for px,py in result:
            pxID = f"px{px}.{py}ID"
            pixelIDs.append(pxID)
            pixels_dict[pxID] = {}
            pixels_dict[pxID]["pos"] = (int(px),int(py))
        pixels[f"prototyp{i}"] = pixelIDs

    return pixels, pixels_dict

def createJson(h2som, data, dframe):
#get max x and max y for height of image
    grid_x = np.array(dframe.index.get_level_values("grid_x")).astype(int)
    grid_y = np.array(dframe.index.get_level_values("grid_y")).astype(int)
    gridX_max = np.amax(grid_x)
    gridY_max = np.amax(grid_y)
    canvas = {'x': gridX_max, 'y': gridY_max}
    json_dict = {}
    ring_dict = {}
    ring_json_list = []
    # Get each Ring
    for ring_idx, ring_tuple in enumerate(h2som._rings, start=1):
        prototyp_dict = {}
        membs, prototypes = calc_memb(data, h2som, ring_idx)
        ring_json_list.append((prototypes, ring_idx))
        pixelsPerPrototype, pixels_dict = getPixelsForRing(data, membs, dframe)
		# get the Prototypes of the ring
        proto_idx = 0
        for protokey, pixel_id_list in pixelsPerPrototype.items():
            prototyp_dict[protokey] = {}
            prototyp_dict[protokey]["pos"] = [h2som._pos[ring_tuple[0]:ring_tuple[1]+1, 0][proto_idx], h2som._pos[ring_tuple[0]:ring_tuple[1]+1, 1][proto_idx]]
            prototyp_dict[protokey]["pixel"] = pixel_id_list
            proto_idx += 1
		# add prtotype to the ring
        ring_dict["ring"+str(ring_idx-1)] = prototyp_dict

	#add Ring, Pixels and Mzs to the Json
    json_dict["rings"] = ring_dict
    json_dict["pixels"] = pixels_dict
    json_dict["mzs"] = [x for x in dframe.columns]

    for pxid, _ in json_dict["pixels"].items():
        json_dict["pixels"][pxid]["membership"] = {}
        for ring_key, protodict in json_dict["rings"].items():
            for protokey, _ in protodict.items():
                if pxid in protodict[protokey]["pixel"]:
                    json_dict["pixels"][pxid]["membership"][ring_key] = protokey

    jsonData = json.dumps(json_dict)
    return jsonData, canvas, ring_json_list


### Spectral workflow

parser = argparse.ArgumentParser(description='Arguments for the h2som')
parser.add_argument('-f', '--filename', dest='file', help='The Filename of the h5 data.', required=True)
parser.add_argument('-o', '--outputfile', dest='out', help='The path where you want to store the computed data', nargs='?')
parser.add_argument('-e', '--epsilon', dest='eps', help='Epsilon parameter for the h2SOM.', nargs=2, default=['1.0', '0.01'])
parser.add_argument('-s', '--sigma', dest='sig', nargs=2, default=['13', '0.24'], help='Sigma parameter for the h2SOM.')
parser.add_argument('-t', '--test', dest='test', action='store_true', help='Set the flag while you develope bro')
parser.add_argument('-i', '--niter', dest='niter', default=10, help='iteration parameter for the h2SOM.')
parser.add_argument('-p', '--posopt', dest='posopt', help='Apply position optimization for H2SOM.', action='store_true')
parser.add_argument('-v', '--posoptalg', dest='posoptalg', help='Position optimization algorithm.', required=False, default="winnertakealldulled", choices=["winnertakeall", "winnertakealldulled", "tugofwar", "tugofwardulled"])
parser.add_argument('-m', '--maxiter', dest='maxiter', default=np.inf, help='Hardcap maximum iterations for position optimization.', required=False)
#parser.add_argument('-t', '--test', dest='test', action='store_true')
args = parser.parse_args()
if (args.test):
    path_to_backend = '../backend/'
else:
    path_to_backend = 'backend/'

outpath = args.out

path = ''
filename = ''
if ('.h5' in args.file):
    path = path_to_backend + path_to_dataset + args.file
    filename = args.file.split('.')[0]
else:
    path = path_to_backend + path_to_dataset + args.file + h5
    filename = args.file


dframe, data = read_data(path)
data = data.copy(order='C')
### For spatial workflow add:
#data = data.T.copy(order="C")
h2som = calc_h2som(data, args.eps, args.sig, args.niter)
if args.posopt:
    h2som_opt = deepcopy(h2som)
    for ring in [1,2,3]:
        print("Start H2SOM position optimization for ring {ring}...")
        prototypes = h2som_opt._centroids[h2som_opt._rings[ring-1][0]:h2som_opt._rings[ring-1][1]+1]
        change = np.inf
        iterations = 0
        while change > 0 and iterations < args.maxiter:
            h2som_opt, change = position_optimization(h2som_opt, prototypes, args.posoptalg, ring)
            iterations += 1
        print(f"Position optimization stopped after {iterations} iterations!")
    h2som = h2som_opt
#membs = calc_memb(data, h2som, 0, args.file)
created_json, dimensions, rings = createJson(h2som, data, dframe)

# TODO: path_ doesn't exist in docker...
if(outpath != None):
    pickle.dump(created_json, open(outpath + filename + '.json', 'wb'))
    pickle.dump(dimensions, open(outpath + filename +"_info.h2som", "wb"))
    for ri in rings:
        pickle.dump(ri[0], open(outpath + filename+'_ring' + str(ri[1]-1) + '.h2som', 'wb'))
else:
    pickle.dump(created_json, open(path_to_backend + path_to_json + filename + '.json', 'wb'))
    pickle.dump(dimensions, open(path_to_backend + path_to_h2som_data + filename +"_info.h2som", "wb"))
    for ri in rings:
        pickle.dump(ri[0], open(path_to_backend + path_to_h2som_data + filename+'_ring' + str(ri[1]-1) + '.h2som', 'wb'))
# spectral_cluster(data, membs, dframe)
#plot_poincare_structure(h2som)
