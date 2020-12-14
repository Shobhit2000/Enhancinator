from flask import Flask, render_template, Response, request, session, redirect, url_for, escape
import youtube_dl
import time
import SRCNN
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key='12345678'

@app.route('/')
def index():
    return render_template('index.html')

def resolve_and_plot(model_pre_trained, model_fine_tuned, lr_image_path):
    lr = lr_image_path
    sr_pt = resolve_single(model_pre_trained, lr)
    return sr_pt

def gen(x):
    video_url = x
    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(video_url, download=False)
    formats = info_dict.get('formats', None)
    #model2 = load_model("./weights/model2.h5")
    #model1 = load_model("./weights/model1.h5")

    for f in formats:
        if f.get('format_note', None) == '144p':
            url = f.get('url', None)
            cap = cv2.VideoCapture(url)

            if not cap.isOpened():
                print('video not opened')
                exit(-1)

            while True:
                ret, frame = cap.read()
                if not ret:0
                    break

                #img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #sr = resolve_and_plot(model1, model2, img)
                # sr = np.array(sr)
                # sr = cv2.cvtColor(sr, cv2.COLOR_RGB2BGR)
                # sr = cv2.resize(sr, (640, 360))
                #lr, sr = SRCNN.sr(frame)
                frame = cv2.resize(frame, (640, 360))
                #sr = cv2.resize(sr, (640, 360))
                #sr1 = np.vstack((frame,sr))
                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                yield (b'--frame\r\n' 
                       b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

            cap.release()

def gen1(x):
    video_url = x
    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(video_url, download=False)
    formats = info_dict.get('formats', None)

    for f in formats:
        if f.get('format_note', None) == '360p':
            url = f.get('url', None)
            cap = cv2.VideoCapture(url)

            if not cap.isOpened():
                print('video not opened')
                exit(-1)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (640, 360))
                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                yield (b'--frame\r\n' 
                       b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

            cap.release()

@app.route('/video_feed1', methods = ["POST"])
def video_feed1():
    url = request.form["first_name"]
    session['url']=url
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    url=''
    try:
        url = session['url']
    except:
        pass
    print(url)
    return Response(gen(url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_fee')
def video_fee():
    url=''
    try:
        url = session['url']
    except:
        pass
    print(url)
    return Response(gen1(url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=False)