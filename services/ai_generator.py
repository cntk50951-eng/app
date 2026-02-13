"""
AI Content Generator Service
香港升小面試 AI 導師 - AI 內容生成引擎

功能：
- 調用 MiniMax API 生成文字內容
- 生成粵語/普通話語音
- Redis 緩存機制
"""

import os
import json
import time
import hashlib
import requests
from functools import wraps
from services.prompts import fill_template, get_template


# ============ 配置 ============

MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1')

# 緩存配置（使用內存緩存替代 Redis，簡化 POC）
CACHE_TTL = 86400  # 24 小時


# ============ 緩存機制 ============

content_cache = {}


def get_cache_key(profile_id, topic):
    """生成緩存鍵."""
    return f"content:{profile_id}:{topic}"


def get_from_cache(profile_id, topic):
    """從緩存獲取."""
    key = get_cache_key(profile_id, topic)
    cached = content_cache.get(key)
    if cached:
        # 檢查是否過期
        if time.time() - cached['timestamp'] < CACHE_TTL:
            print(f"✅ Cache hit: {key}")
            return cached['data']
        else:
            del content_cache[key]
    return None


def save_to_cache(profile_id, topic, data):
    """保存到緩存."""
    key = get_cache_key(profile_id, topic)
    content_cache[key] = {
        'timestamp': time.time(),
        'data': data
    }
    print(f"💾 Cache saved: {key}")


# ============ MiniMax API 調用 ============

def call_minimax_api(endpoint, payload):
    """調用 MiniMax API."""
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API Key not configured")
        print(f"   Checking environment: MINIMAX_API_KEY={MINIMAX_API_KEY}")
        return None

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        url = f"{MINIMAX_BASE_URL}/{endpoint}"
        print(f"📡 Calling MiniMax API: {url}")

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            print(f"✅ MiniMax API success")
            return response.json()
        else:
            print(f"❌ MiniMax API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ MiniMax API exception: {e}")
        return None


def generate_text_content(system_prompt, user_prompt):
    """生成文字內容."""
    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and 'choices' in result:
        content = result['choices'][0]['message']['content']
        if not content or not content.strip():
            print("⚠️ Empty response from API")
            return None
        try:
            # 嘗試解析 JSON
            parsed = json.loads(content)
            # 驗證內容量效性
            if isinstance(parsed, dict) and len(parsed) > 0:
                return parsed
            else:
                print(f"⚠️ Invalid content structure: {parsed}")
                return None
        except json.JSONDecodeError:
            # 如果不是純 JSON，嘗試提取 JSON
            print(f"⚠️ Response is not pure JSON: {content[:200]}")
            # 嘗試從文本中提取有效內容
            if len(content) > 50:  # 如果文本足夠長，可能是有用的內容
                return {"raw_content": content}
            return None

    return None


def generate_speech(text, language='cantonese'):
    """生成語音（TTS）."""
    if language == 'cantonese':
        voice = "Canto-Female-1"
    else:
        voice = "Mandarin-Female-1"

    payload = {
        "model": "speech-01",
        "input": text,
        "voice": voice,
        "speed": 0.9,
        "stream": False
    }

    result = call_minimax_api("audio/speech", payload)

    if result:
        # 返回音頻 URL（實際上需要上傳到 R2）
        return {
            "audio_url": result.get('audio_url'),
            "language": language,
            "text_length": len(text)
        }

    return None


# ============ 主生成函數 ============

def generate_teaching_content(profile, topic_id):
    """
    生成完整教學內容（文字 + 語音 URL）

    Args:
        profile: 用戶畫像 dict
        topic_id: 主題 ID (self-introduction, interests, family, observation, scenarios)

    Returns:
        dict: 教學內容
    """
    profile_id = profile.get('id', 'anonymous')
    topic = topic_id

    # 1. 檢查緩存
    cached = get_from_cache(profile_id, topic)
    if cached and 'error' not in cached:
        return cached

    # 2. 獲取模板
    template = get_template(topic_id)
    if not template:
        return {"error": f"Unknown topic: {topic_id}", "fallback": True}

    # 3. 填充 Prompt
    system_prompt = template.get('system', '')
    user_prompt = fill_template(template.get('user', ''), profile)

    # 4. 生成文字內容
    print(f"🎯 Generating content for topic: {topic_id}")
    start_time = time.time()
    use_fallback = False

    try:
        text_content = generate_text_content(system_prompt, user_prompt)

        if not text_content:
            # API 调用失败，使用 fallback
            print("⚠️ Using fallback data (API call failed)")
            use_fallback = True
            text_content = generate_mock_content(topic_id, profile)
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        use_fallback = True
        text_content = generate_mock_content(topic_id, profile)

    generation_time = time.time() - start_time
    print(f"⏱️ Content generated in {generation_time:.2f}s (fallback: {use_fallback})")

    # 5. 組裝結果
    result = {
        "topic": topic_id,
        "topic_title": get_topic_title(topic_id),
        "profile_id": profile_id,
        "content": text_content,
        "generation_time_ms": int(generation_time * 1000),
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "fallback": use_fallback,
        "audio": {
            "cantonese_url": None,  # 待實現
            "mandarin_url": None    # 待實現
        },
        "images": []  # 待實現
    }

    # 6. 保存到緩存
    save_to_cache(profile_id, topic, result)

    return result


# ============ Mock 數據（開發/測試用） ============

def generate_mock_content(topic_id, profile):
    """生成 Mock 內容（用於開發測試）."""
    name = profile.get('child_name', '小明')
    interests = profile.get('interests', ['Lego'])

    mock_data = {
        "self-introduction": {
            "teaching_goal": f"教 {name} 自信地介紹自己的特點，展示個性。",
            "parent_script": f"""家長可以先問：「{name}，你最鍾意做咩呀？」

然後跟住問：
- 「你點解鍾意玩 {interests[0]} 呀？」
- 「你仲有咩嘢鍾意做？」
- 「你可以話俾老師知你係邊個小朋友？」""",
            "sample_questions": [
                f"你叫咩名？今年幾歲？",
                f"你最鍾意玩咩？點解鍾意？",
                f"你有咩特別既地方？"
            ],
            "model_answer": f"""我叫{name}，今年5歲。我最鍾意砌{interests[0]}，因為我可以砌到好多唔同嘅嘢。我想做建築師，砌好靚嘅屋同埋商場。""",
            "tips": [
                "望住對方眼睛，唔好望地下",
                "講大聲啲、清楚啲",
                "可以加入自己既特點，例如：「我記性好好」"
            ]
        },
        "interests": {
            "teaching_goal": f"教 {name} 深入表達自己的興趣愛好。",
            "parent_script": f"""家長可以問：「{name}，你平時最鍾意做咩？」

引導方向：
- 問「點解」：點解鍾意？邊部分最鍾意？
- 問「點做」：你通常點樣玩？
- 問「咩感覺」：你玩嘅时候開唔開心？""",
            "sample_questions": [
                f"你最鍾意 {interests[0]} 邊部分？",
                f"你點樣玩 {interests[0]}？",
                f"你有無話想做關於{interests[0]}嘅嘢？"
            ],
            "model_answer": f"""我最鍾意{interests[0]}，因為好好玩。我每日都會玩，砌到好多唔同嘅嘢，例如車、屋、恐龍。我最叻砌 LEGO City！""",
            "tips": [
                "講出具體例子",
                "話俾人知你對呢樣嘢有幾鍾意",
                "可以講吓學到咩嘢"
            ]
        },
        "family": {
            "teaching_goal": "教小朋友自然地介紹家庭成員。",
            "parent_script": """家長可以問：「屋企有邊幾個人？」

提示：
- 教小朋友講吓屋企人既特點
- 話俾老師知屋企人點氹小朋友
- 可以講吓屋企人鍾意做咩""",
            "sample_questions": [
                "你屋企有邊幾個人？",
                "你最鍾意同邊個屋企人玩？",
                "屋企人鍾意做咩？"
            ],
            "model_answer": """我屋企有爸爸、媽咪、同我。我最鍾意同爸爸踢波，因為爸爸好勁。媽咪每日都會氹我瞓覺。""",
            "tips": [
                "望住對方講",
                "講吓屋企人對你好",
                "唔好淨係答「爸爸媽咪」"
            ]
        }
    }

    return mock_data.get(topic_id, mock_data["self-introduction"])


def get_topic_title(topic_id):
    """獲取主題標題."""
    titles = {
        'self-introduction': '自我介紹',
        'interests': '興趣愛好',
        'family': '家庭介紹',
        'observation': '觀察力訓練',
        'scenarios': '處境題'
    }
    return titles.get(topic_id, topic_id)


# ============ 工具函數 ============

def clear_cache(profile_id=None):
    """清除緩存."""
    global content_cache
    if profile_id:
        # 清除特定用戶的緩存
        keys_to_delete = [k for k in content_cache if k.startswith(f"content:{profile_id}:")]
        for k in keys_to_delete:
            del content_cache[k]
    else:
        # 清除所有緩存
        content_cache = {}
    print(f"🗑️ Cache cleared for: {profile_id or 'all'}")


# ============ TTS 集成 ============

def generate_teaching_content_with_audio(profile, topic_id):
    """
    生成完整教學內容（文字 + 語音 URL）

    Args:
        profile: 用戶畫像 dict
        topic_id: 主題 ID

    Returns:
        dict: 教學內容（包含 audio URLs）
    """
    # 1. 生成文字內容
    result = generate_teaching_content(profile, topic_id)

    if 'error' in result:
        return result

    # 2. 生成語音（異步，不阻塞返回）
    try:
        from services.tts_service import generate_audio_urls

        text_content = result.get('content', {})
        audio_urls = generate_audio_urls(text_content, language='cantonese')

        # 更新結果中的音頻 URL
        if 'audio' not in result:
            result['audio'] = {}

        result['audio'].update(audio_urls)

        # 標記音頻狀態
        result['audio_status'] = {
            'cantonese': 'ready' if audio_urls.get('cantonese_url') else 'pending',
            'mandarin': 'pending'  # 待實現
        }

    except ImportError:
        print("⚠️ TTS service not available")
        result['audio_status'] = {
            'cantonese': 'unavailable',
            'mandarin': 'unavailable'
        }
    
    # 3. 生成图片
    try:
        from services.image_service import select_images_for_topic
        
        interests = profile.get('interests', [])
        images = select_images_for_topic(topic_id, interests, count=3)
        
        result['images'] = images.get('images', [])
        result['image_status'] = 'ready'
        
    except ImportError:
        print("⚠️ Image service not available")
        result['images'] = []
        result['image_status'] = 'unavailable'

    return result
