#!/usr/bin/env python3

# This code was generated with the help of GenAI tools - please check through thoroughly before using

import base64
import os
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_key(password, salt):
    """Derive a key from the password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits for AES-256
        salt=salt,
        iterations=100000,  # Recommended minimum by NIST
    )
    return kdf.derive(password.encode('utf-8'))

def encrypt_text(text, password):
    """Encrypt text using AES-GCM with a password-derived key."""
    # Generate a random salt
    salt = os.urandom(16)
    
    # Derive key from password
    key = derive_key(password, salt)
    
    # Generate a random nonce
    nonce = os.urandom(12)  # 96 bits as recommended for AES-GCM
    
    # Create an AES-GCM cipher
    aesgcm = AESGCM(key)
    
    # Encrypt the text
    ciphertext = aesgcm.encrypt(nonce, text.encode('utf-8'), None)
    
    # Combine salt, nonce, and ciphertext for storage
    encrypted_data = salt + nonce + ciphertext
    
    # Return base64 encoded data for easy storage/transmission
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_text(encrypted_data, password):
    """Decrypt text that was encrypted with encrypt_text."""
    # Decode from base64
    encrypted_data = base64.b64decode(encrypted_data)
    
    # Extract salt, nonce, and ciphertext
    salt = encrypted_data[:16]
    nonce = encrypted_data[16:28]
    ciphertext = encrypted_data[28:]
    
    # Derive key from password and salt
    key = derive_key(password, salt)
    
    # Create an AES-GCM cipher
    aesgcm = AESGCM(key)
    
    try:
        # Decrypt the ciphertext
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception:
        return "Decryption failed. Incorrect password or corrupted data."

def main():
    print("\n" + "="*60)
    print("Text Encryption/Decryption Tool".center(60))
    print("="*60 + "\n")
    
    while True:
        print("Select an option:")
        print("1. Encrypt text")
        print("2. Decrypt text")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            print("\n--- ENCRYPTION ---")
            text = input("Enter the text to encrypt (or paste a block of text):\n")
            if not text:
                print("No text entered. Returning to menu.")
                continue
                
            password = getpass.getpass("Enter encryption password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if password != confirm_password:
                print("Passwords don't match. Please try again.")
                continue
                
            encrypted = encrypt_text(text, password)
            
            print("\nEncrypted text:")
            print("-"*60)
            print(encrypted)
            print("-"*60)
            print("Keep this encrypted text and your password safe!")
            
        elif choice == '2':
            print("\n--- DECRYPTION ---")
            encrypted_text = input("Enter the encrypted text to decrypt:\n")
            if not encrypted_text:
                print("No text entered. Returning to menu.")
                continue
                
            password = getpass.getpass("Enter decryption password: ")
            
            decrypted = decrypt_text(encrypted_text, password)
            
            print("\nDecrypted text:")
            print("-"*60)
            print(decrypted)
            print("-"*60)
            
        elif choice == '3':
            print("\nExiting program. Goodbye!")
            break
            
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
