"""
AI Chat Guardian - Web版本
提供Web界面供内网用户访问使用
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sys
import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import secrets
import yaml

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.guardian import ChatGuardian

# 创建Flask应用
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 用于session加密
CORS(app)  # 允许跨域请求

# 配置日志目录
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# 配置基础日志（只显示WARNING及以上）
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 隐藏Werkzeug的访问日志
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

# 创建用户行为日志记录器
user_logger = logging.getLogger('user_activity')
user_logger.setLevel(logging.INFO)
user_handler = RotatingFileHandler(
    log_dir / 'user_activity.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8')
user_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
user_logger.addHandler(user_handler)
user_logger.propagate = False

# 全局Guardian实例
guardian = None


def init_guardian():
    """初始化Guardian实例"""
    global guardian
    try:
        guardian = ChatGuardian()
        logger.info("✓ Guardian初始化成功")
        return True
    except Exception as e:
        logger.error(f"✗ Guardian初始化失败: {e}")
        return False


@app.route('/')
def index():
    """主页"""
    # 记录访问
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    user_logger.info(f"访问主页 | IP: {client_ip} | UA: {user_agent}")
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def check_text():
    """检测文本API"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'success': False, 'error': '请输入要检测的文本'}), 400

        # 记录用户行为
        client_ip = request.remote_addr
        session_id = session.get('session_id', 'unknown')
        text_length = len(text)
        text_preview = text[:100].replace('\n', ' ') if len(text) > 100 else text.replace('\n', ' ')

        user_logger.info(f"文本检测 | IP: {client_ip} | Session: {session_id} | "
                         f"长度: {text_length}字符 | 预览: {text_preview}")

        # 执行检测
        result = guardian.check_text(text, auto_obfuscate=True)

        # 构建响应
        response = {
            'success': True,
            'data': {
                'original_text': result.original_text,
                'safe_text': result.safe_text,
                'has_sensitive': result.has_sensitive,
                'detection_count': result.detection_count,
                'detections': result.detections,
                'obfuscation_details': result.obfuscation_details,
                'warnings': result.warnings,
                'llm_raw_response': result.llm_raw_response if hasattr(result, 'llm_raw_response') else ''
            }
        }

        # 记录检测结果
        user_logger.info(f"检测完成 | IP: {client_ip} | Session: {session_id} | "
                         f"敏感信息: {result.detection_count}处 | "
                         f"类型: {', '.join(set([d.get('type', 'unknown') for d in result.detections])) if result.detections else '无'}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"检测失败: {e}", exc_info=True)
        user_logger.error(f"检测失败 | IP: {request.remote_addr} | "
                          f"Session: {session.get('session_id', 'unknown')} | "
                          f"错误: {str(e)}")
        return jsonify({'success': False, 'error': f'检测失败: {str(e)}'}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    try:
        # 检查各个检测器状态
        status = {
            'success': True,
            'data': {
                'guardian_initialized': guardian is not None,
                'regex_enabled': guardian.regex_detector is not None if guardian else False,
                'keyword_enabled': guardian.keyword_detector is not None if guardian else False,
                'ai_enabled': guardian.ai_detector is not None if guardian else False,
                'llm_enabled': guardian.llm_detector is not None if guardian else False,
                'llm_model': guardian.llm_detector.model if (guardian and guardian.llm_detector) else 'N/A',
                'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """配置管理API - 获取或更新配置"""
    global guardian

    if request.method == 'GET':
        # 获取当前配置
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'default_config.yaml'

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 获取当前检测器状态
            detection_config = config.get('detection', {})
            llm_config = config.get('llm_detector', {})

            config_info = {
                'success': True,
                'data': {
                    'detection': {
                        'enable_regex': detection_config.get('enable_regex', True),
                        'enable_keyword': detection_config.get('enable_keyword', True),
                        'enable_ai': detection_config.get('enable_ai', False)
                    },
                    'llm_detector': {
                        'enable': llm_config.get('enable', False),
                        'type': llm_config.get('type', 'api'),
                        'api': llm_config.get('api', {}),
                        'local': llm_config.get('local', {})
                    },
                    'current_status': {
                        'regex_active': guardian.regex_detector is not None if guardian else False,
                        'keyword_active': guardian.keyword_detector is not None if guardian else False,
                        'ai_active': guardian.ai_detector is not None if guardian else False,
                        'llm_active': guardian.llm_detector is not None if guardian else False,
                        'llm_type': getattr(guardian.llm_detector, 'type', None) if guardian and guardian.llm_detector else None,
                        'llm_model': getattr(guardian.llm_detector, 'model', None) if guardian and guardian.llm_detector else None
                    }
                }
            }
            return jsonify(config_info)

        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'POST':
        # 更新配置
        try:
            data = request.get_json()
            config_path = Path(__file__).parent.parent / 'config' / 'default_config.yaml'

            # 记录配置变更
            client_ip = request.remote_addr
            session_id = session.get('session_id', 'unknown')
            user_logger.info(f"配置变更 | IP: {client_ip} | Session: {session_id} | "
                             f"变更内容: {data}")

            # 读取现有配置
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 更新检测器配置
            if 'detection' in data:
                if 'detection' not in config:
                    config['detection'] = {}
                config['detection'].update(data['detection'])

            # 更新LLM配置
            if 'llm_detector' in data:
                if 'llm_detector' not in config:
                    config['llm_detector'] = {}
                config['llm_detector'].update(data['llm_detector'])

            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

            # 重新初始化Guardian
            logger.info("配置已更新，重新初始化Guardian...")
            user_logger.info(f"Guardian重载 | IP: {client_ip} | Session: {session_id}")
            if init_guardian():
                return jsonify({
                    'success': True,
                    'message': '配置已保存并重新加载检测器',
                    'data': {
                        'regex_active': guardian.regex_detector is not None,
                        'keyword_active': guardian.keyword_detector is not None,
                        'ai_active': guardian.ai_detector is not None,
                        'llm_active': guardian.llm_detector is not None
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'Guardian重新初始化失败'}), 500

        except Exception as e:
            logger.error(f"更新配置失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500


@app.before_request
def before_request():
    """每次请求前执行"""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(8)


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'success': False, 'error': '请求的资源不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"服务器错误: {error}")
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("AI Chat Guardian - Web服务")
    print("=" * 60)

    # 初始化Guardian
    if not init_guardian():
        print("✗ Guardian初始化失败，请检查配置")
        sys.exit(1)

    # 获取服务器配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')  # 0.0.0.0允许外部访问
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"\n✓ 服务器配置:")
    print(f"  - 地址: http://{host}:{port}")
    print(f"  - 内网访问: http://<你的IP>:{port}")
    print(f"  - 调试模式: {debug}")
    print(f"\n按 Ctrl+C 停止服务\n")
    print("=" * 60)

    # 启动服务器
    app.run(host=host, port=port, debug=debug, threaded=True)
