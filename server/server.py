from flask import Flask, render_template
from flask import request

import sys
sys.path.append('../')
from main import *


app = Flask(__name__, static_url_path='')

@app.route('/')
def static_page():
    return render_template('index.html')

data = {}
@app.route('/lcc-bot', methods=['POST'])
def login():
    global data
    response = ""
    if request.method == 'POST':
        datafromjs = request.form['mydata']
        
        response, data = broback(datafromjs, data)

    return response

if __name__ == "__main__":
    app.run()
