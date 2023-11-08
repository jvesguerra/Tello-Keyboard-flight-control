from djitellopy import Tello
import keyboard

tello = Tello()
tello.connect()

print(tello.get_battery())
while True:
    if keyboard.is_pressed("q"):
        tello.takeoff()
    if keyboard.is_pressed("p"):
        tello.land()
    if keyboard.is_pressed("i"):
        tello.move_forward(30)
    if keyboard.is_pressed("m"):
        tello.move_back(30)
    if keyboard.is_pressed("j"):
        tello.move_left(30)
    if keyboard.is_pressed("k"):
        tello.move_right(30)
    if keyboard.is_pressed("s"):
        tello.rotate_clockwise(30)
    if keyboard.is_pressed("a"):
        tello.rotate_counter_clockwise(30)
    if keyboard.is_pressed("w"):
        tello.move_up(30)
    if keyboard.is_pressed("z"):
        tello.move_down(30)
    else:
        continue
