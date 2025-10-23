# AI Chat Guardian (AI聊天守护者)# AI Chat Guardian# AI Chat Guardian (AI聊天守护者)



一个智能的敏感信息检测和保护工具,帮助您在使用AI聊天服务时保护隐私和敏感数据。



## 🌟 主要特性一个用于检测和混淆敏感信息的智能守护工具，帮助您安全地使用AI聊天服务。## 项目简介



- **🔍 多层检测机制**

  - 正则表达式：快速检测标准格式（邮箱、电话、身份证、API密钥等15+种类型）

  - 关键词检测：上下文感知的敏感词库匹配（商业机密、技术资料、财务信息等6大类）## 🌟 主要特性AI Chat Guardian 是一个智能的敏感信息检测和保护工具，旨在帮助企业员工在使用外部AI工具时避免敏感信息泄露。

  - LLM语义理解：基于Ollama的本地大语言模型检测（85-90%准确率，完全本地化，隐私保护）



- **🛡️ 智能信息混淆**

  - 自动对检测到的敏感信息进行脱敏处理- **多层检测**：正则表达式 + 关键词 + AI语义分析## 功能特性

  - 保持文本语义和结构的完整性

  - 支持自定义混淆策略- **智能混淆**：自动识别并混淆敏感信息



- **⚙️ 灵活配置**- **高准确率**：改进版检测器准确率达 80%+（微调后可达 95%+）- 🔍 **多层检测机制**

  - 图形界面实时切换检测方案（快速/平衡/精确模式）

  - 支持多种LLM模型选择（qwen2、llama3、mistral等）- **易于集成**：简单的API，支持CLI和GUI  - 正则表达式规则检测（邮箱、电话、身份证、密钥、Token等）- 15+种类型

  - YAML配置文件支持自定义规则

- **数据收集**：内置数据收集功能，支持模型微调  - 自定义敏感词库匹配（6大类敏感信息）

- **💻 友好界面**

  - 命令行界面（CLI）适合批量处理  - **AI语义理解检测**（三种模式）：

  - 图形用户界面（GUI）适合交互使用

  - 实时显示检测结果和详细信息## 📦 安装    - ✨ 增强关键词模式（默认，无需额外依赖）



## 📦 快速开始    - 🎯 零样本分类模式（最高准确率，需transformers）



### 1. 安装项目```bash    - 🔍 相似度匹配模式（最灵活，需sentence-transformers）



```bash# 克隆项目

# 克隆项目

git clone <repository-url>git clone https://github.com/0qinghao/AI_chat_guardian.git- 🛡️ **智能信息混淆**

cd AI_chat_guardian

cd AI_chat_guardian  - 自动对检测到的敏感信息进行脱敏处理

# 安装Python依赖

pip install -r requirements.txt  - 保持文本语义和结构的完整性

```

# 安装依赖  - 支持自定义混淆策略

### 2. 安装Ollama（可选，用于LLM检测）

pip install -r requirements.txt

Ollama是本地运行的LLM服务，完全免费且隐私安全。

```- ⚙️ **灵活配置**

**Windows系统：**

1. 访问 https://ollama.com/download  - YAML配置文件支持

2. 下载并安装Windows版本

3. 安装后会自动启动服务## 🚀 快速开始  - 可自定义检测规则和敏感词库



**下载模型：**  - 支持启用/禁用不同检测模块

```bash

# 推荐：轻量级模型，3GB### 命令行模式

ollama pull qwen2.5:3b

- 💻 **友好界面**

# 或者：标准模型，4.4GB

ollama pull qwen2:7b```bash  - 命令行界面（CLI）



# 或者：大型模型，8.5GB，准确度更高# 交互模式  - 图形用户界面（GUI）- 可选

ollama pull qwen2.5:14b

```python main.py



**验证安装：**## 快速开始

```bash

ollama list  # 查看已安装模型# 检测单个文本

```

python main.py -t "公司Q3营收5000万元"### 安装

### 3. 启动应用



**方式一：图形界面（推荐）**

```bash# 检测文件1. 克隆项目

python gui.py

```python main.py -f your_file.txt```bash

- 点击"⚙️ 配置检测器"按钮选择检测方案

- 在左侧输入框输入或粘贴文本```git clone <repository-url>

- 点击"🔍 检测并混淆"查看结果

cd AI_chat_guardian

**方式二：命令行**

```bash### GUI模式```

# 交互模式

python main.py



# 检测单个文本```bash2. 创建虚拟环境（推荐）

python main.py -t "公司Q3营收5000万元，CEO张三的手机是13812345678"

python gui.py```bash

# 检测文件

python main.py -f your_file.txt```python -m venv venv

```

venv\Scripts\activate  # Windows

**方式三：PowerShell脚本（Windows）**

```powershell### Python API```

.\start.ps1  # 自动检测并启动GUI

```



## ⚙️ 配置说明```python3. 安装依赖



### 检测方案选择from src.guardian import ChatGuardian```bash



在GUI界面点击"⚙️ 配置检测器"可以选择：# 基础版本（仅正则和规则检测）



- **快速模式**：仅正则表达式（毫秒级响应）# 初始化pip install colorama pyyaml

  - 适合：标准格式敏感信息检测

  - 优点：速度极快，无需额外资源guardian = ChatGuardian()

  

- **平衡模式**：正则 + 关键词（秒级响应）# 完整版本（包含AI语义检测）

  - 适合：日常使用，兼顾速度和准确性

  - 优点：支持上下文感知，误报率低# 检测文本pip install -r requirements.txt



- **精确模式**：正则 + 关键词 + LLM（3-5秒响应）result = guardian.check_text("公司Q3营收5000万元")```

  - 适合：重要文档检测

  - 优点：语义理解，检测隐晦表达的敏感信息

  - 要求：需要安装Ollama并下载模型

if result.has_sensitive:### 使用方法

### 配置文件

    print(f"检测到 {result.detection_count} 处敏感信息")

编辑 `config/default_config.yaml` 可自定义：

    print(f"安全文本: {result.safe_text}")#### 命令行模式

```yaml

detectors:```

  regex:

    enable: true  # 启用正则检测```bash

  

  keyword:## 📊 检测能力# 交互式检测

    enable: true  # 启用关键词检测

  python main.py

  llm_detector:

    enable: true  # 启用LLM检测支持检测以下类型的敏感信息：

    provider: "ollama"  # 提供商

    model: "qwen2:7b"  # 模型名称# 检测文件内容

    base_url: "http://localhost:11434"  # Ollama服务地址

    threshold: 0.7  # 置信度阈值- **财务信息**：营收、成本、利润、预算等python main.py --file input.txt

```

- **战略信息**：商业计划、战略规划、机密决策等

### 自定义敏感词库

- **客户信息**：客户资料、合同、商业关系等# 批量检测

编辑 `config/sensitive_keywords.yaml` 添加自定义关键词：

- **人事信息**：薪资、绩效、组织架构等python main.py --batch-dir ./documents

```yaml

categories:- **技术信息**：密码、密钥、API、配置等```

  custom_category:

    keywords:- **个人信息**：手机号、邮箱、身份证等

      - "自定义敏感词1"

      - "自定义敏感词2"#### GUI模式

    weight: 0.8

```## ⚙️ 配置



## 📊 检测类型```bash



### 正则表达式检测编辑 `config/default_config.yaml` 来自定义检测行为：python gui.py



- 个人信息：身份证、手机号、邮箱```

- 金融信息：银行卡、信用卡

- 技术密钥：API密钥、Token、私钥```yaml

- 网络信息：IP地址、URL

- 企业信息：统一社会信用代码detection:#### Python API调用

- ...等15+种类型

  enable_regex: true      # 正则检测

### 关键词检测

  enable_keyword: true    # 关键词检测```python

- 商业机密类：营收、利润、战略计划等

- 技术资料类：源代码、算法、架构设计等  enable_ai: true         # AI检测from src.guardian import ChatGuardian

- 财务信息类：财报、预算、成本等

- 客户信息类：客户名单、合同、商务条款等  

- 人事信息类：薪资、考核、内部通讯录等

- 项目信息类：项目计划、里程碑、资源分配等ai_model:guardian = ChatGuardian()



### LLM语义检测  detector_type: "improved"  # improved(推荐) 或 originalresult = guardian.check_text("你的输入文本")



- 检测隐晦表达的敏感信息  model_name: "bert-base-chinese"

- 理解上下文语义

- 识别潜在的信息泄露风险```if result.has_sensitive:

- 适应多种表达方式

    print(f"检测到 {result.count} 处敏感信息")

## 🔧 高级功能

## 📈 性能    print(f"安全文本: {result.safe_text}")

### 批量处理

```

```bash

# 处理目录下所有txt文件| 检测器版本 | 准确率 | 响应时间 |

for file in *.txt; do

    python main.py -f "$file" > "${file%.txt}_result.txt"|----------|--------|---------|## 配置说明

done

```| 基础版（regex + keyword） | 60% | <100ms |



### API集成| 改进版（混合检测） | 80% | <2s |编辑 `config/default_config.yaml` 来自定义检测规则：



```python| 微调后（fine-tuned） | 95%+ | <2s |

from src import ChatGuardian

```yaml

# 初始化守护者

guardian = ChatGuardian()## 🔧 高级功能detection:



# 检测文本  enable_regex: true      # 启用正则检测

text = "联系张总，手机：13812345678"

results = guardian.check_text(text)### 数据收集与模型微调  enable_keyword: true    # 启用关键词检测



# 混淆敏感信息  enable_ai: false        # 启用AI语义检测（需要额外依赖）

safe_text = guardian.obfuscate_text(text, results)

print(safe_text)  # 输出: "联系张总，手机：[手机号已隐藏]"参考 [数据收集工作流程](DATA_COLLECTION_WORKFLOW.md) 了解如何：

```

- 收集检测数据obfuscation:

### 日志配置

- 人工标注数据  email_mask: "***@***.com"

```python

from src import setup_logging- 训练自己的检测模型  phone_mask: "***-****-****"



# 设置日志级别- 部署微调后的模型  preserve_structure: true

setup_logging('DEBUG')  # DEBUG/INFO/WARNING/ERROR

``````



## 📝 项目结构### 性能测试



```## 项目结构

AI_chat_guardian/

├── main.py                 # CLI入口```bash

├── gui.py                  # GUI入口

├── requirements.txt        # Python依赖# 运行性能对比测试```

├── start.ps1              # Windows启动脚本

├── config/                # 配置文件python benchmark_detectors.pyAI_chat_guardian/

│   ├── default_config.yaml

│   └── sensitive_keywords.yaml```├── src/

├── src/                   # 源代码

│   ├── __init__.py│   ├── detectors/          # 检测器模块

│   ├── guardian.py        # 主检测器

│   ├── utils.py           # 工具函数## 📁 项目结构│   │   ├── regex_detector.py

│   ├── detectors/         # 检测器模块

│   │   ├── regex_detector.py│   │   ├── keyword_detector.py

│   │   ├── keyword_detector.py

│   │   └── llm_detector.py```│   │   └── ai_detector.py

│   └── obfuscators/       # 混淆器模块

│       └── obfuscator.pyAI_chat_guardian/│   ├── obfuscators/        # 混淆器模块

├── examples/              # 示例文件

└── tests/                 # 测试文件├── main.py                 # CLI入口│   │   └── obfuscator.py

```

├── gui.py                  # GUI入口│   ├── guardian.py         # 核心守护类

## 🤝 贡献

├── improved_ai_detector.py # 改进版AI检测器│   └── utils.py            # 工具函数

欢迎提交Issue和Pull Request！

├── data_collector.py       # 数据收集工具├── config/                 # 配置文件

## 📄 许可证

├── model_trainer.py        # 模型训练工具│   ├── default_config.yaml

MIT License

├── benchmark_detectors.py  # 性能测试│   └── sensitive_keywords.yaml

## 🙏 致谢

├── config/                 # 配置文件├── tests/                  # 测试文件

- [Ollama](https://ollama.com/) - 提供本地LLM支持

- [Qwen](https://github.com/QwenLM/Qwen) - 优秀的开源大语言模型├── src/                    # 核心代码├── main.py                 # CLI入口



## 📮 联系方式│   ├── guardian.py         # 主控制器├── gui.py                  # GUI入口



如有问题或建议，请提交Issue。│   ├── detectors/          # 检测器模块└── requirements.txt        # 依赖列表



---│   └── obfuscators/        # 混淆器模块```



**提示：** 首次使用LLM检测需要下载模型文件（3-9GB），请确保网络畅通和磁盘空间充足。├── docs/                   # 文档


└── examples/               # 示例文件## 安全说明

```

- ✅ 所有检测和处理均在本地完成

## 📚 文档- ✅ 不会上传任何数据到外部服务器

- ✅ AI模型使用本地部署（如启用）

- [使用指南](docs/USAGE.md) - 详细使用说明- ✅ 支持离线运行

- [数据收集工作流程](DATA_COLLECTION_WORKFLOW.md) - 模型训练指南

- [部署计划](DEPLOYMENT_PLAN.md) - 生产部署指南## 许可证



## 🤝 贡献MIT License



欢迎提交 Issue 和 Pull Request！## 贡献



## 📄 许可证欢迎提交 Issue 和 Pull Request！


MIT License

## 🙏 致谢

本项目使用了以下开源项目：
- transformers (Hugging Face)
- PyTorch
- PyYAML
- colorama

---

**注意**：本工具旨在辅助保护敏感信息，但不能替代完整的安全审计。请根据您的实际需求进行适当配置和测试。
