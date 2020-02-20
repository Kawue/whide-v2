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
args = parser.parse_args()

h5data = pd.read_hdf(args.file)
data = h5data.values

# Dimension reduction
############################################

u = UMAP(n_components=2)
umapEmbedding = u.fit_transform(data)
np.save('umapEmbedding', umapEmbedding)
umapPolar_embedding = np.array(cart2polar(umapEmbedding[:,0], umapEmbedding[:,1])).T
print("UMAP")

pca = PCA(n_components=2)
pcaEmbedding = pca.fit_transform(data)
np.save('pcaEmbedding', pcaEmbedding)
pcaPolar_embedding = np.array(cart2polar(pcaEmbedding[:,0], pcaEmbedding[:,1])).T
print("PCA")

############################################
print('Dim Reduction is ready')
def plt_cluster_img(h5data, labels, cartOrPolar, cluster, method, color):
    print("plt_cluster_img")
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

def unit_cicle_color_wheel(centers, cartOrPolar, method, cluster):
    print("unit_cicle_color_wheel")
    fig = plt.figure()
    plt.title('ColorWheel_' +cartOrPolar + '_' + method + '_' + cluster)
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
    h2somdata = np.array([[0.45508986056222733, 0.4550898605622273],[3.9408782088522694e-17, 0.6435942529055826],[-0.4550898605622273, 0.45508986056222733],[-0.6435942529055826, 7.881756417704539e-17],[-0.45508986056222744, -0.4550898605622273],[-1.1822634626556806e-16, -0.6435942529055826],[0.4550898605622272, -0.45508986056222744],[0.6435942529055826, -1.5763512835409078e-16]])




    d = centers[:,0]
    colors = cm.to_rgba(d)
    '''


    plt.figure()
    plt.imshow(colors[:,None])
    plt.show()
    '''
    plt.savefig('ColorWheel_' +cartOrPolar + '_' + method + '_' + cluster + '.png')
    plt.close(fig)

    return colors
colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green", 3: "tab:red", 4: "tab:purple", 5: "tab:brown", 6: "tab:pink", 7: "tab:gray", 8: "tab:olive", 9:"tab:cyan"}

def thetaZero(data):
    data[:,0] = 0
    return data
def radiusZero(data):
    data[:,1] = 0
    return data

def kmeans_clustering(embed, polEmbedding, method):
    print("kmeans_clustering")
    e_kmeans = KMeans(n_clusters=8, random_state=42).fit(embed)
    e_labels = e_kmeans.labels_
    e_proto = e_kmeans.cluster_centers_


    pe_kmeans = KMeans(n_clusters=8, random_state=42).fit(polEmbedding)
    pe_labels = pe_kmeans.labels_
    pe_proto = pe_kmeans.cluster_centers_

    pltFigure(embed, polEmbedding, e_labels, e_proto, pe_labels, pe_proto, 'KMeans', method)


    pe_proto_centers, pe_proto_diff, tranformedPolPixels =  applyTransformation(pe_proto, polEmbedding, pe_labels)
    pe_color = unit_cicle_color_wheel(pe_proto_centers, 'peProto', 'KMEANS', method)
    plt_cluster_img(h5data, pe_labels, 'Polar', 'KMEANS', method, pe_color)

    #all_polar_color = unit_cicle_color_wheel(tranformedPolPixels, 'allPolor', 'KMEANS', method)
    #plt_cluster_img(h5data, tranformedPolPixels, 'allPolar', 'KMEANS', method, all_polar_color)


    e_proto_centers, e_proto_diff, transformedPixels =  applyTransformation(e_proto, embed, e_labels)
    e_color = unit_cicle_color_wheel(e_proto_centers, 'eProto', 'KMEANS', method)
    plt_cluster_img(h5data, e_labels, 'Cartesian', 'KMEANS', method, e_color)

    #all_color = unit_cicle_color_wheel(transformedPixels, 'allCartesien', 'KMEANS', method)
    #plt_cluster_img(h5data, transformedPixels, 'allCartesien', 'KMEANS', method, all_color)
    '''
    #####################TEST##############################
    saveEmbed = np.copy(embed)
    thetaZeroEmbeding = thetaZero(embed)
    theta_kmeans = KMeans(n_clusters=8, random_state=42).fit(thetaZeroEmbeding)
    theta_labels = theta_kmeans.labels_
    thate_proto = theta_kmeans.cluster_centers_

    savepol = np.copy(polEmbedding)
    thetaZeroPolaEmbeding = thetaZero(polEmbedding)
    theta_pol_kmeans = KMeans(n_clusters=8, random_state=42).fit(thetaZeroPolaEmbeding)
    theta_pol_labels = theta_kmeans.labels_
    thate_pol_proto = theta_kmeans.cluster_centers_



    pltFigure(thetaZeroEmbeding, thetaZeroPolaEmbeding, theta_labels, thate_proto, theta_pol_labels, thate_pol_proto, 'KMeans_theta_Zero', method)
    theta_proto_centers, theta_proto_diff, theta_tranformedPolPixels =  applyTransformation(thate_proto, thetaZeroEmbeding, theta_labels)
    theta_color = unit_cicle_color_wheel(theta_proto_centers, 'eProto', 'KMeans_theta_Zero', method)
    plt_cluster_img(h5data, theta_labels, 'Polar', 'KMeans_theta_Zero', method, theta_color)

    radiusZeroEmbeding = radiusZero(saveEmbed)
    radius_kmeans = KMeans(n_clusters=8, random_state=42).fit(radiusZeroEmbeding)
    radius_labels = radius_kmeans.labels_
    radius_proto = radius_kmeans.cluster_centers_

    radiusZeroPolEmbeding = radiusZero(savepol)
    radius_pol_kmeans = KMeans(n_clusters=8, random_state=42).fit(radiusZeroPolEmbeding)
    radius_pol_labels = radius_kmeans.labels_
    radius_pol_proto = radius_kmeans.cluster_centers_
    pltFigure(radiusZeroEmbeding, radiusZeroPolEmbeding, radius_labels, radius_proto, radius_pol_labels, radius_pol_proto, 'KMeans_radius_Zero', method)
    radius_proto_centers, radius_proto_diff, radius_tranformedPolPixels =  applyTransformation(radius_proto, radiusZeroEmbeding, radius_labels)
    radius_color = unit_cicle_color_wheel(radius_proto_centers, 'eProto', 'KMeans_radius_Zero', method)
    plt_cluster_img(h5data, radius_labels, 'Polar', 'KMeans_radius_Zero', method, radius_color)
    '''
    return e_proto_centers, e_labels, pe_proto_centers, pe_labels



def agglomerative_clustering(embed, polarEmbed, method):
    print("agglomerative_clustering")
    num_obj = 7
    e_agglomerative = AgglomerativeClustering(n_clusters=num_obj, affinity='euclidean', linkage='ward').fit(embed)
    e_labels = e_agglomerative.labels_
    e_proto = []
    for l in set(e_labels):
        ind = []
        for i in range(len(embed)):
            if e_labels[i] == l:
                ind.append(embed[i])
        pro = np.mean(ind, axis=0)
        e_proto.append(np.array(pro))

    e_proto = np.array(e_proto)

    pe_agglomerative = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward').fit(polarEmbed)
    pe_labels = pe_agglomerative.labels_
    pe_proto = []
    for l in set(pe_labels):
        ind = []
        for i in range(len(polarEmbed)):
            if pe_labels[i] == l:
                ind.append(polarEmbed[i])
        pro = np.mean(ind, axis=0)
        pe_proto.append(np.array(pro))
    pe_proto = np.array(pe_proto)


    pltFigure(embed, polarEmbed, e_labels, e_proto, pe_labels, pe_proto, 'Agglomerative Clustering', method)
    pe_proto_centers, pe_proto_diff, tranformedPolPixels =  applyTransformation(pe_proto, polarEmbed, pe_labels)
    pe_color = unit_cicle_color_wheel(pe_proto_centers, 'peProto', 'AgglomerativeClustering', method)
    plt_cluster_img(h5data, pe_labels, 'Polar', 'Agglomerative',method,  pe_color)

    #all_polar_color = unit_cicle_color_wheel(tranformedPolPixels, 'allPolor', 'AgglomerativeClustering', method)
    #plt_cluster_img(h5data, tranformedPolPixels, 'allPolar', 'Agglomerative',method, all_polar_color)

    e_proto_centers, e_proto_diff, transformedPixels =  applyTransformation(e_proto, embed, e_labels)
    e_color = unit_cicle_color_wheel(e_proto_centers, 'eProto', 'AgglomerativeClustering', method)
    plt_cluster_img(h5data, e_labels, 'Cartesian', 'Agglomerative',method, e_color)

    #all_color = unit_cicle_color_wheel(transformedPixels, 'allCartesien', 'AgglomerativeClustering', method)
    #plt_cluster_img(h5data, transformedPixels, 'allCartesien', 'Agglomerative',method, all_color)






def affinity_propagation(embed, polarEmbed, method):
    e_affinity  = AffinityPropagation().fit(embed)
    e_labels = e_affinity.labels_
    e_proto = e_affinity.cluster_centers_

    while len(e_proto) > 10:
        e_affinity = AffinityPropagation().fit(e_proto)
        e_proto = e_affinity.cluster_centers_
        e_labels = e_affinity.labels_

    print(e_proto.shape)

    pe_affinity  = AffinityPropagation(damping=0.95).fit(polarEmbed)
    pe_labels = pe_affinity.labels_
    pe_proto = pe_affinity.cluster_centers_
    while len(pe_proto) > 10:
        pe_affinity = AffinityPropagation().fit(pe_proto)
        pe_proto = pe_affinity.cluster_centers_
        pe_labels - pe_affinity.labels_

    print(pe_proto.shape)
    print(labels)


    pltFigure(embed, polarEmbed, e_labels, e_proto, pe_labels, pe_proto, 'Affinity Propagation', method)

def pltFigure(embe, pEmbe, labels, proto, pLabels, pProto, clustering, method):
    print("pltFigure")
    fig = plt.figure()
    plt.title('cluster_Cartesian Cluster in Cartesian with ' + clustering + ' and ' + method)
    for i, l in enumerate(labels):
        plt.plot(embe[i,0], embe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(proto):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('cluster_Cartesian_in_cartesien_' + clustering + '_' + method + '.png')
    plt.close(fig)

    fig = plt.figure()
    plt.title('cluster_Cartesian Cluster in Polar with ' + clustering + ' and ' + method)
    for i, l in enumerate(labels):
        plt.plot(pEmbe[i,0], pEmbe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(cart2polar(proto[:,0], proto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('cluster_Cartesian_in_polar_' + clustering + '_' + method + '.png')
    plt.close(fig)

    fig = plt.figure()
    plt.title('cluster_Polar Cluster in Polar with ' + clustering + ' and ' + method)
    for i, l in enumerate(pLabels):
        plt.plot(pEmbe[i,0], pEmbe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(pProto):

        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('cluster_Polar_in_polar_' + clustering + '_' + method + '.png')
    plt.close(fig)

    fig = plt.figure()
    plt.title('cluster_Polar Cluster in Cartesian with ' + clustering + ' and ' + method)
    for i, l in enumerate(pLabels):
        plt.plot(embe[i,0], embe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(polar2cart(pProto[:,0], pProto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('cluster_Polare_in_cartesien_' + clustering + '_' + method + '.png')
    plt.close(fig)


def normalize(a,b,min,max, x):
    norm = (b-a)*((x-min)/(max-min))+a
    return norm

def transform(centers):
    print("transform")
    maxValue = float('-inf')
    minValue = float('inf')
    for i in range(len(centers)):
        if maxValue <= abs(centers[i][1]):
            maxValue = abs(centers[i][1])
        if minValue >= abs(centers[i][1]):
            minValue = abs(centers[i][1])

    thetaList = []
    for i in range(len(centers)):
        thetaList.append([i,centers[i][0]])
    thetaList = sorted(thetaList, key=lambda x: x[1], reverse=False)

    l = len(centers)
    offset = (2*np.pi) / l
    counter = 0
    for i in range(len(thetaList)):
        if counter == 0:
            thetaList[i].append(offset)
            counter += 1
        else:
            thetaList[i].append(thetaList[i-1][2] + offset)
    thetaList = sorted(thetaList, key=lambda x: x[0], reverse=False)
    newPolEmbe = []
    for i in range(len(thetaList)):
        newPolEmbe.append([thetaList[i][2], normalize(1, 5, minValue, maxValue, abs(centers[i][1]))])


    newPolEmbe = np.array(newPolEmbe)
    differenz = {}
    for i in range(len(centers)):
        diffTheta =  newPolEmbe[i][0] - centers[i][0]
        diffR =  newPolEmbe[i][1] - centers[i][1]
        differenz[i] = [diffTheta, diffR]
    return newPolEmbe, differenz

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

def createJson(h5data, prototyps, labels, embedding):
    print("createJson")
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

    ring_json_list.append((prototyps, ring_idx))

    pixelsPerPrototype, pixels_dict = getPixels(gx, gy, prototyps, labels)
	# get the Prototypes of the ring
    prototyp_idx = 0
    for k in range(len(prototyps)):

        prototyp_dict["prototyp"+str(k)] = {}
		# set the items of the Prototype
        prototyp_dict["prototyp"+str(k)]["pos"] = [posX[k], posY[k]]
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

    pickle.dump(jsonData, open('data.json', 'wb'))
    pickle.dump(canvas, open('dimensions_info.h2som', "wb"))
    for ri in ring_json_list:
        pickle.dump(ri[0], open('data_ring' + str(ri[1]-1) + '.h2som', 'wb'))




 #h2somdata = np.array([[0.45508986056222733, 0.4550898605622273],[3.9408782088522694e-17, 0.6435942529055826],[-0.4550898605622273, 0.45508986056222733],[-0.6435942529055826, 7.881756417704539e-17],[-0.45508986056222744, -0.4550898605622273],[-1.1822634626556806e-16, -0.6435942529055826],[0.4550898605622272, -0.45508986056222744],[0.6435942529055826, -1.5763512835409078e-16]])



kmeans_clustering(umapEmbedding, umapPolar_embedding, 'UMAP')
kmeans_clustering(pcaEmbedding, pcaPolar_embedding, 'PCA')
print('KMEANS is ready')
agglomerative_clustering(pcaEmbedding, pcaPolar_embedding, 'PCA')
agglomerative_clustering(umapEmbedding, umapPolar_embedding, 'UMAP')
print('Agglomerative Clustering is ready')
#Fuck you affinity_propagation i will find u and then i will kill u
#affinity_propagation(pcaEmbedding, pcaPolar_embedding, 'PCA')
#affinity_propagation(umapEmbedding, umapPolar_embedding, 'UMAP')
#print('Affinity Propagation is ready')

#created_json, dimensions, rings = createJson(h5data, umap_e_proto, umap_e_labels, umapEmbedding)
