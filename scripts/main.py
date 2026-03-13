#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sugon-Scnet 通用 OCR 技能主脚本
接收命令行参数：ocrType filePath
输出：识别结果的 JSON
"""

import os
import sys
import json
import requests
import mimetypes
from pathlib import Path

# 获取技能根目录（脚本所在目录的上一级）
SKILL_ROOT = Path(__file__).parent.parent.absolute()
ENV_FILE = SKILL_ROOT / "config" / ".env"

def load_config():
    """从 .env 文件加载配置，若文件不存在则抛出友好错误"""
    if not ENV_FILE.exists():
        error_msg = (
            "\n===============================================\n"
            "Scnet OCR 配置文件不存在\n"
            "===============================================\n"
            "请按以下步骤配置：\n\n"
            "1. 申请 Scnet API Token：\n"
            "   访问 https://www.scnet.cn 注册并获取密钥\n\n"
            "2. 配置 Token：\n"
            "   告诉 AI：\"帮我配置 Scnet OCR，Token 是：xxx\"\n\n"
            "   或手动配置：\n"
            f"   cp {SKILL_ROOT}/config/.env.example {ENV_FILE}\n"
            f"   nano {ENV_FILE}\n"
            "   设置 SCNET_API_KEY=你的密钥\n"
        )
        sys.exit(error_msg)

    config = {}
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[key] = value

    # 检查必要配置
    api_key = config.get('SCNET_API_KEY', '')
    if not api_key or api_key == 'your_scnet_api_key_here':
        error_msg = (
            "\n===============================================\n"
            "Scnet API Key 未配置\n"
            "===============================================\n"
            "请按以下步骤配置：\n\n"
            "1. 申请 Scnet API Token：\n"
            "   访问 https://www.scnet.cn 注册并获取密钥\n\n"
            "2. 配置 Token：\n"
            f"   编辑 {ENV_FILE}\n"
            "   设置 SCNET_API_KEY=你的密钥\n"
        )
        sys.exit(error_msg)

    config.setdefault('SCNET_API_BASE', 'https://api.scnet.cn/api/llm/v1')
    return config

def recognize(ocr_type, file_path, config):
    """调用 Scnet OCR API 进行识别"""
    api_base = config['SCNET_API_BASE']
    api_key = config['SCNET_API_KEY']
    url = f"{api_base}/ocr/recognize"

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        sys.exit(f"错误: 文件不存在 - {file_path}")

    # 自动检测 MIME 类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, mime_type)
            }
            data = {
                'ocrType': ocr_type
            }
            response = requests.post(url, headers=headers, data=data, files=files, timeout=60)
    except Exception as e:
        sys.exit(f"网络请求失败: {str(e)}")

    if response.status_code != 200:
        # 针对 401/403 给出明确提示
        if response.status_code in (401, 403):
            error_msg = (
                "\n===============================================\n"
                "Scnet API Token 无效或已过期\n"
                "===============================================\n"
                f"HTTP 状态码: {response.status_code}\n\n"
                "解决方法：\n"
                "1. 访问 https://www.scnet.cn 重新申请 Token\n"
                "2. 告诉 AI：\"我的 Scnet Token 过期了，新的 Token 是：xxx\"\n"
                f"   或手动更新 {ENV_FILE}\n"
            )
            sys.exit(error_msg)
        else:
            sys.exit(f"HTTP 错误 {response.status_code}: {response.text}")

    try:
        result = response.json()
    except Exception:
        sys.exit(f"响应不是有效的 JSON: {response.text}")

    # 检查业务状态码
    if result.get('code') != '0':
        sys.exit(f"API 错误 {result.get('code')}: {result.get('msg')}")

    # 输出 data 部分（识别结果）
    #print(json.dumps(result.get('data', []), ensure_ascii=False, indent=2))
    # 获取 data 部分
    data = result.get('data', [])

    # 移除每个识别项中的 confidence 字段（优化点）
    for file_result in data:
        if 'result' in file_result and isinstance(file_result['result'], list):
            for item in file_result['result']:
                item.pop('confidence', None)  # 删除 confidence，不存在则忽略

    # 输出处理后的数据
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    if len(sys.argv) != 3:
        print("用法: python main.py <ocrType> <filePath>")
        print("ocrType 可选值: GENERAL, ID_CARD, BANK_CARD, BUSINESS_LICENSE, VAT_INVOICE, VAT_ROLL_INVOICE, TAXI_INVOICE, TRAIN_TICKET, AIRPORT_TICKET, VEHICLE_SALE_INVOICE")
        sys.exit(1)

    ocr_type = sys.argv[1]
    file_path = sys.argv[2]

    config = load_config()
    recognize(ocr_type, file_path, config)

if __name__ == '__main__':
    main()