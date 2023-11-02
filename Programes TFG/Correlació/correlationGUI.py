from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import os

def setup():
    """
    Set up the environment and load the images.
    """
    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
    state_images = ["empty.jpg", "half.jpg", "full.jpg"]
    captured_path = os.path.join(images_dir, "test1.jpg")
    paths = [os.path.join(images_dir, img) for img in state_images]
    matrices_gray = [image_to_matrix(path) for path in paths]

    return {
        'state_images': state_images,
        'captured_image': captured_path,
        'paths': paths,
        'matrices_gray': matrices_gray
    }

def image_to_matrix(image_path):
    """
    Convert the image to a grayscale matrix.
    """
    img = Image.open(image_path)
    img_gray = img.convert('L')
    img_gray_resized = img_gray.resize(img.size)
    img_matrix = np.array(img_gray_resized)
    return img_matrix, img_gray_resized

def correlate_images(img1, img2):
    std1 = np.std(img1)
    std2 = np.std(img2)

    if std1 == 0 or std2 == 0:
        print("One or both images have a zero standard deviation, correlation cannot be calculated.")
        return None
    else:
        return np.corrcoef(img1.flatten(), img2.flatten())[0, 1]

def plot(captured_image, closest_state_image, captured_path, closest_state_path, captured_matrix, closest_state_matrix, captured_gray, closest_state_gray, correlation, border_color='black', border_width=3):
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
    ax1.set_title(f'Captured Image')
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
        captured_matrix.flatten(),
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
    plt.show()

def main():
    setup_results = setup()
    captured_image_path = setup_results['captured_image']
    captured_image_matrix, captured_image_gray = image_to_matrix(captured_image_path)
    correlations = [correlate_images(captured_image_matrix, state_img[0]) for state_img in setup_results['matrices_gray']]
    
    max_correlation_index = np.argmax(correlations)
    max_correlation = correlations[max_correlation_index]
    
    closest_state_image = setup_results["state_images"][max_correlation_index]
    closest_state_path = setup_results["paths"][max_correlation_index]
    closest_state_matrix, closest_state_gray = setup_results["matrices_gray"][max_correlation_index]

    print(f'Closest state: {closest_state_image} with correlation coefficient: {max_correlation}')

    plot(captured_image=setup_results['captured_image'], closest_state_image=closest_state_image, 
         captured_path=captured_image_path, closest_state_path=closest_state_path, 
         captured_matrix=captured_image_matrix, closest_state_matrix=closest_state_matrix, 
         captured_gray=captured_image_gray, closest_state_gray=closest_state_gray, 
         correlation=max_correlation)

if __name__ == '__main__':
    main()
