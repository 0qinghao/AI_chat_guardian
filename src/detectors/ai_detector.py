"""
AI语义检测器（可选）
使用本地轻量级AI模型进行语义理解，检测潜在的敏感内容
注意：此模块为可选功能，需要额外依赖

支持两种模式：
1. 零样本分类模式（推荐）- 使用预训练模型直接分类
2. 相似度匹配模式 - 计算与敏感内容模板的相似度
"""
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class SemanticMatch:
    """语义匹配结果"""
    text: str  # 匹配文本
    category: str  # 分类
    start: int  # 起始位置
    end: int  # 结束位置
    confidence: float  # 置信度


class AIDetector:
    """基于AI的语义检测器"""
    def __init__(self, model_name: str = "bert-base-chinese", use_gpu: bool = False, mode: str = "zero-shot"):
        """
        初始化AI检测器
        
        Args:
            model_name: 模型名称（默认：bert-base-chinese）
            use_gpu: 是否使用GPU
            mode: 检测模式 - "zero-shot"（零样本分类）或 "similarity"（相似度匹配）
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.use_gpu = use_gpu
        self.mode = mode
        self.model = None
        self.tokenizer = None
        self.classifier = None
        self.sentence_model = None

        # 定义敏感类别及其描述
        self.categories = {
            'financial': {
                'label': '财务信息',
                'keywords': ['金额', '收入', '成本', '利润', '预算', '营业额', '财报', '资金', '投资'],
                'templates': ['这段文本包含财务数据和金额信息', '讨论公司的收入和利润情况', '涉及预算和资金信息']
            },
            'personnel': {
                'label': '人员信息',
                'keywords': ['员工', '人员', '名单', '工资', '薪资', '招聘', '离职', '绩效'],
                'templates': ['这段文本包含员工个人信息', '讨论人员安排和薪资', '涉及员工名单和联系方式']
            },
            'strategy': {
                'label': '战略信息',
                'keywords': ['战略', '规划', '计划', '目标', '策略', '竞争', '机密', '内部'],
                'templates': ['这段文本包含公司战略规划', '讨论商业计划和竞争策略', '涉及机密的战略信息']
            },
            'technical': {
                'label': '技术信息',
                'keywords': ['代码', '系统', '服务器', '数据库', '架构', '算法', '技术方案'],
                'templates': ['这段文本包含技术实现细节', '讨论系统架构和代码', '涉及技术方案和数据库信息']
            },
            'customer': {
                'label': '客户信息',
                'keywords': ['客户', '用户', '合同', '订单', '商务', '客户数据'],
                'templates': ['这段文本包含客户信息', '讨论客户数据和订单', '涉及商务合同信息']
            }
        }

        self._init_model()

    def _init_model(self):
        """初始化AI模型"""
        try:
            self.logger.info(f"正在加载AI模型: {self.model_name}, 模式: {self.mode}")

            if self.mode == "zero-shot":
                # 零样本分类模式
                self._init_zero_shot_classifier()
            elif self.mode == "similarity":
                # 相似度匹配模式
                self._init_sentence_model()
            else:
                # 增强的关键词匹配模式（不需要额外依赖）
                self.logger.info("使用增强关键词模式（无需额外依赖）")
                self.model = "keyword-enhanced"

        except ImportError as e:
            self.logger.warning(f"未安装必要的库: {e}")
            self.logger.warning("AI检测将使用增强关键词模式")
            self.logger.info("要启用完整AI功能，请运行: pip install transformers torch sentence-transformers")
            self.model = "keyword-enhanced"
        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
            self.logger.info("回退到增强关键词模式")
            self.model = "keyword-enhanced"

    def _init_zero_shot_classifier(self):
        """初始化零样本分类器"""
        try:
            from transformers import pipeline
            import torch

            # 检测设备
            device = 0 if self.use_gpu and torch.cuda.is_available() else -1

            # 使用零样本分类管道
            self.classifier = pipeline("zero-shot-classification", model="bert-base-chinese", device=device)

            self.model = "zero-shot"
            self.logger.info("✓ 零样本分类器加载成功")

        except Exception as e:
            self.logger.warning(f"零样本分类器加载失败: {e}")
            raise

    def _init_sentence_model(self):
        """初始化句子相似度模型"""
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            # 使用轻量级中文句子向量模型
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            self.sentence_model = SentenceTransformer(model_name)

            if self.use_gpu and torch.cuda.is_available():
                self.sentence_model = self.sentence_model.to('cuda')

            # 预计算敏感内容模板的向量
            self._precompute_template_embeddings()

            self.model = "similarity"
            self.logger.info("✓ 句子相似度模型加载成功")

        except Exception as e:
            self.logger.warning(f"句子相似度模型加载失败: {e}")
            raise

    def _precompute_template_embeddings(self):
        """预计算敏感内容模板的向量"""
        self.template_embeddings = {}

        for category, info in self.categories.items():
            templates = info['templates']
            embeddings = self.sentence_model.encode(templates)
            self.template_embeddings[category] = embeddings

        self.logger.debug(f"已预计算 {len(self.template_embeddings)} 个类别的模板向量")

    def detect(self, text: str, threshold: float = 0.7) -> List[SemanticMatch]:
        """
        使用AI模型检测文本中的敏感内容
        
        Args:
            text: 待检测的文本
            threshold: 置信度阈值
        
        Returns:
            匹配结果列表
        """
        if self.model is None:
            self.logger.debug("AI模型未加载，跳过AI检测")
            return []

        results = []

        # 将文本分割成句子进行检测
        sentences = self._split_sentences(text)

        for sentence, start_pos in sentences:
            if len(sentence.strip()) < 10:  # 跳过太短的句子
                continue

            # 根据模式进行分析
            if self.model == "zero-shot":
                detections = self._detect_zero_shot(sentence, threshold)
            elif self.model == "similarity":
                detections = self._detect_similarity(sentence, threshold)
            else:
                # 增强关键词模式
                detections = self._detect_enhanced_keywords(sentence, threshold)

            # 添加位置信息
            for category, confidence in detections:
                match = SemanticMatch(text=sentence, category=category, start=start_pos, end=start_pos + len(sentence), confidence=confidence)
                results.append(match)
                self.logger.debug(f"AI检测到敏感内容 [{category}]: {sentence[:50]}... (置信度: {confidence:.2f})")

        return results

    def _detect_zero_shot(self, text: str, threshold: float) -> List[tuple]:
        """使用零样本分类检测"""
        if self.classifier is None:
            return []

        try:
            # 准备候选标签
            candidate_labels = [info['label'] for info in self.categories.values()]

            # 进行零样本分类
            result = self.classifier(text, candidate_labels, multi_label=True)

            # 提取高置信度的类别
            detections = []
            for label, score in zip(result['labels'], result['scores']):
                if score >= threshold:
                    # 将标签映射回类别键
                    for key, info in self.categories.items():
                        if info['label'] == label:
                            detections.append((key, float(score)))
                            break

            return detections

        except Exception as e:
            self.logger.error(f"零样本分类出错: {e}")
            return []

    def _detect_similarity(self, text: str, threshold: float) -> List[tuple]:
        """使用相似度匹配检测"""
        if self.sentence_model is None or not self.template_embeddings:
            return []

        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity

            # 计算文本向量
            text_embedding = self.sentence_model.encode([text])[0]

            detections = []
            for category, template_embeddings in self.template_embeddings.items():
                # 计算与所有模板的相似度
                similarities = cosine_similarity(text_embedding.reshape(1, -1), template_embeddings)[0]

                # 取最大相似度
                max_similarity = float(np.max(similarities))

                if max_similarity >= threshold:
                    detections.append((category, max_similarity))

            return detections

        except Exception as e:
            self.logger.error(f"相似度计算出错: {e}")
            return []

    def _detect_enhanced_keywords(self, text: str, threshold: float) -> List[tuple]:
        """增强的关键词检测（智能权重）"""
        detections = []
        text_lower = text.lower()

        for category, info in self.categories.items():
            keywords = info['keywords']

            # 计算匹配得分
            matches = sum(1 for kw in keywords if kw in text_lower)

            if matches > 0:
                # 基于匹配数量和关键词重要性计算置信度
                # 考虑文本长度和关键词密度
                text_length = len(text)
                keyword_density = matches / len(keywords)

                # 动态置信度计算
                base_confidence = 0.5
                keyword_boost = keyword_density * 0.3
                length_penalty = max(0, (text_length - 50) / 200) * 0.1

                confidence = min(base_confidence + keyword_boost + length_penalty, 0.95)

                if confidence >= threshold:
                    detections.append((category, confidence))

        return detections

    def _split_sentences(self, text: str) -> List[tuple]:
        """
        将文本分割成句子，返回(句子, 起始位置)元组列表
        
        Args:
            text: 输入文本
        
        Returns:
            (句子, 起始位置)列表
        """
        import re

        # 改进的句子分割（支持中英文）
        sentence_endings = re.compile(r'[。！？；\.\!\?\;]\s*|[\n]{2,}')

        sentences = []
        start = 0

        for match in sentence_endings.finditer(text):
            sentence = text[start:match.end()].strip()
            if sentence and len(sentence) >= 10:  # 过滤太短的句子
                sentences.append((sentence, start))
            start = match.end()

        # 添加最后一句（如果有）
        if start < len(text):
            sentence = text[start:].strip()
            if sentence and len(sentence) >= 10:
                sentences.append((sentence, start))

        return sentences

    def is_available(self) -> bool:
        """检查AI检测器是否可用"""
        return self.model is not None

    def get_model_info(self) -> Dict[str, any]:
        """获取模型信息"""
        return {
            'mode': self.mode,
            'model_name': self.model_name,
            'model_loaded': self.model is not None,
            'model_type': self.model if isinstance(self.model, str) else type(self.model).__name__,
            'use_gpu': self.use_gpu,
            'categories': list(self.categories.keys())
        }
