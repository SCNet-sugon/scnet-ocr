---
name: scnet-ocr
description: 将图片中的文字、身份证、银行卡、营业执照、发票等信息识别并提取出来。本技能应在用户需要 OCR 识别图片中的文字，或识别身份证、银行卡、营业执照、增值税发票、出租车票、火车票、航空行程单、机动车销售统一发票时使用。
version: 1.0.0
author: SCNet
license: MIT
tags:
  - OCR
  - 证件识别
  - 发票识别
  - 文字提取
input:
  - ocrType : 识别类型，可选值见下文
  - filePath : 待识别图片的本地路径
output: 结构化的 JSON 数据，包含识别结果和置信度
---
# Sugon-Scnet 通用 OCR 技能

本技能封装了 Sugon-Scnet 通用 OCR 服务，通过单一接口即可调用 10 种识别能力，高效提取文字及票据信息。

## 功能特性

- **通用文字识别**：提取图片中的全部文字，支持横竖版及坐标定位。
- **个人证照**：识别大陆身份证（姓名、身份证号等）、银行卡（卡号、银行等）。
- **行业资质**：识别营业执照（统一社会信用代码、企业名称等）。
- **财务票据**：覆盖增值税发票、出租车票、火车票、航空行程单、机动车销售统一发票，自动提取关键字段。

## 前置配置

> **⚠️ 重要**：使用前需要申请 Scnet API Token

### 申请 API Token

1. 访问 [Scnet 官网](https://www.scnet.cn) 注册/登录
2. 在控制台申请 API 密钥（格式：`sc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
3. 复制密钥备用

### 配置 Token

**方式一：让 AI 配置**

> “帮我配置 Scnet OCR，Token 是：`xxx`”

**方式二：手动配置**
1. 在技能目录下创建 `config/.env` 文件，内容如下：
```ini
# =====  Sugon-Scnet OCR API 配置 =====
# 申请地址：https://www.scnet.cn
SCNET_API_KEY=your_scnet_api_key_here

# API 基础地址（一般无需修改）
SCNET_API_BASE=https://api.scnet.cn/api/llm/v1
```

### Token 更新

Token 过期后调用会返回 401 或 403 错误。更新方法：重新申请 Token 并替换 config/.env 中的 SCNET_API_KEY。

---
### 使用方法

### 参数说明

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| ocrType | string | 是 | 识别类型枚举。必须为以下之一：<br>• GENERAL（通用文字）<br>• ID_CARD（大陆身份证）<br>• BANK_CARD（银行卡）<br>• BUSINESS_LICENSE（营业执照）<br>• VAT_INVOICE（增值税发票）<br>• VAT_ROLL_INVOICE（增值税卷票）<br>• TAXI_INVOICE（出租车发票）<br>• TRAIN_TICKET（火车票）<br>• AIRPORT_TICKET（航空运输电子客票行程单）<br>• VEHICLE_SALE_INVOICE（机动车销售统一发票） |
| filePath | string | 是 | 待识别图片的本地绝对路径。支持 jpg、png、pdf 等常见格式。 |

### 命令行调用示例

```bash
python .claude/skills/sugon-scnet-ocr/scripts/main.py VAT_INVOICE /path/to/invoice.jpg
```

### 在 AI 对话中使用

用户可以说：

- “帮我识别这张身份证，图片在 /Users/name/Downloads/id.jpg”
- “提取这张发票的信息，路径是 /Users/name/Downloads/fapiao.png”
- “OCR 这个图片里的文字，图片在 /Users/name/Desktop/text.png”

AI 会根据 description 中的关键词自动触发本技能。

### 配置选项

编辑 `config/.env` 文件：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| SCNET_API_KEY | 必需 | Scnet API 密钥 |
| SCNET_API_BASE | https://api.scnet.cn/api/llm/v1 | API 基础地址（一般无需修改） |

### 输出

- 标准输出：识别结果的 JSON 数据，结构与 API 文档一致，位于 `data` 字段内。
- 识别结果位于 data[0].result[0].elements 中，具体字段取决于 ocrType。
- 错误信息：如果发生错误，会输出以 `错误:` 开头的友好提示。

### 故障排除

| 问题 | 解决方案 |
|------|----------|
| 配置文件不存在 | 创建 config/.env 并填入 Token（参考前置配置） |
| API Key 无效/过期 | 重新申请 Token 并更新 `.env` 文件 |
| 文件不存在 | 检查提供的文件路径是否正确 |
| 网络连接失败 | 检查网络连接或防火墙设置 |
| 不支持的文件类型 | 确保文件扩展名为允许的类型（参考 API 文档） |
| 401/403/Unauthorized | Token 无效或过期，重新申请并配置 |


