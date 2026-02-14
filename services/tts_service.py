"""
TTS Service - Text to Speech Generation
香港升小面試 AI 導師 - 語音生成服務

功能：
- 調用 MiniMax TTS API 生成粵語/普通話語音
- 上傳音頻到 Cloudflare R2
- 音頻緩存機制
"""

import os
import time
import uuid
import requests


# ============ 配置 ============

MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat')

# Cloudflare R2 配置
R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID', '')
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'ai-tutor-assets')
R2_PUBLIC_URL = os.getenv('R2_PUBLIC_URL', '')

# 音頻配置
AUDIO_SAMPLE_RATE = 24000
AUDIO_FORMAT = 'mp3'


# ============ R2 文件上傳 ============

def upload_to_r2(audio_data, content_type='audio/mp3'):
    """
    上傳音頻文件到 Cloudflare R2.
    
    Args:
        audio_data: 音頻字節數據
        content_type: MIME 類型
    
    Returns:
        str: 公開訪問 URL
    """
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("⚠️ R2 credentials not configured")
        return None
    
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())[:8]
        filename = f"audio/{file_id}.{AUDIO_FORMAT}"
        
        # 如果沒有配置 R2，返回 Mock URL
        if not R2_ACCOUNT_ID:
            print("⚠️ R2 not configured, returning mock URL")
            return f"https://mock-r2.example.com/{filename}"
        
        # AWS Signature V4 簽名（簡化版本）
        # 實際生產環境建議使用 boto3 庫
        
        # 嘗試使用 S3 兼容 API
        endpoint = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
        
        response = requests.put(
            f"{endpoint}/{R2_BUCKET_NAME}/{filename}",
            data=audio_data,
            headers={
                'Content-Type': content_type,
                'x-amz-acl': 'public-read'
            },
            auth=(R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY),
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            # 返回公開 URL
            if R2_PUBLIC_URL:
                return f"{R2_PUBLIC_URL}/{filename}"
            else:
                return f"{endpoint}/{R2_BUCKET_NAME}/{filename}"
        else:
            print(f"❌ R2 upload failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ R2 upload error: {e}")
        return None


# ============ MiniMax TTS API ============

def call_tts_api(text, voice='male-qn-qingse', speed=1.0):
    """
    調用 MiniMax TTS API (異步版本).

    Args:
        text: 要轉換的文字
        voice: 語音名稱 (male-qn-qingse, female-shaonv 等)
        speed: 播放速度 (0.5-2.0)

    Returns:
        bytes: 音頻數據 或 None
    """
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API key not configured")
        return None

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        # 使用異步 TTS API
        payload = {
            "model": "speech-2.6-hd",
            "text": text,
            "voice_setting": {
                "voice_id": voice,
                "speed": speed
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1
            }
        }

        # 創建異步任務
        response = requests.post(
            f"{MINIMAX_BASE_URL}/v1/t2a_async_v2",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ TTS API error: {response.status_code} - {response.text[:200]}")
            return None

        result = response.json()
        file_id = result.get('file_id')

        if not file_id:
            print(f"⚠️ TTS API 未返回 file_id: {result}")
            return None

        # 輪詢等待音頻生成完成
        max_retries = 10
        for i in range(max_retries):
            time.sleep(2)

            file_resp = requests.get(
                f"{MINIMAX_BASE_URL}/v1/files/retrieve?file_id={file_id}",
                headers=headers,
                timeout=30
            )

            if file_resp.status_code == 200:
                file_result = file_resp.json()
                file_info = file_result.get('file')

                if file_info:
                    download_url = file_info.get('download_url')
                    if download_url:
                        # 下載音頻
                        audio_resp = requests.get(download_url, timeout=60)
                        if audio_resp.status_code == 200:
                            print(f"✅ TTS 成功生成音頻，大小: {len(audio_resp.content)} bytes")
                            return audio_resp.content
                        else:
                            print(f"❌ 下載音頻失敗: {audio_resp.status_code}")
                else:
                    print(f"⚠️ 文件尚未準備好: {file_result}")

        print(f"❌ TTS 輪詢超時")
        return None

    except Exception as e:
        print(f"❌ TTS API exception: {e}")
        return None


def generate_cantonese_audio(text, speed=1.0):
    """生成粵語語音."""
    return call_tts_api(text, voice='Canto-Female-1', speed=speed)


def generate_mandarin_audio(text, speed=1.0):
    """生成普通話語音."""
    return call_tts_api(text, voice='Mandarin-Female-1', speed=speed)


def generate_english_audio(text, speed=1.0):
    """生成英語語音."""
    return call_tts_api(text, voice='English_expressive_narrator', speed=speed)


# ============ 主生成函數 ============

def generate_audio_urls(text_content, language='cantonese'):
    """
    為文字內容生成語音 URL.
    
    Args:
        text_content: dict，包含 parent_script 和 model_answer
        language: 'cantonese' 或 'mandarin'
    
    Returns:
        dict: 包含 cantonese_url 和 mandarin_url
    """
    result = {
        'cantonese_url': None,
        'mandarin_url': None
    }
    
    # 需要生成語音的文字
    texts_to_speak = []
    
    # 1. 家長話術（較長，30-60秒）
    if text_content.get('parent_script'):
        texts_to_speak.append(('parent_script', text_content['parent_script']))
    
    # 2. 示範答案（較短，15-30秒）
    if text_content.get('model_answer'):
        texts_to_speak.append(('model_answer', text_content['model_answer']))
    
    if not texts_to_speak:
        print("⚠️ No text to generate audio for")
        return result
    
    # 生成粵語
    print(f"🎙️ Generating {language} audio...")
    for label, text in texts_to_speak:
        if language == 'cantonese':
            audio_data = generate_cantonese_audio(text, speed=0.9)
        else:
            audio_data = generate_mandarin_audio(text, speed=0.9)
        
        if audio_data:
            # 上傳到 R2
            url = upload_to_r2(audio_data)
            if url:
                if label == 'parent_script':
                    result['cantonese_url'] = url if language == 'cantonese' else result.get('cantonese_url')
                elif label == 'model_answer':
                    # 可以為 model_answer 生成獨立音頻
                    pass
                print(f"✅ {label} audio uploaded: {url[:50]}...")
            else:
                print(f"❌ Failed to upload {label} audio")
        else:
            print(f"❌ Failed to generate {label} audio")
    
    return result


# ============ Mock 音頻（開發用）==========

def generate_mock_audio_url(text, language='cantonese'):
    """
    生成 Mock 音頻 URL（開發環境使用）.
    
    在實際生產環境中，這會返回 None，觸發前端顯示"即將推出".
    """
    # 計算文字長度估算音頻時長
    word_count = len(text)
    estimated_seconds = max(5, word_count // 5)  # 粗略估算
    
    return {
        'url': f"https://mock-audio.example.com/{language}/{int(time.time())}.mp3",
        'duration_seconds': estimated_seconds,
        'text_length': word_count,
        'language': language
    }


# ============ 工具函數 ============

def estimate_audio_duration(text, wpm=150):
    """
    估算語音時長.
    
    Args:
        text: 文字內容
        wpm: 每分鐘詞數（粵語約 150 wpm）
    
    Returns:
        float: 時長（秒）
    """
    words = len(text)
    minutes = words / wpm
    return minutes * 60


def get_voice_options():
    """獲取可用的語音選項."""
    return {
        'cantonese': [
            {'id': 'Canto-Female-1', 'name': '粵語女聲', 'description': '溫和女聲，適合教學'},
            {'id': 'Canto-Male-1', 'name': '粵語男聲', 'description': '清晰男聲'}
        ],
        'mandarin': [
            {'id': 'Mandarin-Female-1', 'name': '普通話女聲', 'description': '標準普通話女聲'},
            {'id': 'Mandarin-Male-1', 'name': '普通話男聲', 'description': '標準普通話男聲'}
        ]
    }
