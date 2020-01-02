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

path_to_assets = '../whide-v2/src/assets/'
path_to_datasets = '../datasets/'
current_dataset = 'barley101GrineV2.h5'

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

vals = mz_values()
print(vals)



app = Flask(__name__)
CORS(app)


@app.route('/coefficients')
def getCoefficienten():
    # request.args.get('index') is the argument given (now the ring0)
    h2som = pickle.load(open(request.args.get('index')+".h2som","rb"))
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
    entries = os.listdir()
    pattern = re.compile("ring[0-9]+.h2som")
    files = []
    for x in entries:
        if pattern.match(x):
            files.append(x)

    indexList = [0]
    for y in files:
        dummy = pickle.load(open(y, "rb"))
        counter = 0
        for i in range(len(dummy)):
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
    dim = pickle.load(open('info.h2som', "rb"))
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
    dir = os.listdir(path_to_assets)
    pattern = re.compile("[.(?i:jpg|gif|png|bmp)")
    pictures = []
    for x in dir:
        if pattern.match(x):
            pictures.append(x)


    return json.dumps(pictures)

if __name__ == '__main__':
    app.run(debug=True)
