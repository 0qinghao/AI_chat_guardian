"""
AI检测器功能测试
测试三种检测模式的效果
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detectors import AIDetector
from src import setup_logging


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_detection_results(results, text):
    """打印检测结果"""
    if not results:
        print(f"✓ 文本: {text}")
        print("  → 未检测到敏感信息")
    else:
        print(f"✗ 文本: {text}")
        for match in results:
            print(f"  → 类别: {match.category:12} | 置信度: {match.confidence:.2f} | 内容: {match.text[:50]}...")


def test_enhanced_keywords_mode():
    """测试增强关键词模式"""
    print_header("测试 1: 增强关键词模式（默认模式，无需额外依赖）")

    # 初始化检测器（自动使用增强关键词模式）
    detector = AIDetector(mode="keyword-enhanced")

    print(f"\n模型信息: {detector.get_model_info()}")

    # 测试用例
    test_cases = [
        ("我们公司Q3营业额5.8亿元，净利润8500万", True),
        ("员工薪资调整方案已提交审批", True),
        ("这是公司的战略规划文档，标记为机密", True),
        ("数据库架构设计和技术方案", True),
        ("客户名单和合同金额统计", True),
        ("今天天气不错，适合出去玩", False),
        ("Python编程最佳实践", False),
    ]

    print("\n开始检测:\n")
    for text, should_detect in test_cases:
        results = detector.detect(text, threshold=0.6)
        print_detection_results(results, text)

        # 验证
        has_detection = len(results) > 0
        status = "✓" if has_detection == should_detect else "✗"
        print(f"  {status} 预期: {'有' if should_detect else '无'}敏感信息 | 实际: {'有' if has_detection else '无'}敏感信息\n")


def test_zero_shot_mode():
    """测试零样本分类模式"""
    print_header("测试 2: 零样本分类模式（需要 transformers 库）")

    try:
        # 尝试初始化零样本分类器
        print("\n正在加载模型（首次运行可能需要下载，请稍候）...")
        detector = AIDetector(model_name="bert-base-chinese", use_gpu=False, mode="zero-shot")

        if detector.model == "zero-shot":
            print("✓ 零样本分类器加载成功！")
            print(f"\n模型信息: {detector.get_model_info()}")

            # 测试用例
            test_cases = [
                "我们今年的财务目标是营收增长20%，成本降低15%",
                "附件包含完整的员工名单和联系方式",
                "这份战略规划文档涉及未来三年的发展方向",
                "系统采用微服务架构，数据库使用MySQL",
                "重要客户的商务合同即将到期",
            ]

            print("\n开始检测:\n")
            for text in test_cases:
                results = detector.detect(text, threshold=0.7)
                print_detection_results(results, text)
                print()
        else:
            print("✗ 零样本分类器未能加载，可能缺少必要的库")
            print("  请运行: pip install transformers torch")

    except Exception as e:
        print(f"✗ 零样本分类模式测试失败: {e}")
        print("  这是正常的，如果未安装 transformers 库")
        print("  安装方法: pip install transformers torch")


def test_similarity_mode():
    """测试相似度匹配模式"""
    print_header("测试 3: 相似度匹配模式（需要 sentence-transformers 库）")

    try:
        print("\n正在加载模型（首次运行可能需要下载，请稍候）...")
        detector = AIDetector(model_name="paraphrase-multilingual-MiniLM-L12-v2", use_gpu=False, mode="similarity")

        if detector.model == "similarity":
            print("✓ 相似度匹配模型加载成功！")
            print(f"\n模型信息: {detector.get_model_info()}")

            # 测试用例
            test_cases = [
                "关于公司利润和收入的讨论",
                "人力资源部门的薪酬调整",
                "商业计划和市场策略",
                "技术实现和代码优化",
                "客户关系管理系统",
            ]

            print("\n开始检测:\n")
            for text in test_cases:
                results = detector.detect(text, threshold=0.75)
                print_detection_results(results, text)
                print()
        else:
            print("✗ 相似度匹配模型未能加载")
            print("  请运行: pip install sentence-transformers")

    except Exception as e:
        print(f"✗ 相似度匹配模式测试失败: {e}")
        print("  这是正常的，如果未安装 sentence-transformers 库")
        print("  安装方法: pip install sentence-transformers")


def test_comparison():
    """对比三种模式"""
    print_header("测试 4: 三种模式对比")

    test_text = "我们公司今年的营业额达到5.8亿元，这是财务报表中的数据"

    print(f"\n测试文本: {test_text}\n")

    modes = [("增强关键词", "keyword-enhanced"), ("零样本分类", "zero-shot"), ("相似度匹配", "similarity")]

    for mode_name, mode_value in modes:
        print(f"\n{mode_name}模式:")
        try:
            detector = AIDetector(mode=mode_value)
            results = detector.detect(test_text, threshold=0.7)

            if results:
                for match in results:
                    print(f"  → {match.category}: {match.confidence:.2f}")
            else:
                print("  → 未检测到敏感信息")

        except Exception as e:
            print(f"  ✗ 无法测试（可能缺少依赖）: {e}")


def test_threshold_sensitivity():
    """测试阈值敏感度"""
    print_header("测试 5: 阈值敏感度分析")

    detector = AIDetector(mode="keyword-enhanced")
    test_text = "讨论一下公司的预算和成本控制"

    print(f"\n测试文本: {test_text}\n")
    print("不同阈值下的检测结果:")

    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]

    for threshold in thresholds:
        results = detector.detect(test_text, threshold=threshold)
        print(f"\n阈值 {threshold:.1f}:")
        if results:
            for match in results:
                print(f"  → {match.category}: {match.confidence:.2f}")
        else:
            print("  → 无检测结果")


def test_edge_cases():
    """测试边界情况"""
    print_header("测试 6: 边界情况")

    detector = AIDetector(mode="keyword-enhanced")

    edge_cases = [
        ("", "空字符串"),
        ("a", "单字符"),
        ("这是一个很短的句子", "短句子"),
        ("这" * 500, "超长重复文本"),
        ("12345 @#$%^ []{}()", "纯符号"),
        ("Hello world! 你好世界！", "中英文混合"),
    ]

    print("\n")
    for text, description in edge_cases:
        print(f"{description}: ", end="")
        try:
            results = detector.detect(text, threshold=0.7)
            print(f"{'有' if results else '无'}检测结果")
        except Exception as e:
            print(f"出错: {e}")


def run_all_tests():
    """运行所有测试"""
    setup_logging('INFO')

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "AI检测器功能测试" + " " * 32 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # 测试1：增强关键词模式（必定可用）
        test_enhanced_keywords_mode()

        # 测试2：零样本分类模式（需要依赖）
        test_zero_shot_mode()

        # 测试3：相似度匹配模式（需要依赖）
        test_similarity_mode()

        # 测试4：模式对比
        test_comparison()

        # 测试5：阈值敏感度
        test_threshold_sensitivity()

        # 测试6：边界情况
        test_edge_cases()

        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)

        print("\n📝 注意事项:")
        print("  1. 增强关键词模式无需额外依赖，始终可用")
        print("  2. 零样本分类和相似度匹配需要安装额外的库")
        print("  3. 首次运行可能需要下载模型文件")
        print("  4. 推荐使用零样本分类模式以获得最佳效果")

        print("\n💡 安装完整功能:")
        print("  pip install transformers torch sentence-transformers")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
