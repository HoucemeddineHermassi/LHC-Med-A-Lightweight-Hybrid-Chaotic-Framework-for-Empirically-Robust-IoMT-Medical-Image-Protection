"""
State/Keystream Recovery Attack Simulation
Attempts to reconstruct chaotic internal state from partial keystream leakage.
"""

import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chaos.hybrid_chaos import HybridChaos

def simulate_state_recovery_attack(keystream_length: int = 1000, 
                                    samples: int = 100) -> dict:
    """
    Simulate state recovery attack from partial keystream observation.
    
    Attack model:
    - Adversary observes N consecutive keystream values
    - Attempts to recover internal state (x_n, y_n) via:
      1. Statistical correlation analysis
      2. Brute-force state search in observed window
    
    Args:
        keystream_length: Number of observed keystream values
        samples: Number of attack attempts
        
    Returns:
        Attack statistics
    """
    print(f"=== State Recovery Attack Simulation ===")
    print(f"Keystream length: {keystream_length}")
    print(f"Attack samples: {samples}")
    
    successful_recoveries = 0
    partial_recoveries = 0
    
    for trial in range(samples):
        # Generate ground truth keystream
        key = os.urandom(32)
        chaos = HybridChaos.from_key(key)
        
        # Store true internal states
        true_states = []
        keystream = []
        
        for i in range(keystream_length):
            x, y, z = chaos.iterate()
            true_states.append((x, y))
            keystream.append(z)
        
        # Attack: attempt state recovery from keystream
        # Using statistical analysis of keystream values
        
        # Method 1: Check if keystream reveals state structure
        # The keystream z = x XOR y (digitized)
        # Try to find correlation between consecutive keystream values
        
        keystream_diffs = np.diff(keystream)
        autocorr = np.correlate(keystream_diffs[:100], keystream_diffs[:100], mode='full')
        max_autocorr = np.max(autocorr[len(autocorr)//2+1:len(autocorr)//2+10])
        
        # If high autocorrelation, might indicate recoverable structure
        if max_autocorr > 50:  # Threshold for "significant" correlation
            partial_recoveries += 1
        
        # Method 2: Brute force in small window
        # Try random initial states and check if they produce matching keystream
        for _ in range(100):  # Limited brute force attempts
            guess_x = np.random.random()
            guess_y = np.random.random()
            
            # Check first 10 keystream values
            test_chaos = HybridChaos(0.456, 0.89, guess_x, guess_y)
            match_count = 0
            for i in range(10):
                _, _, test_z = test_chaos.iterate()
                if abs(test_z - keystream[i]) < 1e-10:
                    match_count += 1
            
            if match_count >= 8:  # Near-complete match
                successful_recoveries += 1
                break
        
        if trial % 20 == 0:
            print(f"  Completed {trial}/{samples} trials...")
    
    success_rate = successful_recoveries / samples * 100
    partial_rate = partial_recoveries / samples * 100
    
    results = {
        'keystream_length': keystream_length,
        'samples': samples,
        'successful_recoveries': successful_recoveries,
        'partial_recoveries': partial_recoveries,
        'success_rate': success_rate,
        'partial_rate': partial_rate,
        'interpretation': 'Resistant' if success_rate < 1 else 'Vulnerable'
    }
    
    print(f"\n=== Results ===")
    print(f"Full recovery success: {successful_recoveries}/{samples} ({success_rate:.2f}%)")
    print(f"Partial structure detected: {partial_recoveries}/{samples} ({partial_rate:.2f}%)")
    print(f"Interpretation: {results['interpretation']}")
    
    return results


def simulate_keystream_correlation_attack(length: int = 10000) -> dict:
    """
    Test keystream for correlation patterns that might aid cryptanalysis.
    """
    print(f"\n=== Keystream Correlation Analysis ===")
    
    key = os.urandom(32)
    chaos = HybridChaos.from_key(key)
    
    keystream = []
    for _ in range(length):
        _, _, z = chaos.iterate()
        keystream.append(z)
    
    keystream = np.array(keystream)
    
    # Compute autocorrelation at various lags
    autocorr = []
    for lag in range(1, 51):
        corr = np.corrcoef(keystream[:-lag], keystream[lag:])[0, 1]
        autocorr.append(abs(corr))
    
    max_corr = max(autocorr)
    avg_corr = np.mean(autocorr)
    
    # Ideal: correlation should be near 0 for all lags
    results = {
        'length': length,
        'max_autocorrelation': max_corr,
        'avg_autocorrelation': avg_corr,
        'lag_with_max': autocorr.index(max_corr) + 1,
        'cryptographic_quality': 'Good' if max_corr < 0.05 else 'Suspicious'
    }
    
    print(f"Max autocorrelation: {max_corr:.6f} (at lag {results['lag_with_max']})")
    print(f"Average autocorrelation: {avg_corr:.6f}")
    print(f"Cryptographic quality: {results['cryptographic_quality']}")
    
    return results


if __name__ == "__main__":
    # Run state recovery attack simulation
    recovery_results = simulate_state_recovery_attack(1000, 100)
    
    # Run keystream correlation analysis
    correlation_results = simulate_keystream_correlation_attack(10000)
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    with open(os.path.join(results_dir, 'state_recovery_results.txt'), 'w') as f:
        f.write("State Recovery Attack Results\n")
        f.write("="*40 + "\n")
        for k, v in recovery_results.items():
            f.write(f"{k}: {v}\n")
        f.write("\nKeystream Correlation Results\n")
        f.write("="*40 + "\n")
        for k, v in correlation_results.items():
            f.write(f"{k}: {v}\n")
    
    print(f"\nResults saved to {results_dir}/state_recovery_results.txt")
