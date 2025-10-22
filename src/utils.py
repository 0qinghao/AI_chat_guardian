"""
工具函数模块
提供配置加载、日志记录等辅助功能
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
    
    Returns:
        配置字典
    """
    if config_path is None:
        config_path = get_project_root() / "config" / "default_config.yaml"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.warning(f"无法加载配置文件 {config_path}: {e}")
        return get_default_config()


def load_sensitive_keywords(keywords_path: str = None) -> Dict[str, list]:
    """
    加载敏感关键词库
    
    Args:
        keywords_path: 关键词文件路径
    
    Returns:
        关键词字典
    """
    if keywords_path is None:
        keywords_path = get_project_root() / "config" / "sensitive_keywords.yaml"

    try:
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords = yaml.safe_load(f)
        return keywords if keywords else {}
    except Exception as e:
        logging.warning(f"无法加载关键词文件 {keywords_path}: {e}")
        return {}


def get_default_config() -> Dict[str, Any]:
    """返回默认配置"""
    return {
        'detection': {
            'enable_regex': True,
            'enable_keyword': True,
            'enable_ai': False,
            'confidence_threshold': 0.7
        },
        'obfuscation': {
            'preserve_structure': True,
            'email_mask': '***@***.com',
            'phone_mask': '***-****-****',
            'id_card_mask': '******************',
            'generic_mask': '[已隐藏]',
            'show_type_hint': True
        },
        'output': {
            'verbose': True,
            'color_highlight': True,
            'log_level': 'INFO'
        }
    }


def setup_logging(log_level: str = 'INFO'):
    """
    设置日志
    
    Args:
        log_level: 日志级别
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def safe_str(obj: Any) -> str:
    """安全地转换对象为字符串"""
    try:
        return str(obj)
    except:
        return repr(obj)
