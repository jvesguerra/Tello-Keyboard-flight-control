from djitellopy import Tello
import cv2, math, time

tello = Tello()
tello.connect()

tello.streamon()
frame_read = tello.get_frame_read()

while True:
    # In reality you want to display frames in a seperate thread. Otherwise
    #  they will freeze while the drone moves.
    img = frame_read.frame
    cv2.imshow("drone", img)

    key = cv2.waitKey(1) & 0xff
    if key == ord('q'):  #takeoff
        tello.takeoff()
    elif key == ord('p'): #land
        tello.land()

    elif key == ord('i'): #pitch forward
        tello.move_forward(30)
    elif key == ord('m'): #pitch backward
        tello.move_back(30)

    elif key == ord('j'): #roll left
        tello.move_left(30)
    elif key == ord('k'): #roll right
        tello.move_right(30)

    elif key == ord('s'): #yaw right
        tello.rotate_clockwise(30)
    elif key == ord('a'):
        tello.rotate_counter_clockwise(30) #yaw left

    elif key == ord('w'): #lift up
        tello.move_up(30)
    elif key == ord('z'): #lift down
        tello.move_down(30)

    elif key == ord('b'): #display battery
        print(tello.get_battery())


