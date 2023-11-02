import time
import picamera
import datetime

import io
import os

from PIL import Image, ImageTk

import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedTk

def save_file(file_stream, file_path):
    with open(file_path, 'wb') as f:
        f.write(file_stream.getbuffer())

def generate_file_path(file_type, duration=None, framerate=None, resolution=None):
    data_folder = 'Data'

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    extension = 'jpg' if file_type.startswith('image') else 'h264'
    res_str = f"{resolution[0]}x{resolution[1]}" if resolution else ""
    settings_str = ""

    if file_type == "video":
        settings_str = f"{duration}s_{framerate}fps_{res_str}"
    elif file_type == "image":
        settings_str = f"{res_str}"

    return os.path.join(data_folder, f"{file_type}_{datetime.datetime.now().strftime('%d%m%Y_%H%M%S')}_{settings_str}.{extension}")

def resize_image(img, max_width, max_height):
    img_width, img_height = img.size
    scale_factor = min(max_width / img_width, max_height / img_height)
    new_width, new_height = int(img_width * scale_factor), int(img_height * scale_factor)
    return img.resize((new_width, new_height), Image.ANTIALIAS)

def take_photo(camera, display_canvas, resolution = (1920, 1080)):
    camera.resolution = resolution
    img_stream = io.BytesIO()
    camera.capture(img_stream, format='jpeg')

    img_stream.seek(0)
    file_path = generate_file_path('image', resolution=resolution)
    save_file(img_stream, file_path)

    img_stream.seek(0)
    img = Image.open(img_stream)
    img_resized = resize_image(img, display_canvas.winfo_width(), display_canvas.winfo_height())
    img_tk = ImageTk.PhotoImage(img_resized)
    return img_tk, file_path



def record_video(camera, display_canvas, resolution=(1920, 1080), framerate=30, duration=5):
    camera.resolution = resolution
    camera.framerate = framerate

    file_path = generate_file_path('video', duration=duration, framerate=framerate, resolution=resolution)

    # Capture the first frame as an image
    img_stream = io.BytesIO()
    camera.capture(img_stream, format='jpeg')
    img_stream.seek(0)
    img = Image.open(img_stream)
    img_resized = resize_image(img, display_canvas.winfo_width(), display_canvas.winfo_height())
    img_tk = ImageTk.PhotoImage(img_resized)
    display_canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
    display_canvas.image = img_tk
    
    # Record the video
    camera.start_recording(file_path)
    time.sleep(duration)
    camera.stop_recording()

    return img_tk, file_path
    
def main():
    def on_take_photo_button_click():
        resolution_choice = resolution_var.get()
        resolution = (1920, 1080) if resolution_choice == "Full HD" else (1280, 720)

        img_tk, file_path = take_photo(camera=camera, display_canvas=display_canvas, resolution=resolution)
        display_canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        display_canvas.image = img_tk

        label_5.config(text=f"Image saved as: {file_path}")

    def on_record_video_button_click():
        resolution_choice = resolution_var.get()
        resolution = (1920, 1080) if resolution_choice == "Full HD" else (1280, 720)

        framerate_choice = framerate_var.get()
        framerate = 30 if framerate_choice == "30 fps" else 60

        duration_choice = duration_var.get()
        duration = int(duration_choice.split(" ")[0])

        img_tk, file_path = record_video(camera=camera, display_canvas=display_canvas, resolution=resolution, framerate=framerate, duration=duration)
        display_canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
        display_canvas.image = img_tk

        label_5.config(text=f"Video saved as: {file_path}")

    with picamera.PiCamera() as camera:

        # Create the main window
        root = ThemedTk(theme="arc")
        root.title("Camera Panel")
        root.geometry("685x600")

        label_1 = ttk.Label(root, text="Actions:", font=("Arial", 16))
        label_1.place(x=20, y=20)

        take_photo_button = ttk.Button(root, text="Take Photo", command= on_take_photo_button_click)
        take_photo_button.place(x=20, y=60)

        take_video_button = ttk.Button(root, text="Record Video", command= on_record_video_button_click)
        take_video_button.place(x=20, y=100)

        label_2 = ttk.Label(root, text="Settings:", font=("Arial", 16))
        label_2.place(x=200, y=20)

        label_res = ttk.Label(root, text="Resolution:")
        label_res.place(x=200, y=60)
        resolution_var = tk.StringVar(root)
        resolution_var.set("Full HD")
        resolution_combobox = ttk.Combobox(root, textvariable=resolution_var, values=("Full HD", "HD"), state="readonly")
        resolution_combobox.place(x=280, y=60)

        label_3 = ttk.Label(root, text="Framerate:")
        label_3.place(x=200, y=100)
        framerate_var = tk.StringVar(root)
        framerate_var.set("30 fps")
        framerate_option = ttk.Combobox(root, textvariable=framerate_var, values=("30 fps", "60 fps"), state="readonly")
        framerate_option.place(x=280, y=100)

        label_4 = ttk.Label(root, text="Duration:")
        label_4.place(x=200, y=140)
        duration_var = tk.StringVar(root)
        duration_var.set("5 seconds")
        duration_option = ttk.Combobox(root, textvariable=duration_var, values=("5 seconds", "10 seconds", "15 seconds"), state="readonly")
        duration_option.place(x=280, y=140)

        label_5 = ttk.Label(root, text="", font=("Arial", 12))
        label_5.place(x=20, y=570)
        display_canvas = tk.Canvas(root, width=640, height=360)
        display_canvas.place(x=20, y=200)
        root.mainloop()

if __name__ == "__main__":
    main()
