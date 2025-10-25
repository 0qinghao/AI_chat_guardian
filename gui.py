"""
AI Chat Guardian - 图形用户界面
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import yaml
import threading

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))


# 加载.env文件到环境变量
def load_env():
    """加载.env文件，支持打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后环境：从exe同目录加载
        env_file = Path(sys.executable).parent / '.env'
    else:
        # 开发环境
        env_file = Path(__file__).parent / '.env'

    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
    else:
        # 如果没有.env文件，提示用户
        pass  # 稍后在GUI中提示


# 在导入ChatGuardian之前加载环境变量
load_env()

from src import ChatGuardian, setup_logging


class GuardianGUI:
    """AI Chat Guardian GUI应用"""
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat Guardian - AI聊天守护者")
        self.root.geometry("1200x800")

        # 设置默认字体
        default_font = ('Microsoft YaHei UI', 10)
        self.root.option_add('*Font', default_font)

        # 配置文件路径
        self.config_path = Path('config/default_config.yaml')

        # 加载配置
        self.load_config()

        # 初始化守护者
        setup_logging('WARNING')  # GUI模式使用WARNING级别
        try:
            self.guardian = ChatGuardian()
        except Exception as e:
            messagebox.showerror("初始化错误", f"初始化失败: {e}")
            self.root.quit()
            return

        self.setup_ui()

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置失败: {e}")
            self.config = {}

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            messagebox.showerror("保存错误", f"保存配置失败: {e}")
            return False

    def reload_guardian(self):
        """重新加载Guardian实例"""
        try:
            # 重新加载配置文件到内存
            self.load_config()
            # 重新初始化Guardian
            self.guardian = ChatGuardian()
            messagebox.showinfo("成功", "配置已更新并重新加载检测器")
            return True
        except Exception as e:
            messagebox.showerror("重载错误", f"重新加载失败: {e}")
            return False

    def get_status_text(self):
        """获取当前配置状态文本"""
        enabled = []
        detection_config = self.config.get('detection', {})
        llm_config = self.config.get('llm_detector', {})

        if detection_config.get('enable_regex', True):
            enabled.append("✓正则")
        if detection_config.get('enable_keyword', True):
            enabled.append("✓关键词")
        if detection_config.get('enable_ai', False):
            enabled.append("✓AI")
        if llm_config.get('enable', False):
            llm_type = llm_config.get('type', 'local')
            if llm_type == 'api':
                provider = llm_config.get('api', {}).get('provider', 'unknown')
                provider_names = {'zhipu': '智谱AI', 'siliconflow': '硅基流动'}
                provider_display = provider_names.get(provider, provider)
                enabled.append(f"✓LLM-API({provider_display})")
            else:
                llm_model = llm_config.get('local', {}).get('model', 'unknown')
                enabled.append(f"✓LLM-本地({llm_model})")

        if not enabled:
            return "⚠️ 未启用任何检测器"
        return " | ".join(enabled)

    def open_config_window(self):
        """打开配置窗口"""
        # 先重新加载配置，确保显示最新的配置
        self.load_config()

        config_win = tk.Toplevel(self.root)
        config_win.title("检测器配置")
        config_win.geometry("650x850")  # 增加尺寸：宽度650，高度850
        config_win.resizable(True, True)  # 允许调整大小
        config_win.transient(self.root)
        config_win.grab_set()

        # 窗口居中
        config_win.update_idletasks()
        x = (config_win.winfo_screenwidth() // 2) - (650 // 2)
        y = (config_win.winfo_screenheight() // 2) - (850 // 2)
        config_win.geometry(f"650x850+{x}+{y}")  # 标题
        title = tk.Label(config_win, text="⚙️ 检测器配置", font=('Microsoft YaHei UI', 16, 'bold'), fg='#2196F3')
        title.pack(pady=15)

        # 配置面板
        config_frame = ttk.LabelFrame(config_win, text="启用/禁用检测器", padding=15)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 检测器开关变量
        detection_config = self.config.get('detection', {})
        llm_config = self.config.get('llm_detector', {})

        self.regex_var = tk.BooleanVar(value=detection_config.get('enable_regex', True))
        self.keyword_var = tk.BooleanVar(value=detection_config.get('enable_keyword', True))
        self.ai_var = tk.BooleanVar(value=detection_config.get('enable_ai', False))
        self.llm_var = tk.BooleanVar(value=llm_config.get('enable', False))

        # 复选框 - 使用更好的字体和样式
        checkbox_font = ('Microsoft YaHei UI', 11)
        tk.Checkbutton(config_frame, text="✓ 正则表达式检测器 (快速)", variable=self.regex_var, font=checkbox_font, anchor='w').pack(fill=tk.X, pady=8, padx=5)
        tk.Checkbutton(config_frame, text="✓ 关键词检测器 (上下文感知)", variable=self.keyword_var, font=checkbox_font, anchor='w').pack(fill=tk.X, pady=8, padx=5)
        tk.Checkbutton(config_frame, text="✓ AI检测器 (需要模型文件)", variable=self.ai_var, font=checkbox_font, anchor='w').pack(fill=tk.X, pady=8, padx=5)

        llm_check = tk.Checkbutton(config_frame, text="✓ LLM检测器 (本地Ollama或在线API)", variable=self.llm_var, font=checkbox_font, anchor='w', command=lambda: self.toggle_llm_options())
        llm_check.pack(fill=tk.X, pady=8, padx=5)

        # LLM配置框架
        llm_frame = ttk.LabelFrame(config_frame, text="LLM检测器配置", padding=10)
        llm_frame.pack(fill=tk.X, padx=10, pady=10)

        # 获取LLM配置
        llm_config = self.config.get('llm_detector', {})

        # 第一行：检测器类型选择
        type_frame = tk.Frame(llm_frame, bg='white')
        type_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(type_frame, text="检测器类型:", font=('Microsoft YaHei UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.llm_type_var = tk.StringVar(value=llm_config.get('type', 'api'))

        # 单选按钮
        tk.Radiobutton(type_frame, text="☁️ 在线API (推荐)", variable=self.llm_type_var, value='api', font=('Microsoft YaHei UI', 10), bg='white',
                       command=self.update_llm_config_display).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(type_frame, text="🏠 本地Ollama", variable=self.llm_type_var, value='local', font=('Microsoft YaHei UI', 10), bg='white', command=self.update_llm_config_display).pack(side=tk.LEFT,
                                                                                                                                                                                           padx=5)

        # 分隔线
        separator = tk.Frame(llm_frame, height=1, bg='#ddd')
        separator.pack(fill=tk.X, pady=5)

        # API配置区域
        self.api_config_frame = tk.Frame(llm_frame, bg='white')
        self.api_config_frame.pack(fill=tk.X, pady=5)

        # API提供商选择
        provider_row = tk.Frame(self.api_config_frame, bg='white')
        provider_row.pack(fill=tk.X, pady=3)
        tk.Label(provider_row, text="API提供商:", font=('Microsoft YaHei UI', 10), bg='white', width=12, anchor='w').pack(side=tk.LEFT, padx=(0, 5))

        api_config = llm_config.get('api', {})
        self.api_provider_var = tk.StringVar(value=api_config.get('provider', 'zhipu'))

        provider_options = [('智谱AI (推荐)', 'zhipu'), ('硅基流动', 'siliconflow')]

        provider_combo = ttk.Combobox(provider_row, textvariable=self.api_provider_var, width=18, font=('Microsoft YaHei UI', 9), state='readonly', values=[name for name, _ in provider_options])
        provider_combo.pack(side=tk.LEFT, padx=5)

        # 绑定选择事件，将显示名称转换为配置值
        self.provider_display_to_value = {name: value for name, value in provider_options}
        self.provider_value_to_display = {value: name for name, value in provider_options}

        # 设置初始显示值
        current_provider = api_config.get('provider', 'zhipu')
        if current_provider in self.provider_value_to_display:
            provider_combo.set(self.provider_value_to_display[current_provider])

        # API密钥提示
        key_row = tk.Frame(self.api_config_frame, bg='white')
        key_row.pack(fill=tk.X, pady=3)
        tk.Label(key_row, text="💡 提示:", font=('Microsoft YaHei UI', 9), bg='white', fg='#666').pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(key_row, text="API密钥请在环境变量中设置 (参考.env.example)", font=('Microsoft YaHei UI', 8), bg='white', fg='#888').pack(side=tk.LEFT)

        # 本地Ollama配置区域
        self.local_config_frame = tk.Frame(llm_frame, bg='white')
        self.local_config_frame.pack(fill=tk.X, pady=5)

        model_row = tk.Frame(self.local_config_frame, bg='white')
        model_row.pack(fill=tk.X, pady=3)
        tk.Label(model_row, text="本地模型:", font=('Microsoft YaHei UI', 10), bg='white', width=12, anchor='w').pack(side=tk.LEFT, padx=(0, 5))

        local_config = llm_config.get('local', {})
        self.local_model_var = tk.StringVar(value=local_config.get('model', 'qwen2:7b'))

        # 从配置文件读取可用模型列表
        available_models = local_config.get('available_models', ['qwen2:7b', 'gemma3:4b'])
        clean_models = [m.split('#')[0].strip() for m in available_models]

        local_model_combo = ttk.Combobox(model_row, textvariable=self.local_model_var, width=18, font=('Consolas', 9), values=clean_models, state='readonly')
        local_model_combo.pack(side=tk.LEFT, padx=5)

        self.llm_frame = llm_frame
        self.update_llm_config_display()
        self.toggle_llm_options()

        # 说明文字区域 - 限制高度
        info_frame = tk.Frame(config_win, bg='#f5f5f5', relief=tk.FLAT, height=200)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        info_frame.pack_propagate(False)  # 防止内容撑大frame

        info_title = tk.Label(info_frame, text="📖 检测方案说明", font=('Microsoft YaHei UI', 10, 'bold'), bg='#f5f5f5', fg='#333')
        info_title.pack(anchor=tk.W, padx=10, pady=(10, 5))

        info_text = """• 正则表达式：快速模式匹配，适合标准格式（邮箱、电话等）
• 关键词：上下文感知的关键词检测
• AI检测器：需要本地训练模型（已弃用）
• LLM检测器：
  - API模式：使用在线API（智谱AI、硅基流动等），速度快
  - 本地模式：使用本地Ollama，完全隐私保护
"""

        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=('Microsoft YaHei UI', 9), fg='#666', bg='#f5f5f5')
        info_label.pack(anchor=tk.W, padx=10, pady=(0, 10))

        # 分隔线
        separator = tk.Frame(config_win, height=2, bg='#ddd')
        separator.pack(fill=tk.X, padx=20, pady=10)

        # 按钮区域 - 固定在底部，给予足够空间
        btn_frame = tk.Frame(config_win, bg='white', relief=tk.FLAT)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 20), padx=20)

        def save_and_reload():
            # 更新配置
            if 'detection' not in self.config:
                self.config['detection'] = {}

            # 更新检测配置
            self.config['detection']['enable_regex'] = self.regex_var.get()
            self.config['detection']['enable_keyword'] = self.keyword_var.get()
            self.config['detection']['enable_ai'] = self.ai_var.get()

            # 更新LLM配置
            if 'llm_detector' not in self.config:
                self.config['llm_detector'] = {}

            self.config['llm_detector']['enable'] = self.llm_var.get()
            self.config['llm_detector']['type'] = self.llm_type_var.get()

            # 根据类型更新对应的配置
            if self.llm_type_var.get() == 'api':
                # 更新API配置
                if 'api' not in self.config['llm_detector']:
                    self.config['llm_detector']['api'] = {}

                # 从显示名称获取配置值
                provider_display = self.api_provider_var.get()
                provider_value = self.provider_display_to_value.get(provider_display, 'zhipu')
                self.config['llm_detector']['api']['provider'] = provider_value

            else:  # local
                # 更新本地配置
                if 'local' not in self.config['llm_detector']:
                    self.config['llm_detector']['local'] = {}
                self.config['llm_detector']['local']['model'] = self.local_model_var.get()

            # 保存并重载
            if self.save_config():
                if self.reload_guardian():
                    # 更新主界面状态显示
                    self.status_detector_label.config(text=self.get_status_text())
                    config_win.destroy()

        # 按钮容器 - 水平居中，增加内边距
        btn_container = tk.Frame(btn_frame, bg='white')
        btn_container.pack(pady=10)

        # 确定按钮
        tk.Button(btn_container,
                  text="✓ 确定并应用",
                  command=save_and_reload,
                  bg='#4CAF50',
                  fg='white',
                  width=16,
                  height=2,
                  font=('Microsoft YaHei UI', 11, 'bold'),
                  relief=tk.FLAT,
                  cursor='hand2',
                  activebackground='#45a049').pack(side=tk.LEFT, padx=8)

        # 取消按钮
        tk.Button(btn_container,
                  text="✕ 取消",
                  command=config_win.destroy,
                  bg='#f44336',
                  fg='white',
                  width=16,
                  height=2,
                  font=('Microsoft YaHei UI', 11),
                  relief=tk.FLAT,
                  cursor='hand2',
                  activebackground='#da190b').pack(side=tk.LEFT, padx=8)

    def update_llm_config_display(self):
        """根据选择的LLM类型更新配置显示"""
        if hasattr(self, 'api_config_frame') and hasattr(self, 'local_config_frame'):
            llm_type = self.llm_type_var.get()

            # 显示/隐藏对应的配置区域
            if llm_type == 'api':
                self.api_config_frame.pack(fill=tk.X, pady=5)
                self.local_config_frame.pack_forget()
            else:  # local
                self.api_config_frame.pack_forget()
                self.local_config_frame.pack(fill=tk.X, pady=5)

    def toggle_llm_options(self):
        """切换LLM选项的可用状态"""
        if hasattr(self, 'llm_frame'):
            state = 'normal' if self.llm_var.get() else 'disabled'

            # 递归设置所有子组件状态
            def set_state(widget):
                try:
                    if isinstance(widget, (ttk.Combobox, tk.Radiobutton)):
                        widget.configure(state=state)
                    elif isinstance(widget, tk.Label):
                        # 标签保持正常状态，只是颜色变化
                        fg_color = 'black' if state == 'normal' else '#999'
                        widget.configure(fg=fg_color)
                except:
                    pass

                # 递归处理子组件
                for child in widget.winfo_children():
                    set_state(child)

            set_state(self.llm_frame)

    def setup_ui(self):
        """设置UI"""
        # 设置样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei UI', 10))
        style.configure('Status.TLabel', font=('Microsoft YaHei UI', 9))

        # 顶部工具栏
        toolbar_frame = tk.Frame(self.root, bg='#f0f0f0', relief=tk.FLAT, bd=1)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # 配置按钮
        config_btn = tk.Button(toolbar_frame,
                               text="⚙️ 配置检测器",
                               command=self.open_config_window,
                               bg='#2196F3',
                               fg='white',
                               width=15,
                               height=1,
                               font=('Microsoft YaHei UI', 10, 'bold'),
                               relief=tk.FLAT,
                               cursor='hand2',
                               activebackground='#1976D2')
        config_btn.pack(side=tk.LEFT, padx=10, pady=8)

        # 检测器状态显示
        status_frame = tk.Frame(toolbar_frame, bg='#f0f0f0')
        status_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(status_frame, text="当前检测器:", font=('Microsoft YaHei UI', 9), bg='#f0f0f0', fg='#666').pack(side=tk.LEFT)
        self.status_detector_label = tk.Label(status_frame, text=self.get_status_text(), font=('Microsoft YaHei UI', 9, 'bold'), bg='#f0f0f0', fg='#2196F3')
        self.status_detector_label.pack(side=tk.LEFT, padx=5)

        # 顶部标题
        title_frame = tk.Frame(self.root, bg='white', relief=tk.FLAT)
        title_frame.pack(fill=tk.X, pady=10)

        title_label = tk.Label(title_frame, text="🛡️ AI Chat Guardian", font=('Microsoft YaHei UI', 18, 'bold'), bg='white', fg='#1976D2')
        title_label.pack()

        subtitle_label = tk.Label(title_frame, text="保护您的敏感信息，安全使用AI聊天服务", font=('Microsoft YaHei UI', 10), bg='white', fg='#666')
        subtitle_label.pack()

        # 主容器
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：输入区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_label = tk.Label(left_frame, text="📝 输入文本（粘贴待检测内容）", font=('Microsoft YaHei UI', 11, 'bold'), fg='#333')
        input_label.pack(anchor=tk.W, pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(left_frame, width=45, height=22, wrap=tk.WORD, font=('Microsoft YaHei UI', 11), relief=tk.SOLID, bd=1)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X)

        btn_style = {'font': ('Microsoft YaHei UI', 10), 'cursor': 'hand2', 'relief': tk.FLAT}

        self.check_button = tk.Button(button_frame, text="🔍 检测并混淆", command=self.check_text, bg='#4CAF50', fg='white', width=14, **btn_style)
        self.check_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="🗑️ 清空", command=self.clear_all, bg='#f44336', fg='white', width=10, **btn_style)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(button_frame, text="📂 加载文件", command=self.load_file, bg='#FF9800', fg='white', width=12, **btn_style)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # 右侧：输出区域
        right_frame = ttk.Frame(main_frame, padding=(15, 0, 0, 0))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        output_label = tk.Label(right_frame, text="✅ 安全文本（已混淆）", font=('Microsoft YaHei UI', 11, 'bold'), fg='#333')
        output_label.pack(anchor=tk.W, pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(right_frame, width=45, height=22, wrap=tk.WORD, font=('Microsoft YaHei UI', 11), bg='#f0f8ff', relief=tk.SOLID, bd=1)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 输出按钮区域
        output_button_frame = ttk.Frame(right_frame)
        output_button_frame.pack(fill=tk.X)

        self.copy_button = tk.Button(output_button_frame, text="📋 复制到剪贴板", command=self.copy_output, state=tk.DISABLED, bg='#2196F3', fg='white', width=14, **btn_style)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(output_button_frame, text="💾 保存文件", command=self.save_file, state=tk.DISABLED, bg='#9C27B0', fg='white', width=12, **btn_style)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # 底部：进度和详情区域
        bottom_frame = tk.Frame(self.root, bg='white', relief=tk.FLAT)
        bottom_frame.pack(fill=tk.BOTH, padx=15, pady=(0, 15))

        # 进度显示
        progress_frame = tk.Frame(bottom_frame, bg='white')
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(progress_frame, text="检测进度:", font=('Microsoft YaHei UI', 10, 'bold'), bg='white', fg='#333').pack(side=tk.LEFT, padx=(0, 10))

        self.progress_label = tk.Label(progress_frame, text="就绪", font=('Microsoft YaHei UI', 10), bg='white', fg='#4CAF50')
        self.progress_label.pack(side=tk.LEFT)

        # 检测详情
        details_label = tk.Label(bottom_frame, text="📊 检测详情", font=('Microsoft YaHei UI', 11, 'bold'), bg='white', fg='#333')
        details_label.pack(anchor=tk.W, pady=(0, 5))

        self.details_text = scrolledtext.ScrolledText(bottom_frame, height=9, wrap=tk.WORD, font=('Microsoft YaHei UI', 10), bg='#fffaf0', relief=tk.SOLID, bd=1)
        self.details_text.pack(fill=tk.BOTH, expand=True)

    def check_text(self):
        """检测文本"""
        text = self.input_text.get('1.0', tk.END).strip()

        if not text:
            messagebox.showwarning("警告", "请输入要检测的文本！")
            return

        # 禁用按钮
        self.check_button.config(state=tk.DISABLED, text="检测中...")
        self.progress_label.config(text="准备检测...", fg='#FF9800')
        self.root.update()

        # 在新线程中执行检测
        def detect_thread():
            try:
                result = self.perform_detection(text)
                # 在主线程中更新UI
                self.root.after(0, lambda r=result: self.display_result(r))
            except Exception as e:
                self.root.after(0, lambda err=e: self.handle_error(err))

        threading.Thread(target=detect_thread, daemon=True).start()

    def perform_detection(self, text):
        """执行检测并显示进度"""
        # 显示检测进度
        self.root.after(0, lambda: self.progress_label.config(text="🔍 正在检测...", fg='#2196F3'))

        # 直接使用guardian的check_text方法，它会处理所有检测器
        result = self.guardian.check_text(text, auto_obfuscate=True)

        # 完成检测
        self.root.after(0, lambda: self.progress_label.config(text="✓ 检测完成", fg='#4CAF50'))

        return result

    def handle_error(self, error):
        """处理错误"""
        messagebox.showerror("错误", f"检测失败: {error}")
        self.progress_label.config(text="✗ 检测失败", fg='#f44336')
        self.check_button.config(state=tk.NORMAL, text="🔍 检测并混淆")

    def display_result(self, result):
        """显示检测结果"""
        # 清空输出
        self.output_text.delete('1.0', tk.END)
        self.details_text.delete('1.0', tk.END)

        # 显示安全文本
        self.output_text.insert('1.0', result.safe_text)

        # 高亮混淆的文本
        if result.has_sensitive and result.obfuscation_details:
            # 配置tag样式 - 使用醒目的橙红色和加粗
            self.output_text.tag_config(
                'obfuscated',
                foreground='#FF5722',  # 深橙色
                background='#FFE0B2',  # 浅橙色背景
                font=('Microsoft YaHei UI', 11, 'bold'))

            # 收集所有混淆文本的位置（避免重复标记）
            obfuscated_positions = []
            current_pos = 0
            safe_text = result.safe_text

            for detail in result.obfuscation_details:
                obfuscated = detail.get('obfuscated', '')
                if obfuscated and obfuscated in safe_text[current_pos:]:
                    # 找到第一个出现的位置
                    pos = safe_text.find(obfuscated, current_pos)
                    if pos != -1:
                        obfuscated_positions.append((pos, pos + len(obfuscated)))
                        current_pos = pos + len(obfuscated)

            # 应用高亮标记
            for start, end in obfuscated_positions:
                # 计算tkinter的行列位置
                start_line = safe_text[:start].count('\n') + 1
                start_col = start - safe_text[:start].rfind('\n') - 1
                end_line = safe_text[:end].count('\n') + 1
                end_col = end - safe_text[:end].rfind('\n') - 1

                start_idx = f"{start_line}.{start_col}"
                end_idx = f"{end_line}.{end_col}"

                self.output_text.tag_add('obfuscated', start_idx, end_idx)

        # 显示详情
        if result.has_sensitive:
            details = f"🔍 检测结果摘要\n"
            details += f"{'━'*60}\n\n"
            details += f"📌 敏感信息数量: {result.detection_count} 处\n\n"

            # 按类型分组
            type_groups = {}
            for detection in result.detections:
                det_type = detection.get('type', '未知类型')
                if det_type not in type_groups:
                    type_groups[det_type] = []
                type_groups[det_type].append(detection)

            details += "📊 按类型统计:\n\n"

            # 类型图标映射
            type_icons = {'pii': '👤', 'financial': '💰', 'technical': '🔑', 'company': '🏢', 'contact': '📞', 'location': '📍', 'credential': '🔐', 'custom': '⚙️'}

            for det_type, detections in type_groups.items():
                icon = type_icons.get(det_type, '📋')
                details += f"{icon} [{det_type}] 共 {len(detections)} 处:\n"
                details += f"{'─'*58}\n"

                for i, det in enumerate(detections, 1):
                    content = det.get('content', '')
                    # 截断过长内容
                    if len(content) > 40:
                        content = content[:40] + "..."
                    confidence = det.get('confidence', 0) * 100
                    start = det.get('start', 0)
                    end = det.get('end', start)

                    details += f"  {i}. {content}\n"
                    details += f"     • 置信度: {confidence:.1f}%  • 位置: {start}-{end}\n"

                details += "\n"

            self.details_text.insert('1.0', details)
            self.progress_label.config(text=f"⚠️ 检测到 {result.detection_count} 处敏感信息", fg='#f44336')

            # 启用按钮
            self.copy_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

        else:
            self.progress_label.config(text="✅ 未检测到敏感信息，文本安全", fg='#4CAF50')
            details = "✅ 未检测到敏感信息\n\n"
            details += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            details += "您的文本是安全的，可以放心使用。"

            self.details_text.insert('1.0', details)

            # 仍然启用复制和保存
            self.copy_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

        # 恢复检测按钮
        self.check_button.config(state=tk.NORMAL, text="🔍 检测并混淆")

    def copy_output(self):
        """复制输出到剪贴板"""
        text = self.output_text.get('1.0', tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("成功", "已复制到剪贴板！")

    def save_file(self):
        """保存文件"""
        text = self.output_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "没有内容可保存！")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("成功", f"文件已保存到：\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

    def load_file(self):
        """加载文件"""
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("Markdown文件", "*.md"), ("所有文件", "*.*")])

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                self.progress_label.config(text=f"✓ 已加载文件: {Path(file_path).name}", fg='#4CAF50')
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {e}")

    def clear_all(self):
        """清空所有内容"""
        self.input_text.delete('1.0', tk.END)
        self.output_text.delete('1.0', tk.END)
        self.details_text.delete('1.0', tk.END)
        self.progress_label.config(text="就绪", fg='#4CAF50')
        self.copy_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)


def main():
    """主函数"""
    root = tk.Tk()
    app = GuardianGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
