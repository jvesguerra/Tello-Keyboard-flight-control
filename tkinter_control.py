import tkinter as tk
from tkinter import ttk
import cv2
from djitellopy import Tello
from pynput import keyboard

class TelloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tello Video Stream")

        # Create a label for displaying the battery percentage
        self.battery_label = ttk.Label(self.root, text="Battery Percentage: N/A")
        self.battery_label.pack()

        # Create a frame for the video feed
        self.video_frame = ttk.Label(self.root)
        self.video_frame.pack()

        # Create a Tello instance
        self.tello = Tello()

        # Connect to the Tello
        self.tello.connect()
        self.tello.streamon()

        # Create a function to update the video feed and battery percentage
        self.update_display()

        # Initialize the keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def update_display(self):
        # Update the battery percentage
        battery_percentage = self.tello.get_battery()
        self.battery_label.config(text=f'Battery Percentage: {battery_percentage}%')

        # Update the video feed
        frame = self.tello.get_frame_read().frame

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = tk.PhotoImage(data=frame.tobytes())
            self.video_frame.img = img
            self.video_frame.config(image=img)
            self.root.after(10, self.update_display)
        else:
            self.root.after(10, self.update_display)

    def on_key_press(self, key):
        try:
            key = key.char
            if key == 'q':
                # Take off
                self.tello.takeoff()
            elif key == 'p':
                # Land
                self.tello.land()
            elif key == 'i':
                #pitch forward
                self.tello.send_rc_control(0, 30, 0, 0)
            elif key == 'm':
                #pitch backward
                self.tello.send_rc_control(0, -30, 0, 0)
            elif key == 'j':
                #roll left
                self.tello.send_rc_control(-30, 0, 0, 0)
            elif key == 'k':
                #roll right
                self.tello.send_rc_control(30, 0, 0, 0)
            elif key == 's':
                #yaw right
                self.tello.send_rc_control(0, 0, 0, 30)
            elif key == 'a':
                #yaw left
                self.tello.send_rc_control(0, 0, 0, -30)
            elif key == 'w':
                #lift up
                self.tello.send_rc_control(0, 0, 30, 0)
            elif key == 'z':
                #lift down
                self.tello.send_rc_control(0, 0, -30, 0)
        except AttributeError:
            # Handle non-character keys (if needed)
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TelloApp(root)
    root.mainloop()