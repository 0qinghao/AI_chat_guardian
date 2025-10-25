"""
信息混淆器
对检测到的敏感信息进行脱敏处理
"""
import logging
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ObfuscationRule:
    """混淆规则"""
    type: str  # 信息类型
    mask_pattern: str  # 掩码模式
    show_hint: bool  # 是否显示类型提示


class Obfuscator:
    """敏感信息混淆器"""
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化混淆器
        
        Args:
            config: 混淆配置
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        self._init_rules()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {'preserve_structure': True, 'email_mask': '***@***.com', 'phone_mask': '***-****-****', 'id_card_mask': '******************', 'generic_mask': '[已隐藏]', 'show_type_hint': True}

    def _init_rules(self):
        """初始化混淆规则"""
        self.rules = {
            'email': ObfuscationRule(type='email', mask_pattern=self.config.get('email_mask', '***@***.com'), show_hint=self.config.get('show_type_hint', True)),
            'phone_cn': ObfuscationRule(type='phone', mask_pattern=self.config.get('phone_mask', '***-****-****'), show_hint=self.config.get('show_type_hint', True)),
            'phone_landline': ObfuscationRule(type='phone', mask_pattern=self.config.get('phone_mask', '***-****-****'), show_hint=self.config.get('show_type_hint', True)),
            'id_card_cn': ObfuscationRule(type='id_card', mask_pattern=self.config.get('id_card_mask', '******************'), show_hint=self.config.get('show_type_hint', True)),
            'ipv4': ObfuscationRule(type='ip', mask_pattern='***.***.***.***', show_hint=self.config.get('show_type_hint', True)),
            'api_key': ObfuscationRule(type='api_key', mask_pattern='[API_KEY_HIDDEN]', show_hint=self.config.get('show_type_hint', True)),
            'jwt_token': ObfuscationRule(type='token', mask_pattern='[TOKEN_HIDDEN]', show_hint=self.config.get('show_type_hint', True)),
            'credit_card': ObfuscationRule(type='credit_card', mask_pattern='****-****-****-****', show_hint=self.config.get('show_type_hint', True)),
            'bank_card': ObfuscationRule(type='bank_card', mask_pattern='****-****-****-****', show_hint=self.config.get('show_type_hint', True)),
            'url_secret': ObfuscationRule(type='secret', mask_pattern='[HIDDEN]', show_hint=self.config.get('show_type_hint', True)),
            'aws_key': ObfuscationRule(type='aws_key', mask_pattern='[AWS_KEY_HIDDEN]', show_hint=self.config.get('show_type_hint', True)),
            'db_connection': ObfuscationRule(type='db_connection', mask_pattern='[DB_CONNECTION_HIDDEN]', show_hint=self.config.get('show_type_hint', True)),
            'private_key': ObfuscationRule(type='private_key', mask_pattern='[PRIVATE_KEY_HIDDEN]', show_hint=self.config.get('show_type_hint', True)),
        }

    def obfuscate(self, text: str, detections: List[Any]) -> tuple:
        """
        混淆文本中的敏感信息
        
        Args:
            text: 原始文本
            detections: 检测结果列表（可以是DetectionResult或KeywordMatch）
        
        Returns:
            (混淆后的文本, 混淆详情列表)
        """
        if not detections:
            return text, []

        # 按位置排序（从后往前处理，避免位置偏移）
        sorted_detections = sorted(detections, key=lambda x: x.start, reverse=True)

        obfuscated_text = text
        obfuscation_details = []

        for detection in sorted_detections:
            # 获取原始内容
            original_content = text[detection.start:detection.end]

            # 生成混淆内容
            obfuscated_content = self._generate_obfuscation(detection, original_content)

            # 替换
            obfuscated_text = (obfuscated_text[:detection.start] + obfuscated_content + obfuscated_text[detection.end:])

            # 记录混淆详情
            detail = {
                'type': getattr(detection, 'type', getattr(detection, 'category', 'unknown')),
                'original': original_content,
                'obfuscated': obfuscated_content,
                'position': (detection.start, detection.end),
                'confidence': getattr(detection, 'confidence', 0.0)
            }
            obfuscation_details.append(detail)

            self.logger.debug(f"混淆 {detail['type']}: {original_content} -> {obfuscated_content}")

        return obfuscated_text, obfuscation_details

    def _generate_obfuscation(self, detection: Any, original: str) -> str:
        """
        生成混淆内容
        
        Args:
            detection: 检测结果
            original: 原始内容
        
        Returns:
            混淆后的内容
        """
        detection_type = getattr(detection, 'type', getattr(detection, 'category', 'unknown'))

        # 获取混淆规则
        rule = self.rules.get(detection_type)

        # 特殊处理：保留部分结构以便理解上下文
        if self.config.get('preserve_structure', True):
            preserved = self._preserve_structure(detection_type, original)
            if preserved:
                return preserved

        # 使用简洁的类型标识
        if rule or self.config.get('show_type_hint', True):
            type_name = self._get_type_name(detection_type)
            # 使用简洁的格式：【类型】而不是[类型已隐藏]
            return f"【{type_name}】"

        # 默认混淆
        return "【隐藏】"

    def _preserve_structure(self, detection_type: str, original: str) -> str:
        """
        保留部分结构以便理解上下文（返回None表示不保留结构）
        
        Args:
            detection_type: 检测类型
            original: 原始内容
        
        Returns:
            保留结构的掩码，或None表示使用默认混淆
        """
        # 邮箱：保留域名后缀
        if detection_type == 'email' and '@' in original:
            parts = original.split('@')
            if len(parts) == 2:
                domain_parts = parts[1].split('.')
                if len(domain_parts) >= 2:
                    # 保留第一个字符和域名
                    return f"{original[0]}***@{parts[1]}"

        # 手机号：保留前3后4
        if detection_type in ['phone_cn', 'phone'] and len(original) >= 11:
            return f"{original[:3]}****{original[-4:]}"

        # 身份证：保留前6后4
        if detection_type == 'id_card_cn' and len(original) == 18:
            return f"{original[:6]}****{original[-4:]}"

        # 银行卡：保留后4位
        if detection_type in ['bank_card', 'credit_card']:
            clean_num = original.replace(' ', '').replace('-', '')
            if len(clean_num) >= 4:
                return f"**** **** **** {clean_num[-4:]}"

        # IP地址：保留第一段
        if detection_type in ['ipv4', 'ip'] and '.' in original:
            parts = original.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.***.***.***"

        # 对于其他类型，返回None使用默认格式
        return None

    def _get_type_name(self, detection_type: str) -> str:
        """获取类型的中文名称"""
        type_names = {
            'email': '邮箱',
            'phone_cn': '手机号',
            'phone_landline': '电话',
            'phone': '电话',
            'id_card_cn': '身份证',
            'id_card': '身份证',
            'ipv4': 'IP地址',
            'ip': 'IP地址',
            'api_key': 'API密钥',
            'jwt_token': 'Token',
            'token': 'Token',
            'credit_card': '信用卡',
            'bank_card': '银行卡',
            'url_secret': '密钥',
            'secret': '密钥',
            'aws_key': 'AWS密钥',
            'db_connection': '数据库连接',
            'private_key': '私钥',
            'personnel': '人员信息',
            'financial': '财务信息',
            'strategy': '战略信息',
            'technical': '技术信息',
            'customer': '客户信息',
        }
        return type_names.get(detection_type, '敏感信息')

    def create_mapping(self, detections: List[Any], text: str) -> Dict[str, str]:
        """
        创建原始内容到混淆内容的映射表
        
        Args:
            detections: 检测结果列表
            text: 原始文本
        
        Returns:
            映射字典
        """
        mapping = {}
        for detection in detections:
            original = text[detection.start:detection.end]
            obfuscated = self._generate_obfuscation(detection, original)

            # 使用hash作为key以避免重复
            key = hashlib.md5(original.encode()).hexdigest()[:8]
            mapping[key] = {'original': original, 'obfuscated': obfuscated, 'type': getattr(detection, 'type', getattr(detection, 'category', 'unknown'))}

        return mapping
