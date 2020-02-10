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
from os import listdir
from os.path import isfile, join
import re
import base64
import argparse


path_to_modalities = './modalities/'
path_to_datasets = './datasets/'
path_to_json = './json/'
path_to_h2som_data = './h2som/'

ringdata = {}

info_file = ''
json_file = ''
img_file = ''



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

parser = argparse.ArgumentParser(description='Arguments for Backend.')
parser.add_argument('-f', '--filename', dest='file', help='The Filename of the h5 data, which is located at the datasets directory.', required=True)
parser.add_argument('-i', '--image', dest='img', help='The brightfield image of the sample.')
args = parser.parse_args()
current_dataset = args.file
img_file = args.img
dataset_name = current_dataset.split('.')[0]


h2som_files = [f for f in listdir(path_to_h2som_data) if isfile(join(path_to_h2som_data, f))]
for file in h2som_files:
    if(dataset_name + '_info' in file):
        info_file = file
    if(dataset_name + '_ring' in file):
        split = file.split('_')[-1].split(".")[0]
        ringdata[split] = pickle.load(open(os.path.join(path_to_h2som_data, file), "rb"))

json_files = [f for f in listdir(path_to_json) if isfile(join(path_to_json, f))]
for file in json_files:
    if dataset_name in file:
        json_file = file


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


app = Flask(__name__)
CORS(app)


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
    dim = pickle.load(open(path_to_h2som_data + info_file, "rb"))
    returnData = {'indizes' : indexList, 'dim': {'x': int(dim['x']), 'y': int(dim['y'])}}
    return json.dumps(returnData)

@app.route('/dimensions')
def getDimensions():
    #dim = pickle.load(open('info.h2som', "rb"))
    dim = ringdata["info"]
    dim['x'] = int(dim['x'])
    dim['y'] = int(dim['y'])
    dimX = int(dim['x'])
    dimY = int(dim['y'])
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
    img_io = BytesIO()
    img = Image.open(path_to_modalities + img_file)
    img.save(img_io, format='PNG')
    img_io.seek(0)
    response = make_response('data:image/png;base64,' + base64.b64encode(img_io.getvalue()).decode('utf-8'), 200)
    response.mimetype = 'text/plain'
    return response

@app.route('/getjson')
def getJson():
    print(json_file)
    jsn = pickle.load(open(path_to_json + str(json_file), "rb"))
    print(jsn)
    return jsn



if __name__ == '__main__':
    app.run(debug=True)
