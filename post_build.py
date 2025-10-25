"""
打包后处理脚本
将config和examples文件夹从_internal复制到exe同目录
"""
import shutil
import sys
from pathlib import Path

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 打包输出目录
dist_dir = Path(__file__).parent / "dist" / "AI_Chat_Guardian"
internal_dir = dist_dir / "_internal"

# 要复制的目录
folders_to_copy = ["config", "examples"]

print("=" * 60)
print("打包后处理：复制配置文件到exe同目录")
print("=" * 60)

for folder in folders_to_copy:
    src = internal_dir / folder
    dst = dist_dir / folder

    if src.exists():
        # 如果目标已存在，先删除
        if dst.exists():
            shutil.rmtree(dst)
            print(f"✓ 删除旧的 {folder}")

        # 复制整个目录
        shutil.copytree(src, dst)
        print(f"✓ 复制 {folder} 到exe同目录")
    else:
        print(f"✗ 源目录不存在: {src}")

# 复制.env.example
env_src = Path(__file__).parent / ".env.example"
env_dst = dist_dir / ".env.example"
if env_src.exists():
    shutil.copy2(env_src, env_dst)
    print(f"✓ 复制 .env.example")

# 复制README
readme_src = Path(__file__).parent / "README.md"
readme_dst = dist_dir / "README.md"
if readme_src.exists():
    shutil.copy2(readme_src, readme_dst)
    print(f"✓ 复制 README.md")

print("=" * 60)
print("✅ 处理完成！")
print(f"\n最终结构:")
print(f"  {dist_dir.name}/")
print(f"    ├── AI_Chat_Guardian.exe")
print(f"    ├── config/              ← 配置文件（可编辑）")
print(f"    ├── examples/            ← 示例文件")
print(f"    ├── .env.example         ← API密钥模板")
print(f"    ├── README.md            ← 使用说明")
print(f"    └── _internal/           ← 依赖文件")
print("=" * 60)
