"""
Main Entry Point for Enhanced PWLCM Cipher
"""

import argparse
import numpy as np
from PIL import Image
from pathlib import Path

from crypto import EnhancedPWLCM
from metrics import SecurityMetrics
from visualization import PaperVisualizer


def main():
    parser = argparse.ArgumentParser(description='Enhanced PWLCM Medical Image Encryption')
    parser.add_argument('--mode', choices=['encrypt', 'full'], default='full',
                        help='Mode: encrypt only or full analysis')
    parser.add_argument('--input', type=str, required=True,
                        help='Input image path')
    parser.add_argument('--output', type=str, default='results/encrypted_image.png',
                        help='Output encrypted image path')
    parser.add_argument('--key', type=str, default='EnhancedPWLCM_SecretKey_2026Med1',
                        help='Encryption key (will be padded to 32 bytes)')
    parser.add_argument('--min-rounds', type=int, default=4,
                        help='Minimum encryption rounds')
    parser.add_argument('--max-rounds', type=int, default=12,
                        help='Maximum encryption rounds')
    parser.add_argument('--block-size', type=int, default=8,
                        help='Block size in bytes')
    
    args = parser.parse_args()
    
    # Prepare key (pad or truncate to 32 bytes)
    key_bytes = args.key.encode('utf-8')
    if len(key_bytes) < 32:
        key_bytes = key_bytes + b'0' * (32 - len(key_bytes))
    else:
        key_bytes = key_bytes[:32]
    
    print("="*80)
    print(" ENHANCED PWLCM MEDICAL IMAGE ENCRYPTION")
    print("="*80)
    print(f"\nInput image: {args.input}")
    print(f"Mode: {args.mode}")
    print(f"Adaptive rounds: {args.min_rounds} - {args.max_rounds}")
    print(f"Block size: {args.block_size} bytes")
    
    # Load image
    print("\n[1/4] Loading image...")
    img = Image.open(args.input).convert('L')
    img_array = np.array(img)
    print(f"  Image size: {img_array.shape}")
    
    # Create cipher
    print("\n[2/4] Initializing cipher...")
    cipher = EnhancedPWLCM(key_bytes, 
                           min_rounds=args.min_rounds,
                           max_rounds=args.max_rounds,
                           block_size=args.block_size)
    
    # Encrypt
    print("\n[3/4] Encrypting image...")
    encrypted = cipher.encrypt_image(img_array)
    
    # Get statistics
    stats = cipher.get_encryption_statistics()
    print(f"\n  Encryption Statistics:")
    print(f"    Total blocks: {stats['total_blocks']}")
    print(f"    Mean rounds: {stats['mean_rounds']:.2f}")
    print(f"    Round range: {stats['min_rounds']} - {stats['max_rounds']}")
    
    # Save encrypted image
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(encrypted).save(output_path)
    print(f"\n  Encrypted image saved to: {output_path}")
    
    if args.mode == 'full':
        print("\n[4/4] Performing security analysis...")
        
        # Calculate metrics
        metrics = SecurityMetrics.analyze_image_complete(img_array, encrypted)
        
        # Calculate NPCR/UACI
        modified_plain = img_array.copy()
        modified_plain[0, 0] ^= 1
        
        cipher_test = EnhancedPWLCM(key_bytes,
                                   min_rounds=args.min_rounds,
                                   max_rounds=args.max_rounds,
                                   block_size=args.block_size)
        encrypted_modified = cipher_test.encrypt_image(modified_plain)
        
        npcr = SecurityMetrics.calculate_npcr(encrypted, encrypted_modified)
        uaci = SecurityMetrics.calculate_uaci(encrypted, encrypted_modified)
        
        # Print metrics
        print(f"\n  Security Metrics:")
        print(f"    Plain Image Entropy: {metrics['plain']['entropy']:.4f}")
        print(f"    Encrypted Image Entropy: {metrics['encrypted']['entropy']:.4f} (ideal: 8.0)")
        print(f"\n    Correlation Coefficients:")
        print(f"      Plain  (H/V/D): {metrics['plain']['corr_h']:.4f}, "
              f"{metrics['plain']['corr_v']:.4f}, {metrics['plain']['corr_d']:.4f}")
        print(f"      Encrypted (H/V/D): {metrics['encrypted']['corr_h']:.4f}, "
              f"{metrics['encrypted']['corr_v']:.4f}, {metrics['encrypted']['corr_d']:.4f}")
        print(f"\n    Differential Analysis:")
        print(f"      NPCR: {npcr:.4f}% (ideal: >99.6%)")
        print(f"      UACI: {uaci:.4f}% (ideal: 33.46%)")
        print(f"\n    Chi-Square Test: "
              f"{'PASSED' if metrics['encrypted']['chi_square']['passed'] else 'FAILED'}")
        
        # Generate visualizations
        print(f"\n  Generating visualizations...")
        viz = PaperVisualizer(output_dir='results/analysis')
        viz.plot_image_comparison(img_array, encrypted)
        viz.plot_histograms(img_array, encrypted)
        viz.plot_correlation_all_directions(img_array, encrypted, name='analysis')
        
        print(f"\n  Visualizations saved to: results/analysis/")
    
    print("\n" + "="*80)
    print(" ENCRYPTION COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
