#import picamera
import time
import datetime
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PIL import Image
import matplotlib.gridspec as gridspec
import numpy as np
from globals import script_dir
from matplotlib.patches import Rectangle

STATE_IMAGES = None
MATRICES_GRAY = None

def setup():
    camera = picamera.PiCamera()
    camera.resolution = (1920, 1080)
    startup_setup()
    return camera

def startup_setup():
    global STATE_IMAGES
    global MATRICES_GRAY
    global paths
    global image_paths

    STATE_IMAGES = ["buit.jpg", "mig.jpg", "ple.jpg"]

    paths = [os.path.join(script_dir, "stock_correlation_images", img) for img in STATE_IMAGES]

    # Create a dictionary that maps each state image to its path.
    image_paths = {img: path for img, path in zip(STATE_IMAGES, paths)}

    MATRICES_GRAY = [image_to_matrix(path) for path in paths]

def correlate_image(output_filename_path):
    global paths
    global image_paths

    captured_image_matrix, captured_image_gray = image_to_matrix(output_filename_path)

    correlations = [correlate_images(captured_image_matrix, state_img[0]) for state_img in MATRICES_GRAY]

    max_correlation_index = np.argmax(correlations)

    max_correlation = correlations[max_correlation_index]

    closest_state_image = STATE_IMAGES[max_correlation_index]

    # Find the path of the closest_state_image using the image_paths dictionary.
    closest_state_path = image_paths[closest_state_image]

    closest_state_matrix, closest_state_gray = MATRICES_GRAY[max_correlation_index]

    output_filename = os.path.basename(output_filename_path)
    # Send data to save_plot
    correlation_result = save_plot(
        output_filename,
        output_filename_path,
        captured_image_matrix,
        captured_image_gray,
        max_correlation,
        closest_state_image,
        closest_state_path,
        closest_state_matrix,
        closest_state_gray,
        border_color='black',
        border_width=3
    )

    return correlation_result


def save_plot(captured_image, captured_path, captured_image_matrix,captured_gray, correlation, closest_state_image, closest_state_path, closest_state_matrix, closest_state_gray, border_color='black', border_width=3):
    """
    Plot images and the correlation scatter plot.
    """
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(2, 3)
    img1 = Image.open(captured_path)
    img2 = Image.open(closest_state_path)

    # Display Captured Image (Original)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(img1)
    ax1.set_title(f'"{captured_image}"')
    ax1.axis('off')
    ax1.add_patch(Rectangle((0, 0), img1.width - 1, img1.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display Closest State Image (Original)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(img2)
    ax2.set_title(f'Closest State Image "{closest_state_image}"')
    ax2.axis('off')
    ax2.add_patch(Rectangle((0, 0), img2.width - 1, img2.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display Captured Image (Grayscale)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.imshow(captured_gray, cmap='gray')
    ax3.set_title(f'Grayscale Captured Image')
    ax3.axis('off')
    ax3.add_patch(Rectangle((0, 0), captured_gray.width - 1, captured_gray.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display Closest State Image (Grayscale)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.imshow(closest_state_gray, cmap='gray')
    ax4.set_title(f'Grayscale Closest State Image')
    ax4.axis('off')
    ax4.add_patch(Rectangle((0, 0), closest_state_gray.width - 1, closest_state_gray.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display the heat map
    ax5 = fig.add_subplot(gs[:, 2])
    heatmap, xedges, yedges, img = ax5.hist2d(
        captured_image_matrix.flatten(),
        closest_state_matrix.flatten(),
        bins=500,
        cmap='plasma',
        range=[[0, 255], [0, 255]],
        vmin=0,
        vmax=150
    )
    ax5.set_xlabel('Captured Image Intensity Values')
    ax5.set_ylabel('Closest State Image Intensity Values')
    ax5.set_title(f'Correlation: {correlation:.2f}')
    cbar = plt.colorbar(img, ax=ax5)
    cbar.ax.set_ylabel('Counts')

    plt.tight_layout()

    output_dir = os.path.dirname(captured_path)
    filename = os.path.basename(captured_path)
    output_filename = 'correlation_result_' + filename
    output_path = os.path.join(output_dir, output_filename)

    # Save the figure to a file
    plt.savefig(output_path)

    return output_path


def image_to_matrix(image_path):

    img = Image.open(image_path)
    img_gray = img.convert('L')
    img_gray_resized = img_gray.resize(img.size)
    img_matrix = np.array(img_gray_resized)
    return img_matrix, img_gray_resized

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

def take_picture(camera,  resolution = (1920, 1080)):
    file_path = generate_file_path("image", resolution=resolution)
    camera.capture(file_path)
    print(f"Picture saved as {file_path}")
    return file_path

def take_video(camera, duration=5, output_path=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"video_{timestamp}.h264"
    if not output_path:
        output_path = "./"
    elif not output_path.endswith('/'):
        output_path += '/'
    camera.start_recording(output_path + filename)
    time.sleep(duration)
    camera.stop_recording()
    print(f"Video saved as {output_path + filename}")

def correlate_images(img1, img2):
    std1 = np.std(img1)
    std2 = np.std(img2)

    if std1 == 0 or std2 == 0:
        print("One or both images have a zero standard deviation, correlation cannot be calculated.")
        return None
    else:
        return np.corrcoef(img1.flatten(), img2.flatten())[0, 1]
    




def cleanup(camera):
    camera.close()
