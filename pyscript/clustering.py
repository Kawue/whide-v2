import numpy as np
from umap import UMAP
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colors as mplcolors
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import AffinityPropagation
import json
import pickle

path_to_backend_testing = '../backend/'
path_to_backend = 'backend/'
path_to_dataset = 'datasets/'
path_to_json = 'json/'
path_to_h2som_data = 'h2som/'
h5 = '.h5'

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
parser.add_argument('-e', '--embedding', dest='embedding', help='Embedding from before to this dataset', default=False)
parser.add_argument('-s', '--space', dest='space', help='Choose between clusting in polar space or cartesien space', default='cartesien', choices=['polar', 'cartesien'])
parser.add_argument('-a', '--all_prototyps', dest='all', help='Cluster data but every pixel is a prototyp', action='store_true')
parser.add_argument('-d', '--dimensions_reduction', dest='dim', help='Choose between PCA and UMAP as dimension reduction', default='umap', choices=['pca', 'umap'])
parser.add_argument('-m', '--clustering_method', dest='method', help='Choose between KMEANS and Agglomerative Clustering', default='kmeans', choices=['kmeans', 'agglomerative'])
parser.add_argument('-c', '--no_dimension_reduction', dest='clustering', help='If clustering is done on Data without dimension reduction', action='store_true')
parser.add_argument('-t', '--test', dest='test', action='store_true')
args = parser.parse_args()
outpath = args.out

path = ''
filename = ''
if(args.test) :
    path_to_backend = '../backend/'

if ('.h5' in args.file):
    # line for Docker
    path = path_to_backend + path_to_dataset + args.file
    # Line for testing
    #path = path_to_backend_testing + path_to_dataset + args.file
    filename = args.file.split('.')[0]
else:
    # line for Docker
    path = path_to_backend + path_to_dataset + args.file + h5
    # line for testing
    #path = path_to_backend_testing +path_to_dataset + args.file + h5
    filename = args.file

# read path
h5data = pd.read_hdf(path)
data = h5data.values

# Dimension reduction
############################################
dimReduction = ''
computed_embedding = ''
if (args.embedding == False):
    if (args.clustering):
        computed_embedding = data
    else:
        if (args.dim == 'umap'):
            print('Dimensions reduction: UMAP')
            dimReduction = 'UMAP'
            u = UMAP(n_components=2)
            computed_embedding = u.fit_transform(data)
            if args.space == 'polar':
                print('Space: Polarspace')
                computed_embedding = np.array(cart2polar(computed_embedding[:,0], computed_embedding[:,1])).T
            else:
                print('Space: Cartesienspace')
            np.save('embedding', computed_embedding)
            print('Dim Reduction is ready')
        else:
            print('Dimensions reduction: PCA')
            dimReduction = 'PCA'
            pca = PCA(n_components=2)
            computed_embedding = pca.fit_transform(data)
            if args.space == 'polar':
                print('Space: Polarspace')
                computed_embedding = np.array(cart2polar(computed_embedding[:,0], computed_embedding[:,1])).T
            else:
                print('Space: Cartesienspace')
            np.save('embedding', computed_embedding)
            print('Dim Reduction is ready')
else:
    computed_embedding = np.load(args.embedding)
    if args.space == 'polar':
        print('Space: Polarspace')
        computed_embedding = np.array(cart2polar(computed_embedding[:,0], computed_embedding[:,1])).T
    else:
        print('Space: Cartesienspace')

###########################################

def plt_cluster_img(h5data, labels, color):
    gx = h5data.index.get_level_values("grid_x")
    gy = h5data.index.get_level_values("grid_y")
    img = np.full((gy.max()+1, gx.max()+1,4), -1)
    for i, l in enumerate(labels):

        if (isinstance(l, np.ndarray)):
            k = i
        else:
            k = l
        img[(gy[i], gx[i])] = list((color[k] * 255).astype(int))
    fig = plt.figure()
    plt.imshow(img.astype('uint8'), interpolation='nearest')
    plt.savefig('Segmentation_' + cartOrPolar + '_' + cluster + '_'   + method + '.png')
    plt.close(fig)

def unit_cicle_color_wheel(centers):

    fig = plt.figure()
    plt.title('ColorWheel')
    display_axes = fig.add_axes([0.1,0.1,0.8,0.8], projection='polar')
    display_axes._direction = 2*np.pi
    norm = mpl.colors.Normalize(0.0, 2*np.pi)

    # Plot the colorbar onto the polar axis
    # note - use orientation horizontal so that the gradient goes around
    # the wheel rather than center out
    quant_steps = 12056
    cm = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.get_cmap('hsv',quant_steps))

    cb = mpl.colorbar.ColorbarBase(display_axes, cmap=mpl.cm.get_cmap('hsv',quant_steps),
                                    norm=norm,
                                    orientation='horizontal')


    #for x in np.arctan2(embedding[:,0],embedding[:,1]):
    #    print(display_axes.format_coord(x,0.8))

    cb.outline.set_visible(False)
    display_axes.set_axis_off()
    display_axes.plot(centers[:,0], centers[:,1],"ko")

    d = centers[:,0]
    colors = cm.to_rgba(d)

    plt.savefig('ColorWheel.png')
    plt.close(fig)

    return colors

    return colors
colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green", 3: "tab:red", 4: "tab:purple", 5: "tab:brown", 6: "tab:pink", 7: "tab:gray", 8: "tab:olive", 9:"tab:cyan"}


def kmeans_clustering(embed, method):
    e_kmeans = KMeans(n_clusters=8, random_state=42, n_jobs=-2).fit(embed)
    labels = e_kmeans.labels_
    proto = e_kmeans.cluster_centers_
    if (args.clustering):
        u = UMAP(n_components=2)
        proto = u.fit_transform(proto)

    proto_centers, proto_diff, tranformedPixels =  applyTransformation(proto, embed, labels)
    if (args.all):
        proto_centers, diff = transform(embed)
        labels = np.arange(np.size(embed,0))





    pltFigure(embed, labels, proto)

    #color = unit_cicle_color_wheel(proto_centers)
    #plt_cluster_img(h5data, pe_labels,  color)

    #all_polar_color = unit_cicle_color_wheel(tranformedPolPixels)
    #plt_cluster_img(h5data, tranformedPolPixels, all_polar_color)


    #all_color = unit_cicle_color_wheel(transformedPixels)
    #plt_cluster_img(h5data, transformedPixels,  all_color)

    return proto_centers, labels



def agglomerative_clustering(embed, method):
    num_obj = 8

    e_agglomerative = AgglomerativeClustering(n_clusters=num_obj, affinity='euclidean', linkage='ward').fit(embed)
    labels = e_agglomerative.labels_
    proto = []
    for l in set(labels):
        ind = []
        for i in range(len(embed)):
            if labels[i] == l:
                ind.append(embed[i])
        pro = np.mean(ind, axis=0)
        proto.append(np.array(pro))
    proto = np.array(proto)
    proto_centers, proto_diff, tranformedPixels =  applyTransformation(proto, embed, labels)
    if (args.all):
        proto_centers, diff = transform(embed)
        labels = np.arange(np.size(embed,0))



    pltFigure(embed, labels, proto)

    #color = unit_cicle_color_wheel(proto_centers)
    #plt_cluster_img(h5data, labels,  color)

    #all_polar_color = unit_cicle_color_wheel(tranformedPolPixels)
    #plt_cluster_img(h5data, tranformedPolPixels,  all_polar_color)

    #all_color = unit_cicle_color_wheel(transformedPixels)
    #plt_cluster_img(h5data, transformedPixels,  all_color)

    return proto_centers, labels


def pltFigure(embed, labels, proto):
    fig = plt.figure()
    for i, l in enumerate(labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(proto):
        plt.plot(tup[0], tup[1], color='black', marker="s")

    plt.savefig('cluster.png')
    plt.close(fig)



def normalize(a,b,min,max, x):
    norm = (b-a)*((x-min)/(max-min))+a
    return norm

def transform(centers):
    if(args.space == 'polar'):
        for i in range(len(centers)):
            centers[i] = np.array(polar2cart(centers[i][0], centers[i][1]))
    yMeanCenters = []
    for i in range(len(centers)):
        yMeanCenters.append(centers[i][1])
    midY = np.mean(np.array(yMeanCenters))


    xMeanCenters = []
    for i in range(len(centers)):
        xMeanCenters.append(centers[i][0])
    midX = np.mean(np.array(xMeanCenters))


    yHighMaxValue = float('-inf')
    yHighMinValue = float('inf')
    yLowMaxValue = float('-inf')
    yLowMinValue = float('inf')

    for i in range(len(centers)):
        if centers[i][1] >= midY:
            if yHighMaxValue <= centers[i][1]:
                yHighMaxValue = centers[i][1]
            if yHighMinValue >= centers[i][1]:
                yHighMinValue = centers[i][1]
        else:
            if yLowMaxValue <= centers[i][1]:
                yLowMaxValue = centers[i][1]
            if yLowMinValue >= centers[i][1]:
                yLowMinValue = centers[i][1]
    xHighMaxValue = float('-inf')
    xHighMinValue = float('inf')
    xLowMaxValue = float('-inf')
    xLowMinValue = float('inf')

    for i in range(len(centers)):
        if centers[i][0] >= midX:
            if xHighMaxValue <= centers[i][0]:
                xHighMaxValue = centers[i][0]
            if xHighMinValue >= centers[i][0]:
                xHighMinValue = centers[i][0]
        else:
            if xLowMaxValue <= centers[i][0]:
                xLowMaxValue = centers[i][0]
            if xLowMinValue >= centers[i][0]:
                xLowMinValue = centers[i][0]



    transformed_centers = []

    for pos in centers:
        new_pos = [0,0]
        if pos[1] < midY:
            new_pos[1] = normalize(-0.9, -0.5, yLowMinValue, yLowMaxValue, pos[1])
        else:
            new_pos[1] = normalize(0.5, 0.9, yHighMinValue, yHighMaxValue, pos[1])

        if pos[0] < midX:
            new_pos[0] = normalize(-0.9, -0.5, xLowMinValue, xLowMaxValue, pos[0])
        else:
            new_pos[0] = normalize(0.5, 0.9, xHighMinValue, xHighMaxValue, pos[0])

        transformed_centers.append(new_pos)

    transformed_centers = np.array(transformed_centers)

    differenz = {}
    for i in range(len(centers)):
        diffTheta =  transformed_centers[i][0] - centers[i][0]
        diffR =  transformed_centers[i][1] - centers[i][1]
        differenz[i] = [diffTheta, diffR]
    return transformed_centers, differenz

def applyTransformation(centers, embedding, labels):
    new_centers, new_centers_diff = transform(centers)
    maxValue = float('-inf')
    minValue = float('inf')
    for i in range(len(embedding)):
        if maxValue <= abs(embedding[i][1]):
            maxValue = abs(embedding[i][1])
        if minValue >= abs(embedding[i][1]):
            minValue = abs(embedding[i][1])

    allPixels = []
    for l in set(labels):
        for i in range(len(embedding)):
            if(labels[i] == l):
                diff = new_centers_diff[l]
                current = embedding[i]
                t = current[0] + diff[0]
                #r = current[1] + diff[1]
                r =  normalize(0.5, 6, minValue, maxValue, abs(embedding[i][1]))
                allPixels.append([t,r])
    allPixels = np.array(allPixels)
    return new_centers, new_centers_diff, allPixels

def getPixels(grid_x, grid_y, proto_idx, labels):
    pixels = []
    pixels_dict = {}
    id = 0
    for i in range(len(proto_idx)):
        idx = np.argwhere(labels == i).flatten()
        # Get x and y coordinates of the matching pixels
        seg_x = grid_x[idx]
        seg_y = grid_y[idx]
        #Zip X-Values and Y-Values to one List [(x1,y1),(x2,y2),...]
        result = list(zip(seg_x, seg_y))
        pixelIDs = []
        for k in range(0,len(result)):
	    #creat all pixel Ids
            pixelIDs.append("px"+str(id)+"ID")
	    #creat all x and y coordinate for each pixel Id
            pixels_dict["px"+str(id)+"ID"] = {}
            pixels_dict["px"+str(id)+"ID"]["pos"] = (int(result[k][0]),int(result[k][1]))
            id += 1

        pixels.append(pixelIDs)
    return pixels, pixels_dict

def calculateCoefficients( data, prototyps, labels, embedding):
    bookmark_ring = []
    if(args.clustering):
        u = UMAP(n_components=2)
        pixel_embed = u.fit_transform(embedding)
    else:
        pixel_embed = embedding
    #forEach prototype
    for i in range(len(prototyps)):
        #get indizes from pixel in prototyp
        indizes = np.argwhere(labels == i).flatten()
        #  x and y of prototyp
        center_point = prototyps[i]
        # get an array with all the mz values of each pixel
        pixelIntensities = data[indizes]
        # get the x and y of each pixel
        pixelPoints = pixel_embed[indizes]

        weightedIntensities = []
        weights = []
        # foreach pixel calculate distance and multiply with mz vector
        for j in range(len(pixelIntensities)):
            # mzValues of Pixel j
            intensities_pixel = pixelIntensities[j]
            #point x and y of pixel j
            point_pixel = pixelPoints[j]
            if (args.all):
                d_p_c = 1
            else:
                #distance between prototyp point and pixel point and save distance
                d_p_c = np.linalg.norm(point_pixel-center_point)
            weights.append(d_p_c)
            # weight the mz vector with distance and save it
            weigIntens = np.multiply(d_p_c, intensities_pixel)
            weightedIntensities.append(weigIntens)
        # calculate sum of weighted mzValues
        sumOfIntensities = np.sum(np.array(weightedIntensities), axis=0)
        # calculate sum of distances
        if (args.all):
            computed_intensitie = sumOfIntensities
        else:
            computed_intensitie = np.multiply((1 / np.sum(weights)) , sumOfIntensities)
        bookmark_ring.append(computed_intensitie)

    bookmark_ring = np.array(bookmark_ring)
    return bookmark_ring

def createJson(h5data, prototyps, labels, embedding):
    gx = np.array(h5data.index.get_level_values("grid_x"))
    gy = np.array(h5data.index.get_level_values("grid_y"))
    gridX_max = np.amax(gx)
    gridY_max = np.amax(gy)
    canvas = {'x': gridX_max, 'y': gridY_max}

    posX = prototyps[:,0]
    posY = prototyps[:,1]


    json_dict = {}

    ring_idx = 1
    prototyp_dict ={}
    ring_dict = {}
    pixels_dict = None

	# Get each Ring
    pixels_dict = None
    ring_json_list = []
    prototypCoeff = calculateCoefficients(data, prototyps, labels, embedding)
    ring_json_list.append((prototypCoeff, ring_idx))

    pixelsPerPrototype, pixels_dict = getPixels(gx, gy, prototyps, labels)

	# get the Prototypes of the ring
    prototyp_idx = 0
    for k in range(len(prototyps)):

        prototyp_dict["prototyp"+str(k)] = {}
		# set the items of the Prototype
        polarX, polarY = polar2cart(posX[k], posY[k])
        prototyp_dict["prototyp"+str(k)]["pos"] = [polarX, polarY]
        prototyp_dict["prototyp"+str(k)]["pixel"] = pixelsPerPrototype[prototyp_idx]
        prototyp_dict["prototyp"+str(k)]["coefficients"] = []
        prototyp_idx += 1

		# add prtotype to the ring
    ring_dict["ring0"] = prototyp_dict

	#add Ring, Pixels and Mzs to the Json
    json_dict["rings"] = ring_dict
    json_dict["pixels"] = pixels_dict
    json_dict["mzs"] = [x for x in h5data.columns]

    for key_px, val_px in json_dict["pixels"].items():
        json_dict["pixels"][key_px]["membership"] = {}
        for key_ring, val_ring in json_dict["rings"].items():
            for prot, val_prot in val_ring.items():
                if key_px in val_prot["pixel"]:
                    json_dict["pixels"][key_px]["membership"][key_ring] = prot


    jsonData= json.dumps(json_dict)

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

if args.method == 'kmeans':
    print('Clustering method: KMEANS')
    proto, labels = kmeans_clustering(computed_embedding, dimReduction)
else:
    print('Clustering method: Agglomerative Clustering')
    proto, labels = agglomerative_clustering(computed_embedding, dimReduction)

createJson(h5data, proto, labels, computed_embedding)
