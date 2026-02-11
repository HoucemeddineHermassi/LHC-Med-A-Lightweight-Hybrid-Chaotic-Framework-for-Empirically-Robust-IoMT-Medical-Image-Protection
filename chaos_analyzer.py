"""
Digital Chaos Behavior Analyzer
Quantifies cycle length distribution and state collision probabilities to address finite-precision concerns.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import time

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chaos.hybrid_chaos import HybridChaos

def analyze_digital_chaos(iterations=1000000):
    """
    Empirically analyze cycle length and collision probability in 64-bit float chaos.
    """
    print(f"--- Analyzing Digital Chaos Behavior ({iterations} iterations) ---")
    
    # Use a random key for initialization
    key = os.urandom(32)
    chaos = HybridChaos.from_key(key)
    
    states = []
    collisions = 0
    start_time = time.time()
    
    # To save memory and time, we'll hash the state or use a subset
    # Actually for 10^6 we can store floats as a set
    visited = set()
    
    print("Running iterations...")
    for i in range(iterations):
        x, y, z = chaos.iterate()
        state = (round(x, 15), round(y, 15)) # 64-bit precision practical limit
        
        if state in visited:
            collisions += 1
            # In a real cycle length analysis we'd stop here, 
            # but we want to see frequency of collisions over time
        else:
            visited.add(state)
        
        if i > 0 and i % 250000 == 0:
            print(f"  Processed {i} iterations...")

    end_time = time.time()
    
    collision_prob = collisions / iterations
    unique_ratio = len(visited) / iterations
    
    print(f"\nResults:")
    print(f"  Total Iterations: {iterations}")
    print(f"  Unique States found: {len(visited)}")
    print(f"  Collision Count: {collisions}")
    print(f"  Empirical Collision Probability: {collision_prob:.8f}")
    print(f"  State space coverage ratio: {unique_ratio:.6f}")
    print(f"  Analysis Time: {end_time - start_time:.2f}s")
    
    if collisions == 0:
        print("  Interpretation: No cycles detected in this window. Cycle length >> 10^6.")
    else:
        print(f"  Interpretation: Finite precision effects detected. Cycle length approx {iterations/collisions:.0f} steps.")

    # Save summary to a text file for LaTeX integration
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, 'chaos_behavior.txt'), 'w') as f:
        f.write(f"Iterations: {iterations}\n")
        f.write(f"Unique States: {len(visited)}\n")
        f.write(f"Collision Probability: {collision_prob}\n")
        f.write(f"Coverage: {unique_ratio}\n")

if __name__ == "__main__":
    # Run with 10 million iterations for rigorous statistical validation  
    analyze_digital_chaos(10000000)
