"""
Mock Interview Service - AI 模拟面试服务
香港升小面试 AI 导师 - 模拟面试功能

功能：
- 生成个性化面试问题
- 根据目标学校类型调整问题难度
- 生成语音提问
- 评估回答并提供反馈
"""

import os
import json
import time
import random
import requests


# ============ 配置 ============

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")


# ============ 学校类型配置 ============

SCHOOL_TYPES = {
    "academic": {
        "id": "academic",
        "name": "学术型",
        "name_en": "Academic",
        "examples": "DBS / SPCC / 女校",
        "description": "注重学术表现，提问较深入",
        "question_style": "学术导向",
        "difficulty": "medium",
        "focus_areas": ["逻辑思维", "语言表达", "基础知识"],
    },
    "holistic": {
        "id": "holistic",
        "name": "全人型",
        "name_en": "Holistic",
        "examples": "英华 / TSL / 协和",
        "description": "注重全面发展，提问较全面",
        "question_style": "综合导向",
        "difficulty": "easy",
        "focus_areas": ["兴趣爱好", "品格教育", "社交能力"],
    },
    "international": {
        "id": "international",
        "name": "国际型",
        "name_en": "International",
        "examples": "CKY / 港同 / HKIS",
        "description": "注重国际视野，英文要求高",
        "question_style": "国际导向",
        "difficulty": "hard",
        "focus_areas": ["英文表达", "创意思维", "独立性"],
    },
    "traditional": {
        "id": "traditional",
        "name": "传统名校",
        "name_en": "Traditional",
        "examples": "KTS / SFA / 圣保禄",
        "description": "注重传统价值，提问较正式",
        "question_style": "传统导向",
        "difficulty": "medium",
        "focus_areas": ["礼仪礼貌", "家庭价值观", "学习态度"],
    },
}


# ============ 问题模板 ============

QUESTION_TEMPLATES = {
    "self_introduction": [
        "小朋友，你叫咩名呀？",
        "你今年几岁呀？",
        "你读紧边间幼儿园呀？",
        "你钟意幼儿园咩嘢呀？",
        "你大个想读咩小学呀？",
    ],
    "family": [
        "你屋企有边几个人呀？",
        "你最钟意同边个屋企人玩呀？",
        "爸爸妈妈做咩工既？",
        "你同爸爸妈妈通常会一齐做咩呀？",
        "爷爷婆婆有几多岁呀？",
    ],
    "interests": [
        "你平时钟意做咩嘢呀？",
        "你钟意玩咩游戏呀？",
        "你学紧啲咩课外活动呀？",
        "你钟意睇咩卡通片呀？",
        "如果可以学一样新嘢，你最想学咩？",
    ],
    "school": [
        "你钟意幼儿园既咩嘢呀？",
        "你读K几呀？",
        "你中意同边个同学玩呀？",
        "老师教过你咩嘢呀？",
        "你钟意读书吗？点解呀？",
    ],
    "daily_life": [
        "你今日食咗咩早餐呀？",
        "你琴晚瞓得好吗？",
        "你钟意食咩嘢呀？",
        "你通常几点起身呀？",
        "你钟意边个季节呀？点解呀？",
    ],
    "future": [
        "你大个想做什么呀？",
        "如果可以许一个愿，你會许咩愿？",
        "你知唔知面试系咩呀？",
        "你对小学生活有什么期望呀？",
        "你觉得面试当日应该点样准备呀？",
    ],
    "problem_solving": [
        "如果你同同学唔啱，你会点做呀？",
        "如果你唔开心，你会点做呀？",
        "如果有一日你迟咗，你会点做呀？",
        "如果你唔识做功课，你会点样？",
        "如果有大人呃你，你會點做？",
    ],
    "values": [
        "你觉得分享系咩呀？",
        "你钟意帮助人吗？点解呀？",
        "你有无做错事呀？点样改过？",
        "你觉得好孩子应该点样？",
        "你最感激边个人呀？点解？",
    ],
}


# ============ 英文问题模板 ============

ENGLISH_QUESTION_TEMPLATES = {
    "self_introduction": [
        "Hello! What is your name?",
        "How old are you?",
        "Which kindergarten do you go to?",
        "What do you like most about your kindergarten?",
        "Which primary school would you like to go to when you grow up?",
    ],
    "family": [
        "How many people are there in your family?",
        "Who is your favorite family member? Why?",
        "What do your parents do for work?",
        "What do you like to do with your parents?",
        "How old are your grandparents?",
    ],
    "interests": [
        "What do you like to do in your free time?",
        "What games do you like to play?",
        "What extracurricular activities do you take?",
        "What cartoons do you like to watch?",
        "If you could learn something new, what would it be?",
    ],
    "school": [
        "What do you like most about your school?",
        "Which grade are you in? (K1, K2, K3)",
        "Who is your best friend at school?",
        "What has your teacher taught you?",
        "Do you like studying? Why or why not?",
    ],
    "daily_life": [
        "What did you have for breakfast today?",
        "Did you sleep well last night?",
        "What is your favorite food?",
        "What time do you usually wake up?",
        "Which season do you like best? Why?",
    ],
    "future": [
        "What do you want to be when you grow up?",
        "If you could make one wish, what would it be?",
        "Do you know what an interview is?",
        "What are you looking forward to in primary school?",
        "How do you think you should prepare for your interview?",
    ],
    "problem_solving": [
        "If you have a problem with a classmate, what would you do?",
        "If you feel sad, what do you do?",
        "If you are late for something, what would you do?",
        "If you do not understand your homework, what would you do?",
        "If an adult tells you something not true, what would you do?",
    ],
    "values": [
        "What does sharing mean to you?",
        "Do you like helping others? Why?",
        "Have you ever done something wrong? How did you fix it?",
        "What do you think a good child should do?",
        "Who are you most grateful for? Why?",
    ],
}


# ============ 面试官风格配置 ============

INTERVIEWER_STYLES = {
    "friendly": {
        "id": "friendly",
        "name": "亲和型",
        "name_en": "Friendly",
        "description": "温和友善，鼓励式提问",
        "avatar_color": "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
        "avatar_icon": "sentiment_satisfied",
        "prompt": """你是一个温和友善的小学面试官，特别擅长鼓励小朋友。
你提问时语气亲切，用词简单易懂。
如果小朋友回答得好，要及时表扬和鼓励。
永远保持耐心和微笑，让小朋友感到放松。
用粤语提问，保持语气轻松愉快。
如果小朋友回答得好，说「劲劲劲！你叻晒！」或「好好呀！」来表扬。""",
        "pressure_level": 1,
        "follow_up_rate": 0.6,
    },
    "strict": {
        "id": "strict",
        "name": "严格型",
        "name_en": "Strict",
        "description": "严谨提问，标准较高",
        "avatar_color": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
        "avatar_icon": "sentiment_strict",
        "prompt": """你是一个严谨的小学面试官，对小朋友的回答有较高要求。
你会追问细节，确保小朋友真正理解问题。
如果回答不够完整，你会温和地指出需要改进的地方。
但不要过于严厉，保持专业和友善。
用粤语提问，语气稳重。
如果小朋友回答得好，可以说「几好呀，继续努力」或「有进步」来肯定。""",
        "pressure_level": 3,
        "follow_up_rate": 0.8,
    },
    "lively": {
        "id": "lively",
        "name": "活泼型",
        "name_en": "Lively",
        "description": "轻松有趣，互动性强",
        "avatar_color": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "avatar_icon": "sentiment_very_satisfied",
        "prompt": """你是一个活泼有趣的小学面试官，喜欢用生动的方式提问。
你会用表情和语气让面试过程轻松愉快。
如果小朋友回答得好，要热情地表扬！
你可能会用一些有趣的说法来引发小朋友的兴趣。
用粤语提问，语气生动有趣。
如果小朋友回答得好，可以说「哇！你好叻呀！」或「正呀！」来热烈表扬。""",
        "pressure_level": 2,
        "follow_up_rate": 0.7,
    },
}


# ============ 怯场模式配置 ============

STAGE_FRIGHT_LEVELS = {
    1: {
        "level": 1,
        "name": "初阶",
        "description": "轻松对话，环境熟悉",
        "pressure_description": "面试官很温和，不用紧张",
        "interrupt_rate": 0.05,
        "follow_up_rate": 0.4,
    },
    2: {
        "level": 2,
        "name": "中阶",
        "description": "加入时间压力",
        "pressure_description": "面试官会提醒时间",
        "interrupt_rate": 0.1,
        "follow_up_rate": 0.5,
    },
    3: {
        "level": 3,
        "name": "高阶",
        "description": "增加追问和环境干扰",
        "pressure_description": "面试官会追问更多细节",
        "interrupt_rate": 0.15,
        "follow_up_rate": 0.7,
    },
    4: {
        "level": 4,
        "name": "挑战",
        "description": "模拟真实面试压力",
        "pressure_description": "像真实面试一样有压力",
        "interrupt_rate": 0.2,
        "follow_up_rate": 0.8,
    },
    5: {
        "level": 5,
        "name": "脱敏",
        "description": "最大压力训练",
        "pressure_description": "完全模拟真实面试压力",
        "interrupt_rate": 0.25,
        "follow_up_rate": 0.9,
    },
}


# ============ MiniMax API 调用 ============


def call_minimax_api(endpoint, payload):
    """调用 MiniMax API."""
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API Key not configured")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        url = f"{MINIMAX_BASE_URL}/{endpoint}"
        print(f"📡 Calling MiniMax API: {url}")

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"✅ MiniMax API success")
            return response.json()
        else:
            print(f"❌ MiniMax API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ MiniMax API exception: {e}")
        return None


def generate_interview_questions(profile, school_type, num_questions=5):
    """
    生成个性化面试问题。

    Args:
        profile: 用户画像 dict
        school_type: 学校类型 ID
        num_questions: 问题数量

    Returns:
        list: 问题列表
    """
    # 获取学校类型配置
    school_config = SCHOOL_TYPES.get(school_type, SCHOOL_TYPES["holistic"])

    # 合并所有问题模板
    all_categories = list(QUESTION_TEMPLATES.keys())

    # 根据学校类型选择问题类别权重
    if school_type == "academic":
        # 学术型：更多逻辑和学校相关问题
        weights = [0.15, 0.1, 0.15, 0.25, 0.1, 0.1, 0.1, 0.05]
    elif school_type == "international":
        # 国际型：更多未来和价值观问题
        weights = [0.15, 0.1, 0.15, 0.15, 0.1, 0.15, 0.1, 0.1]
    elif school_type == "traditional":
        # 传统型：更多家庭和价值观问题
        weights = [0.15, 0.2, 0.1, 0.15, 0.1, 0.1, 0.1, 0.1]
    else:
        # 全人型：均衡
        weights = [0.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05]

    # 选择问题类别
    selected_categories = random.choices(
        all_categories, weights=weights, k=num_questions
    )

    # 生成问题列表
    questions = []
    seen_categories = set()

    for i, category in enumerate(selected_categories):
        # 如果类别已用过，换一个
        if category in seen_categories:
            available = [c for c in all_categories if c not in seen_categories]
            if available:
                category = random.choice(available)
            seen_categories.add(category)
        else:
            seen_categories.add(category)

        # 从模板中随机选择一个问题
        template_questions = QUESTION_TEMPLATES.get(category, [])
        english_template_questions = ENGLISH_QUESTION_TEMPLATES.get(category, [])

        if template_questions:
            question = random.choice(template_questions)
            # 获取对应索引的英文问题（如果英文模板足够长）
            eng_idx = (
                template_questions.index(question)
                if question in template_questions
                else random.randint(0, len(english_template_questions) - 1)
            )
            english_question = (
                english_template_questions[eng_idx]
                if eng_idx < len(english_template_questions)
                else english_template_questions[0]
                if english_template_questions
                else "Tell me more about that."
            )

            questions.append(
                {
                    "id": i + 1,
                    "category": category,
                    "question": question,
                    "question_en": english_question,
                    "category_zh": get_category_name(category),
                    "category_en": get_category_name_en(category),
                }
            )

    return questions


def get_category_name_en(category_id):
    """获取类别英文名称."""
    names = {
        "self_introduction": "Self Introduction",
        "family": "Family",
        "interests": "Interests & Hobbies",
        "school": "School Life",
        "daily_life": "Daily Life",
        "future": "Future Plans",
        "problem_solving": "Problem Solving",
        "values": "Values & Morals",
    }
    return names.get(category_id, category_id)


def get_category_name(category_id):
    """获取类别中文名称."""
    names = {
        "self_introduction": "自我介绍",
        "family": "家庭介绍",
        "interests": "兴趣爱好",
        "school": "学校生活",
        "daily_life": "日常生活",
        "future": "未来展望",
        "problem_solving": "情境处理",
        "values": "价值观",
    }
    return names.get(category_id, category_id)


def generate_ai_follow_up(base_question, previous_answer, profile):
    """
    使用 AI 生成追问问题。

    Args:
        base_question: 基础问题
        previous_answer: 之前的回答
        profile: 用户画像

    Returns:
        str: 追问问题
    """
    child_name = profile.get("child_name", "小朋友")
    age = profile.get("child_age", "5岁")

    system_prompt = """你是一个资深的小学面试官，善于通过追问来深入了解小朋友。
你需要根据小朋友的回答，提出一个简短的追问问题（5-15字）。
问题要适合{}岁左右的小朋友理解。
用粤语提问，保持语气温和友善。""".format(age)

    user_prompt = """面试官问：「{}」
小朋友回答：「{}」

请提出一个追问问题，了解更多细节。""".format(base_question, previous_answer)

    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 100,
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and "choices" in result:
        follow_up = result["choices"][0]["message"]["content"]
        # 清理回答
        follow_up = follow_up.strip()
        if follow_up.startswith("「") and follow_up.endswith("」"):
            follow_up = follow_up[1:-1]
        if follow_up.startswith('"') and follow_up.endswith('"'):
            follow_up = follow_up[1:-1]
        return follow_up

    # 如果 API 失败，使用默认追问
    default_follow_ups = [
        "可以话多啲俾老师知吗？",
        "点解咁讲呀？",
        "然后呢？",
        "你最钟意边个部分呀？",
    ]
    return random.choice(default_follow_ups)


def evaluate_answer(question, answer, profile, school_type):
    """
    评估小朋友的回答。

    Args:
        question: 问题
        answer: 回答
        profile: 用户画像
        school_type: 学校类型

    Returns:
        dict: 评估结果
    """
    child_name = profile.get("child_name", "小朋友")
    school_config = SCHOOL_TYPES.get(school_type, SCHOOL_TYPES["holistic"])

    # 简单评估逻辑（可以后续接入 AI）
    score = 0
    feedback = []
    strengths = []
    improvements = []

    # 评估回答长度
    answer_length = len(answer)
    if answer_length < 5:
        score += 1
        feedback.append("回答较简短，可以讲多啲嘢")
        improvements.append("尝试讲多啲关于你既嘢")
    elif answer_length >= 10:
        score += 3
        strengths.append("表达完整")

    # 检查是否有具体内容
    if any(word in answer for word in ["因为", "所以", "最", "钟意", "好"]):
        score += 2
        strengths.append("有具体表达")

    # 检查礼貌用语
    if any(word in answer for word in ["谢谢", "老师", "请", "早晨"]):
        score += 1
        strengths.append("有礼貌")

    # 转换为百分制分数
    final_score = min(100, score * 20)

    # 生成反馈
    if final_score >= 80:
        feedback_text = "表现好好！继续努力！"
    elif final_score >= 60:
        feedback_text = "几好呀，可以讲多啲细节！"
    else:
        feedback_text = "既嘢讲得不错，继续练习！"

    return {
        "score": final_score,
        "feedback": feedback_text,
        "strengths": strengths,
        "improvements": improvements,
        "suggestions": generate_suggestions(question, answer, school_config),
    }


def generate_suggestions(question, answer, school_config):
    """生成改进建议."""
    suggestions = []

    if school_config["id"] == "academic":
        suggestions.append("可以讲多啲关于学习既嘢")
    elif school_config["id"] == "international":
        suggestions.append("试下用英文表达下")
    elif school_config["id"] == "traditional":
        suggestions.append("记得保持礼貌呀")

    suggestions.append("望住老师眼睛讲话")
    suggestions.append("讲大声啲、清楚啲")

    return suggestions[:2]


def generate_mock_interview_questions(profile, school_type, num_questions=5):
    """生成模拟面试问题（支持中英文）。"""
    # 获取学校类型配置
    school_config = SCHOOL_TYPES.get(school_type, SCHOOL_TYPES["holistic"])

    # 合并所有问题模板
    all_categories = list(QUESTION_TEMPLATES.keys())

    # 根据学校类型选择问题类别
    if school_type == "academic":
        weights = [0.15, 0.1, 0.15, 0.25, 0.1, 0.1, 0.1, 0.05]
    elif school_type == "international":
        weights = [0.15, 0.1, 0.15, 0.15, 0.1, 0.15, 0.1, 0.1]
    elif school_type == "traditional":
        weights = [0.15, 0.2, 0.1, 0.15, 0.1, 0.1, 0.1, 0.1]
    else:
        weights = [0.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05]

    # 选择问题类别
    selected_categories = random.choices(
        all_categories, weights=weights, k=num_questions
    )

    # 生成问题列表（包含中英文）
    questions = []
    used_questions = set()

    for i, category in enumerate(selected_categories):
        template_questions = QUESTION_TEMPLATES.get(category, [])
        english_template_questions = ENGLISH_QUESTION_TEMPLATES.get(category, [])

        # 随机选择未使用的问题
        available = [q for q in template_questions if q not in used_questions]
        if available:
            question = random.choice(available)
            used_questions.add(question)
        else:
            question = random.choice(template_questions)

        # 获取对应索引的英文问题
        try:
            eng_idx = template_questions.index(question)
            english_question = (
                english_template_questions[eng_idx]
                if eng_idx < len(english_template_questions)
                else random.choice(english_template_questions)
                if english_template_questions
                else "Tell me more about that."
            )
        except (ValueError, IndexError):
            english_question = (
                random.choice(english_template_questions)
                if english_template_questions
                else "Tell me more about that."
            )

        questions.append(
            {
                "id": i + 1,
                "category": category,
                "question": question,
                "question_en": english_question,
                "category_zh": get_category_name(category),
                "category_en": get_category_name_en(category),
            }
        )

    return questions


# ============ TTS 集成 ============


def generate_question_audio(question_text, language="cantonese"):
    """
    生成问题语音（使用真实 MiniMax TTS API）。

    Args:
        question_text: 问题文字
        language: 语言类型 ('cantonese', 'mandarin', 'english')

    Returns:
        str: 音频 URL 或 None
    """
    try:
        from services.tts_service import (
            generate_cantonese_audio,
            generate_mandarin_audio,
            generate_english_audio,
            upload_to_r2,
        )
        import uuid

        # 根据语言选择生成函数
        if language == "english":
            audio_data = generate_english_audio(question_text, speed=1.0)
        elif language == "mandarin":
            audio_data = generate_mandarin_audio(question_text, speed=1.0)
        else:
            audio_data = generate_cantonese_audio(question_text, speed=1.0)

        if audio_data:
            url = upload_to_r2(audio_data)
            if url:
                print(f"✅ Generated {language} audio: {url[:50]}...")
                return url
            else:
                print(f"❌ Failed to upload {language} audio")
                return None
        else:
            print(f"❌ Failed to generate {language} audio - using base64 fallback")
            # 返回 None，让前端处理
            return None

    except Exception as e:
        print(f"❌ Error generating question audio: {e}")
        return None


def generate_bilingual_audio(question_text, question_en):
    """
    生成中英文双语问题语音。

    Args:
        question_text: 粤语问题文字
        question_en: 英文问题文字

    Returns:
        dict: {'cantonese_url': str, 'english_url': str}
    """
    result = {"cantonese_url": None, "english_url": None}

    # 生成粤语语音
    result["cantonese_url"] = generate_question_audio(question_text, "cantonese")

    # 生成英文语音
    # 生成英文语音
    result["english_url"] = generate_question_audio(question_en, "english")

    return result


# ============ 面试记录存储 ============

# 内存存储（生产环境应使用数据库）
interview_sessions = {}


def save_interview_session(user_id, session_data):
    """保存面试会话。"""
    if user_id not in interview_sessions:
        interview_sessions[user_id] = []

    session_id = f"interview_{int(time.time())}"
    session_data["session_id"] = session_id
    session_data["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    interview_sessions[user_id].insert(0, session_data)
    # 保留最近 50 次面试记录
    interview_sessions[user_id] = interview_sessions[user_id][:50]

    return session_id


def get_interview_sessions(user_id, limit=10):
    """获取用户的面试记录。"""
    sessions = interview_sessions.get(user_id, [])
    return sessions[:limit]


def get_interview_session(user_id, session_id):
    """获取特定面试会话。"""
    sessions = interview_sessions.get(user_id, [])
    for session in sessions:
        if session.get("session_id") == session_id:
            return session
    return None


# ============ 工具函数 ============


def get_school_types():
    """获取所有学校类型。"""
    return list(SCHOOL_TYPES.values())


def get_school_type_config(school_type_id):
    """获取学校类型配置。"""
    return SCHOOL_TYPES.get(school_type_id)


# ============ 面试官风格函数 ============


def get_interviewer_styles():
    """获取所有面试官风格。"""
    return list(INTERVIEWER_STYLES.values())


def get_interviewer_style(style_id):
    """获取特定面试官风格。"""
    return INTERVIEWER_STYLES.get(style_id)


def get_interviewer_prompt(style_id):
    """获取面试官的prompt。"""
    style = INTERVIEWER_STYLES.get(style_id, INTERVIEWER_STYLES["friendly"])
    return style["prompt"]


def get_stage_fright_levels():
    """获取所有怯场级别。"""
    return list(STAGE_FRIGHT_LEVELS.values())


def get_stage_fright_level(level):
    """获取特定怯场级别。"""
    return STAGE_FRIGHT_LEVELS.get(level)


# ============ AI 评估报告生成 ============


def generate_ai_evaluation_report(session_data):
    """
    使用 AI 生成详细的面试评估报告。

    Args:
        session_data: 面试会话数据

    Returns:
        dict: 详细评估报告
    """
    if not MINIMAX_API_KEY:
        return generate_basic_evaluation_report(session_data)

    try:
        child_name = session_data.get("profile", {}).get("child_name", "小朋友")
        questions = session_data.get("questions", [])
        answers = session_data.get("answers", [])
        interviewer_style = session_data.get("interviewer_style", "friendly")
        stage_fright_level = session_data.get("stage_fright_level", 1)
        school_type = session_data.get("school_type", "holistic")

        style_config = INTERVIEWER_STYLES.get(
            interviewer_style, INTERVIEWER_STYLES["friendly"]
        )

        # 构建评估 prompt
        system_prompt = f"""你是一个资深的小学面试评估专家，擅长分析小朋友的面试表现。
请根据以下面试数据，生成一份详细的评估报告。

面试官风格: {style_config["name"]}
怯场模式级别: {stage_fright_level}
学校类型: {school_type}

请生成以下格式的JSON评估报告：
{{
    "overall_score": 0-100的总分,
    "overall_summary": "整体表现总结（50字以内）",
    "strengths": ["优势1", "优势2", "优势3"],
    "improvements": ["需要改进的地方1", "需要改进的地方2"],
    "category_scores": {{
        "self_introduction": 分数,
        "family": 分数,
        "interests": 分数,
        "school": 分数,
        "daily_life": 分数,
        "future": 分数,
        "problem_solving": 分数,
        "values": 分数
    }},
    "emotional_score": 情绪表现分数(0-100),
    "confidence_score": 自信程度分数(0-100),
    "expression_score": 表达能力分数(0-100),
    "logic_score": 逻辑思维分数(0-100),
    "suggestions": ["建议1", "建议2", "建议3"]
}}

请只返回JSON，不要其他内容。"""

        # 构建问答内容
        qa_content = ""
        for i, answer_data in enumerate(answers):
            question = answer_data.get("question", "")
            answer = answer_data.get("answer", "")
            qa_content += f"问题{i + 1}: {question}\n回答: {answer}\n\n"

        user_prompt = f"面试问答内容:\n{qa_content}"

        payload = {
            "model": "abab6.5-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }

        result = call_minimax_api("text/chatcompletion_v2", payload)

        if result and "choices" in result:
            content = result["choices"][0]["message"]["content"]
            # 尝试解析 JSON
            import re

            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                return json.loads(json_match.group())

    except Exception as e:
        print(f"❌ AI evaluation error: {e}")

    # 如果 AI 评估失败，使用基础评估
    return generate_basic_evaluation_report(session_data)


def generate_basic_evaluation_report(session_data):
    """生成基础评估报告（不调用 AI）。"""
    answers = session_data.get("answers", [])
    questions = session_data.get("questions", [])

    # 按类别分组问题
    category_scores = {}
    category_count = {}

    for answer_data in answers:
        answer = answer_data.get("answer", "")
        question_text = answer_data.get("question", "")

        # 简单评分逻辑
        score = 0
        if len(answer) > 10:
            score += 30
        if len(answer) > 30:
            score += 20
        if any(word in answer for word in ["因为", "所以", "最", "钟意", "好"]):
            score += 25
        if any(word in answer for word in ["谢谢", "老师", "请", "早晨"]):
            score += 15
        score = min(100, score)

        # 找到问题类别
        category = "other"
        for q in questions:
            if q.get("question") == question_text:
                category = q.get("category", "other")
                break

        if category not in category_scores:
            category_scores[category] = 0
            category_count[category] = 0

        category_scores[category] += score
        category_count[category] += 1

    # 计算各类别平均分
    for category in category_scores:
        if category_count[category] > 0:
            category_scores[category] //= category_count[category]

    # 计算总分
    total_score = (
        sum(category_scores.values()) // len(category_scores) if category_scores else 0
    )

    return {
        "overall_score": total_score,
        "overall_summary": "继续努力，会越来越好的！"
        if total_score >= 60
        else "多练习就会进步！",
        "strengths": ["表达清晰"] if total_score >= 60 else ["有尝试回答"],
        "improvements": ["可以讲多啲细节"] if total_score < 80 else ["继续保持"],
        "category_scores": category_scores,
        "emotional_score": total_score,
        "confidence_score": total_score,
        "expression_score": total_score,
        "logic_score": total_score,
        "suggestions": ["多练习面试", "保持自信", "注意礼貌"],
    }
