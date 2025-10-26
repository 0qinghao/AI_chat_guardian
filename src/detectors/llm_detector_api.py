"""
LLM在线API检测器
支持多个免费API提供商：智谱AI、硅基流动等
"""
import logging
import json
import re
import time
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


# 尝试加载.env文件
def load_dotenv():
    """简单的.env文件加载器"""
    try:
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value and not value.startswith('#') and key not in os.environ:
                            os.environ[key] = value
    except Exception:
        pass  # 忽略加载错误


# 自动加载.env文件
load_dotenv()


@dataclass
class LLMMatch:
    """LLM检测结果"""
    text: str  # 敏感文本
    category: str  # 类别
    start: int  # 起始位置
    end: int  # 结束位置
    confidence: float  # 置信度
    reason: str  # 检测理由


class LLMDetectorAPI:
    """基于在线API的LLM检测器"""

    # 支持的API提供商配置
    PROVIDERS = {
        'zhipu': {
            'name': '智谱AI',
            'base_url': 'https://open.bigmodel.cn/api/paas/v4',
            'default_model': 'glm-4-flash',
            'models': ['glm-4-flash', 'glm-4-air', 'glm-4'],
            'format': 'openai'  # OpenAI兼容格式
        },
        'siliconflow': {
            'name': '硅基流动',
            'base_url': 'https://api.siliconflow.cn/v1',
            'default_model': 'Qwen/Qwen2.5-7B-Instruct',
            'models': ['Qwen/Qwen2.5-7B-Instruct', 'Qwen/Qwen2.5-14B-Instruct'],
            'format': 'openai'
        }
    }

    def __init__(self, provider: str = 'zhipu', api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化LLM API检测器
        
        Args:
            provider: API提供商 ('zhipu', 'siliconflow')
            api_key: API密钥（优先从环境变量读取）
            model: 模型名称（为空则使用默认模型）
            base_url: 自定义API地址（可选）
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider.lower()

        # 验证提供商
        if self.provider not in self.PROVIDERS:
            available = ', '.join(self.PROVIDERS.keys())
            raise ValueError(f"不支持的提供商: {provider}，可用选项: {available}")

        provider_config = self.PROVIDERS[self.provider]

        # 设置API密钥（优先级：参数 > 环境变量）
        self.api_key = api_key or self._get_api_key_from_env()
        if not self.api_key:
            self.logger.warning(f"未设置API密钥，请在环境变量或配置中设置")

        # 设置模型
        self.model = model or provider_config['default_model']

        # 设置API地址
        self.base_url = base_url or provider_config['base_url']

        # 设置格式
        self.api_format = provider_config['format']

        self.last_raw_response = ""  # 保存最后一次原始响应，用于调试

        self.logger.info(f"初始化LLM API检测器: {provider_config['name']} ({self.model})")

    def _get_api_key_from_env(self) -> Optional[str]:
        """从环境变量获取API密钥"""
        # 尝试多个可能的环境变量名
        env_keys = [
            f'{self.provider.upper()}_API_KEY',  # ZHIPU_API_KEY
            f'{self.provider}_API_KEY',  # zhipu_API_KEY
            'LLM_API_KEY',  # 通用
            'OPENAI_API_KEY'  # OpenAI兼容
        ]

        for key in env_keys:
            value = os.getenv(key)
            if value:
                self.logger.debug(f"从环境变量 {key} 获取API密钥")
                return value

        return None

    def detect(self, text: str, threshold: float = 0.7) -> List[LLMMatch]:
        """
        使用在线LLM API检测敏感信息
        
        Args:
            text: 待检测文本
            threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        if len(text.strip()) < 10:
            return []

        if not self.api_key:
            self.logger.error("API密钥未设置，无法进行检测")
            return []

        try:
            start_time = time.time()
            self.logger.info(f"开始LLM API检测 ({self.PROVIDERS[self.provider]['name']})...")

            results = self._call_api(text, threshold)

            elapsed_time = time.time() - start_time
            self.logger.info(f"LLM API检测完成，耗时: {elapsed_time:.2f}秒，检测到 {len(results)} 项")

            return results
        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            self.logger.error(f"LLM API检测失败 (耗时: {elapsed_time:.2f}秒): {e}")
            return []

    def _build_prompt(self, text: str) -> str:
        """构建检测提示词"""
        return f"""你是一个专业的敏感信息检测系统。可识别文本中的敏感信息。

**敏感信息类别：**
1. financial（财务信息）：金额、营收、利润、成本、预算等
2. personnel（人员信息）：员工姓名、薪资、联系方式、人员安排等
3. strategy（战略信息）：商业计划、战略规划、竞争策略、机密文件等
4. technical（技术信息）：代码、密钥、密码、系统架构、技术方案等
5. customer（客户信息）：客户数据、合同信息、订单详情等

**检测要求：**
- 如果发现敏感信息，返回JSON格式的结果
- 每个检测项包含：text（敏感内容，必须与原文完全一致）、category（类别）
- 如果没有敏感信息，返回空数组

**待检测文本：**
"{text}"

若检测到敏感信息，请严格按照以下JSON格式返回结果：
{{"detections":[{{"text":"敏感内容(必须与原文字符级一致)","category":"financial"}}]}}

若无敏感信息，返回：
{{"detections":[]}}

只返回JSON，不要包含其他解释。需严格遵守JSON格式，注意检查括号成对。"""

    def _call_api(self, text: str, threshold: float) -> List[LLMMatch]:
        """调用API进行检测"""
        if self.api_format == 'openai':
            return self._call_openai_format_api(text, threshold)
        else:
            raise ValueError(f"不支持的API格式: {self.api_format}")

    def _call_openai_format_api(self, text: str, threshold: float) -> List[LLMMatch]:
        """调用OpenAI格式的API"""
        try:
            import requests
        except ImportError:
            self.logger.error("请安装 requests 库: pip install requests")
            return []

        try:
            url = f"{self.base_url}/chat/completions"

            headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

            payload = {
                'model': self.model,
                'messages': [{
                    'role': 'user',
                    'content': self._build_prompt(text)
                }],
                'temperature': 0.1,  # 低温度，更确定性
                'max_tokens': 512,  # 限制输出长度
                'stream': False
            }

            self.logger.debug(f"调用API: {url}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # 提取响应内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                self.last_raw_response = content
                self.logger.debug(f"API原始响应: {content[:200]}...")
                return self._parse_response(content, text, threshold)
            else:
                self.logger.warning("API响应格式异常")
                return []

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    self.logger.error(f"错误详情: {error_detail}")
                except:
                    self.logger.error(f"响应内容: {e.response.text[:200]}")
            return []
        except Exception as e:
            self.logger.error(f"API调用失败: {e}")
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

                # confidence 字段可选，默认 0.8
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

                        self.logger.debug(f"检测到: [{match.category}] {match.text[:30]}... " f"(置信度: {match.confidence:.2f})")
                    else:
                        self.logger.warning(f"⚠️ 无法在原文中定位: '{sensitive_text[:50]}...'")

            return matches

        except json.JSONDecodeError as e:
            self.logger.warning(f"无法解析JSON响应: {e}")
            self.logger.debug(f"原始内容: {content[:200]}...")
            return []
        except Exception as e:
            self.logger.error(f"解析响应失败: {e}")
            return []

    def _fuzzy_match(self, llm_text: str, original_text: str) -> tuple:
        """
        模糊匹配：当LLM输出的文本在原文中找不到时，尝试找到相似的片段
        
        Returns:
            (匹配的文本, 起始位置, 结束位置) 或 (None, -1, -1)
        """
        # 提取数字
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

        window_size = len(llm_text) + 20

        for i in range(len(original_text) - window_size + 1):
            window = original_text[i:i + window_size]
            score = sum(1 for kw in keywords if kw in window)

            if score > best_score:
                best_score = score
                best_match = window
                best_start = i
                best_end = i + window_size

        # 如果找到了包含至少一半关键词的片段
        if best_score >= len(keywords) / 2:
            if best_match:
                # 优化边界
                first_kw_pos = len(best_match)
                last_kw_pos = 0

                for kw in keywords:
                    pos = best_match.find(kw)
                    if pos != -1:
                        first_kw_pos = min(first_kw_pos, pos)
                        last_kw_pos = max(last_kw_pos, pos + len(kw))

                margin = 5
                start_offset = max(0, first_kw_pos - margin)
                end_offset = min(len(best_match), last_kw_pos + margin)

                optimized_match = best_match[start_offset:end_offset].strip()
                optimized_start = best_start + start_offset
                optimized_end = optimized_start + len(optimized_match)

                return optimized_match, optimized_start, optimized_end

        return None, -1, -1

    def is_available(self) -> bool:
        """检查API是否可用"""
        if not self.api_key:
            return False

        try:
            import requests
            # 简单的健康检查（可以根据不同API调整）
            return True
        except ImportError:
            return False

    def get_info(self) -> Dict:
        """获取检测器信息"""
        provider_config = self.PROVIDERS[self.provider]
        return {
            'provider': self.provider,
            'provider_name': provider_config['name'],
            'model': self.model,
            'base_url': self.base_url,
            'available': self.is_available(),
            'has_api_key': bool(self.api_key)
        }

    print("\n" + "=" * 60)
