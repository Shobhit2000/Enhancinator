from flask import Flask, render_template, Response
import youtube_dl
import time
import SRCNN
import cv2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    video_url = 'https://youtu.be/x0CJKvevs2M'
    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(video_url, download=False)
    formats = info_dict.get('formats', None)

    for f in formats:
        if f.get('format_note', None) == '144p':
            url = f.get('url', None)
            cap = cv2.VideoCapture(url)

            if not cap.isOpened():
                print('video not opened')
                exit(-1)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                lr, sr = SRCNN.sr(frame)
                frame = cv2.resize(frame, (640, 360))
                sr = cv2.resize(sr, (640, 360))
                (flag, encodedImage) = cv2.imencode(".jpg", sr)
                yield (b'--frame\r\n' 
                       b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

            cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=False)
