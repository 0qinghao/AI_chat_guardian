"""
正则表达式检测器
使用正则表达式检测常见的敏感信息模式
"""
import re
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """检测结果"""
    type: str  # 敏感信息类型
    content: str  # 检测到的内容
    start: int  # 起始位置
    end: int  # 结束位置
    confidence: float  # 置信度 (0-1)


class RegexDetector:
    """基于正则表达式的敏感信息检测器"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_patterns()

    def _init_patterns(self):
        """初始化正则表达式模式"""
        self.patterns = {
            # 邮箱地址
            'email': {
                'pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'confidence': 0.95
            },

            # 中国手机号
            'phone_cn': {
                'pattern': re.compile(r'\b1[3-9]\d{9}\b'),
                'confidence': 0.9
            },

            # 固定电话
            'phone_landline': {
                'pattern': re.compile(r'\b\d{3,4}-\d{7,8}\b'),
                'confidence': 0.85
            },

            # 中国身份证号（18位）
            'id_card_cn': {
                'pattern': re.compile(r'\b[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b'),
                'confidence': 0.95
            },

            # IPv4地址
            'ipv4': {
                'pattern': re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
                'confidence': 0.8
            },

            # API密钥模式（常见格式）
            'api_key': {
                'pattern': re.compile(r'\b[A-Za-z0-9]{32,64}\b'),
                'confidence': 0.6
            },

            # JWT Token
            'jwt_token': {
                'pattern': re.compile(r'\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b'),
                'confidence': 0.95
            },

            # 信用卡号
            'credit_card': {
                'pattern': re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),
                'confidence': 0.7
            },

            # 银行卡号（中国，16-19位）
            'bank_card': {
                'pattern': re.compile(r'\b\d{16,19}\b'),
                'confidence': 0.65
            },

            # URL中的密钥参数
            'url_secret': {
                'pattern': re.compile(r'(password|passwd|pwd|secret|token|key|api_key|apikey)=[A-Za-z0-9_\-]+', re.IGNORECASE),
                'confidence': 0.9
            },

            # AWS密钥
            'aws_key': {
                'pattern': re.compile(r'\b(AKIA[0-9A-Z]{16})\b'),
                'confidence': 0.95
            },

            # 数据库连接字符串
            'db_connection': {
                'pattern': re.compile(r'(mongodb|mysql|postgresql|redis)://[^\s]+', re.IGNORECASE),
                'confidence': 0.9
            },

            # Private Key
            'private_key': {
                'pattern': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                'confidence': 0.99
            },
        }

    def detect(self, text: str) -> List[DetectionResult]:
        """
        检测文本中的敏感信息
        
        Args:
            text: 待检测的文本
        
        Returns:
            检测结果列表
        """
        results = []

        for pattern_name, pattern_info in self.patterns.items():
            pattern = pattern_info['pattern']
            confidence = pattern_info['confidence']

            for match in pattern.finditer(text):
                # 对于低置信度的模式，进行额外验证
                if confidence < 0.8:
                    if not self._validate_match(pattern_name, match.group()):
                        continue

                result = DetectionResult(type=pattern_name, content=match.group(), start=match.start(), end=match.end(), confidence=confidence)
                results.append(result)

                self.logger.debug(f"检测到 {pattern_name}: {match.group()}")

        # 去重和排序
        results = self._deduplicate_results(results)
        results.sort(key=lambda x: x.start)

        return results

    def _validate_match(self, pattern_type: str, content: str) -> bool:
        """
        对低置信度匹配进行额外验证
        
        Args:
            pattern_type: 模式类型
            content: 匹配内容
        
        Returns:
            是否有效
        """
        # API密钥验证：检查是否看起来像真实的密钥
        if pattern_type == 'api_key':
            # 排除全数字或全字母
            if content.isdigit() or content.isalpha():
                return False
            # 检查字符多样性
            if len(set(content)) < 10:
                return False

        # 银行卡号验证：Luhn算法
        if pattern_type in ['bank_card', 'credit_card']:
            clean_num = content.replace(' ', '').replace('-', '')
            if not self._luhn_check(clean_num):
                return False

        return True

    def _luhn_check(self, card_number: str) -> bool:
        """Luhn算法验证银行卡号"""
        try:
            digits = [int(d) for d in card_number]
            checksum = 0
            for i, digit in enumerate(reversed(digits)):
                if i % 2 == 1:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
            return checksum % 10 == 0
        except:
            return False

    def _deduplicate_results(self, results: List[DetectionResult]) -> List[DetectionResult]:
        """
        去重：处理重叠的检测结果，保留置信度最高的
        
        Args:
            results: 检测结果列表
        
        Returns:
            去重后的结果列表
        """
        if not results:
            return results

        # 按位置排序
        sorted_results = sorted(results, key=lambda x: (x.start, -x.confidence))

        # 去重
        filtered = []
        for result in sorted_results:
            # 检查是否与已有结果重叠
            overlaps = False
            for existing in filtered:
                if self._is_overlap(result, existing):
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(result)

        return filtered

    def _is_overlap(self, r1: DetectionResult, r2: DetectionResult) -> bool:
        """判断两个检测结果是否重叠"""
        return not (r1.end <= r2.start or r1.start >= r2.end)
