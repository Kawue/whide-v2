# Handbook
The Handbook for WHIDE is split into two parts. The Data Creation [Data Creation](#-data-creation) part and the use of WHIDE [WHIDE](#-use-whide).

## Data Creation
For the data creation you can choose between the `h2som.py` and the `clustering.py`.
To start one of those files zou use these commands.
```shell script
docker build -t whide/h2som .

docker run -v <path_to_backend>:/backend  --rm whide/h2som python <file>.py -f <dataset_name>
```
Where `<file>` a placeholder for `h2som` and `clustering` is. 
Both scripts use an argument parser where you can use the flag `-h` for help. 
Both have some special flags which you can set. 

### h2som.py
```shell script
usage: h2som.py [-h] -f FILE [-o [OUT]] [-e EPS EPS] [-s SIG SIG] [-t]

Arguments for the h2som

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --filename 
                        The Filename of the h5 data.
  -o [OUT], --outputfile 
                        The path where you want to store the computed data
  -e EPS, --epsilon 
                        Epsilon parameter for the h2SOM.
  -s SIG, --sigma 
                        Sigma parameter for the h2SOM.
  -t, --test
```
The required flag is `-f`. Please write the Filename of the .h5 file in `backend/datasets` which you want to use.

The default settings are:
 
 `Epsilon: 1.0, 0.01`
 
 `Sigma: 13, 0.24`

The `h2som` has 10 iterations.

`Here some informations how to choose sigma and epsilon, need to ask karsten again how this should work`

### clustering.py
```shell script
usage: clustering.py [-h] -f FILE [-o [OUT]] [-e EMBEDDING]
                     [-s {polar,cartesien}] [-a] [-d {pca,umap}]
                     [-m {kmeans,agglomerative}] [-c] [-t]

Arguments for clustering

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --filename FILE 
                        The Filename of the h5 data.
  -o [OUT], --outputfile [OUT]
                        The path where you want to store the computed data
  -e EMBEDDING, --embedding EMBEDDING
                        Embedding from before to this dataset
  -s {polar,cartesien}, --space {polar,cartesien}
                        Choose between clusting in polar space or cartesien space                   
  -a, --all_prototyps   Cluster data but every pixel is a prototyp
  -d {pca,umap}, --dimensions_reduction {pca,umap}
                        Choose between PCA and UMAP as dimension reduction
  -m {kmeans,agglomerative}, --clustering_method {kmeans,agglomerative}
                        Choose between KMEANS and Agglomerative Clustering
  -c, --no_dimension_reduction
                        If clustering is done on Data without dimension reduction
                        
  -t, --test
```
The required flag is `-f`. Please write the Filename of the .h5 file in `backend/datasets` which you want to use.

The default settings are:

`Dimension reduction: umap`

`Space: cartesien`

`Clustering: kmeans`

You can combine all the flags as desired. For example:
 ```shell script
clustering.py -f <dataset_name> -d pca -s polar -m agglomerative
```
 
 ## Use WHIDE 
 
 


