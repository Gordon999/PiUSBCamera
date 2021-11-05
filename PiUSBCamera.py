#!/usr/bin/python3
import os
import pygame, sys
from pygame.locals import *
import pygame.camera
import datetime
import cv2
import time

# version 9

# auto detect camera format
auto_detect = 1 # set to 1 to enable auto detect, will override window and resolution values set below

# preview window
preview_width  = 800
preview_height = 600

# still camera resolution 
still_width  = 1280
still_height = 960

# video camera resolution
video_width  = 1280
video_height = 960

# limit above which cv2 is used to capture video, as opposed to pygame.
# Enables Philips 740/900 USB cameras to work at 640x480 if set for 640, and video_width = 640 and video_height = 480
vlimit = 640

# show every sframe during video recording
sframe = 10

# save pictures and videos to..
pic_dir = "/home/pi/Pictures/"
vid_dir = "/home/pi/Videos/"

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
    global width,height,usb,preview_width,preview_height,video_width,video_height
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
        still_width = w
        still_height = h
        video_width = w
        video_height = h
        if still_width < preview_width:
            preview_width = still_width
            preview_height = still_height
    print ("Format set: " ,still_width," x" ,still_height)

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

def button(col,row, bColor):
    global preview_width,bw,bh
    colors = [greyColor, dgryColor]
    Color = colors[bColor]
    bx = preview_width + (col * bw)
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
        fontObj =       pygame.font.Font('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', int(fsize))
    else:
        fontObj =       pygame.font.Font(None, int(fsize))
    msgSurfaceObj = fontObj.render(msg, False, Color)
    msgRectobj =    msgSurfaceObj.get_rect()
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
        pygame.draw.rect(windowSurfaceObj,bColor,Rect(bx+int(bw/2.2),by+int(bh/2)+1,int(bw/2),int(bh/2)-2))
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
        ft = int(bh/2.2) 
        fv = int(bh/2.2)

#setup window
windowSurfaceObj = pygame.display.set_mode((preview_width + bw,preview_height),1,24)
pygame.display.set_caption('Pi USB Camera')

camera_controls()
camera_controls()

def setup_screen():
    global parameters,preview_height,bh
    for d in range(0,int(len(parameters)/6) + 1):
        button(0,d,0)
    button(0,int(preview_height/bh)-1,0)
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
            pygame.draw.rect(windowSurfaceObj,(100,100,100),Rect(preview_width +2,((int(d/6)+1) * bh)+2,j+1,5))
    text(int(preview_height/bh)-1,3,0,1,"EXIT",fv,7)
    text(int(preview_height/bh)-1,2,1,1,"Refresh",fv,7)
    
setup_screen()

while True:
    # get a picture
    image = cam.get_image()
    #display the picture
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
            
            # set camera to factory defaults (click top left of picture)
            if mousex < preview_width and mousey < preview_height:
                for h in range(0,len(parameters),6):
                    txt = "v4l2-ctl -c " + parameters[h] + "=" + str(parameters[h+4])
                    os.system(txt)
                camera_controls()
                setup_screen()
                
            # action menu selection   
            if mousex > preview_width:
                e = int((mousex-preview_width)/int(bw/2))
                f = int(mousey/bh)
                g = int(f*2) + e
                g = int(g/2)*2
                if g == (int(preview_height/bh)-1)*2 and mousex < preview_width + int(bw/2):
                   # exit
                    cam.stop()
                    pygame.display.quit()
                    sys.exit()

                elif g == (int(preview_height/bh)-1)*2:
                    camera_controls()
                    setup_screen()

                elif g == 0:
                    # capture picture
                    button(0,0,1)
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
                        button(0,0,1)
                        text(0,3,0,1,"STOP",ft,0)
                        text(0,3,1,1,"Video",ft,0)
                        if video_width > vlimit:
                            if usb == 0: 
                                vid_capture = cv2.VideoCapture(0)
                            if usb == 1: 
                                vid_capture = cv2.VideoCapture(1)
                            # set to video camera resolution
                            vid_capture.set(3,video_width)
                            vid_capture.set(4,video_height)
                        else:
                            # set to video camera resolution
                            cam = pygame.camera.Camera(path,(video_width,video_height))
                            cam.start()
                        vid_cod = cv2.VideoWriter_fourcc(*'MP4V')
                        # make video filename YYMMDDHHMMSS.mp4
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%y%m%d%H%M%S")
                        output = cv2.VideoWriter(vid_dir + timestamp + ".mp4", vid_cod, 17920/video_width, (video_width,video_height))
                        stop = 0
                        count = 0
                        while stop == 0:
                            for event in pygame.event.get():
                                if (event.type == MOUSEBUTTONUP):
                                    mousex, mousey = event.pos
                                    # stop video recording
                                    if mousex > preview_width and mousey < bh:
                                       stop = 1
                            if video_width > vlimit:
                                # use cv2 to record video
                                ret,frame = vid_capture.read()
                                output.write(frame)
                                count +=1
                                if count == sframe:
                                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    img = pygame.surfarray.make_surface(img)
                                    img = pygame.transform.rotate(img,270)
                                    image = pygame.transform.flip(img, True, False)
                            else:
                                # use pygame to record video
                                image = cam.get_image()
                                count +=1
                                img = pygame.transform.rotate(image,270)
                                img = pygame.transform.flip(img, True, False)
                                img = pygame.surfarray.array3d(img)
                                frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                output.write(frame)
                            # show frame during recording
                            if count == sframe:
                                count = 0
                                imageq = pygame.transform.scale(image, [preview_width,preview_height])
                                catSurfaceObj = imageq
                                windowSurfaceObj.blit(catSurfaceObj,(0,0))
                                pygame.draw.rect(windowSurfaceObj,(255,0,0),Rect(10,10,20,20))
                                pygame.display.update()
                        if video_width > vlimit:
                            vid_capture.release()
                        else:
                            cam.stop()
                        output.release()
                    button(0,0,0)
                    text(0,1,0,1,"CAPTURE",ft,7)
                    text(0,1,1,1,"Still",ft,7)
                    text(0,1,1,1,"Video",ft,7)
                    # restart preview   
                    cam = pygame.camera.Camera(path,(preview_width,preview_height))
                    cam.start()
                else:
                    # change a camera parameter
                    p = int(parameters[((g-2)*3) + 5])
                    if mousex < preview_width + int(bw/2):
                        if int(parameters[((g-2)*3) + 3]) == -1:
                           p -=1
                        else:
                           p -=int(parameters[((g-2)*3) + 3])
                        if int(parameters[((g-2)*3) + 1]) != -1:
                           p = max(p,int(parameters[((g-2)*3) + 1]))
                        else:
                           p = max(p,0)
                           
                    else:
                        if int(parameters[((g-2)*3) + 3]) == -1:
                           p +=1
                        else:
                           p +=int(parameters[((g-2)*3) + 3])
                        if int(parameters[((g-2)*3) + 2]) != -1:
                            p = min(p,int(parameters[((g-2)*3) + 2]))
                        else:
                            p = min(p,1)
                    parameters[((g-2)*3) + 5] = str(p)
                    text(int(g/2),3,1,1,str(p),fv,7)
                    txt = "v4l2-ctl -c " + parameters[(g-2)*3] + "=" + str(p)
                    os.system(txt)
                    if int(parameters[((g-2)*3) + 1]) != -1:
                        pygame.draw.rect(windowSurfaceObj,greyColor,Rect(preview_width,(int(g/2) * bh) + 2,bw,5))
                        j = int(int(parameters[((g-2)*3) + 5]) / (int(parameters[((g-2)*3) + 2]) - int(parameters[((g-2)*3) + 1]))  * (bw))
                        pygame.draw.rect(windowSurfaceObj,(100,100,100),Rect(preview_width + 2,(int(g/2) * bh) + 2,j+1,5))

               

