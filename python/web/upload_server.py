'''
Author       : HouJinxin jinxinhou@tuputech.com
Date         : 2025-01-17 03:15:45
LastEditors  : HouJinxin jinxinhou@tuputech.com
LastEditTime : 2025-01-17 03:55:17
FilePath     : /DeepLearning/python/web/upload_server.py
Description  : 

Copyright (c) 2025 by @Me, All Rights Reserved. 
'''
from flask import Flask, request, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 创建上传目录

@app.route('/', methods=['GET'])
def index():
    return '''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload a File</h1>
    <form method="post" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

@app.route('/upload', methods=['GET', 'POST'])  # 允许GET和POST请求
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print(f"[error]: No file part")
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            print(f"[error]: No selected file")
            return 'No selected file'
        
        print(f"filename: {file.filename}")

        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return 'File uploaded successfully!'
    else:
        return index()  # 如果是GET请求，返回上传页面

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50077, debug=True)  # 监听所有可用的IP地址
