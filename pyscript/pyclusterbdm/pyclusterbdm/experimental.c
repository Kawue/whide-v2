int c_ERRbmu(const double* signal,const double* centroids,const int itms,const int dims,double *mdist){
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
	*mdist=mindist;
	return idx;
}


void c_ERRlearning(const double *data,double *centroids,double* err,const int dim,const int itms,const int learningSteps,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,const double *pos){
	const int itmrange=maxRing-minRing+1;
	#pragma omp parallel for
	for(int i=0;i<learningSteps;i++){
		curSigma-=sigmaStep;
		curEpsilon-=epsilonStep;
		unsigned int signal=rand()%itms;
		double dist;
		int bmu=minRing+c_ERRbmu(&data[signal*dim],&centroids[minRing*dim],itmrange,dim,&dist);
		err[bmu]+=dist;
		c_adapt(&data[signal*dim],centroids,dim,bmu,minRing,maxRing,curSigma,curEpsilon,pos);
	}
}



// //		----------------				NODE-H2SOM				---------------------		//
// 
// 
// 
// void c_NODEadapt(const double* signal,double* centroids,const int dim,const double mapWidth,const int bmu,const int minRing, const int maxRing,const double curSigma,const double curEpsilon,struct node *nodes){	
// 	//update bmu
//     for(int j=0;j<dim;j++){
//          centroids[bmu*dim+j] += curEpsilon * (signal[j] - centroids[bmu*dim+j]);
//     }
// 	
// 	//cu (current upper) and cl (current lower) are the nodes which are adapted at the moment
// 	int cu=nodes[bmu].right;
// 	int cl=nodes[bmu].left;
// 	//adapt whole range of nodes. There are 2 times curSigma nodes which are updated
// 	const int range = curSigma;
// 	for(int i=0;i<range;i++){
// 		//adapt according to this formular (see paper)
// 		double distMod = curEpsilon * exp(-(mapWidth*(i+1)*mapWidth*(i+1)) / (2.0 * curSigma * curSigma));
// 		for(int j=0;j<dim;j++){
// 			centroids[cu*dim+j] += nodes[cu].rightWeight * distMod * (signal[j] - centroids[cu*dim+j]);
// 			centroids[cl*dim+j] += nodes[cl].leftWeight * distMod * (signal[j] - centroids[cl*dim+j]);
// 		}
// 		cu=nodes[cu].right;
// 		cl=nodes[cl].left;
// 	}
// }
// 
// 
// 
// void c_NODElearning(const double *data,double *centroids,const int dim,const int itms,const int learningSteps,const double mapWidth,const int minRing,const int maxRing,double curSigma,const double sigmaStep,double curEpsilon,const double epsilonStep,struct node *nodes){
// 	const int itmrange=maxRing-minRing+1;
// 	#pragma omp parallel for
// 	for(int i=0;i<learningSteps;i++){
// 		curSigma-=sigmaStep;
// 		curEpsilon-=epsilonStep;
// 		unsigned int signal=rand()%itms;
// 		int bmu=minRing+c_bmu(&data[signal*dim],&centroids[minRing*dim],itmrange,dim);
// 		c_NODEadapt(&data[signal*dim],centroids,dim,mapWidth,bmu,minRing,maxRing,curSigma,curEpsilon,nodes);
// 	}
// }
// 
// 
// 
// 
// 
// int c_NODEh2som(const double *data,double *centroids,const int dim,const int items,const int learningSteps,const int numRings,const int spread,const  int swidth,const double sigma,const double sigmaEnd,const double epsilon,const double epsilonEnd){
// 	//	----------				build Architecture				-----------	//
// 	const double MIN_BORDER=0.1;
// 	const double MAX_BORDER=2.0;
// 	const int MIN_ADDEDNODES=0;
// 	const int MAX_ADDEDNODES=spread;
// 	
// 	
// 	//nodes are equidistant with distance mapWidth
// 	const double mapWidth = acosh(1.0 + 2.0 * (sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) * cos(2.0 *M_PI / spread) * sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) * cos(2.0 * M_PI / spread) + sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) * cos(2.0 * M_PI / spread) * sqrt(1.0 - 4.0 *pow(sin(M_PI / spread), 2.0)) * cos(2.0 * M_PI / spread)) / (1.0 - (sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) * cos(2.0 * M_PI / spread) * sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) * cos(2.0 * M_PI / spread) + sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) * cos(2.0 * M_PI / spread) * sqrt(1.0 - 4.0 * pow(sin(M_PI / spread), 2.0)) *cos(2.0 * M_PI / spread))));
// 	
// 	//set up variables
// 	
// 	//number of Nodes in whole H2SOM
// 	const int numSomNodes=numNodes(numRings,MAX_ADDEDNODES);
// 	
// 	//structure for storing links and weights to neighbors
// 	struct node nodes[numSomNodes+1];
// 	
// 	
// 	//childs stores the indeces of all childs of a node
// 	//we need this info for all nodes except the last ring
// 	const int childSize=numSomNodes;
// 	int **childs = (int**) malloc(childSize*sizeof(int*));
// 		
// 	//store num children for each node
// 	int childlen[numSomNodes];
// 	
// 	//stores information about the start/stop idx of each ring
// 	struct ring rings[numRings];
// 	
// 	rings[0].start=rings[0].stop=0;
// 	
// 	//fill <rings> with information
// 	rings[1].start=1;
// 	rings[1].stop=spread;
// 	for(int j=rings[1].start+1;j<rings[1].stop;j++){
// 		nodes[j].left=j-1;
// 		nodes[j].right=j+1;
// 		nodes[j].leftWeight=1.0;
// 		nodes[j].rightWeight=1.0;
// 	}
// 	nodes[rings[1].start].left=rings[1].stop;
// 	nodes[rings[1].start].right=rings[1].start+1;
// 	nodes[rings[1].start].leftWeight=1.0;
// 	nodes[rings[1].start].rightWeight=1.0;
// 	nodes[rings[1].stop].left=rings[1].stop-1;
// 	nodes[rings[1].stop].right=rings[1].start;
// 	nodes[rings[1].stop].leftWeight=1.0;
// 	nodes[rings[1].stop].rightWeight=1.0;
// 	
// 	// int start=0;
// 	// for(int i=1;i<=numRings;i++){
// 	// 	int tmp=numNodes(i,spread);
// 	// 	rings[i].start=1
// 	// 	rings[i].stop=tmp;
// 	// 	start=tmp;
// 	// 	for(int j=rings[i].start+1;j<rings[i].stop;j++){
// 	// 		nodes[j].left=j-1;
// 	// 		nodes[j].right=j+1;
// 	// 		nodes[j].leftWeight=1.0;
// 	// 		nodes[j].rightWeight=1.0;
// 	// 	}
// 	// 	nodes[rings[i].start].left=rings[i].stop;
// 	// 	nodes[rings[i].start].right=rings[i].start+1;
// 	// 	nodes[rings[i].start].leftWeight=1.0;
// 	// 	nodes[rings[i].start].rightWeight=1.0;
// 	// 	nodes[rings[i].stop].left=rings[i].stop-1;
// 	// 	nodes[rings[i].stop].right=rings[i].start;
// 	// 	nodes[rings[i].stop].leftWeight=1.0;
// 	// 	nodes[rings[i].stop].rightWeight=1.0;
// 	// }
// 	
// 	
// 	//fill childs array
// 	//fill childlen array
// 	childs[0]=(int*) malloc(spread*sizeof(int));
// 	for(int i=1;i<spread+1;i++){
// 		childs[0][i-1]=i;
// 	}
// 	
// 	// int cur = spread+1;
// // 	int marker=spread;
// // 	int doubles[childSize];
// // 	int doublesIdx=0;
// // 	
// // 	for(int i=1;i<childSize;i++){
// // 		if (i==marker){
// // 			childlen[i]=spread-3;
// // 			childs[i]=(int*) malloc((spread-3)*sizeof(int));
// // 			childs[i][0]=marker+1;
// // 			for(int j=0;j<(spread-4);j++){
// // 				childs[i][1+j]=cur+j;
// // 			}
// // 			doubles[doublesIdx++]=marker+1;
// // 			marker=cur+(spread-5);
// // 			cur+=spread-4;
// // 		} else {
// // 			int found=0;
// // 			for(int j=0;j<doublesIdx;j++){
// // 				if(doubles[j]==i){
// // 					found=1;
// // 					break;
// // 				}
// // 			}
// // 			if(found){
// // 				childlen[i]=spread-4;
// // 				childs[i]=(int*) malloc((spread-4)*sizeof(int));
// // 				for(int j=0;j<(spread-4);j++){
// // 					childs[i][j]=cur+j;
// // 				}
// // 				doubles[doublesIdx++]=cur+spread-5;
// // 				cur+=spread-5;
// // 			}else{
// // 				childlen[i]=spread-3;
// // 				childs[i]=(int*) malloc((spread-3)*sizeof(int));
// // 				for(int j=0;j<(spread-3);j++){
// // 					childs[i][j]=cur+j;
// // 				}
// // 				cur+=spread-4;
// // 				doubles[doublesIdx++]=cur;
// // 			}
// // 		}
// // 	}
// // 	
// // 	//these are the nodes of the last ring they have 0 children
// // 	for(int i=childSize;i<numSomNodes;i++){
// // 		childlen[i]=0;
// // 	}
// 	
// 	
// 	//	----------------			cluster					-----------------	//
// 	
// 	
// 	//compute mean as initialization of first ring
// 	double initial[dim];
// 	for(int i=0;i<dim;i++){
// 		initial[i]=0.0;
// 	}
// 	
// 	for(int i=0;i<items;i++){
// 		for(int j=0;j<dim;j++){
// 			initial[j]+=data[i*dim+j];
// 		}
// 	}
// 	
// 	for(int i=0;i<dim;i++){
// 		initial[i]/=items;
// 	}
// 	
// 	//set first ring to initial (mean of data)
// 	for(int i=0;i<(spread+1);i++){
// 		for(int j=0;j<dim;j++){
// 			centroids[i*dim+j]=initial[j];
// 		}
// 	}
// 	
// 	int curNodeCount=spread+1;
// 	
// 	//train each ring
// 	for(int i=1;i<=numRings;i++){
// 		printf("ring %i\n",i);
// 	
// 		//compute sigma
// 		double curSigma=sigma;
// 		double sigStep=(curSigma-sigmaEnd)/learningSteps;
// 		
// 		
// 		//compute epsilon
// 		double curEpsilon=epsilon;
// 		double epsStep=(curEpsilon-epsilonEnd)/learningSteps;
// 		
// 		
// 		//compute BMU and update Centroids
// 		// #pragma omp parallel for(size_t i = 0; i < count; ++i)
// 		{
// 			/* code */
// 		}
// 		for(int j=0;j<learningSteps;j++){
// 			//decrease sigma and epsilon with each learning step
// 			curSigma-=sigStep;
// 			curEpsilon-=epsStep;
// 			
// 			//get random signal
// 			unsigned int signal=rand()%items;
// 			
// 			
// 			// int c_bmu(const double* signal,const double* centroids,const int itms,const int dims);
// 			//get bmu by employing beamSearch
// 			
// 			int bmu=rings[i].start+c_bmu(&data[signal*dim],&centroids[rings[i].start*dim],rings[i].stop-rings[i].start,dim);
// 				// c_beamSearch(&data[signal*dim],centroids,childs,childlen,spread,swidth,i,dim);
// 
// 			//adapt the nodes
// 			c_NODEadapt(&data[signal*dim],centroids,dim,mapWidth,bmu,rings[i].start,rings[i].stop,curSigma,curEpsilon,nodes);
// 
// 		}
// 		
// 		//measure stress
// 		//TODO don't take all nodes into account only parent data should be considered
// 		
// 
// 		
// 		int numCentItems=rings[i].stop-rings[i].start+1;
// 		double mqe[numCentItems];
// 		c_mqe(data,&centroids[rings[i].start*dim],mqe,items,numCentItems,dim);
// 		double avg_mqe=0.0;
// 		for(int j=0;j<numCentItems;j++){
// 			avg_mqe+=mqe[j];
// 		}
// 		avg_mqe/=numCentItems;
// 		
// 		if (i!=numRings){
// 			rings[i+1].start=curNodeCount;
// 			for(int j=0;j<numCentItems;j++){
// 				//evaluate stress
// 				int numNewNodes;
// 				//if mqe/avg in [MIN_BORDER,MAX_BORDER]
// 				numNewNodes=((mqe[j]/avg_mqe)-MIN_BORDER)/(MAX_BORDER-MIN_BORDER)*(MAX_ADDEDNODES-MIN_ADDEDNODES);
// 
// 				//TODO brauch ich das überhaupt
// 				//if mqe/avg > MAX_BORDER
// 				if((mqe[j]/avg_mqe)>MAX_BORDER){
// 					numNewNodes=MAX_ADDEDNODES;
// 				}
// 				//if mqe/avg < MIN_BORDER
// 				if((mqe[j]/avg_mqe)<MIN_BORDER){
// 					numNewNodes=MIN_ADDEDNODES;
// 				}
// 
// 				//alter childs and childlen
// 				childs[rings[i].start+j]=(int*) malloc(numNewNodes*sizeof(int));
// 				childlen[rings[i].start+j]=numNewNodes;
// 	
// 				//add nodes
// 				for(int k=0;k<numNewNodes;k++){
// 					memcpy(&centroids[curNodeCount*dim],&centroids[(rings[i].start+j)*dim],dim*sizeof(centroids[0]));
// 					childs[rings[i].start+j][k]=curNodeCount;
// 					curNodeCount++;
// 					nodes[curNodeCount].left=curNodeCount-1;
// 					nodes[curNodeCount].right=curNodeCount+1;
// 					nodes[curNodeCount].leftWeight=1.0;
// 					nodes[curNodeCount].rightWeight=1.0;
// 				}
// 			}
// 			rings[i+1].stop=curNodeCount-1;
// 			nodes[rings[i+1].start].left=rings[i+1].stop;
// 			nodes[rings[i+1].start].right=rings[i+1].start+1;
// 			nodes[rings[i+1].start].leftWeight=1.0;
// 			nodes[rings[i+1].start].rightWeight=1.0;
// 			nodes[rings[i+1].stop].left=rings[i+1].stop-1;
// 			nodes[rings[i+1].stop].right=rings[i+1].start;
// 			nodes[rings[i+1].stop].leftWeight=1.0;
// 			nodes[rings[i+1].stop].rightWeight=1.0;
// 		}
// 	}	
// 	// printf("freeing NODES %i\n",curNodeCount-1);
// 	// TODO FREE MEMORY
// 	//after clustering free memory
// 	// for(int i=0;i<curNodeCount;i++){
// // 		if(childs[i]){
// // 			free(childs[i]);
// // 		}
// // 	}
// // 	if(childs){
// // 		free(childs);
// // 	}
// 	return curNodeCount-1;
// }