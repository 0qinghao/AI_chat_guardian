# AI Chat Guardian (AI聊天守护者)

一个智能的敏感信息检测和保护工具，帮助您在使用AI聊天服务时保护隐私和敏感数据。

## 🌟 主要特性

- **🔍 多层检测机制**
  - 正则表达式：快速检测标准格式（邮箱、电话、身份证、API密钥等15+种类型）
  - 关键词检测：上下文感知的敏感词库匹配（商业机密、技术资料、财务信息等6大类）
  - **LLM语义理解**：支持本地Ollama和在线API两种模式
    - 🏠 本地模式：基于Ollama的本地大语言模型（完全隐私）
    - ☁️ API模式：支持智谱AI、硅基流动等免费API（快速便捷）

- **🛡️ 智能信息混淆**
  - 自动对检测到的敏感信息进行脱敏处理
  - 保持文本语义和结构的完整性
  - 支持自定义混淆策略

- **⚙️ 灵活配置**
  - 图形界面实时切换检测方案（快速/平衡/精确模式）
  - 支持本地和云端LLM灵活切换
  - YAML配置文件支持自定义规则

- **💻 友好界面**
  - 命令行界面（CLI）适合批量处理
  - 图形用户界面（GUI）适合交互使用
  - 实时显示检测结果和详细信息

---

## 📦 快速开始

### 1. 安装项目

```bash
# 克隆项目
git clone https://github.com/0qinghao/AI_chat_guardian.git
cd AI_chat_guardian

# 安装基础依赖
pip install -r requirements.txt
```

### 2. 配置LLM检测器（二选一）

#### 方式A：使用在线API（✨推荐 - 快速便捷）

**优点**：无需本地部署、速度快、易于分享给同事

1. **注册智谱AI账号**：https://open.bigmodel.cn
2. **获取API密钥**：进入"API密钥"页面创建
3. **配置环境变量**：
   ```powershell
   # Windows PowerShell
   $env:ZHIPU_API_KEY="your_api_key_here"
   ```
4. **修改配置文件** `config/default_config.yaml`：
   ```yaml
   llm_detector:
     type: api  # 使用API模式
     enable: true
     api:
       provider: zhipu
   ```

📖 **详细配置请参考**：[LLM API使用指南](docs/LLM_API_使用指南.md)

#### 方式B：使用本地Ollama（🔒隐私优先）

**优点**：完全本地化、数据不出本地、无限制使用

1. **安装Ollama**：https://ollama.com/download
2. **下载模型**：
   ```bash
   ollama pull qwen2:7b
   ```
3. **修改配置文件** `config/default_config.yaml`：
   ```yaml
   llm_detector:
     type: local  # 使用本地模式
     enable: true
     local:
       model: qwen2:7b
   ```

### 3. 启动应用

#### 图形界面（推荐）
```bash
python gui.py
```

#### 命令行模式
```bash
# 交互模式
python main.py

# 检测单个文本
python main.py -t "公司Q3营收5000万元"

# 检测文件
python main.py -f your_file.txt
```

---

## ⚙️ 配置说明

### 检测方案选择

在GUI界面点击"⚙️ 配置检测器"可以选择：

- **快速模式**：仅正则表达式（毫秒级响应）
  - 适合：标准格式敏感信息检测
  - 优点：速度极快，无需额外资源

- **平衡模式**：正则 + 关键词（秒级响应）
  - 适合：日常使用，兼顾速度和准确性
  - 优点：支持上下文感知，误报率低

- **精确模式**：正则 + 关键词 + LLM（3-5秒响应）
  - 适合：重要文档检测
  - 优点：语义理解，检测隐晦表达的敏感信息
  - 要求：需要配置LLM（本地或API）

### LLM配置对比

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **API模式**<br>(智谱AI等) | ✅ 无需本地部署<br>✅ 速度快（1-2秒）<br>✅ 易于分享给同事<br>✅ 免费额度充足 | ❌ 需要网络连接<br>❌ 数据传输到云端<br>❌ 有使用限额 | • 个人/团队使用<br>• 快速部署<br>• 轻量级检测 |
| **本地模式**<br>(Ollama) | ✅ 完全隐私保护<br>✅ 无限制使用<br>✅ 离线可用<br>✅ 一次配置永久使用 | ❌ 需要安装配置<br>❌ 占用本地资源<br>❌ 速度较慢（3-5秒） | • 高隐私需求<br>• 内网环境<br>• 处理敏感数据 |

### 配置文件示例

编辑 `config/default_config.yaml`：

```yaml
detection:
  enable_regex: true      # 正则检测
  enable_keyword: true    # 关键词检测
  confidence_threshold: 0.7

llm_detector:
  type: api  # 'api' 或 'local'
  enable: true
  threshold: 0.7
  
  # API模式配置
  api:
    provider: zhipu  # 'zhipu', 'siliconflow'
    api_key: ""      # 留空从环境变量读取
    model: ""        # 留空使用默认模型
  
  # 本地模式配置
  local:
    base_url: http://localhost:11434
    model: qwen2:7b

obfuscation:
  email_mask: "***@***.com"
  phone_mask: "***-****-****"
  preserve_structure: true
```

### 自定义敏感词库

编辑 `config/sensitive_keywords.yaml`：

```yaml
categories:
  custom_category:
    keywords:
      - "自定义敏感词1"
      - "自定义敏感词2"
    weight: 0.8
```

---

## 📊 检测能力

支持检测以下类型的敏感信息：

### 个人信息
- 手机号、邮箱、身份证号
- 姓名、地址

### 金融信息
- 银行卡号、信用卡号
- 金额、营收、利润、成本

### 技术信息
- API密钥、Token、密码
- 私钥、证书
- 源代码片段

### 企业信息
- 商业计划、战略规划
- 客户信息、合同内容
- 人事信息、薪资数据
- 项目计划、预算

---

## 🔧 使用示例

### Python API

```python
from src.guardian import ChatGuardian

# 初始化
guardian = ChatGuardian()

# 检测文本
result = guardian.check_text("公司Q3营收5000万元，CEO张三的手机是13812345678")

if result.has_sensitive:
    print(f"检测到 {result.detection_count} 处敏感信息")
    print(f"安全文本: {result.safe_text}")
    
    # 查看详细检测结果
    for detection in result.detections:
        print(f"- [{detection['type']}] {detection['content']}")
```

### 命令行批量处理

```bash
# 处理目录下所有txt文件
for file in *.txt; do
    python main.py -f "$file" > "${file%.txt}_result.txt"
done
```

---

## 📁 项目结构

```
AI_chat_guardian/
├── main.py                     # CLI入口
├── gui.py                      # GUI入口
├── requirements.txt            # 依赖列表
├── config/                     # 配置文件
│   ├── default_config.yaml    # 主配置
│   └── sensitive_keywords.yaml # 敏感词库
├── src/                        # 源代码
│   ├── guardian.py            # 核心检测器
│   ├── utils.py               # 工具函数
│   ├── detectors/             # 检测器模块
│   │   ├── regex_detector.py  # 正则检测
│   │   ├── keyword_detector.py # 关键词检测
│   │   ├── llm_detector.py    # 本地LLM检测
│   │   └── llm_detector_api.py # API版LLM检测
│   └── obfuscators/           # 混淆器模块
│       └── obfuscator.py
├── docs/                       # 文档
│   └── LLM_API_使用指南.md    # API配置详细说明
└── examples/                   # 示例文件
```

---

## 🆚 版本对比

### v2.0 (当前) - API支持版本
- ✅ 支持在线API（智谱AI、硅基流动）
- ✅ 无需本地部署大模型
- ✅ 更快的检测速度（1-2秒）
- ✅ 易于团队分享和使用
- ✅ 免费额度充足

### v1.0 - 本地版本
- ✅ 完全本地化
- ✅ 数据隐私保护
- ❌ 需要安装Ollama
- ❌ 检测速度较慢（3-5秒）

---

## 🐛 常见问题

### Q: API模式下提示"API密钥未设置"？
**A**: 确保环境变量设置正确：
```powershell
# 检查是否设置
$env:ZHIPU_API_KEY

# 如果为空，重新设置
$env:ZHIPU_API_KEY="your_api_key"
```

### Q: 本地模式下LLM检测不可用？
**A**: 
1. 确认Ollama已安装并启动
2. 检查模型是否已下载：`ollama list`
3. 确认配置文件中 `type: local` 和模型名称正确

### Q: 如何切换API提供商？
**A**: 修改 `config/default_config.yaml`：
```yaml
llm_detector:
  api:
    provider: siliconflow  # 改为硅基流动
```
并设置对应的环境变量：`$env:SILICONFLOW_API_KEY="..."`

### Q: 免费API额度用完怎么办？
**A**: 
1. 切换到其他提供商
2. 等待下月额度重置
3. 切换回本地模式
4. 降低检测频率或仅在必要时使用LLM检测

---

## 🔐 安全提示

⚠️ **重要安全建议**：

- ✅ 不要将API密钥提交到Git仓库
- ✅ 使用环境变量存储密钥（最安全）
- ✅ 不要在代码中硬编码密钥
- ✅ `.env` 文件已加入 `.gitignore`
- ✅ 定期轮换API密钥
- ✅ 处理极度敏感数据时使用本地模式

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [Ollama](https://ollama.com/) - 提供本地LLM支持
- [智谱AI](https://open.bigmodel.cn) - 提供优秀的API服务
- [Qwen](https://github.com/QwenLM/Qwen) - 优秀的开源大语言模型

---

## 📮 联系方式

如有问题或建议，请提交Issue或查看[详细使用指南](docs/LLM_API_使用指南.md)。

---

**⭐ 推荐配置（最佳实践）**：

```bash
# 1. 设置API环境变量
$env:ZHIPU_API_KEY="your_api_key"

# 2. 启动GUI
python gui.py

# 3. 选择"精确模式"开始检测
```

祝使用愉快！🎉
