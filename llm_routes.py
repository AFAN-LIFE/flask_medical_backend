from flask import Blueprint, request, jsonify
from flask import Flask, request, Response, stream_with_context
import time

# 创建蓝图
llm_bp = Blueprint('llm', __name__)


# 或者更简单的版本（直接返回文本流）：
@llm_bp.route('/abstract_generate', methods=['POST'])
def abstract_generate():
    data = request.get_json()
    query = data.get('query', '')
    print(f"Received query: {query}")

    def generate_stream():
        response_text = f"正在为您生成关于'{query}'的文献综述...\n\n"
        response_text += "这是一段模拟的流式响应内容，实际应用中会连接真实的大模型API。"

        for char in response_text:
            yield char
            time.sleep(0.1)  # 控制流式速度

    return Response(stream_with_context(generate_stream()), mimetype='text/plain')
