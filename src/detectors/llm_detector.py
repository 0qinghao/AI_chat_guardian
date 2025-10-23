"""
LLM本地检测器 (基于Ollama)
使用本地大语言模型进行敏感信息检测
"""
import logging
import json
import re
import time
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class LLMMatch:
    """LLM检测结果"""
    text: str  # 敏感文本
    category: str  # 类别
    start: int  # 起始位置
    end: int  # 结束位置
    confidence: float  # 置信度
    reason: str  # 检测理由


class LLMDetector:
    """基于Ollama本地大语言模型的检测器"""

    def __init__(self, model: str = "qwen2:7b", base_url: str = "http://localhost:11434"):
        """
        初始化LLM检测器
        
        Args:
            model: Ollama模型名称 (如 qwen2:7b, llama3:8b)
            base_url: Ollama服务地址
        """
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.base_url = base_url.rstrip('/')

        self.logger.info(f"初始化LLM检测器: Ollama/{self.model}")

    def detect(self, text: str, threshold: float = 0.7) -> List[LLMMatch]:
        """
        使用本地LLM检测敏感信息
        
        Args:
            text: 待检测文本
            threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        if len(text.strip()) < 10:
            return []

        try:
            start_time = time.time()
            self.logger.info(f"开始LLM检测 (模型: {self.model})...")

            results = self._detect_ollama(text, threshold)

            elapsed_time = time.time() - start_time
            self.logger.info(f"LLM检测完成，耗时: {elapsed_time:.2f}秒，检测到 {len(results)} 项")

            return results
        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            self.logger.error(f"LLM检测失败 (耗时: {elapsed_time:.2f}秒): {e}")
            return []

    def _build_prompt(self, text: str) -> str:
        """构建检测提示词（英文版：企业防泄密场景 - 平衡版）"""
        return f"""You are a corporate data leak detector. Identify sensitive info in the text.

Categories:
- financial: money, revenue, profit, budget, salary
- personnel: employee name, ID, phone, email  
- strategy: confidential projects, business plans
- technical: passwords, keys, IPs, database URLs
- customer: client names, contracts, deals

Text: "{text}"

JSON format:
{{"detections":[{{"text":"sensitive content","category":"type"}}]}}

Output:"""

    def _detect_ollama(self, text: str, threshold: float) -> List[LLMMatch]:
        """使用Ollama本地模型检测"""
        try:
            import requests

            # API端点
            url = f"{self.base_url}/api/generate"

            # 调用API（优化参数以提升速度）
            self.logger.debug("正在调用Ollama API...")
            response = requests.post(
                url,
                json={
                    'model': self.model,
                    'prompt': self._build_prompt(text),
                    'stream': False,
                    'options': {
                        'temperature': 0.1,  # 低温度，更确定性
                        'top_p': 0.9,  # 降低随机性
                        'num_predict': 512,  # 限制最大输出token（加速）
                        'stop': ['}}\n\n']  # 只在JSON结束后停止
                    }
                })

            response.raise_for_status()

            # 解析结果
            content = response.json().get('response', '').strip()
            self.logger.debug(f"LLM原始响应: {content[:200]}...")
            return self._parse_response(content, text, threshold)

        except ImportError:
            self.logger.error("请安装 requests 库: pip install requests")
            return []
        except requests.exceptions.ConnectionError:
            self.logger.error("无法连接到Ollama服务，请确保Ollama已启动")
            self.logger.info("启动方法: 在终端运行 'ollama serve' 或 Ollama应用会自动启动服务")
            return []
        except Exception as e:
            self.logger.error(f"Ollama API调用失败: {e}")
            return []

    def _parse_response(self, content: str, original_text: str, threshold: float) -> List[LLMMatch]:
        """
        解析LLM返回的JSON结果
        
        Args:
            content: LLM返回的内容
            original_text: 原始文本
            threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        matches = []

        try:
            # 提取JSON部分（处理可能的markdown代码块）
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试提取花括号或方括号内容
                json_match = re.search(r'[\{\[].*[\}\]]', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = content

            # 解析JSON
            result = json.loads(json_str)

            # 提取检测结果 - 处理不同的JSON格式
            detections = []
            if isinstance(result, dict):
                detections = result.get('detections', [])
            elif isinstance(result, list):
                detections = result
            else:
                self.logger.warning(f"未知的JSON格式: {type(result)}")
                return []

            for det in detections:
                if not isinstance(det, dict):
                    continue

                # confidence 字段可选，默认 0.8（只要LLM返回就认为检测到）
                confidence = float(det.get('confidence', 0.8))

                if confidence >= threshold:
                    sensitive_text = det.get('text', '')

                    # 在原文中查找位置
                    start = original_text.find(sensitive_text)

                    if start != -1:
                        match = LLMMatch(text=sensitive_text,
                                         category=det.get('category', 'unknown'),
                                         start=start,
                                         end=start + len(sensitive_text),
                                         confidence=confidence,
                                         reason=det.get('reason', 'LLM检测'))
                        matches.append(match)

                        self.logger.debug(f"LLM检测到: [{match.category}] {match.text[:30]}... "
                                          f"(置信度: {match.confidence:.2f})")

            return matches

        except json.JSONDecodeError as e:
            self.logger.warning(f"无法解析LLM返回的JSON: {e}")
            self.logger.debug(f"原始内容: {content[:200]}...")
            return []
        except Exception as e:
            self.logger.error(f"解析LLM响应失败: {e}")
            self.logger.debug(f"详细错误: {type(e).__name__}: {str(e)}")
            return []

    def is_available(self) -> bool:
        """检查LLM检测器是否可用"""
        try:
            import requests
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_info(self) -> Dict:
        """获取检测器信息"""
        return {'provider': 'ollama', 'model': self.model, 'base_url': self.base_url, 'available': self.is_available()}


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 测试文本
    test_text = "公司Q3营收5000万元，API密钥sk-123456，员工张三的薪资为50万元/年"

    print("=" * 60)
    print("LLM本地检测器测试 (Ollama)")
    print("=" * 60)

    try:
        # 创建检测器
        detector = LLMDetector(model="qwen2:7b")

        # 检查服务状态
        if detector.is_available():
            print(f"✓ Ollama服务运行正常")
            print(f"✓ 使用模型: {detector.model}\n")

            # 执行检测
            print(f"待检测文本: {test_text}\n")
            print("正在检测... (可能需要较长时间)")

            start_time = time.time()
            results = detector.detect(test_text)
            elapsed_time = time.time() - start_time

            print(f"\n⏱️  检测耗时: {elapsed_time:.2f}秒")

            if results:
                print(f"\n✓ 检测到 {len(results)} 个敏感项：\n")
                for i, match in enumerate(results, 1):
                    print(f"{i}. [{match.category}] {match.text}")
                    print(f"   置信度: {match.confidence:.2%}")
                    print(f"   原因: {match.reason}")
                    print(f"   位置: {match.start}-{match.end}\n")
            else:
                print("\n✓ 未检测到敏感信息")
        else:
            print("✗ Ollama服务未启动")
            print("\n启动方法:")
            print("  1. 确保已安装Ollama: https://ollama.com/download")
            print("  2. Ollama会自动启动服务，或运行: ollama serve")
            print(f"  3. 下载模型: ollama pull qwen2:7b")

    except Exception as e:
        print(f"✗ 测试失败: {e}")

    print("\n" + "=" * 60)
