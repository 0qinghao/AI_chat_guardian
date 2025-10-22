"""
AI Chat Guardian - 图形用户界面
"""
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src import ChatGuardian, setup_logging


class GuardianGUI:
    """AI Chat Guardian GUI应用"""
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat Guardian - AI聊天守护者")
        self.root.geometry("900x700")

        # 初始化守护者
        setup_logging('WARNING')  # GUI模式使用WARNING级别
        try:
            self.guardian = ChatGuardian()
        except Exception as e:
            messagebox.showerror("初始化错误", f"初始化失败: {e}")
            self.root.quit()
            return

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 设置样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))

        # 顶部标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(title_frame, text="🛡️ AI Chat Guardian - 保护您的敏感信息", style='Title.TLabel')
        title_label.pack()

        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：输入区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_label = ttk.Label(left_frame, text="输入文本（粘贴待检测内容）：")
        input_label.pack(anchor=tk.W)

        self.input_text = scrolledtext.ScrolledText(left_frame, width=40, height=20, wrap=tk.WORD, font=('Consolas', 10))
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X)

        self.check_button = ttk.Button(button_frame, text="🔍 检测敏感信息", command=self.check_text)
        self.check_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(button_frame, text="🗑️ 清空", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(button_frame, text="📂 加载文件", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # 右侧：输出区域
        right_frame = ttk.Frame(main_frame, padding=(10, 0, 0, 0))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        output_label = ttk.Label(right_frame, text="安全文本（已混淆）：")
        output_label.pack(anchor=tk.W)

        self.output_text = scrolledtext.ScrolledText(right_frame, width=40, height=20, wrap=tk.WORD, font=('Consolas', 10), bg='#f0f8ff')
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # 输出按钮区域
        output_button_frame = ttk.Frame(right_frame)
        output_button_frame.pack(fill=tk.X)

        self.copy_button = ttk.Button(output_button_frame, text="📋 复制到剪贴板", command=self.copy_output, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(output_button_frame, text="💾 保存文件", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # 底部：状态和详情区域
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.BOTH)

        # 状态栏
        self.status_label = ttk.Label(bottom_frame, text="就绪", style='Status.TLabel', relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, pady=(0, 5))

        # 检测详情
        details_label = ttk.Label(bottom_frame, text="检测详情：")
        details_label.pack(anchor=tk.W)

        self.details_text = scrolledtext.ScrolledText(bottom_frame, height=8, wrap=tk.WORD, font=('Consolas', 9), bg='#fffaf0')
        self.details_text.pack(fill=tk.BOTH, expand=True)

    def check_text(self):
        """检测文本"""
        text = self.input_text.get('1.0', tk.END).strip()

        if not text:
            messagebox.showwarning("警告", "请输入要检测的文本！")
            return

        try:
            self.status_label.config(text="正在检测...")
            self.root.update()

            # 执行检测
            result = self.guardian.check_text(text)

            # 显示结果
            self.display_result(result)

        except Exception as e:
            messagebox.showerror("错误", f"检测失败: {e}")
            self.status_label.config(text="检测失败")

    def display_result(self, result):
        """显示检测结果"""
        # 清空输出
        self.output_text.delete('1.0', tk.END)
        self.details_text.delete('1.0', tk.END)

        # 显示安全文本
        self.output_text.insert('1.0', result.safe_text)

        # 显示详情
        if result.has_sensitive:
            self.status_label.config(text=f"⚠️ 检测到 {result.detection_count} 处敏感信息！", )

            details = f"检测结果摘要：\n"
            details += f"{'='*60}\n"
            details += f"敏感信息数量: {result.detection_count}\n\n"

            # 按类型分组
            type_groups = {}
            for detection in result.detections:
                det_type = detection['type']
                if det_type not in type_groups:
                    type_groups[det_type] = []
                type_groups[det_type].append(detection)

            details += "按类型统计：\n"
            for det_type, detections in type_groups.items():
                details += f"\n  [{det_type}] 共 {len(detections)} 处:\n"
                for i, det in enumerate(detections, 1):
                    content = det['content']
                    if len(content) > 50:
                        content = content[:50] + "..."
                    confidence = det['confidence'] * 100
                    details += f"    {i}. {content}\n"
                    details += f"       (置信度: {confidence:.1f}%, 位置: {det['position'][0]}-{det['position'][1]})\n"

            self.details_text.insert('1.0', details)

            # 启用按钮
            self.copy_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

        else:
            self.status_label.config(text="✅ 未检测到敏感信息，文本安全！")
            self.details_text.insert('1.0', "✓ 未检测到敏感信息\n\n文本可以安全使用。")

            # 仍然启用复制和保存
            self.copy_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

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
                self.status_label.config(text=f"已加载文件: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {e}")

    def clear_all(self):
        """清空所有内容"""
        self.input_text.delete('1.0', tk.END)
        self.output_text.delete('1.0', tk.END)
        self.details_text.delete('1.0', tk.END)
        self.status_label.config(text="就绪")
        self.copy_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)


def main():
    """主函数"""
    root = tk.Tk()
    app = GuardianGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
