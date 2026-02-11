# Quick Start Guide

## Installation

1. **Navigate to the project directory:**
```bash
cd "d:\Atelier HDR\ENCRYPT MEDICAL\enhanced_encryption"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Generate ALL Paper Materials (Recommended)

This will encrypt your medical images and generate ALL figures, tables, and metrics for your paper:

```bash
python generate_paper_materials.py
```

**Output Location**: `results/paper_materials/`

**Generated Materials**:
- ✅ Chaotic map bifurcation diagrams
- ✅ Lyapunov exponent plots
- ✅ Image comparisons (plain vs encrypted)
- ✅ Histogram comparisons
- ✅ Correlation plots (all directions)
- ✅ Comprehensive metrics tables
- ✅ Performance analysis tables
- ✅ Comparison with PRESENT cipher table

### Option 2: Encrypt a Single Image with Full Analysis

```bash
python main.py --mode full --input "../Viral Pneumonia-9.png" --output "results/encrypted.png"
```

### Option 3: Quick Encryption Only

```bash
python main.py --mode encrypt --input "../Viral Pneumonia-9.png" --output "results/encrypted.png"
```

## Main Script Options

```bash
python main.py --help
```

**Arguments**:
- `--mode`: `encrypt` or `full` (default: `full`)
- `--input`: Path to input image (required)
- `--output`: Path to save encrypted image (default: `results/encrypted_image.png`)
- `--key`: Encryption key string (default: auto-generated)
- `--min-rounds`: Minimum adaptive rounds (default: 4)
- `--max-rounds`: Maximum adaptive rounds (default: 12)
- `--block-size`: Block size in bytes (default: 8)

## Expected Runtime

- **Single image encryption**: ~5-30 seconds (depending on size)
- **Full paper materials generation**: ~2-5 minutes (processes 3 images + generates all figures)

## Validation Checklist

After running `generate_paper_materials.py`, verify:

1. **Image Encryption** ✓
   - Encrypted images look like random noise
   - Decryption recovers original (if implemented)

2. **Security Metrics** ✓
   - Entropy (encrypted): >7.99 (close to 8.0)
   - NPCR: >99.6%
   - UACI: ~33.4%
   - Correlation: <0.01 (all directions)

3. **Figures Generated** ✓
   - Bifurcation diagrams exist
   - Image comparisons are clear
   - Histograms show uniformity for encrypted
   - Correlation plots show dispersion for encrypted

4. **Tables Created** ✓
   - `comprehensive_metrics_table.txt`
   - `performance_table.txt`
   - `comparison_table.txt`

All tables include both plain text and LaTeX versions for easy paper integration.

## For Paper Writing

### Where to Find Materials

All materials are in `results/paper_materials/`:

**Figures** (use in paper):
```
- bifurcation_*.png              → Section: Chaotic Map Analysis
- lyapunov_*.png                 → Section: Chaotic Map Analysis
- image_comparison_*.png         → Section: Experimental Results
- histogram_comparison_*.png     → Section: Security Analysis
- correlation_all_directions_*.png → Section: Security Analysis
```

**Tables** (copy LaTeX code):
```
- comprehensive_metrics_table.txt  → Security metrics table
- performance_table.txt            → Adaptive rounds analysis
- comparison_table.txt             → Comparison with PRESENT
```

### Copy-Paste LaTeX Tables

The `.txt` files contain LaTeX table code at the bottom. Simply:
1. Open the `.txt` file
2. Scroll to "LaTeX Version:"
3. Copy the `\begin{tabular}...\end{tabular}` section
4. Paste into your `.tex` file

## Troubleshooting

### Issue: "No module named 'chaos'"
**Solution**: Make sure you're in the `enhanced_encryption` directory when running scripts.

### Issue: "No medical images found"
**Solution**: The script will create synthetic test images automatically. Or place your medical images in the parent directory.

### Issue: Memory error with large images
**Solution**: Images are automatically resized to 512x512 for processing.

### Issue: Figures look different each run
**Solution**: This is normal due to chaotic randomness. For reproducible results, use the same key.

## Next Steps

1. ✅ Run `generate_paper_materials.py`
2. ✅ Verify all metrics meet security requirements
3. ✅ Review generated figures
4. ✅ Copy tables to your LaTeX paper
5. ✅ Write paper sections using the results

## Contact & Support

For questions about the implementation, refer to:
- `implementation_plan.md` - Detailed technical design
- `publication_assessment.md` - Publication strategy and target journals
- Source code comments - Detailed explanations in each module
