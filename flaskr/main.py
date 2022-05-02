from flask import Flask, render_template, request
import os
import json
import subprocess
import pathlib

ROOT_DIR = pathlib.Path(__file__).parent.parent.absolute()

app = Flask(__name__)

@app.route('/')
def index():
    data = dict()
    data['name'] = "News Crawler"
    return render_template('/index.html', data = data)

@app.route('/crawl_cnn', methods = ["POST"])
def crawl_cnn():
    if request.method == 'POST':
        request_json = request.data.decode('utf-8')
        data = json.loads(request_json)
        print(data['url'])
        dir = '/'.join([str(ROOT_DIR), 'news_spider', 'news_spider'])
        print(dir)
        try:
            spider = 'cnn_crawler'
            subprocess.run(f'scrapy crawl {spider}', cwd = dir, shell = True)
            return 'ok'
        except Exception as e:
            print('ERROR:', str(e))
            return 'not ok, check log'
    return 'invalid method request'

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    app.run(debug = True, host = '0.0.0.0', port = port)
