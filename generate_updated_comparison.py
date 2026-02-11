import matplotlib.pyplot as plt
import numpy as np

def generate_comparison_chart():
    # Performance metrics for comparison (EXACT VALUES FROM TABLE 3)
    labels = ['Entropy', 'Correlation', 'NPCR (%)', 'UACI (%)', 'Complexity (1/CPB)']
    
    # Table 3 Data
    #             Entropy   Corr    NPCR    UACI    CPB
    table_data = {
        'PRESENT':   [7.5,     0.05,   99.5,   33.1,   850.0],
        'Speck-128': [7.92,    0.004,  99.55,  33.3,   72.0],
        'CLEFIA':    [7.99,    0.002,  99.61,  33.45,  140.0],
        'ASCON-128': [7.999,   0.001,  99.63,  33.48,  18.0],
        'AES-128':   [7.99,    0.002,  99.60,  33.46,  210.0],
        'LHC-Med':   [7.9985,  0.0016, 100.0,  33.95,  15.5]
    }
    
    # Normalization Logic (all higher is better)
    # 1. Entropy: x/8.0
    # 2. Correlation: 1 - x
    # 3. NPCR: x/100.0
    # 4. UACI: x/theoretical (33.46)
    # 5. Complexity: (1/CPB) normalized so LHC-Med = 1.0
    
    max_inv_cpb = 1/15.5
    uaci_theoretical = 33.46
    
    normalized_data = {}
    for cipher, vals in table_data.items():
        norm_vals = [
            vals[0] / 8.0,             # Entropy
            1.0 - vals[1],             # Correlation
            vals[2] / 100.0,           # NPCR
            vals[3] / uaci_theoretical, # UACI
            (1.0/vals[4]) / max_inv_cpb # Complexity
        ]
        normalized_data[cipher] = norm_vals

    colors = ['#BDC3C7', '#95A5A6', '#7F8C8D', '#F39C12', '#2C3E50', '#E74C3C']
    
    x = np.arange(len(labels))
    width = 0.13
    
    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    
    # Customizing the background
    ax.set_facecolor('#fdfdfd')
    fig.patch.set_facecolor('white')
    
    # Sort keys to ensure consistent order (though OrderedDict would be better, standard keys work)
    cipher_order = ['PRESENT', 'Speck-128', 'CLEFIA', 'ASCON-128', 'AES-128', 'LHC-Med']
    
    for i, cipher in enumerate(cipher_order):
        vals = normalized_data[cipher]
        offset = (i - 2.5) * width
        bars = ax.bar(x + offset, vals, width, label=cipher, color=colors[i], 
                      alpha=0.9, edgecolor='white', linewidth=0.5)
        
        if cipher == 'LHC-Med':
            for bar in bars:
                bar.set_linewidth(1.5)
                bar.set_edgecolor('#c0392b')

    # Zoom in on the y-axis to see differences in Entropy/NPCR/UACI/Corr
    # But keep 0 for Complexity to show how much better we are
    ax.set_ylim(0, 1.1) 
    
    ax.set_ylabel('Normalized Performance Score', fontsize=12, fontweight='bold')
    ax.set_title('Normalized Performance Benchmark: LHC-Med vs. Standards', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), 
              ncol=6, frameon=True, facecolor='white', edgecolor='#eeeeee', fontsize=10)
    
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#999999')
    ax.set_axisbelow(True)
    
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('d:/Atelier HDR/ENCRYPT MEDICAL/paper/statistical_comparison.png', 
                dpi=400, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    generate_comparison_chart()
    print("Mathematically accurate statistical comparison chart generated.")
