# AI Chat Guardian - 快速演示

欢迎使用 AI Chat Guardian！这是一个保护您敏感信息的工具。

## 🚀 快速体验

### 方式1: 命令行交互模式（推荐新手）

```bash
python main.py
```

然后粘贴以下测试文本：

```
你好，我需要帮助分析一下代码。

我的联系方式是：zhangsan@company.com，电话：13812345678
数据库连接：mysql://user:pass123@10.0.1.100:3306/mydb
API密钥：AKIA1234567890ABCDEF

这是我们的财务报表数据，包含营业额和净利润信息。
```

按Enter后再输入一个空行结束输入，查看检测结果！

### 方式2: GUI图形界面（最简单）

```bash
python gui.py
```

1. 在左侧文本框粘贴内容
2. 点击"🔍 检测敏感信息"按钮
3. 在右侧查看安全的混淆文本
4. 点击"📋 复制到剪贴板"直接复制结果

### 方式3: 检测示例文件

```bash
# 检测包含个人信息的文件
python main.py -f examples/sample_text_with_pii.txt

# 检测包含密钥的文件
python main.py -f examples/sample_code_with_secrets.txt

# 检测公司敏感信息
python main.py -f examples/sample_company_confidential.txt

# 检测安全文本（无敏感信息）
python main.py -f examples/sample_safe_text.txt
```

### 方式4: 批量检测

```bash
python main.py -b examples
```

一次检测整个目录的所有文本文件！

## 📊 检测能力展示

### 可以检测的敏感信息类型：

✅ **个人信息**
- 邮箱地址：user@example.com
- 手机号：13812345678
- 身份证号：110101199001011234
- 银行卡号：6222021234567890123

✅ **技术信息**
- API密钥：sk-1234567890abcdef
- JWT Token：eyJhbGciOiJIUzI1NiI...
- AWS密钥：AKIA1234567890EXAMPLE
- 数据库连接：mysql://user:pass@host:3306/db
- IP地址：192.168.1.1
- SSH私钥：-----BEGIN PRIVATE KEY-----

✅ **公司信息（关键词）**
- 财务相关：财务报表、营业额、净利润、预算
- 人员相关：员工名单、薪资表、工号
- 战略相关：战略规划、商业计划、机密
- 客户相关：客户名单、合同金额
- 技术相关：内网IP、生产环境、服务器地址

## 💡 实际使用场景

### 场景1：询问ChatGPT代码问题

❌ **不安全的做法：**
```
我的代码连接数据库出错了：
mysql://admin:MyPassword123@10.0.1.100:3306/production_db
能帮我看看问题吗？
```

✅ **使用Guardian后：**
```
我的代码连接数据库出错了：
[数据库连接已隐藏]
能帮我看看问题吗？
```

### 场景2：分享工作内容

❌ **不安全的做法：**
```
我们公司Q3营业额5.8亿，净利润8500万，
负责人张伟（zhangwei@company.com）
```

✅ **使用Guardian后：**
```
我们公司Q3[财务信息已隐藏]5.8亿，[财务信息已隐藏]8500万，
负责人张伟（***@***.com）
```

## 🎯 三步使用流程

1. **输入** - 粘贴或输入待检查的文本
2. **检测** - 自动识别敏感信息
3. **使用** - 复制安全文本发送给AI工具

## ⚙️ 自定义配置

编辑 `config/default_config.yaml` 来调整检测行为：

```yaml
detection:
  enable_regex: true      # 正则检测
  enable_keyword: true    # 关键词检测
  enable_ai: false        # AI语义检测

obfuscation:
  show_type_hint: true    # 显示"[邮箱已隐藏]"等提示
  preserve_structure: true # 保留部分信息结构
```

添加自定义关键词到 `config/sensitive_keywords.yaml`：

```yaml
my_category:
  - 自定义关键词1
  - 自定义关键词2
```

## 📚 更多资源

- 📖 [详细使用指南](docs/USAGE.md)
- 🔧 [开发文档](docs/DEVELOPMENT.md)  
- 📝 [项目说明](README.md)
- ℹ️ [项目信息](PROJECT_INFO.md)

## 🎬 视频教程（建议录制）

1. **2分钟快速入门** - 展示基本使用
2. **5分钟完整教程** - 展示所有功能
3. **高级配置** - 自定义规则和扩展

## 💬 获取帮助

遇到问题？

1. 运行测试：`python tests/test_basic.py`
2. 查看详细日志：`python main.py -v`
3. 查看文档：`docs/USAGE.md`

## ⚠️ 重要提醒

1. 本工具在本地运行，不会上传任何数据
2. 检测不能100%覆盖所有情况，建议配合人工审核
3. 混淆后的内容无法恢复原文
4. 定期更新关键词库以提高准确性

---

**立即开始保护您的隐私！🛡️**

```bash
# Windows快速启动
.\start.ps1

# 或直接运行
python main.py    # 命令行
python gui.py     # 图形界面
```
