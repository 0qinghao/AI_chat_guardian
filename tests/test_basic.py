"""
测试 AI Chat Guardian 的基本功能
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ChatGuardian, setup_logging


def test_regex_detection():
    """测试正则表达式检测"""
    print("\n" + "=" * 60)
    print("测试 1: 正则表达式检测")
    print("=" * 60)

    guardian = ChatGuardian()

    test_texts = [
        "请联系张三，邮箱：zhangsan@company.com，电话：13812345678",
        "我的身份证号是：110101199001011234",
        "API密钥：sk-1234567890abcdef1234567890abcdef",
        "数据库连接：mysql://user:password@localhost:3306/mydb",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i}:")
        print(f"原文: {text}")

        result = guardian.check_text(text)
        print(f"检测结果: {'发现敏感信息' if result.has_sensitive else '安全'}")
        print(f"敏感信息数量: {result.detection_count}")
        print(f"安全文本: {result.safe_text}")


def test_keyword_detection():
    """测试关键词检测"""
    print("\n" + "=" * 60)
    print("测试 2: 关键词检测")
    print("=" * 60)

    guardian = ChatGuardian()

    test_texts = [
        "这是我们公司的财务报表，包含营业额和净利润数据",
        "员工名单如下，包含工号和联系方式",
        "这是我们的战略规划文档，标记为机密",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i}:")
        print(f"原文: {text}")

        result = guardian.check_text(text)
        print(f"检测结果: {'发现敏感信息' if result.has_sensitive else '安全'}")
        print(f"敏感信息数量: {result.detection_count}")
        if result.has_sensitive:
            for detection in result.detections:
                print(f"  - 类型: {detection['type']}, 内容: {detection['content']}")


def test_mixed_content():
    """测试混合内容"""
    print("\n" + "=" * 60)
    print("测试 3: 混合内容检测")
    print("=" * 60)

    guardian = ChatGuardian()

    text = """
    嗨，我想咨询一下关于项目的问题。
    
    我们团队负责人是李明（limming@company.com，电话：13900001234）。
    项目预算大约500万元，这是财务报表中的数据。
    
    需要连接到数据库：mysql://admin:SecretPass123@10.0.0.100:3306/project_db
    
    另外，API密钥是：AKIA1234567890ABCDEF
    
    请帮我分析一下这些代码的性能问题。
    """

    print("测试文本:")
    print(text)

    result = guardian.check_text(text)

    print(f"\n检测结果:")
    print(f"  发现 {result.detection_count} 处敏感信息")
    print(f"\n详细信息:")
    for detection in result.detections:
        print(f"  - 类型: {detection['type']}")
        print(f"    内容: {detection['content']}")
        print(f"    置信度: {detection['confidence']:.2f}")

    print(f"\n安全文本:")
    print(result.safe_text)


def test_no_sensitive():
    """测试无敏感信息的文本"""
    print("\n" + "=" * 60)
    print("测试 4: 无敏感信息")
    print("=" * 60)

    guardian = ChatGuardian()

    text = "你好，我想了解一下关于Python编程的最佳实践，特别是代码优化方面的建议。"

    print(f"测试文本: {text}")

    result = guardian.check_text(text)
    print(f"检测结果: {'发现敏感信息' if result.has_sensitive else '安全'}")
    print(f"安全文本: {result.safe_text}")


def run_all_tests():
    """运行所有测试"""
    setup_logging('WARNING')

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "AI Chat Guardian 测试" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")

    try:
        test_regex_detection()
        test_keyword_detection()
        test_mixed_content()
        test_no_sensitive()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
