import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

# Add the enhanced_encryption directory to the path
sys.path.append(os.path.abspath('enhanced_encryption'))

from crypto.enhanced_cipher import EnhancedPWLCM

def plot_enhanced_correlation(image_path, output_path, key_bytes, max_points=10000):
    """
    Generate high-density, journal-quality correlation plots
    """
    print(f"Processing {image_path}...")
    img = Image.open(image_path).convert('L')
    plain = np.array(img)
    
    # Initialize cipher and encrypt
    cipher = EnhancedPWLCM(key_bytes)
    encrypted = cipher.encrypt_image(plain)
    
    # Set academic style
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 10,
        'axes.labelsize': 10,
        'axes.titlesize': 12,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 10,
        'figure.titlesize': 14
    })
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    directions = ['horizontal', 'vertical', 'diagonal']
    images = [plain, encrypted]
    image_names = ['Plain', 'Encrypted']
    colors = ['#2980b9', '#c0392b'] # Academic blue and red
    
    for i, (img_arr, img_name) in enumerate(zip(images, image_names)):
        for j, direction in enumerate(directions):
            ax = axes[i, j]
            
            # Extract adjacent pixels
            if direction == 'horizontal':
                x = img_arr[:, :-1].flatten()
                y = img_arr[:, 1:].flatten()
            elif direction == 'vertical':
                x = img_arr[:-1, :].flatten()
                y = img_arr[1:, :].flatten()
            else: # diagonal
                x = img_arr[:-1, :-1].flatten()
                y = img_arr[1:, 1:].flatten()
            
            # Higher density sampling
            if len(x) > max_points:
                indices = np.random.choice(len(x), max_points, replace=False)
                x = x[indices]
                y = y[indices]
            
            corr = np.corrcoef(x, y)[0, 1]
            
            # Plot with smaller dots and alpha
            ax.scatter(x, y, alpha=0.4, s=0.8, color=colors[i], edgecolors='none')
            ax.set_xlabel('Pixel Value $P(i, j)$')
            ax.set_ylabel(f'Adj. Pixel $P(i\', j\')$ ({direction})')
            ax.set_title(f'{img_name} - {direction.capitalize()}\n$r_{{xy}} = {corr:.6f}$')
            ax.grid(True, linestyle='--', alpha=0.4)
            ax.set_xlim(0, 255)
            ax.set_ylim(0, 255)
            ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(output_path, dpi=400, bbox_inches='tight')
    plt.close()
    print(f"Generated enhanced visualization: {output_path}")

if __name__ == "__main__":
    key = b'EnhancedPWLCM_SecretKey_2026Med1'.ljust(32, b'0')[:32]
    
    # Target files in paper directory
    images_to_process = [
        ('enhanced_encryption/visualization/Viral Pneumonia-9.png', 'paper/correlation_all_directions_Viral Pneumonia-9.png'),
        ('enhanced_encryption/visualization/image mokh.jpg', 'paper/correlation_all_directions_image mokh.jpg.png'),
        ('enhanced_encryption/Viral Pneumonia-10.png', 'paper/correlation_all_directions_Viral Pneumonia-10.png'),
        ('enhanced_encryption/visualization/imagemain.jpg', 'paper/correlation_all_directions_imagemain.jpg.png')
    ]
    
    for input_file, output_file in images_to_process:
        if os.path.exists(input_file):
            plot_enhanced_correlation(input_file, output_file, key)
        else:
            print(f"Warning: Input file {input_file} not found.")
