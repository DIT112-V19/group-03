# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
#
# The webpage: http://172.20.10.6:8000/index.html
# The stream: http://172.20.10.6:8000/stream.mjpg

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

# html starts here 
PAGE="""\
<html>
    <head>
        <title>Car control</title>
        <style>
            body {
                font-family: "courier", courier, sans-serif;
                background-color: #fffff;
            }
        div.container {
            width: 100%;
            border: 1px solid black;
        }
        div.boxA {
            box-sizing: border-box;
            width: 39%;
            height: 600px;
            border: 1px solid black;
            padding: 10px;
            float: left;
        }
        div.boxB {
            box-sizing: border-box;
            width: 61%;
            height: 600px;
            border: 1px solid black;
            padding: 10px;
            float: left;
        }
        .button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 17px 28px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 1px 1px;
            -webkit-transition-duration: 0.4s;
            transition-duration: 0.4s;
            cursor: pointer;
        }
        .button1 {
            background-color: white;
            color: black;
            border: 2px solid #555555;
            position: absolute;
            left: 200px;
            top: 150px;
            border-radius: 8px;
            width: 130px;
        }
        .button1:hover {
            background-color: #555555;
            color: white;
        }
        .button2 {
            background-color: white;
            color: black;
            border: 2px solid #555555;
            position: absolute;
            left: 200px;
            top: 350px;
            border-radius: 8px;
            width: 130px;
        }
        .button2:hover {
            background-color: #555555;
            color: white;
        }
        .button3 {
            background-color: white;
            color: black;
            border: 2px solid #555555;
            position: absolute;
            left: 355px;
            top: 250px;
            border-radius: 8px;
            width: 130px;
        }
        .button3:hover {
            background-color: #555555;
            color: white;
        }
        .button4 {
            background-color: white;
            color: black;
            border: 2px solid #555555;
            position: absolute;
            left: 45px;
            top: 250px;
            border-radius: 8px;
            width: 130px;
        }
        .button4:hover {
            background-color: #555555;
            color: white;
        }
        .button5 {
            background-color: white;
            color: black;
            border: 2px solid #555555;
            position: absolute;
            left: 220px;
            top: 234px;
            border-radius: 50px;
            width: 90px;
            height: 90px;
        }
        .button5:hover {
            background-color: #555555;
            color: white;
        }
        
            </style>
    </head>
    <body>
        
        <h1>Car control</h1>
        
        <div class="container">
            <div class="boxA">left half
                <button class="button button1">Forward</button>
                <button class="button button2">Backward</button>
                <button class="button button3">Right</button>
                <button class="button button4">Left</button>
                <button class="button button5">Stop</button>
            </div>
            <div class="boxB">
                <img src="stream.mjpg" width="640" height="550">
                    </div>
            <div style="clear:both;"></div>
        </div>
        
    </body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
    
    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                                'Removed streaming client %s: %s',
                                self.client_address, str(e))


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
