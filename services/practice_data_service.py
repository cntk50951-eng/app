"""
Practice Data Service
练习数据服务 - 错题本、进度追踪、每日挑战
"""

import random
from datetime import datetime, date, timedelta
from services.question_bank_service import SAMPLE_QUESTIONS


def get_user_stats(user_id):
    """获取用户练习统计数据"""
    # 使用内存模拟数据（生产环境应查询数据库）
    return {
        'total_practice_count': 0,
        'total_questions_answered': 0,
        'current_streak': 0,
        'longest_streak': 0,
        'total_time_minutes': 0
    }


def get_category_progress(user_id):
    """获取用户各分类的练习进度"""
    categories = [
        {'category': 'self_intro', 'category_name_zh': '自我介绍', 'total': 5, 'practiced': 0, 'correct': 0},
        {'category': 'family', 'category_name_zh': '家庭背景', 'total': 5, 'practiced': 0, 'correct': 0},
        {'category': 'hobbies', 'category_name_zh': '兴趣爱好', 'total': 5, 'practiced': 0, 'correct': 0},
        {'category': 'school', 'category_name_zh': '学校相关', 'total': 5, 'practiced': 0, 'correct': 0},
        {'category': 'life', 'category_name_zh': '生活常识', 'total': 5, 'practiced': 0, 'correct': 0},
        {'category': 'science', 'category_name_zh': '科学常识', 'total': 3, 'practiced': 0, 'correct': 0},
        {'category': 'society', 'category_name_zh': '社会常识', 'total': 2, 'practiced': 0, 'correct': 0},
        {'category': 'creative', 'category_name_zh': '创意想象', 'total': 3, 'practiced': 0, 'correct': 0},
        {'category': 'situational', 'category_name_zh': '处境题', 'total': 5, 'practiced': 0, 'correct': 0},
        {'category': 'group', 'category_name_zh': '小组面试', 'total': 3, 'practiced': 0, 'correct': 0},
    ]
    return categories


def get_wrong_questions(user_id, limit=20):
    """获取用户的错题列表"""
    return []


def get_favorites(user_id, limit=20):
    """获取用户收藏的题目"""
    return []


def get_daily_challenge(user_id):
    """获取今日挑战"""
    today = date.today()

    # 生成10道今日挑战题目
    challenge_questions = random.sample(SAMPLE_QUESTIONS, min(10, len(SAMPLE_QUESTIONS)))

    return {
        'date': today.isoformat(),
        'questions': challenge_questions,
        'completed': False,
        'questions_completed': 0,
        'total_questions': 10,
        'streak_days': 0
    }


def get_recommended_questions(user_id, categories=None, limit=10):
    """智能推荐题目 - 基于用户薄弱环节"""
    # 优先推荐高频+用户未练过的题目
    high_freq = [q for q in SAMPLE_QUESTIONS if q.get('frequency') == 'high']
    recommended = random.sample(high_freq, min(limit, len(high_freq)))
    return recommended


def record_practice(user_id, question_id, is_correct=True):
    """记录练习结果"""
    # 生产环境应写入数据库
    return True


def add_favorite(user_id, question_id):
    """添加收藏"""
    return True


def remove_favorite(user_id, question_id):
    """取消收藏"""
    return True


def mark_wrong(user_id, question_id):
    """标记错题"""
    return True


def unmark_wrong(user_id, question_id):
    """取消错题标记"""
    return True
