"""
AI智能匹配服务
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', '')

# 导入AI服务
try:
    from services.ai_generator import generate_text
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


def get_db_connection():
    """获取数据库连接"""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def get_child_profile(user_id):
    """获取孩子画像数据"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 获取孩子基本信息
        cursor.execute("""
            SELECT cp.*, u.email
            FROM child_profiles cp
            JOIN users u ON cp.user_id = u.id
            WHERE cp.user_id = %s
        """, (user_id,))

        profile = cursor.fetchone()

        if profile:
            # 获取兴趣
            cursor.execute("""
                SELECT i.name_zh
                FROM child_interests ci
                JOIN interests i ON ci.interest_id = i.id
                WHERE ci.profile_id = %s
            """, (profile['id'],))
            interests = cursor.fetchall()
            profile['interests'] = [i['name_zh'] for i in interests]

            # 获取目标学校
            cursor.execute("""
                SELECT st.name_zh
                FROM target_schools ts
                JOIN school_types st ON ts.school_type_id = st.id
                WHERE ts.child_profile_id = %s
            """, (profile['id'],))
            schools = cursor.fetchall()
            profile['target_schools'] = [s['name_zh'] for s in schools]

        cursor.close()
        conn.close()
        return profile
    except Exception as e:
        print(f"Error fetching child profile: {e}")
        return None


def get_school_info(school_id):
    """获取学校信息"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM school_question_bank WHERE school_id = s.id) as question_count
            FROM schools s
            WHERE s.id = %s
        """, (school_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Error fetching school info: {e}")
        return None


def get_school_questions_by_type(school_id, question_types):
    """根据题型获取题目"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, question_text, question_type, difficulty, category, sample_answer, tips
            FROM school_question_bank
            WHERE school_id = %s AND question_type = ANY(%s)
            ORDER BY difficulty, created_at DESC
            LIMIT 20
        """, (school_id, question_types))

        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []


def analyze_strengths_weaknesses(child_profile, school_questions):
    """分析强弱项"""
    strengths = []
    weaknesses = []

    if not child_profile or not school_questions:
        return strengths, weaknesses

    interests = child_profile.get('interests', [])

    # 根据兴趣分析
    interest_types = {
        '運動': ['situational', 'creative'],
        '閱讀': ['self_intro', 'language'],
        '科學': ['science', 'logic'],
        '藝術': ['creative', 'language'],
        '數學': ['math', 'logic']
    }

    # 根据孩子的特点给出建议
    profile_analysis = child_profile.get('analysis') if child_profile else None

    return strengths, weaknesses


def generate_ai_recommendation(child_profile, school_info, questions):
    """使用AI生成个性化推荐"""
    if not AI_AVAILABLE:
        return generate_default_recommendation(child_profile, school_info, questions)

    try:
        prompt = f"""
你是一個專業的教育顧問，請根據以下信息為孩子生成面試準備建議：

孩子信息：
- 年齡：{child_profile.get('child_age', '未知')}歲
- 姓名：{child_profile.get('child_name', '孩子')}
- 興趣愛好：{', '.join(child_profile.get('interests', []))}
- 目標學校：{', '.join(child_profile.get('target_schools', []))}

學校信息：
- 名稱：{school_info.get('name_zh', '未知')}
- 面試形式：{school_info.get('interview_format', '未知')}
- 學校類別：{school_info.get('category', '未知')}

請提供：
1. 孩子的優勢分析（strengths）
2. 需要加強的方面（weaknesses）
3. 具體的準備建議（suggestions）

請用JSON格式返回：
{{
    "strengths": ["優勢1", "優勢2"],
    "weaknesses": ["需改進1", "需改進2"],
    "suggestions": ["建議1", "建議2"]
}}
"""

        response = generate_text(prompt)
        if response:
            # 尝试解析JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                pass

    except Exception as e:
        print(f"AI recommendation error: {e}")

    return generate_default_recommendation(child_profile, school_info, questions)


def generate_default_recommendation(child_profile, school_info, questions):
    """生成默认推荐（无AI时）"""
    strengths = []
    weaknesses = []
    suggestions = []

    if child_profile:
        child_name = child_profile.get('child_name', '孩子')
        interests = child_profile.get('interests', [])

        strengths.append(f"{child_name}有良好的表達能力")
        if interests:
            strengths.append(f"對{', '.join(interests[:2])}有濃厚興趣")

        weaknesses.append("需要多加練習自我介紹")
        weaknesses.append("建議增加模擬面試練習")

        suggestions.append("每天練習1-2次自我介紹")
        suggestions.append("觀看相關面試視頻學習")
        suggestions.append("與家長進行模擬問答")
    else:
        strengths.append("孩子年輕有活力")
        weaknesses.append("缺乏面試經驗")
        suggestions.append("建議先了解目標學校的面試形式")

    # 根据学校类型添加建议
    if school_info:
        school_type = school_info.get('category', '')
        if school_type == 'academic':
            suggestions.append("加強學術問題的準備")
        elif school_type == 'international':
            suggestions.append("加強英語口語練習")

    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggestions': suggestions
    }


def recommend_questions(user_id, school_id=None, profile_id=None):
    """
    AI智能推荐题目

    Args:
        user_id: 用户ID
        school_id: 可选，学校ID
        profile_id: 可选，孩子画像ID

    Returns:
        dict: 包含推荐题目和分析结果
    """
    # 获取孩子画像
    child_profile = get_child_profile(user_id)

    # 获取学校信息
    school_info = None
    if school_id:
        school_info = get_school_info(school_id)

    # 根据画像选择合适的题目类型
    question_types = ['self_intro']  # 默认必考题

    if child_profile:
        interests = child_profile.get('interests', [])
        # 根据兴趣添加相关题型
        if any('運動' in i or '体育' in i for i in interests):
            question_types.append('situational')
        if any('閱讀' in i or '阅读' in i for i in interests):
            question_types.append('language')
        if any('科學' in i or '科学' in i for i in interests):
            question_types.append('science')
            question_types.append('logic')

    # 添加常见题型
    question_types.extend(['family', 'hobbies', 'school', 'creative'])

    # 获取题目
    questions = []
    if school_id:
        questions = get_school_questions_by_type(school_id, question_types)
    else:
        # 如果没有指定学校，获取所有学校的精选题
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT q.id, q.school_id, q.question_text, q.question_type,
                           q.difficulty, q.category, q.sample_answer, q.tips,
                           s.name_zh as school_name
                    FROM school_question_bank q
                    JOIN schools s ON q.school_id = s.id
                    WHERE q.question_type = ANY(%s) AND q.is_featured = TRUE
                    ORDER BY q.difficulty, q.view_count DESC
                    LIMIT 30
                """, (question_types,))
                questions = cursor.fetchall()
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error fetching all questions: {e}")

    # 生成分析和建议
    if school_info or child_profile:
        analysis = generate_ai_recommendation(
            child_profile,
            school_info or {'name_zh': '目標學校', 'category': '待定'},
            questions
        )
    else:
        analysis = generate_default_recommendation(child_profile, school_info, questions)

    # 计算匹配度
    match_score = 0
    if child_profile and school_info:
        # 简单计算匹配度
        if school_info.get('category') == 'academic':
            match_score = 75
        elif school_info.get('category') == 'holistic':
            match_score = 85
        else:
            match_score = 70
    else:
        match_score = 50

    # 保存匹配记录
    record_id = save_match_record(user_id, school_id, profile_id, match_score, questions, analysis)

    return {
        'match_score': match_score,
        'questions': questions,
        'analysis': analysis,
        'child_profile': child_profile,
        'school': school_info,
        'record_id': record_id
    }


def save_match_record(user_id, school_id, profile_id, match_score, questions, analysis):
    """保存匹配记录"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO ai_match_records
            (user_id, school_id, child_profile_id, match_score, recommended_questions, strengths, weaknesses, suggestions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            school_id,
            profile_id,
            match_score,
            json.dumps([{'id': q['id'], 'text': q['question_text']} for q in questions[:10]]),
            json.dumps(analysis.get('strengths', [])),
            json.dumps(analysis.get('weaknesses', [])),
            json.dumps(analysis.get('suggestions', []))
        ))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return result['id'] if result else None
    except Exception as e:
        print(f"Error saving match record: {e}")
        return None


def get_match_history(user_id, limit=10):
    """获取匹配历史"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT mr.*, s.name_zh as school_name
            FROM ai_match_records mr
            LEFT JOIN schools s ON mr.school_id = s.id
            WHERE mr.user_id = %s
            ORDER BY mr.created_at DESC
            LIMIT %s
        """, (user_id, limit))

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # 转换JSON字段
        for row in results:
            if row.get('recommended_questions') and isinstance(row['recommended_questions'], str):
                row['recommended_questions'] = json.loads(row['recommended_questions'])
            if row.get('strengths') and isinstance(row['strengths'], str):
                row['strengths'] = json.loads(row['strengths'])
            if row.get('weaknesses') and isinstance(row['weaknesses'], str):
                row['weaknesses'] = json.loads(row['weaknesses'])
            if row.get('suggestions') and isinstance(row['suggestions'], str):
                row['suggestions'] = json.loads(row['suggestions'])
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else row['created_at']

        return results
    except Exception as e:
        print(f"Error fetching match history: {e}")
        return []


def get_question_types():
    """获取所有题型"""
    return [
        {'id': 'self_intro', 'name': '自我介紹', 'icon': 'person'},
        {'id': 'family', 'name': '家庭相關', 'icon': 'family_restroom'},
        {'id': 'hobbies', 'name': '興趣愛好', 'icon': 'favorite'},
        {'id': 'school', 'name': '學校相關', 'icon': 'school'},
        {'id': 'life', 'name': '日常生活', 'icon': 'daily_life'},
        {'id': 'science', 'name': '科學常识', 'icon': 'science'},
        {'id': 'society', 'name': '社會認知', 'icon': 'public'},
        {'id': 'creative', 'name': '創意表達', 'icon': 'lightbulb'},
        {'id': 'situational', 'name': '情境應對', 'icon': 'question_answer'},
        {'id': 'group', 'name': '小組活動', 'icon': 'groups'},
        {'id': 'math', 'name': '數學', 'icon': 'calculate'},
        {'id': 'language', 'name': '語言', 'icon': 'translate'}
    ]
