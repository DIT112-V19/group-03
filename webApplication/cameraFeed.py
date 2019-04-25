# Web streaming
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

from io import BytesIO

PAGE="""\
    <html>
        <head>
            <meta charset="utf-8"/>
            <title>Car control</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <style>
        body {
        font-family: "courier", courier, sans-serif;
        background-color: #fffff;
        background-image: url("img/background.jpg");
        }
        .header {
        width:90%;
        padding: 10px;
        margin: auto;
        }
        .videoFeed {
        width: 90%;
        border: 2px dotted #6F6F6F;
        padding: 10px;
        margin-left: auto;
        margin-right: auto;
        margin-top: auto;
        margin-bottom: 10px;
        }
        .controlBox {
        width: 90%;
        border: 2px solid #6F6F6F;
        padding: 10px;
        margin: auto;
        }
        .upperBox {
        width: 90%;
        padding: 10px;
        margin: auto;
        }
        .middleBox {
        width: 90%;
        padding: 10px;
        margin: auto;
        }
        .lowerBox {
        width: 90%;
        padding: 10px;
        margin: auto;
        }
    /* button design */
        .button {
        background-color: #A4B88D;
        border-radius:15px;
        box-shadow: 0 2px #C9C9C9;
        color: white;
        padding: 17px 17px;
        text-align: center;
        display: inline-block;
        margin:auto;
        font-size: 16px;
        -webkit-transition-duration: 0.4s;
        transition-duration: 0.1s;
        cursor: pointer;
        border: 2px solid #91AE79;
        }
        .button:active{
        background-color: #618761;
        box-shadow: 0 1px #666;
        }
        .button1 {
        color: black;
        border-radius: 8px;
        width: 130px;
        }
        .button2 {
        color: black;
        border-radius: 8px;
        width: 130px;
        }
        .button3 {
        color: black;
        border-radius: 8px;
        width: 130px;
        }
        .button4 {
        color: black;
        border-radius: 8px;
        width: 130px;
        }
        .button:hover {
        background-color: #7B9565;
        border: 2px solid #7B9565;
        color: white;
        }
        .button5 {
        color: black;
        border-radius: 50px;
        width: 80px;
        height: 80px;
        }
        .button5:hover {
        background-color: #BB3C3C;
        border: 2px solid #BB3C3C;
        color: white;
        }
        </style>
    </head>
    <body>
        <div class="header", style="text-align:center">
            <h1>Car control</h1>
            </div>
            <div class="videoFeed", style="text-align:center">
                <img src="stream.mjpg" width="100%" height="60%">
            </div>
            <div class="controlBox">
                <div class="upperBox", style="text-align:center">
                    <button class="button button1">Forward</button>
                </div>
                <div class="middleBox", style="text-align:center">
                    <button class="button button4">Left</button>
                    <button class="button button5">Stop</button>
                    <button class="button button3">Right</button>
                </div>
                <div class="lowerBox", style="text-align:center">
                    <button class="button button2">Backward</button>
                </div>
            </div>
    </body>
<script>
var button_c = "left";
$.post('localhost',{
boton: button_c,
},function(res){
console.log(res);
});
</script>
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

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())

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
