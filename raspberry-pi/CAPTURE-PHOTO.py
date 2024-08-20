#!/usr/bin/env python3
#############################################################
# Usage: python camerastand.py <NAME>
# Takes a picture with attached camera and saves to Rasberry
# Pi and/or Remote server (bases on user selection)
#############################################################

# Import necessary packages
import sys
from datetime import datetime
import serial
import subprocess as sp
from tkinter import *
from tkinter import messagebox
import os
import re
import shutil
# This function takes a picture with a camera.
# It requires the computer to have gphoto2 installed and uses
# the subprocess module to write to the command line to take pictures.
# Usage: takepic("picture_name", save_locally, uplaod_to_server)
class App(object):
    def __init__(self, master):
        # Create a frame for the GUI componenets
        frame = Frame(root, width=600, height=600)
        frame.pack()

        # Create an entry field for the user to enter the filename
        self.name = Entry(frame, width=35, font=('Verdana', 18))
        self.name.pack(side=TOP)

        # Create a button to take the picture
        self.button = Button(frame, text="Click here to take a picture!", fg="black", command=self.takePic, height=5, width=20)
        self.button.pack(side=LEFT)

        # Create a label to display the status
        self.status = Label(frame, text=" ", font=('Verdana', 18))
        self.status.pack(side=BOTTOM)

        # Create radiobuttons to allow the user to select where to save the image
        self.save_location = StringVar()
        self.save_location.set("local")

        Radiobutton(frame, text="Save Locally", variable=self.save_location, value="local").pack(anchor=W)
        Radiobutton(frame, text="Save to Public Drive", variable=self.save_location, value="public").pack(anchor=W)
        Radiobutton(frame, text="Save to Both", variable=self.save_location, value="both").pack(anchor=W)

    def takePic(self):
        # Check if the user has entered a filename
        if self.name.get() == "":
            # If not, display an error message
            messagebox.showerror(title="Error", message="Please enter a filename")
        else:
            # Get the filepath of the picture
            picName = self.name.get().rstrip()
            date = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            filename = f"{picName}_{date}.jpg"

            # Modify local path and public path to store the acquired images
            local_path = f"/home/pi/Desktop/PHOTOS/{filename}"
            # Write your server or cloud storage path here
            public_path = f"/mnt/public/YOUR_PUBLIC_DRIVE_FOLDER/{filename}"

            # Capture the image
            temp_path = f"/tmp/{filename}"
            sp.call(["gphoto2", "--trigger-capture", "--wait-event-and-download=FILEADDED", "--filename", temp_path])

            # Save based on user selection
            if self.save_location.get() in ["local", "both"]:
                shutil.copy2(temp_path, local_path)
                print(f"Image saved locally: {local_path}")

            if self.save_location.get() in ["public", "both"]:
                shutil.copy2(temp_path, public_path)
                print(f"Image saved to public drive: {public_path}")
                
           # Remove the temporary file
            os.remove(temp_path)
           
            # Clear the input fields
            self.name.delete(0, END)
            self.name.insert(0, "")

def main():
    # Use gphoto2 --auto-detect to check camera is still attached
    sp.call(["gphoto2", "--auto-detect"])

root = Tk()
root.wm_title("Photo Studio")
app = App(root)
root.mainloop()

if __name__ == "__main__":
    main()