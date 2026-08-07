#!/usr/bin/env python3
"""
Cryptographic Utilities for WSN Spoofing Detection Framework (Objective 4).
Implements lightweight crypto primitives, ECDSA-P256 signatures, HMAC-SHA256,
and energy accounting functions.
"""

import hmac
import hashlib
import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# Energy Cost Constants (Joules)
ECC_P256_SIGN_ENERGY = 0.045     # 45 mJ per signature generation on MSP430
ECC_P256_VERIFY_ENERGY = 0.090   # 90 mJ per signature verification on MSP430
HMAC_SHA256_ENERGY = 0.001       # 1 mJ per HMAC operation
TIER1_RSSI_CHECK_ENERGY = 0.000005 # 5 uJ for physical layer RSSI check
TIER2_ML_EVAL_ENERGY = 0.00010   # 100 uJ for lightweight ML evaluation

def generate_ecdsa_keypair():
    """Generates an ECDSA NIST P-256 private and public key pair."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

def ecdsa_sign(private_key, data: bytes) -> bytes:
    """Signs data using ECDSA-P256 with SHA-256 digest."""
    signature = private_key.sign(
        data,
        ec.ECDSA(hashes.SHA256())
    )
    return signature

def ecdsa_verify(public_key, signature: bytes, data: bytes) -> bool:
    """Verifies an ECDSA-P256 signature against data."""
    try:
        public_key.verify(
            signature,
            data,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False

def compute_hmac(key: bytes, message: bytes) -> bytes:
    """Computes HMAC-SHA256 tag for payload integrity."""
    return hmac.new(key, message, hashlib.sha256).digest()

def verify_hmac(key: bytes, message: bytes, tag: bytes) -> bool:
    """Verifies HMAC-SHA256 tag in constant time."""
    expected = compute_hmac(key, message)
    return hmac.compare_digest(expected, tag)

def serialize_public_key(public_key) -> bytes:
    """Serializes public key to PEM format."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_public_key(pem_bytes: bytes):
    """Deserializes public key from PEM format."""
    return serialization.load_pem_public_key(pem_bytes)
