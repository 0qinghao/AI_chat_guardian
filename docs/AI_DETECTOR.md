# AI语义检测器技术文档

## 📋 概述

AI语义检测器是 AI Chat Guardian 的高级功能，通过深度学习模型进行语义理解，检测上下文中的敏感信息。

---

## 🎯 三种检测模式

### 1. 零样本分类模式（Zero-Shot Classification）✨ 推荐

**原理**：
- 使用预训练的BERT模型进行零样本分类
- 无需训练数据即可使用
- 基于自然语言理解判断文本类别

**优点**：
- ✅ 开箱即用，无需训练
- ✅ 准确率高
- ✅ 可处理未见过的表达方式

**缺点**：
- ❌ 需要下载模型（~400MB）
- ❌ 首次运行较慢
- ❌ 需要 transformers 库

**适用场景**：
- 企业部署
- 准确率要求高
- 有网络下载模型

**代码示例**：
```python
from src.detectors import AIDetector

# 初始化零样本分类器
detector = AIDetector(
    model_name="bert-base-chinese",
    use_gpu=False,
    mode="zero-shot"
)

# 检测文本
results = detector.detect("我们公司Q3营业额5.8亿元", threshold=0.7)
```

---

### 2. 相似度匹配模式（Similarity Matching）

**原理**：
- 使用句子向量模型（Sentence-BERT）
- 计算文本与敏感内容模板的余弦相似度
- 基于相似度阈值判断

**优点**：
- ✅ 可自定义敏感内容模板
- ✅ 灵活性高
- ✅ 速度较快

**缺点**：
- ❌ 需要下载模型（~120MB）
- ❌ 需要 sentence-transformers 库
- ❌ 模板设计影响效果

**适用场景**：
- 特定领域检测
- 需要自定义规则
- 对模板有明确认知

**代码示例**：
```python
detector = AIDetector(
    model_name="paraphrase-multilingual-MiniLM-L12-v2",
    use_gpu=False,
    mode="similarity"
)

results = detector.detect("讨论公司战略规划", threshold=0.75)
```

---

### 3. 增强关键词模式（Enhanced Keywords）🚀 默认

**原理**：
- 基于关键词匹配
- 智能权重计算
- 考虑关键词密度和文本长度

**优点**：
- ✅ 无需额外依赖
- ✅ 速度最快
- ✅ 占用内存小
- ✅ 离线可用

**缺点**：
- ❌ 准确率相对较低
- ❌ 可能误报
- ❌ 难以理解复杂语义

**适用场景**：
- 快速部署
- 资源受限环境
- 无法安装深度学习库

**代码示例**：
```python
detector = AIDetector(
    mode="keyword-enhanced"  # 或不指定，自动回退
)

results = detector.detect("员工薪资调整方案", threshold=0.6)
```

---

## 🔧 安装和配置

### 基础安装（增强关键词模式）

```bash
# 无需额外安装，使用项目基础依赖即可
pip install colorama pyyaml
```

### 零样本分类模式

```bash
# 安装深度学习库
pip install transformers torch

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 相似度匹配模式

```bash
# 安装句子向量库
pip install sentence-transformers

# 完整安装
pip install transformers torch sentence-transformers
```

---

## ⚙️ 配置文件

编辑 `config/default_config.yaml`：

```yaml
detection:
  enable_ai: true           # 启用AI检测
  confidence_threshold: 0.7  # 置信度阈值

ai_model:
  model_name: "bert-base-chinese"  # 模型名称
  use_gpu: false                   # 是否使用GPU
  mode: "zero-shot"                # 检测模式
  batch_size: 8                    # 批处理大小
  max_length: 512                  # 最大序列长度
```

---

## 📊 性能对比

| 模式 | 准确率 | 速度 | 内存占用 | 依赖 | 首次启动 |
|------|--------|------|----------|------|----------|
| 零样本分类 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ~500MB | transformers | ~10秒 |
| 相似度匹配 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ~200MB | sentence-transformers | ~5秒 |
| 增强关键词 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~10MB | 无 | <1秒 |

---

## 🎯 检测类别

AI检测器支持5大类敏感信息：

### 1. 财务信息 (financial)
**关键词**：金额、收入、成本、利润、预算、营业额、财报、资金、投资

**示例**：
```
✓ "我们公司Q3营业额5.8亿元，净利润8500万"
✓ "今年预算投入2亿元用于研发"
✓ "成本控制目标是降低15%"
```

### 2. 人员信息 (personnel)
**关键词**：员工、人员、名单、工资、薪资、招聘、离职、绩效

**示例**：
```
✓ "附件是员工薪资调整方案"
✓ "新员工名单已发送"
✓ "绩效考核结果将在下周公布"
```

### 3. 战略信息 (strategy)
**关键词**：战略、规划、计划、目标、策略、竞争、机密、内部

**示例**：
```
✓ "明年的战略规划重点是海外市场"
✓ "这是机密的竞争策略文档"
✓ "内部计划不要外传"
```

### 4. 技术信息 (technical)
**关键词**：代码、系统、服务器、数据库、架构、算法、技术方案

**示例**：
```
✓ "这是我们的系统架构设计"
✓ "数据库优化方案已完成"
✓ "核心算法的实现细节"
```

### 5. 客户信息 (customer)
**关键词**：客户、用户、合同、订单、商务、客户数据

**示例**：
```
✓ "客户名单和联系方式"
✓ "大客户合同金额统计"
✓ "用户数据分析报告"
```

---

## 💻 使用示例

### 基础使用

```python
from src import ChatGuardian

# 初始化（自动使用配置文件设置）
guardian = ChatGuardian()

# 检测文本
text = "我们公司Q3财务报表显示营业额5.8亿，净利润8500万"
result = guardian.check_text(text)

if result.has_sensitive:
    print(f"检测到 {result.detection_count} 处敏感信息")
    for detection in result.detections:
        print(f"- {detection['type']}: {detection['content']}")
```

### 手动启用AI检测

```python
from src.detectors import AIDetector

# 创建AI检测器
detector = AIDetector(
    model_name="bert-base-chinese",
    use_gpu=False,
    mode="zero-shot"
)

# 检测文本
results = detector.detect("这是公司的战略规划文档", threshold=0.7)

for match in results:
    print(f"类别: {match.category}")
    print(f"内容: {match.text}")
    print(f"置信度: {match.confidence:.2f}")
```

### 批量检测

```python
# 检测多个句子
texts = [
    "我们的营业额增长了15%",
    "员工薪资调整方案",
    "新的技术架构设计",
    "天气真好啊"  # 安全文本
]

detector = AIDetector(mode="zero-shot")

for text in texts:
    results = detector.detect(text, threshold=0.7)
    if results:
        print(f"✗ {text}")
        for r in results:
            print(f"  → {r.category} ({r.confidence:.2f})")
    else:
        print(f"✓ {text}")
```

---

## 🔬 高级功能

### 1. 自定义类别

```python
# 在 ai_detector.py 中添加新类别
detector.categories['custom_category'] = {
    'label': '自定义类别',
    'keywords': ['关键词1', '关键词2'],
    'templates': [
        '这段文本包含自定义内容',
        '讨论特定主题'
    ]
}
```

### 2. 调整阈值

```python
# 降低阈值，增加检测灵敏度（可能增加误报）
results = detector.detect(text, threshold=0.5)

# 提高阈值，减少误报（可能漏检）
results = detector.detect(text, threshold=0.85)
```

### 3. GPU加速

```python
# 启用GPU（需要CUDA）
detector = AIDetector(
    model_name="bert-base-chinese",
    use_gpu=True,  # 启用GPU
    mode="zero-shot"
)
```

### 4. 获取模型信息

```python
info = detector.get_model_info()
print(f"模式: {info['mode']}")
print(f"模型加载: {info['model_loaded']}")
print(f"支持类别: {info['categories']}")
```

---

## 🐛 故障排除

### 问题1：模型下载失败

**现象**：
```
ConnectionError: Can't reach 'huggingface.co'
```

**解决方案**：
1. 使用镜像站点
2. 手动下载模型文件
3. 使用代理

```python
# 方法1：设置镜像
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 方法2：使用本地模型
detector = AIDetector(
    model_name="/path/to/local/model",
    mode="zero-shot"
)
```

### 问题2：内存不足

**现象**：
```
RuntimeError: CUDA out of memory
```

**解决方案**：
```python
# 禁用GPU，使用CPU
detector = AIDetector(use_gpu=False)

# 或减少批处理大小
# 在 config.yaml 中设置
ai_model:
  batch_size: 4  # 减小批次
```

### 问题3：检测速度慢

**解决方案**：
1. 使用GPU加速
2. 切换到相似度模式
3. 使用增强关键词模式
4. 减少文本长度

```python
# 使用更快的模式
detector = AIDetector(mode="keyword-enhanced")
```

### 问题4：误报率高

**解决方案**：
```python
# 提高阈值
results = detector.detect(text, threshold=0.85)

# 或在配置中设置
detection:
  confidence_threshold: 0.85
```

---

## 📈 最佳实践

### 1. 生产环境推荐配置

```yaml
detection:
  enable_regex: true
  enable_keyword: true
  enable_ai: true
  confidence_threshold: 0.75

ai_model:
  model_name: "bert-base-chinese"
  use_gpu: true  # 如果有GPU
  mode: "zero-shot"
```

### 2. 资源受限环境

```yaml
detection:
  enable_regex: true
  enable_keyword: true
  enable_ai: false  # 禁用AI，节省资源
```

### 3. 高准确率要求

```yaml
detection:
  enable_ai: true
  confidence_threshold: 0.85  # 提高阈值

ai_model:
  mode: "zero-shot"
  use_gpu: true
```

### 4. 快速响应要求

```yaml
detection:
  enable_ai: true
  confidence_threshold: 0.6

ai_model:
  mode: "keyword-enhanced"  # 最快模式
```

---

## 🎓 技术细节

### 模型架构

**零样本分类**：
```
输入文本 → BERT编码器 → 分类层 → 多标签输出
         ↓
    [财务信息, 人员信息, ...]
```

**相似度匹配**：
```
输入文本 → Sentence-BERT → 文本向量
                            ↓
                         余弦相似度
                            ↓
敏感模板 → Sentence-BERT → 模板向量
```

### 置信度计算

**零样本分类**：
- 直接使用模型输出的概率值
- 范围：0.0 - 1.0

**相似度匹配**：
- 余弦相似度值
- 范围：-1.0 到 1.0（通常0.5-1.0）

**增强关键词**：
```python
confidence = base(0.5) + keyword_density * 0.3 + length_bonus * 0.1
```

---

## 📚 参考资源

- [Transformers文档](https://huggingface.co/docs/transformers)
- [Sentence-BERT论文](https://arxiv.org/abs/1908.10084)
- [零样本学习介绍](https://huggingface.co/tasks/zero-shot-classification)
- [BERT模型详解](https://arxiv.org/abs/1810.04805)

---

## 🔄 更新日志

### v1.0.0 (2025-10-22)
- ✅ 实现三种检测模式
- ✅ 支持5大类敏感信息
- ✅ 提供完整的配置选项
- ✅ 优化性能和准确率

---

**让AI检测更智能！🤖**
