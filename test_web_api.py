"""
测试Web服务API端点
"""
import requests
import json

BASE_URL = "http://localhost:5000"


def test_health():
    """测试健康检查端点"""
    print("\n" + "=" * 60)
    print("测试 /api/health")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_detect():
    """测试检测端点"""
    print("\n" + "=" * 60)
    print("测试 /api/detect")
    print("=" * 60)

    test_text = "公司Q3营收5000万元，API密钥sk-123456，员工张三的薪资为50万元/年"

    try:
        response = requests.post(f"{BASE_URL}/api/detect", json={"text": test_text, "auto_obfuscate": True}, timeout=30)
        print(f"状态码: {response.status_code}")
        data = response.json()

        if data['success']:
            result = data['data']
            print(f"\n✓ 检测成功")
            print(f"  - 敏感信息数量: {result['detection_count']}")
            print(f"  - 原始文本: {result['original_text']}")
            print(f"  - 混淆后: {result['safe_text']}")

            if result['detections']:
                print(f"\n  检测详情:")
                for det in result['detections']:
                    print(f"    [{det['type']}] {det['content']} (置信度: {det['confidence']*100:.1f}%)")
        else:
            print(f"❌ 失败: {data.get('error', '未知错误')}")

        return response.status_code == 200 and data['success']
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_config():
    """测试配置端点"""
    print("\n" + "=" * 60)
    print("测试 /api/config")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/config", timeout=5)
        print(f"状态码: {response.status_code}")
        data = response.json()

        if data['success']:
            config = data['config']
            print(f"\n✓ 获取配置成功")
            print(f"  LLM配置:")
            llm = config.get('llm_detector', {})
            print(f"    - 启用: {llm.get('enable')}")
            print(f"    - 模型: {llm.get('model')}")
            print(f"    - 阈值: {llm.get('threshold')}")

        return response.status_code == 200 and data['success']
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_models():
    """测试模型列表端点"""
    print("\n" + "=" * 60)
    print("测试 /api/models")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/models", timeout=5)
        print(f"状态码: {response.status_code}")
        data = response.json()

        if data['success']:
            print(f"\n✓ 获取模型列表成功")
            print(f"  当前模型: {data['current_model']}")
            print(f"  可用模型:")
            for model in data['models']:
                print(f"    - {model['name']:20s} {model.get('description', '')}")

        return response.status_code == 200 and data['success']
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


if __name__ == '__main__':
    print("\n🧪 AI Chat Guardian Web服务API测试")
    print("=" * 60)
    print(f"目标地址: {BASE_URL}")
    print("\n⚠️  请确保Web服务已启动 (运行 start_web.bat 或 python web_server.py)")
    print("=" * 60)

    input("\n按回车键开始测试...")

    results = []
    results.append(("健康检查", test_health()))
    results.append(("配置获取", test_config()))
    results.append(("模型列表", test_models()))
    results.append(("文本检测", test_detect()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name:15s} {status}")

    passed = sum(1 for _, s in results if s)
    print(f"\n总计: {passed}/{len(results)} 通过")

    if passed == len(results):
        print("\n🎉 所有测试通过！Web服务运行正常。")
    else:
        print("\n⚠️  部分测试失败，请检查服务状态。")
