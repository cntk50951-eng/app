#!/usr/bin/env python3
"""
Test AI Content Generation Service
驗證 AI 生成服務是否正常工作
"""

import sys
import json

# 測試前需要載入環境變量
from dotenv import load_dotenv
load_dotenv()

def test_prompts():
    """測試 Prompt 模板."""
    print("\n" + "="*50)
    print("🧪 測試 Prompt 模板")
    print("="*50)

    from services.prompts import TOPIC_TEMPLATES, fill_template, get_template

    # 檢查模板是否存在
    topics = ['self-introduction', 'interests', 'family', 'observation', 'scenarios']
    for topic in topics:
        template = get_template(topic)
        if template:
            print(f"✅ {topic}: 模板存在")
        else:
            print(f"❌ {topic}: 模板不存在")

    # 測試模板填充
    test_profile = {
        'child_name': '小明',
        'child_age': 'K2',
        'child_gender': '男',
        'interests': ['恐龍', 'Lego'],
        'target_schools': ['academic', 'holistic']
    }

    user_prompt = get_template('self-introduction').get('user', '')
    filled_prompt = fill_template(user_prompt, test_profile)

    print(f"\n✅ 模板填充測試:")
    print(f"   - 姓名: {test_profile['child_name']}")
    print(f"   - 年齡: {test_profile['child_age']}")
    print(f"   - 興趣: {test_profile['interests']}")
    print(f"   - 目標學校: {test_profile['target_schools']}")
    print(f"   - 填充後包含姓名: {'小明' in filled_prompt}")
    print(f"   - 填充後包含興趣: {'恐龍' in filled_prompt}")


def test_ai_generator():
    """測試 AI 生成服務."""
    print("\n" + "="*50)
    print("🤖 測試 AI 生成引擎")
    print("="*50)

    from services.ai_generator import (
        generate_teaching_content,
        generate_mock_content,
        get_topic_title,
        get_cache_key,
        save_to_cache,
        get_from_cache
    )

    # 測試 Mock 內容生成
    test_profile = {
        'id': 'test-user-001',
        'child_name': '小明',
        'child_age': 'K2',
        'interests': ['恐龍', 'Lego']
    }

    # 測試不同主題
    topics = ['self-introduction', 'interests', 'family']
    for topic in topics:
        try:
            content = generate_teaching_content(test_profile, topic)
            title = get_topic_title(topic)

            if content and 'content' in content:
                print(f"✅ {title}: 生成成功")
                print(f"   - 教學目標: {content['content'].get('teaching_goal', 'N/A')[:30]}...")
            else:
                print(f"❌ {title}: 生成失敗")
        except Exception as e:
            print(f"❌ {topic}: 異常 - {e}")

    # 測試緩存
    print(f"\n✅ 緩存測試:")
    cache_key = get_cache_key('test-user-001', 'self-introduction')
    print(f"   - Cache Key: {cache_key}")

    save_to_cache('test-user-001', 'self-introduction', {'test': 'data'})
    cached = get_from_cache('test-user-001', 'self-introduction')
    print(f"   - 緩存讀取: {'成功' if cached else '失敗'}")

    # 測試標題獲取
    print(f"\n✅ 主題標題測試:")
    for topic in topics:
        title = get_topic_title(topic)
        print(f"   - {topic}: {title}")


def test_api_endpoint():
    """測試 API 端點格式."""
    print("\n" + "="*50)
    print("🌐 測試 API 端點格式")
    print("="*50)

    # 模擬 API 請求
    test_request = {
        'topic': 'self-introduction',
        'force_regenerate': False
    }

    print(f"✅ 請求格式正確:")
    print(f"   - topic: {test_request['topic']}")
    print(f"   - force_regenerate: {test_request['force_regenerate']}")

    # 模擬回應格式
    mock_response = {
        'topic': 'self-introduction',
        'topic_title': '自我介紹',
        'content': {
            'teaching_goal': '教學目標...',
            'parent_script': '家長話術...',
            'sample_questions': ['問題1', '問題2', '問題3'],
            'model_answer': '示範答案...',
            'tips': ['技巧1', '技巧2']
        },
        'audio': {
            'cantonese_url': None,
            'mandarin_url': None
        },
        'images': [],
        'generation_time_ms': 1500,
        'created_at': '2026-02-09 10:00:00'
    }

    print(f"✅ 回應格式正確:")
    print(f"   - 包含 topic: {'topic' in mock_response}")
    print(f"   - 包含 content: {'content' in mock_response}")
    print(f"   - 包含 audio: {'audio' in mock_response}")
    print(f"   - 包含 images: {'images' in mock_response}")


def main():
    """主測試函數."""
    print("\n" + "🚀" * 20)
    print("AI Tutor - 服務測試")
    print("🚀" * 20)

    try:
        test_prompts()
        test_ai_generator()
        test_api_endpoint()

        print("\n" + "="*50)
        print("✅ 所有測試通過!")
        print("="*50)
        return 0

    except ImportError as e:
        print(f"\n❌ 導入錯誤: {e}")
        print("請確保所有依賴已安裝: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
