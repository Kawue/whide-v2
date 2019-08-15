from flask import Flask
from flask import abort
from flask import request
from flask_cors import CORS
import pickle

def loadCoefficienten():
    h2som = pickle.load(open("ring-1.h2som","rb"))
    print(h2som)

app = Flask(__name__)
CORS(app)

@app.route('/hello')
def hello_world():
    loadData()
    return 'Hello World!!! wertt'

@app.route('<ringIdx>/getCoefficients/', methods=['POST'])
def getCoefficienten(ringIdx):
    h2som = pickle.load(open(str(ringIdx)+".h2som","rb"))
    return h2som

if __name__ == '__main__':
    app.run(debug=True)
