"""
AI Chat Guardian Web服务
提供RESTful API和Web界面，支持局域网访问
"""
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.guardian import ChatGuardian

# 创建Flask应用
app = Flask(__name__, static_folder='web/static', template_folder='web/templates')

# 启用CORS，允许跨域访问
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Guardian实例
guardian = None


def init_guardian():
    """初始化Guardian实例"""
    global guardian
    try:
        guardian = ChatGuardian()
        logger.info("✓ ChatGuardian初始化成功")
        return True
    except Exception as e:
        logger.error(f"✗ ChatGuardian初始化失败: {e}")
        return False


# 启动时初始化
init_guardian()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    status = {'status': 'healthy', 'guardian_available': guardian is not None, 'llm_available': False}

    if guardian and hasattr(guardian, 'llm_detector') and guardian.llm_detector:
        status['llm_available'] = guardian.llm_detector.is_available()
        status['llm_model'] = guardian.llm_detector.model

    return jsonify(status)


@app.route('/api/detect', methods=['POST'])
def detect_text():
    """
    检测文本中的敏感信息
    
    请求体:
    {
        "text": "待检测的文本",
        "auto_obfuscate": true  // 可选，默认true
    }
    
    返回:
    {
        "success": true,
        "data": {
            "has_sensitive": true,
            "detection_count": 2,
            "original_text": "原始文本",
            "safe_text": "混淆后的文本",
            "detections": [...],
            "llm_raw_response": "LLM原始输出"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': '缺少必需参数: text'}), 400

        text = data['text']
        auto_obfuscate = data.get('auto_obfuscate', True)

        if not text or not text.strip():
            return jsonify({'success': False, 'error': '文本不能为空'}), 400

        # 检测
        logger.info(f"收到检测请求，文本长度: {len(text)}")
        result = guardian.check_text(text, auto_obfuscate=auto_obfuscate)

        # 构建响应
        response_data = {
            'has_sensitive': result.has_sensitive,
            'detection_count': result.detection_count,
            'original_text': result.original_text,
            'safe_text': result.safe_text,
            'detections': result.detections,
            'llm_raw_response': result.llm_raw_response if hasattr(result, 'llm_raw_response') else '',
            'warnings': result.warnings
        }

        logger.info(f"检测完成，发现 {result.detection_count} 处敏感信息")

        return jsonify({'success': True, 'data': response_data})

    except Exception as e:
        logger.error(f"检测失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """
    获取当前配置
    
    返回:
    {
        "success": true,
        "config": {
            "llm_detector": {...},
            "detection": {...}
        }
    }
    """
    try:
        if not guardian:
            return jsonify({'success': False, 'error': 'Guardian未初始化'}), 500

        return jsonify({'success': True, 'config': guardian.config})

    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_available_models():
    """
    获取可用的LLM模型列表
    
    返回:
    {
        "success": true,
        "models": [
            {"name": "gemma3:1b", "size": "0.76GB"},
            ...
        ]
    }
    """
    try:
        if not guardian or not guardian.llm_detector:
            return jsonify({'success': False, 'error': 'LLM检测器不可用'}), 500

        # 从配置中读取可用模型
        llm_config = guardian.config.get('llm_detector', {})
        available_models = llm_config.get('available_models', [])

        # 清理模型名称（去除注释）
        models = []
        for model in available_models:
            model_name = model.split('#')[0].strip()
            comment = ''
            if '#' in model:
                comment = model.split('#')[1].strip()

            models.append({'name': model_name, 'description': comment})

        return jsonify({'success': True, 'models': models, 'current_model': guardian.llm_detector.model})

    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'success': False, 'error': '资源未找到'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"服务器内部错误: {error}")
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


def main():
    """启动Web服务"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Chat Guardian Web服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0，所有接口)')
    parser.add_argument('--port', type=int, default=5000, help='监听端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

    # 显示启动信息
    print("=" * 70)
    print("🚀 AI Chat Guardian Web服务")
    print("=" * 70)
    print(f"监听地址: {args.host}:{args.port}")
    print(f"本机访问: http://localhost:{args.port}")
    print(f"局域网访问: http://<你的IP>:{args.port}")
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 70)
    print("\n按 Ctrl+C 停止服务\n")

    # 启动服务
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True  # 启用多线程处理
    )


if __name__ == '__main__':
    main()
