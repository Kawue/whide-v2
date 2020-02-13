import numpy as np
from umap import UMAP
import pandas as pd
from sys import argv
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import colors as mplcolors
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import AffinityPropagation

def cart2polar(x,y):
    theta = np.arctan2(y,x)
    r = np.sqrt(x**2 + y**2)
    return theta, r

def polar2cart(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

h5data = pd.read_hdf(argv[1])
data = h5data.values

# Dimension reduction
############################################

u = UMAP(n_components=2)
umapEmbedding = u.fit_transform(data)
umapPolar_embedding = np.array(cart2polar(umapEmbedding[:,0], umapEmbedding[:,1])).T


pca = PCA(n_components=2)
pcaEmbedding = pca.fit_transform(data)
pcaPolar_embedding = np.array(cart2polar(pcaEmbedding[:,0], pcaEmbedding[:,1])).T

############################################
print('Dim Reduction is ready')
def plt_cluster_img(h5data, labels, cartOrPolar, cluster, method, color):
    gx = h5data.index.get_level_values("grid_x")
    gy = h5data.index.get_level_values("grid_y")
    img = np.full((gy.max()+1, gx.max()+1), -1)
    for i, l in enumerate(labels):
        img[(gy[i], gx[i])] = l
    cmap = mplcolors.ListedColormap(color)
    #cmap = mplcolors.ListedColormap(["white", "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"])
    bounds=[-1, 0,1,2,3,4,5,6,7,8,9,10]
    norm = mplcolors.BoundaryNorm(bounds, cmap.N)
    fig = plt.figure()
    plt.imshow(img, interpolation='nearest', cmap=cmap, norm=norm)
    plt.savefig('Segmentation_' + cartOrPolar + '_' + cluster + '_'   + method + '.png')
    plt.close(fig)

def unit_cicle_color_wheel(centers, cartOrPolar, method, cluster):

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

def kmeans_clustering(embed, polEmbedding, method):
    e_kmeans = KMeans(n_clusters=8, random_state=42).fit(embed)
    e_labels = e_kmeans.labels_
    e_proto = e_kmeans.cluster_centers_


    pe_kmeans = KMeans(n_clusters=8, random_state=42).fit(polEmbedding)
    pe_labels = pe_kmeans.labels_
    pe_proto = pe_kmeans.cluster_centers_

    #pltFigure(embed, polEmbedding, e_labels, e_proto, pe_labels, pe_proto, 'KMeans', method)


    pe_proto_centers, pe_proto_diff = transform(pe_proto)
    pe_color = unit_cicle_color_wheel(pe_proto_centers, 'peProto', 'KMEANS', method)

    e_proto_centers, e_proto_diff = transform(e_proto)
    e_color = unit_cicle_color_wheel(e_proto_centers, 'eProto', 'KMEANS', method)
    #plt_cluster_img(h5data, e_labels, 'Cartesian', 'KMEANS', method, e_color)
    #plt_cluster_img(h5data, pe_labels, 'Polar', 'KMEANS', method, pe_color)

    all_pol_emb = []
    for l in set(pe_labels):
        for i in range(len(polEmbedding)):
            if(pe_labels[i] == l):
                diff = pe_proto_diff[l]
                current = polEmbedding[i]
                t = current[0] + diff[0]
                r = current[1] + diff[1]
                all_pol_emb.append([t,r])

    tranformedPolPixels = np.array(all_pol_emb)
    all_polar_color = unit_cicle_color_wheel(tranformedPolPixels, 'allPolor', 'KMEANS', method)


    all_emb = []
    for l in set(e_labels):
        for i in range(len(embed)):
            if(e_labels[i] == l):
                diff = e_proto_diff[l]
                current = embed[i]
                t = current[0] + diff[0]
                r = current[1] + diff[1]
                all_emb.append([t,r])
    transformedPixels = np.array(all_emb)
    all_color = unit_cicle_color_wheel(transformedPixels, 'allCartesien', 'KMEANS', method)




def agglomerative_clustering(embed, polarEmbed, method):
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


    #pltFigure(embed, polarEmbed, e_labels, e_proto, pe_labels, pe_proto, 'Agglomerative Clustering', method)

    pe_proto_centers, pe_proto_diff = transform(pe_proto)
    pe_color = unit_cicle_color_wheel(pe_proto_centers, 'peProto', 'AgglomerativeClustering', method)

    e_proto_centers, e_proto_diff = transform(e_proto)
    e_color = unit_cicle_color_wheel(e_proto_centers, 'eProto', 'AgglomerativeClustering', method)

    #plt_cluster_img(h5data, e_labels, 'Cartesian', 'Agglomerative',method, e_color)
    #plt_cluster_img(h5data, pe_labels, 'Polar', 'Agglomerative',method,  pe_color)
    all_pol_emb = []
    for l in set(pe_labels):
        for i in range(len(polarEmbed)):
            if(pe_labels[i] == l):
                diff = pe_proto_diff[l]
                current = polarEmbed[i]
                t = current[0] + diff[0]
                r = current[1] + diff[1]
                all_pol_emb.append([t,r])

    tranformedPolPixels = np.array(all_pol_emb)
    all_polar_color = unit_cicle_color_wheel(tranformedPolPixels, 'allPolor', 'AgglomerativeClustering', method)


    all_emb = []
    for l in set(e_labels):
        for i in range(len(embed)):
            if(e_labels[i] == l):
                diff = e_proto_diff[l]
                current = embed[i]
                t = current[0] + diff[0]
                r = current[1] + diff[1]
                all_emb.append([t,r])
    transformedPixels = np.array(all_emb)
    all_color = unit_cicle_color_wheel(transformedPixels, 'allCartesien', 'AgglomerativeClustering', method)



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


    pltFigure(embed, polarEmbed, e_labels, e_proto, pe_labels, pe_proto, 'Affinity Propagation', method)

def pltFigure(embe, pEmbe, labels, proto, pLabels, pProto, clustering, method):
    fig = plt.figure()
    plt.title('Cartesian Cluster in Cartesian with ' + clustering + ' and ' + method)
    for i, l in enumerate(labels):
        plt.plot(embe[i,0], embe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(proto):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('Cartesian_in_cartesien_' + clustering + '_' + method + '.png')
    plt.close(fig)

    fig = plt.figure()
    plt.title('Cartesian Cluster in Polar with ' + clustering + ' and ' + method)
    for i, l in enumerate(labels):
        plt.plot(pEmbe[i,0], pEmbe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(cart2polar(proto[:,0], proto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('Cartesian_in_polar_' + clustering + '_' + method + '.png')
    plt.close(fig)

    fig = plt.figure()
    plt.title('Polar Cluster in Polar with ' + clustering + ' and ' + method)
    for i, l in enumerate(pLabels):
        plt.plot(pEmbe[i,0], pEmbe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(pProto):

        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('Polar_in_polar_' + clustering + '_' + method + '.png')
    plt.close(fig)

    fig = plt.figure()
    plt.title('Polar Cluster in Cartesian with ' + clustering + ' and ' + method)
    for i, l in enumerate(pLabels):
        plt.plot(embe[i,0], embe[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(polar2cart(pProto[:,0], pProto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.savefig('Polare_in_cartesien_' + clustering + '_' + method + '.png')
    plt.close(fig)


def normalize(a,b,min,max, x):
    norm = (b-a)*((x-min)/(max-min))+a
    return norm

def transform(centers):
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
#unit_cicle_color_wheel(pcaEmbedding, pcaPolar_embedding)
'''
print("----------------")

unit_cicle_color_wheel(e_proto, np.array(cart2polar(e_proto[:,0], e_proto[:,1])).T)

print("----------------")

unit_cicle_color_wheel(np.array(polar2cart(pe_proto[:,0], pe_proto[:,1])).T, pe_proto)

'''

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
