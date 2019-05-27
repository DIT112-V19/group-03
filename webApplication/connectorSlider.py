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
        background-color:rgb(226, 177, 177);
        }
        .header {
        width:100%;
        margin: auto;
        color: rgb(89, 59, 59);
		    font-family: 'Arvo', Georgia, Times, serif;
		    font-size: 25px;
        }
        .videoFeed {
        width: 60%;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 10px;
        }
        .controlBox {
        width: 40%;
        margin: auto;
        }
        .leftBox {
        width: 70%; 
        float: left;  
        }
        .rightBox {
        width: 30%; 
        display: flex;
        justify-content: center; 
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
          background-color: rgb(226, 177, 177);
          border-radius: 50px;
          width: 70px;
	        height: 70px;
          font-size: 12px;
          color: black;
          padding: 10px 10px;
          text-align: center;
          display: inline-block;
          margin: none;
          -webkit-transition-duration: 0.4s;
          transition-duration: 0.1s;
          cursor: pointer;
          border: 2px solid black;
        }
        .button:active{
          background-color: rgb(0, 0, 0, 0.29);
        }
        .button:hover {
          background-color: rgb(0, 0, 0, 0.29);
          border: 2px solid #7B9565;
          color: black;
        }
        .button1 {
          margin-right: 13px;
        }
        .button2 {
          margin-left: 13px;
        }
        .button5 {
          color: black;
          border-radius: 50px;
          width: 70px;
          height: 70px;
        }
        .button5:hover {
          background-color: rgb(0, 0, 0, 0.29);
          border: 2px solid #BB3C3C;
          color: black;
        }
        /* Expand feed button design */  
        .button6 {
          position:relative;
          top:50px;
          border:none;
          right: 9px;
          background:rgba(0,0,0,0);
          color: white;
          padding: 8px 10px;
          font-size: 16px;
          cursor: pointer;
          transition: 0.3s;
          border-radius: 12px;
        }
        /* Enable FullScreen */
        #videoStream {
          border-radius: 5px;
          cursor: pointer;
          transition: 0.3s;
        }
        img {
            border-radius: 12px;
        }
        /* The background of the fullScreen */
        .fullScreen {
          display: none;
          position: fixed; 
          z-index: 1; /* Sit on top */
          padding-top: 20px;
          padding-bottom: 10px;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          background-color: rgb(0,0,0);
          background-color: rgba(0,0,0,0.9); 
          }
        /* Content of the fullScreen */
        .fullScreen-content {
          margin: auto;
          display: block;
          width: 95%;
          height: 95%;  
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
          color: rgb(89, 59, 59);
          font-size: 40px;
          font-weight: bold;
          transition: 0.3s;
        }
        .close:hover,
        .close:focus {
          color: #808080;
          text-decoration: none;
          cursor: pointer;
        }
        /* Speed controller */
        .btngroup {
          color: black; 
          background-color: rgb(226, 177, 177);
          text-align: center;
          border: none; 
          cursor: pointer; 
          width: 45px; 
          height: 40px;
          display: block; /* Make the buttons appear below each other */
        }
        .buttonMid {
          border-right: 2px solid rgb(0, 0, 0);
          border-left: 2px solid rgb(0, 0, 0);
        }
        .buttonTop{
          border: 2px solid rgb(0, 0, 0);
          border-top-left-radius: 15px; 
          border-top-right-radius: 15px;
          border-bottom: none;
        } 
        .buttonEnd{
          border: 2px solid rgb(0, 0, 0);
          border-top: none;
          border-bottom-left-radius: 15px; 
          border-bottom-right-radius: 15px;
        }  
        .btngroup button:not(:last-child) {
          border-bottom: none; 
        } 
        .active, .btngroup:hover {
          background-color: rgba(0, 0, 0, 0.29);
          color: rgb(0, 0, 0);
        }
        /* Adapted fullScreen and buttons to smaller screens */
        @media only screen and (max-width: 1040px){
        .videoFeed {
            width: 90%
          }
        .controlBox {
            width: 90%
          }
        .fullScreen-content {
            width: 90%;
          }
        .button {
          width: 80px;
          height: 80px;
          }      
        }
        @media only screen and (max-width: 700px){
        .fullScreen-content {
            width: 100%;
          }
        .button {
          width: 60px;
          height: 60px;
          }    
        }
        @media only screen and (max-width: 400px){
        .button {
          width: 50px;
          height: 50px;
          }    
        }
        </style>
        </head>

        <body>
        <div class="header", style="text-align:center">
          <h1>Car Control</h1>
        </div>
        <div id="stream" class="videoFeed", style="text-align:right">
            <button id="expand" class= "button6", type="button6"><i class="fa fa-expand"></i></button>
            <img id="normalStream" src="stream.mjpg" style="width:100%;">
        </div>
        <div id="fullScreen" class="fullScreen" style="text-align:center">
            <span class="close">&times;</span>
            <img class="fullScreen-content" id="stream.mjpg" style="width:100%;">
        </div>
        <div class="controlBox">
            <div class="leftBox">  
              <div class="upperBox", style="text-align:center">
                <button id="forward" class="button" type="button">Go</button>
              </div>
              <div class="middleBox", style="text-align:center">
                <button id="left" class="button button1" type="button1">Left</button>
                <button id="stop" class="button button5" type="button5">Stop</button>
                <button id="right" class="button button2" type="button2">Right</button>
              </div>
              <div class="lowerBox", style="text-align:center">
                <button id="backward" class="button" type="button">Back</button>
              </div>
            </div>
            </div>
            <div class="rightBox">  
                <div class="btngroup", id="btngroup">
                    <button class="btngroup buttonTop" id="high">High</button>
                    <button class="btngroup buttonMid" id="Medium">Med</button>
                    <button class="btngroup buttonMid" id="Low">Low</button>
                    <button class="btngroup buttonMid active" id="Stop">Stop</button>
                    <button class="btngroup buttonMid" id="LowB">Low</button>
                    <button class="btngroup buttonEnd" id="MediumB">Med</button>
                </div>
            </div>          
        </div>    
        <script>
          
          // Steering functionality
            var accelerate = document.getElementById('forward');
			      var turnLeft = document.getElementById('left');
			      var turnRight = document.getElementById('right');
			      var stop = document.getElementById('stop');
		      	var decelerate = document.getElementById('backward'); 
            var maxSpeed = document.getElementById('high');
            var medSpeed = document.getElementById('Medium');
            var lowSpeed = document.getElementById('Low');
            var noSpeed = document.getElementById ('Stop');
            var lowSpeedB = document.getElementById('LowB');
            var highSpeedB = document.getElementById('MediumB');
        
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
            maxSpeed.onclick = function(){
              $.post('172.20.10.6',{
              command: "maxSpeed"
              });
            }
            medSpeed.onclick = function(){
              $.post('172.20.10.6',{
              command: "medSpeed"
              });
            }
            lowSpeed.onclick = function(){
              $.post('172.20.10.6',{
              command: "lowSpeed"
              });
            }
            noSpeed.onclick = function(){
              $.post('172.20.10.6',{
              command: "noSpeed"
              });
            }
            lowSpeedB.onclick = function(){
              $.post('172.20.10.6',{
              command: "lowSpeedB"
              });
            }
            highSpeedB.onclick = function(){
              $.post('172.20.10.6',{
              command: "highSpeedB"
              });
            }
            
        // Open the fullScreen
            var fullScreen = document.getElementById('fullScreen');
            var modalImg = document.getElementById("fullStream");
            var expand = document.getElementById("expand");
            expand.onclick = function(){
            fullScreen.style.display = "block";
            }
            var span = document.getElementsByClassName("close")[0];
            span.onclick = function() {
            fullScreen.style.display = "none";
            }
        // Mark the lastest pressed speedbutton  
            var header = document.getElementById("btngroup");
            var btns = header.getElementsByClassName("btngroup");
            for (var i = 0; i < btns.length; i++) {
            btns[i].addEventListener("click", function() {
            var current = document.getElementsByClassName("active");
            current[0].className = current[0].className.replace(" active", "");
            this.className += " active";
            });
          }
        </script>
        </body>
</html>

"""

#A try except lopp for connecting to the Arduino, name of the port we're connecting to and the 
# buad-rate of the arudino sketch.

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
	#Here we're checking the body for different values which decides what should be written to the Arduino

        if b'forward' in body: 	#Setting the angle of the car to 0 degrees (Backward)
            ser.write(b'w \n')

        elif b'backward' in body: #Setting the angle of the car to 0 degrees (Backward)
            ser.write(b's \n')

        elif b'turnLeft' in body: #Making the car take a left turn for -75 degrees
            ser.write(b'a \n')

        elif b'turnRight' in body: #Making the car take a right turn for 75 degrees
            ser.write(b'd \n')

        elif b'stop' in body: #Stopping the car, no matter the speed or angle...
            ser.write(b'r \n')

        elif b'maxSpeed' in body: #Fastest speed for the car, forward
            ser.write(b'1 \n')
				
        elif b'medSpeed' in body: #Medium speed for the car, forward
            ser.write(b'2 \n')

        elif b'lowSpeed' in body: #Low speed for the car, forward
            ser.write(b'3 \n')
				
        elif b'noSpeed' in body: #No speed for the car. Standing still
            ser.write(b'4 \n')
				
        elif b'lowSpeedB' in body: #Low speed for the car, backward
            ser.write(b'5 \n') 

        elif b'highSpeedB' in body: #Medium speed for the car, backward
            ser.write(b'6 \n')


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
