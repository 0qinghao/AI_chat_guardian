# 使用指南

## 目录
1. [快速开始](#快速开始)
2. [命令行使用](#命令行使用)
3. [GUI使用](#gui使用)
4. [API调用](#api调用)
5. [配置说明](#配置说明)
6. [自定义规则](#自定义规则)
7. [常见问题](#常见问题)

---

## 快速开始

### 1. 安装依赖

#### 基础版本（推荐）
仅使用正则和关键词检测，无需深度学习库：

```bash
pip install colorama pyyaml
```

#### 完整版本
包含AI语义检测功能：

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python tests/test_basic.py
```

### 3. 启动应用

**命令行模式：**
```bash
python main.py
```

**GUI模式：**
```bash
python gui.py
```

---

## 命令行使用

### 交互式模式

直接运行程序进入交互模式：

```bash
python main.py
```

然后粘贴或输入文本，按Enter键后再输入一个空行结束输入。

### 检测文件

```bash
python main.py -f examples/sample_text_with_pii.txt
```

### 保存安全文本

```bash
python main.py -f input.txt -o safe_output.txt
```

### 批量检测目录

```bash
python main.py -b ./examples
```

### 使用自定义配置

```bash
python main.py -c config/my_config.yaml
```

### 详细输出模式

```bash
python main.py -v
```

---

## GUI使用

### 启动GUI

```bash
python gui.py
```

### GUI功能说明

1. **输入区域（左侧）**
   - 直接输入或粘贴待检测文本
   - 支持多行文本
   - 可通过"加载文件"按钮导入文件

2. **操作按钮**
   - 🔍 检测敏感信息：开始检测
   - 🗑️ 清空：清除所有内容
   - 📂 加载文件：从文件导入文本

3. **输出区域（右侧）**
   - 显示混淆后的安全文本
   - 蓝色背景表示处理后的内容

4. **输出操作**
   - 📋 复制到剪贴板：快速复制结果
   - 💾 保存文件：保存到本地文件

5. **检测详情（底部）**
   - 显示检测到的敏感信息类型
   - 显示位置和置信度
   - 按类型分组显示

---

## API调用

### 基本使用

```python
from src import ChatGuardian

# 初始化
guardian = ChatGuardian()

# 检测文本
text = "请联系张三，邮箱：zhangsan@company.com"
result = guardian.check_text(text)

# 检查结果
if result.has_sensitive:
    print(f"发现 {result.detection_count} 处敏感信息")
    print(f"安全文本: {result.safe_text}")
else:
    print("文本安全")
```

### 访问检测详情

```python
result = guardian.check_text(text)

for detection in result.detections:
    print(f"类型: {detection['type']}")
    print(f"内容: {detection['content']}")
    print(f"位置: {detection['position']}")
    print(f"置信度: {detection['confidence']}")
```

### 获取统计信息

```python
stats = guardian.get_statistics(result)
print(f"总检测数: {stats['total_detections']}")
print(f"按类型统计: {stats['by_type']}")
```

### 检测文件

```python
result = guardian.check_file('path/to/file.txt')
```

### 不自动混淆

```python
result = guardian.check_text(text, auto_obfuscate=False)
# result.safe_text 将等于 result.original_text
```

---

## 配置说明

### 配置文件位置

默认配置文件：`config/default_config.yaml`

### 主要配置项

#### 检测配置

```yaml
detection:
  enable_regex: true      # 启用正则检测
  enable_keyword: true    # 启用关键词检测
  enable_ai: false        # 启用AI检测（需要额外依赖）
  confidence_threshold: 0.7  # 置信度阈值
```

#### 混淆配置

```yaml
obfuscation:
  preserve_structure: true    # 保留部分结构
  email_mask: "***@***.com"
  phone_mask: "***-****-****"
  show_type_hint: true        # 显示类型提示
```

#### 输出配置

```yaml
output:
  verbose: true           # 详细输出
  color_highlight: true   # 颜色高亮
  log_level: "INFO"       # 日志级别
```

---

## 自定义规则

### 添加自定义关键词

编辑 `config/sensitive_keywords.yaml`：

```yaml
# 添加新分类
my_custom_category:
  - 关键词1
  - 关键词2
  - 关键词3
```

### 创建自定义配置

1. 复制默认配置：
```bash
cp config/default_config.yaml config/my_config.yaml
```

2. 修改配置文件

3. 使用自定义配置：
```bash
python main.py -c config/my_config.yaml
```

### 编程方式添加关键词

```python
from src import ChatGuardian

guardian = ChatGuardian()

# 动态添加关键词
guardian.keyword_detector.add_keywords(
    category='my_category',
    keywords=['keyword1', 'keyword2']
)
```

---

## 常见问题

### Q1: 如何提高检测准确率？

**A:** 
1. 启用所有检测模块
2. 根据实际需求添加自定义关键词
3. 调整置信度阈值（降低会增加检测数量但可能误报）

### Q2: 混淆后的文本还能恢复吗？

**A:** 不能。混淆是单向的，无法恢复原始内容。这是为了安全考虑。

### Q3: 可以检测图片中的文本吗？

**A:** 当前版本不支持。需要先使用OCR工具提取文本后再检测。

### Q4: AI检测器为什么不工作？

**A:** 
1. 确认已安装完整依赖：`pip install transformers torch`
2. 在配置中启用：`detection.enable_ai: true`
3. 首次运行会下载模型，需要网络连接

### Q5: 如何处理特定格式的密钥？

**A:** 可以在 `src/detectors/regex_detector.py` 中添加自定义正则模式：

```python
'my_key_type': {
    'pattern': re.compile(r'your_regex_pattern'),
    'confidence': 0.9
}
```

### Q6: 命令行没有颜色显示？

**A:** 
1. 安装 colorama：`pip install colorama`
2. 或使用 `--no-color` 参数禁用颜色

### Q7: 如何批量处理多个文件？

**A:** 使用批量模式：
```bash
python main.py -b /path/to/directory
```

### Q8: 检测速度太慢怎么办？

**A:** 
1. 禁用AI检测（最耗时）
2. 减少自定义关键词数量
3. 处理前先分段文本

### Q9: 误报太多怎么办？

**A:** 
1. 提高置信度阈值（config中的 confidence_threshold）
2. 禁用某些检测类型
3. 修改正则表达式使其更精确

### Q10: 可以集成到其他应用吗？

**A:** 可以。使用Python API：

```python
from src import ChatGuardian

guardian = ChatGuardian()
result = guardian.check_text(your_text)

if result.has_sensitive:
    # 使用 result.safe_text
    pass
```

---

## 技术支持

如有问题，请：
1. 查看日志文件
2. 使用 `-v` 参数获取详细输出
3. 提交Issue到GitHub仓库

---

## 更新日志

### v1.0.0 (2025-10-22)
- 初始版本发布
- 支持正则、关键词、AI三种检测模式
- 提供CLI和GUI两种界面
- 支持文件和批量检测
