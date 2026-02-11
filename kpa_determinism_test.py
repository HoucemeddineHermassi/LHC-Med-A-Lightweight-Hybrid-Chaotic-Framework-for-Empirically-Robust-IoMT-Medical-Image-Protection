
import sys
import os
import numpy as np

# Ensure we can import the project modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.enhanced_cipher import EnhancedPWLCM as LHCMedEncryption

def test_kpa_vulnerability():
    print("[-] Starting KPA Determinism Test...")
    
    # Fixed Master Key
    master_key = b"0123456789ABCDEF0123456789ABCDEF" # Exactly 32 bytes
    
    # Create two different dummy images (same size)
    img_a = np.zeros((64, 64), dtype=np.uint8) # Image A: All Blacks
    img_b = np.full((64, 64), 255, dtype=np.uint8) # Image B: All Whites
    
    cipher = LHCMedEncryption(master_key)
    
    # We need to hook into the cipher to capture the internal state or keystream
    # Since we can't easily hook without modifying, we will infer vulnerability 
    # if the encryption process doesn't produce a unique IV/Nonce in the output
    # OR if we can predict the chaotic sequence.
    
    # Ideally, we should check if the cipher uses an IV.
    # Let's check the ciphertext structure.
    
    print("[-] Encrypting Image A (Run 1)...")
    enc_a1, iv1 = cipher.encrypt_image(img_a)
    print(f"    IV1: {iv1.hex()}")
    
    # Re-init cipher to simulate fresh session with same key
    cipher_2 = LHCMedEncryption(master_key)
    print("[-] Encrypting Image A (Run 2, Same Key)...")
    enc_a2, iv2 = cipher_2.encrypt_image(img_a)
    print(f"    IV2: {iv2.hex()}")

    # Check 1: Ciphertext Equality
    is_deterministic = np.array_equal(enc_a1, enc_a2)
    
    if is_deterministic:
        print("\n[!!!] VULNERABILITY CONFIRMED [!!!]")
        print("System is DETERMINISTIC. Encrypting the same image with the same key")
        print("produces IDENTICAL ciphertext.")
        print("This allows replay attacks and traffic analysis.")
        print("It also allows an attacker to build a dictionary of P-C pairs.")
    else:
        print("\n[+] System uses probabilistic encryption (IV detected?).")
        print("Ciphertexts are different for same input.")

if __name__ == "__main__":
    test_kpa_vulnerability()
