"""
The core module is the interface to the low level c functions.
Usually you need not to call these but can rely on high level python wrappers in algorithms anc clusterValidation.
"""

import cython
import collections
import sys
import scipy

import numpy as np
cimport numpy as np

cdef extern from "c_core.h":
	cdef struct node:
		long left
		double leftWeight
		long right
		double rightWeight
		

cdef extern int c_bmu(const double* signal,const double* data,const int itms,const int dims)
cdef extern void c_bmus(const double* signals,const double* centroids,int* idxs,const int signalitms,const int centitms,const int dims)
cdef extern void c_mqe(const double* signals,const double* centroids,double* mqe,const int signalitms,const int centitms,const int dims)
cdef extern void c_adapt(const double* signal,double* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const double curSigma,const double curEpsilon,const double *pos)
cdef extern void c_learning(const double* data,double* centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos)
cdef extern void c_partial_learning(const double *data,const double *X,const int xsize,double *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos,int * bmuCounter)
cdef extern void c_label_learning(const double *data,double *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const long *randomlist,const long randlistsize,const double *pos)
cdef extern void c_h2som(const double *data,double *centroids,const int dim,const int items,const int learningSteps,const int numRings,const int spread,const  int swidth,const double sigma,const double sigmaEnd,const double epsilon,const double epsilonEnd)
cdef extern void c_som(const double *data,double *centroids,const int dim,const int items,const int learningSteps,const int width,const int height,const double sigma,const double sigmaEnd,double epsilon,double epsilonEnd)
cdef extern void c_ng_learning(const double *data,double *centroids,const int clusterCnt,const int dim,const int itms,const int learningSteps,double curLambda,const double lambdaStep,double curEpsilon,const double epsilonStep)
cdef extern void c_kmeans_learning(const double *data,double *centroids,const int clusterCnt,const int dim,const int itms)
cdef extern void c_knn(const double *data,const double *tdata,const int *lbl,int *testlbl,const int itms,const int testitms,const int dim,const int k)
cdef extern void c_silhouette(const double *data,const int *labels,const int *itmsPerCluster,const int numClusters,const int itms,const int dim,double *sw)
cdef extern void c_kmer(const char *seq,const int len,int *kmers)
cdef extern void c_generalkmer(const char* seq,const int len,int *kmers,int K)

cdef extern int c_bmuf(const float* signal,const float* data,const int itms,const int dims)
cdef extern void c_bmusf(const float* signals,const float* centroids,int* idxs,const int signalitms,const int centitms,const int dims)
cdef extern void c_mqef(const float* signals,const float* centroids,float* mqe,const int signalitms,const int centitms,const int dims)
cdef extern void c_adaptf(const float* signal,float* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const float curSigma,const float curEpsilon,const float *pos)
cdef extern void c_learningf(const float *data,float *centroids,const int dim,const int itms,const unsigned long learningSteps,const int minRing,const int maxRing,float curSigma,const float sigmaStep,float curEpsilon,const float epsilonStep,const float *pos)
cdef extern void c_label_learningf(const float *data,float *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,float curSigma,const float sigmaStep,float curEpsilon,const float epsilonStep,const long *randomlist,const long randlistsize,const float *pos)
cdef extern void c_h2somf(const float *data,float *centroids,const int dim,const int items,const int learningSteps,const int numRings,const int spread,const  int swidth,const float sigma,const float sigmaEnd,const float epsilon,const float epsilonEnd)
cdef extern void c_somf(const float *data,float *centroids,const int dim,const int items,const int learningSteps,const int width,const int height,const float sigma,const float sigmaEnd,float epsilon,float epsilonEnd)
cdef extern void c_ng_learningf(const float *data,float *centroids,const int clusterCnt,const int dim,const int itms,const int learningSteps,float curLambda,const float lambdaStep,float curEpsilon,const float epsilonStep)
cdef extern void c_kmeans_learningf(const float *data,float *centroids,const int clusterCnt,const int dim,const int itms)
cdef extern void c_knnf(const float *data,const float *tdata,const int *lbl,int *testlbl,const int itms,const int testitms,const int dims,const int k)
cdef extern void c_silhouettef(const float *data,const int *labels,const int *itmsPerCluster,const int numClusters,const int itms,const int dims,float *sw)

cdef extern void c_trainLLM(const int items,const int outputdim,const int dim, const double epsilonStart, const double epsilonStop,const int* labels,const double *data,const double *weight, const double *A,const double *theta)
cdef extern void c_outputLLM(const int outputdim,const int dim,const double *A,const double *theta,const double *input,const double *weight,double *outp)
cdef extern void c_balanced_learning(const int* s,const double *data,double *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos)


# cdef extern int c_NODEh2som(const double *data,double *centroids,const int dim,const int items,const int learningSteps,const int numRings,const int spread,const  int swidth,const double sigma,const double sigmaEnd,const double epsilon,const double epsilonEnd)
# cdef extern void c_NODElearning(const double *data,double *centroids,const int dim,const int itms,const int learningSteps,const double mapWidth,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,node *nodes)
# cdef extern void c_ERRlearning(const double* data,double* centroids,double* err,const int dim,const int itms,const int learningSteps,const double mapWidth,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep)





@cython.boundscheck(False)
@cython.wraparound(False)
def bmu(np.ndarray[double,ndim=1,mode="c"] signal,np.ndarray[double,ndim=2,mode="c"] centroids):
	'''
		bmu(signal,centroids)
		
		Index of Best Matching Unit for a given signal in given centroids.
		
		Computes the index of the BMU aka nearest neighbor using squared euclidean metric.
		
		Parameters
		----------
		signal: ndarray[double], shape(n)
			The signal is the data of which the nearest neighbor should be found.
			
		centroids: ndarray[double], shape(m,n)
			The centroids are the data set in which the nearest neighbors are searched.
			
		Returns
		-------
		out: int
			Index of the BMU
			
		See Also
		--------
		bmuf,bmus,bmusf
			
		Examples
		--------
			>>> signal=np.random.rand(2)
			>>> centroids=np.random.rand(100,2)
			>>> pycluster.core.bmu(signal,centroids)
			35	
	'''
	cdef int m,n
	m, n = centroids.shape[0], centroids.shape[1]
	return c_bmu(&signal[0],&centroids[0,0],m,n)
	
@cython.boundscheck(False)
@cython.wraparound(False)
def bmuf(np.ndarray[float,ndim=1,mode="c"] signal,np.ndarray[float,ndim=2,mode="c"] centroids):
	'''
		bmuf(signal,centroids)
		
		Index of Best Matching Unit for a given signal in given centroids (float version).
		
		Computes the index of the BMU aka nearest neighbor using squared euclidean metric.
		
		Parameters
		----------
		signal: ndarray[float], shape(n)
			The signal is the data of which the nearest neighbor should be found.
			
		centroids: ndarray[float], shape(m,n)
			The centroids are the data set in which the nearest neighbors are searched.
			
		Returns
		-------
		out: int
			Index of the BMU
			
		See Also
		--------
		bmu,bmus,bmusf
			
		Examples
		--------
			>>> signal=np.random.rand(2).astype('float32')
			>>> centroids=np.random.rand(100,2).astype('float32')
			>>> pycluster.core.bmuf(signal,centroids)
			35	
	'''
	cdef int m,n
	m, n = centroids.shape[0], centroids.shape[1]
	return c_bmuf(&signal[0],&centroids[0,0],m,n)

@cython.boundscheck(False)
@cython.wraparound(False)
def bmus(np.ndarray[double,ndim=2,mode="c"] signals,np.ndarray[double,ndim=2,mode="c"] centroids):
	'''
		bmus(signals,centroids)
		
		Inidices of Best Matching Units for a list of given signals in given centroids.
		
		Computes the indices of the BMUs aka nearest neighbors using squared euclidean metric.
		
		Parameters
		----------
		signals: ndarray[float], shape(m,n)
			The signals are the data of which the nearest neighbor should be found.
			
		centroids: ndarray[float], shape(o,n)
			The centroids are the data set in which the nearest neighbors are searched.
			
		Returns
		-------
		out: ndarray[int],shape(m)
			Indices of the BMUs
			
		See Also
		--------
		bmu,bmuf,bmusf
			
		Examples
		--------
			>>> signals=np.random.rand(100,2)
			>>> centroids=np.random.rand(1000,2)
			>>> pycluster.core.bmus(signals,centroids)
			array([376, 294, 213, 493, 551, 181, 612, 379, 840, 549, 996, 238, 491,
			        14, 308, 522, 611, 152, 835, 920, 553, 432, 291, 976, 713, 759,
			       755, 780, 761, 226, 491, 732, 348, 173, 980, 946, 933, 875, 915,
			       127, 434, 734,  97, 354, 651, 330, 805,  25, 794, 714, 631, 718,
			       574, 129, 377, 129, 610, 116, 284, 435, 304, 437, 742, 301, 496,
			        25, 464,  76,  11, 571, 862, 839, 133, 128,  23, 875, 329, 339,
			       595, 243, 712,  13, 454, 770, 573, 343, 214, 969, 448, 175,  50,
			       737, 755, 601, 335, 892, 735, 611,  11, 678], dtype=int32)
	'''
	cdef int m,n,o
	m, n = centroids.shape[0], centroids.shape[1]
	o = signals.shape[0]
	cdef np.ndarray[int,ndim=1,mode="c"] idxs=np.zeros(o,dtype=np.int32)
	c_bmus(&signals[0,0],&centroids[0,0],&idxs[0],o,m,n)
	return idxs

@cython.boundscheck(False)
@cython.wraparound(False)
def bmusf(np.ndarray[float,ndim=2,mode="c"] signals,np.ndarray[float,ndim=2,mode="c"] centroids):
	'''
		bmusf(signals,centroids)
		
		Inidices of Best Matching Units for a list of given signals in given centroids (float version).
		
		Computes the indices of the BMUs aka nearest neighbors using squared euclidean metric. In contrast to bmus function signals and centroids are of type float.
		
		Parameters
		----------
		signals: ndarray[float], shape(m,n)
			The signals are the data of which the nearest neighbors should be found.
			
		centroids: ndarray[float], shape(o,n)
			The centroids are the data set in which the nearest neighbors are searched.
			
		Returns
		-------
		out: ndarray[int],shape(m)
			Indices of the BMUs
			
		See Also
		--------
		bmu,bmuf,bmus
			
		Examples
		--------
			>>> signals=np.random.rand(100,2).astype('float32')
			>>> centroids=np.random.rand(1000,2).astype('float32')
			>>> pycluster.core.bmusf(signals,centroids)
			array([376, 294, 213, 493, 551, 181, 612, 379, 840, 549, 996, 238, 491,
			        14, 308, 522, 611, 152, 835, 920, 553, 432, 291, 976, 713, 759,
			       755, 780, 761, 226, 491, 732, 348, 173, 980, 946, 933, 875, 915,
			       127, 434, 734,  97, 354, 651, 330, 805,  25, 794, 714, 631, 718,
			       574, 129, 377, 129, 610, 116, 284, 435, 304, 437, 742, 301, 496,
			        25, 464,  76,  11, 571, 862, 839, 133, 128,  23, 875, 329, 339,
			       595, 243, 712,  13, 454, 770, 573, 343, 214, 969, 448, 175,  50,
			       737, 755, 601, 335, 892, 735, 611,  11, 678], dtype=int32)
	'''
	cdef int m,n,o
	m, n = centroids.shape[0], centroids.shape[1]
	o = signals.shape[0]
	cdef np.ndarray[int,ndim=1,mode="c"] idxs=np.zeros(o,dtype=np.int32)
	c_bmusf(&signals[0,0],&centroids[0,0],&idxs[0],o,m,n)
	return idxs

@cython.boundscheck(False)
@cython.wraparound(False)
def mqe(np.ndarray[double,ndim=2,mode="c"] signals,np.ndarray[double,ndim=2,mode="c"] centroids,np.ndarray[double,ndim=1,mode="c"] mqe):
	'''
		mqe(signals,centroids,mqe)
		
		Mean Quantization Error for each centroid.
		
		Computes the mean quantization error for each centroid. The mean quantization error is the sum of the distances between a centroid and the signals it represents divided by the number of signals per centroid.
		The mqe serves as a quality measure for the reprensentation of the signals by the centroids.
		
		Parameters
		----------
		signals: ndarray[double], shape(m,n)
			The signals which are reprensented by the centroids.
			
		centroids: ndarray[double], shape(o,n)
			The centroids of which the MQE is computed.
		
		mqe ndarray[double],shape(o):
			Returns the computed mqes for each signal.
			
		Returns
		-------
		-
			
		See Also
		--------
		mqef
			
		Examples
		--------
			>>> signals=np.random.rand(3,2)
			>>> centroids=np.random.rand(15,2)
			>>> mqe=np.zeros(15)
			>>> pycluster.core.mqe(signals,centroids,mqe)
			>>> mqe
			array([ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
			        0.        ,  0.03158062,  0.        ,  0.        ,  0.        ,
			        0.        ,  0.0096769 ,  0.0062308 ,  0.        ,  0.        ])
	'''
	cdef int m,n,o
	m, n = centroids.shape[0], centroids.shape[1]
	o=signals.shape[0]
	c_mqe(&signals[0,0],&centroids[0,0],&mqe[0],o,m,n)
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def mqef(np.ndarray[float,ndim=2,mode="c"] signals,np.ndarray[float,ndim=2,mode="c"] centroids,np.ndarray[float,ndim=1,mode="c"] mqe):
	'''
		mqef(signals,centroids,mqe)
		
		Mean Quantization Error for each centroid.
		
		Computes the mean quantization error for each centroid. The mean quantization error is the sum of the distances between a centroid and the signals it represents divided by the number of signals per centroid.
		The mqe serves as a quality measure for the reprensentation of the signals by the centroids.
		
		Parameters
		----------
		signals: ndarray[float], shape(m,n)
			The signals which are reprensented by the centroids.
			
		centroids: ndarray[float], shape(o,n)
			The centroids of which the MQE is computed.
		
		mqe ndarray[float],shape(o):
			Returns the computed mqes for each signal.
			
		Returns
		-------
		-
			
		See Also
		--------
		mqe
			
		Examples
		--------
		>>> signals=np.random.rand(3,2).astype('float32')
		>>> centroids=np.random.rand(15,2).astype('float32')
		>>> mqe=np.zeros(15).astype('float32')
		>>> pycluster.core.mqef(signals,centroids,mqe)
		>>> mqe
		array([ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
		        0.        ,  0.03158062,  0.        ,  0.        ,  0.        ,
		        0.        ,  0.0096769 ,  0.0062308 ,  0.        ,  0.        ])
	'''
	cdef int m,n,o
	m, n = centroids.shape[0], centroids.shape[1]
	o=signals.shape[0]
	c_mqef(&signals[0,0],&centroids[0,0],&mqe[0],o,m,n)
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def adapt(np.ndarray[double,ndim=1,mode="c"] signal,np.ndarray[double,ndim=2,mode="c"] centroids,int bmu,int minRing,int maxRing,double curSigma,double curEpsilon,np.ndarray[double,ndim=2,mode="c"] pos):
	'''
		adapt(signal,centroids,bmu,minRing,maxRing,curSigma,curEpsilon,pos)
		
		Adaption Function for H2SOM
		
		Adapts the centroids according to [Ontrup2005].
		
		Parameters
		----------
		signal: ndarray[double], shape(n)
			The presented signal in the learning step.
			
		centroids: ndarray[double], shape(m,n)
			The centroids of the H2SOM nodes.
		
		bmu int:
			The BMU computed in the learning step.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga double:
			The current neighborhood adaption range sigma.
			
		curEpsilon double:
			The current adaption step size epsilon.
			
		pos ndarray[double], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		adaptf
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
			
		Examples
		--------
		>>> signal=np.random.rand(2)
		>>> centroids=np.random.rand(9,2)
		>>> pos=np.array([[  0.00000000e+00,   0.00000000e+00],[  4.55089861e-01,   4.55089861e-01],[  3.94087821e-17,   6.43594253e-01],[ -4.55089861e-01,   4.55089861e-01],[ -6.43594253e-01,   7.88175642e-17],[ -4.55089861e-01,  -4.55089861e-01],[ -1.18226346e-16,  -6.43594253e-01],[  4.55089861e-01,  -4.55089861e-01],[  6.43594253e-01,  -1.57635128e-16]])
		>>> pycluster.core.adapt(signal,centroids,3,1,8,8.,1.,pos)
		>>> centroids
		array([[ 0.92990389,  0.71612127],
		       [ 0.67258162,  0.25200621],
		       [ 0.67265366,  0.25108006],
		       [ 0.67272307,  0.25088236],
		       [ 0.67259491,  0.25089111],
		       [ 0.6732766 ,  0.25098389],
		       [ 0.67106019,  0.25363417],
		       [ 0.673211  ,  0.2533806 ],
		       [ 0.67001245,  0.25154977]])
	'''
	cdef int dim
	dim=centroids.shape[1]
	c_adapt(&signal[0],&centroids[0,0],dim,bmu,minRing,maxRing,curSigma,curEpsilon,&pos[0,0])
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def adaptf(np.ndarray[float,ndim=1,mode="c"] signal,np.ndarray[float,ndim=2,mode="c"] centroids,int bmu,int minRing,int maxRing,float curSigma,float curEpsilon,np.ndarray[float,ndim=2,mode="c"] pos):
	'''
		adaptf(signal,centroids,bmu,minRing,maxRing,curSigma,curEpsilon,pos)
		
		Adaption Function for H2SOM
		
		Adapts the centroids according to [Ontrup2005].
		
		Parameters
		----------
		signal: ndarray[float], shape(n)
			The presented signal in the learning step.
			
		centroids: ndarray[float], shape(m,n)
			The centroids of the H2SOM nodes.
		
		bmu int:
			The BMU computed in the learning step.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga float:
			The current neighborhood adaption range sigma.
			
		curEpsilon float:
			The current adaption step size epsilon.
			
		pos ndarray[float], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		adapt
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
			
		Examples
		--------
		>>> signal=np.random.rand(2).astype('float32')
		>>> centroids=np.random.rand(9,2).astype('float32')
		>>> pos=np.array([[  0.00000000e+00,   0.00000000e+00],[  4.55089861e-01,   4.55089861e-01],[  3.94087821e-17,   6.43594253e-01],[ -4.55089861e-01,   4.55089861e-01],[ -6.43594253e-01,   7.88175642e-17],[ -4.55089861e-01,  -4.55089861e-01],[ -1.18226346e-16,  -6.43594253e-01],[  4.55089861e-01,  -4.55089861e-01],[  6.43594253e-01,  -1.57635128e-16]]).astype('float32')
		>>> pycluster.core.adapt(signal,centroids,3,1,8,8.,1.,pos)
		>>> centroids
		array([[ 0.92990389,  0.71612127],
		       [ 0.67258162,  0.25200621],
		       [ 0.67265366,  0.25108006],
		       [ 0.67272307,  0.25088236],
		       [ 0.67259491,  0.25089111],
		       [ 0.6732766 ,  0.25098389],
		       [ 0.67106019,  0.25363417],
		       [ 0.673211  ,  0.2533806 ],
		       [ 0.67001245,  0.25154977]])
	'''
	cdef int dim
	dim=centroids.shape[1]
	c_adaptf(&signal[0],&centroids[0,0],dim,bmu,minRing,maxRing,curSigma,curEpsilon,&pos[0,0])
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,unsigned long learningSteps,int minRing,int maxRing,double curSigma,double sigmaStep,double curEpsilon,double epsilonStep,np.ndarray[double,ndim=2,mode="c"] pos):
	'''
		learning(data,centroids,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,pos)
		
		H2SOM learning algorithm.
		
		H2SOM learning according to [Ontrup2005] employing global search instead of beamSearch.
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the H2SOM.
			
		centroids: ndarray[double], shape(o,n)
			The centroids of the H2SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga double:
			The current neighborhood adaption range sigma.
			
		simgaStep double:
			The value which is subtracted every iteration from curSigma.
			
		curEpsilon double:
			The current adaption step size epsilon.
			
		epsilonStep double:
			The value which is subtracted every iteration from curEpsilon.
			
		pos ndarray[double], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		learningf, adapt, bmu
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_learning(&data[0,0],&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&pos[0,0])
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def balanced_learning(np.ndarray[int,ndim=1,mode="c"] s,np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,int minRing,int maxRing,double curSigma,double sigmaStep,double curEpsilon,double epsilonStep,np.ndarray[double,ndim=2,mode="c"] pos):
	'''
		balanced_learning(data,centroids,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,pos)
		
		H2SOM balanced learning algorithm.
		
		H2SOM learning according to [Ontrup2005] employing global search instead of beamSearch.
		
		Parameters
		----------
		s: ndarray[int], shape(learningSteps)
			The signals which are choosen in each learning step.

		data: ndarray[double], shape(m,n)
			The data which should be learned by the H2SOM.
			
		centroids: ndarray[double], shape(o,n)
			The centroids of the H2SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga double:
			The current neighborhood adaption range sigma.
			
		simgaStep double:
			The value which is subtracted every iteration from curSigma.
			
		curEpsilon double:
			The current adaption step size epsilon.
			
		epsilonStep double:
			The value which is subtracted every iteration from curEpsilon.
			
		pos ndarray[double], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		learningf, adapt, bmu
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_balanced_learning(&s[0],&data[0,0],&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&pos[0,0])
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def partial_learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] X,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,int minRing,int maxRing,double curSigma,double sigmaStep,double curEpsilon,double epsilonStep,np.ndarray[double,ndim=2,mode="c"] pos, np.ndarray[int,ndim=1,mode="c"] bmuCounter):
	'''
		learning(data,centroids,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,pos)
		
		H2SOM learning algorithm.
		
		H2SOM learning according to [Ontrup2005] employing global search instead of beamSearch.
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the H2SOM.
			
		centroids: ndarray[double], shape(o,n)
			The centroids of the H2SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga double:
			The current neighborhood adaption range sigma.
			
		simgaStep double:
			The value which is subtracted every iteration from curSigma.
			
		curEpsilon double:
			The current adaption step size epsilon.
			
		epsilonStep double:
			The value which is subtracted every iteration from curEpsilon.
			
		pos ndarray[double], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		learningf, adapt, bmu
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	xsize = X.shape[0]
	#c_partial_learning(&data[0,0],&X[0,0],xsize,&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&pos[0,0],&bmuCounter[0])
	c_learning(&data[0,0],&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&pos[0,0])
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def learningf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] centroids,int learningSteps,int minRing,int maxRing,float curSigma,float sigmaStep,float curEpsilon,float epsilonStep,np.ndarray[float,ndim=2,mode="c"] pos):
	'''
		learningf(data,centroids,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,pos)
		
		H2SOM learning algorithm.
		
		H2SOM learning according to [Ontrup2005] employing global search instead of beamSearch.
		
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be learned by the H2SOM.
			
		centroids: ndarray[float], shape(o,n)
			The centroids of the H2SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga float:
			The current neighborhood adaption range sigma.
			
		simgaStep float:
			The value which is subtracted every iteration from curSigma.
			
		curEpsilon float:
			The current adaption step size epsilon.
			
		epsilonStep float:
			The value which is subtracted every iteration from curEpsilon.
			
		pos ndarray[float], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		learningf, adapt, bmu
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_learningf(&data[0,0],&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&pos[0,0])
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def lbllearning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,int minRing,int maxRing,double curSigma,double sigmaStep,double curEpsilon,double epsilonStep,np.ndarray[long,ndim=1,mode="c"] randlist,np.ndarray[double,ndim=2,mode="c"] pos):
	'''
		lbllearning(data,centroids,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,randlist,pos)
		
		H2SOM learning algorithm with list of random items to sample from.
		
		H2SOM learning according to [Ontrup2005] employing global search instead of beamSearch modified to use a list of items from which sample from. This gives the opportunity to present underepresented data in the input data set more often.
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the H2SOM.
			
		centroids: ndarray[double], shape(o,n)
			The centroids of the H2SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		minRing int:
			The lower bound of the current H2SOM ring.
			
		maxRing int:
			The upper bound of the current H2SOM ring.
			
		curSimga double:
			The current neighborhood adaption range sigma.
			
		simgaStep double:
			The value which is subtracted every iteration from curSigma.
			
		curEpsilon double:
			The current adaption step size epsilon.
			
		epsilonStep double:
			The value which is subtracted every iteration from curEpsilon.
		
		randlist ndarray[int,shape p]
			A list containing indices of data items.
			
		pos ndarray[double], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
			
		Returns
		-------
		-
			
		See Also
		--------
		lbllearningf,learning,learningf, adapt, bmu
		
		Note
		----
		The items from the randlist are not choosen in order. learningStep items are sampled randomly from the list.
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	randlistsize=randlist.shape[0]
	c_label_learning(&data[0,0],&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&randlist[0],randlistsize,&pos[0,0])
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def lbllearningf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] centroids,int learningSteps,int minRing,int maxRing,float curSigma,float sigmaStep,float curEpsilon,float epsilonStep,np.ndarray[long,ndim=1,mode="c"] randlist,np.ndarray[float,ndim=2,mode="c"] pos):
	'''
		lbllearningf(data,centroids,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,randlist,pos)
	
		H2SOM learning algorithm with list of random items to sample from.
	
		H2SOM learning according to [Ontrup2005] employing global search instead of beamSearch modified to use a list of items from which sample from. This gives the opportunity to present underepresented data in the input data set more often.
	
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be learned by the H2SOM.
		
		centroids: ndarray[float], shape(o,n)
			The centroids of the H2SOM nodes.
	
		learningSteps int:
			Number of iterations for each ring.
		
		minRing int:
			The lower bound of the current H2SOM ring.
		
		maxRing int:
			The upper bound of the current H2SOM ring.
		
		curSimga float:
			The current neighborhood adaption range sigma.
		
		simgaStep float:
			The value which is subtracted every iteration from curSigma.
		
		curEpsilon float:
			The current adaption step size epsilon.
		
		epsilonStep float:
			The value which is subtracted every iteration from curEpsilon.
	
		randlist ndarray[int,shape p]
			A list containing indices of data items.
		
		pos ndarray[float], shape(m,2):
			The positions of the low dimensional H2SOM grid nodes.
		
		Returns
		-------
		-
		
		See Also
		--------
		lbllearning,learning,learningf, adaptf, bmuf
	
		Note
		----
		The items from the randlist are not choosen in order. learningStep items are sampled randomly from the list.
		
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	randlistsize=randlist.shape[0]
	c_label_learningf(&data[0,0],&centroids[0,0],dim,itms,learningSteps,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&randlist[0],randlistsize,&pos[0,0])
	return

# @cython.boundscheck(False)
# @cython.wraparound(False)
# def NODElearning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,double mapWidth,int minRing,int maxRing,double curSigma,double sigmaStep,double curEpsilon,double epsilonStep,np.ndarray[node, ndim=1,mode="c"] pnodes):
# 	cdef int dim,itms
# 	itms,dim=data.shape[0], data.shape[1]
# 	# cdef np.ndarray[node, ndim=1] pnodes = np.zeros(10, np.dtype([('left', np.int),('leftWeight', np.float64),('right', np.int),('rightWeight', np.float64)]))
# 	cdef node [:] nodes = pnodes
# 	c_NODElearning(&data[0,0],&centroids[0,0],dim,itms,learningSteps,mapWidth,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep,&nodes[0])
# 	return
# 
# @cython.boundscheck(False)
# @cython.wraparound(False)
# def ERRlearning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,np.ndarray[double,ndim=1,mode="c"] err,int learningSteps,double mapWidth,int minRing,int maxRing,double curSigma,double sigmaStep,double curEpsilon,double epsilonStep):
# 	cdef int dim,itms
# 	itms,dim=data.shape[0], data.shape[1]
# 	c_ERRlearning(&data[0,0],&centroids[0,0],&err[0],dim,itms,learningSteps,mapWidth,minRing,maxRing,curSigma,sigmaStep,curEpsilon,epsilonStep)
# 	return
# 
# @cython.boundscheck(False)
# @cython.wraparound(False)
# def NODEh2som_learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,int numRings,int spread,int swidth,double sigmaStart,double sigmaEnd,double epsilonStart,double epsilonEnd):
# 	cdef int dim,itms
# 	itms,dim=data.shape[0], data.shape[1]
# 	return c_NODEh2som(&data[0,0],&centroids[0,0],dim,itms,learningSteps,numRings,spread,swidth,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
# 
@cython.boundscheck(False)
@cython.wraparound(False)
def h2sombeam_learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,int numRings,int spread,int swidth,double sigmaStart,double sigmaEnd,double epsilonStart,double epsilonEnd):
	'''
		h2sombeam_learning(data,centroids,learningSteps,numRings,spread,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
		
		H2SOM learning algorithm employing beam search.
		
		H2SOM learning according to [Ontrup2005] employing beam search.
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the H2SOM.
			
		centroids: ndarray[double], shape(o,n)
			The centroids of the H2SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		numRings int:
			The number of rings which should be trained.
			
		spread int:
			The number of neighbors a node should have.
			
		sigmaStart double:
			The value of the neighborhood adaption range at the start of the learning process.
		
		simgaStop double:
			The value of the neighborhood adaption range at the end of the learning process.
		
		epsilonStart double:
			The value of the adaption step size at the start of the learning process.
		
		epsilonStop double:
			The value of the adaption step size at the end of the learning process.
			
		Returns
		-------
		-
			
		See Also
		--------
		h2sombeam_learningf, learning, learningf, lbllearning, lbllearningf
			
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_h2som(&data[0,0],&centroids[0,0],dim,itms,learningSteps,numRings,spread,swidth,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def h2sombeam_learningf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] centroids,int learningSteps,int numRings,int spread,int swidth,float sigmaStart,float sigmaEnd,float epsilonStart,float epsilonEnd):
	'''
		h2sombeam_learning(data,centroids,learningSteps,numRings,spread,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
	
		H2SOM learning algorithm employing beam search.
	
		H2SOM learning according to [Ontrup2005] employing beam search.
	
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be learned by the H2SOM.
		
		centroids: ndarray[float], shape(o,n)
			The centroids of the H2SOM nodes.
	
		learningSteps int:
			Number of iterations for each ring.
		
		numRings int:
			The number of rings which should be trained.
		
		spread int:
			The number of neighbors a node should have.
		
		sigmaStart float:
			The value of the neighborhood adaption range at the start of the learning process.
	
		simgaStop float:
			The value of the neighborhood adaption range at the end of the learning process.
	
		epsilonStart float:
			The value of the adaption step size at the start of the learning process.
	
		epsilonStop float:
			The value of the adaption step size at the end of the learning process.
		
		Returns
		-------
		-
		
		See Also
		--------
		h2sombeam_learning, learning, learningf, lbllearning, lbllearningf
		
		Literature
		----------
		[Ontrup2005] A hierarchically growing hyperbolic self-organizing map for rapid structuring of large data sets - J. Ontrup and H. Ritter 2005
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_h2somf(&data[0,0],&centroids[0,0],dim,itms,learningSteps,numRings,spread,swidth,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def som_learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int learningSteps,int width,int height,double sigmaStart,double sigmaEnd,double epsilonStart,double epsilonEnd):
	'''
		som_learning(data,centroids,learningSteps,width,height,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
		
		SOM learning algorithm.
		
		SOM learning according to [Kohonen1982].
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the SOM.
			
		centroids: ndarray[double], shape(width*height,n)
			The centroids of the SOM nodes.
		
		learningSteps int:
			Number of iterations for each ring.
			
		width int:
			The number of nodes in horizontal direction.
			
		height int:
			The number of nodes in vertical direction.
			
		sigmaStart double:
			The value of the neighborhood adaption range at the start of the learning process.
			
		simgaStop double:
			The value of the neighborhood adaption range at the end of the learning process.
			
		epsilonStart double:
			The value of the adaption step size at the start of the learning process.
			
		epsilonStop double:
			The value of the adaption step size at the end of the learning process.
	
		Returns
		-------
		-
			
		See Also
		--------
		som_learningf
			
		Literature
		----------
		[Kohonen1982] Self-Organized Formation of Topologically Correct Feature Maps - T. Kohonen 1982
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_som(&data[0,0],&centroids[0,0],dim,itms,learningSteps,width,height,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def som_learningf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] centroids,int learningSteps,int width,int height,float sigmaStart,float sigmaEnd,float epsilonStart,float epsilonEnd):
	'''
		som_learningf(data,centroids,learningSteps,width,height,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
	
		SOM learning algorithm.
	
		SOM learning according to [Kohonen1982].
	
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be learned by the SOM.
		
		centroids: ndarray[float], shape(width*height,n)
			The centroids of the SOM nodes.
	
		learningSteps int:
			Number of iterations for each ring.
		
		width int:
			The number of nodes in horizontal direction.
		
		height int:
			The number of nodes in vertical direction.
		
		sigmaStart float:
			The value of the neighborhood adaption range at the start of the learning process.
		
		simgaStop float:
			The value of the neighborhood adaption range at the end of the learning process.
		
		epsilonStart float:
			The value of the adaption step size at the start of the learning process.
		
		epsilonStop float:
			The value of the adaption step size at the end of the learning process.

		Returns
		-------
		-
		
		See Also
		--------
		som_learning
		
		Literature
		----------
		[Kohonen1982] Self-Organized Formation of Topologically Correct Feature Maps - T. Kohonen 1982
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_somf(&data[0,0],&centroids[0,0],dim,itms,learningSteps,width,height,sigmaStart,sigmaEnd,epsilonStart,epsilonEnd)
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def ng_learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int clusterCnt,int learningSteps,double curLambda,double lambdaStep,double curEpsilon,double epsilonStep):
	'''
		ng_learning(data,centroids,clusterCnt,learningSteps,curLambda,lambdaStep,curEpsilon,epsilonStep)
		
		Neural Gas learning algorithm.
		
		Neural Gas learning according to [Martinez1991].
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the NeuralGas algorithm.
		
		centroids: ndarray[double], shape(clusterCnt,n)
			The centroids which are computed by the Neural algorithm.
		
		clusterCnt: int
			Number of clusters.
		
		learningSteps int:
			Number of iterations for each ring.
			
		curLambda double:
			Lambda determines the number of nodes which are significantly updated each adaption step. curLambda ist the value at the start of the learning process.
			
		lambdaStep double:
			The value which is subtracted every iteration from curLambda.
			
		curEpsilon double:
			The current adaption step size epsilon.
	
		epsilonStep double:
			The value which is subtracted every iteration from curEpsilon.
	
		Returns
		-------
		-
			
		See Also
		--------
		ng_learningf
			
		Literature
		----------
		[Martinez1991] A „neural-gas“ network learns topologies - T. Martinez 1991
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_ng_learning(&data[0,0],&centroids[0,0],clusterCnt,dim,itms,learningSteps,curLambda,lambdaStep,curEpsilon,epsilonStep)
	return
	
@cython.boundscheck(False)
@cython.wraparound(False)
def ng_learningf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] centroids,int clusterCnt,int learningSteps,float curLambda,float lambdaStep,float curEpsilon,float epsilonStep):
	'''
		ng_learningf(data,centroids,clusterCnt,learningSteps,curLambda,lambdaStep,curEpsilon,epsilonStep)
	
		Neural Gas learning algorithm.
	
		Neural Gas learning according to [Martinez1991].
	
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be learned by the NeuralGas algorithm.
		
		centroids: ndarray[float], shape(clusterCnt,n)
			The centroids which are computed by the Neural algorithm.
	
		clusterCnt: int
			Number of clusters.
	
		learningSteps int:
			Number of iterations for each ring.
		
		curLambda float:
			Lambda determines the number of nodes which are significantly updated each adaption step. curLambda ist the value at the start of the learning process.
		
		lambdaStep float:
			The value which is subtracted every iteration from curLambda.
		
		curEpsilon float:
			The current adaption step size epsilon.

		epsilonStep float:
			The value which is subtracted every iteration from curEpsilon.

		Returns
		-------
		-
		
		See Also
		--------
		ng_learning
		
		Literature
		----------
		[Martinez1991] A „neural-gas“ network learns topologies - T. Martinez 1991
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_ng_learningf(&data[0,0],&centroids[0,0],clusterCnt,dim,itms,learningSteps,curLambda,lambdaStep,curEpsilon,epsilonStep)
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def kmeans_learning(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] centroids,int clusterCnt):
	'''
		kmeans_learning(data,centroids,clusterCnt)
		
		K-Means learning algorithm.
		
		K-Means learning employing Lloyds method [Lloyd1982].
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be learned by the K-Means algorithm.
			
		centroids: ndarray[double], shape(clusterCnt,n)
			The centroids which are computed by the K-Means algorithm.
		
		clusterCnt: int
			Number of clusters.
	
		Returns
		-------
		-
			
		See Also
		--------
		kmeans_learningf
			
		Literature
		----------
		[Lloyd1982] Least squares quantization in PCM - S.P. Lloyd 1982
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_kmeans_learning(&data[0,0],&centroids[0,0],clusterCnt,dim,itms)
	return

@cython.boundscheck(False)
@cython.wraparound(False)
def kmeans_learningf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] centroids,int clusterCnt):
	'''
		kmeans_learning(data,centroids,clusterCnt)
	
		K-Means learning algorithm.
	
		K-Means learning employing Lloyds method [Lloyd1982].
	
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be learned by the K-Means algorithm.
		
		centroids: ndarray[float], shape(clusterCnt,n)
			The centroids which are computed by the K-Means algorithm.
	
		clusterCnt: int
			Number of clusters.

		Returns
		-------
		-
		
		See Also
		--------
		kmeans_learning
		
		Literature
		----------
		[Lloyd1982] Least squares quantization in PCM - S.P. Lloyd 1982
	'''
	cdef int dim,itms
	itms,dim=data.shape[0], data.shape[1]
	c_kmeans_learningf(&data[0,0],&centroids[0,0],clusterCnt,dim,itms)
	return

	
@cython.boundscheck(False)
@cython.wraparound(False)
def knn(np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[double,ndim=2,mode="c"] tdata,np.ndarray[int,ndim=1,mode="c"] lbl,int k):
	'''
		knn_learning(data,tdata,lbl,k)
		
		K-Nearest-Neighbor classification algorithm.
		
		K-Nearest-Neighbor classification algorithm using simple majority voting.
		
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data which should be classified.
			
		tdata: ndarray[double], shape(o,n)
			The template data which is already labeled and used to classify the data.  
		
		lbl: ndarray[int],shape[o]
			The labels corresponding to tdata.
		
		k: int
			The number of neighbors which are used for determine the label for each data.
	
		Returns
		-------
		out: ndarray[int],shape[m]
			The labels for data computed by knn.
			
		See Also
		--------
		knnf
	'''
	cdef int dim,itms,testitms
	itms,dim=data.shape[0],data.shape[1]
	testitms=tdata.shape[0]
	cdef np.ndarray[int,ndim=2,mode="c"] testlbl=np.zeros((testitms,k),dtype=np.int32)
	c_knn(&data[0,0],&tdata[0,0],&lbl[0],&testlbl[0,0],itms,testitms,dim,k)
	cdef np.ndarray[int,ndim=1,mode="c"] retlbl=np.zeros(testitms,dtype=np.int32)
	for idx,i in enumerate(testlbl):
		retlbl[idx]=collections.Counter(i).most_common(1)[0][0]
	return retlbl
	
@cython.boundscheck(False)
@cython.wraparound(False)
def knnf(np.ndarray[float,ndim=2,mode="c"] data,np.ndarray[float,ndim=2,mode="c"] tdata,np.ndarray[int,ndim=1,mode="c"] lbl,int k):
	'''
		knn_learning(data,tdata,lbl,k)
	
		K-Nearest-Neighbor classification algorithm.
	
		K-Nearest-Neighbor classification algorithm using simple majority voting.
	
		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data which should be classified.
		
		tdata: ndarray[float], shape(o,n)
			The template data which is already labeled and used to classify the data.  
	
		lbl: ndarray[int],shape[o]
			The labels corresponding to tdata.
	
		k: int
			The number of neighbors which are used for determine the label for each data.

		Returns
		-------
		out: ndarray[int],shape[m]
			The labels for data computed by knn.
		
		See Also
		--------
		knn
	'''
	cdef int dim,itms,testitms
	itms,dim=data.shape[0],data.shape[1]
	testitms=tdata.shape[0]
	cdef np.ndarray[int,ndim=2,mode="c"] testlbl=np.zeros((testitms,k),dtype=np.int32)
	c_knnf(&data[0,0],&tdata[0,0],&lbl[0],&testlbl[0,0],itms,testitms,dim,k)
	cdef np.ndarray[int,ndim=1,mode="c"] retlbl=np.zeros(testitms,dtype=np.int32)
	for idx,i in enumerate(testlbl):
		retlbl[idx]=collections.Counter(i).most_common(1)[0][0]
	return retlbl


@cython.boundscheck(False)
@cython.wraparound(False)
def silhouetteWidth(np.ndarray[double,ndim=2,mode="c"] data,dict clusterIdxMap):
	'''
		silhouetteWidth(data,clusterIdxMap)
	
		Silhouette width cluster index.
	
		Computes the silhouette width cluster index for assessing the quality of a clustering result.
	
		Parameters
		----------
		data: ndarray[double], shape(m,n)
			The data used for clustering.
		
		clusterIdxMap: dict
			Listing all centroids which belonged to the original data.

		Returns
		-------
		out: float
			The computed silhouette width.
		
		See Also
		--------
		silhouetteWidthf
	'''
	cdef np.ndarray[double,ndim=1,mode="c"] sw=np.zeros(data.shape[0])
	cdef np.ndarray[int,ndim=1,mode="c"] labels=np.zeros(data.shape[0],dtype=np.int32)
	for i in clusterIdxMap:
		labels[clusterIdxMap[i]]=i
	cdef np.ndarray[int,ndim=1,mode="c"] itmsPerCluster=np.zeros(len(clusterIdxMap),dtype=np.int32)
	for i in clusterIdxMap:
		itmsPerCluster[i]=len(clusterIdxMap[i])
	c_silhouette(&data[0,0],&labels[0],&itmsPerCluster[0],len(clusterIdxMap),data.shape[0],data.shape[1],&sw[0])
	return sw
	
@cython.boundscheck(False)
@cython.wraparound(False)
def silhouetteWidthf(np.ndarray[float,ndim=2,mode="c"] data,dict clusterIdxMap):
	'''
		silhouetteWidthf(data,clusterIdxMap)

		Silhouette width cluster index.

		Computes the silhouette width cluster index for assessing the quality of a clustering result.

		Parameters
		----------
		data: ndarray[float], shape(m,n)
			The data used for clustering.

		clusterIdxMap: dict
			Listing all centroids which belonged to the original data.

		Returns
		-------
		out: float
			The computed silhouette width.

		See Also
		--------
		silhouetteWidth
	'''
	cdef np.ndarray[float,ndim=1,mode="c"] sw=np.zeros(data.shape[0])
	cdef np.ndarray[int,ndim=1,mode="c"] labels=np.zeros(data.shape[0],dtype=np.int32)
	for i in clusterIdxMap:
		labels[clusterIdxMap[i]]=i
	cdef np.ndarray[int,ndim=1,mode="c"] itmsPerCluster=np.zeros(len(clusterIdxMap),dtype=np.int32)
	for i in clusterIdxMap:
		itmsPerCluster[i]=len(clusterIdxMap[i])
	c_silhouettef(&data[0,0],&labels[0],&itmsPerCluster[0],len(clusterIdxMap),data.shape[0],data.shape[1],&sw[0])
	return sw


@cython.boundscheck(False)
@cython.wraparound(False)
def kmer(bytes seq):
	cdef int seqlen
	seqlen=len(seq)
	cdef np.ndarray[int,ndim=1,mode="c"] kmer=np.zeros(256,dtype=np.int32)
	c_kmer(seq,seqlen,&kmer[0])
	norm=np.linalg.norm(kmer)
	cdef np.ndarray[double,ndim=1,mode="c"] retkmer
	if norm:
		retkmer=kmer/norm
	else:
		retkmer=np.zeros(256)
	return retkmer
	

@cython.boundscheck(False)
@cython.wraparound(False)
def genkmer(bytes seq,int K):
	cdef int seqlen
	seqlen=len(seq)
	cdef np.ndarray[int,ndim=1,mode="c"] kmer=np.zeros(4**K,dtype=np.int32)
	c_generalkmer(seq,seqlen,&kmer[0],K)
	norm=np.linalg.norm(kmer)
	cdef np.ndarray[double,ndim=1,mode="c"] retkmer
	if norm:
		retkmer=kmer/norm
	else:
		retkmer=np.zeros(4**K)
	return retkmer

@cython.boundscheck(False)
@cython.wraparound(False)
def helperLLM(int outputdim,np.ndarray[double,ndim=1,mode="c"] weight,np.ndarray[double,ndim=2,mode="c"] data,np.ndarray[int,ndim=1,mode="c"] labels,epsilon):
	cdef int items=data.shape[0]
	cdef int dim=data.shape[1]
	cdef int learningSteps=items*100
	cdef np.ndarray[double,ndim=1,mode="c"] theta=np.random.rand(outputdim)
	cdef np.ndarray[double,ndim=2,mode="c"] A=np.random.rand(outputdim,dim)
	c_trainLLM(items, outputdim, dim, epsilon[0], epsilon[1],&labels[0],&data[0,0],&weight[0], &A[0,0],&theta[0]);
	return A,theta

@cython.boundscheck(False)
@cython.wraparound(False)
def trainLLM(int outputdim,np.ndarray[double,ndim=1,mode="c"] weight,np.ndarray[double,ndim=2,mode="c"] data,labels,epsilon):
	labels=labels.astype(np.int32)
	return helperLLM(outputdim,weight,data,labels,epsilon)

@cython.boundscheck(False)
@cython.wraparound(False)
def outputLLM(int outputdim,np.ndarray[double,ndim=2,mode="c"] A,np.ndarray[double,ndim=1,mode="c"] theta,np.ndarray[double,ndim=1,mode="c"] input,np.ndarray[double,ndim=1,mode="c"] weight):
	cdef int dim=input.shape[0]
	cdef np.ndarray[double,ndim=1,mode="c"] output=np.zeros(outputdim)
	c_outputLLM(outputdim,dim,&A[0,0],&theta[0],&input[0],&weight[0],&output[0])
	return output