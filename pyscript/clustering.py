import numpy as np
from umap import UMAP
import pandas as pd
import argparse
from os.path import join
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colors as mplcolors
from sklearn.cluster import KMeans, AgglomerativeClustering, AffinityPropagation, DBSCAN
import json
import pickle
from msi_dimension_reducer import PCA, UMAP


path_to_backend = 'backend/'
path_to_dataset = 'datasets/'
path_to_json = 'json/'
path_to_h2som_data = 'h2som/'
h5 = '.h5'

colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green", 3: "tab:red", 4: "tab:purple", 5: "tab:brown", 6: "tab:pink", 7: "tab:gray", 8: "tab:olive", 9:"tab:cyan"}


def cart2polar(x,y):
    theta = np.arctan2(y,x)
    r = np.sqrt(x**2 + y**2)
    return theta, r

def polar2cart(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

parser = argparse.ArgumentParser(description='Arguments for clustering')
parser.add_argument('-f', '--filename', dest='file', help='The Filename of the h5 data.', required=True)
parser.add_argument('-o', '--outputfile', dest='out', help='The path where you want to store the computed data', nargs='?')
parser.add_argument('-k', '--nrclusters', dest='nr', help='The number of clusters', default=8, type=int)
parser.add_argument('-e', '--embedding', dest='embedding', help='Embedding from before to this dataset', default=False)
parser.add_argument('-s', '--space', dest='space', help='Choose between clusting in polar space or cartesien space', default='cartesien', choices=['polar', 'cartesien'])
parser.add_argument('-a', '--all_prototyps', dest='all', help='Cluster data but every pixel is a prototyp', action='store_true')
parser.add_argument('-d', '--dimensions_reduction', dest='dim', help='Choose between PCA and UMAP as dimension reduction', default='umap', choices=['pca', 'umap'])
parser.add_argument('-m', '--clustering_method', dest='method', help='Choose between KMEANS and Agglomerative Clustering', default='kmeans', choices=['kmeans', 'agglomerative'])
parser.add_argument('-c', '--no_dimension_reduction', dest='clustering', help='If clustering is done on Data without dimension reduction', action='store_true')
parser.add_argument('-t', '--test', dest='test', action='store_true')
args = parser.parse_args()
outpath = args.out
nr_clusters = args.nr

path = ''
filename = ''
if(args.test) :
    path_to_backend = '../backend/'

if ('.h5' in args.file):
    # line for Docker
    path = path_to_backend + path_to_dataset + args.file
    filename = args.file.split('.')[0]
else:
    # line for Docker
    path = path_to_backend + path_to_dataset + args.file + h5

    filename = args.file

# read path
h5data = pd.read_hdf(path)
data = h5data.values

# Dimension reduction
############################################
dimReductionDict = {
    "pca": PCA,
    "umap": UMAP
}

if (args.embedding == False):
    if (args.clustering):
        embedding = data
    else:
        embedding = dimReductionDict[args.dim](data, 2).perform()
        if args.space == 'polar':
            print('Space: Polar space')
            embedding = np.array(cart2polar(embedding[:,0], embedding[:,1])).T
        else:
            print('Space: Cartesien space')
        #np.save(join(outpath, filename + "_" + args.dim + '_embedding.npy'), embedding)
        np.save(join(filename + "_" + args.dim + '_embedding.npy'), embedding)
else:
    embedding = np.load(args.embedding)
    if args.space == 'polar':
        print('Space: Polar space')
        embedding = np.array(cart2polar(embedding[:,0], embedding[:,1])).T
    else:
        print('Space: Cartesien space')

###########################################
def kmeans_clustering(embedding, nr_clusters):
    e_kmeans = KMeans(n_clusters=nr_clusters, random_state=42, n_jobs=-1).fit(embedding)
    labels = e_kmeans.labels_
    proto = e_kmeans.cluster_centers_
    if (args.clustering):
        proto = dimReductionDict[args.dim](proto, 2).perform()
    proto_centers, proto_diff, tranformedPixels =  applyTransformation(proto, embedding, labels)
    if (args.all):
        proto_centers, diff = transform(embedding)
        labels = np.arange(np.size(embedding,0))
    return proto_centers, labels

def agglomerative_clustering(embedding, nr_clusters):
    e_agglomerative = AgglomerativeClustering(n_clusters=nr_clusters, affinity='euclidean', linkage='ward').fit(embedding)
    labels = e_agglomerative.labels_
    proto = []
    for l in set(labels):
        idx = np.where(labels == l)
        proto.append(np.mean(embedding[idx], axis=0))
    proto = np.array(proto)
    proto_centers, proto_diff, tranformedPixels =  applyTransformation(proto, embedding, labels)
    if (args.all):
        proto_centers, diff = transform(embedding)
        labels = np.arange(np.size(embedding,0))
    return proto_centers, labels

def affinity_propagation_clustering(embedding, nr_clusters):
    e_affinity = AffinityPropagation(random_state=42).fit(embedding)
    labels = e_affinity.labels_
    proto = e_affinity.cluster_centers_
    if (args.clustering):
        proto = dimReductionDict[args.dim](proto, 2).perform()
    proto_centers, proto_diff, tranformedPixels =  applyTransformation(proto, embedding, labels)
    if (args.all):
        proto_centers, diff = transform(embedding)
        labels = np.arange(np.size(embedding,0))
    return proto_centers, labels

def dbscan_clustering(embedding, nr_clusters):
    e_dbscan = DBSCAN(eps=0.3).fit(embedding)
    labels = e_dbscan.labels_
    if -1 in labels:
        labels += 1
    #proto = embedding[core_sample_indices_]
    proto = []
    for l in set(labels):
        idx = np.where(labels == l)
        proto.append(np.mean(embedding[idx], axis=0))
    proto = np.array(proto)
    proto_centers, proto_diff, tranformedPixels = applyTransformation(proto, embedding, labels)
    if (args.all):
        proto_centers, diff = transform(embedding)
        labels = np.arange(np.size(embedding,0))
    return proto_centers, labels

def normalize(newmin, newmax, minval, maxval, x):
    norm = (newmax-newmin)*((x-minval)/(maxval-minval))+newmin
    return norm

def newTransformation(centers):
    # calculate mean and max distance
    mx,my = np.mean(centers, axis=0)
    distances = np.array([np.sqrt((dx-mx)**2 + (dy-my)**2) for (dx,dy) in centers])
    max_dist = np.amax(distances)
    point = centers[np.argmax(distances)]
    print('The point with max distance is {} and the distance is {}'.format(point, max_dist))
    scale = (1-0.1)/max_dist
    transformed_centers = np.array([[scale*(dx-mx), scale*(dy-my)] for (dx,dy) in centers])
    # diffTheta: tcenter[0] - centers[i][0]; diffR: tcenter[1] - centers[i][1]]
    difference = {idx:[tcenter[0] - centers[idx][0], tcenter[1] - centers[idx][1]] for idx, tcenter in enumerate(transformed_centers)}
    return transformed_centers, difference

def transform(centers):
    if(args.space == 'polar'):
        centers = np.array([polar2cart(center[0], center[1]) for center in centers])

    midX, midY = np.mean(centers, axis=0)
    upperX = centers[np.where(centers[:,0] >= midX)][:,0]
    lowerX = centers[np.where(centers[:,0] < midX)][:,0]
    upperY = centers[np.where(centers[:,1] >= midY)][:,1]
    lowerY = centers[np.where(centers[:,1] < midY)][:,1]

    xHighMaxValue = np.amax(upperX)
    xHighMinValue = np.amin(upperX)
    xLowMaxValue = np.amax(lowerX)
    xLowMinValue = np.amin(lowerX)
    yHighMaxValue = np.amax(upperY)
    yHighMinValue = np.amin(upperY)
    yLowMaxValue = np.amax(lowerY)
    yLowMinValue = np.amin(lowerY)

    transformed_centersX = [
        normalize(-0.9, -0.5, xLowMinValue, xLowMaxValue, center[0])
        if center[0] < midX else
        normalize(0.5, 0.9, xHighMinValue, xHighMaxValue, center[0])
        for center in centers
        ]

    transformed_centersY = [
        normalize(-0.9, -0.5, yLowMinValue, yLowMaxValue, center[1])
        if center[0] < midX else
        normalize(0.5, 0.9, yHighMinValue, yHighMaxValue, center[1])
        for center in centers
        ]

    transformed_centers = np.array(list(zip(transformed_centersX, transformed_centersY)))

    # diffTheta: tcenter[0] - centers[i][0]; diffR: tcenter[1] - centers[i][1]]
    difference = {idx:[tcenter[0] - centers[idx][0], tcenter[1] - centers[idx][1]] for idx, tcenter in enumerate(transformed_centers)}

    return transformed_centers, difference

def applyTransformation(centers, embedding, labels):
    new_centers, new_centers_diff = newTransformation(centers)
    #new_centers, new_centers_diff = transform(centers)

    maxValue = np.amax(abs(embedding))
    minValue = np.amin(abs(embedding))

    allPixels = []
    for l in set(labels):
        idx = np.where(labels == l)
        # t=embedding[i][0] + new_centers_diff[l][0] >> angle
        # r=normalize(0.5, 6, minValue, maxValue, abs(embedding[i][1])); alternative t=embedding[i][1] + new_centers_diff[l][1] >> radius
        allPixels.append([[embedding[i][0] + new_centers_diff[l][0], normalize(0.5, 6, minValue, maxValue, abs(embedding[i][1]))] for i,_ in enumerate(embedding[idx])])
    allPixels = np.concatenate(allPixels)
    return new_centers, new_centers_diff, allPixels


def getPixels(grid_x, grid_y, proto_idx, labels):
    pixels = {}
    pixels_dict = {}
    for i in range(len(proto_idx)):
        idx = np.where(labels == i)[0]
        # Get x and y coordinates of the matching pixels
        seg_x = grid_x[idx]
        seg_y = grid_y[idx]
        #Zip X-Values and Y-Values to one List [(x1,y1),(x2,y2),...]
        result = list(zip(seg_x, seg_y))
        pixelIDs = []
        for px,py in result:
            pxID = f"px{px}.{py}ID"
	        #creat all pixel Ids
            pixelIDs.append(pxID)
	        #creat all x and y coordinate for each pixel Id
            pixels_dict[pxID] = {}
            pixels_dict[pxID]["pos"] = (int(px),int(py))
        pixels[f"prototyp{i}"] = pixelIDs
    return pixels, pixels_dict


def calculateCoefficients(data, prototyps, labels, embedding):
    bookmark_ring = []
    if(args.clustering):
        pixel_embedding = dimReductionDict[args.dim](embedding, 2).perform()
    else:
        pixel_embedding = embedding
    # center_point: x, y of prototyp
    for idx, center_point in enumerate(prototyps):
        #get indizes from pixel in prototyp
        indices = np.where(labels == idx)
        # get an array with all the mz values of each pixel
        pixelIntensities = data[indices]
        # get the x and y of each pixel
        pixelPoints = pixel_embedding[indices]

        weightedIntensities = []
        weights = []
        # calculate distance and multiply with mz vector
        for idx2, px_intensity in enumerate(pixelIntensities):
            # x,y of pixel idx2
            point_pixel = pixelPoints[idx2]
            # distance between prototyp point and pixel point
            if (args.all):
                d_p_c = 1
            else:
                d_p_c = np.linalg.norm(point_pixel-center_point)
            weights.append(d_p_c)
            # weight the mz vector with distance
            weigIntens = np.multiply(d_p_c, px_intensity)
            weightedIntensities.append(weigIntens)
        # calculate sum of weighted mzValues
        sumOfIntensities = np.sum(np.array(weightedIntensities), axis=0)
        # calculate sum of distances
        if (args.all):
            computed_intensitie = sumOfIntensities
        else:
            computed_intensitie = np.multiply((1 / np.sum(weights)) , sumOfIntensities)
        bookmark_ring.append(computed_intensitie)
    return np.array(bookmark_ring)

def createJson(h5data, prototyps, labels, embedding):
    gx = np.array(h5data.index.get_level_values("grid_x")).astype(int)
    gy = np.array(h5data.index.get_level_values("grid_y")).astype(int)
    gridX_max = np.amax(gx)
    gridY_max = np.amax(gy)
    canvas = {'x': gridX_max, 'y': gridY_max}
    json_dict = {}
    ring_idx = 1
    prototyp_dict ={}
    ring_dict = {}
    ring_json_list = []
    prototypCoeff = calculateCoefficients(data, prototyps, labels, embedding)
    ring_json_list.append((prototypCoeff, ring_idx))
    posX = prototyps[:,0]
    posY = prototyps[:,1]
    pixelsPerPrototype, pixels_dict = getPixels(gx, gy, prototyps, labels)

	# get the Prototypes of the ring
    for k, _ in enumerate(prototyps):
        protokey = "prototyp"+str(k)
        prototyp_dict[protokey] = {}
		# set the items of the Prototype
        prototyp_dict[protokey]["pos"] = [posX[k], posY[k]]
        prototyp_dict[protokey]["pixel"] = pixelsPerPrototype[protokey]
        #prototyp_dict["prototyp"+str(k)]["coefficients"] = []

	# add prtotype to the ring
    ring_dict["ring0"] = prototyp_dict

	#add Ring, Pixels and Mzs to the Json
    json_dict["rings"] = ring_dict
    json_dict["pixels"] = pixels_dict
    json_dict["mzs"] = [x for x in h5data.columns]

    for pxid, _ in json_dict["pixels"].items():
        json_dict["pixels"][pxid]["membership"] = {}
        for ring_key, protodict in json_dict["rings"].items():
            for protokey, _ in protodict.items():
                if pxid in protodict[protokey]["pixel"]:
                    json_dict["pixels"][pxid]["membership"][ring_key] = protokey

    jsonData = json.dumps(json_dict)

    if(outpath != None):
        pickle.dump(jsonData, open(outpath + filename + '.json', 'wb'))
        pickle.dump(canvas, open(outpath + filename +"_info.h2som", "wb"))
        for ri in ring_json_list:
            pickle.dump(ri[0], open(outpath + filename+'_ring' + str(ri[1]-1) + '.h2som', 'wb'))
    else:
        pickle.dump(jsonData, open(path_to_backend + path_to_json + filename + '.json', 'wb'))
        pickle.dump(canvas, open(path_to_backend + path_to_h2som_data + filename +"_info.h2som", "wb"))
        for ri in ring_json_list:
            pickle.dump(ri[0], open(path_to_backend + path_to_h2som_data + filename+'_ring' + str(ri[1]-1) + '.h2som', 'wb'))



#h2somdata = np.array([[0.45508986056222733, 0.4550898605622273],[3.9408782088522694e-17, 0.6435942529055826],[-0.4550898605622273, 0.45508986056222733],[-0.6435942529055826, 7.881756417704539e-17],[-0.45508986056222744, -0.4550898605622273],[-1.1822634626556806e-16, -0.6435942529055826],[0.4550898605622272, -0.45508986056222744],[0.6435942529055826, -1.5763512835409078e-16]])


#kmeans_clustering(umapEmbedding, umapPolar_embedding, 'UMAP')
#kmeans_clustering(pcaEmbedding, pcaPolar_embedding, 'PCA')
#print('KMEANS is ready')
#agglomerative_clustering(pcaEmbedding, pcaPolar_embedding, 'PCA')

# clustering in polar coordinates or in cartesien

# clustering in polar coordinates or in cartesien
if args.method == 'kmeans':
    print('Clustering method: k-Means')
    proto, labels = kmeans_clustering(embedding, nr_clusters)
elif args.method == 'agglomerative':
    print('Clustering method: Agglomerative Clustering')
    proto, labels = agglomerative_clustering(embedding, nr_clusters)
elif args.method == 'affinity':
    print('Clustering method: Affinity Propagation')
    proto, labels = affinity_propagation_clustering(embedding, nr_clusters)
elif args.method == 'dbscan':
    print('Clustering method: DBSCAN')
    proto, labels = dbscan_clustering(embedding, nr_clusters)
else:
    raise ValueError("Something went wrong with the selection of a clustering method.")


createJson(h5data, proto, labels, embedding)
