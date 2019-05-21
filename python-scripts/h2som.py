#from pyclusterbdm.algorithms import H2SOM
#import pyclusterbdm.core as core
from pycluster.algorithms import H2SOM
import pycluster.core as core
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from os import listdir, makedirs
from os.path import join, exists
import json 

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
    

    # 2D positions in on poincare disc
    #print(h2som._pos)

    # Cluster Centroids
    #print(h2som._centroids.shape)

    # H2SOM initialization
    h2som = H2SOM(data)
    
    # H2SOM training
    h2som.cluster()
    #print(h2som._childs.items())

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
    #print(grid_x)
    #print(grid_y)
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
        #print(img)
        plt.imshow(img, cmap="tab20")
    plt.show()

def getPixelsForRing(data, bmu_matches, dframe,ring):
    grid_x = np.array(dframe.index.get_level_values("grid_x"))
    grid_y = np.array(dframe.index.get_level_values("grid_y"))
    
    proto_idx = np.array(range(np.amax(bmu_matches+1)))
    print(proto_idx)
    pixels = []
    pixels_dict = {}
    id = 0
    for i in proto_idx:
        #print(i)
        # Find indices in bmu that matches a specific prototype, i.e. indices of pixels that match a specific prototype
        idx = np.where(bmu_matches == i)[0]
        #print("indexinPrototyp"+str(len(idx)))
        # Get x and y coordinates of the matching pixels
       
        seg_x = grid_x[idx]
     
        seg_y = grid_y[idx]
    
        
        result = list(zip(seg_x, seg_y))
        #print("Pixels:"+str(i))
        pixelIDs = []
        for k in range(0,len(result)):
            #pixelIDs[] = (int(result[k][0]),int(result[k][1]))
            pixelIDs.append("px"+str(id)+"ID")
            pixels_dict["px"+str(id)+"ID"] = {}
            pixels_dict["px"+str(id)+"ID"]["pos"] = (int(result[k][0]),int(result[k][1]))
            id += 1
        
        #print(pixelIDs)
        pixels.append(pixelIDs)
        #pixelIDs = {}
        #print("prototyp"+str(i))
        #print(pixels)
        #allResults.append(pixels)
        #allResults["protottyp"+str(i)] = allResultsPerProto
    #print(len(allResults))
    return pixels, pixels_dict
        

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

def createJson(h2som, data, dframe):
	posRings = {}
	pixelRings = {}
	coefficientsRings = {}
	posX = h2som._pos[:,0]
	posY = h2som._pos[:,1]

	solution = []
	jsonA = {}
	i = 0
	ring_idx = 1
	prototypX ={}
	ringY = {}
	rings= {}
	print(h2som._rings)
	# Get each Ring
	pixels_dict = None
	for ring in h2som._rings:
		membs = calc_memb(data, h2som, ring_idx)
		#print("ALLE PIXEL IN RING: "+str(ring_idx))
		pixelsPerPrototype, pixels_dict = getPixelsForRing(data, membs, dframe,ring)
		ring_idx +=1
		
		#print("Range Rings:")
		#print(ring[0]-1,ring[1]-1)
		#print("Anzahl der berechneten Prototypen mit pixels")
		#print(len(pixelsPerPrototype))
		#print(pixelsPerPrototype[0])
		# get the Prototypes of the ring
		prototyp_idx = 0
		for k in range(ring[0],ring[1]+1):
			prototypX["prototyp"+str(k-1)] = {}
			# set the pos of the Prototype
			prototypX["prototyp"+str(k-1)]["pos"] = [posX[k-1], posY[k-1]]
			#print(type(pixelsPerPrototype[prototyp_idx]))
			prototypX["prototyp"+str(k-1)]["pixel"] = pixelsPerPrototype[prototyp_idx]
			prototypX["prototyp"+str(k-1)]["coefficients"] = []
			# add pos and coefficient to the prototype
			
			prototyp_idx += 1
		# add prtotype to the ring
	    
		ringY["ring"+str(i)]=prototypX
		prototypX = {}
		pixelRings = {}
		coefficientsRings = {}
		posRings = {}
		i +=1
	jsonA["rings"] = ringY
	jsonA["pixels"] = pixels_dict
	jsonA["mzs"] = [x for x in dframe.columns]
	
	for key_px, val_px in jsonA["pixels"].items():
		jsonA["pixels"][key_px]["membership"] = {}
		for key_ring, val_ring in jsonA["rings"].items():
			for prot, val_prot in val_ring.items():
				if key_px in val_prot["pixel"]:
					jsonA["pixels"][key_px]["membership"][key_ring] = prot

	#ring_idx_for_Pixels = 1
	#pixels_Pixels = {}
	#for ring in h2som._rings:
	 #   membsPixel = calc_memb(data, h2som, ring_idx_for_Pixels)
	 #   pixels_Pixels = getPixelsForRing(data,membsPixel, dframe, ring)
	 #   ring_idx_for_Pixels += 1
	    #for y in pixels_Pixels:
		
	#solution.append(jsonA)
	#ding=solution[0]['rings']['ring0']['prototyp0'][1]['pixel']['pixels']['px0ID']
	#print(type(ding[0]), type(ding[1]))
	#with open('solution.txt', 'w') as out2:
	#    out2.writelines(["%s\n" % item  for item in solution])
	with open('data.json', 'w') as outfile:  
	    json.dump(jsonA, outfile)
	#print(solution)
	#print(type(solution), data.dtype, type(dframe), type(h2som))
	
	jsonData= json.dumps(jsonA)
	
	return jsonData
	
	
### Spectral workflow
path = "/home/kwuellems/datasets/barley101.h5"
dframe, data = read_data(path)
### For spatial workflow add:
#data = data.T.copy(order="C")
print(data.shape)
h2som = calc_h2som(data)
membs = calc_memb(data, h2som, 0)
json = createJson(h2som, data, dframe)
#print(json)


spectral_cluster(data, membs, dframe)
#plot_poincare_structure(h2som)
