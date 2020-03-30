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
 
### Segmentation Map
* Zoom with mouse wheel
* Hover over Segmentation map highlights all pixel that belong to this cluster
* Click on highlighted cluster adds the related boomark to the bookmarks.
* Transparency slider regulates the transparency from the segmantation map. Shows more of the brightfield image.
* The button "mz-Image" on shows the distribution of the current mz-value. 
* There are two options for choosing aggregation method and color scale for the mz-Image
* While showing the mz-image click on the "Inverse" Button for inverse highlighting

### MZ-List
* If mz-Image is on, click on mz value shows his distribution an Segmentation Map
* Double click on mz value to annotate this mz value
* Press "Enter" on selected mz value to add this mz value to aggregation list (also multiple selected mz values)
* Press "Delete" on selected mz value to to ignore it (grey and at the end of the list) and again delete to reignore it
* Press the "pencil" button to show  annotations
* Press "arrow up" button to put selected mz value/s to aggregation list
* Press "arrow down" button to remove the selected mz value from aggregation list
* Press "Delete" on aggregation list mz value to remove this mz value from aggregation list
* Press "brushes" button to clear the whole aggregation list
* Press "sign in" button to show mz-Image from the whole aggregation list
* Press "Enter" or click on aggregation list mz value to ignore or deignorize mz value

### Color Wheel
* Hover over prototype point to highlight related pixels in the segmentation map 
* The granularity slider regulates the granularity of the clustering
* Press "arrow up" button or "arrow up" key to move prototypes upwards
* Press "arrow left" button or "arrow left" key to move prototypes to the left
* Press "arrow right" button or "arrow right" key to move prototypes to the right
* Press "arrow down" button or "arrow down" key to move prototypes downwards
* Press "back" button below the arrows to move the prototypes to the default positions
* Press "circle arrow" to rotate the color wheel
* Press "back" button below the circle arrow to rotate the color wheel to the default position
* Press "pointed circle" to rotate the prototype postions
* Press "back" button below pointed circle put the prototypes on their default position after rotating them

### Bookmarks
* Pull the top of the Bookmark panel to resize it
* Hover over chosen bookmark to highlight the related pixels on segmentation map
* Hover over bars in the chart to show the mz value
* Click on the "close" button to delete the bookmark
* Click on the "Horizontal" button to visualize the bookmarks horizontally 
* Clicking on "Spektrum" button while horizontal visualisation to visualize the pseudo spektrum
* Click on the "Show MZ-Values" button to visualize mz value on the bars in the charts
* Click on the "Show Annotations" button to show the annotation of each mz value
* Click on the "Fullscreen" button for fullscreen Bookmarks
* Click on the "Clear Bookmarks" Button to delete all the bookmarks and resize the Bookmark panel

