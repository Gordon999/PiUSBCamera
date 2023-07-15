#!/usr/bin/python3

"""Copyright (c) 2021
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. """

import os
import pygame, sys
from pygame.locals import *
import pygame.camera
import datetime
import cv2
import time
import subprocess
import signal

# version 1.6, modified for Bullseye, HDMI Video Capture adaptor added

# auto detect camera format
auto_detect = 1 # set to 1 to enable auto detect, may override window, still and video resolution values set below

# preview window
preview_width  = 800
preview_height = 600

# still camera resolution 
still_width  = 1280
still_height = 960

# video camera resolution
video_width  = 1280
video_height = 720

# save pictures and videos to..
# default directories and files
pic         = "Pictures"
vid         = "Videos"

# setup directories
Home_Files  = []
Home_Files.append(os.getlogin())
pic_dir     = "/home/" + Home_Files[0]+ "/" + pic + "/"
vid_dir     = "/home/" + Home_Files[0]+ "/" + vid + "/"

# set button sizes
bw = 160 
bh = 34
ft = int(bh/2.2) 
fv = int(bh/2.2)

#initialise pygame   
pygame.init()
pygame.camera.init()

def camera_format():
    # find formats, and set still width and height
    global width,height,usb,preview_width,preview_height,video_width,video_height,still_width,still_height
    txt = "v4l2-ctl -d " + str(usb) + " --list-formats-ext > cam_fmts.txt"
    os.system(txt)
    w = 0
    h = 0
    with open("cam_fmts.txt", "r") as file:
        line = file.readline()
        while line:
            line = file.readline()
            count = line.count(":")
            if count == 1:
                a,b = line.split(":")
                if a[len(a)-4:len(a)] == "Size":
                    c,d = b.split("x")
                    e,f,g = c.split(" ")
                    if int(d) > h:
                        h = int(d)
                    if int(g) > w:
                        w = int(g)
    if w != 0 and h!= 0:
        still_width  = w
        still_height = h
        if still_width < preview_width:
            preview_width = still_width
            preview_height = still_height
    if w < video_width or h < video_height:
        video_width  = w
        video_height = h
    print ("Still Format set: " ,still_width," x" ,still_height)
    print ("Video Format set: " ,video_width," x" ,video_height)

# find camera
if os.path.exists('/dev/video0'):
    usb = 0
    if auto_detect == 1:
        camera_format()
    cam = pygame.camera.Camera("/dev/video0",(preview_width,preview_height))
    path = '/dev/video0'
    cam.start()
elif os.path.exists('/dev/video1'):
    usb = 1
    if auto_detect == 1:
        camera_format()
    cam = pygame.camera.Camera("/dev/video1",(preview_width,preview_height))
    path = '/dev/video1'
    cam.start()
else:
    print ("No USB Camera Found")
    sys.exit()

global greyColor, redColor, greenColor, blueColor, dgryColor, lgryColor, blackColor, whiteColor, purpleColor, yellowColor
lgryColor =   pygame.Color(192, 192, 192)
blackColor =  pygame.Color(  0,   0,   0)
whiteColor =  pygame.Color(200, 200, 200)
greyColor =   pygame.Color(128, 128, 128)
dgryColor =   pygame.Color( 64,  64,  64)
greenColor =  pygame.Color(  0, 255,   0)
purpleColor = pygame.Color(255,   0, 255)
yellowColor = pygame.Color(255, 255,   0)
blueColor =   pygame.Color(  0,   0, 255)
redColor =    pygame.Color(220,   0,   0)

def button(row, bColor):
    global preview_width,bw,bh
    colors = [greyColor, dgryColor]
    Color = colors[bColor]
    bx = preview_width
    by = row * bh
    pygame.draw.rect(windowSurfaceObj,Color,Rect(bx,by,bw-1,bh))
    pygame.draw.line(windowSurfaceObj,whiteColor,(bx,by),(bx+bw,by))
    pygame.draw.line(windowSurfaceObj,greyColor,(bx+bw-1,by),(bx+bw-1,by+bh))
    pygame.draw.line(windowSurfaceObj,whiteColor,(bx,by),(bx,by+bh-1))
    pygame.draw.line(windowSurfaceObj,dgryColor,(bx,by+bh-1),(bx+bw-1,by+bh-1))
    pygame.display.update(bx, by, bw, bh)
    return

def text(row,fColor,top,upd,msg,fsize,bcolor):
    global bh,preview_width,fv
    colors =  [dgryColor, greenColor, yellowColor, redColor, purpleColor, blueColor, whiteColor, greyColor, blackColor, purpleColor]
    Color  =  colors[fColor]
    bColor =  colors[bcolor]
    bx = preview_width
    by = row * bh
    if os.path.exists ('/usr/share/fonts/truetype/freefont/FreeSerif.ttf'): 
        fontObj = pygame.font.Font('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', int(fsize))
    else:
        fontObj = pygame.font.Font(None, int(fsize))
    msgSurfaceObj = fontObj.render(msg, False, Color)
    msgRectobj =  msgSurfaceObj.get_rect()
    if top == 0:
        pygame.draw.rect(windowSurfaceObj,bColor,Rect(bx+1,by+1,bw-4,int(bh/2)))
        msgRectobj.topleft = (bx + 5, by + 3)
    elif msg == "Still":
        pygame.draw.rect(windowSurfaceObj,bColor,Rect(bx+5,by+int(bh/2)+1,int(bw/2),int(bh/2)-2))
        msgRectobj.topleft = (bx + 5, by + 1 + int(bh/2)-int(bh/20))
    elif msg == "Video" or msg == "Refresh":
       pygame.draw.rect(windowSurfaceObj,bColor,Rect(bx+int(bw/2),by+int(bh/2)+1,int(bw/2),int(bh/2)-2))
       msgRectobj.topleft = (bx + int(bw/2) + 5, by + 1 + int(bh/2)-int(bh/20))
    else:
        pygame.draw.rect(windowSurfaceObj,bColor,Rect(bx+int(bw/2.2),by+int(bh/2)-1,int(bw/2),int(bh/2)-2))
        msgRectobj.topleft = (bx + int(bw/2.2), by + 1 + int(bh/2)-int(bh/20))
       
    windowSurfaceObj.blit(msgSurfaceObj, msgRectobj)
    if upd == 1:
       pygame.display.update(bx, by, bw, bh)

txt = "lsusb > usb_list.txt"
os.system(txt)
webcam = 0
with open("usb_list.txt", "r") as file:
    line = file.readline()
    if "C270" in line and "Logitech" in line: 
        webcam = 270
    while line:
        line = file.readline()
        if "C270" in line and "Logitech" in line: 
            webcam = 270
       
def camera_controls():
    # find camera controls
    global usb,parameters,preview_height,bh,ft,fv,text
    txt = "v4l2-ctl -l -d " + str(usb) + " > cam_ctrls.txt"
    os.system(txt)
    config = []
    with open("cam_ctrls.txt", "r") as file:
        line = file.readline()
        while line:
            config.append(line.strip())
            line = file.readline()
    parameters = []
    for x in range(0,len(config)):
        fet = config[x].split(' ')
        name = ""
        minm = -1
        maxm = -1
        step = -1
        defa = -1
        valu = -1
        for y in range(0,len(fet)):
            #print (fet)
            name = fet[0]
            if fet[y][0:3] == "min":
                minm = fet[y][4:]
            if fet[y][0:3] == "max":
                maxm = fet[y][4:]
            if fet[y][0:3] == "ste":
                step = fet[y][5:]
                if webcam == 270 and (name == "exposure_absolute" or name == "white_balance_temperature"):
                    step = 50
            if fet[y][0:3] == "def":
                defa = fet[y][8:]
            if fet[y][0:3] == "val":
                valu = fet[y][6:]
            if valu != -1 and defa != -1: 
                parameters.append(name)
                parameters.append(minm)
                parameters.append(maxm)
                parameters.append(step)
                parameters.append(defa)
                parameters.append(valu)
                name = ""
                minm = -1
                maxm = -1
                step = -1
                defa = -1
                valu = -1
    if len(parameters) > 0:
        bh = int(preview_height/((len(parameters)/6)+2))
        bh = min(bh,80)
        ft = int(bh/2.2)
        ft = min(ft,20)
        fv = int(bh/2.2)
        fv = min(fv,20)

#setup window
windowSurfaceObj = pygame.display.set_mode((preview_width + bw,preview_height),1,24)
pygame.display.set_caption('Pi USB Camera')

camera_controls()
camera_controls()

def setup_screen():
    global parameters,preview_height,bh
    for d in range(0,int(len(parameters)/6) + 1):
        button(d,0)
    button(int(preview_height/bh)-1,0)
    text(0,1,0,1,"CAPTURE",ft,7)
    text(0,1,1,1,"Still",ft,7)
    text(0,1,1,1,"Video",ft,7)
    l = len(parameters)
    l = min(l,(int(preview_height/bh)-2)*6)
    for d in range(0,l,6):
        text(int(d/6) + 1,5,0,1,parameters[d],ft,7)
        text(int(d/6) + 1,3,1,1,str(parameters[d+5]),fv,7)
        if int(parameters[d + 1]) != -1:
            j = 1 + int(int(parameters[d+5]) / (int(parameters[d + 2]) - int(parameters[d + 1]))  * bw)
            pygame.draw.rect(windowSurfaceObj,(100,100,100),Rect(preview_width + 2,((int(d/6)+1) * bh)+2,j+1,5))
            pygame.draw.rect(windowSurfaceObj,(255,1,1),Rect(preview_width + (j-5),((int(d/6)+1) * bh) + 2,8,5))
    text(int(preview_height/bh)-1,3,0,1,"EXIT",fv,7)
    text(int(preview_height/bh)-1,2,1,1,"Refresh",fv,7)
    
setup_screen()

while True:
    # get a preview picture
    image = cam.get_image()
    #display the preview picture
    catSurfaceObj = image
    windowSurfaceObj.blit(catSurfaceObj,(0,0))
    pygame.display.update()
    
    #check for any mouse button presses
    for event in pygame.event.get():
        if event.type == QUIT:
            cam.stop()
            pygame.display.quit()
            sys.exit()

        elif (event.type == MOUSEBUTTONUP):
            mousex, mousey = event.pos
            
            # set camera to factory defaults (click on picture)
            if mousex < preview_width and mousey < preview_height:
                for h in range(0,len(parameters),6):
                    txt = "v4l2-ctl -c " + parameters[h] + "=" + str(parameters[h+4])
                    os.system(txt)
                camera_controls()
                setup_screen()
                
            # action menu selection   
            if mousex > preview_width:
                button_row = int((mousey)/bh) + 1
                if button_row > 1 + len(parameters)/6:
                    if mousex < preview_width + int(bw/2):
                        # exit
                        cam.stop()
                        pygame.display.quit()
                        sys.exit()
                    else:
                        # refresh control readings
                        camera_controls()
                        setup_screen()

                elif button_row == 1:
                    # capture still picture or video
                    button(0,1)
                    text(0,3,0,1,"CAPTURE",ft,0)
                    text(0,3,1,1,"Still",ft,0)
                    cam.stop()
                    if mousex < preview_width + int(bw/2):
                        # set to still camera resolution
                        cam = pygame.camera.Camera(path,(still_width,still_height))
                        cam.start()
                        pic_image = cam.get_image()
                        # make still filename YYMMDDHHMMSS.jpg
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%y%m%d%H%M%S")
                        fname =  pic_dir + str(timestamp) + '.jpg'
                        pygame.image.save(pic_image,fname)
                        cam.stop()
                    else:
                        #Capture video from webcam (NO AUDIO!!)
                        button(0,1)
                        text(0,3,0,1,"STOP",ft,0)
                        text(0,3,1,1,"Video",ft,0)
                        
                        # make video filename YYMMDDHHMMSS.mp4
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%y%m%d%H%M%S")
                        cmd = 'ffmpeg -f v4l2 -framerate 10 -video_size ' + str(video_width) + "x" + str(video_height) + ' -i ' + path + ' + vid_dir + timestamp + '.mp4'
                        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
                        stop = 0
                        count = 0
                        start_video = time.monotonic()
                        while stop == 0:
                            duration = time.monotonic() - start_video
                            text(0,3,1,1,str(int(duration)),ft,0)
                            for event in pygame.event.get():
                                if (event.type == MOUSEBUTTONUP):
                                    mousex, mousey = event.pos
                                    # stop video recording
                                    if mousex > preview_width and mousey < bh:
                                       text(0,3,0,1,"STOPPING...",ft,0)
                                       text(0,3,1,1," ",ft,0)
                                       poll = p.poll()
                                       if poll == None:
                                           os.killpg(p.pid, signal.SIGTERM)
                                           time.sleep(5)
                                               
                                       stop = 1
                    button(0,0)
                    text(0,1,0,1,"CAPTURE",ft,7)
                    text(0,1,1,1,"Still",ft,7)
                    text(0,1,1,1,"Video",ft,7)
                    # restart preview
                    if os.path.exists('/dev/video0'):
                        usb = 0
                        cam = pygame.camera.Camera("/dev/video0",(preview_width,preview_height))
                        path = '/dev/video0'
                        cam.start()
                    elif os.path.exists('/dev/video1'):
                        usb = 1
                        cam = pygame.camera.Camera("/dev/video1",(preview_width,preview_height))
                        path = '/dev/video1'
                        cam.start()
                    #cam = pygame.camera.Camera(path,(preview_width,preview_height))
                    #cam.start()
                else:
                    # change a camera parameter
                    p = int(parameters[((button_row -2)*6) + 5])
                    if mousey < ((button_row-1)*bh) + 8:
                        p = int(((mousex-preview_width) / bw) * (int(parameters[((button_row -2)*6) + 2])-int(parameters[((button_row -2)*6) + 1])))
                    elif mousex < preview_width + int(bw/2):
                        if int(parameters[((button_row-2)*6) + 3]) == -1:
                           p -=1
                        else:
                           p -=int(parameters[((button_row-2)*6) + 3])
                        if int(parameters[((button_row-2)*6) + 1]) != -1:
                           p = max(p,int(parameters[((button_row-2)*6) + 1]))
                        else:
                           p = max(p,0)
                    else:
                        if int(parameters[((button_row-2)*6) + 3]) == -1:
                           p +=1
                        else:
                           p +=int(parameters[((button_row-2)*6) + 3])
                        if int(parameters[((button_row-2)*6) + 2]) != -1:
                            p = min(p,int(parameters[((button_row-2)*6) + 2]))
                        else:
                            p = min(p,1)
                    parameters[((button_row-2)*6) + 5] = str(p)
                    text(int(button_row-1),3,1,1,str(p),fv,7)
                    txt = "v4l2-ctl -c " + parameters[(button_row-2)*6] + "=" + str(p)
                    os.system(txt)
                    if int(parameters[((button_row-2)*6) + 1]) != -1:
                        pygame.draw.rect(windowSurfaceObj,greyColor,Rect(preview_width,(int(button_row-1) * bh) + 2,bw,5))
                        j = int(int(parameters[((button_row-2)*6) + 5]) / (int(parameters[((button_row-2)*6) + 2]) - int(parameters[((button_row-2)*6) + 1]))  * (bw))
                        pygame.draw.rect(windowSurfaceObj,(100,100,100),Rect(preview_width + 2,(int(button_row-1) * bh) + 2,j+1,5))
                        pygame.draw.rect(windowSurfaceObj,(255,1,1),Rect(preview_width + (j-5),(int(button_row-1) * bh) + 2,8,5))

               

