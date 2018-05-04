from flask import Flask, render_template
from flask import request

import sys
sys.path.append('../')
from main import *


app = Flask(__name__, static_url_path='')

@app.route('/')
def static_page():
	    return render_template('index.html')


@app.route('/lcc-bot', methods=['POST'])
def login():
        if request.method == 'POST':
                datafromjs = request.form['mydata']
        
        return broback(datafromjs)

if __name__ == "__main__":
    app.run()
