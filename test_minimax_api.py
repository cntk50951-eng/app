#!/usr/bin/env python3
"""
Test script to verify MiniMax API integration.
"""

import os
import sys

# Add project to path
sys.path.insert(0, '/Volumes/Newsmy1 - m/app/web-poc')

from dotenv import load_dotenv
load_dotenv()

from services.ai_generator import (
    call_minimax_api,
    generate_text_content,
    generate_mock_content,
    get_topic_title
)
import json

def test_minimax_api():
    """Test MiniMax API connectivity and response."""
    print("=" * 60)
    print("MiniMax API Integration Test")
    print("=" * 60)

    # Check API key
    api_key = os.getenv('MINIMAX_API_KEY')
    print(f"\n1. API Key configured: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"   Key preview: {api_key[:10]}...")

    # Test text generation
    print(f"\n2. Testing text generation...")
    system_prompt = "你是香港資深升小面試導師，擁有 10 年教學經驗。"
    user_prompt = "請用粵語介紹你自己。"

    result = call_minimax_api("text/chatcompletion_v2", {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    })

    print(f"   Response received: {'Yes' if result else 'No'}")
    if result:
        print(f"   Response keys: {list(result.keys())}")
        if 'choices' in result:
            content = result['choices'][0]['message']['content']
            print(f"   Content preview: {content[:200]}...")
        else:
            print(f"   Full response: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")

    # Test prompt template
    print(f"\n3. Testing prompt template...")
    profile = {
        'child_name': '小明',
        'child_age': 'K2',
        'child_gender': '男',
        'interests': ['Lego', '恐龍'],
        'target_schools': ['academic']
    }

    mock_result = generate_mock_content('self-introduction', profile)
    print(f"   Mock data generated: Yes")
    print(f"   Teaching goal: {mock_result.get('teaching_goal', 'N/A')}")

    # Test topic title
    print(f"\n4. Testing topic titles...")
    topics = ['self-introduction', 'interests', 'family', 'observation', 'scenarios']
    for topic in topics:
        title = get_topic_title(topic)
        print(f"   {topic}: {title}")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

    return result is not None

if __name__ == '__main__':
    success = test_minimax_api()
    sys.exit(0 if success else 1)
