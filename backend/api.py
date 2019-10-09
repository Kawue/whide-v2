from flask import Flask
from flask import abort
from flask import request
from flask_cors import CORS
import pickle
import json
import os
import re

def loadCoefficienten():
    h2som = pickle.load(open("ring-1.h2som","rb"))
    print(h2som)

app = Flask(__name__)
CORS(app)

@app.route('/coefficients')
def getCoefficienten():
    h2som = pickle.load(open(request.args.get('index')+".h2som","rb"))
    givenlastIdx = request.args.get('lastIndex')
    data = {}
    coefficients = {}
    for i in range(len(h2som)):
        id = int(givenlastIdx)+i
        coefficients['prototyp'+str(id)] = list(h2som[i])
    data['coefficients'] = coefficients
    return json.dumps(data)

@app.route('/coefficientsindex')
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
    return returnData

if __name__ == '__main__':
    app.run(debug=True)
