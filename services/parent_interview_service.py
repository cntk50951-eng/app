"""
Parent Interview Service - AI 家长面试服务
家长面试 AI 教练 - 服务模块

功能：
- 加载家长面试题库
- 生成个性化面试问题
- 根据目标学校类型调整问题
- 评估回答并提供反馈
- 记录面试历史
"""

import os
import json
import time
import random
import uuid
from datetime import datetime
import requests


# ============ 配置 ============

MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1')

# 加载题库数据
def load_question_bank():
    """加载家长面试题库"""
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'parent_questions.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading question bank: {e}")
        return None


# ============ MiniMax API 调用 ============

def call_minimax_api(endpoint, payload):
    """调用 MiniMax API."""
    if not MINIMAX_API_KEY:
        print("WARNING: MiniMax API Key not configured")
        return None

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        url = f"{MINIMAX_BASE_URL}/{endpoint}"
        print(f"Calling MiniMax API: {url}")

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            print(f"MiniMax API success")
            return response.json()
        else:
            print(f"MiniMax API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"MiniMax API exception: {e}")
        return None


# ============ 题库功能 ============

def get_question_categories():
    """获取所有问题分类"""
    data = load_question_bank()
    if not data:
        return []

    categories = []
    for cat_id, cat_info in data.get('categories', {}).items():
        categories.append({
            'id': cat_id,
            'name': cat_info.get('name'),
            'name_en': cat_info.get('name_en'),
            'icon': cat_info.get('icon'),
            'description': cat_info.get('description'),
            'question_count': len(cat_info.get('questions', []))
        })

    return categories


def get_school_types():
    """获取所有学校类型"""
    data = load_question_bank()
    if not data:
        return []

    school_types = []
    for st_id, st_info in data.get('school_types', {}).items():
        school_types.append({
            'id': st_id,
            'name': st_info.get('name'),
            'name_en': st_info.get('name_en'),
            'examples': st_info.get('examples'),
            'description': st_info.get('description'),
            'focus': st_info.get('focus', [])
        })

    return school_types


def get_questions_by_category(category_id, limit=10):
    """获取指定分类的问题"""
    data = load_question_bank()
    if not data:
        return []

    category = data.get('categories', {}).get(category_id, {})
    questions = category.get('questions', [])

    # 随机选择问题
    if len(questions) > limit:
        questions = random.sample(questions, limit)

    return questions


def get_questions_for_interview(school_type, num_questions=5, categories=None):
    """
    为面试生成问题

    Args:
        school_type: 学校类型
        num_questions: 问题数量
        categories: 指定分类列表，None则随机选择

    Returns:
        list: 问题列表
    """
    data = load_question_bank()
    if not data:
        return []

    # 如果没有指定分类，则从所有分类中随机选择
    if not categories:
        categories = list(data.get('categories', {}).keys())

    # 根据学校类型调整分类权重
    category_weights = get_category_weights(school_type)

    # 生成问题列表
    questions = []
    seen_categories = set()

    for i in range(num_questions):
        # 根据权重选择分类
        available_categories = [c for c in categories if c in category_weights]
        if not available_categories:
            available_categories = categories

        # 加权随机选择分类
        weights = [category_weights.get(c, 1) for c in available_categories]
        total = sum(weights)
        weights = [w / total for w in weights]

        selected_category = random.choices(available_categories, weights=weights, k=1)[0]

        # 如果该分类已用过，换一个
        if selected_category in seen_categories:
            remaining = [c for c in available_categories if c not in seen_categories]
            if remaining:
                selected_category = random.choice(remaining)
            seen_categories.add(selected_category)
        else:
            seen_categories.add(selected_category)

        # 从分类中获取问题
        category_questions = data.get('categories', {}).get(selected_category, {}).get('questions', [])
        if category_questions:
            question = random.choice(category_questions)
            questions.append({
                'id': question.get('id'),
                'question': question.get('question'),
                'hint': question.get('hint'),
                'category': selected_category,
                'category_name': data.get('categories', {}).get(selected_category, {}).get('name'),
                'category_icon': data.get('categories', {}).get(selected_category, {}).get('icon'),
                'index': i + 1
            })

    return questions


def get_category_weights(school_type):
    """根据学校类型获取分类权重"""
    weights = {
        'philosophy': 1.0,
        'parenting': 1.0,
        'school_choice': 1.5,  # 选校原因更重要
        'family': 0.8,
        'child_understanding': 1.0,
        'cooperation': 1.2,  # 家校配合
        'situation': 1.0
    }

    if school_type == 'academic':
        # 学术型：更重视教育理念和选校原因
        weights['philosophy'] = 1.5
        weights['school_choice'] = 1.8
    elif school_type == 'international':
        # 国际型：更重视家校配合和育儿方式
        weights['cooperation'] = 1.5
        weights['parenting'] = 1.3
    elif school_type == 'traditional':
        # 传统型：更重视家庭背景和教育理念
        weights['family'] = 1.3
        weights['philosophy'] = 1.3

    return weights


# ============ AI 反馈功能 ============

def generate_follow_up_question(base_question, previous_answer):
    """
    使用 AI 生成追问问题

    Args:
        base_question: 基础问题
        previous_answer: 之前的回答

    Returns:
        str: 追问问题
    """
    system_prompt = """你是一位资深的小学面试官，善于通过追问来深入了解家长。
    你需要根据家长的回答，提出一个简短的追问问题。
    问题要切中要点，帮助更好地了解家长的教育理念和育儿方式。
    用普通话或广东话提问都可以，保持语气专业友善。"""

    user_prompt = """面试官问：「{}」
    家长回答：「{}」

    请提出一个追问问题，了解更多细节。
    请用中文提问。""".format(base_question, previous_answer)

    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and 'choices' in result:
        follow_up = result['choices'][0]['message']['content']
        follow_up = follow_up.strip()
        # 清理可能的引号
        if follow_up.startswith('"') and follow_up.endswith('"'):
            follow_up = follow_up[1:-1]
        if follow_up.startswith('"') and follow_up.endswith('"'):
            follow_up = follow_up[1:-1]
        return follow_up

    # 如果 API 失败，使用默认追问
    default_follow_ups = [
        '可以详细说明一下您的想法吗？',
        '您为什么这样认为呢？',
        '您能举个例子说明吗？',
        '您通常会怎么做呢？',
    ]
    return random.choice(default_follow_ups)


def evaluate_answer(question, answer, school_type):
    """
    评估家长的回答

    Args:
        question: 问题
        answer: 回答
        school_type: 学校类型

    Returns:
        dict: 评估结果
    """
    # 基础评估逻辑
    score = 0
    feedback = []
    strengths = []
    improvements = []

    # 评估回答长度
    answer_length = len(answer)
    if answer_length < 20:
        score += 1
        feedback.append('回答较简短，可以更详细一些')
    elif answer_length >= 50:
        score += 3
        strengths.append('表达详细')
    else:
        score += 2

    # 检查是否有具体例子
    if any(word in answer for word in ['例如', '比如', '比如说', '举例', '像']):
        score += 2
        strengths.append('有具体例子')

    # 检查是否有逻辑连接词
    if any(word in answer for word in ['因为', '所以', '首先', '其次', '然后', '因此']):
        score += 1
        strengths.append('表达有条理')

    # 检查是否表达配合意愿
    if any(word in answer for word in ['配合', '支持', '沟通', '参与', '愿意']):
        score += 2
        strengths.append('家校配合意愿强')

    # 检查是否有教育理念
    if any(word in answer for word in ['教育', '培养', '成长', '发展', '学习']):
        score += 1

    # 转换为百分制分数
    final_score = min(100, score * 15)

    # 生成反馈
    if final_score >= 85:
        feedback_text = '回答非常出色！您的教育理念和育儿经验都很棒。'
    elif final_score >= 70:
        feedback_text = '回答不错！建议可以更具体一些会更好。'
    elif final_score >= 50:
        feedback_text = '回答还行，建议多举例说明您的观点。'
    else:
        feedback_text = '建议更详细地表达您的想法和做法。'

    return {
        'score': final_score,
        'feedback': feedback_text,
        'strengths': strengths,
        'improvements': improvements,
        'suggestions': generate_suggestions(school_type)
    }


def generate_suggestions(school_type):
    """生成改进建议"""
    suggestions = []

    if school_type == 'academic':
        suggestions.append('可以多谈谈对孩子学术期望和学习规划')
    elif school_type == 'international':
        suggestions.append('可以强调您对国际化教育的理解和配合')
    elif school_type == 'traditional':
        suggestions.append('可以多谈谈传统价值观在家庭教育中的体现')
    else:
        suggestions.append('可以举例说明您的育儿实践经验')

    suggestions.append('回答时条理清晰，分点说明会更好')
    suggestions.append('表达对学校的了解和认可以增加好感度')

    return suggestions[:2]


def generate_detailed_feedback(question, answer, school_type):
    """
    使用 AI 生成详细反馈

    Args:
        question: 问题
        answer: 回答
        school_type: 学校类型

    Returns:
        dict: 详细反馈
    """
    school_info = {
        'academic': '学术型学校',
        'holistic': '全人型学校',
        'international': '国际型学校',
        'traditional': '传统名校'
    }
    school_name = school_info.get(school_type, '目标学校')

    system_prompt = f"""你是一位资深的教育专家，专门评估家长在面试中的表现。
    你需要根据家长对面试问题的回答，提供专业、具体、可操作的反馈。
    目标学校类型是：{school_name}。

    请从以下几个方面进行评估：
    1. 回答的完整性 - 是否涵盖了问题的各个方面
    2. 逻辑性 - 表达是否有条理
    3. 真实性 - 是否结合了实际经验
    4. 与学校类型的匹配度 - 是否符合该类型学校的期望
    5. 改进建议 - 如何让回答更出色

    请用中文回答，保持专业、友善的语气。"""

    user_prompt = f"""面试问题：「{question}」
    家长回答：「{answer}」

    请提供详细的反馈，包括：
    1. 评分（0-100）
    2. 优点
    3. 需要改进的地方
    4. 具体建议"""

    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and 'choices' in result:
        feedback_text = result['choices'][0]['message']['content']
        # 解析AI反馈（简化处理）
        return {
            'detailed_feedback': feedback_text,
            'uses_ai': True
        }

    # 如果 API 失败，使用基础评估
    basic_eval = evaluate_answer(question, answer, school_type)
    return {
        'score': basic_eval['score'],
        'feedback': basic_eval['feedback'],
        'strengths': basic_eval['strengths'],
        'improvements': basic_eval['improvements'],
        'suggestions': basic_eval['suggestions'],
        'uses_ai': False
    }


# ============ 面试会话管理 ============

class ParentInterviewSession:
    """家长面试会话管理"""

    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id, school_type, num_questions=5):
        """创建新的面试会话"""
        session_id = str(uuid.uuid4())

        # 生成问题
        questions = get_questions_for_interview(school_type, num_questions)

        self.sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'school_type': school_type,
            'questions': questions,
            'current_index': 0,
            'answers': [],
            'created_at': datetime.now().isoformat(),
            'status': 'in_progress'
        }

        return self.sessions[session_id]

    def get_session(self, session_id):
        """获取会话"""
        return self.sessions.get(session_id)

    def add_answer(self, session_id, question, answer, follow_up_question=None, follow_up_answer=None):
        """添加回答"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # 评估回答
        evaluation = evaluate_answer(question['question'], answer, session['school_type'])

        answer_data = {
            'question': question['question'],
            'question_id': question.get('id'),
            'category': question.get('category'),
            'answer': answer,
            'evaluation': evaluation,
            'timestamp': datetime.now().isoformat()
        }

        if follow_up_question and follow_up_answer:
            answer_data['follow_up_question'] = follow_up_question
            answer_data['follow_up_answer'] = follow_up_answer
            follow_up_eval = evaluate_answer(follow_up_question, follow_up_answer, session['school_type'])
            answer_data['follow_up_evaluation'] = follow_up_eval

        session['answers'].append(answer_data)
        session['current_index'] += 1

        return answer_data

    def finish_session(self, session_id):
        """完成会话"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        session['status'] = 'completed'
        session['finished_at'] = datetime.now().isoformat()

        # 计算总分
        total_score = 0
        answer_count = 0
        for answer in session['answers']:
            total_score += answer.get('evaluation', {}).get('score', 0)
            answer_count += 1

        if answer_count > 0:
            session['total_score'] = int(total_score / answer_count)
        else:
            session['total_score'] = 0

        return session

    def get_all_sessions(self, user_id=None):
        """获取所有会话"""
        if user_id:
            return [s for s in self.sessions.values() if s.get('user_id') == user_id]
        return list(self.sessions.values())


# 全局会话管理
parent_interview_session = ParentInterviewSession()


# ============ TTS 功能 ============

def generate_tts(text, voice_id=None):
    """
    生成语音

    Args:
        text: 要转换的文本
        voice_id: 语音ID（可选）

    Returns:
        dict: 包含音频数据或URL
    """
    if not MINIMAX_API_KEY:
        print("WARNING: MiniMax API Key not configured for TTS")
        return None

    try:
        # 使用 MiniMax TTS API
        payload = {
            "model": "speech-01-turbo",
            "text": text,
            "voice_setting": {
                "voice_id": voice_id or "male-qn-qingse",
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3"
            }
        }

        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        url = f"{MINIMAX_BASE_URL}/audio/generation"

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('data') and result['data'].get('audio'):
                return {
                    'audio_data': result['data']['audio']
                }

        return None

    except Exception as e:
        print(f"TTS error: {e}")
        return None


# ============ 面试报告生成 ============

def generate_interview_report(session_id):
    """
    生成面试报告

    Args:
        session_id: 会话ID

    Returns:
        dict: 报告数据
    """
    session = parent_interview_session.get_session(session_id)
    if not session:
        return None

    # 统计各分类的问题和回答情况
    category_stats = {}
    for answer in session.get('answers', []):
        cat = answer.get('category', 'unknown')
        if cat not in category_stats:
            category_stats[cat] = {
                'count': 0,
                'total_score': 0,
                'questions': []
            }
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_score'] += answer.get('evaluation', {}).get('score', 0)
        category_stats[cat]['questions'].append(answer)

    # 计算各分类平均分
    for cat in category_stats:
        count = category_stats[cat]['count']
        if count > 0:
            category_stats[cat]['avg_score'] = int(category_stats[cat]['total_score'] / count)
        else:
            category_stats[cat]['avg_score'] = 0

    # 生成改进建议
    improvements = []
    for cat, stats in category_stats.items():
        if stats['avg_score'] < 70:
            cat_name = get_category_name(cat)
            improvements.append(f"建议加强{cat_name}方面的准备")

    # 学校类型建议
    school_type = session.get('school_type')
    school_type_suggestions = {
        'academic': '学术型学校更注重孩子的学习能力和学术潜力，建议多谈谈对学术教育的重视和规划',
        'holistic': '全人型学校更注重全面发展，建议多强调孩子的兴趣爱好和综合素质培养',
        'international': '国际型学校更注重英文能力和国际化视野，建议多谈谈国际教育理念和英文学习',
        'traditional': '传统名校更注重礼仪和价值观，建议多谈谈家庭教育和品德培养'
    }

    report = {
        'session_id': session_id,
        'school_type': school_type,
        'total_questions': len(session.get('questions', [])),
        'answered_questions': len(session.get('answers', [])),
        'total_score': session.get('total_score', 0),
        'category_stats': category_stats,
        'answers': session.get('answers', []),
        'improvements': improvements,
        'school_type_suggestion': school_type_suggestions.get(school_type, ''),
        'created_at': session.get('created_at'),
        'finished_at': session.get('finished_at')
    }

    return report


def get_category_name(cat_id):
    """获取分类中文名称"""
    names = {
        'philosophy': '教育理念',
        'parenting': '育儿方式',
        'school_choice': '选校原因',
        'family': '家庭背景',
        'child_understanding': '对孩子了解',
        'cooperation': '家校配合',
        'situation': '情境题'
    }
    return names.get(cat_id, cat_id)
