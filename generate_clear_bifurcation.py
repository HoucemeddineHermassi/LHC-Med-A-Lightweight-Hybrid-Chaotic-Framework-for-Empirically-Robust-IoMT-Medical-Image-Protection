import numpy as np
import matplotlib.pyplot as plt

# Using a professional style for academic papers
try:
    plt.style.use('seaborn-v0_8-paper')
except:
    plt.style.use('ggplot')

def skew_tent_map(x, p):
    if 0 <= x < p:
        return x / p
    elif p <= x <= 1:
        return (1 - x) / (1 - p)
    return x

def logistic_sine_map(y, mu):
    # This is the coupling used in the paper
    return (mu * y * (1 - y) + (4 - mu) * np.sin(np.pi * y) / 4) % 1

def generate_bifurcation_stm():
    print("Generating Ultra-High Fidelity STM Bifurcation Diagram...")
    n_params = 4000  # Increased from 2000
    n_iters = 2000   # Increased from 1500
    n_last = 1000    # Increased from 600
    
    ps = np.linspace(0.01, 0.99, n_params)
    x_results = []
    p_results = []
    
    for p in ps:
        x = 0.512345  # Seed
        for i in range(n_iters):
            x = skew_tent_map(x, p)
            if i >= (n_iters - n_last):
                x_results.append(x)
                p_results.append(p)
                
    plt.figure(figsize=(10, 6), dpi=600)
    # Using a professional navy blue with very low alpha for density visualization
    plt.plot(p_results, x_results, ',', color='#003366', alpha=0.1)
    
    plt.title("Bifurcation Analysis: Skew Tent Map (Full Dynamics)", fontsize=16, fontweight='bold')
    plt.xlabel("Control Parameter ($p$)", fontsize=14)
    plt.ylabel("State Variable ($x$)", fontsize=14)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.2)
    
    # Save to paper directory
    out_path = "d:/Atelier HDR/ENCRYPT MEDICAL/paper/bifurcation_SkewTentMap_p.png"
    plt.savefig(out_path, bbox_inches='tight', dpi=600, facecolor='white')
    plt.close()

def generate_bifurcation_lsm():
    print("Generating Ultra-High Fidelity LSM Bifurcation Diagram...")
    n_params = 4000  # Increased from 2000
    n_iters = 2000   # Increased from 1500
    n_last = 1000    # Increased from 600
    
    mus = np.linspace(0.01, 0.99, n_params)
    y_results = []
    mu_results = []
    
    for mu in mus:
        y = 0.512345  # Seed
        for i in range(n_iters):
            y = logistic_sine_map(y, mu)
            if i >= (n_iters - n_last):
                y_results.append(y)
                mu_results.append(mu)
                
    plt.figure(figsize=(10, 6), dpi=600)
    # Consistent professional navy blue
    plt.plot(mu_results, y_results, ',', color='#003366', alpha=0.1)
    
    plt.title("Bifurcation Analysis: Logistic-Sine Map (Full Dynamics)", fontsize=16, fontweight='bold')
    plt.xlabel("Control Parameter ($\mu$)", fontsize=14)
    plt.ylabel("State Variable ($y$)", fontsize=14)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.2)
    
    # Save to paper directory
    out_path = "d:/Atelier HDR/ENCRYPT MEDICAL/paper/bifurcation_LogisticSineMap_mu.png"
    plt.savefig(out_path, bbox_inches='tight', dpi=600, facecolor='white')
    plt.close()

if __name__ == "__main__":
    generate_bifurcation_stm()
    generate_bifurcation_lsm()
    print("Ultra-high fidelity bifurcation diagrams generated successfully.")
