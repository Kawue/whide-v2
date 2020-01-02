from flask import Flask, make_response, abort, request
from flask_cors import CORS
from mzDataset import MzDataSet
from PIL import Image
from io import BytesIO
import numpy as np
import pandas as pd
import pickle
import json
import os
import re
import base64
from sys import argv

path_to_assets = './modalities/'
path_to_datasets = './datasets/'
path_to_json = './json/'
path_to_h2som_data = './h2som'

datasets = {}
ringdata = {}

colorscales = {
        'Viridis': 'viridis',
        'Magma': 'magma',
        'Inferno': 'inferno',
        'Plasma': 'plasma',
        'PiYG': 'PiYG'
    }

aggregation_methods = {
    'mean': np.mean,
    'median': np.median,
    'min': np.min,
    'max': np.max
}


if len(argv[3:]) == 0:
    print('h2Som.py was not executed till now, please execute it!')
else:
    for f in argv[4:]:
        split = f.split('_')[-1].split(".")[0]
        ringdata[split] = pickle.load(open(os.path.join(path_to_h2som_data, f), "rb"))

def read_data(path):
    dframe = pd.read_hdf(path)
    # Rows = pixel, Columns = m/z channels
    data = dframe.values
    #print(data.shape)
    return dframe, data

dframe, data = read_data(path_to_datasets + current_dataset)
dataset = MzDataSet(dframe)

# returns list of all mz_values
def mz_values():
    return dataset.getMzValues()



#dframe, data = read_data(path_to_datasets + argv[2])
#dataset = MzDataSet(dframe)


app = Flask(__name__)
CORS(app)


@app.route('/json')
def getJson():
    with open(os.path.join(path_to_json, argv[1])) as json_file:
        json_data = json.load(json_file)
    return json.dumps(json_data)

@app.route('/coefficients')
def getCoefficienten():
    # request.args.get('index') is the argument given (now the ring0)
    #h2som = pickle.load(open(request.args.get('index')+".h2som","rb"))
    h2som = ringdata[request.args.get('index')]
    givenlastIdx = request.args.get('lastIndex')
    data = {}
    coefficients = {}
    for i in range(len(h2som)):
        id = int(givenlastIdx)+i
        coefficients['prototyp'+str(id)] = list(h2som[i])
    data['coefficients'] = coefficients
    return json.dumps(data)

@app.route('/ringdata')
def getCoefIndeizes():
    rings = []
    for key, value in ringdata.items():
        pattern = re.compile("ring[0-9]")
        if pattern.match(key):
            rings.append((key, value))
    rings.sort(key=lambda x: int(x[0].split("ring")[1]))
    rings = list(zip(*rings))[1]


    indexList = [0]
    for ring in rings:
        counter = 0
        for i in range(len(ring)):
            counter += 1
        indexList.append(counter)

    indexList.sort()
    for i in range(len(indexList)):
        if i != 0:
           indexList[i] = indexList[i] + indexList[i-1]
    indexList = indexList[:-1]
    returnData = {'indizes' : indexList}
    return json.dumps(returnData)

@app.route('/dimensions')
def getDimensions():
    #dim = pickle.load(open('info.h2som', "rb"))
    dim = ringdata["info"]
    dim['x'] = int(dim['x'])
    dim['y'] = int(dim['y'])
    return json.dumps(dim)

# get mz image data for dataset and mz values
# specified merge method is passed via GET parameter
# mz values are passed via post request
@app.route('/mzimage', methods=['POST'])
def imagedata_multiple_mz_action():
    try:
        post_data = request.get_data()
        post_data_json = json.loads(post_data.decode('utf-8'))
        aggeregation_method = post_data_json['method']
        colorscale = post_data_json['colorscale']
        post_data_mz_values = [float(i) for i in post_data_json['mzValues']]
    except:
        return abort(400)

    if len(post_data_mz_values) == 0:
        return abort(400)

    img_io = BytesIO()
    Image.fromarray(
        dataset.getColorImage(
            post_data_mz_values,
            method=aggregation_methods[aggeregation_method],
            cmap=colorscales[colorscale]),
        mode='RGBA'
    ).save(img_io, 'PNG')
    img_io.seek(0)
    response = make_response('data:image/png;base64,' + base64.b64encode(img_io.getvalue()).decode('utf-8'), 200)
    response.mimetype = 'text/plain'
    return response

@app.route('/brightfieldimage')
def getBrightfieldImage():
    picture = os.path.join(path_to_assets, argv[3])
    return json.dumps(pictures)

if __name__ == '__main__':
    app.run(debug=True)
