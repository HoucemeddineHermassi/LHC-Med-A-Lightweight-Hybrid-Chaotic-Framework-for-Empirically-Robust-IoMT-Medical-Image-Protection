"""
Cryptographic Attack Simulator for LHC-Med
Implements Chosen-Plaintext Attack (CPA) and Known-Plaintext Attack (KPA) simulations.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto.enhanced_cipher import EnhancedPWLCM

def simulate_cpa_pathological():
    """
    Simulate Chosen-Plaintext Attack using pathological images:
    - All-zero image
    - All-white image (255)
    - Single pixel modified image (Differential Analysis)
    """
    print("--- Starting Chosen-Plaintext Attack (CPA) Simulation ---")
    
    key = os.urandom(32)
    cipher = EnhancedPWLCM(key)
    
    # 1. All-zero image
    zero_img = np.zeros((128, 128), dtype=np.uint8)
    encrypted_zero = cipher.encrypt_image(zero_img)
    
    # 2. All-white image
    white_img = np.ones((128, 128), dtype=np.uint8) * 255
    encrypted_white = cipher.encrypt_image(white_img)
    
    # Analysis: Entropy of encrypted pathological images
    def calculate_entropy(img):
        marg = np.histogram(img, bins=256, range=(0, 255), density=True)[0]
        marg = marg[marg > 0]
        return -np.sum(marg * np.log2(marg))

    entropy_zero = calculate_entropy(encrypted_zero)
    entropy_white = calculate_entropy(encrypted_white)
    
    print(f"Entropy (All-Zero Cipher): {entropy_zero:.6f}")
    print(f"Entropy (All-White Cipher): {entropy_white:.6f}")
    
    # Differential Analysis bit-level
    zero_img_mod = zero_img.copy()
    zero_img_mod[64, 64] = 1 # Change 1 pixel
    encrypted_zero_mod = cipher.encrypt_image(zero_img_mod)
    
    npcr = np.mean(encrypted_zero != encrypted_zero_mod) * 100
    print(f"NPCR (Single Pixel Change in All-Zero): {npcr:.6f}%")
    
    # Save visuals
    plt.figure(figsize=(15, 6))
    plt.subplot(131)
    plt.title("Cipher (All-Zero Input)", fontsize=14)
    plt.imshow(encrypted_zero, cmap='gray')
    plt.axis('off')
    
    plt.subplot(132)
    plt.title("Cipher (All-White Input)", fontsize=14)
    plt.imshow(encrypted_white, cmap='gray')
    plt.axis('off')
    
    plt.subplot(133)
    plt.title("Detailed Difference Map", fontsize=14)
    plt.imshow(encrypted_zero ^ encrypted_zero_mod, cmap='magma')
    plt.axis('off')
    
    plt.tight_layout()
    
    save_path = os.path.join(os.path.dirname(__file__), 'results', 'cpa_results.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=100)
    plt.close()
    print(f"CPA Visuals saved to {save_path}")



def simulate_kpa_recovery():
    """
    Simulate Known-Plaintext Attack:
    Attempt to recover keystream by XORing Plaintext and Ciphertext.
    Check if recovered keystream can decrypt another block.
    """
    print("\n--- Starting Known-Plaintext Attack (KPA) Simulation ---")
    
    key = os.urandom(32)
    cipher = EnhancedPWLCM(key)
    
    # Attacker has Plaintext P1 and its Ciphertext C1
    p1 = np.random.randint(0, 256, size=(64, 64), dtype=np.uint8)
    c1 = cipher.encrypt_image(p1)
    
    # Naive keystream recovery (assuming simple stream cipher, which it's NOT)
    recovered_keystream_naive = p1 ^ c1
    
    # Attacker intercepts C2, tries to decrypt using recovered_keystream_naive
    p2_real = np.random.randint(0, 256, size=(64, 64), dtype=np.uint8)
    c2 = cipher.encrypt_image(p2_real)
    
    p2_cracked = c2 ^ recovered_keystream_naive
    
    # Measure success
    similarity = np.mean(p2_cracked == p2_real) * 100
    print(f"Naive KPA Success Rate (Simultaneous Decryption): {similarity:.2f}%")
    print("Interpretation: Since LHC-Med uses dynamic SPN and content-adaptive rounds, simple KPA fails.")

if __name__ == "__main__":
    simulate_cpa_pathological()
    simulate_kpa_recovery()
