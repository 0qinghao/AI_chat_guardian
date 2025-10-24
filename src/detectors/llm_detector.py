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
        self.last_raw_response = ""  # 保存最后一次原始响应，用于调试

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
        return f"""你是一个专业的敏感信息检测系统。可识别文本中的敏感信息。

**敏感信息类别：**
1. financial（财务信息）：金额、营收、利润、成本、预算等
2. personnel（人员信息）：员工姓名、薪资、联系方式、人员安排等
3. strategy（战略信息）：商业计划、战略规划、竞争策略、机密文件等
4. technical（技术信息）：代码、密钥、密码、系统架构、技术方案等
5. customer（客户信息）：客户数据、合同信息、订单详情等

**检测要求：**
- 如果发现敏感信息，返回JSON格式的结果
- 每个检测项包含：text（敏感内容）、category（类别）
- 如果没有敏感信息，返回空数组

**待检测文本：**
"{text}"

若检测到敏感信息，请严格按照以下JSON格式返回结果：
{{"detections":[{{"text":"sensitive content(必须与原文字符级一致)","category":"financial"}}]}}

若无敏感信息，返回：
{{"detections":[]}}

只返回JSON，不要包含其他解释。需严格遵守JSON格式，注意检查括号成对。"""

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
                        # 'stop': ['}}\n\n']  # 只在JSON结束后停止
                    }
                })

            response.raise_for_status()

            # 解析结果
            content = response.json().get('response', '').strip()
            self.last_raw_response = content  # 保存原始响应
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

                    if not sensitive_text:
                        continue

                    # 在原文中查找位置（精确匹配）
                    start = original_text.find(sensitive_text)
                    end = start + len(sensitive_text) if start != -1 else -1

                    # 如果直接找不到，尝试模糊匹配
                    if start == -1:
                        matched_text, match_start, match_end = self._fuzzy_match(sensitive_text, original_text)
                        if matched_text:
                            sensitive_text = matched_text
                            start = match_start
                            end = match_end
                            self.logger.debug(f"使用模糊匹配: '{sensitive_text[:30]}...'")

                    if start != -1 and end != -1:
                        match = LLMMatch(text=sensitive_text, category=det.get('category', 'unknown'), start=start, end=end, confidence=confidence, reason=det.get('reason', 'LLM检测'))
                        matches.append(match)

                        self.logger.debug(f"LLM检测到: [{match.category}] {match.text[:30]}... "
                                          f"(置信度: {match.confidence:.2f}, 位置: {start}-{end})")
                    else:
                        self.logger.warning(f"⚠️ 无法在原文中定位敏感内容: '{sensitive_text[:50]}...'")

            return matches

        except json.JSONDecodeError as e:
            self.logger.warning(f"无法解析LLM返回的JSON: {e}")
            self.logger.debug(f"原始内容: {content[:200]}...")
            return []
        except Exception as e:
            self.logger.error(f"解析LLM响应失败: {e}")
            self.logger.debug(f"详细错误: {type(e).__name__}: {str(e)}")
            return []

    def _fuzzy_match(self, llm_text: str, original_text: str) -> tuple:
        """
        模糊匹配：当LLM输出的文本在原文中找不到时，尝试找到相似的片段
        
        策略：
        1. 提取数字和关键词
        2. 在原文中查找包含这些关键信息的片段
        3. 返回最匹配的原文片段
        
        Args:
            llm_text: LLM输出的敏感文本
            original_text: 原始文本
            
        Returns:
            (匹配的文本, 起始位置, 结束位置) 或 (None, -1, -1)
        """
        import re

        # 提取数字（包括金额、百分比等）
        numbers = re.findall(r'\d+(?:\.\d+)?(?:[万亿千百]|%)?', llm_text)

        # 提取关键中文词（2个字符以上）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', llm_text)

        # 提取英文单词（3个字符以上）
        english_words = re.findall(r'[a-zA-Z]{3,}', llm_text)

        keywords = numbers + chinese_words + english_words

        if not keywords:
            return None, -1, -1

        # 在原文中查找包含最多关键词的片段
        best_match = None
        best_score = 0
        best_start = -1
        best_end = -1

        # 使用滑动窗口查找
        window_size = len(llm_text) + 20  # 稍微放宽一些

        for i in range(len(original_text) - window_size + 1):
            window = original_text[i:i + window_size]

            # 计算这个窗口包含多少关键词
            score = sum(1 for kw in keywords if kw in window)

            if score > best_score:
                best_score = score
                best_match = window
                best_start = i
                best_end = i + window_size

        # 如果找到了包含至少一半关键词的片段，则认为匹配成功
        if best_score >= len(keywords) / 2:
            # 优化边界：尝试缩小到更精确的范围
            if best_match:
                # 找到第一个关键词的位置
                first_kw_pos = len(best_match)
                last_kw_pos = 0

                for kw in keywords:
                    pos = best_match.find(kw)
                    if pos != -1:
                        first_kw_pos = min(first_kw_pos, pos)
                        last_kw_pos = max(last_kw_pos, pos + len(kw))

                # 稍微扩展边界，包含完整的词
                margin = 5
                start_offset = max(0, first_kw_pos - margin)
                end_offset = min(len(best_match), last_kw_pos + margin)

                optimized_match = best_match[start_offset:end_offset].strip()
                optimized_start = best_start + start_offset
                optimized_end = optimized_start + len(optimized_match)

                self.logger.debug(f"模糊匹配成功: 关键词匹配度 {best_score}/{len(keywords)}")
                return optimized_match, optimized_start, optimized_end

        return None, -1, -1

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
