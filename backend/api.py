from flask import Flask
from flask import abort
from flask import request
from flask_cors import CORS
import pickle
import json

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
    lastIndex = 0
    for i in range(len(h2som)):
        id = int(givenlastIdx)+i
        print(id)
        coefficients['prototyp'+str(id)] = list(h2som[i])
        lastIndex = id
    data['coefficients'] = coefficients
    data['idx'] = lastIndex
    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True)
