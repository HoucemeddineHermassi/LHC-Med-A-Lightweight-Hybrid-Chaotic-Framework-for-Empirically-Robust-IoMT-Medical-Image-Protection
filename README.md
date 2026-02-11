# LHC-Med: A Lightweight Hybrid Chaotic Framework for Empirically Robust IoMT Medical Image Protection

Implementation of lightweight encryption for medical images in IoMT infrastructure.

## Features

- Hybrid chaotic map system (Skew Tent + Logistic-Sine)
- Adaptive round selection based on image content
- Dynamic S-BOX generation using chaotic sequences
- Bit-level permutation with diffusion
- Comprehensive security analysis
- Automated paper material generation

## Project Structure
enhanced_encryption/
├── chaos/              # Chaotic map implementations
├── crypto/             # Encryption core components
├── medical/            # Medical image specific features
├── metrics/            # Security metrics & analysis
├── visualization/      # Paper graphics generation
├── comparison/         # Baseline comparisons
├── data/              # Test images
├── results/           # Generated outputs
└── main.py            # Primary entry point
```

## Requirements

```
numpy>=1.24.0
matplotlib>=3.7.0
Pillow>=10.0.0
scipy>=1.10.0
opencv-python>=4.8.0
pandas>=2.0.0
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run full encryption & generate paper materials
python main.py --mode full --input data/Viral_Pneumonia-9.png

# Run only encryption
python main.py --mode encrypt --input data/test_image.png

# Generate all paper figures
python generate_paper_materials.py
```

## Output

All paper materials will be generated in `results/paper_materials/`:
- Correlation plots
- Histogram analysis
- Chaos map visualizations
- Performance comparison tables
- Security metrics tables
- Encrypted/decrypted image examples
# LHC-Med-A-Lightweight-Hybrid-Chaotic-Framework-for-Empirically-Robust-IoMT-Medical-Image-Protection
