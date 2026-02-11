"""
Hardware Profiling Simulator for IoMT
Estimates performance metrics for target constrained devices (ARM Cortex-M4, ESP32, RPi 4)
based on algorithm complexity and Python execution profiling.
"""

import time
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.enhanced_cipher import EnhancedPWLCM as LHCMedEncryption
from chaos.hybrid_chaos import HybridChaos

def profile_hcg_performance(iterations=100000):
    """Profile Hybrid Chaos Generator core performance."""
    key = os.urandom(32)
    chaos = HybridChaos.from_key(key)
    
    start = time.time()
    for _ in range(iterations):
        chaos.iterate()
    duration = time.time() - start
    
    ops_per_sec = iterations / duration
    # 3 doubles (24 bytes) per iteration
    throughput_mbps = (ops_per_sec * 24 * 8) / 1e6
    
    return {
        'component': 'HCG Core',
        'iterations': iterations,
        'duration_sec': duration,
        'ops_per_sec': ops_per_sec,
        'throughput_mbps_python': throughput_mbps
    }

def profile_encryption_performance(size=(256, 256), rounds=10, samples=10):
    """Profile full image encryption performance."""
    key = os.urandom(32)
    cipher = LHCMedEncryption(key)
    image = np.random.randint(0, 256, size, dtype=np.uint8)
    
    durations = []
    for _ in range(samples):
        # Only measure encryption, not initialization
        start = time.time()
        cipher.encrypt_image(image)  # This uses adaptive rounds, but we can't force fixed easily without modifying class
        durations.append(time.time() - start)
        
    avg_duration = np.mean(durations)
    data_size_bits = size[0] * size[1] * 8
    throughput_mbps = (data_size_bits / avg_duration) / 1e6
    
    return {
        'component': f'Full Encryption {size}',
        'avg_duration_sec': avg_duration,
        'throughput_mbps_python': throughput_mbps
    }

def estimate_embedded_performance(python_metrics):
    """
    Estimate performance on embedded targets using scaled IPC and clock ratios.
    Base reference: Python on Desktop ~ 3 GHz.
    Factor: C implementation typically 50-100x faster than Python.
    """
    
    # Python Throughput (Mbps)
    py_tput = python_metrics['throughput_mbps_python']
    
    # Scaling factors (Conservative C implementation vs Python)
    c_speedup = 50.0 
    
    # Target Hardware Specs
    targets = {
        'Raspberry Pi 4 (C++)': {'clock_mhz': 1500, 'ipc_factor': 1.0},
        'ESP32-S3 (C)': {'clock_mhz': 240, 'ipc_factor': 0.8},
        'ARM Cortex-M4 (C)': {'clock_mhz': 80, 'ipc_factor': 0.6}
    }
    
    # Assume Desktop is ~3000 MHz effective
    desktop_clock = 3000.0
    
    estimates = {}
    for name, specs in targets.items():
        # Scale by clock and IPC
        hw_factor = (specs['clock_mhz'] / desktop_clock) * specs['ipc_factor']
        
        # Combined estimator: Python Tput * C_Speedup * HW_Factor
        est_tput = py_tput * c_speedup * hw_factor
        
        # Energy Estimation (J/MB)
        # Power estimates (Active): RPi4 ~ 3W, ESP32 ~ 0.5W, M4 ~ 0.1W
        power_w = 0.0
        if 'Pi 4' in name: power_w = 3.0
        elif 'ESP32' in name: power_w = 0.5
        elif 'M4' in name: power_w = 0.1
        
        # Energy = Power * Time = Power * (Size / Throughput)
        # Energy per MB = Power / (Throughput_MBps)
        # Throughput_MBps = est_tput / 8
        if est_tput > 0:
            energy_per_mb_j = power_w / (est_tput / 8.0)
            energy_per_kb_uj = energy_per_mb_j * 1000 / 1024
        else:
            energy_per_kb_uj = 0
            
        estimates[name] = {
            'throughput_mbps': est_tput,
            'energy_uj_per_kb': energy_per_kb_uj,
            'cycles_per_byte': (specs['clock_mhz']*1e6) / (est_tput*1e6/8)
        }
        
    return estimates

if __name__ == "__main__":
    print("=== Hardware Performance Profiling (Simulated) ===\n")
    
    # Run profiles
    hcg_res = profile_hcg_performance()
    enc_res = profile_encryption_performance((256, 256))
    enc_res_512 = profile_encryption_performance((512, 512))
    
    print(f"Base Python Performance (Desktop):")
    print(f"  HCG Core: {hcg_res['throughput_mbps_python']:.2f} Mbps")
    print(f"  Encryption (256x256): {enc_res['throughput_mbps_python']:.2f} Mbps")
    print(f"  Encryption (512x512): {enc_res_512['throughput_mbps_python']:.2f} Mbps")
    
    # Estimate Embedded
    estimates = estimate_embedded_performance(enc_res_512)
    
    print("\n=== Estimated Embedded Performance (optimized C implementation) ===")
    print(f"{'Platform':<20} | {'Throughput (Mbps)':<18} | {'Cycles/Byte':<12} | {'Energy (uJ/KB)':<15}")
    print("-" * 75)
    
    for name, metrics in estimates.items():
        print(f"{name:<20} | {metrics['throughput_mbps']:<18.2f} | {metrics['cycles_per_byte']:<12.1f} | {metrics['energy_uj_per_kb']:<15.2f}")
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, 'hardware_estimates.txt'), 'w') as f:
        f.write("Estimated IoMT Performance Profile\n")
        f.write("="*40 + "\n\n")
        for name, metrics in estimates.items():
            f.write(f"Platform: {name}\n")
            f.write(f"  Throughput: {metrics['throughput_mbps']:.2f} Mbps\n")
            f.write(f"  Cycles/Byte: {metrics['cycles_per_byte']:.1f}\n")
            f.write(f"  Energy Efficiency: {metrics['energy_uj_per_kb']:.2f} uJ/KB\n\n")
            
    print(f"\nResults saved to results/hardware_estimates.txt")
