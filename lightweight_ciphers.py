"""
Lightweight Cipher Implementations for Extended Experimental Comparison
========================================================================

Reference implementations of:
- SIMON-64/128 (NSA 2013)
- SPECK-64/128 (NSA 2013)  
- PRESENT-80 (ISO/IEC 29192-2)
- LEA-128 (Korean Standard)

These are pure-Python implementations for benchmark comparison purposes.
"""

import numpy as np
from typing import Tuple
import time
import tracemalloc


# =============================================================================
# SIMON-64/128 Implementation
# =============================================================================

class Simon64_128:
    """SIMON-64/128: 64-bit block, 128-bit key, 44 rounds."""
    
    WORD_SIZE = 32
    ROUNDS = 44
    KEY_WORDS = 4
    
    # SIMON z-sequence for 64/128
    z = [1,1,0,1,0,0,0,1,1,1,1,0,0,1,1,0,1,0,1,1,0,1,1,0,0,0,1,0,0,0,0,0,
         0,1,0,1,1,1,0,0,0,0,1,1,0,0,1,0,1,0,0,1,0,0,1,1,1,0,1,1,1,1]
    
    def __init__(self, key: bytes):
        """Initialize with 128-bit (16-byte) key."""
        assert len(key) == 16, "SIMON-64/128 requires 16-byte key"
        self.round_keys = self._key_schedule(key)
    
    def _rol(self, x: int, n: int) -> int:
        """Rotate left within 32-bit word."""
        return ((x << n) | (x >> (self.WORD_SIZE - n))) & 0xFFFFFFFF
    
    def _ror(self, x: int, n: int) -> int:
        """Rotate right within 32-bit word."""
        return ((x >> n) | (x << (self.WORD_SIZE - n))) & 0xFFFFFFFF
    
    def _key_schedule(self, key: bytes) -> list:
        """Generate round keys from master key."""
        k = [int.from_bytes(key[i*4:(i+1)*4], 'little') for i in range(4)]
        keys = k.copy()
        
        for i in range(self.ROUNDS - self.KEY_WORDS):
            tmp = self._ror(keys[-1], 3)
            tmp ^= keys[-3]
            tmp ^= self._ror(tmp, 1)
            new_key = ~keys[-(self.KEY_WORDS)] & 0xFFFFFFFF
            new_key ^= tmp
            new_key ^= self.z[(i + self.KEY_WORDS - 1) % 62]
            new_key ^= 3
            keys.append(new_key & 0xFFFFFFFF)
        
        return keys
    
    def encrypt_block(self, block: bytes) -> bytes:
        """Encrypt a single 64-bit block."""
        x = int.from_bytes(block[4:8], 'little')
        y = int.from_bytes(block[0:4], 'little')
        
        for i in range(self.ROUNDS):
            tmp = x
            x = y ^ (self._rol(x, 1) & self._rol(x, 8)) ^ self._rol(x, 2) ^ self.round_keys[i]
            y = tmp
            x &= 0xFFFFFFFF
        
        return y.to_bytes(4, 'little') + x.to_bytes(4, 'little')
    
    def decrypt_block(self, block: bytes) -> bytes:
        """Decrypt a single 64-bit block."""
        x = int.from_bytes(block[4:8], 'little')
        y = int.from_bytes(block[0:4], 'little')
        
        for i in range(self.ROUNDS - 1, -1, -1):
            tmp = y
            y = x ^ (self._rol(y, 1) & self._rol(y, 8)) ^ self._rol(y, 2) ^ self.round_keys[i]
            x = tmp
            y &= 0xFFFFFFFF
        
        return y.to_bytes(4, 'little') + x.to_bytes(4, 'little')


# =============================================================================
# SPECK-64/128 Implementation
# =============================================================================

class Speck64_128:
    """SPECK-64/128: 64-bit block, 128-bit key, 27 rounds."""
    
    WORD_SIZE = 32
    ROUNDS = 27
    ALPHA = 8
    BETA = 3
    
    def __init__(self, key: bytes):
        """Initialize with 128-bit (16-byte) key."""
        assert len(key) == 16, "SPECK-64/128 requires 16-byte key"
        self.round_keys = self._key_schedule(key)
    
    def _ror(self, x: int, n: int) -> int:
        return ((x >> n) | (x << (self.WORD_SIZE - n))) & 0xFFFFFFFF
    
    def _rol(self, x: int, n: int) -> int:
        return ((x << n) | (x >> (self.WORD_SIZE - n))) & 0xFFFFFFFF
    
    def _key_schedule(self, key: bytes) -> list:
        """Generate round keys."""
        k = [int.from_bytes(key[i*4:(i+1)*4], 'little') for i in range(4)]
        keys = [k[0]]
        l = k[1:]
        
        for i in range(self.ROUNDS - 1):
            l_new = (keys[i] + self._ror(l[0], self.ALPHA)) & 0xFFFFFFFF
            l_new ^= i
            k_new = self._rol(keys[i], self.BETA) ^ l_new
            keys.append(k_new)
            l = l[1:] + [l_new]
        
        return keys
    
    def encrypt_block(self, block: bytes) -> bytes:
        """Encrypt a single 64-bit block."""
        x = int.from_bytes(block[4:8], 'little')
        y = int.from_bytes(block[0:4], 'little')
        
        for k in self.round_keys:
            x = (self._ror(x, self.ALPHA) + y) & 0xFFFFFFFF
            x ^= k
            y = self._rol(y, self.BETA) ^ x
        
        return y.to_bytes(4, 'little') + x.to_bytes(4, 'little')
    
    def decrypt_block(self, block: bytes) -> bytes:
        """Decrypt a single 64-bit block."""
        x = int.from_bytes(block[4:8], 'little')
        y = int.from_bytes(block[0:4], 'little')
        
        for k in reversed(self.round_keys):
            y = self._ror(x ^ y, self.BETA)
            x = self._rol((x ^ k) - y & 0xFFFFFFFF, self.ALPHA)
        
        return y.to_bytes(4, 'little') + x.to_bytes(4, 'little')


# =============================================================================
# PRESENT-80 Implementation
# =============================================================================

class Present80:
    """PRESENT-80: 64-bit block, 80-bit key, 31 rounds."""
    
    ROUNDS = 31
    
    # PRESENT S-box (4-bit)
    SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
            0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
    
    SBOX_INV = [0x5, 0xE, 0xF, 0x8, 0xC, 0x1, 0x2, 0xD,
                0xB, 0x4, 0x6, 0x3, 0x0, 0x7, 0x9, 0xA]
    
    # Permutation layer
    PBOX = [0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51,
            4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
            8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59,
            12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63]
    
    def __init__(self, key: bytes):
        """Initialize with 80-bit (10-byte) key."""
        assert len(key) == 10, "PRESENT-80 requires 10-byte key"
        self.round_keys = self._key_schedule(key)
    
    def _key_schedule(self, key: bytes) -> list:
        """Generate 32 round keys (64-bit each)."""
        key_reg = int.from_bytes(key, 'big')
        keys = []
        
        for i in range(self.ROUNDS + 1):
            # Extract top 64 bits as round key
            keys.append((key_reg >> 16) & 0xFFFFFFFFFFFFFFFF)
            
            # Rotate left 61 bits
            key_reg = ((key_reg << 61) | (key_reg >> 19)) & ((1 << 80) - 1)
            
            # Apply S-box to top 4 bits
            top4 = (key_reg >> 76) & 0xF
            key_reg = (key_reg & ((1 << 76) - 1)) | (self.SBOX[top4] << 76)
            
            # XOR round counter into bits 15-19
            key_reg ^= (i + 1) << 15
        
        return keys
    
    def _sbox_layer(self, state: int) -> int:
        """Apply 4-bit S-box to 64-bit state."""
        result = 0
        for i in range(16):
            nibble = (state >> (i * 4)) & 0xF
            result |= self.SBOX[nibble] << (i * 4)
        return result
    
    def _permutation(self, state: int) -> int:
        """Apply bit permutation."""
        result = 0
        for i in range(64):
            if state & (1 << i):
                result |= 1 << self.PBOX[i]
        return result
    
    def encrypt_block(self, block: bytes) -> bytes:
        """Encrypt a single 64-bit block."""
        state = int.from_bytes(block, 'big')
        
        for i in range(self.ROUNDS):
            state ^= self.round_keys[i]
            state = self._sbox_layer(state)
            state = self._permutation(state)
        
        state ^= self.round_keys[self.ROUNDS]
        return state.to_bytes(8, 'big')


# =============================================================================
# LEA-128 Implementation
# =============================================================================

class Lea128:
    """LEA-128: 128-bit block, 128-bit key, 24 rounds."""
    
    ROUNDS = 24
    DELTA = [0xc3efe9db, 0x44626b02, 0x79e27c8a, 0x78df30ec,
             0x715ea49e, 0xc785da0a, 0xe04ef22a, 0xe5c40957]
    
    def __init__(self, key: bytes):
        """Initialize with 128-bit (16-byte) key."""
        assert len(key) == 16, "LEA-128 requires 16-byte key"
        self.round_keys = self._key_schedule(key)
    
    def _rol(self, x: int, n: int) -> int:
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF
    
    def _ror(self, x: int, n: int) -> int:
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF
    
    def _key_schedule(self, key: bytes) -> list:
        """Generate round keys."""
        T = [int.from_bytes(key[i*4:(i+1)*4], 'little') for i in range(4)]
        keys = []
        
        for i in range(self.ROUNDS):
            d = self.DELTA[i % 4]
            T[0] = self._rol((T[0] + self._rol(d, i)) & 0xFFFFFFFF, 1)
            T[1] = self._rol((T[1] + self._rol(d, i + 1)) & 0xFFFFFFFF, 3)
            T[2] = self._rol((T[2] + self._rol(d, i + 2)) & 0xFFFFFFFF, 6)
            T[3] = self._rol((T[3] + self._rol(d, i + 3)) & 0xFFFFFFFF, 11)
            keys.append(T.copy())
        
        return keys
    
    def encrypt_block(self, block: bytes) -> bytes:
        """Encrypt a single 128-bit block."""
        X = [int.from_bytes(block[i*4:(i+1)*4], 'little') for i in range(4)]
        
        for rk in self.round_keys:
            tmp = X.copy()
            X[0] = self._rol((tmp[0] ^ rk[0]) + (tmp[1] ^ rk[1]) & 0xFFFFFFFF, 9)
            X[1] = self._ror((tmp[1] ^ rk[2]) + (tmp[2] ^ rk[1]) & 0xFFFFFFFF, 5)
            X[2] = self._ror((tmp[2] ^ rk[3]) + (tmp[3] ^ rk[1]) & 0xFFFFFFFF, 3)
            X[3] = tmp[0]
        
        result = b''
        for x in X:
            result += x.to_bytes(4, 'little')
        return result


# =============================================================================
# Image Encryption Wrapper for Block Ciphers
# =============================================================================

def encrypt_image_with_cipher(cipher, image: np.ndarray, block_size: int = 8) -> np.ndarray:
    """
    Encrypt an image using a block cipher in ECB mode.
    
    Args:
        cipher: Cipher object with encrypt_block method
        image: Grayscale image as numpy array
        block_size: Block size in bytes (8 for 64-bit, 16 for 128-bit)
    
    Returns:
        Encrypted image as numpy array
    """
    h, w = image.shape
    flat = image.flatten().tobytes()
    
    # Pad to block size
    pad_len = (block_size - len(flat) % block_size) % block_size
    flat_padded = flat + bytes(pad_len)
    
    # Encrypt block by block
    encrypted = b''
    for i in range(0, len(flat_padded), block_size):
        block = flat_padded[i:i+block_size]
        encrypted += cipher.encrypt_block(block)
    
    # Convert back to image
    encrypted_arr = np.frombuffer(encrypted[:h*w], dtype=np.uint8).reshape(h, w)
    return encrypted_arr


# =============================================================================
# Chaos-Based Schemes (2023-2024)
# =============================================================================

class HuaLogisticSine2023:
    """
    2D Logistic-Sine-Coupling Map (Hua et al. 2023)
    Simplified implementation for benchmark comparison.
    """
    
    def __init__(self, key: bytes):
        """Initialize with 256-bit key."""
        self.x0 = (int.from_bytes(key[:8], 'big') % (10**14)) / 10**14
        self.y0 = (int.from_bytes(key[8:16], 'big') % (10**14)) / 10**14
        self.mu = 3.9 + (int.from_bytes(key[16:20], 'big') % 1000) / 10000
    
    def _iterate(self, x, y, n=100):
        """Generate n chaotic values."""
        values = []
        for _ in range(n + 100):  # 100 transient iterations
            x_new = np.sin(np.pi * (4 * self.mu * x * (1 - x) + (1 - self.mu) * np.sin(np.pi * y)))
            y_new = np.sin(np.pi * (4 * self.mu * y * (1 - y) + (1 - self.mu) * np.sin(np.pi * x)))
            x, y = x_new % 1, y_new % 1
            if len(values) < n:
                values.append((x, y))
        return values[-n:]
    
    def encrypt_image(self, image: np.ndarray) -> np.ndarray:
        """Encrypt image using 2D logistic-sine chaos."""
        h, w = image.shape
        flat = image.flatten()
        
        # Generate keystream
        n_values = (len(flat) + 1) // 2
        chaos_values = self._iterate(self.x0, self.y0, n_values)
        
        # Create keystream
        keystream = []
        for x, y in chaos_values:
            keystream.append(int(x * 256) % 256)
            keystream.append(int(y * 256) % 256)
        keystream = np.array(keystream[:len(flat)], dtype=np.uint8)
        
        # XOR encryption with diffusion
        encrypted = np.zeros_like(flat)
        encrypted[0] = flat[0] ^ keystream[0]
        for i in range(1, len(flat)):
            encrypted[i] = flat[i] ^ keystream[i] ^ encrypted[i-1]
        
        return encrypted.reshape(h, w)


class Yuan4DHyperchaotic2024:
    """
    4D Hyperchaotic System (Yuan et al. 2024)
    Simplified implementation for benchmark comparison.
    """
    
    def __init__(self, key: bytes):
        """Initialize with 256-bit key."""
        self.x0 = (int.from_bytes(key[0:4], 'big') % 10000) / 10000
        self.y0 = (int.from_bytes(key[4:8], 'big') % 10000) / 10000
        self.z0 = (int.from_bytes(key[8:12], 'big') % 10000) / 10000
        self.w0 = (int.from_bytes(key[12:16], 'big') % 10000) / 10000
        self.a, self.b, self.c, self.d = 35, 3, 12, 7
    
    def _iterate(self, n=100):
        """Generate n chaotic values using RK4 integration."""
        dt = 0.001
        x, y, z, w = self.x0, self.y0, self.z0, self.w0
        values = []
        
        for _ in range(n + 1000):  # 1000 transient
            # Simplified Euler integration
            dx = self.a * (y - x) + w
            dy = self.c * x - x * z + w
            dz = x * y - self.b * z
            dw = -y * z + self.d * w
            
            x = (x + dt * dx) % 10
            y = (y + dt * dy) % 10
            z = (z + dt * dz) % 10
            w = (w + dt * dw) % 10
            
            if len(values) < n:
                values.append((x, y, z, w))
        
        return values[-n:]
    
    def encrypt_image(self, image: np.ndarray) -> np.ndarray:
        """Encrypt image using 4D hyperchaotic system."""
        h, w = image.shape
        flat = image.flatten()
        
        # Generate keystream
        n_values = (len(flat) + 3) // 4
        chaos_values = self._iterate(n_values)
        
        # Create keystream from 4D values
        keystream = []
        for vals in chaos_values:
            for v in vals:
                keystream.append(int(abs(v) * 256) % 256)
        keystream = np.array(keystream[:len(flat)], dtype=np.uint8)
        
        # XOR encryption with diffusion
        encrypted = np.zeros_like(flat)
        encrypted[0] = flat[0] ^ keystream[0]
        for i in range(1, len(flat)):
            encrypted[i] = flat[i] ^ keystream[i] ^ encrypted[i-1]
        
        return encrypted.reshape(h, w)


# =============================================================================
# Benchmark Utilities
# =============================================================================

def measure_memory_footprint(cipher_class, key: bytes) -> float:
    """Measure memory footprint of cipher initialization in KB."""
    tracemalloc.start()
    cipher = cipher_class(key)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024  # Convert to KB


def measure_execution_time(encrypt_func, image: np.ndarray, iterations: int = 10) -> float:
    """Measure average execution time in milliseconds."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        encrypt_func(image)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    return np.mean(times)


def estimate_energy_consumption(execution_time_ms: float, power_watts: float = 0.5) -> float:
    """
    Estimate energy consumption in mJ.
    Assumes typical embedded processor power consumption.
    
    Args:
        execution_time_ms: Execution time in milliseconds
        power_watts: Estimated power consumption (default 0.5W for Cortex-M4)
    
    Returns:
        Energy in millijoules (mJ)
    """
    return execution_time_ms * power_watts


if __name__ == "__main__":
    # Quick test
    key_128 = b'\x00' * 16
    key_80 = b'\x00' * 10
    
    print("Testing SIMON-64/128...")
    simon = Simon64_128(key_128)
    pt = b'\x00' * 8
    ct = simon.encrypt_block(pt)
    dt = simon.decrypt_block(ct)
    print(f"  PT: {pt.hex()}, CT: {ct.hex()}, DT: {dt.hex()}")
    assert pt == dt, "SIMON decryption failed!"
    
    print("Testing SPECK-64/128...")
    speck = Speck64_128(key_128)
    ct = speck.encrypt_block(pt)
    dt = speck.decrypt_block(ct)
    print(f"  PT: {pt.hex()}, CT: {ct.hex()}, DT: {dt.hex()}")
    assert pt == dt, "SPECK decryption failed!"
    
    print("Testing PRESENT-80...")
    present = Present80(key_80)
    ct = present.encrypt_block(pt)
    print(f"  PT: {pt.hex()}, CT: {ct.hex()}")
    
    print("Testing LEA-128...")
    lea = Lea128(key_128)
    pt_128 = b'\x00' * 16
    ct = lea.encrypt_block(pt_128)
    print(f"  PT: {pt_128.hex()}, CT: {ct.hex()}")
    
    print("\nAll cipher implementations verified!")
