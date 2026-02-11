"""
Generate All Paper Materials
Creates all figures, tables, and metrics for publication
"""

import numpy as np
from PIL import Image
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from chaos import SkewTentMap, LogisticSineMap, HybridChaos
from crypto import EnhancedPWLCM
from metrics import SecurityMetrics
from visualization import PaperVisualizer


def generate_all_paper_materials(medical_images_dir='.'):
    """
    Generate all materials needed for paper publication
    
    Args:
        medical_images_dir: Directory containing medical images
    """
    print("="*80)
    print(" LHC-Med: GENERATING ALL PAPER MATERIALS")
    print("="*80)
    
    # Create visualizer
    viz = PaperVisualizer(output_dir='results/paper_materials')
    
    # -------------------------------------------------------------------------
    # 1. CHAOTIC MAP ANALYSIS
    # -------------------------------------------------------------------------
    print("\n[1/8] Generating chaotic map analysis figures...")
    
    # Bifurcation diagrams
    p_range = np.linspace(0.01, 0.99, 1000)
    viz.plot_chaos_bifurcation(SkewTentMap, 'p', p_range, iterations=1000)
    
    mu_range = np.linspace(0.01, 0.99, 1000)
    viz.plot_chaos_bifurcation(LogisticSineMap, 'mu', mu_range, iterations=1000)
    
    # Lyapunov exponents
    viz.plot_lyapunov_exponent(SkewTentMap, 'p', p_range)
    viz.plot_lyapunov_exponent(LogisticSineMap, 'mu', mu_range)
    
    print("  [OK] Chaotic map analysis complete")
    
    # -------------------------------------------------------------------------
    # 2. TEST ON MEDICAL IMAGES
    # -------------------------------------------------------------------------
    print("\n[2/8] Encrypting medical images...")
    
    # Define master key
    master_key = b'EnhancedPWLCM_SecretKey_2026' + b'Med1'  # 32 bytes = 256 bits
    
    # Create cipher
    cipher = EnhancedPWLCM(master_key, min_rounds=4, max_rounds=12, block_size=8)
    
    # Find medical images
    medical_images_data = []
    image_names = []
    
    # Check root directory and visualization directory
    search_dirs = [Path(medical_images_dir), Path(medical_images_dir) / 'visualization']
    
    found_paths = []
    for d in search_dirs:
        if d.exists():
            # Include all .png and .jpg images
            found_paths.extend(list(d.glob('*.png')))
            found_paths.extend(list(d.glob('*.jpg')))
    
    # Filter to avoid duplicates if same image is in multiple lists
    unique_paths = list(set(found_paths))
    
    # Sort for consistent output
    unique_paths.sort(key=lambda x: x.name)
    
    if not unique_paths:
        print("  [WARNING] No images found. Creating test images...")
        for i in range(3):
            img = np.random.randint(50, 200, size=(512, 512), dtype=np.uint8)
            y, x = np.ogrid[:512, :512]
            mask = (x - 256)**2 + (y - 256)**2 < 200**2
            img[mask] = (img[mask] * 1.2).clip(0, 255).astype(np.uint8)
            medical_images_data.append(img)
            image_names.append(f'Synthetic_Medical_{i+1}')
    else:
        for img_path in unique_paths:
            try:
                img = Image.open(img_path).convert('L')
                img_array = np.array(img)
                medical_images_data.append(img_array)
                image_names.append(img_path.name)
                print(f"  [Found] {img_path.name}")
            except Exception as e:
                print(f"  [Error] Could not load {img_path.name}: {e}")
    
    print(f"  Processing total of {len(medical_images_data)} images...")
    
    # Store results
    results_all = []
    
    for idx, (img_array, img_name) in enumerate(zip(medical_images_data, image_names)):
        print(f"\n  Processing: {img_name}")
        
        # Resize if necessary (for faster processing in testing)
        if img_array.shape[0] > 512 or img_array.shape[1] > 512:
            pil_img = Image.fromarray(img_array)
            pil_img = pil_img.resize((512, 512), Image.Resampling.LANCZOS)
            img_array = np.array(pil_img)
        
        # Encrypt
        encrypted = cipher.encrypt_image(img_array)
        
        # Get encryption statistics
        stats = cipher.get_encryption_statistics()
        
        # Calculate security metrics
        metrics = SecurityMetrics.analyze_image_complete(img_array, encrypted)
        
        # Calculate NPCR/UACI (differential analysis)
        modified_plain = img_array.copy()
        modified_plain[0, 0] ^= 1
        
        cipher_test = EnhancedPWLCM(master_key, min_rounds=4, max_rounds=12, block_size=8)
        encrypted_modified = cipher_test.encrypt_image(modified_plain)
        
        npcr = SecurityMetrics.calculate_npcr(encrypted, encrypted_modified)
        uaci = SecurityMetrics.calculate_uaci(encrypted, encrypted_modified)
        
        metrics['differential'] = {'npcr': npcr, 'uaci': uaci}
        metrics['encryption_stats'] = stats
        
        results_all.append({
            'name': img_name,
            'plain': img_array,
            'encrypted': encrypted,
            'metrics': metrics
        })
        
        print(f"    Entropy: {metrics['encrypted']['entropy']:.4f}")
        print(f"    NPCR: {npcr:.4f}%")
        print(f"    UACI: {uaci:.4f}%")
        print(f"    Avg rounds: {stats['mean_rounds']:.2f}")
    
    print("\n  [OK] Medical image encryption complete")
    
    # -------------------------------------------------------------------------
    # 3. GENERATE IMAGE VISUALIZATIONS
    # -------------------------------------------------------------------------
    print("\n[3/8] Generating image comparison figures...")
    
    for result in results_all:
        viz.plot_image_comparison(
            result['plain'], 
            result['encrypted'], 
            title_suffix=f"_{result['name']}"
        )
    
    print("  [OK] Image comparisons complete")
    
    # -------------------------------------------------------------------------
    # 4. GENERATE HISTOGRAMS
    # -------------------------------------------------------------------------
    print("\n[4/8] Generating histogram figures...")
    
    for result in results_all:
        viz.plot_histograms(
            result['plain'],
            result['encrypted'],
            title_suffix=f"_{result['name']}"
        )
    
    print("  [OK] Histograms complete")
    
    # -------------------------------------------------------------------------
    # 5. GENERATE CORRELATION PLOTS
    # -------------------------------------------------------------------------
    print("\n[5/8] Generating correlation plots...")
    
    for result in results_all:
        viz.plot_correlation_all_directions(
            result['plain'],
            result['encrypted'],
            name=result['name']
        )
    
    print("  [OK] Correlation plots complete")
    
    # -------------------------------------------------------------------------
    # 6. CREATE METRICS TABLES
    # -------------------------------------------------------------------------
    print("\n[6/8] Creating metrics tables...")
    
    from tabulate import tabulate
    
    # Comprehensive metrics table for all images
    table_data = []
    for result in results_all:
        m = result['metrics']
        row = [
            result['name'],
            f"{m['plain']['entropy']:.4f}",
            f"{m['encrypted']['entropy']:.4f}",
            f"{m['plain']['corr_h']:.4f}",
            f"{m['encrypted']['corr_h']:.4f}",
            f"{m['plain']['corr_v']:.4f}",
            f"{m['encrypted']['corr_v']:.4f}",
            f"{m['plain']['corr_d']:.4f}",
            f"{m['encrypted']['corr_d']:.4f}",
            f"{m['differential']['npcr']:.4f}",
            f"{m['differential']['uaci']:.4f}",
        ]
        table_data.append(row)
    
    headers = [
        'Image', 
        'H (Plain)', 'H (Enc)', 
        'Corr-H (P)', 'Corr-H (E)',
        'Corr-V (P)', 'Corr-V (E)',
        'Corr-D (P)', 'Corr-D (E)',
        'NPCR (%)', 'UACI (%)'
    ]
    
    table = tabulate(table_data, headers=headers, tablefmt='grid')
    
    with open(viz.output_dir / 'comprehensive_metrics_table.txt', 'w') as f:
        f.write("COMPREHENSIVE SECURITY METRICS\n")
        f.write("="*120 + "\n\n")
        f.write(table)
        f.write("\n\n")
        
        # Add LaTeX version
        latex_table = tabulate(table_data, headers=headers, tablefmt='latex')
        f.write("\nLaTeX Version:\n")
        f.write(latex_table)
    
    print("  [OK] Metrics table created")
    
    # -------------------------------------------------------------------------
    # 7. CREATE ENCRYPTION PERFORMANCE TABLE
    # -------------------------------------------------------------------------
    print("\n[7/8] Creating performance analysis table...")
    
    perf_data = []
    for result in results_all:
        stats = result['metrics']['encryption_stats']
        row = [
            result['name'],
            stats['total_blocks'],
            f"{stats['mean_rounds']:.2f}",
            stats['min_rounds'],
            stats['max_rounds'],
            f"{stats['std_rounds']:.2f}"
        ]
        perf_data.append(row)
    
    perf_headers = ['Image', 'Total Blocks', 'Mean Rounds', 'Min Rounds', 'Max Rounds', 'Std Rounds']
    perf_table = tabulate(perf_data, headers=perf_headers, tablefmt='grid')
    
    with open(viz.output_dir / 'performance_table.txt', 'w') as f:
        f.write("ENCRYPTION PERFORMANCE ANALYSIS\n")
        f.write("="*80 + "\n\n")
        f.write(perf_table)
        f.write("\n\n")
        latex_perf = tabulate(perf_data, headers=perf_headers, tablefmt='latex')
        f.write("LaTeX Version:\n")
        f.write(latex_perf)
    
    print("  [OK] Performance table created")
    
    # -------------------------------------------------------------------------
    # 8. CREATE COMPARISON WITH PRESENT TABLE (Theoretical)
    # -------------------------------------------------------------------------
    print("\n[8/8] Creating comparison table with PRESENT cipher...")
    
    # Average metrics from results
    avg_entropy_enc = np.mean([r['metrics']['encrypted']['entropy'] for r in results_all])
    avg_corr_h = np.mean([abs(r['metrics']['encrypted']['corr_h']) for r in results_all])
    avg_corr_v = np.mean([abs(r['metrics']['encrypted']['corr_v']) for r in results_all])
    avg_npcr = np.mean([r['metrics']['differential']['npcr'] for r in results_all])
    avg_uaci = np.mean([r['metrics']['differential']['uaci'] for r in results_all])
    avg_rounds = np.mean([r['metrics']['encryption_stats']['mean_rounds'] for r in results_all])
    
    # Comparison table (PRESENT values from paper)
    comp_data = [
        ['Entropy', '~7.5', f'{avg_entropy_enc:.4f}', '8.0 (ideal)'],
        ['Correlation (H)', '0.05-0.94*', f'{avg_corr_h:.4f}', '<0.01'],
        ['Correlation (V)', '0.05-0.90*', f'{avg_corr_v:.4f}', '<0.01'],
        ['NPCR (%)', '~99.5', f'{avg_npcr:.4f}', '>99.6'],
        ['UACI (%)', '28.56-29.53', f'{avg_uaci:.4f}', '33.46'],
        ['Rounds', '31 (fixed)', f'{avg_rounds:.1f} (adaptive)', 'Variable'],
        ['Key Space', '2^80', '2^256', '>2^128'],
    ]
    
    comp_headers = ['Metric', 'PRESENT', 'Enhanced PWLCM', 'Ideal/Target']
    comp_table = tabulate(comp_data, headers=comp_headers, tablefmt='grid')
    
    with open(viz.output_dir / 'comparison_table.txt', 'w') as f:
        f.write("COMPARISON: PRESENT vs Enhanced PWLCM\n")
        f.write("="*80 + "\n")
        f.write("* PRESENT shows poor correlation for highly correlated images\n\n")
        f.write(comp_table)
        f.write("\n\n")
        latex_comp = tabulate(comp_data, headers=comp_headers, tablefmt='latex')
        f.write("LaTeX Version:\n")
        f.write(latex_comp)
    
    print("  [OK] Comparison table created")
    
    #--------------------------------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "="*80)
    print(" PAPER MATERIALS GENERATION COMPLETE!")
    print("="*80)
    print(f"\nAll materials saved to: {viz.output_dir}")
    print("\nGenerated files:")
    print("  * Chaotic map analysis (bifurcation, Lyapunov)")
    print("  * Image comparisons (original vs encrypted)")
    print("  * Histogram comparisons")
    print("  * Correlation plots (H/V/D)")
    print("  * Comprehensive metrics table")
    print("  * Performance analysis table")
    print("  * Comparison with PRESENT cipher")
    print("\n[SUCCESS] Ready for paper writing!")
    print("="*80)


if __name__ == "__main__":
    generate_all_paper_materials()
