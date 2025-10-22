# 开发文档

## 项目架构

### 目录结构

```
AI_chat_guardian/
├── src/                      # 源代码
│   ├── detectors/            # 检测器模块
│   │   ├── __init__.py
│   │   ├── regex_detector.py      # 正则检测器
│   │   ├── keyword_detector.py    # 关键词检测器
│   │   └── ai_detector.py         # AI检测器
│   ├── obfuscators/          # 混淆器模块
│   │   ├── __init__.py
│   │   └── obfuscator.py          # 混淆器
│   ├── __init__.py
│   ├── guardian.py           # 核心守护类
│   └── utils.py              # 工具函数
├── config/                   # 配置文件
│   ├── default_config.yaml
│   └── sensitive_keywords.yaml
├── tests/                    # 测试文件
│   └── test_basic.py
├── examples/                 # 示例文件
├── docs/                     # 文档
│   ├── USAGE.md
│   └── DEVELOPMENT.md
├── main.py                   # CLI入口
├── gui.py                    # GUI入口
├── requirements.txt          # 依赖列表
└── README.md
```

---

## 核心模块说明

### 1. 检测器模块 (detectors)

#### RegexDetector
基于正则表达式的检测器，识别结构化的敏感信息。

**支持的检测类型：**
- 邮箱地址
- 手机号（中国）
- 固定电话
- 身份证号（18位）
- IPv4地址
- API密钥
- JWT Token
- 信用卡号
- 银行卡号
- URL密钥参数
- AWS密钥
- 数据库连接字符串
- 私钥

**关键方法：**
```python
def detect(text: str) -> List[DetectionResult]
```

#### KeywordDetector
基于关键词匹配的检测器。

**关键方法：**
```python
def detect(text: str) -> List[KeywordMatch]
def add_keywords(category: str, keywords: List[str])
```

#### AIDetector
基于AI模型的语义检测器（可选）。

**关键方法：**
```python
def detect(text: str, threshold: float) -> List[SemanticMatch]
def is_available() -> bool
```

### 2. 混淆器模块 (obfuscators)

#### Obfuscator
负责对检测到的敏感信息进行混淆处理。

**混淆策略：**
- 完全掩码：用固定字符替换
- 部分掩码：保留部分结构（如邮箱保留域名后缀）
- 类型提示：显示信息类型

**关键方法：**
```python
def obfuscate(text: str, detections: List) -> tuple
def create_mapping(detections: List, text: str) -> Dict
```

### 3. 核心守护类 (guardian)

#### ChatGuardian
整合所有检测和混淆模块的核心类。

**关键方法：**
```python
def check_text(text: str, auto_obfuscate: bool) -> GuardianResult
def check_file(file_path: str, auto_obfuscate: bool) -> GuardianResult
def get_statistics(result: GuardianResult) -> Dict
```

**数据结构：**
```python
@dataclass
class GuardianResult:
    original_text: str
    safe_text: str
    has_sensitive: bool
    detection_count: int
    detections: List[Dict]
    obfuscation_details: List[Dict]
    warnings: List[str]
```

---

## 扩展开发

### 添加新的检测类型

1. 在 `regex_detector.py` 中添加新模式：

```python
def _init_patterns(self):
    self.patterns = {
        # ... 现有模式 ...
        
        # 新增模式
        'new_pattern': {
            'pattern': re.compile(r'your_regex'),
            'confidence': 0.9
        }
    }
```

2. 在 `obfuscator.py` 中添加混淆规则：

```python
def _init_rules(self):
    self.rules = {
        # ... 现有规则 ...
        
        'new_pattern': ObfuscationRule(
            type='new_pattern',
            mask_pattern='[新类型已隐藏]',
            show_hint=True
        )
    }
```

### 实现自定义检测器

创建新的检测器类：

```python
from typing import List
from dataclasses import dataclass

@dataclass
class CustomDetectionResult:
    type: str
    content: str
    start: int
    end: int
    confidence: float

class CustomDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect(self, text: str) -> List[CustomDetectionResult]:
        results = []
        # 实现检测逻辑
        return results
```

集成到 `ChatGuardian`：

```python
class ChatGuardian:
    def _init_detectors(self):
        # ... 现有检测器 ...
        self.custom_detector = CustomDetector()
    
    def check_text(self, text: str, auto_obfuscate: bool = True):
        # ... 现有逻辑 ...
        custom_results = self.custom_detector.detect(text)
        all_detections.extend(custom_results)
```

### 添加新的混淆策略

在 `Obfuscator` 类中扩展：

```python
def _generate_obfuscation(self, detection, original: str) -> str:
    detection_type = detection.type
    
    # 自定义混淆逻辑
    if detection_type == 'my_custom_type':
        return self._custom_mask(original)
    
    # 默认处理
    return super()._generate_obfuscation(detection, original)

def _custom_mask(self, original: str) -> str:
    # 实现自定义混淆
    return "***"
```

---

## 测试

### 运行测试

```bash
python tests/test_basic.py
```

### 添加测试用例

在 `tests/` 目录下创建新的测试文件：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ChatGuardian

def test_my_feature():
    guardian = ChatGuardian()
    text = "测试文本"
    result = guardian.check_text(text)
    assert result.detection_count == expected_count
```

---

## 性能优化建议

### 1. 正则表达式优化
- 使用编译后的正则对象
- 避免回溯过多的复杂模式
- 使用非捕获组 `(?:...)` 而非捕获组 `(...)`

### 2. 关键词检测优化
- 使用Trie树或Aho-Corasick算法（大量关键词时）
- 预处理文本（统一大小写、去除特殊字符）

### 3. AI检测优化
- 批处理多个文本
- 使用更轻量的模型
- 缓存模型加载结果

### 4. 通用优化
- 并行处理多个检测器（使用线程池）
- 对长文本分段处理
- 缓存重复检测的结果

---

## 依赖管理

### 核心依赖
```
colorama>=0.4.6  # 彩色终端输出
pyyaml>=6.0      # YAML配置文件解析
```

### 可选依赖（AI功能）
```
transformers>=4.35.0  # Hugging Face Transformers
torch>=2.0.0          # PyTorch
sentencepiece>=0.1.99 # 分词器
```

### 开发依赖
```
pytest>=7.0.0         # 测试框架
black>=23.0.0         # 代码格式化
flake8>=6.0.0         # 代码检查
```

---

## 代码风格

遵循 PEP 8 标准：
- 使用4个空格缩进
- 行长度限制为88字符（Black默认）
- 使用类型注解
- 编写docstring

示例：

```python
def function_name(param1: str, param2: int) -> bool:
    """
    函数简短描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        返回值说明
    """
    # 实现
    return True
```

---

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

MIT License - 详见 LICENSE 文件

---

## 联系方式

- 项目地址：[GitHub仓库]
- 问题反馈：[Issues]
- 邮件：[联系邮箱]
