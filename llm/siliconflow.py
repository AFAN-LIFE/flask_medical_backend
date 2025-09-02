import base64
import requests, json
from config import SILICON_FLOW_TOKEN

# https://cloud.siliconflow.cn/models
sk = SILICON_FLOW_TOKEN

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_batch_dsv3_response(messages):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "stream": False,
        "max_tokens": 8192,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "messages": messages
    }
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json"
    }
    # 忽略 SSL 验证
    response = requests.post(url, json=payload, headers=headers, verify=False)
    return response.text

def get_batch_siliconflow_json_response(messages):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",
        "stream": False,
        "max_tokens": 5120,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json"
    }
    # 忽略 SSL 验证
    response = requests.post(url, json=payload, headers=headers, verify=False)
    return response.text


def get_stream_dsv3_response(messages, **kwargs):
    """
    调用硅基流动的流式 API
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/deepseek-ai/DeepSeek-V3",  # 指定模型
        "messages": messages,  # 对话历史
        "stream": True,  # 启用流式输出
        "max_tokens": 5120,  # 最大 token 数
        "temperature": 0.7,  # 温度参数
        "top_p": 0.7,  # top_p 参数
        "top_k": 50,  # top_k 参数
        "frequency_penalty": 0.5,  # 频率惩罚
        "n": 1  # 返回的候选数
    }
    # 发送请求并流式获取响应
    response = requests.post(url, json=payload, headers=headers, stream=True, verify=False)
    if response.status_code != 200:
        raise Exception(f"API 请求失败，状态码：{response.status_code}，错误信息：{response.text}")

    # 逐行读取流式响应
    for chunk in response.iter_lines():
        if chunk:
            # 解析 JSON 数据
            chunk_str = chunk.decode("utf-8").strip()
            if chunk_str.startswith("data:"):
                chunk_data = chunk_str[5:].strip()  # 去掉 "data: " 前缀
                if chunk_data == "[DONE]":  # 流式结束标志
                    break
                try:
                    chunk_json = json.loads(chunk_data)
                    content = chunk_json["choices"][0]["delta"].get("content", "")
                    yield content
                except json.JSONDecodeError:
                    continue

def get_batch_dsvl2_response(messages):
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "deepseek-ai/deepseek-vl2",
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": messages,
    }

    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json"
    }
    # 忽略 SSL 验证
    response = requests.post(url, json=payload, headers=headers, verify=False)
    return response.text

def get_stream_dsvl2_response(messages, **kwargs):
    """
    调用硅基流动的流式 API
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sk}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/deepseek-vl2",
        "stream": True,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "stop": [],
        "messages": messages
    }
    # 发送请求并流式获取响应
    response = requests.post(url, json=payload, headers=headers, stream=True, verify=False)
    if response.status_code != 200:
        raise Exception(f"API 请求失败，状态码：{response.status_code}，错误信息：{response.text}")

    # 逐行读取流式响应
    for chunk in response.iter_lines():
        if chunk:
            # 解析 JSON 数据
            chunk_str = chunk.decode("utf-8").strip()
            if chunk_str.startswith("data:"):
                chunk_data = chunk_str[5:].strip()  # 去掉 "data: " 前缀
                if chunk_data == "[DONE]":  # 流式结束标志
                    break
                try:
                    chunk_json = json.loads(chunk_data)
                    content = chunk_json["choices"][0]["delta"].get("content", "")
                    print(content)
                    yield content
                except json.JSONDecodeError:
                    continue