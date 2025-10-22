"""
AI Chat Guardian - 命令行界面
"""
import sys
import argparse
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src import ChatGuardian, setup_logging
from src.utils import load_config

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

    # 如果没有colorama，定义占位符
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = WHITE = RESET = ''

    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''


def print_colored(text: str, color=Fore.WHITE, bright=False):
    """打印彩色文本"""
    if HAS_COLORAMA:
        style = Style.BRIGHT if bright else Style.NORMAL
        print(f"{style}{color}{text}{Style.RESET_ALL}")
    else:
        print(text)


def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║        AI Chat Guardian (AI聊天守护者)            ║
    ║                                                  ║
    ║        保护您的敏感信息，安全使用AI工具            ║
    ╚══════════════════════════════════════════════════╝
    """
    print_colored(banner, Fore.CYAN, bright=True)


def print_result(result):
    """打印检测结果"""
    print_colored("\n" + "=" * 60, Fore.CYAN)
    print_colored("检测结果", Fore.CYAN, bright=True)
    print_colored("=" * 60, Fore.CYAN)

    if result.has_sensitive:
        print_colored(f"\n⚠️  检测到 {result.detection_count} 处敏感信息！", Fore.RED, bright=True)

        # 按类型分组显示
        type_groups = {}
        for detection in result.detections:
            det_type = detection['type']
            if det_type not in type_groups:
                type_groups[det_type] = []
            type_groups[det_type].append(detection)

        print_colored("\n详细信息：", Fore.YELLOW)
        for det_type, detections in type_groups.items():
            print_colored(f"\n  [{det_type}] 共 {len(detections)} 处:", Fore.YELLOW)
            for i, det in enumerate(detections, 1):
                content = det['content']
                # 截断过长的内容
                if len(content) > 50:
                    content = content[:50] + "..."
                confidence = det['confidence'] * 100
                print(f"    {i}. {content} (置信度: {confidence:.1f}%)")

        # 显示安全文本
        print_colored("\n" + "-" * 60, Fore.GREEN)
        print_colored("✅ 安全文本（已混淆）：", Fore.GREEN, bright=True)
        print_colored("-" * 60, Fore.GREEN)
        print(f"\n{result.safe_text}\n")

    else:
        print_colored("\n✓ 未检测到敏感信息，文本安全！", Fore.GREEN, bright=True)
        print(f"\n{result.original_text}\n")

    # 显示警告
    if result.warnings:
        print_colored("\n警告信息：", Fore.YELLOW)
        for warning in result.warnings:
            print_colored(f"  ⚠ {warning}", Fore.YELLOW)


def interactive_mode(guardian: ChatGuardian):
    """交互式模式"""
    print_colored("\n进入交互式模式（输入 'exit' 或 'quit' 退出）", Fore.CYAN)
    print_colored("提示：可以直接粘贴多行文本，输入空行结束输入\n", Fore.CYAN)

    while True:
        try:
            print_colored("请输入要检测的文本：", Fore.YELLOW)

            # 读取多行输入
            lines = []
            while True:
                try:
                    line = input()
                    if line.lower() in ['exit', 'quit']:
                        print_colored("\n感谢使用 AI Chat Guardian！", Fore.CYAN, bright=True)
                        return
                    if not line and lines:  # 空行表示结束输入
                        break
                    lines.append(line)
                except EOFError:
                    break

            if not lines:
                continue

            text = '\n'.join(lines)

            # 检测
            print_colored("\n正在检测...", Fore.CYAN)
            result = guardian.check_text(text)

            # 显示结果
            print_result(result)

            # 询问是否继续
            print_colored("\n按 Enter 继续检测，或输入 'exit' 退出", Fore.CYAN)
            choice = input().strip().lower()
            if choice in ['exit', 'quit']:
                print_colored("\n感谢使用 AI Chat Guardian！", Fore.CYAN, bright=True)
                break

        except KeyboardInterrupt:
            print_colored("\n\n感谢使用 AI Chat Guardian！", Fore.CYAN, bright=True)
            break
        except Exception as e:
            print_colored(f"\n错误: {e}", Fore.RED)


def file_mode(guardian: ChatGuardian, file_path: str, output_path: str = None):
    """文件模式"""
    print_colored(f"\n正在检测文件: {file_path}", Fore.CYAN)

    result = guardian.check_file(file_path)
    print_result(result)

    # 保存安全文本到文件
    if output_path and result.has_sensitive:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.safe_text)
            print_colored(f"\n安全文本已保存到: {output_path}", Fore.GREEN)
        except Exception as e:
            print_colored(f"\n保存文件失败: {e}", Fore.RED)


def batch_mode(guardian: ChatGuardian, directory: str):
    """批量处理模式"""
    from pathlib import Path

    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        print_colored(f"错误: 目录不存在: {directory}", Fore.RED)
        return

    # 查找文本文件
    text_files = list(dir_path.glob('**/*.txt')) + list(dir_path.glob('**/*.md'))

    if not text_files:
        print_colored(f"在 {directory} 中未找到文本文件", Fore.YELLOW)
        return

    print_colored(f"\n找到 {len(text_files)} 个文件，开始批量检测...\n", Fore.CYAN)

    total_sensitive = 0
    results_summary = []

    for file_path in text_files:
        print_colored(f"检测: {file_path.name}", Fore.CYAN)
        result = guardian.check_file(str(file_path))

        if result.has_sensitive:
            total_sensitive += 1
            results_summary.append({'file': file_path.name, 'count': result.detection_count})
            print_colored(f"  ⚠ 发现 {result.detection_count} 处敏感信息", Fore.YELLOW)
        else:
            print_colored(f"  ✓ 安全", Fore.GREEN)

    # 显示总结
    print_colored("\n" + "=" * 60, Fore.CYAN)
    print_colored("批量检测总结", Fore.CYAN, bright=True)
    print_colored("=" * 60, Fore.CYAN)
    print(f"\n总文件数: {len(text_files)}")
    print(f"包含敏感信息的文件: {total_sensitive}")

    if results_summary:
        print_colored("\n敏感文件列表：", Fore.YELLOW)
        for item in results_summary:
            print(f"  - {item['file']}: {item['count']} 处")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI Chat Guardian - 保护您的敏感信息',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
示例:
  python main.py                          # 交互式模式
  python main.py -f input.txt             # 检测文件
  python main.py -f input.txt -o safe.txt # 检测并保存安全文本
  python main.py -b ./documents           # 批量检测目录
        """)

    parser.add_argument('-f', '--file', help='检测文件')
    parser.add_argument('-o', '--output', help='输出文件路径（保存安全文本）')
    parser.add_argument('-b', '--batch', help='批量检测目录')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--no-color', action='store_true', help='禁用颜色输出')

    args = parser.parse_args()

    # 禁用颜色
    if args.no_color:
        global HAS_COLORAMA
        HAS_COLORAMA = False

    # 打印横幅
    print_banner()

    # 设置日志
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level)

    # 初始化守护者
    try:
        print_colored("\n正在初始化...", Fore.CYAN)
        guardian = ChatGuardian(config_path=args.config)
        print_colored("✓ 初始化完成\n", Fore.GREEN)
    except Exception as e:
        print_colored(f"初始化失败: {e}", Fore.RED)
        return 1

    # 根据参数选择模式
    try:
        if args.file:
            file_mode(guardian, args.file, args.output)
        elif args.batch:
            batch_mode(guardian, args.batch)
        else:
            interactive_mode(guardian)
    except Exception as e:
        print_colored(f"\n运行错误: {e}", Fore.RED)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
