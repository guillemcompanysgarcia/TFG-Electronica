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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image1 = "normal.png"
    image2 = "invertida.png"
    path1 = os.path.join(script_dir, "Data", image1)
    path2 = os.path.join(script_dir, "Data", image2)
    img1_matrix, img1_gray = image_to_matrix(path1)
    img2_matrix, img2_gray = image_to_matrix(path2)

    return {
        'image1': image1,
        'image2': image2,
        'path1': path1,
        'path2': path2,
        'img1_matrix': img1_matrix,
        'img2_matrix': img2_matrix,
        'img1_gray': img1_gray,
        'img2_gray': img2_gray
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

def plot(image1, image2,path1, path2, img1_matrix, img2_matrix, img1_gray, img2_gray, correlation, border_color='black', border_width=3):
    """
    Plot images and the correlation scatter plot.
    """
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(2, 3)

    img1 = Image.open(path1)
    img2 = Image.open(path2)

    # Display Image 1 (Original)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(img1)
    ax1.set_title(f'Imatge 1 "{image1}"')
    ax1.axis('off')
    ax1.add_patch(Rectangle((0, 0), img1.width - 1, img1.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display Image 2 (Original)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(img2)
    ax2.set_title(f'Imatge 2 "{image2}"')
    ax2.axis('off')
    ax2.add_patch(Rectangle((0, 0), img2.width - 1, img2.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display Image 1 (Grayscale)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.imshow(img1_gray, cmap='gray')
    ax3.set_title(f'Escala de grisos Imatge 1')
    ax3.axis('off')
    ax3.add_patch(Rectangle((0, 0), img1_gray.width - 1, img1_gray.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display Image 2 (Grayscale)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.imshow(img2_gray, cmap='gray')
    ax4.set_title(f'Escala de grisos Imatge 2')
    ax4.axis('off')
    ax4.add_patch(Rectangle((0, 0), img2_gray.width - 1, img2_gray.height - 1, edgecolor=border_color, linewidth=border_width, fill=False))

    # Display the heat map
    ax5 = fig.add_subplot(gs[:, 2])
    heatmap, xedges, yedges, img = ax5.hist2d(
    img1_matrix.flatten(),
    img2_matrix.flatten(),
    bins=500,
    cmap='plasma',
    range=[[0, 255], [0, 255]],
    vmin=0,
    vmax=150
    )
    ax5.set_xlabel('Image 1 Intensity Values')
    ax5.set_ylabel('Image 2 Intensity Values')
    ax5.set_title(f'Correlation: {correlation:.2f}')
    cbar = plt.colorbar(img, ax=ax5)
    cbar.ax.set_ylabel('Counts')

    plt.tight_layout()
    plt.show()


def main():
    setup_results = setup()
    img1_matrix = setup_results['img1_matrix']
    img2_matrix = setup_results['img2_matrix']
    
    std1 = np.std(img1_matrix)
    std2 = np.std(img2_matrix)

    if std1 == 0 or std2 == 0:
        print("One or both images have a zero standard deviation, correlation cannot be calculated.")
    else:
        correlation = np.corrcoef(img1_matrix.flatten(), img2_matrix.flatten())[0, 1]
        print(f'Correlation coefficient: {correlation}')
        plot(correlation=correlation, **setup_results)

        

if __name__ == '__main__':
    main()