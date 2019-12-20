#include "c_coref.h"

#ifndef M_PI
#define M_PI    3.14159265358979323846f
#endif

/**---									Utility Functions								---**/

#ifdef CILK_ENABLED
int c_bmuf(const float* signal,const float* centroids,const int itms,const int dims){
	float dists[itms];
	#pragma omp parallel for
	for(int i=0;i<itms;i++){
		dists[i]=__sec_reduce_add ((signal[0:dims]-centroids[i*dims:dims])*(signal[0:dims]-centroids[i*dims:dims]));
	}
	return __sec_reduce_min_ind(dists[0:itms]);
}
#else
int c_bmuf(const float* signal,const float* centroids,const int itms,const int dims){
	float mindist=99999.f;
	int idx=0;
	for(int i=0;i<itms;i++){
		float dist=0.f;
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
void c_bmusf(const float* signals,const float* centroids,int* idxs,const int signalitms,const int centitms,const int dims){
	#pragma omp parallel for
	for(int sigs=0;sigs<signalitms;sigs++){
		float dists[centitms];
		for(int i=0;i<centitms;i++){
			dists[i]=__sec_reduce_add ((signals[sigs*dims:dims]-centroids[i*dims:dims])*(signals[sigs*dims:dims]-centroids[i*dims:dims]));
		}
		idxs[sigs]=__sec_reduce_min_ind(dists[0:centitms]);
	}
}
#else
void c_bmusf(const float* signals,const float* centroids,int* idxs,const int signalitms,const int centitms,const int dims){
	#pragma omp parallel for
	for(int sigs=0;sigs<signalitms;sigs++){
		float mindist=FLT_MAX;
		int idx=0;
		for(int i=0;i<centitms;i++){
			float dist=0.f;
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
void c_mqef(const float* signals,const float* centroids,float* mqe,const int signalitms,const int centitms,const int dims){
	//init variables
	int counter[centitms];
	mqe[0:centitms]=0.0;
	counter[:]=0;
	
	for(int sigs=0;sigs<signalitms;sigs++){
		float dists[centitms];
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
void c_mqef(const float* signals,const float* centroids,float* mqe,const int signalitms,const int centitms,const int dims){
	//init variables
	int counter[centitms];
	for(int i=0;i<centitms;i++){
		mqe[i]=0.f;
		counter[i]=0;
	}
	
	//find bmu and add up distances
	for(int sigs=0;sigs<signalitms;sigs++){
		float mindist=FLT_MAX;
		int idx=-1;
		for(int i=0;i<centitms;i++){
			float dist=0.f;
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

float hyperdistf(const int bmu,const int node,const float *pos){
	float xr=pos[bmu*2];
	float xi=pos[bmu*2+1];
	float yr=pos[node*2];
	float yi=pos[node*2+1];
	return acosh(1.f + 2.f*( (xr-yr)*(xr-yr) + (xi-yi)*(xi-yi) ) / ((1.f - (xr*xr+xi*xi))*(1.f - (yr*yr+yi*yi))));
}


#ifdef CILK_ENABLED
void c_adaptf(const float* signal,float* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const float curSigma,const float curEpsilon,const float *pos){	
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
	const int range = max(1.f,curSigma);
	for(int i=0;i<range;i++){
		//adapt according to this formular (see paper)
		float upperDist=hyperdistf(bmu,cu,pos);
		float lowerDist=hyperdistf(bmu,cl,pos);
		float sig=2.f * curSigma * curSigma;
		float upperdistMod = curEpsilon * exp(-(upperDist*upperDist) / sig);
		float lowerdistMod = curEpsilon * exp(-(lowerDist*lowerDist) / sig);
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
void c_adaptf(const float* signal,float* centroids,const int dim,const int bmu,const int minRing, const int maxRing,const float curSigma,const float curEpsilon,const float *pos){	
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
	const int range = max(1.f,curSigma);
	for(int i=0;i<range;i++){
		
		//adapt according to this formular (see paper)
		float upperDist=hyperdistf(bmu,cu,pos);
		float lowerDist=hyperdistf(bmu,cl,pos);
		float sig=2.f * curSigma * curSigma;
		float upperdistMod = curEpsilon * exp(-(upperDist*upperDist) / sig);
		float lowerdistMod = curEpsilon * exp(-(lowerDist*lowerDist) / sig);
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

void c_learningf(const float *data,float *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,float curSigma,const float sigmaStep,float curEpsilon,const float epsilonStep,const float *pos){
	const int itmrange=maxRing-minRing;
	#pragma omp parallel for
	for(int i=0;i<learningSteps;i++){
		curSigma-=sigmaStep;
		curEpsilon-=epsilonStep;
		unsigned int signal=rand()%itms;
		int bmu=minRing+c_bmuf(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
		c_adaptf(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
	}
}

void c_label_learningf(const float *data,float *centroids,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,float curSigma,const float sigmaStep,float curEpsilon,const float epsilonStep,const long *randomlist,const long randlistsize,const float *pos){
	const int itmrange=maxRing-minRing+1;
		for(int i=0;i<learningSteps;i++){
			curSigma-=sigmaStep;
			curEpsilon-=epsilonStep;
			unsigned int signal=randomlist[rand()%randlistsize];
			int bmu=minRing+c_bmuf(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
			c_adaptf(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
		}
}

int compare_functionf(const void *a,const void *b) {
	struct Recordf *x = (struct Recordf *) a;
	struct Recordf *y = (struct Recordf *) b;
	return (int) x->value - y->value;
}


/**---									Neural Gas								---**/

void c_ng_learningf(const float *data,float *centroids,const int clusterCnt,const int dim,const int itms,const int learningSteps,float curLambda,const float lambdaStep,float curEpsilon,const float epsilonStep){
	for(int i=0;i<learningSteps;i++){
		curLambda-=lambdaStep;
		curEpsilon-=epsilonStep;
		unsigned int signal=rand()%itms;
		struct Recordf r_store[clusterCnt]; //needs to be freed?
		for(int j=0;j<clusterCnt;j++){
			float dist=0.f;
			for(int k=0;k<dim;k++){
				dist+=(data[signal*dim+k]-centroids[j*dim+k])*(data[signal*dim+k]-centroids[j*dim+k]);
			}
			r_store[j].key=j;
			r_store[j].value=dist;
		}
		qsort(r_store,clusterCnt,sizeof(struct Recordf),compare_functionf);
		for(int j=0;j<clusterCnt;j++){
			int idx=r_store[j].key;
			for(int k=0;k<dim;k++){
				centroids[idx*dim+k]+=curEpsilon * exp(-j / curLambda)*(data[signal*dim+k]-centroids[idx*dim+k]);
			}
		}
	}
}

/**---									KMeans								---**/

void c_kmeans_learningf(const float *data,float *centroids,const int clusterCnt,const int dim,const int itms){
	int mov = 1;
	while(mov){
		int idx[itms];
		for(int i=0;i<itms;i++){
			idx[i]=c_bmuf(&data[i*dim],centroids,clusterCnt,dim);
		}
	
		//adapt
		float newcents[clusterCnt*dim];
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


/**---									H2SOM								---**/

//used for sorting the dist2Idxf array to get the bmu at position 0
int comparef(const void *a,const void *b){
	if ((*(struct dist2Idxf*)a).dist < (*(struct dist2Idxf*)b).dist){
		return -1;
	} 
	else if((*(struct dist2Idxf*)a).dist > (*(struct dist2Idxf*)b).dist){
		return 1;
	}
	return 0;
}

//helper function for beam search for details look at <c_beamSearchf>
struct dist2Idxf c_recBeamSearchf(const float* signal,const float* centroids,const struct dist2Idxf winner,int **childs,const int *childlen ,const int swidth, int curDepth,int maxDepth, const int dims){
	// if reached bottom ring
	if(curDepth==maxDepth){
		return winner;
	}
	struct dist2Idxf distmat[childlen[winner.idx]];
	for(int i=0;i<childlen[winner.idx];i++){
		distmat[i].idx=childs[winner.idx][i];
		distmat[i].dist=0.f;
		for(int j=0;j<dims;j++){
			distmat[i].dist+=(signal[j]-centroids[childs[winner.idx][i]*dims+j])*(signal[j]-centroids[childs[winner.idx][i]*dims+j]);
		}	
	}
	qsort(distmat,childlen[winner.idx],sizeof(struct dist2Idxf),comparef);
	struct dist2Idxf subdists[swidth];
	for(int i=0;i<swidth;i++){
		subdists[i]=c_recBeamSearchf(signal,centroids,distmat[i],childs,childlen,swidth,curDepth+1,maxDepth,dims);
	}
	qsort(subdists,swidth,sizeof(struct dist2Idxf),comparef);
	return subdists[0];
}


//beamSearch
int c_beamSearchf(const float* signal,const float* centroids,int **childs,int *childlen,const int spread,int swidth,int maxDepth,const int dims){
	//distmat stores the distance from signal to nodes
	struct dist2Idxf distmat[spread];
	
	//compute and store first ring statistics
	for(int i=1;i<spread+1;i++){
		
		//store idx
		distmat[i-1].idx=i;
		
		//compute euclidean distance
		distmat[i-1].dist=0.f;
		for(int j=0;j<dims;j++){
			distmat[i-1].dist+=(signal[j]-centroids[i*dims+j])*(signal[j]-centroids[i*dims+j]);
		}
	}
	
	//sort distmatrix using <compare> (sort using only the distances)
	qsort(distmat,spread,sizeof(struct dist2Idxf),comparef);
	
	if(maxDepth==1){
	        return distmat[0].idx;
	}
	
	//initialize array with distances for the recursion results
	struct dist2Idxf subdists[swidth];
	
	//for the best <swidth> solutions do a recursive beamSearch
	for(int i=0;i<swidth;i++){
		subdists[i]=c_recBeamSearchf(signal,centroids,distmat[i],childs,childlen,swidth,1,maxDepth,dims);
	}
	
	//sort distance array to get the bmu at <subdists[0]>
	qsort(subdists,swidth,sizeof(struct dist2Idxf),comparef);
	return subdists[0].idx;
}

void rotateNodef(const float *pos,int iCenter, int iFrom, float *newPos,float fSin,float fCos) {

    float fX1, fX2, fY1, fY2, fU, fV, fQ, fDx, fDy, fTmp;

    fX1 = pos[iCenter*2]; // the center coordinate
    fY1 = pos[iCenter*2+1];

    fX2 = pos[iFrom*2]; // the origin node
    fY2 = pos[iFrom*2+1];

    // apply transform moving center into origin of H2:
    fU = 1.f - fX1 * fX2 - fY1*fY2;
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
    fU = 1.f + fX1 * fX2 + fY1*fY2;
    fV = -fX2 * fY1 + fX1*fY2;
    fQ = fU * fU + fV*fV;
    fDx = fX2 + fX1;
    fDy = fY2 + fY1;

    // and finally set the new coordinate
    newPos[0] = (fDx * fU + fDy * fV) / fQ;
    newPos[1] = (-fDx * fV + fDy * fU) / fQ;
}

int addRingf(const int first,const int last,const int spread,int *neighborlist,float *pos,float fSin,float fCos) {
	int iCurrent = last + 1;	//ic=9
	neighborlist[last]++;		//last=8		[8,3,3,3,3,3,3,3,4,0]
	neighborlist[iCurrent]++;	//ic=9			[8,3,3,3,3,3,3,3,4,1]
	for (int iCenter = first; iCenter <= last; iCenter++) {
		// find out, how many nodes we have to add
		
		int iNumToAdd = spread - neighborlist[iCenter];		//8-3=5 icent=1
		for (int i = 0; i < iNumToAdd; i++) {
			// set position of current node
			rotateNodef(pos,iCenter, iCurrent - 1,&pos[iCurrent*2],fSin,fCos);
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

void c_h2somf(const float *data,float *centroids,const int dim,const int items,const int learningSteps,const int numRings,const int spread,const  int swidth,const float sigma,const float sigmaEnd,const float epsilon,const float epsilonEnd){
	//	----------				build Architecture				-----------	//
	//number of Nodes in whole H2SOM
	const int numSomNodes=numNodes(numRings,spread);
	
	//childs stores the indeces of all childs of a node
	//we need this info for all nodes except the last ring
	const int childSize=numNodes(numRings-1,spread);
	int **childs = (int**) malloc(childSize*sizeof(int*));
	
	//positions of H2SOMNODES
	float pos[numSomNodes*2];
	pos[0]=0.f;
	pos[1]=0.f;
	
	//numNeighbors of Node i
	int neighborlist[numSomNodes];
	for(int i=0;i<numSomNodes;i++){
		neighborlist[i]=0;
	}
	neighborlist[0]=spread;
	
	//precomputed constants
	const float fAngle = 2.f * M_PI / spread;
	const float fRadius = sqrt(1.f - 4.f * pow(sin(M_PI / spread), 2.f));
	const float fSin=sin(fAngle);
	const float fCos=cos(fAngle);
	
	
	
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
		int iLastAdded=addRingf(iFirst,iLast,spread,neighborlist,pos,fSin,fCos);
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
	float initial[dim];
	for(int i=0;i<dim;i++){
		initial[i]=0.f;
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
		float curSigma=sigma;
		float sigStep=(curSigma-sigmaEnd)/learningSteps;
		
		
		//compute epsilon
		float curEpsilon=epsilon;
		float epsStep=(curEpsilon-epsilonEnd)/learningSteps;
		
		
		// compute BMU and update Centroids
		#pragma omp parallel for
		for(int j=0;j<learningSteps;j++){
			//decrease sigma and epsilon with each learning step
			curSigma-=sigStep;
			curEpsilon-=epsStep;
			
			//get random signal
			unsigned int signal=rand()%items;
			
			//get bmu by employing beamSearch
			int bmu=c_beamSearchf(&data[signal*dim],centroids,childs,childlen,spread,swidth,i,dim);
			
			//adapt the nodes
			c_adaptf(&data[signal*dim],centroids,dim,bmu,rings[i].start,rings[i].stop,curSigma,curEpsilon,pos);
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


void c_SOMadaptf(const float* signal,float* centroids,int centitms,const int dim,const int bmu,const float curSigma,const float curEpsilon,struct SOMnodef *nodes){
    for(int i=0;i<centitms;i++){
        float dist=(nodes[bmu].x-nodes[i].x)*(nodes[bmu].x-nodes[i].x)+(nodes[bmu].y-nodes[i].y)*(nodes[bmu].y-nodes[i].y);
        float distMod = curEpsilon * exp(-(dist*dist) / (2.f * curSigma * curSigma));
        for(int j=0;j<dim;j++){
            centroids[i*dim+j] += distMod * (signal[j] - centroids[i*dim+j]);
        }
    }
}


void c_somf(const float *data,float *centroids,const int dim,const int items,const int learningSteps,const int width,const int height,const float sigma,const float sigmaEnd,float epsilon,float epsilonEnd){
    const int centitms=width*height;
    struct SOMnodef nodes[centitms];
    
    for(int i=0;i<width;i++){
        for(int j=0;j<height;j++){
            nodes[i*width+j].x=i;
            nodes[i*width+j].y=j;
        }
    }
    
    
    //init SOM
    for(int i=0;i<centitms;i++){
        for(int j=0;j<dim;j++){
            centroids[i*dim+j]=((float)rand())/RAND_MAX;
        }
    }
    
	//compute sigma
	float curSigma=sigma;
	float sigStep=(curSigma-sigmaEnd)/learningSteps;
	
	
	//compute epsilon
	float curEpsilon=epsilon;
	float epsStep=(curEpsilon-epsilonEnd)/learningSteps;
	
	
	//compute BMU and update Centroids
    #pragma omp parallel for
	for(int j=0;j<learningSteps;j++){
		//decrease sigma and epsilon with each learning step
		curSigma-=sigStep;
		curEpsilon-=epsStep;
		
		//get random signal
		unsigned int signal=rand()%items;
		
		//get bmu by employing beamSearch
        int bmu=c_bmuf(&data[signal*dim],centroids,centitms,dim);
        
		//adapt the nodes
		c_SOMadaptf(&data[signal*dim],centroids,centitms,dim,bmu,curSigma,curEpsilon,nodes);
	}
}

//		----------------				KNN				---------------------		//

void c_knnf(const float *data,const float *tdata,const int *lbl,int *testlbl,const int itms,const int testitms,const int dims,const int k){
#pragma omp parallel for
	for(int i=0;i<testitms;i++){
		struct dist2Idxf dists[k+1];
		for(int j=0;j<k;j++){
			dists[j].dist=FLT_MAX;
			dists[j].idx=-1;
		}
		for(int j=0;j<itms;j++){
			dists[k].dist=0.f;
			dists[k].idx=j;
			for(int l=0;l<dims;l++){
				dists[k].dist+=(data[j*dims+l]-tdata[i*dims+l])*(data[j*dims+l]-tdata[i*dims+l]);
			}
			qsort(dists,k+1,sizeof(struct dist2Idxf),comparef);
		}
		for(int m=0;m<(k+1);m++){
			testlbl[i*k+m]=lbl[dists[m].idx];
		}
	}
}


//		----------------				Silhouette Cluster Index				---------------------		//

void c_silhouettef(const float *data,const int *labels,const int *itmsPerCluster,const int numClusters,const int itms,const int dims,float *sw){
	// float sw[itms];
#pragma omp parallel for
	for(int i=0;i<itms;i++){
		float dists[numClusters];
		for(int h=0;h<numClusters;h++){
			dists[h]=0.f;
		}
		for(int j=0;j<itms;j++){
			float tmp=0.f;
			for(int k=0;k<dims;k++){
					tmp+=(data[i*dims+k]-data[j*dims+k])*(data[i*dims+k]-data[j*dims+k]);
			}
			dists[labels[j]]+=sqrt(tmp);
		}
		float a=dists[labels[i]]/(itmsPerCluster[labels[i]]-1);
		dists[labels[i]]=FLT_MAX;
		float b=FLT_MAX;
		int idx=-1;
		for(int m=0;m<numClusters;m++){
			if(dists[m]<b){
				b=dists[m];
				idx=m;
			}
		}
		b/=itmsPerCluster[idx];
		float m=a;
		if(b>a){
			m=b;
		}
		sw[i]=(b-a)/m;
	}
	// float s=0;
	// for(int i=0;i<itms;i++){
	// 	s+=sw[i];
	// }	
	// return s/itms;
}



