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
import serial
import webbrowser


# import webbrowser

PAGE="""\
<html>
	  <head>
	    <meta charset="utf-8"/>
	    <title>Car control</title>
	    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
	    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
	    <style>
	    body {
	    font-family: "courier", courier, sans-serif;
	    background-color: #ffffff;
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
	    border-radius: 8px;
	    width: 130px;
	    }
	    .button:active{
	    background-color: #618761;
	    box-shadow: 1px #666;
	    }
	    .button:hover {
	    background-color: #7B9565;
	    border: 2px solid #7B9565;
	    color: black;
	    }
	    .button5 {
	    color: white;
	    border-radius: 50px;
	    width: 80px;
	    height: 80px;
	    }
	    .button5:hover {
	    background-color: #BB3C3C;
	    border: 2px solid #BB3C3C;
	    color: white;
	    }
      .button6 {
	      background-color: #A4B88D;
	      border : none;
	      color: white;
	      padding: 12px 16px;
	      font-size: 16px;
	      cursor: pointer;
	    }
	    .button6:hover {
	      background-color: #7B9565;
	    }
	    /*Code to enable FullScreen*/
	    #videoStream {
	      border-radius: 5px;
	      cursor: pointer;
	      transition: 0.3s;
	    }
	    
	    /* The background of the fullScreen */
	    .fullScreen {
	      display: none; 
	      position: fixed; /* Stay in place */
	      z-index: 1; /* Sit on top */
	      padding-top: 20px; 
        padding-bottom: 10px;
	      left: 0;
	      top: 0;
	      width: 100%; 
	      height: 100%; 
	      background-color: rgb(0,0,0); 
	      background-color: rgba(0,0,0,0.9); /* Black with opacity */
	      }
	    /* Content of the fullScreen(image) */
	    .fullScreen-content {
	      margin: auto;
	      display: block;
	      width: 95%;
	      height: 95%;  /* This needs to be changed to adapt to the screen (always fill) */
	    }
	
	    /* Animation */
	    .fullScreen-content {
	      -webkit-animation-name: zoom;
	      -webkit-animation-duration: 0.1s;
	      animation-name: zoom;
	      animation-duration: 0.1s;
	    }
	
	    @-webkit-keyframes zoom {
	      from {-webkit-transform:scale(0)}
	      to {-webkit-transform:scale(1)}
	    }
	    @keyframes zoom {
	      from {transform:scale(0)}
	      to {transform:scale(1)}
	    }
	
	    /* The Close Button */
	    .close {
	      position: absolute;
	      top: 15px;
	      right: 35px;
	      color: #91AE79;
	      font-size: 40px;
	      font-weight: bold;
	      transition: 0.3s;
	    }
	    .close:hover,
	    .close:focus {
	      color: #7B9565;
	      text-decoration: none;
	      cursor: pointer;
	    }
	
	    /* Adapted fullScreen and buttons to smaller screens */
	    @media only screen and (max-width: 700px){
	      .fullScreen-content {
	        width: 100%;
	      }
        .button {
	        width: 90px;
          font-size: 12px;
        }  
        .button5 {
	        width: 70px;
	        height: 70px;  
	      }
	    }
	    </style>
	    </head>
	
	    <body>
	    <div class="header", style="text-align:center">
	      <h1>Car control</h1>
      </div>
      
	    <div id="stream" class="videoFeed", style="text-align:center">
	      <button id="expand" class= "button6", type="button6"><i class="fa fa-expand"></i></button>
        <img id="videoStream" src="stream.mjpg" style="width:100%;">
      </div>
      <div id="fullScreen" class="fullScreen" style="text-align:center">
	      <span class="close">&times;</span>
        <img class="fullScreen-content" id="videoStream" src="stream.mjpg" style="width:100%;">
      </div>  	
	
	    <div class="controlBox">
	      <div class="upperBox", style="text-align:center">
	        <button id="forward" class="button" type="button" onClick="forward()" >Forward</button>
	      </div>
	      <div class="middleBox", style="text-align:center">
          <button id="left" class="button" type="button" onClick="left()">Left</button>
          <button id="stop" class="button button5" type="button5" onClick="stop()">Stop</button>
          <button id="right" class="button" type="button" onClick="right()">Right</button>
	      </div>
	      <div class="lowerBox", style="text-align:center">
	        <button id="backward" class="button" type="button" onClick="backward()">Backward</button>
	      </div>
	    </div>
	
	
	    <script>
			// Steering onclick test example 	
			/* var button_1 = "left";
      $.post('172.20.10.6',{
      button: button_1,
      },function(res){
      console.log(res);
			}); */

			var accelerate = document.getElementById('forward');
			var turnLeft = document.getElementById('left');
			var turnRight = document.getElementById('right');
			var stop = document.getElementById('stop');
			var decelerate = document.getElementById('backward');
			
			accelerate.onclick = function(){
				$.post('172.20.10.6',{
      	command: "accelerate"
				});
			}	
			decelerate.onclick = function(){
				$.post('172.20.10.6',{
      	command: "decelerate"
				});
			}	
			turnLeft.onclick = function(){
				$.post('172.20.10.6',{
      	command: "turnLeft"
				});
			}	
			turnRight.onclick = function(){
				$.post('172.20.10.6',{
      	command: "turnRight"
				});
			}	
			stop.onclick = function(){
				$.post('172.20.10.6',{
      	command: "stop"
				});
			}	

	    // Open the fullScreen
	    var fullScreen = document.getElementById('fullScreen');
		  var img = document.getElementById('videoStream');
	    var modalImg = document.getElementById("videoStream");
      var expand = document.getElementById("expand");
	    expand.onclick = function(){
	      fullScreen.style.display = "block";
	      modalImg.src = this.src;
	    }
	
	    var span = document.getElementsByClassName("close")[0];
      span.onclick = function() {
	      fullScreen.style.display = "none";
	    }
      
	    </script>
	    </body>
</html>
"""
try:
    ser = serial.Serial('/dev/ttyACM0',9600)
    print("Arduino Connected")
except:
    print("Arduino not connected")

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
    
    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
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
            # url = 'file://Documents/webDesign/index2.html'
            # webbrowser.open(url new=0)
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
        if b'accelerate' in body: 
            ser.write(b'w \n')

        elif b'decelerate' in body:
            ser.write(b's \n')

        elif b'turnLeft' in body:
            ser.write(b'a \n')

        elif b'turnRight' in body:
            ser.write(b'd \n')

        elif b'stop' in body:
            ser.write(b'q \n')

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