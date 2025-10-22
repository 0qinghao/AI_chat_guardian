# AI Chat Guardian (AI聊天守护者)

## 项目简介

AI Chat Guardian 是一个智能的敏感信息检测和保护工具，旨在帮助企业员工在使用外部AI工具时避免敏感信息泄露。

## 功能特性

- 🔍 **多层检测机制**
  - 正则表达式规则检测（邮箱、电话、身份证、密钥、Token等）- 15+种类型
  - 自定义敏感词库匹配（6大类敏感信息）
  - **AI语义理解检测**（三种模式）：
    - ✨ 增强关键词模式（默认，无需额外依赖）
    - 🎯 零样本分类模式（最高准确率，需transformers）
    - 🔍 相似度匹配模式（最灵活，需sentence-transformers）

- 🛡️ **智能信息混淆**
  - 自动对检测到的敏感信息进行脱敏处理
  - 保持文本语义和结构的完整性
  - 支持自定义混淆策略

- ⚙️ **灵活配置**
  - YAML配置文件支持
  - 可自定义检测规则和敏感词库
  - 支持启用/禁用不同检测模块

- 💻 **友好界面**
  - 命令行界面（CLI）
  - 图形用户界面（GUI）- 可选

## 快速开始

### 安装

1. 克隆项目
```bash
git clone <repository-url>
cd AI_chat_guardian
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
# 基础版本（仅正则和规则检测）
pip install colorama pyyaml

# 完整版本（包含AI语义检测）
pip install -r requirements.txt
```

### 使用方法

#### 命令行模式

```bash
# 交互式检测
python main.py

# 检测文件内容
python main.py --file input.txt

# 批量检测
python main.py --batch-dir ./documents
```

#### GUI模式

```bash
python gui.py
```

#### Python API调用

```python
from src.guardian import ChatGuardian

guardian = ChatGuardian()
result = guardian.check_text("你的输入文本")

if result.has_sensitive:
    print(f"检测到 {result.count} 处敏感信息")
    print(f"安全文本: {result.safe_text}")
```

## 配置说明

编辑 `config/default_config.yaml` 来自定义检测规则：

```yaml
detection:
  enable_regex: true      # 启用正则检测
  enable_keyword: true    # 启用关键词检测
  enable_ai: false        # 启用AI语义检测（需要额外依赖）

obfuscation:
  email_mask: "***@***.com"
  phone_mask: "***-****-****"
  preserve_structure: true
```

## 项目结构

```
AI_chat_guardian/
├── src/
│   ├── detectors/          # 检测器模块
│   │   ├── regex_detector.py
│   │   ├── keyword_detector.py
│   │   └── ai_detector.py
│   ├── obfuscators/        # 混淆器模块
│   │   └── obfuscator.py
│   ├── guardian.py         # 核心守护类
│   └── utils.py            # 工具函数
├── config/                 # 配置文件
│   ├── default_config.yaml
│   └── sensitive_keywords.yaml
├── tests/                  # 测试文件
├── main.py                 # CLI入口
├── gui.py                  # GUI入口
└── requirements.txt        # 依赖列表
```

## 安全说明

- ✅ 所有检测和处理均在本地完成
- ✅ 不会上传任何数据到外部服务器
- ✅ AI模型使用本地部署（如启用）
- ✅ 支持离线运行

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
