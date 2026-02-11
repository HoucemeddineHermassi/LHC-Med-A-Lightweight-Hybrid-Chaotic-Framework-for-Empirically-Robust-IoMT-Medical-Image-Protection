import numpy as np

def get_nonlinearity(sbox):
    """Calculate nonlinearity of a 4x4 S-box."""
    n = 4
    size = 1 << n
    nl = size
    
    for a in range(1, size):
        res_walsh = []
        for b in range(size):
            sum_val = 0
            for x in range(size):
                # Component function: b . S(x)
                fx = 0
                for i in range(n):
                    if (b >> i) & 1:
                        fx ^= (sbox[x] >> i) & 1
                
                # Walsh-Hadamard Transform
                val = (a & x)
                dot_ax = 0
                for i in range(n):
                    if (val >> i) & 1:
                        dot_ax ^= 1
                
                if fx ^ dot_ax == 0:
                    sum_val += 1
                else:
                    sum_val -= 1
            res_walsh.append(sum_val)
        
        max_walsh = max(abs(x) for x in res_walsh)
        nl = min(nl, (size - max_walsh) // 2)
    return nl

def get_differential_uniformity(sbox):
    """Calculate differential uniformity (max entry in DDT)."""
    size = 16
    ddt = np.zeros((size, size), dtype=int)
    for delta_x in range(size):
        for x in range(size):
            delta_y = sbox[x] ^ sbox[x ^ delta_x]
            ddt[delta_x][delta_y] += 1
    
    max_val = 0
    for i in range(1, size):
        for j in range(size):
            if ddt[i][j] > max_val:
                max_val = ddt[i][j]
    return max_val

def get_max_linear_bias(sbox):
    """Calculate maximum linear bias from LAT."""
    size = 16
    lat = np.zeros((size, size), dtype=int)
    for a in range(size):
        for b in range(size):
            count = 0
            for x in range(size):
                # a.x ^ b.S(x)
                dot_ax = bin(a & x).count('1') % 2
                dot_bsx = bin(b & sbox[x]).count('1') % 2
                if dot_ax == dot_bsx:
                    count += 1
            lat[a][b] = count - size // 2
            
    max_bias = 0
    for i in range(1, size):
        for j in range(1, size):
            bias = abs(lat[i][j])
            if bias > max_bias:
                max_bias = bias
    return max_bias

def get_algebraic_degree(sbox):
    """Calculate algebraic degree of a 4x4 S-box."""
    size = 16
    n = 4
    max_deg = 0
    
    # Check each output bit
    for bit in range(n):
        f = [(sbox[x] >> bit) & 1 for x in range(size)]
        # Algebraic Normal Form (ANF) using Butterfly Transform
        anf = list(f)
        for i in range(n):
            for j in range(size):
                if (j >> i) & 1:
                    anf[j] ^= anf[j ^ (1 << i)]
        
        # Degree is max weight of non-zero ANF coefficients
        for i in range(size):
            if anf[i]:
                deg = bin(i).count('1')
                if deg > max_deg:
                    max_deg = deg
    return max_deg

def analyze_sbox(sbox, name="S-box"):
    print(f"--- Analysis of {name} ---")
    print(f"Nonlinearity: {get_nonlinearity(sbox)}")
    print(f"Differential Uniformity: {get_differential_uniformity(sbox)}")
    print(f"Max Linear Bias: {get_max_linear_bias(sbox)}/8")
    print(f"Algebraic Degree: {get_algebraic_degree(sbox)}")
    print("-" * 30)

if __name__ == "__main__":
    # Test cases
    aes_sbox_4bit = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2] # This is actually the LHC-Med initial S-box
    present_sbox = [0xc, 0x5, 0x6, 0xb, 0x9, 0x0, 0xa, 0xd, 0x3, 0xe, 0xf, 0x8, 0x4, 0x7, 0x1, 0x2] # Wait, PRESENT is actually this one too? Let me double check.
    
    # PRESENT S-box:
    present_real = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 3, 0xE, 0xF, 8, 4, 7, 1, 2] # Yes, it matches LHC-Med's initial.
    
    analyze_sbox(present_real, "LHC-Med Initial (PRESENT)")
    
    # Let's test a dynamic one
    import sys
    import os
    # Add project root and enhanced_encryption to path
    root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root)
    sys.path.append(os.path.join(root, "enhanced_encryption"))
    
    from enhanced_encryption.chaos.hybrid_chaos import HybridChaos
    from enhanced_encryption.crypto.sbox_generator import ChaoticSBox
    
    chaos = HybridChaos(p=0.423, mu=0.891, x0=0.123, y0=0.456)
    sbox_gen = ChaoticSBox(chaos)
    
    for i in range(5):
        dynamic_sbox = sbox_gen.generate_sbox()
        analyze_sbox(dynamic_sbox, f"LHC-Med Dynamic S-box Round {i+1}")
