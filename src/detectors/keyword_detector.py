"""
关键词检测器
基于敏感词库进行匹配检测
"""
import logging
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class KeywordMatch:
    """关键词匹配结果"""
    keyword: str  # 匹配到的关键词
    category: str  # 所属分类
    start: int  # 起始位置
    end: int  # 结束位置
    confidence: float  # 置信度


class KeywordDetector:
    """基于关键词的敏感信息检测器"""
    def __init__(self, keywords_dict: Dict[str, List[str]]):
        """
        初始化关键词检测器
        
        Args:
            keywords_dict: 关键词字典，格式为 {分类: [关键词列表]}
        """
        self.logger = logging.getLogger(__name__)
        self.keywords_dict = keywords_dict
        self._build_keyword_index()

    def _build_keyword_index(self):
        """构建关键词索引"""
        self.keyword_index = {}
        for category, keywords in self.keywords_dict.items():
            if keywords:
                for keyword in keywords:
                    if keyword and isinstance(keyword, str):
                        self.keyword_index[keyword.lower()] = category

        self.logger.info(f"已加载 {len(self.keyword_index)} 个敏感关键词")

    def detect(self, text: str) -> List[KeywordMatch]:
        """
        检测文本中的敏感关键词
        
        Args:
            text: 待检测的文本
        
        Returns:
            匹配结果列表
        """
        results = []
        text_lower = text.lower()

        for keyword, category in self.keyword_index.items():
            # 查找所有出现的位置
            start = 0
            while True:
                pos = text_lower.find(keyword, start)
                if pos == -1:
                    break

                match = KeywordMatch(
                    keyword=keyword,
                    category=category,
                    start=pos,
                    end=pos + len(keyword),
                    confidence=0.85  # 关键词匹配置信度固定为0.85
                )
                results.append(match)

                self.logger.debug(f"检测到敏感词 [{category}]: {keyword}")
                start = pos + len(keyword)

        # 去重和排序
        results = self._deduplicate_matches(results)
        results.sort(key=lambda x: x.start)

        return results

    def _deduplicate_matches(self, matches: List[KeywordMatch]) -> List[KeywordMatch]:
        """
        去重：处理重叠的匹配，保留最长的匹配
        
        Args:
            matches: 匹配结果列表
        
        Returns:
            去重后的结果列表
        """
        if not matches:
            return matches

        # 按起始位置和长度排序（优先保留更长的匹配）
        sorted_matches = sorted(matches, key=lambda x: (x.start, -(x.end - x.start)))

        filtered = []
        for match in sorted_matches:
            # 检查是否与已有匹配重叠
            overlaps = False
            for existing in filtered:
                if self._is_overlap(match, existing):
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(match)

        return filtered

    def _is_overlap(self, m1: KeywordMatch, m2: KeywordMatch) -> bool:
        """判断两个匹配是否重叠"""
        return not (m1.end <= m2.start or m1.start >= m2.end)

    def add_keywords(self, category: str, keywords: List[str]):
        """
        动态添加关键词
        
        Args:
            category: 分类名称
            keywords: 关键词列表
        """
        if category not in self.keywords_dict:
            self.keywords_dict[category] = []

        self.keywords_dict[category].extend(keywords)

        # 更新索引
        for keyword in keywords:
            if keyword and isinstance(keyword, str):
                self.keyword_index[keyword.lower()] = category

        self.logger.info(f"添加了 {len(keywords)} 个关键词到分类 {category}")
