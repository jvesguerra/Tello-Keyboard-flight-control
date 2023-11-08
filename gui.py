import keyboard
from djitellopy import Tello

# Create a Tello object
tello = Tello()

# Connect to the Tello drone
tello.connect()


# Function to handle keyboard inputs
def keyboard_control(e):
    if e.event_type == keyboard.KEY_DOWN:
        if e.name == "q":
            tello.takeoff()
        if e.name == "p":
            tello.land()
        if e.name == "i":
            tello.move_forward(30)
        if e.name == "m":
            tello.move_back(30)
        if e.name == "j":
            tello.move_left(30)
        if e.name == "k":
            tello.move_right(30)
        if e.name == "s":
            tello.rotate_clockwise(30)
        if e.name == "a":
            tello.rotate_counter_clockwise(30)
        if e.name == "w":
            tello.move_up(30)
        if e.name == "z":
            tello.move_down(30)


# Register the keyboard event handler
keyboard.hook(keyboard_control)

# Wait for keyboard input until you decide to exit
keyboard.wait("p")

# Land and disconnect from the drone
tello.land()
tello.end()
