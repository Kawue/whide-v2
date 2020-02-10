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
'''
u = UMAP(n_components=2)
umapEmbedding = u.fit_transform(data)
umapPolar_embedding = np.array(cart2polar(umapEmbedding[:,0], umapEmbedding[:,1])).T
'''

pca = PCA(n_components=2)
pcaEmbedding = pca.fit_transform(data)
pcaPolar_embedding = np.array(cart2polar(pcaEmbedding[:,0], pcaEmbedding[:,1])).T

############################################
print('Dim Reduction is ready')
def plt_cluster_img(h5data, labels):
    gx = h5data.index.get_level_values("grid_x")
    gy = h5data.index.get_level_values("grid_y")
    img = np.full((gy.max()+1, gx.max()+1), -1)
    for i, l in enumerate(labels):
        img[(gy[i], gx[i])] = l
    cmap = mplcolors.ListedColormap(["white", "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"])
    bounds=[-1, 0,1,2,3,4,5,6,7,8,9,10]
    norm = mplcolors.BoundaryNorm(bounds, cmap.N)
    plt.figure()
    plt.imshow(img, interpolation='nearest', cmap=cmap, norm=norm)

def unit_cicle_color_wheel(embedding, polar_embedding):
    fig = plt.figure()
    display_axes = fig.add_axes([0.1,0.1,0.8,0.8], projection='polar')
    display_axes._direction = 2*np.pi
    norm = mpl.colors.Normalize(0.0, 2*np.pi)

    # Plot the colorbar onto the polar axis
    # note - use orientation horizontal so that the gradient goes around
    # the wheel rather than center out
    quant_steps = 2056
    cm = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.get_cmap('hsv',quant_steps))

    cb = mpl.colorbar.ColorbarBase(display_axes, cmap=mpl.cm.get_cmap('hsv',quant_steps),
                                    norm=norm,
                                    orientation='horizontal')


    #for x in np.arctan2(embedding[:,0],embedding[:,1]):
    #    print(display_axes.format_coord(x,0.8))

    cb.outline.set_visible(False)
    display_axes.set_axis_off()
    display_axes.plot(polar_embedding[:,0], np.sqrt(polar_embedding[:,1]),"ko")
    '''
    d = polar_embedding[:,0] + np.pi
    colors = cm.to_rgba(d)
    plt.figure()
    plt.imshow(colors[:,None])
    plt.show()
    '''

colors = {0: "tab:blue", 1: "tab:orange", 2: "tab:green", 3: "tab:red", 4: "tab:purple", 5: "tab:brown", 6: "tab:pink", 7: "tab:gray", 8: "tab:olive", 9:"tab:cyan"}

def kmeans_clustering(embed, polEmbedding, method):
    e_kmeans = KMeans(n_clusters=8, random_state=101).fit(embed)
    e_labels = e_kmeans.labels_
    e_proto = e_kmeans.cluster_centers_

    pe_kmeans = KMeans(n_clusters=8, random_state=101).fit(polEmbedding)
    pe_labels = pe_kmeans.labels_
    pe_proto = pe_kmeans.cluster_centers_

    plt.figure()
    plt.title('Cartesian Cluster in Cartesian with KMEANS and ' + method)
    for i, l in enumerate(e_labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(e_proto):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.figure()
    plt.title("Cartesian Cluster in Polar with KMEANS and " + method)
    for i, l in enumerate(e_labels):
        plt.plot(polEmbedding[i,0], polEmbedding[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(cart2polar(e_proto[:,0], e_proto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.figure()
    plt.title("Polar Cluster in Polar with KMEANS and " + method)
    for i, l in enumerate(pe_labels):
        plt.plot(polEmbedding[i,0], polEmbedding[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(pe_proto):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.figure()
    plt.title("Polar Cluster in Cartesian with KMEANS and " + method)
    for i, l in enumerate(pe_labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(polar2cart(pe_proto[:,0], pe_proto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

def agglomerative_clustering(embed, polarEmbed, method):
    e_agglomerative = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward').fit(embed)
    e_labels = e_agglomerative.labels_

    pe_agglomerative = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward').fit(polarEmbed)
    pe_labels = pe_agglomerative.labels_

    plt.figure()
    plt.title('Cartesian Cluster in Cartesian with Agglomerative Clustering and ' + method)
    for i, l in enumerate(e_labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

    plt.figure()
    plt.title("Cartesian Cluster in Polar with Agglomerative Clustering and " + method)
    for i, l in enumerate(e_labels):
        plt.plot(polarEmbed[i,0], polarEmbed[i,1], color=colors[l], marker="x")

    plt.figure()
    plt.title("Polar Cluster in Polar with Agglomerative Clustering and " + method)
    for i, l in enumerate(pe_labels):
        plt.plot(polarEmbed[i,0], polarEmbed[i,1], color=colors[l], marker="x")

    plt.figure()
    plt.title("Polar Cluster in Cartesian with Agglomerative Clustering and " + method)
    for i, l in enumerate(pe_labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

def affinity_propagation(embed, polarEmbed, method):
    e_affinity  = AffinityPropagation().fit(embed)
    e_labels = e_affinity.labels_
    e_proto = e_affinity.cluster_centers_

    ep_affinity  = AffinityPropagation().fit(polarEmbed)
    ep_labels = ep_affinity.labels_
    ep_proto = ep_affinity.cluster_centers_

    plt.figure()
    plt.title('Cartesian Cluster in Cartesian with Affinity Propagation and ' + method)
    for i, l in enumerate(e_labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(e_proto):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.figure()
    plt.title("Cartesian Cluster in Polar with Affinity Propagation and " + method)
    for i, l in enumerate(e_labels):
        plt.plot(polarEmbed[i,0], polarEmbed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(cart2polar(e_proto[:,0], e_proto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.figure()
    plt.title("Polar Cluster in Polar with Affinity Propagation and " + method)
    for i, l in enumerate(pe_labels):
        plt.plot(polarEmbed[i,0], polarEmbed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(pe_proto):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

    plt.figure()
    plt.title("Polar Cluster in Cartesian with Affinity Propagation and " + method)
    for i, l in enumerate(pe_labels):
        plt.plot(embed[i,0], embed[i,1], color=colors[l], marker="x")

    for i, tup in enumerate(np.array(polar2cart(pe_proto[:,0], pe_proto[:,1])).T):
        plt.plot(tup[0], tup[1], color=colors[i], marker="s")

'''
unit_cicle_color_wheel(embedding, polar_embedding)

print("----------------")

unit_cicle_color_wheel(e_proto, np.array(cart2polar(e_proto[:,0], e_proto[:,1])).T)

print("----------------")

unit_cicle_color_wheel(np.array(polar2cart(pe_proto[:,0], pe_proto[:,1])).T, pe_proto)

plt_cluster_img(h5data, e_labels)


plt_cluster_img(h5data, pe_labels)
'''

#kmeans_clustering(umapEmbedding, umapPolar_embedding, 'UMAP')
#kmeans_clustering(pcaEmbedding, pcaPolar_embedding, 'PCA')
#agglomerative_clustering(pcaEmbedding, pcaPolar_embedding, 'PCA')
#agglomerative_clustering(umapEmbedding, umapPolar_embedding, 'UMAP')
affinity_propagation(pcaEmbedding, pcaEmbedding, 'PCA')
plt.show()
