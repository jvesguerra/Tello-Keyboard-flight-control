from djitellopy import Tello
from Buttons import Button as button
import cv2
import pygame
import numpy as np
import time

# Speed of the drone
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 120

w, h = 960, 640
fbRange = [25000, 35000]
pid = [0.4, 0.4, 0]
pError = 0
isFollowingFace = False

hsvVals = [0,0,117,179,22,219] #will change depending on the color picker
sensors = 3 #width of the image should be divisible by the value of sensor
threshold = 0.2
width, height = 480, 360 #change this
sensitivity = 3 #if number is high, then less sensitive
weigths = [-25, -15, 0, 15, 25]
curve = 0
fSpeed = 15

frame = None

class FrontEnd(object):
    def __init__(self):
        # Init pygame
        pygame.init()

        # Create pygame window
        pygame.display.set_caption("Exercise 9")
        self.screen = pygame.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False
        self.face_tracking_active = False
        self.line_following_active = False

        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):
        global frame
        self.tello.connect()
        self.tello.set_speed(self.speed)

        # In case streaming is on. This happens when we quit this program without the escape key.
        if self.tello.stream_on:
            self.tello.streamoff()
        self.tello.streamon()

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            up_button = button(200, 450, image=pygame.image.load("images/W.png"))
            down_button = button(200, 650, image=pygame.image.load("images/Z.png"))
            rot_left_button = button(100, 550, image=pygame.image.load("images/A.png"))
            rot_right_button = button(300, 550, image=pygame.image.load("images/S.png"))
            forward_button = button(750, 450, image=pygame.image.load("images/I.png"))
            backward_button = button(750, 650, image=pygame.image.load("images/M.png"))
            left_button = button(650, 550, image=pygame.image.load("images/J.png"))
            right_button = button(850, 550, image=pygame.image.load("images/K.png"))
            takeoff_button = button(75, 100, image=pygame.image.load("images/Q.png"))
            land_button = button(75, 220, image=pygame.image.load("images/P.png"))



            if frame_read.stopped:
                break

            self.screen.fill([0, 0, 0])

            frame = frame_read.frame

            # battery
            text = "Battery: {}%".format(self.tello.get_battery())
            cv2.putText(frame,
                        text,
                        (750, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # frame, info = self.findFace(frame)
            

            if self.face_tracking_active:
                global pError
                frame, info = self.findFace(frame_read.frame)
                pError = self.trackFace(info, w, pid, pError)
            
            if self.line_following_active:
                imagee = cv2.flip(frame)
                imageThres = self.thresholding(imagee)
                cx = self.getContours(imageThres,imagee)
                senOut = self.getSensorOutput(imageThres, sensors)
                self.sendCommands(senOut, cx)


            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))

            for buttons in [up_button, down_button,
                        rot_left_button, rot_right_button,
                        forward_button, backward_button,
                        left_button, right_button,
                        takeoff_button, land_button]:
                        buttons.update(self.screen)
            pygame.display.update()



            time.sleep(1 / FPS)

        # Call it always before finishing. To deallocate resources.
        self.tello.end()

    def keydown(self, key):
        # Update velocities based on key pressed

        if key == pygame.K_i:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_m:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_j:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_k:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_z:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw counterclockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_s:  # set yaw clockwise velocity
            self.yaw_velocity = S
        elif key == pygame.K_f:  # start face tracking
           self.toggleFaceTracking()
        elif key == pygame.K_f:  # start line following
           self.toggleLineFollowing()


    def keyup(self, key):
        # Update velocities based on key released

        if key == pygame.K_i or key == pygame.K_m:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_j or key == pygame.K_k:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_z:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_s:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_q:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_p:  # land
            self.tello.land()
            self.send_rc_control = False

    def update(self):
        # Update routine. Send velocities to Tello.
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity,
                                       self.for_back_velocity,
                                       self.up_down_velocity,
                                       self.yaw_velocity)
    def toggleFaceTracking(self):
        global pError
        self.face_tracking_active = not self.face_tracking_active
        if self.face_tracking_active:
            pError = 0
    
    
    def findFace(self,img):
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

        myFaceListC = []
        myFaceListArea = []

        for(x,y,w,h) in faces:
            print(x,y,w,h)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            cx = x + w//2
            cy = y + h//2
            area = w*h
            myFaceListArea.append(area)
            myFaceListC.append([cx,cy])
    
    
        if len(myFaceListArea) !=0:
            i = myFaceListArea.index(max(myFaceListArea))
            return img, [myFaceListC[i],myFaceListArea[i]]
        else:
            return img,[[0,0],0]

    def trackFace(self,info,w,pid,pError):

        area = info[1]
        x,y = info[0]
        fb = 0

        error = x - w//2
        speed = pid[0]*error + pid[1]*(error-pError)
        speed = int(np.clip(speed,-100,100))
        

        if area > fbRange[0] and area < fbRange[1]:
            fb = 0
        elif area > fbRange[1]:
            fb = -60
        elif area < fbRange[0] and area != 0:
            fb = 60

        if x == 0:
            speed = 0
            error = 0

        # print("FB, speed", fb, speed)

        self.tello.send_rc_control(0,fb, 0, speed)

        return error
    
    def toggleLineFollowing(self):
        self.line_following_active = not self.line_following_active

    def thresholding(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])
        upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])
        mask = cv2.inRange(hsv, lower, upper)

        return mask
    
    def getContours(self, imgThreshold, img):
        cx = 0
        contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours != 0):
            biggest = max(contours, key = cv2.contourArea)
            x,y,w,h = cv2.boundingRect(biggest)
            cx = x + w//2
            cy = y + h//2

            cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
            cv2.circle(img, (cx, cy), 10, (0,255,0), cv2.FILLED)

        return cx
    
    def getSensorOutput(self, imgThres, sensors):
        imgs = np.hsplit(imgThres, sensors)
        totalPixels = (frame.shape[1] // sensors) * frame.shape[0] #frame(?)
        senOut = []
        for x,im in enumerate(imgs):
            pixelCount = cv2.countNonZero(im)
            if pixelCount > threshold * totalPixels:
                senOut.append(1)
            else:
                senOut.append(0)
            cv2.imshow(str(x), im)
        
        print(senOut)
        return senOut
    
    def sendCommands(self, senOut, cx):
        global curve

        #translation
        lr = (cx - width // 2) // sensitivity
        lr = int(np.clip(lr, -10, 10))
        if lr < 2 and lr > -2: lr = 0

        if senOut == [1,0,0]:
            curve = weigths[0]
        elif senOut == [1,1,0]:
            curve = weigths[1]
        elif senOut == [0,1,0]:
            curve = weigths[2]
        elif senOut == [0,1,1]:
            curve = weigths[3]
        elif senOut == [0,0,1]:
            curve = weigths[4]
        
        elif senOut == [0,0,0]:
            curve = weigths[2]
        elif senOut == [1,1,1]:
            curve = weigths[2]
        elif senOut == [1,0,1]:
            curve = weigths[2]
        

        self.tello.send_rc_control(lr, fSpeed, 0, curve)

        

    


def main():
    frontend = FrontEnd()

    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()

#3:25:00 for the conversion to drone