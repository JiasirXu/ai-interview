import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查接口"""
    print("=== 测试健康检查接口 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_dimensions():
    """测试获取维度信息接口"""
    print("\n=== 测试获取维度信息接口 ===")
    try:
        response = requests.get(f"{BASE_URL}/dimensions")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print("评分维度:")
        for key, value in data.items():
            print(f"  {key}: {value['name']} - {value['description']}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_predict():
    """测试单文本预测接口"""
    print("\n=== 测试单文本预测接口 ===")
    test_text = "我认为这个职位非常适合我，因为我有三年的相关工作经验，熟悉行业发展趋势，并且具备良好的沟通能力和团队合作精神。我相信我能够为公司带来价值。"
    
    try:
        response = requests.post(f"{BASE_URL}/predict", 
                               json={"text": test_text})
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print("预测成功!")
            scores = data["data"]
            print(f"输入文本: {scores['text'][:50]}...")
            print("评分结果:")
            dimensions = ["clarity", "relevance", "logic", "fluency", 
                         "confidence", "professionality", "completeness", "empathy"]
            for dim in dimensions:
                print(f"  {dim}: {scores[dim]}")
        else:
            print(f"预测失败: {data}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_batch_predict():
    """测试批量预测接口"""
    print("\n=== 测试批量预测接口 ===")
    test_texts = [
        "我有丰富的项目管理经验，能够有效协调团队资源。",
        "虽然我在这个领域经验不多，但我学习能力很强，愿意接受挑战。"
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/batch_predict", 
                               json={"texts": test_texts})
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print("批量预测成功!")
            for result in data["results"]:
                if "data" in result:
                    print(f"文本 {result['index']}: {result['data']['text'][:30]}...")
                    print(f"  clarity: {result['data']['clarity']}")
                else:
                    print(f"文本 {result['index']}: 预测失败 - {result['error']}")
        else:
            print(f"批量预测失败: {data}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试AI模拟面试评分API...")
    print("请确保API服务已启动 (python app.py)")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 执行测试
    tests = [
        ("健康检查", test_health),
        ("获取维度信息", test_dimensions),
        ("单文本预测", test_predict),
        ("批量预测", test_batch_predict)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # 间隔1秒
    
    # 输出测试结果汇总
    print(f"\n{'='*50}")
    print("测试结果汇总:")
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 个测试通过")

if __name__ == "__main__":
    main()
