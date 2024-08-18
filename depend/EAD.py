from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def encrypt_data(data):
    """使用AES加密数据"""
    # 生成密钥和初始化向量IV
    key = os.urandom(32)  # AES-256位密钥
    iv = os.urandom(16)  # AES需要128位IV

    # 配置加密器
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    ).encryptor()

    # 填充数据以满足AES块大小要求
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    # 加密数据
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data, key, iv

def decrypt_data(encrypted_data, key, iv):
    """使用AES解密数据"""
    # 配置解密器
    decryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    ).decryptor()

    # 解密数据
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # 移除填充
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return decrypted_data.decode('utf-8')