"""
Structural Chosen-Plaintext Attack Simulation
Tests encryption behavior on structured inputs: gradients, stripes, checkerboards, blocks.
"""

import numpy as np
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.enhanced_cipher import EnhancedPWLCM as LHCMedEncryption


def create_gradient_image(size: int = 256) -> np.ndarray:
    """Create horizontal gradient image."""
    return np.tile(np.arange(256, dtype=np.uint8), (size, 1))[:size, :size]


def create_vertical_gradient(size: int = 256) -> np.ndarray:
    """Create vertical gradient image."""
    return np.tile(np.arange(256, dtype=np.uint8).reshape(-1, 1), (1, size))[:size, :size]


def create_checkerboard(size: int = 256, block_size: int = 8) -> np.ndarray:
    """Create checkerboard pattern."""
    img = np.zeros((size, size), dtype=np.uint8)
    for i in range(size):
        for j in range(size):
            if ((i // block_size) + (j // block_size)) % 2 == 0:
                img[i, j] = 255
    return img


def create_stripes(size: int = 256, stripe_width: int = 16, vertical: bool = True) -> np.ndarray:
    """Create striped pattern."""
    img = np.zeros((size, size), dtype=np.uint8)
    for i in range(size):
        for j in range(size):
            coord = j if vertical else i
            if (coord // stripe_width) % 2 == 0:
                img[i, j] = 255
    return img


def create_blocks(size: int = 256, block_size: int = 64) -> np.ndarray:
    """Create block pattern."""
    img = np.zeros((size, size), dtype=np.uint8)
    for i in range(0, size, block_size * 2):
        for j in range(0, size, block_size * 2):
            img[i:i+block_size, j:j+block_size] = 255
    return img


def analyze_correlation(plain: np.ndarray, cipher: np.ndarray) -> dict:
    """Analyze correlation between plaintext structure and ciphertext."""
    # Flatten for correlation
    p_flat = plain.flatten().astype(float)
    c_flat = cipher.flatten().astype(float)
    
    # Pearson correlation
    correlation = np.corrcoef(p_flat, c_flat)[0, 1]
    
    # Histogram uniformity of ciphertext
    hist, _ = np.histogram(cipher, bins=256, range=(0, 256))
    hist_std = np.std(hist)
    expected_std_uniform = np.sqrt(len(c_flat) / 256)  # Theoretical for uniform
    
    # Entropy
    hist_norm = hist / hist.sum()
    hist_norm = hist_norm[hist_norm > 0]
    entropy = -np.sum(hist_norm * np.log2(hist_norm))
    
    return {
        'correlation': abs(correlation),
        'cipher_entropy': entropy,
        'histogram_std': hist_std,
        'uniformity_ratio': hist_std / expected_std_uniform,
        'is_uniform': hist_std < expected_std_uniform * 1.5
    }


def run_structural_cpa_tests() -> dict:
    """Run full structural CPA test battery."""
    print("=== Structural Chosen-Plaintext Attack Simulation ===\n")
    
    # Initialize encryption with random key
    key = os.urandom(32)
    cipher = LHCMedEncryption(key)
    
    # Test patterns
    test_cases = {
        'Horizontal Gradient': create_gradient_image(),
        'Vertical Gradient': create_vertical_gradient(),
        'Checkerboard 8x8': create_checkerboard(block_size=8),
        'Checkerboard 16x16': create_checkerboard(block_size=16),
        'Vertical Stripes': create_stripes(vertical=True),
        'Horizontal Stripes': create_stripes(vertical=False),
        'Block Pattern': create_blocks()
    }
    
    results = {}
    
    for name, plaintext in test_cases.items():
        print(f"Testing: {name}...")
        
        # Encrypt
        ciphertext = cipher.encrypt_image(plaintext)
        
        # Analyze
        analysis = analyze_correlation(plaintext, ciphertext)
        results[name] = analysis
        
        print(f"  Correlation: {analysis['correlation']:.6f}")
        print(f"  Cipher Entropy: {analysis['cipher_entropy']:.4f}")
        print(f"  Histogram Uniform: {analysis['is_uniform']}")
    
    # Summary
    all_correlations = [r['correlation'] for r in results.values()]
    all_entropies = [r['cipher_entropy'] for r in results.values()]
    
    summary = {
        'max_correlation': max(all_correlations),
        'avg_correlation': np.mean(all_correlations),
        'min_entropy': min(all_entropies),
        'avg_entropy': np.mean(all_entropies),
        'all_uniform': all(r['is_uniform'] for r in results.values()),
        'interpretation': 'Resistant' if max(all_correlations) < 0.01 else 'Potential Leakage'
    }
    
    print(f"\n=== Summary ===")
    print(f"Max correlation across all patterns: {summary['max_correlation']:.6f}")
    print(f"Average entropy: {summary['avg_entropy']:.4f}")
    print(f"All histograms uniform: {summary['all_uniform']}")
    print(f"Interpretation: {summary['interpretation']}")
    
    return {'individual': results, 'summary': summary}


if __name__ == "__main__":
    results = run_structural_cpa_tests()
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    with open(os.path.join(results_dir, 'structural_cpa_results.txt'), 'w') as f:
        f.write("Structural CPA Test Results\n")
        f.write("="*50 + "\n\n")
        
        for name, analysis in results['individual'].items():
            f.write(f"{name}:\n")
            f.write(f"  Correlation: {analysis['correlation']:.6f}\n")
            f.write(f"  Entropy: {analysis['cipher_entropy']:.4f}\n")
            f.write(f"  Uniform: {analysis['is_uniform']}\n\n")
        
        f.write("Summary:\n")
        for k, v in results['summary'].items():
            f.write(f"  {k}: {v}\n")
    
    print(f"\nResults saved to results/structural_cpa_results.txt")
