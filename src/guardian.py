"""
AI Chat Guardian 核心类
整合所有检测和混淆模块
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .detectors import RegexDetector, KeywordDetector, AIDetector
from .obfuscators import Obfuscator
from .utils import load_config, load_sensitive_keywords


@dataclass
class GuardianResult:
    """守护检测结果"""
    original_text: str  # 原始文本
    safe_text: str  # 安全文本（已混淆）
    has_sensitive: bool  # 是否包含敏感信息
    detection_count: int  # 检测到的敏感信息数量
    detections: List[Dict[str, Any]] = field(default_factory=list)  # 检测详情
    obfuscation_details: List[Dict[str, Any]] = field(default_factory=list)  # 混淆详情
    warnings: List[str] = field(default_factory=list)  # 警告信息


class ChatGuardian:
    """AI聊天守护者主类"""
    def __init__(self, config_path: str = None, keywords_path: str = None):
        """
        初始化守护者
        
        Args:
            config_path: 配置文件路径
            keywords_path: 关键词文件路径
        """
        self.logger = logging.getLogger(__name__)

        # 加载配置
        self.config = load_config(config_path)
        self.keywords = load_sensitive_keywords(keywords_path)

        # 初始化检测器
        self._init_detectors()

        # 初始化混淆器
        self.obfuscator = Obfuscator(self.config.get('obfuscation', {}))

        self.logger.info("AI Chat Guardian 初始化完成")

    def _init_detectors(self):
        """初始化所有检测器"""
        detection_config = self.config.get('detection', {})

        # 正则检测器
        if detection_config.get('enable_regex', True):
            self.regex_detector = RegexDetector()
            self.logger.info("正则检测器已启用")
        else:
            self.regex_detector = None
            self.logger.info("正则检测器已禁用")

        # 关键词检测器
        if detection_config.get('enable_keyword', True):
            self.keyword_detector = KeywordDetector(self.keywords)
            self.logger.info("关键词检测器已启用")
        else:
            self.keyword_detector = None
            self.logger.info("关键词检测器已禁用")

        # AI检测器
        if detection_config.get('enable_ai', False):
            try:
                ai_config = self.config.get('ai_model', {})
                self.ai_detector = AIDetector(model_name=ai_config.get('model_name', 'bert-base-chinese'), use_gpu=ai_config.get('use_gpu', False), mode=ai_config.get('mode', 'keyword-enhanced'))
                if self.ai_detector.is_available():
                    self.logger.info(f"AI检测器已启用 (模式: {ai_config.get('mode', 'keyword-enhanced')})")
                else:
                    self.ai_detector = None
                    self.logger.warning("AI检测器初始化失败")
            except Exception as e:
                self.logger.error(f"AI检测器初始化出错: {e}")
                self.ai_detector = None
        else:
            self.ai_detector = None
            self.logger.info("AI检测器已禁用")

    def check_text(self, text: str, auto_obfuscate: bool = True) -> GuardianResult:
        """
        检查文本中的敏感信息
        
        Args:
            text: 待检查的文本
            auto_obfuscate: 是否自动混淆
        
        Returns:
            检测结果
        """
        if not text or not text.strip():
            return GuardianResult(original_text=text, safe_text=text, has_sensitive=False, detection_count=0)

        self.logger.info(f"开始检测文本，长度: {len(text)}")

        # 收集所有检测结果
        all_detections = []
        warnings = []

        # 1. 正则检测
        if self.regex_detector:
            try:
                regex_results = self.regex_detector.detect(text)
                all_detections.extend(regex_results)
                self.logger.debug(f"正则检测发现 {len(regex_results)} 处敏感信息")
            except Exception as e:
                self.logger.error(f"正则检测出错: {e}")
                warnings.append(f"正则检测出错: {str(e)}")

        # 2. 关键词检测
        if self.keyword_detector:
            try:
                keyword_results = self.keyword_detector.detect(text)
                all_detections.extend(keyword_results)
                self.logger.debug(f"关键词检测发现 {len(keyword_results)} 处敏感信息")
            except Exception as e:
                self.logger.error(f"关键词检测出错: {e}")
                warnings.append(f"关键词检测出错: {str(e)}")

        # 3. AI语义检测
        if self.ai_detector:
            try:
                threshold = self.config.get('detection', {}).get('confidence_threshold', 0.7)
                ai_results = self.ai_detector.detect(text, threshold)
                all_detections.extend(ai_results)
                self.logger.debug(f"AI检测发现 {len(ai_results)} 处敏感信息")
            except Exception as e:
                self.logger.error(f"AI检测出错: {e}")
                warnings.append(f"AI检测出错: {str(e)}")

        # 去重和合并
        all_detections = self._merge_detections(all_detections)

        has_sensitive = len(all_detections) > 0

        # 混淆处理
        if auto_obfuscate and has_sensitive:
            safe_text, obfuscation_details = self.obfuscator.obfuscate(text, all_detections)
        else:
            safe_text = text
            obfuscation_details = []

        # 构建检测详情
        detection_details = self._build_detection_details(all_detections, text)

        result = GuardianResult(original_text=text,
                                safe_text=safe_text,
                                has_sensitive=has_sensitive,
                                detection_count=len(all_detections),
                                detections=detection_details,
                                obfuscation_details=obfuscation_details,
                                warnings=warnings)

        self.logger.info(f"检测完成，发现 {len(all_detections)} 处敏感信息")

        return result

    def _merge_detections(self, detections: List[Any]) -> List[Any]:
        """
        合并重叠的检测结果
        
        Args:
            detections: 检测结果列表
        
        Returns:
            合并后的结果列表
        """
        if not detections:
            return []

        # 按位置排序
        sorted_detections = sorted(detections, key=lambda x: (x.start, -x.confidence))

        # 去除完全重叠的检测
        merged = []
        for detection in sorted_detections:
            is_duplicate = False
            for existing in merged:
                # 如果区域完全重叠，保留置信度更高的
                if (detection.start >= existing.start and detection.end <= existing.end):
                    is_duplicate = True
                    break

            if not is_duplicate:
                merged.append(detection)

        return merged

    def _build_detection_details(self, detections: List[Any], text: str) -> List[Dict[str, Any]]:
        """
        构建检测详情列表
        
        Args:
            detections: 检测结果
            text: 原始文本
        
        Returns:
            详情列表
        """
        details = []
        for detection in detections:
            detail = {
                'type': getattr(detection, 'type', getattr(detection, 'category', 'unknown')),
                'content': text[detection.start:detection.end],
                'position': (detection.start, detection.end),
                'confidence': getattr(detection, 'confidence', 0.0)
            }
            details.append(detail)

        return details

    def check_file(self, file_path: str, auto_obfuscate: bool = True) -> GuardianResult:
        """
        检查文件内容
        
        Args:
            file_path: 文件路径
            auto_obfuscate: 是否自动混淆
        
        Returns:
            检测结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.check_text(text, auto_obfuscate)
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
            return GuardianResult(original_text="", safe_text="", has_sensitive=False, detection_count=0, warnings=[f"读取文件失败: {str(e)}"])

    def get_statistics(self, result: GuardianResult) -> Dict[str, Any]:
        """
        获取检测统计信息
        
        Args:
            result: 检测结果
        
        Returns:
            统计信息
        """
        stats = {'total_detections': result.detection_count, 'has_sensitive': result.has_sensitive, 'by_type': {}}

        # 按类型统计
        for detection in result.detections:
            det_type = detection['type']
            if det_type not in stats['by_type']:
                stats['by_type'][det_type] = 0
            stats['by_type'][det_type] += 1

        return stats
