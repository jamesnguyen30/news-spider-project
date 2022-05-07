from flask import Flask, render_template, request
import os
import json
import subprocess
import pathlib
from crawlers.crawlers import CnnCrawler

ROOT_DIR = pathlib.Path(__file__).parent.parent.absolute()

app = Flask(__name__)

@app.route('/')
def index():
    data = dict()
    data['name'] = "News Crawler"
    return render_template('/index.html', data = data)

@app.route('/crawl_cnn', methods = ["POST"])
def crawl_cnn():
    return 'ok'

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    app.run(debug = True, host = '0.0.0.0', port = port)
