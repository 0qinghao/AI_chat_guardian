# LLM检测器 - API版本使用指南

## 🎯 概述

项目已升级支持**在线API版LLM检测器**，无需本地部署大模型，使用免费的云端API即可进行敏感内容检测。

---

## 📋 支持的API提供商

### 🥇 1. 智谱AI (推荐)
- **免费额度**: 100万tokens/月（约50万汉字）
- **速度**: ⚡⚡⚡ 极快
- **模型**: GLM-4-Flash（Flash专为速度优化）
- **注册**: https://open.bigmodel.cn
- **优点**: 
  - 国内访问快速稳定
  - 中文理解能力强
  - 免费额度充足
  - 注册简单

### 🥈 2. 硅基流动
- **免费额度**: 每日免费调用
- **速度**: ⚡⚡⚡ 快
- **模型**: Qwen2.5等
- **注册**: https://siliconflow.cn
- **优点**: 多模型选择、专注推理优化

---

## 🚀 快速开始

### 步骤1: 注册并获取API密钥

以**智谱AI**为例（推荐）：

1. 访问 https://open.bigmodel.cn
2. 注册/登录账号
3. 进入"API密钥"页面
4. 创建新的API密钥
5. 复制密钥（格式类似：`a1b2c3d4e5f6...`）

### 步骤2: 配置API密钥

**方法1: 使用环境变量（推荐）**

```bash
# Windows (PowerShell)
$env:ZHIPU_API_KEY="your_api_key_here"

# Windows (CMD)
set ZHIPU_API_KEY=your_api_key_here

# Linux/Mac
export ZHIPU_API_KEY="your_api_key_here"
```

**方法2: 使用 .env 文件**

```bash
# 1. 复制示例文件
copy .env.example .env

# 2. 编辑 .env 文件，填写API密钥
notepad .env

# 3. 在 .env 中添加:
ZHIPU_API_KEY=your_api_key_here
```

**方法3: 直接修改配置文件（不推荐）**

编辑 `config/default_config.yaml`：

```yaml
llm_detector:
  type: api  # 使用API模式
  api:
    provider: zhipu
    api_key: "your_api_key_here"  # 不安全，不推荐
```

### 步骤3: 启用API检测器

编辑 `config/default_config.yaml`：

```yaml
llm_detector:
  type: api        # 重要：设置为 'api'
  enable: true     # 启用LLM检测器
  threshold: 0.7
  
  api:
    provider: zhipu          # 选择提供商
    api_key: ""              # 留空，从环境变量读取
    model: ""                # 留空使用默认模型
    base_url: ""             # 留空使用默认地址
```

### 步骤4: 安装依赖

```bash
pip install requests
# 或
pip install -r requirements.txt
```

### 步骤5: 测试

```bash
# 直接测试API检测器
python src/detectors/llm_detector_api.py

# 或使用GUI
python gui.py
```

---

## ⚙️ 配置说明

### 完整配置示例

```yaml
llm_detector:
  # 检测器类型: 'local' (本地Ollama) 或 'api' (在线API)
  type: api
  enable: true
  threshold: 0.7
  
  # 本地Ollama配置（type=local时使用）
  local:
    base_url: http://localhost:11434
    model: gemma3:4b
  
  # 在线API配置（type=api时使用）
  api:
    # API提供商: 'zhipu', 'siliconflow'
    provider: zhipu
    
    # API密钥（优先从环境变量读取）
    api_key: ""
    
    # 模型名称（留空使用默认模型）
    # zhipu默认: glm-4-flash
    # siliconflow默认: Qwen/Qwen2.5-7B-Instruct
    model: ""
    
    # 自定义API地址（可选）
    base_url: ""
```

### API密钥优先级

系统按以下顺序查找API密钥：

1. 环境变量 `{PROVIDER}_API_KEY` (如 `ZHIPU_API_KEY`)
2. 环境变量 `LLM_API_KEY`
3. 配置文件中的 `llm_detector.api.api_key`

---

## 🔄 切换API提供商

### 切换到硅基流动

```yaml
llm_detector:
  type: api
  api:
    provider: siliconflow
    model: "Qwen/Qwen2.5-7B-Instruct"  # 可选
```

```bash
# 设置环境变量
$env:SILICONFLOW_API_KEY="your_api_key"
```

---

## 🆚 本地模式 vs API模式

### 本地模式 (Ollama)
```yaml
llm_detector:
  type: local
  local:
    model: gemma3:4b
```

**优点**: 
- ✅ 完全免费
- ✅ 数据不出本地
- ✅ 无网络限制

**缺点**:
- ❌ 需要安装Ollama
- ❌ 需要下载模型（几GB）
- ❌ 占用本地资源
- ❌ 速度较慢

### API模式 (在线)
```yaml
llm_detector:
  type: api
  api:
    provider: zhipu
```

**优点**:
- ✅ 无需本地部署
- ✅ 速度极快
- ✅ 不占用本地资源
- ✅ 易于分享给同事

**缺点**:
- ❌ 需要网络连接
- ❌ 数据传输到云端
- ❌ 有使用限额（但免费额度充足）

---

## 💡 推荐配置方案

### 方案1: 个人使用（推荐智谱AI）
```yaml
llm_detector:
  type: api
  enable: true
  api:
    provider: zhipu
    # 其他留空，使用默认值
```

**适用场景**: 
- 个人开发测试
- 小团队使用
- 轻量级检测任务

### 方案2: 团队使用
```yaml
llm_detector:
  type: api
  enable: true
  api:
    provider: siliconflow  # 多模型选择
```

**适用场景**:
- 多人协作
- 需要不同模型对比
- 中等规模检测

### 方案3: 对数据安全要求高
```yaml
llm_detector:
  type: local
  enable: true
  local:
    model: gemma3:4b
```

**适用场景**:
- 处理敏感数据
- 内网环境
- 对隐私要求极高

---

## 🐛 常见问题

### Q1: API密钥配置后提示"未设置"？

**解决方法**:
1. 检查环境变量是否正确设置：
   ```bash
   # PowerShell
   $env:ZHIPU_API_KEY
   ```
2. 确认环境变量名与提供商匹配（大写）
3. 重启终端或IDE

### Q2: API调用失败，提示401错误？

**原因**: API密钥无效或过期

**解决方法**:
1. 检查API密钥是否正确复制
2. 登录提供商网站确认密钥状态
3. 重新生成密钥

### Q3: 检测速度慢？

**可能原因**:
- 网络延迟
- 模型负载高

**解决方法**:
1. 切换到更快的提供商（智谱AI的Flash模型）
2. 减少检测文本长度
3. 尝试不同时间段

### Q4: 免费额度用完怎么办？

**解决方法**:
1. 切换到其他提供商
2. 等待下月额度重置
3. 降低检测频率
4. 切换回本地模式

### Q5: 同事无法使用，提示API密钥错误？

**原因**: 每个人需要自己的API密钥

**解决方法**:
1. 让同事自行注册账号获取密钥
2. 或使用团队账号共享密钥（通过.env文件）

---

## 📊 性能对比

| 提供商 | 速度 | 中文能力 | 免费额度 | 推荐度 |
|--------|------|----------|----------|--------|
| 智谱AI | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 100万tokens/月 | ⭐⭐⭐⭐⭐ |
| 硅基流动 | ⚡⚡⚡ | ⭐⭐⭐⭐ | 每日免费 | ⭐⭐⭐⭐ |
| 本地Ollama | ⚡ | ⭐⭐⭐ | 无限制 | ⭐⭐⭐ |

---

## 📞 技术支持

如有问题，请：
1. 查看日志输出（设置 `LOG_LEVEL: DEBUG`）
2. 查看 [API提供商文档]
3. 提交Issue到项目仓库

---

## 🔐 安全提示

⚠️ **重要**:
- 不要将API密钥提交到Git仓库
- 不要在代码中硬编码密钥
- `.env` 文件已加入 `.gitignore`
- 使用环境变量是最安全的方式
- 定期轮换API密钥

---

## 📝 总结

推荐配置（最佳实践）：

```bash
# 1. 设置环境变量
$env:ZHIPU_API_KEY="your_api_key"

# 2. 修改配置文件
# config/default_config.yaml
llm_detector:
  type: api
  enable: true
  api:
    provider: zhipu

# 3. 运行
python gui.py
```

祝使用愉快！🎉
