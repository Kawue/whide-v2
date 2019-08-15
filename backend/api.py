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

@app.route('/hello')
def hello_world():
    loadData()
    return 'Hello World!!! wertt'

@app.route('/coefficients')
def getCoefficienten():
    h2som = pickle.load(open(request.args.get('index')+".h2som","rb"))
    coefficients = {}
    for i in range(len(h2som)):
        coefficients['prototyp'+str(i)] = list(h2som[i])
    return json.dumps(coefficients)

if __name__ == '__main__':
    app.run(debug=True)
