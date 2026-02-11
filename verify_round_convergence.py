import numpy as np
import sys
import os

# Add project root and enhanced_encryption to path
root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)
sys.path.append(os.path.join(root, "enhanced_encryption"))

from enhanced_encryption.crypto.enhanced_cipher import EnhancedPWLCM # Note: The class name might be different in the actual file, let me check
from enhanced_encryption.chaos.hybrid_chaos import HybridChaos

def calculate_npcr(c1, c2):
    return np.mean(c1 != c2) * 100

def calculate_uaci(c1, c2):
    return np.mean(np.abs(c1.astype(float) - c2.astype(float))) / 255 * 100

def test_convergence():
    # Setup
    p, mu, x0, y0 = 0.4, 0.9, 0.3, 0.7
    chaos = HybridChaos(p, mu, x0, y0)
    
    # Create test image (8x8 block)
    block1 = np.random.randint(0, 256, (8, 8), dtype=np.uint8)
    block2 = block1.copy()
    block2[0, 0] ^= 1 # 1-bit change
    
    from enhanced_encryption.crypto.permutation import ChaoticPermutation
    from enhanced_encryption.crypto.sbox_generator import ChaoticSBox
    
    sbox_gen = ChaoticSBox(chaos)
    perm_gen = ChaoticPermutation(chaos)
    
    print("Round | NPCR (%) | UACI (%)")
    print("-" * 30)
    
    b1 = block1.flatten()
    b2 = block2.flatten()
    
    for r in range(1, 11):
        # Apply one round
        sbox = sbox_gen.generate_sbox()
        # Key mixing
        k = np.random.randint(0, 256, len(b1), dtype=np.uint8)
        
        # S-box
        b1 = sbox_gen.substitute_block(b1, sbox)
        b2 = sbox_gen.substitute_block(b2, sbox)
        
        # Permutation
        b1 = perm_gen.permute_bits(b1)
        b2 = perm_gen.permute_bits(b2)
        
        # XOR
        b1 ^= k
        b2 ^= k
        
        npcr = calculate_npcr(b1, b2)
        uaci = calculate_uaci(b1, b2)
        print(f"{r:5d} | {npcr:8.2f} | {uaci:8.2f}")

if __name__ == "__main__":
    test_convergence()
