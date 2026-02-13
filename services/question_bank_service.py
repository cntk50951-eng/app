"""
Question Bank Service
面试真题库服务
"""

import random
from db.database import get_db_connection


def get_question_by_id(question_id):
    """根据ID获取题目"""
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


def get_random_questions(school_type=None, categories=None, limit=10):
    """随机获取题目组合"""
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
