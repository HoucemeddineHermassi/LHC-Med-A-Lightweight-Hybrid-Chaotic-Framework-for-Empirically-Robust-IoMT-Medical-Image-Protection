"""
Extended Experimental Comparison Benchmark
==========================================

Runs benchmarks on:
- SIMON-64/128, SPECK-64/128, PRESENT-80, LEA-128 (Lightweight Block Ciphers)
- Hua 2023 (2D Logistic-Sine), Yuan 2024 (4D Hyperchaotic) (Chaos-Based)
- LHC-Med (Our Proposal)

Metrics:
- NPCR, UACI
- Correlation Coefficients (H/V/D)
- Execution Time (ms)
- Energy Consumption (mJ)
- Memory Footprint (KB)
"""

import numpy as np
import cv2
import os
import sys
import time
import tracemalloc
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass

# Import our ciphers
from lightweight_ciphers import (
    Simon64_128, Speck64_128, Present80, Lea128,
    HuaLogisticSine2023, Yuan4DHyperchaotic2024,
    encrypt_image_with_cipher, measure_memory_footprint,
    measure_execution_time, estimate_energy_consumption
)

# Import LHC-Med
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crypto import EnhancedPWLCM as HybridChaoticEncryption


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    name: str
    npcr: float
    uaci: float
    corr_h: float
    corr_v: float
    corr_d: float
    exec_time_ms: float
    energy_mj: float
    memory_kb: float
    entropy: float


def calculate_npcr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate Number of Pixels Change Rate."""
    diff = np.sum(img1 != img2)
    total = img1.size
    return (diff / total) * 100


def calculate_uaci(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate Unified Average Changing Intensity."""
    diff = np.abs(img1.astype(np.float64) - img2.astype(np.float64))
    return np.mean(diff) / 255 * 100


def calculate_correlation(img: np.ndarray, direction: str = 'horizontal', samples: int = 5000) -> float:
    """Calculate correlation coefficient for adjacent pixels."""
    h, w = img.shape
    pairs = []
    
    np.random.seed(42)
    for _ in range(samples):
        x, y = np.random.randint(1, h-1), np.random.randint(1, w-1)
        
        if direction == 'horizontal':
            pairs.append((img[x, y], img[x, y+1] if y+1 < w else img[x, y-1]))
        elif direction == 'vertical':
            pairs.append((img[x, y], img[x+1, y] if x+1 < h else img[x-1, y]))
        else:  # diagonal
            pairs.append((img[x, y], img[x+1, y+1] if x+1 < h and y+1 < w else img[x-1, y-1]))
    
    pairs = np.array(pairs)
    if len(pairs) == 0:
        return 0.0
    
    x_vals, y_vals = pairs[:, 0].astype(float), pairs[:, 1].astype(float)
    
    # Pearson correlation
    mean_x, mean_y = np.mean(x_vals), np.mean(y_vals)
    numerator = np.sum((x_vals - mean_x) * (y_vals - mean_y))
    denominator = np.sqrt(np.sum((x_vals - mean_x)**2) * np.sum((y_vals - mean_y)**2))
    
    if denominator == 0:
        return 0.0
    
    return abs(numerator / denominator)


def calculate_entropy(img: np.ndarray) -> float:
    """Calculate Shannon entropy."""
    hist, _ = np.histogram(img.flatten(), bins=256, range=(0, 256))
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))


def run_benchmark_block_cipher(cipher_class, cipher_name: str, key: bytes, 
                                image: np.ndarray, block_size: int = 8) -> BenchmarkResult:
    """Run full benchmark suite for a block cipher."""
    print(f"  Benchmarking {cipher_name}...")
    
    # Memory footprint
    memory_kb = measure_memory_footprint(cipher_class, key)
    
    # Initialize cipher
    cipher = cipher_class(key)
    
    # Create encryption function
    def encrypt_func(img):
        return encrypt_image_with_cipher(cipher, img, block_size)
    
    # Execution time
    exec_time_ms = measure_execution_time(encrypt_func, image, iterations=5)
    
    # Energy estimation
    energy_mj = estimate_energy_consumption(exec_time_ms)
    
    # Encrypt images for NPCR/UACI
    encrypted1 = encrypt_func(image)
    
    # Modify one pixel for differential analysis
    image_mod = image.copy()
    image_mod[0, 0] = (int(image_mod[0, 0]) + 1) % 256
    encrypted2 = encrypt_func(image_mod)
    
    # Calculate metrics
    npcr = calculate_npcr(encrypted1, encrypted2)
    uaci = calculate_uaci(encrypted1, encrypted2)
    corr_h = calculate_correlation(encrypted1, 'horizontal')
    corr_v = calculate_correlation(encrypted1, 'vertical')
    corr_d = calculate_correlation(encrypted1, 'diagonal')
    entropy = calculate_entropy(encrypted1)
    
    return BenchmarkResult(
        name=cipher_name,
        npcr=npcr,
        uaci=uaci,
        corr_h=corr_h,
        corr_v=corr_v,
        corr_d=corr_d,
        exec_time_ms=exec_time_ms,
        energy_mj=energy_mj,
        memory_kb=memory_kb,
        entropy=entropy
    )


def run_benchmark_chaos_scheme(scheme_class, scheme_name: str, key: bytes,
                                image: np.ndarray) -> BenchmarkResult:
    """Run full benchmark suite for a chaos-based scheme."""
    print(f"  Benchmarking {scheme_name}...")
    
    # Memory footprint
    memory_kb = measure_memory_footprint(scheme_class, key)
    
    # Initialize scheme
    scheme = scheme_class(key)
    
    # Create encryption function
    def encrypt_func(img):
        return scheme.encrypt_image(img)
    
    # Execution time
    exec_time_ms = measure_execution_time(encrypt_func, image, iterations=5)
    
    # Energy estimation
    energy_mj = estimate_energy_consumption(exec_time_ms)
    
    # Encrypt images for NPCR/UACI
    encrypted1 = encrypt_func(image)
    
    # Modify one pixel
    image_mod = image.copy()
    image_mod[0, 0] = (int(image_mod[0, 0]) + 1) % 256
    encrypted2 = encrypt_func(image_mod)
    
    # Calculate metrics
    npcr = calculate_npcr(encrypted1, encrypted2)
    uaci = calculate_uaci(encrypted1, encrypted2)
    corr_h = calculate_correlation(encrypted1, 'horizontal')
    corr_v = calculate_correlation(encrypted1, 'vertical')
    corr_d = calculate_correlation(encrypted1, 'diagonal')
    entropy = calculate_entropy(encrypted1)
    
    return BenchmarkResult(
        name=scheme_name,
        npcr=npcr,
        uaci=uaci,
        corr_h=corr_h,
        corr_v=corr_v,
        corr_d=corr_d,
        exec_time_ms=exec_time_ms,
        energy_mj=energy_mj,
        memory_kb=memory_kb,
        entropy=entropy
    )


def run_benchmark_lhc_med(image: np.ndarray, key: bytes) -> BenchmarkResult:
    """Run benchmark for LHC-Med."""
    print(f"  Benchmarking LHC-Med...")
    
    # Memory footprint
    tracemalloc.start()
    encryptor = HybridChaoticEncryption(master_key=key, min_rounds=4, max_rounds=12)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_kb = peak / 1024
    
    # Encryption function - returns (encrypted, iv) tuple
    def encrypt_func(img):
        encrypted, _ = encryptor.encrypt_image(img)
        return encrypted
    
    # Execution time
    times = []
    for _ in range(5):
        start = time.perf_counter()
        encrypted1, _ = encryptor.encrypt_image(image)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    exec_time_ms = np.mean(times)
    
    # Energy estimation
    energy_mj = estimate_energy_consumption(exec_time_ms)
    
    # Encrypt for differential analysis
    encrypted1, _ = encryptor.encrypt_image(image)
    
    image_mod = image.copy()
    image_mod[0, 0] = (int(image_mod[0, 0]) + 1) % 256
    encrypted2, _ = encryptor.encrypt_image(image_mod)
    
    # Calculate metrics
    npcr = calculate_npcr(encrypted1, encrypted2)
    uaci = calculate_uaci(encrypted1, encrypted2)
    corr_h = calculate_correlation(encrypted1, 'horizontal')
    corr_v = calculate_correlation(encrypted1, 'vertical')
    corr_d = calculate_correlation(encrypted1, 'diagonal')
    entropy = calculate_entropy(encrypted1)
    
    return BenchmarkResult(
        name="LHC-Med",
        npcr=npcr,
        uaci=uaci,
        corr_h=corr_h,
        corr_v=corr_v,
        corr_d=corr_d,
        exec_time_ms=exec_time_ms,
        energy_mj=energy_mj,
        memory_kb=memory_kb,
        entropy=entropy
    )


def generate_comparison_table_latex(results: List[BenchmarkResult], output_path: str):
    """Generate LaTeX table from benchmark results."""
    
    latex = r"""\begin{table}[ht]
\caption{Extended Experimental Comparison: LHC-Med vs. Lightweight Block Ciphers and Recent Chaos-Based Schemes}\label{tab:extended_comparison}
\centering
\scriptsize
\begin{tabular}{lccccccccc}
\toprule
\textbf{Scheme} & \textbf{NPCR(\%)} & \textbf{UACI(\%)} & \textbf{Corr(H)} & \textbf{Corr(V)} & \textbf{Corr(D)} & \textbf{Time(ms)} & \textbf{Energy(mJ)} & \textbf{RAM(KB)} & \textbf{Entropy} \\
\midrule
"""
    
    for r in results:
        # Bold LHC-Med row
        bold = r.name == "LHC-Med"
        name = f"\\textbf{{{r.name}}}" if bold else r.name
        
        row = f"{name} & {r.npcr:.2f} & {r.uaci:.2f} & {r.corr_h:.4f} & {r.corr_v:.4f} & {r.corr_d:.4f} & {r.exec_time_ms:.2f} & {r.energy_mj:.2f} & {r.memory_kb:.1f} & {r.entropy:.4f} \\\\\n"
        
        if bold:
            row = row.replace(f"{r.npcr:.2f}", f"\\textbf{{{r.npcr:.2f}}}")
            row = row.replace(f"{r.uaci:.2f}", f"\\textbf{{{r.uaci:.2f}}}")
            row = row.replace(f"{r.entropy:.4f} \\\\", f"\\textbf{{{r.entropy:.4f}}} \\\\")
        
        latex += row
    
    latex += r"""\botrule
\end{tabular}
\end{table}
"""
    
    with open(output_path, 'w') as f:
        f.write(latex)
    
    print(f"[+] LaTeX table saved to {output_path}")


def generate_radar_chart(results: List[BenchmarkResult], output_path: str):
    """Generate radar chart comparing all schemes."""
    
    # Normalize metrics for radar chart (higher is better for all)
    metrics = ['NPCR', 'UACI', '1-Corr(H)', 'Entropy', '1/Time', '1/Energy']
    
    # Extract and normalize values
    data = []
    for r in results:
        values = [
            r.npcr / 100,  # Normalize to 0-1
            r.uaci / 33.46,  # Normalize to ideal
            1 - r.corr_h,  # Lower is better, so invert
            r.entropy / 8,  # Normalize to max entropy
            1 / (r.exec_time_ms + 0.1),  # Invert (lower is better)
            1 / (r.energy_mj + 0.1)  # Invert
        ]
        # Normalize inverse metrics to 0-1 range
        data.append(values)
    
    # Normalize time and energy across all schemes
    max_inv_time = max(d[4] for d in data)
    max_inv_energy = max(d[5] for d in data)
    for d in data:
        d[4] /= max_inv_time
        d[5] /= max_inv_energy
    
    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    
    for i, r in enumerate(results):
        values = data[i] + data[i][:1]  # Close the polygon
        ax.plot(angles, values, 'o-', linewidth=2, label=r.name, color=colors[i % len(colors)])
        ax.fill(angles, values, alpha=0.1, color=colors[i % len(colors)])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, size=12)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.set_title('Extended Comparison: Normalized Performance Metrics', size=14, y=1.08)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[+] Radar chart saved to {output_path}")


def main():
    """Run complete benchmark suite."""
    print("=" * 60)
    print("Extended Experimental Comparison Benchmark")
    print("=" * 60)
    
    # Load test image
    image_path = "Viral Pneumonia-10.png"
    if not os.path.exists(image_path):
        print(f"[!] Test image not found: {image_path}")
        print("    Creating synthetic test image...")
        image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
    else:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        else:
            # Resize if needed
            # Resize to match manuscript standard (299x299)
            image = cv2.resize(image, (299, 299))
    
    print(f"[+] Test image shape: {image.shape}")
    
    # Keys
    key_128 = b'\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3c'
    key_80 = b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99'
    key_256 = key_128 + key_128
    
    results = []
    
    print("\n[Phase 1] Benchmarking Lightweight Block Ciphers...")
    
    # SIMON-64/128
    results.append(run_benchmark_block_cipher(Simon64_128, "SIMON-64/128", key_128, image, 8))
    
    # SPECK-64/128
    results.append(run_benchmark_block_cipher(Speck64_128, "SPECK-64/128", key_128, image, 8))
    
    # PRESENT-80
    results.append(run_benchmark_block_cipher(Present80, "PRESENT-80", key_80, image, 8))
    
    # LEA-128
    results.append(run_benchmark_block_cipher(Lea128, "LEA-128", key_128, image, 16))
    
    print("\n[Phase 2] Benchmarking Chaos-Based Schemes (2023-2024)...")
    
    # Hua 2023
    results.append(run_benchmark_chaos_scheme(HuaLogisticSine2023, "Hua 2023", key_256, image))
    
    # Yuan 2024
    results.append(run_benchmark_chaos_scheme(Yuan4DHyperchaotic2024, "Yuan 2024", key_256, image))
    
    print("\n[Phase 3] Benchmarking LHC-Med...")
    
    # LHC-Med
    results.append(run_benchmark_lhc_med(image, key_256))
    
    # Print results summary
    print("\n" + "=" * 100)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 100)
    print(f"{'Scheme':<15} {'NPCR(%)':<10} {'UACI(%)':<10} {'Corr(H)':<10} {'Corr(V)':<10} {'Corr(D)':<10} {'Time(ms)':<12} {'Energy(mJ)':<12} {'RAM(KB)':<10} {'Entropy':<10}")
    print("-" * 100)
    
    for r in results:
        print(f"{r.name:<15} {r.npcr:<10.2f} {r.uaci:<10.2f} {r.corr_h:<10.4f} {r.corr_v:<10.4f} {r.corr_d:<10.4f} {r.exec_time_ms:<12.2f} {r.energy_mj:<12.2f} {r.memory_kb:<10.1f} {r.entropy:<10.4f}")
    
    print("=" * 100)
    
    # Generate outputs
    output_dir = "../paper"
    os.makedirs(output_dir, exist_ok=True)
    
    generate_comparison_table_latex(results, os.path.join(output_dir, "extended_comparison.tex"))
    generate_radar_chart(results, os.path.join(output_dir, "extended_comparison_radar.png"))
    
    print("\n[+] Benchmark complete!")
    
    return results


if __name__ == "__main__":
    results = main()
