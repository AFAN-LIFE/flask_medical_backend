from flask import Flask
from auth_routes import auth_bp

app = Flask(__name__)

# 注册认证路由
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True, port=25432)