#include "c_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#if defined(_OPENMP)
#include <omp.h>
#endif
#include <string.h>

#ifdef INTEL_MKL_VERSION
#include <mkl.h>
#else
#include <cblas.h>
#endif
#ifndef M_PI
#define M_PI    3.14159265358979323846
#endif

#if  __cilk >= 200
#define CILK_ENABLED
#endif

#ifndef max
#define max(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a > _b ? _a : _b; })
#endif
		   
#ifndef min
#define min(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })
#endif



/**---									Utility Functions								---**/


#ifdef CILK_ENABLED
int c_bmu(const double* signal,const double* centroids,const int itms,const int dims){
	double dists[itms];
	#pragma omp parallel for
	for(int i=0;i<itms;i++){
		dists[i]=__sec_reduce_add ((signal[0:dims]-centroids[i*dims:dims])*(signal[0:dims]-centroids[i*dims:dims]));
	}
	return __sec_reduce_min_ind(dists[0:itms]);
}
#else
int c_bmu(const double* signal,const double* centroids,const int itms,const int dims){
	double mindist=DBL_MAX;
	int idx=0;
	for(int i=0;i<itms;i++){
		double dist=0.0;
		for(int j=0;j<dims;j++){
			dist+=(signal[j]-centroids[i*dims+j])*(signal[j]-centroids[i*dims+j]);
		}
		if(dist<mindist){
			mindist=dist;
			idx=i;
		}
	}
	return idx;
}
#endif

#ifdef CILK_ENABLED
void c_bmus(const double* signals,const double* centroids,int* idxs,const int signalitms,const int centitms,const int dims){
	#pragma omp parallel for
	for(int sigs=0;sigs<signalitms;sigs++){
		double dists[centitms];
		for(int i=0;i<centitms;i++){
			dists[i]=__sec_reduce_add ((signals[sigs*dims:dims]-centroids[i*dims:dims])*(signals[sigs*dims:dims]-centroids[i*dims:dims]));
		}
		idxs[sigs]=__sec_reduce_min_ind(dists[0:centitms]);
	}
}
#else
void c_bmus(const double* signals,const double* centroids,int* idxs,const int signalitms,const int centitms,const int dims){
	#pragma omp parallel for
	for(int sigs=0;sigs<signalitms;sigs++){
		double mindist=DBL_MAX;
		int idx=0;
		for(int i=0;i<centitms;i++){
			double dist=0.0;
			for(int j=0;j<dims;j++){
				dist+=(signals[sigs*dims+j]-centroids[i*dims+j])*(signals[sigs*dims+j]-centroids[i*dims+j]);
			}
			if(dist<mindist){
				mindist=dist;
				idx=i;
			}
		}
		idxs[sigs]=idx;
	}
}
#endif

#ifdef CILK_ENABLED
void c_mqe(const double* signals,const double* centroids,double* mqe,const int signalitms,const int centitms,const int dims){
	//init variables
	int counter[centitms];
	mqe[0:centitms]=0.0;
	counter[:]=0;
	
	for(int sigs=0;sigs<signalitms;sigs++){
		double dists[centitms];
		for(int i=0;i<centitms;i++){
			dists[i]=__sec_reduce_add ((signals[sigs*dims:dims]-centroids[i*dims:dims])*(signals[sigs*dims:dims]-centroids[i*dims:dims]));
		}
		int idx=__sec_reduce_min_ind(dists[0:centitms]);
		mqe[idx]+=dists[idx];
		counter[idx]+=1;
	}
	for(int i=0;i<centitms;i++){
		if(counter[i]){
			mqe[i]/=counter[i];
		}
	}
}
#else
void c_mqe(const double* signals,const double* centroids,double* mqe,const int signalitms,const int centitms,const int dims){
	//init variables
	int counter[centitms];
	for(int i=0;i<centitms;i++){
		mqe[i]=0.0;
		counter[i]=0;
	}
	
	//find bmu and add up distances
	for(int sigs=0;sigs<signalitms;sigs++){
		double mindist=DBL_MAX;
		int idx=-1;
		for(int i=0;i<centitms;i++){
			double dist=0.0;
			for(int j=0;j<dims;j++){
				dist+=(signals[sigs*dims+j]-centroids[i*dims+j])*(signals[sigs*dims+j]-centroids[i*dims+j]);
			}
			if(dist<mindist){
				mindist=dist;
				idx=i;
			}
		}
		if(idx!=-1){
			mqe[idx]+=mindist;
			counter[idx]++;
		}
	}
	//normalize with numHits
	for(int i=0;i<centitms;i++){
		if(counter[i]){
			mqe[i]/=counter[i];
		}
	}
}
#endif


double hyperdist(const int bmu,const int node,const double *pos){
	double xr=pos[bmu*2];
	double xi=pos[bmu*2+1];
	double yr=pos[node*2];
	double yi=pos[node*2+1];
	return acosh(1. + 2.*( (xr-yr)*(xr-yr) + (xi-yi)*(xi-yi) ) / ((1. - (xr*xr+xi*xi))*(1. - (yr*yr+yi*yi))));
}

#ifdef CILK_ENABLED
void c_adapt(const double* signal,double* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const double curSigma,const double curEpsilon,const double *pos){	
	//update bmu
	centroids[bmu*dim:dim]+= curEpsilon * (signal[0:dim]-centroids[bmu*dim:dim]);
	
	//cu (current upper) and cl (current lower) are the nodes which are adapted at the moment
	int cu=bmu+1;
	int cl=bmu-1;

	//check range
	if (cu>maxRing){
		cu=minRing;
	}
	if (cl<minRing){
		cl=maxRing;
	}
	
	//adapt whole range of nodes. There are 2 times curSigma nodes which are updated
	const int range = max(1.,curSigma);
	for(int i=0;i<range;i++){
		//adapt according to this formular (see paper)
		double upperDist=hyperdist(bmu,cu,pos);
		double lowerDist=hyperdist(bmu,cl,pos);
		double sig=2.0 * curSigma * curSigma;
		double upperdistMod = curEpsilon * exp(-(upperDist*upperDist) / sig);
		double lowerdistMod = curEpsilon * exp(-(lowerDist*lowerDist) / sig);
		centroids[cu*dim:dim]+=upperdistMod * (signal[0:dim] - centroids[cu*dim:dim]);
		centroids[cl*dim:dim]+=upperdistMod * (signal[0:dim] - centroids[cl*dim:dim]);
		//iterate current nodes
		++cu;
		--cl;
		
		//check range
		if (cu>maxRing){
			cu=minRing;
		}
		if (cl<minRing){
			cl=maxRing;
		}
	}
}
#else
void c_adapt(const double* signal,double* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const double curSigma,const double curEpsilon,const double *pos){	
	//update bmu
	for(int j=0;j<dim;j++){
		centroids[bmu*dim+j] += curEpsilon * (signal[j] - centroids[bmu*dim+j]);
	}
	
	//cu (current upper) and cl (current lower) are the nodes which are adapted at the moment
	int cu=bmu+1;
	int cl=bmu-1;

	//check range
	if (cu>maxRing){
		cu=minRing;
	}
	if (cl<minRing){
		cl=maxRing;
	}
	
	//adapt whole range of nodes. There are 2 times curSigma nodes which are updated
	const int range = max(1.,curSigma);
	for(int i=0;i<range;i++){
		
		//adapt according to this formular (see paper)
		double upperDist=hyperdist(bmu,cu,pos);
		double lowerDist=hyperdist(bmu,cl,pos);
		double sig=2.0 * curSigma * curSigma;
		double upperdistMod = curEpsilon * exp(-(upperDist*upperDist) / sig);
		double lowerdistMod = curEpsilon * exp(-(lowerDist*lowerDist) / sig);
		for(int j=0;j<dim;j++){
			centroids[cu*dim+j] += upperdistMod * (signal[j] - centroids[cu*dim+j]);
			centroids[cl*dim+j] += lowerdistMod * (signal[j] - centroids[cl*dim+j]);
		}

		//iterate current nodes
		++cu;
		--cl;
		
		//check range
		if (cu>maxRing){
			cu=minRing;
		}
		if (cl<minRing){
			cl=maxRing;
		}
	}
}
#endif


#ifdef CILK_ENABLED
void c_partial_adapt(const double* signal,double* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const double curSigma,const double curEpsilon,const double *pos){	
	//update bmu
	centroids[bmu*dim:dim]+= curEpsilon * (signal[0:dim]-centroids[bmu*dim:dim]);
	
	//cu (current upper) and cl (current lower) are the nodes which are adapted at the moment
	int cu=bmu+1;
	int cl=bmu-1;

	//check range
	if (cu>maxRing){
		cu=minRing;
	}
	if (cl<minRing){
		cl=maxRing;
	}
	
	//adapt whole range of nodes. There are 2 times curSigma nodes which are updated
	const int range = max(1.,curSigma);
	for(int i=0;i<range;i++){
		//adapt according to this formular (see paper)
		double upperDist=hyperdist(bmu,cu,pos);
		double lowerDist=hyperdist(bmu,cl,pos);
		double sig=2.0 * curSigma * curSigma;
		double upperdistMod = curEpsilon/10 * exp(-(upperDist*upperDist) / sig);
		double lowerdistMod = curEpsilon/10 * exp(-(lowerDist*lowerDist) / sig);
		centroids[cu*dim:dim]+=upperdistMod * (signal[0:dim] - centroids[cu*dim:dim]);
		centroids[cl*dim:dim]+=upperdistMod * (signal[0:dim] - centroids[cl*dim:dim]);
		//iterate current nodes
		++cu;
		--cl;
		
		//check range
		if (cu>maxRing){
			cu=minRing;
		}
		if (cl<minRing){
			cl=maxRing;
		}
	}
}
#else
void c_partial_adapt(const double* signal,double* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const double curSigma,const double curEpsilon,const double *pos){	
	//update bmu
	for(int j=0;j<dim;j++){
		centroids[bmu*dim+j] += curEpsilon * (signal[j] - centroids[bmu*dim+j]);
	}
	
	//cu (current upper) and cl (current lower) are the nodes which are adapted at the moment
	int cu=bmu+1;
	int cl=bmu-1;

	//check range
	if (cu>maxRing){
		cu=minRing;
	}
	if (cl<minRing){
		cl=maxRing;
	}
	
	//adapt whole range of nodes. There are 2 times curSigma nodes which are updated
	const int range = max(1.,curSigma);
	for(int i=0;i<range;i++){
		
		//adapt according to this formular (see paper)
		double upperDist=hyperdist(bmu,cu,pos);
		double lowerDist=hyperdist(bmu,cl,pos);
		double sig=2.0 * curSigma * curSigma;
		double upperdistMod = curEpsilon/100. * exp(-(upperDist*upperDist) / sig);
		double lowerdistMod = curEpsilon/100. * exp(-(lowerDist*lowerDist) / sig);
		for(int j=0;j<dim;j++){
			centroids[cu*dim+j] += upperdistMod * (signal[j] - centroids[cu*dim+j]);
			centroids[cl*dim+j] += lowerdistMod * (signal[j] - centroids[cl*dim+j]);
		}

		//iterate current nodes
		++cu;
		--cl;
		
		//check range
		if (cu>maxRing){
			cu=minRing;
		}
		if (cl<minRing){
			cl=maxRing;
		}
	}
}
#endif

void c_learning(const double *data,double *centroids,const int dim,const unsigned int itms,const unsigned long learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos){
	const int itmrange=maxRing-minRing+1;
		#pragma omp parallel for
		for(int i=0;i<learningSteps;i++){
			curSigma-=sigmaStep;
			curEpsilon-=epsilonStep;
			unsigned int signal=rand()%itms;
			int bmu=minRing+c_bmu(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
			c_adapt(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
		}
}

void c_balanced_learning(const int* s,const double *data,double *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos){
	const int itmrange=maxRing-minRing+1;
		#pragma omp parallel for
		for(int i=0;i<learningSteps;i++){
			curSigma-=sigmaStep;
			curEpsilon-=epsilonStep;
			unsigned int signal=s[i];
			int bmu=minRing+c_bmu(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
			c_adapt(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
		}
}

void c_partial_learning(const double *data,const double *X,const int xsize,double *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos,int * bmuCounter){
	const int itmrange=maxRing-minRing+1;
		#pragma omp parallel for
		for(int i=0;i<learningSteps;i++){
			curSigma-=sigmaStep;
			unsigned int signal=rand()%itms;
			int bmu=minRing+c_bmu(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
			bmuCounter[bmu]++;
			double curEpsilon = 1./sqrt((double)bmuCounter[bmu]);
			c_partial_adapt(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
			unsigned int xsignal = rand()%xsize;
			bmu=minRing+c_bmu(&X[xsignal*dim],&centroids[minRing*dim],itmrange,dim);
			bmuCounter[bmu]++;
			curEpsilon = 1./sqrt((double)bmuCounter[bmu]);
			c_partial_adapt(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
		}
}

void c_label_learning(const double *data,double *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const long *randomlist,const long randlistsize,const double *pos){
	const int itmrange=maxRing-minRing+1;
		for(int i=0;i<learningSteps;i++){
			curSigma-=sigmaStep;
			curEpsilon-=epsilonStep;
			unsigned int signal=randomlist[rand()%randlistsize];
			int bmu=minRing+c_bmu(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
			c_adapt(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
		}
}

int compare_function(const void *a,const void *b) {
	struct Record *x = (struct Record *) a;
	struct Record *y = (struct Record *) b;
	return (int) x->value - y->value;
}


/**---									Neural Gas								---**/

void c_ng_learning(const double *data,double *centroids,const int clusterCnt,const int dim,const int itms,const int learningSteps,double curLambda,const double lambdaStep,double curEpsilon,const double epsilonStep){
	for(int i=0;i<learningSteps;i++){
		curLambda-=lambdaStep;
		curEpsilon-=epsilonStep;
		unsigned int signal=rand()%itms;
		struct Record r_store[clusterCnt]; //needs to be freed?
		for(int j=0;j<clusterCnt;j++){
			double dist=0.0;
			for(int k=0;k<dim;k++){
				dist+=(data[signal*dim+k]-centroids[j*dim+k])*(data[signal*dim+k]-centroids[j*dim+k]);
			}
			r_store[j].key=j;
			r_store[j].value=dist;
		}
		qsort(r_store,clusterCnt,sizeof(struct Record),compare_function);
		for(int j=0;j<clusterCnt;j++){
			int idx=r_store[j].key;
			for(int k=0;k<dim;k++){
				centroids[idx*dim+k]+=curEpsilon * exp(-j / curLambda)*(data[signal*dim+k]-centroids[idx*dim+k]);
			}
		}
	}
}

/**---									KMeans								---**/

void c_kmeans_learning(const double *data,double *centroids,const int clusterCnt,const int dim,const int itms){
	int mov = 1;
	while(mov){
		int idx[itms];
		for(int i=0;i<itms;i++){
			idx[i]=c_bmu(&data[i*dim],centroids,clusterCnt,dim);
		}
	
		//adapt
		double newcents[clusterCnt*dim];
		for(int i=0;i<clusterCnt*dim;i++){
			newcents[i]=0;
		}
		int clusterSize[clusterCnt];
		for(int i=0;i<clusterCnt;i++){
			clusterSize[i]=0;
		}
		for(int i=0;i<itms;i++){
			for(int j=0;j<dim;j++){
				newcents[idx[i]*dim+j]+=data[i*dim+j];
			}
			clusterSize[idx[i]]+=1;
		}
	
		mov = 0;
		for (int i = 0; i < clusterCnt; i++) {
			if (!clusterSize[i]) {
				continue;
			}
			for(int j=0;j<dim;j++){
				newcents[i*dim+j]/=clusterSize[i];
				if (fabs(newcents[i*dim+j] - centroids[i*dim+j]) > 10e-10) {
					mov = 1;
					// probably break and goto just updating
				}
				centroids[i*dim+j]=newcents[i*dim+j];
			}
		}
	}
	// newcents-centroids is possibly negative ! > 10e-10
	// break in stop test is probably breaking everything
	
}

/**---									K-Mer								---**/

int lookup(char c){
	switch (c) {
		case 'a':
			return 0;
			break;
		case 'A':
			return 0;
			break;
		case 'c':
			return 1;
			break;
		case 'C':
			return 1;
			break;
		case 'g':
			return 2;
			break;
		case 'G':
			return 2;
			break;
		case 't':
			return 3;
			break;
		case 'T':
			return 3;
			break;
		default:
			return -1;
			break;
	}
}

void c_kmer(const char* seq,const int len,int *kmers){
	for(int i=0;i<(len-3);i++){
		int idx=(64*lookup(seq[i])+16*lookup(seq[i+1])+4*lookup(seq[i+2])+lookup(seq[i+3]));
		if (idx>-1){
			++kmers[idx];
		}
	}
}

void c_generalkmer(const char* seq,const int len,int *kmers,int K){
	for(int i=0;i<(len-3);i++){
		int idx=0;
		for (int k=0;k<K;k++){
			idx+=pow(4,K-k-1)*lookup(seq[i+k]);
		}
		if (idx>-1){
			++kmers[idx];
		}
	}
}

/**---									H2SOM								---**/

int newNodes(int rings,int spread){
    if (rings==0)
        return 1;
	if (rings==1)
		return spread;
	if (rings==2)
		return spread*(spread-4);
	return newNodes(rings-1,spread)*(spread-4)-newNodes(rings-2,spread);
}

int numNodes(int rings,int spread){
    if (rings==0)
        return 1;
	if(rings==1)
		return spread+1;
	return newNodes(rings,spread)+numNodes(rings-1,spread);
}


//used for sorting the dist2Idx array to get the bmu at position 0
int compare(const void *a,const void *b){
	if ((*(struct dist2Idx*)a).dist < (*(struct dist2Idx*)b).dist){
		return -1;
	} 
	else if((*(struct dist2Idx*)a).dist > (*(struct dist2Idx*)b).dist){
		return 1;
	}
	return 0;
}

//helper function for beam search for details look at <c_beamSearch>
struct dist2Idx c_recBeamSearch(const double* signal,const double* centroids,const struct dist2Idx winner,int **childs,const int *childlen ,const int swidth, int curDepth,int maxDepth, const int dims){
	// if reached bottom ring
	if(curDepth==maxDepth){
		return winner;
	}
	struct dist2Idx distmat[childlen[winner.idx]];
	for(int i=0;i<childlen[winner.idx];i++){
		distmat[i].idx=childs[winner.idx][i];
		distmat[i].dist=0.0;
		for(int j=0;j<dims;j++){
			distmat[i].dist+=(signal[j]-centroids[childs[winner.idx][i]*dims+j])*(signal[j]-centroids[childs[winner.idx][i]*dims+j]);
		}	
	}
	qsort(distmat,childlen[winner.idx],sizeof(struct dist2Idx),compare);
	struct dist2Idx subdists[swidth];
	for(int i=0;i<swidth;i++){
		subdists[i]=c_recBeamSearch(signal,centroids,distmat[i],childs,childlen,swidth,curDepth+1,maxDepth,dims);
	}
	qsort(subdists,swidth,sizeof(struct dist2Idx),compare);
	return subdists[0];
}


//beamSearch
int c_beamSearch(const double* signal,const double* centroids,int **childs,int *childlen,const int spread,int swidth,int maxDepth,const int dims){
	//distmat stores the distance from signal to nodes
	struct dist2Idx distmat[spread];
	
	//compute and store first ring statistics
	for(int i=1;i<spread+1;i++){
		
		//store idx
		distmat[i-1].idx=i;
		
		//compute euclidean distance
		distmat[i-1].dist=0.0;
		for(int j=0;j<dims;j++){
			distmat[i-1].dist+=(signal[j]-centroids[i*dims+j])*(signal[j]-centroids[i*dims+j]);
		}
	}
	
	//sort distmatrix using <compare> (sort using only the distances)
	qsort(distmat,spread,sizeof(struct dist2Idx),compare);
	
	if(maxDepth==1){
	        return distmat[0].idx;
	}
	
	//initialize array with distances for the recursion results
	struct dist2Idx subdists[swidth];
	
	//for the best <swidth> solutions do a recursive beamSearch
	for(int i=0;i<swidth;i++){
		subdists[i]=c_recBeamSearch(signal,centroids,distmat[i],childs,childlen,swidth,1,maxDepth,dims);
	}
	
	//sort distance array to get the bmu at <subdists[0]>
	qsort(subdists,swidth,sizeof(struct dist2Idx),compare);
	return subdists[0].idx;
}

void rotateNode(const double *pos,int iCenter, int iFrom, double *newPos,double fSin,double fCos) {

    double fX1, fX2, fY1, fY2, fU, fV, fQ, fDx, fDy, fTmp;

    fX1 = pos[iCenter*2]; // the center coordinate
    fY1 = pos[iCenter*2+1];

    fX2 = pos[iFrom*2]; // the origin node
    fY2 = pos[iFrom*2+1];

    // apply transform moving center into origin of H2:
    fU = 1.0 - fX1 * fX2 - fY1*fY2;
    fV = fX2 * fY1 - fX1*fY2;
    fQ = fU * fU + fV*fV;
    fDx = fX2 - fX1;
    fDy = fY2 - fY1;
    fX2 = (fDx * fU + fDy * fV) / fQ;
    fY2 = (-fDx * fV + fDy * fU) / fQ;

    // now rotate point 2 by angle about origin:
    fTmp = fCos * fX2 - fSin * fY2;
    fY2 = fSin * fX2 + fCos * fY2;
    fX2 = fTmp;

    // backtransform (replace point 1 by mirror image):
    fU = 1.0 + fX1 * fX2 + fY1*fY2;
    fV = -fX2 * fY1 + fX1*fY2;
    fQ = fU * fU + fV*fV;
    fDx = fX2 + fX1;
    fDy = fY2 + fY1;

    // and finally set the new coordinate
    newPos[0] = (fDx * fU + fDy * fV) / fQ;
    newPos[1] = (-fDx * fV + fDy * fU) / fQ;
}

int addRing(const int first,const int last,const int spread,int *neighborlist,double *pos,double fSin,double fCos) {
	int iCurrent = last + 1;	//ic=9
	neighborlist[last]++;		//last=8		[8,3,3,3,3,3,3,3,4,0]
	neighborlist[iCurrent]++;	//ic=9			[8,3,3,3,3,3,3,3,4,1]
	for (int iCenter = first; iCenter <= last; iCenter++) {
		// find out, how many nodes we have to add
		
		int iNumToAdd = spread - neighborlist[iCenter];		//8-3=5 icent=1
		for (int i = 0; i < iNumToAdd; i++) {
			// set position of current node
			rotateNode(pos,iCenter, iCurrent - 1,&pos[iCurrent*2],fSin,fCos);
			neighborlist[iCurrent]+=3;		//ic=9		[8,3,3,3,3,3,3,3,4,4]
			neighborlist[iCenter]++;		//icent=1	[8,4,3,3,3,3,3,3,4,4]
			iCurrent++;						//ic=10
		}
		if (iCenter!=last){				
			neighborlist[iCurrent-1]++;	//
			neighborlist[iCenter+1]++;
		}
	}
	return iCurrent-1;
}

void c_h2som(const double *data,double *centroids,const int dim,const int items,const int learningSteps,const int numRings,const int spread,const  int swidth,const double sigma,const double sigmaEnd,const double epsilon,const double epsilonEnd){
	//	----------				build Architecture				-----------	//
	//number of Nodes in whole H2SOM
	const int numSomNodes=numNodes(numRings,spread);
	
	//childs stores the indeces of all childs of a node
	//we need this info for all nodes except the last ring
	const int childSize=numNodes(numRings-1,spread);
	int **childs = (int**) malloc(childSize*sizeof(int*));
	
	//positions of H2SOMNODES
	double pos[numSomNodes*2];
	pos[0]=0.0;
	pos[1]=0.0;
	
	//numNeighbors of Node i
	int neighborlist[numSomNodes];
	for(int i=0;i<numSomNodes;i++){
		neighborlist[i]=0;
	}
	neighborlist[0]=spread;
	
	//precomputed constants
	const double fAngle = 2. * M_PI / spread;
	const double fRadius = sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0));
	const double fSin=sin(fAngle);
	const double fCos=cos(fAngle);
	
	
	
	//store num children for each node
	int childlen[numSomNodes];
	
	//stores information about the start/stop idx of each ring
	struct ring rings[numRings];
	
	rings[0].start=rings[0].stop=0;
	
	//fill <rings> with information
	int start=0;
	for(int i=1;i<=numRings;i++){
		int tmp=numNodes(i,spread)-1;
		rings[i].start=start+1;
		rings[i].stop=tmp;
		start=tmp;
	}
	
	//fill childs array
	//fill childlen array
	//add positions of first ring nodes
	childs[0]=(int*) malloc(spread*sizeof(int));
	for(int i=1;i<spread+1;i++){
		childs[0][i-1]=i;
		pos[i*2]=fRadius*cos(i*fAngle);
		pos[i*2+1]=fRadius*sin(i*fAngle);
		neighborlist[i]=3;
	}
		
	//add positions for further rings
	int iFirst = 1;
	int iLast = spread;
	for(int i=1;i<numRings;i++){
		int iLastAdded=addRing(iFirst,iLast,spread,neighborlist,pos,fSin,fCos);
		iFirst=iLast+1;
		iLast=iLastAdded;
	}
		
	int cur = spread+1;
	int marker=spread;
	int doubles[childSize];
	int doublesIdx=0;
	
	for(int i=1;i<childSize;i++){
		if (i==marker){
			childlen[i]=spread-3;
			childs[i]=(int*) malloc((spread-3)*sizeof(int));
			childs[i][0]=marker+1;
			for(int j=0;j<(spread-4);j++){
				childs[i][1+j]=cur+j;
			}
			doubles[doublesIdx++]=marker+1;
			marker=cur+(spread-5);
			cur+=spread-4;
		} else {
			int found=0;
			for(int j=0;j<doublesIdx;j++){
				if(doubles[j]==i){
					found=1;
					break;
				}
			}
			if(found){
				childlen[i]=spread-4;
				childs[i]=(int*) malloc((spread-4)*sizeof(int));
				for(int j=0;j<(spread-4);j++){
					childs[i][j]=cur+j;
				}
				doubles[doublesIdx++]=cur+spread-5;
				cur+=spread-5;
			}else{
				childlen[i]=spread-3;
				childs[i]=(int*) malloc((spread-3)*sizeof(int));
				for(int j=0;j<(spread-3);j++){
					childs[i][j]=cur+j;
				}
				cur+=spread-4;
				doubles[doublesIdx++]=cur;
			}
		}
	}
	
	
	
	
	
	
	
	
	
	//these are the nodes of the last ring they have 0 children
	for(int i=childSize;i<numSomNodes;i++){
		childlen[i]=0;
	}
	
	
	//		---		cluster			---			//
	
	
	//compute mean as initialization of first ring
	double initial[dim];
	for(int i=0;i<dim;i++){
		initial[i]=0.0;
	}
	
	for(int i=0;i<items;i++){
		for(int j=0;j<dim;j++){
			initial[j]+=data[i*dim+j];
		}
	}
	
	for(int i=0;i<dim;i++){
		initial[i]/=items;
	}
	
	//set first ring to initial (mean of data)
	for(int i=0;i<(spread+1);i++){
		for(int j=0;j<dim;j++){
			centroids[i*dim+j]=initial[j];
		}
	}
	
	//train each ring
	for(int i=1;i<=numRings;i++){
		//compute sigma
		double curSigma=sigma;
		double sigStep=(curSigma-sigmaEnd)/learningSteps;
		
		
		//compute epsilon
		double curEpsilon=epsilon;
		double epsStep=(curEpsilon-epsilonEnd)/learningSteps;
		
		
		// compute BMU and update Centroids
		#pragma omp parallel for
		for(int j=0;j<learningSteps;j++){
			//decrease sigma and epsilon with each learning step
			curSigma-=sigStep;
			curEpsilon-=epsStep;
			
			//get random signal
			unsigned int signal=rand()%items;
			
			//get bmu by employing beamSearch
			int bmu=c_beamSearch(&data[signal*dim],centroids,childs,childlen,spread,swidth,i,dim);
			
			//adapt the nodes
			c_adapt(&data[signal*dim],centroids,dim,bmu,rings[i].start,rings[i].stop,curSigma,curEpsilon,pos);
		}

		if (i!=numRings){
			//copy values to child nodes
			for(int j=rings[i].start;j<=rings[i].stop;j++){
				for(int k=0;k<childlen[j];k++){
					memcpy(&centroids[(childs[j][k])*dim],&centroids[j*dim],dim*sizeof(centroids[0]));
				}
			}
		}
	}	
	//after clustering free memory
	for(int i=0;i<childSize;i++){
		if(childs[i]){
			free(childs[i]);
		}
	}
	if(childs){
		free(childs);
	}
}




//		----------------				SOM				---------------------		//


void c_SOMadapt(const double* signal,double* centroids,int centitms,const int dim,const int bmu,const double curSigma,const double curEpsilon,struct SOMnode *nodes){
    for(int i=0;i<centitms;i++){
        double dist=(nodes[bmu].x-nodes[i].x)*(nodes[bmu].x-nodes[i].x)+(nodes[bmu].y-nodes[i].y)*(nodes[bmu].y-nodes[i].y);
        double distMod = curEpsilon * exp(-(dist*dist) / (2.0 * curSigma * curSigma));
        for(int j=0;j<dim;j++){
            centroids[i*dim+j] += distMod * (signal[j] - centroids[i*dim+j]);
        }
    }
}


void c_som(const double *data,double *centroids,const int dim,const int items,const int learningSteps,const int width,const int height,const double sigma,const double sigmaEnd,double epsilon,double epsilonEnd){
    const int centitms=width*height;
    struct SOMnode nodes[centitms];
    
    for(int i=0;i<width;i++){
        for(int j=0;j<height;j++){
            nodes[i*width+j].x=i;
            nodes[i*width+j].y=j;
        }
    }
    
    
    //init SOM
    for(int i=0;i<centitms;i++){
        for(int j=0;j<dim;j++){
            centroids[i*dim+j]=((double)rand())/RAND_MAX;
        }
    }
    
	//compute sigma
	double curSigma=sigma;
	double sigStep=(curSigma-sigmaEnd)/learningSteps;
	
	
	//compute epsilon
	double curEpsilon=epsilon;
	double epsStep=(curEpsilon-epsilonEnd)/learningSteps;
	
	
	//compute BMU and update Centroids
    #pragma omp parallel for
	for(int j=0;j<learningSteps;j++){
		//decrease sigma and epsilon with each learning step
		curSigma-=sigStep;
		curEpsilon-=epsStep;
		
		//get random signal
		unsigned int signal=rand()%items;
		
		//get bmu by employing beamSearch
        int bmu=c_bmu(&data[signal*dim],centroids,centitms,dim);
        
		//adapt the nodes
		c_SOMadapt(&data[signal*dim],centroids,centitms,dim,bmu,curSigma,curEpsilon,nodes);
	}
}


//		----------------				KNN				---------------------		//

void c_knn(const double *data,const double *tdata,const int *lbl,int *testlbl,const int itms,const int testitms,const int dims,const int k){
#pragma omp parallel for
	for(int i=0;i<testitms;i++){
		struct dist2Idx dists[k+1];
		for(int j=0;j<k;j++){
			dists[j].dist=DBL_MAX;
			dists[j].idx=-1;
		}
		for(int j=0;j<itms;j++){
			dists[k].dist=0.0;
			dists[k].idx=j;
			for(int l=0;l<dims;l++){
				dists[k].dist+=(data[j*dims+l]-tdata[i*dims+l])*(data[j*dims+l]-tdata[i*dims+l]);
			}
			qsort(dists,k+1,sizeof(struct dist2Idx),compare);
		}
		for(int m=0;m<(k+1);m++){
			testlbl[i*k+m]=lbl[dists[m].idx];
		}
	}
}


//		----------------				Silhouette Cluster Index				---------------------		//

void c_silhouette(const double *data,const int *labels,const int *itmsPerCluster,const int numClusters,const int itms,const int dims,double *sw){
	// double sw[itms];
#pragma omp parallel for
	for(int i=0;i<itms;i++){
		double dists[numClusters];
		for(int h=0;h<numClusters;h++){
			dists[h]=0.0;
		}
		for(int j=0;j<itms;j++){
			double tmp=0.0;
			for(int k=0;k<dims;k++){
					tmp+=(data[i*dims+k]-data[j*dims+k])*(data[i*dims+k]-data[j*dims+k]);
			}
			dists[labels[j]]+=sqrt(tmp);
		}
		double a=dists[labels[i]]/(itmsPerCluster[labels[i]]-1);
		dists[labels[i]]=DBL_MAX;
		double b=DBL_MAX;
		int idx=-1;
		for(int m=0;m<numClusters;m++){
			if(dists[m]<b){
				b=dists[m];
				idx=m;
			}
		}
		b/=itmsPerCluster[idx];
		double m=a;
		if(b>a){
			m=b;
		}
		sw[i]=(b-a)/m;
	}
	// double s=0;
	// for(int i=0;i<itms;i++){
	// 	s+=sw[i];
	// }	
	// return s/itms;
}

//		----------------				LLM				---------------------		//

void c_outputLLM(const int outputdim,const int dim,const double *A,const double *theta,const double *input,const double *weight,double *outp){
	double v1[dim];
	for(int i=0;i<dim;i++){
		v1[i]=input[i]-weight[i];
	}
	memcpy(outp, theta, sizeof(double)*outputdim);
	cblas_dgemv(CblasRowMajor, CblasNoTrans, outputdim, dim, 1.0,A, dim, v1, 1, 1.0, outp, 1);
}

void c_trainLLM(const int items,const int outputdim,const int dim, const double epsilonStart, const double epsilonStop,const int* labels,const double *data,const double *weight, double *A, double *theta){
	int learningSteps=items*100;
	const double epsStep=((epsilonStart-epsilonStop)/learningSteps);
	double eps=epsilonStart;

	for(int i=0;i<learningSteps;i++){
		const int sig=rand()%items;
		double output[outputdim];
		double outputLLMvec[outputdim];
		for(int j=0;j<outputdim;j++){
			output[j]=0.0;
		}
		output[labels[sig]]=1.0;
		
		c_outputLLM(outputdim,dim,A,theta,&data[sig*dim],weight,outputLLMvec);
		for(int j=0;j<outputdim;j++){
			theta[j]+=eps*(output[j]-outputLLMvec[j]);
		}

		c_outputLLM(outputdim,dim,A,theta,&data[sig*dim],weight,outputLLMvec);
		double v1[outputdim];
		double v2[dim];
		for(int j=0;j<outputdim;j++){
			v1[j]=(output[j]-outputLLMvec[j]);
		}
		for(int j=0;j<dim;j++){
			v2[j]=data[sig*dim+j]-weight[j];
		}
		cblas_dger(CblasRowMajor, outputdim, dim, eps, v1, 1, v2, 1, A, dim);
		eps-=epsStep;
	}
}
	

#include "experimental.c"
#include "c_coref.c"