from pyclusterbdm.algorithms import H2SOM
import pyclusterbdm.core as core
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from os import listdir, makedirs
from os.path import join, exists

matplotlib.use("TkAgg")

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


def calc_h2som(data):
    ### Important H2SOM Properties
    # hierachical ring index intervals
    #print(h2som._rings)

    # Child node indices of each node as dict. Key = node, value = list of child indices.
    # Indices which are not included: parent index, index of both same level hierarchy neighbors
    #print(h2som._childs)

    # 2D positions in on poincare disc
    #print(h2som._pos)

    # Cluster Centroids
    #print(h2som._centroids.shape)

    # H2SOM initialization
    h2som = H2SOM(data)
    
    # H2SOM training
    h2som.cluster()

    return h2som


def calc_memb(data, h2som, ring_idx):
    ring_idx = ring_idx-1
    # Find best matching unit (prototype) for each data point
    # index in bmu_matches = data point index; value in bmu_matches = prototype index
    bmu_matches = core.bmus(data, h2som._centroids[h2som._rings[ring_idx][0]:h2som._rings[ring_idx][1]+1])   
    #print(np.amin(bmu_matches))
    #print(np.amax(bmu_matches))
    #print(bmu_matches)
    return bmu_matches


# Calculate cluster of pixels, aka. segmentation map
def spectral_cluster(data, bmu_matches, dframe):
    # Create empty image
    grid_x = np.array(dframe.index.get_level_values("grid_x"))
    grid_y = np.array(dframe.index.get_level_values("grid_y"))
    img = np.zeros((np.amax(grid_y)+1, np.amax(grid_x)+1))

    proto_idx = np.array(range(np.amax(bmu_matches+1)))
    #print(proto_idx)

    # Iterate over each prototype
    for i in proto_idx:
        # Find indices in bmu that matches a specific prototype, i.e. indices of pixels that match a specific prototype
        idx = np.where(bmu_matches == i)[0]
        # Get x and y coordinates of the matching pixels
        seg_x = grid_x[idx]
        seg_y = grid_y[idx]
        # Set matching pixels to a prototype specific value
        img[seg_y, seg_x] = i
        plt.imshow(img, cmap="tab20")
    plt.show()


# Calculate cluster of images
def spatial_cluster(data, h2som, bmu_matches, dframe):
    grid_x = np.array(dframe.index.get_level_values("grid_x"))
    grid_y = np.array(dframe.index.get_level_values("grid_y"))
    gridX_max = np.amax(grid_x)
    gridY_max = np.amax(grid_y)

    savepath = "./cluster/"

    proto_idx = np.array(range(np.amax(bmu_matches+1)))
    #print(proto_idx)

    # Iterate over each prototype
    for i in proto_idx:
        cl = "c" + str(i)
        cl_path = join(savepath, cl)
        if not exists(cl_path):
            makedirs(cl_path)
        # Find indices in bmu that matches a specific prototype, i.e. indices of images that match a specific prototype
        idx = np.where(bmu_matches == i)[0]
        # Iterate over each matching image
        for j in idx:
            # Create empty image
            img = np.zeros((gridY_max+1, gridX_max+1))
            # Grab intensity values
            intens = data[j,:]
            # Create m/z intensity image
            img[grid_y, grid_x] = intens
            # Scale intensity image in [0,1]
            img = ((img - np.amin(img)) / (np.amax(img) - np.amin(img)))
            plt.imsave(join(cl_path, str(j)), img, vmin=0, vmax=1)

        # Create empty image for the prototype image
        img = np.zeros((gridY_max+1, gridX_max+1))
        # Grab intensity values for the prototype image
        intens = h2som._centroids[i]
        # Create prototype image
        img[grid_y, grid_x] = intens
        # Scale prototype image in [0,1]
        img = ((img - np.amin(img)) / (np.amax(img) - np.amin(img)))
        plt.imsave(join(cl_path, "proto" + str(i)), img, vmin=0, vmax=1)



### Spectral workflow
path = "/home/kwuellems/datasets/barley101.h5"
dframe, data = read_data(path)
### For spatial workflow add:
#data = data.T.copy(order="C")
h2som = calc_h2som(data)
membs = calc_memb(data, h2som, 1)
spectral_cluster(data, membs, dframe)
#plot_poincare_structure(h2som)
