import time
import requests
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tool.auth_storage import AuthUtils
from flask import Blueprint, request, jsonify
from config import login_url

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 定义密钥
key = b'cBeaUKs3ZA==HKXT'


# 加密函数
def aes_encode(plain_text):
    # 创建AES加密器
    cipher = AES.new(key, AES.MODE_ECB)
    # 对数据进行填充并加密
    encrypted_bytes = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
    # 将加密结果编码为base64
    encrypted_base64 = b64encode(encrypted_bytes).decode('utf-8')
    return encrypted_base64


# 解密函数
def aes_decode(encrypted_base64):
    # 将base64编码的加密数据解码
    encrypted_bytes = b64decode(encrypted_base64)
    # 创建AES解密器
    cipher = AES.new(key, AES.MODE_ECB)
    # 对数据进行解密并去除填充
    decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    # 将解密结果转换为字符串
    decrypted_text = decrypted_bytes.decode('utf-8')
    return decrypted_text


def request_login(username, encrypted_password):
    # 请求数据
    data = {
        "username": username,
        "password": encrypted_password
    }

    # 请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': '_ga=GA1.1.1850943592.1694747216; ajs_anonymous_id=cc39bf4a-d45f-4ed4-8d15-6e4cec4eecef',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    # 发送POST请求
    response = requests.post(login_url, json=data, headers=headers, verify=False)
    return response


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        login_user_name = data.get('username')
        enrypt_pwd = data.get('password')  # 密码已经在前端加密

        if not login_user_name or not enrypt_pwd:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        # 远程生产模式
        login_return = request_login(str(login_user_name), str(enrypt_pwd))
        login_return_json = json.loads(login_return.text)

        if login_return_json['retCode'] == '0':
            username = login_return_json['data']['username']
            xAuthToken = login_return_json['data']['xAuthToken']

            # 生成 medical_token
            medical_token = AuthUtils.create_auth_token(username)

            # 构建完整的用户信息
            user_info = {
                'userId': login_return_json['data'].get('userId'),
                'username': username,
                'xAuthToken': xAuthToken,
                'nickName': login_return_json['data'].get('nickName'),
                'email': login_return_json['data'].get('email'),
                'avatar': login_return_json['data'].get('avatar'),
                'phone': login_return_json['data'].get('phone'),
                'createTime': login_return_json['data'].get('createTime'),
                'loginDate': login_return_json['data'].get('loginDate'),
                'accountNonExpired': login_return_json['data'].get('accountNonExpired', True),
                'accountNonLocked': login_return_json['data'].get('accountNonLocked', True),
                'credentialsNonExpired': login_return_json['data'].get('credentialsNonExpired', True),
                'enabled': login_return_json['data'].get('enabled', True),
                'disabled': login_return_json['data'].get('disabled', False),
                'deleted': login_return_json['data'].get('deleted', False),
                'resourceAuthorities': login_return_json['data'].get('resourceAuthorities', []),
                'roleAuthorities': login_return_json['data'].get('roleAuthorities', []),
                'medical_token': medical_token
            }
        else:
            return jsonify({
                'success': False,
                'message': login_return_json.get('retMsg', '登录失败')
            }), 401

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': user_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录过程中发生错误: {str(e)}'
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token不能为空'
            }), 400

        # 验证token
        status, username, message = AuthUtils.validate_auth_token(token)

        if status == 'success':
            return jsonify({
                'success': True,
                'message': 'Token验证成功',
                'data': {
                    'username': username,
                    'valid': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': message,
                'data': {
                    'valid': False
                }
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token验证过程中发生错误: {str(e)}'
        }), 500