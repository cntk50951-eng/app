"""
Voice Interview Service - AI 语音实时对话面试服务
香港升小面试 AI 导师 - 语音识别和实时对话功能

功能：
- 语音识别 (ASR) - 使用 MiniMax API 或 Web Speech API
- AI 追问生成
- TTS 语音播放
- 实时对话流程管理
"""

import os
import json
import time
import random
import uuid
import base64
import requests


# ============ 配置 ============

MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
# 标准API (用于text/chat, audio/asr) - 需要/v1后缀
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1')
# TTS专用API (不带/v1后缀)
MINIMAX_TTS_BASE_URL = os.getenv('MINIMAX_TTS_BASE_URL', 'https://api.minimax.chat')


# ============ 语音识别 (ASR) ============

def call_asr_api(audio_data, language=' Cantonese'):
    """
    调用 MiniMax ASR API 进行语音识别。

    Args:
        audio_data: 音频二进制数据
        language: 语言类型 (Cantonese/Mandarin)

    Returns:
        dict: 识别结果 {'text': '识别文本', 'success': bool}
    """
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API Key not configured")
        return {'text': '', 'success': False, 'error': 'API key not configured'}

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
        }

        # 准备 multipart 请求
        files = {
            'file': ('audio.wav', audio_data, 'audio/wav'),
            'model': (None, 'speech-01-turbo'),
            'language': (None, language),
        }

        url = f"{MINIMAX_BASE_URL}/v1/audio/asr"

        print(f"📡 Calling MiniMax ASR API...")

        response = requests.post(
            url,
            files=files,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')
            print(f"✅ ASR success: {text[:50]}...")
            return {'text': text, 'success': True}
        else:
            print(f"❌ ASR API error: {response.status_code}")
            return {'text': '', 'success': False, 'error': f'API error: {response.status_code}'}

    except Exception as e:
        print(f"❌ ASR API exception: {e}")
        return {'text': '', 'success': False, 'error': str(e)}


def recognize_speech(audio_data, use_web_speech=False):
    """
    语音识别主函数。

    优先使用 MiniMax ASR API，如果失败则返回空文本让用户手动输入。

    Args:
        audio_data: 音频二进制数据
        use_web_speech: 是否使用 Web Speech API (前端处理)

    Returns:
        dict: 识别结果
    """
    if use_web_speech:
        # 前端使用 Web Speech API，不需要服务端处理
        return {'text': '', 'success': True, 'use_web_speech': True}

    # 尝试使用 MiniMax ASR
    result = call_asr_api(audio_data, language='Cantonese')

    if result['success'] and result['text']:
        return result

    # 如果 ASR 失败，返回提示让用户手动输入
    return {
        'text': '',
        'success': False,
        'error': result.get('error', 'ASR failed'),
        'fallback': True
    }


# ============ AI 追问生成 ============

def call_minimax_chat(system_prompt, user_prompt):
    """调用 MiniMax 聊天 API。"""
    if not MINIMAX_API_KEY:
        return None

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": "abab6.5-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

        url = f"{MINIMAX_BASE_URL}/v1/text/chatcompletion_v2"

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Chat API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Chat API exception: {e}")
        return None


def generate_voice_follow_up(base_question, previous_answer, profile, question_history=None):
    """
    生成语音面试的追问问题。

    Args:
        base_question: 基础问题
        previous_answer: 之前的回答
        profile: 用户画像 dict
        question_history: 历史问题列表 (可选)

    Returns:
        dict: {'follow_up': '追问问题', 'needs_follow_up': bool}
    """
    child_name = profile.get('child_name', '小朋友')
    child_age = profile.get('child_age', '5岁')

    # 判断是否需要追问
    answer_length = len(previous_answer) if previous_answer else 0

    # 简短回答需要追问
    if answer_length < 10:
        system_prompt = f"""你是一个资深的小学面试官，善于通过追问来深入了解小朋友。
你需要根据小朋友的回答，提出一个简短的追问问题（5-15字）。
问题要适合{child_age}岁左右的小朋友理解。
用粤语提问，保持语气温和友善。
如果小朋友回答得太简短，一定要追问。
回答要简短，最多15个字。"""

        user_prompt = f"""面试官问：「{base_question}」
小朋友回答：「{previous_answer}」

请提出一个追问问题。"""

        result = call_minimax_chat(system_prompt, user_prompt)

        if result and 'choices' in result:
            follow_up = result['choices'][0]['message']['content']
            # 清理回答
            follow_up = follow_up.strip()
            # 移除可能的引号
            if follow_up.startswith('「') and follow_up.endswith('」'):
                follow_up = follow_up[1:-1]
            if follow_up.startswith('"') and follow_up.endswith('"'):
                follow_up = follow_up[1:-1]

            return {
                'follow_up': follow_up,
                'needs_follow_up': True
            }

        # API 失败时使用默认追问
        default_follow_ups = [
            '可以话多啲俾老师知吗？',
            '点解咁讲呀？',
            '然后呢？',
            '你最钟意边个部分呀？',
        ]
        return {
            'follow_up': random.choice(default_follow_ups),
            'needs_follow_up': True
        }

    # 回答较长，不需要追问
    return {
        'follow_up': '',
        'needs_follow_up': False
    }


# ============ TTS 语音生成 ============

def generate_voice_audio(text, voice='male-qn-qingse', speed=1.0):
    """
    生成语音面试的 TTS 音频（使用 MiniMax 异步 TTS API）。

    Args:
        text: 要转换的文字
        voice: 语音名称 (male-qn-qingse, female-shaonv 等)
        speed: 播放速度 (0.5-2.0)

    Returns:
        dict: {'audio_url': '音频URL', 'audio_data': base64编码的音频数据}
    """
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API Key not configured")
        return {'audio_url': None, 'audio_data': None}

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        # 使用异步 TTS API
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

        url = f"{MINIMAX_TTS_BASE_URL}/v1/t2a_async_v2"

        print(f"📡 Creating MiniMax TTS async task with voice: {voice}...")

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ TTS API error: {response.status_code} - {response.text[:200]}")
            return {'audio_url': None, 'audio_data': None}

        result = response.json()
        file_id = result.get('file_id')

        if not file_id:
            print(f"⚠️ TTS API 未返回 file_id: {result}")
            return {'audio_url': None, 'audio_data': None}

        # 轮询等待音频生成完成
        max_retries = 10
        for i in range(max_retries):
            time.sleep(2)

            file_resp = requests.get(
                f"{MINIMAX_TTS_BASE_URL}/v1/files/retrieve?file_id={file_id}",
                headers=headers,
                timeout=30
            )

            if file_resp.status_code == 200:
                file_result = file_resp.json()
                download_url = file_result.get('file', {}).get('download_url')

                if download_url:
                    # 下载音频
                    audio_resp = requests.get(download_url, timeout=60)
                    if audio_resp.status_code == 200:
                        audio_data = audio_resp.content
                        print(f"✅ TTS 成功生成音频，大小: {len(audio_data)} bytes")

                        # 上传到 R2
                        audio_url = upload_audio_to_storage(audio_data)

                        return {
                            'audio_url': audio_url,
                            'audio_data': base64.b64encode(audio_data).decode('utf-8') if audio_url is None else None
                        }

        print(f"❌ TTS 轮询超时")
        return {'audio_url': None, 'audio_data': None}

    except Exception as e:
        print(f"❌ TTS API exception: {e}")
        return {'audio_url': None, 'audio_data': None}


def upload_audio_to_storage(audio_data):
    """上传音频到存储并返回 URL。"""
    try:
        from services.tts_service import upload_to_r2
        return upload_to_r2(audio_data, 'audio/mp3')
    except Exception as e:
        print(f"❌ Audio upload error: {e}")
        return None


# ============ 面试会话管理 ============

# 内存存储 (生产环境应使用数据库)
voice_interview_sessions = {}


def create_voice_session(user_id, school_type, profile, num_questions=5):
    """
    创建语音面试会话。

    Args:
        user_id: 用户 ID
        school_type: 学校类型
        profile: 用户画像
        num_questions: 问题数量

    Returns:
        dict: 会话数据
    """
    from services.mock_interview_service import (
        generate_mock_interview_questions,
        SCHOOL_TYPES
    )

    # 生成问题
    questions = generate_mock_interview_questions(profile, school_type, num_questions)

    # 创建会话
    session_id = f"voice_{uuid.uuid4().hex[:12]}"

    session_data = {
        'session_id': session_id,
        'user_id': user_id,
        'school_type': school_type,
        'school_type_name': SCHOOL_TYPES.get(school_type, {}).get('name', '语音面试'),
        'profile': profile,
        'questions': questions,
        'current_question_index': 0,
        'answers': [],
        'follow_ups': [],
        'status': 'started',  # started, in_progress, completed
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'started_at': time.time()
    }

    # 存储会话
    if user_id not in voice_interview_sessions:
        voice_interview_sessions[user_id] = {}

    voice_interview_sessions[user_id][session_id] = session_data

    return session_data


def get_voice_session(user_id, session_id):
    """获取语音面试会话。"""
    if user_id in voice_interview_sessions:
        return voice_interview_sessions[user_id].get(session_id)
    return None


def update_voice_session(user_id, session_id, updates):
    """更新语音面试会话。"""
    if user_id in voice_interview_sessions:
        session = voice_interview_sessions[user_id].get(session_id)
        if session:
            session.update(updates)
            return session
    return None


def save_voice_answer(user_id, session_id, answer_data):
    """保存用户回答。"""
    session = get_voice_session(user_id, session_id)
    if session:
        answers = session.get('answers', [])
        answers.append(answer_data)
        session['answers'] = answers
        return True
    return False


def complete_voice_session(user_id, session_id):
    """完成语音面试会话。"""
    session = get_voice_session(user_id, session_id)
    if session:
        session['status'] = 'completed'
        session['completed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        session['duration'] = time.time() - session.get('started_at', time.time())
        return session
    return None


def get_voice_interview_history(user_id, limit=10):
    """获取语音面试历史记录。"""
    if user_id not in voice_interview_sessions:
        return []

    sessions = voice_interview_sessions[user_id].values()
    # 按时间倒序
    sorted_sessions = sorted(
        [s for s in sessions if s.get('status') == 'completed'],
        key=lambda x: x.get('completed_at', ''),
        reverse=True
    )

    history = []
    for session in sorted_sessions[:limit]:
        history.append({
            'session_id': session.get('session_id'),
            'school_type_name': session.get('school_type_name', '语音面试'),
            'score': session.get('score', 0),
            'num_questions': len(session.get('questions', [])),
            'num_answers': len(session.get('answers', [])),
            'created_at': session.get('created_at', ''),
            'completed_at': session.get('completed_at', '')
        })

    return history


# ============ 评估函数 ============

def evaluate_voice_answer(question, answer, profile, school_type):
    """
    评估语音面试回答。

    Args:
        question: 问题
        answer: 回答
        profile: 用户画像
        school_type: 学校类型

    Returns:
        dict: 评估结果
    """
    from services.mock_interview_service import evaluate_answer
    return evaluate_answer(question, answer, profile, school_type)


def generate_voice_report(user_id, session_id):
    """生成语音面试报告。"""
    session = get_voice_session(user_id, session_id)
    if not session:
        return None

    # 评估每个回答
    evaluations = []
    total_score = 0

    for answer_data in session.get('answers', []):
        question = answer_data.get('question', '')
        answer = answer_data.get('answer', '')

        if question and answer:
            evaluation = evaluate_voice_answer(
                question,
                answer,
                session.get('profile', {}),
                session.get('school_type', 'holistic')
            )
            evaluations.append({
                'question': question,
                'answer': answer,
                'follow_up': answer_data.get('follow_up', ''),
                'follow_up_answer': answer_data.get('follow_up_answer', ''),
                'evaluation': evaluation
            })
            total_score += evaluation.get('score', 0)

    # 计算平均分
    avg_score = total_score // len(evaluations) if evaluations else 0

    # 更新会话
    session['score'] = avg_score
    session['evaluations'] = evaluations

    return {
        'session_id': session_id,
        'school_type': session.get('school_type'),
        'school_type_name': session.get('school_type_name'),
        'score': avg_score,
        'total_questions': len(session.get('questions', [])),
        'total_answers': len(session.get('answers', [])),
        'evaluations': evaluations,
        'duration': session.get('duration', 0),
        'created_at': session.get('created_at'),
        'completed_at': session.get('completed_at')
    }
