from auth_routes import auth_bp
from llm_routes import llm_bp
from flask import Flask, request, jsonify
from tool.auth_storage import AuthUtils

app = Flask(__name__)

# 不需要验证token的路由列表
EXCLUDED_ROUTES = {
    '/auth/login',
    '/auth/verify-token',
    # 可以添加其他不需要验证的路由
}

@app.before_request
def check_auth():
    # 跳过OPTIONS请求（CORS预检请求）
    if request.method == 'OPTIONS':
        return

    # 检查是否在排除列表中
    if request.path in EXCLUDED_ROUTES:
        return

    # 获取token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({
            'success': False,
            'message': '缺少认证token'
        }), 401

    # 移除Bearer前缀（如果有）
    if token.startswith('Bearer '):
        token = token[7:]

    # 验证token
    status, username, message = AuthUtils.validate_auth_token(token)

    if status != 'success':
        return jsonify({
            'success': False,
            'message': message or 'Token验证失败'
        }), 401

    # 将用户名添加到request对象中，方便后续使用
    request.username = username
    request.token = token

# 注册认证路由
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(llm_bp, url_prefix='/llm')

if __name__ == '__main__':
    app.run(debug=True, port=25432)