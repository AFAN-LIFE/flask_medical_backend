from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, hmac
from cryptography.hazmat.backends import default_backend
import os
import time
import base64

# 用于对称加密算法（如 AES）对数据进行加密和解密，确保数据的 机密性，即只有持有正确密钥的人才能解密数据。
ENCRYPTION_KEY = b'\xf7B\xa1\xcc\xb0\xd1\x80\x81\xa1\xabM\xdd\xf2\xf0\x00\x01\x97\xadMN \xaf\x9a\xa0\xe5\xec\xb7\xb1&:\x1f)'  # 32 bytes for AES-256
# 用于生成 HMAC（Hash-based Message Authentication Code，基于哈希的消息认证码）,确保数据的 完整性 和 真实性，即数据在传输或存储过程中未被篡改
HMAC_KEY = b'\x9f\xf4\xaa#N\x84\xa8\x8a%\xecI\xacM\xc4\x836\xb6rI\xbc,Hw%u9\xe60\xeb~\x823'  # 32 bytes for HMAC-SHA256

LOCAL_STORAGE_TOKEN_INVALID = 'token_invalid'
LOCAL_STORAGE_WRONG_SIGNATURE = 'wrong_signature'
LOCAL_STORAGE_TOKEN_EXPIRE = 'token_expire'

class CryptoUtils:
    @staticmethod
    def encrypt(data: str, key: bytes) -> str:
        """加密数据并返回 Base64 编码的字符串"""
        # 生成随机 IV
        iv = os.urandom(16)
        # 使用 PKCS7 填充
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()
        # 加密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        # 返回 Base64 编码的 IV + 加密数据
        return base64.b64encode(iv + encrypted_data).decode()

    @staticmethod
    def decrypt(encrypted_data: str, key: bytes) -> str:
        """解密 Base64 编码的加密数据"""
        # 解码 Base64
        data = base64.b64decode(encrypted_data)
        iv = data[:16]  # 前 16 字节是 IV
        encrypted_data = data[16:]
        # 解密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        # 去除填充
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        return (unpadder.update(padded_data) + unpadder.finalize()).decode()

    @staticmethod
    def sign(data: str, key: bytes) -> str:
        """生成 HMAC 签名"""
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data.encode())
        return base64.b64encode(h.finalize()).decode()

    @staticmethod
    def verify(data: str, signature: str, key: bytes) -> bool:
        """验证 HMAC 签名"""
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data.encode())
        try:
            h.verify(base64.b64decode(signature))
            return True
        except:
            return False

class AuthUtils:
    @staticmethod
    def create_auth_token(username: str) -> str:
        """生成包含用户名和时间戳的加密 Token"""
        # 加入时间戳
        timestamp = str(int(time.time()))
        data = f"{username}|{timestamp}"
        # 加密数据
        encrypted_data = CryptoUtils.encrypt(data, ENCRYPTION_KEY)
        # 生成 HMAC 签名
        signature = CryptoUtils.sign(encrypted_data, HMAC_KEY)
        # 返回加密数据 + 签名
        return f"{encrypted_data}.{signature}"

    @staticmethod
    def validate_auth_token(token: str, max_age: int = 24 * 3600):
        """验证 Token 并返回用户名"""
        try:
            encrypted_data, signature = token.split(".")
            # 验证 HMAC 签名
            if not CryptoUtils.verify(encrypted_data, signature, HMAC_KEY):
                return 'failed', None, LOCAL_STORAGE_WRONG_SIGNATURE
            # 解密数据
            data = CryptoUtils.decrypt(encrypted_data, ENCRYPTION_KEY)
            username, timestamp = data.split("|")
            # 检查时间戳是否过期
            if int(time.time()) - int(timestamp) > max_age:
                return 'failed', None, LOCAL_STORAGE_TOKEN_EXPIRE
            return 'success', username, '解析用户名成功'
        except Exception as e:
            return 'failed', None, LOCAL_STORAGE_TOKEN_INVALID

if __name__ == '__main__':
    print(os.urandom(32))