"""
Question Bank Service
面试真题库服务
"""

import random
from db.database import get_db_connection


# Sample questions as fallback when database is not available
SAMPLE_QUESTIONS = [
    {'question_id': 'Q00001', 'category': 'self_intro', 'category_name_zh': '自我介绍',
     'question_zh': '你叫什么名字？', 'question_en': 'What is your name?',
     'answer_tips': '简洁回答姓名', 'frequency': 'high', 'difficulty': 'easy'},
    {'question_id': 'Q00002', 'category': 'self_intro', 'category_name_zh': '自我介绍',
     'question_zh': '你今年几岁？', 'question_en': 'How old are you?',
     'answer_tips': '清晰回答年龄', 'frequency': 'high', 'difficulty': 'easy'},
    {'question_id': 'Q00003', 'category': 'self_intro', 'category_name_zh': '自我介绍',
     'question_zh': '你可以介绍一下自己吗？', 'question_en': 'Can you introduce yourself?',
     'answer_tips': '包括姓名、年龄、兴趣爱好', 'frequency': 'high', 'difficulty': 'medium'},
    {'question_id': 'Q00004', 'category': 'family', 'category_name_zh': '家庭背景',
     'question_zh': '你家里有谁和你一起住？', 'question_en': 'Who lives with you?',
     'answer_tips': '列出主要家庭成员', 'frequency': 'high', 'difficulty': 'easy'},
    {'question_id': 'Q00005', 'category': 'family', 'category_name_zh': '家庭背景',
     'question_zh': '爸爸妈妈做什么工作？', 'question_en': 'What do your parents do?',
     'answer_tips': '简单说明父母职业', 'frequency': 'high', 'difficulty': 'medium'},
    {'question_id': 'Q00006', 'category': 'hobbies', 'category_name_zh': '兴趣爱好',
     'question_zh': '你在幼稚园最喜欢上什么课？为什么？', 'question_en': 'What is your favorite class? Why?',
     'answer_tips': '说明喜欢的科目和原因', 'frequency': 'high', 'difficulty': 'medium'},
    {'question_id': 'Q00007', 'category': 'hobbies', 'category_name_zh': '兴趣爱好',
     'question_zh': '你有什么兴趣爱好？', 'question_en': 'What are your hobbies?',
     'answer_tips': '可列举多个兴趣', 'frequency': 'high', 'difficulty': 'easy'},
    {'question_id': 'Q00008', 'category': 'school', 'category_name_zh': '学校相关',
     'question_zh': '你喜欢我们学校吗？为什么？', 'question_en': 'Do you like our school? Why?',
     'answer_tips': '表达对学校的向往', 'frequency': 'high', 'difficulty': 'medium'},
    {'question_id': 'Q00009', 'category': 'life', 'category_name_zh': '生活常识',
     'question_zh': '今天你是怎么来学校的？', 'question_en': 'How did you come to school today?',
     'answer_tips': '描述交通工具', 'frequency': 'high', 'difficulty': 'easy'},
    {'question_id': 'Q00010', 'category': 'life', 'category_name_zh': '生活常识',
     'question_zh': '过马路时要注意什么？', 'question_en': 'What should you pay attention to when crossing the road?',
     'answer_tips': '描述交通安全', 'frequency': 'high', 'difficulty': 'easy'},
    {'question_id': 'Q00011', 'category': 'situational', 'category_name_zh': '处境题',
     'question_zh': '如果在地上捡到钱，你会怎么做？', 'question_en': 'What would you do if you found money?',
     'answer_tips': '展示诚实品格', 'frequency': 'high', 'difficulty': 'medium'},
    {'question_id': 'Q00012', 'category': 'situational', 'category_name_zh': '处境题',
     'question_zh': '如果在街上和父母失散了，你会怎么做？', 'question_en': 'What if you got lost?',
     'answer_tips': '展示应变能力', 'frequency': 'high', 'difficulty': 'medium'},
    {'question_id': 'Q00013', 'category': 'science', 'category_name_zh': '科学常识',
     'question_zh': '你知道哪些动物？', 'question_en': 'What animals do you know?',
     'answer_tips': '可分类列举', 'frequency': 'medium', 'difficulty': 'easy'},
    {'question_id': 'Q00014', 'category': 'creative', 'category_name_zh': '创意想象',
     'question_zh': '如果你有一支魔术笔，你会画什么？', 'question_en': 'If you had a magic pen, what would you draw?',
     'answer_tips': '展示想象力', 'frequency': 'medium', 'difficulty': 'easy'},
    {'question_id': 'Q00015', 'category': 'group', 'category_name_zh': '小组面试',
     'question_zh': '请和其他小朋友一起完成这个任务', 'question_en': 'Please complete this task with others',
     'answer_tips': '展示团队合作能力', 'frequency': 'high', 'difficulty': 'medium'},
]

CATEGORIES = [
    {'category': 'self_intro', 'category_name_zh': '自我介绍', 'count': 15},
    {'category': 'family', 'category_name_zh': '家庭背景', 'count': 15},
    {'category': 'hobbies', 'category_name_zh': '兴趣爱好', 'count': 15},
    {'category': 'school', 'category_name_zh': '学校相关', 'count': 15},
    {'category': 'life', 'category_name_zh': '生活常识', 'count': 15},
    {'category': 'science', 'category_name_zh': '科学常识', 'count': 15},
    {'category': 'society', 'category_name_zh': '社会常识', 'count': 15},
    {'category': 'creative', 'category_name_zh': '创意想象', 'count': 15},
    {'category': 'situational', 'category_name_zh': '处境题', 'count': 15},
    {'category': 'group', 'category_name_zh': '小组面试', 'count': 15},
]


def _check_table_exists():
    """Check if interview_questions table exists"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interview_questions'")
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except:
        return False


def get_question_by_id(question_id):
    """根据ID获取题目"""
    if not _check_table_exists():
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM interview_questions WHERE question_id = ?",
        (question_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return dict(result) if result else None


def get_questions_by_category(category, limit=50):
    """根据分类获取题目"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM interview_questions
           WHERE category = ? AND is_active = 1
           ORDER BY RANDOM() LIMIT ?""",
        (category, limit)
    )

    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def get_questions_by_school_type(school_type, limit=50):
    """根据学校类型获取题目"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM interview_questions
           WHERE school_types LIKE ? AND is_active = 1
           ORDER BY RANDOM() LIMIT ?""",
        (f'%{school_type}%', limit)
    )

    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def get_high_frequency_questions(limit=100):
    """获取高频题目"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM interview_questions
           WHERE frequency = 'high' AND is_active = 1
           ORDER BY RANDOM() LIMIT ?""",
        (limit,)
    )

    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def get_questions_by_school_and_category(school_type, category, limit=20):
    """根据学校类型和分类获取题目"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM interview_questions
           WHERE category = ? AND school_types LIKE ? AND is_active = 1
           ORDER BY RANDOM() LIMIT ?""",
        (category, f'%{school_type}%', limit)
    )

    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def get_all_categories():
    """获取所有分类"""
    if not _check_table_exists():
        return CATEGORIES

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT category, category_name_zh, COUNT(*) as count
               FROM interview_questions
               WHERE is_active = 1
               GROUP BY category
               ORDER BY count DESC"""
        )

        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
    except:
        return CATEGORIES


def get_random_questions(school_type=None, categories=None, limit=10):
    """随机获取题目组合"""
    if not _check_table_exists():
        # Use sample questions
        filtered = SAMPLE_QUESTIONS
        if categories:
            filtered = [q for q in filtered if q['category'] in categories]
        random.shuffle(filtered)
        return filtered[:limit]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if categories and len(categories) > 0:
            category_list = "','".join(categories)
            query = f"""SELECT * FROM interview_questions
                        WHERE category IN ('{category_list}') AND is_active = 1"""

            if school_type:
                query += f" AND school_types LIKE '%{school_type}%'"

            query += f" ORDER BY RANDOM() LIMIT {limit}"
            cursor.execute(query)
        elif school_type:
            cursor.execute(
                """SELECT * FROM interview_questions
                   WHERE school_types LIKE ? AND is_active = 1
                   ORDER BY RANDOM() LIMIT ?""",
                (f'%{school_type}%', limit)
            )
        else:
            cursor.execute(
                """SELECT * FROM interview_questions
                   WHERE is_active = 1
                   ORDER BY RANDOM() LIMIT ?""",
                (limit,)
            )

        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
    except:
        filtered = SAMPLE_QUESTIONS
        if categories:
            filtered = [q for q in filtered if q['category'] in categories]
        random.shuffle(filtered)
        return filtered[:limit]


def save_practice_history(user_id, question_id, user_answer=None):
    """保存练习历史"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO question_practice_history (user_id, question_id, user_answer)
           VALUES (?, ?, ?)""",
        (user_id, question_id, user_answer)
    )

    conn.commit()
    conn.close()


def get_user_practice_history(user_id, limit=50):
    """获取用户练习历史"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT q.*, p.practiced_at, p.user_answer
           FROM question_practice_history p
           JOIN interview_questions q ON p.question_id = q.question_id
           WHERE p.user_id = ?
           ORDER BY p.practiced_at DESC
           LIMIT ?""",
        (user_id, limit)
    )

    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def get_question_statistics():
    """获取题目统计"""
    if not _check_table_exists():
        return {
            'total': len(SAMPLE_QUESTIONS),
            'by_category': CATEGORIES,
            'by_frequency': [
                {'frequency': 'high', 'count': 10},
                {'frequency': 'medium', 'count': 4},
                {'frequency': 'low', 'count': 1}
            ],
            'by_difficulty': [
                {'difficulty': 'easy', 'count': 8},
                {'difficulty': 'medium', 'count': 6},
                {'difficulty': 'hard', 'count': 1}
            ]
        }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) as total FROM interview_questions WHERE is_active = 1")
        total = cursor.fetchone()['total']

        # By category
        cursor.execute(
            """SELECT category, category_name_zh, COUNT(*) as count
               FROM interview_questions
               WHERE is_active = 1
               GROUP BY category
               ORDER BY count DESC"""
        )
        by_category = cursor.fetchall()

        # By frequency
        cursor.execute(
            """SELECT frequency, COUNT(*) as count
               FROM interview_questions
               WHERE is_active = 1
               GROUP BY frequency"""
        )
        by_frequency = cursor.fetchall()

        # By difficulty
        cursor.execute(
            """SELECT difficulty, COUNT(*) as count
               FROM interview_questions
               WHERE is_active = 1
               GROUP BY difficulty"""
        )
        by_difficulty = cursor.fetchall()

        conn.close()

        return {
            'total': total,
            'by_category': [dict(row) for row in by_category],
            'by_frequency': [dict(row) for row in by_frequency],
            'by_difficulty': [dict(row) for row in by_difficulty]
        }
    except:
        return {
            'total': len(SAMPLE_QUESTIONS),
            'by_category': CATEGORIES,
            'by_frequency': [
                {'frequency': 'high', 'count': 10},
                {'frequency': 'medium', 'count': 4},
                {'frequency': 'low', 'count': 1}
            ],
            'by_difficulty': [
                {'difficulty': 'easy', 'count': 8},
                {'difficulty': 'medium', 'count': 6},
                {'difficulty': 'hard', 'count': 1}
            ]
        }
