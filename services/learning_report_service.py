"""
Learning Report Service
学习报告服务 - 周报/月报生成、数据分析
"""

import random
from datetime import datetime, timedelta
from services.question_bank_service import SAMPLE_QUESTIONS
from services.practice_data_service import get_category_progress, get_user_stats


def generate_weekly_report(user_id):
    """生成每周学习报告"""
    # 模拟数据 - 生产环境应从数据库获取
    stats = get_user_stats(user_id or 0)
    categories = get_category_progress(user_id or 0)

    # 计算进度百分比
    total_practice = sum(cat['practiced'] for cat in categories)
    total_questions = sum(cat['total'] for cat in categories)
    completion_rate = int((total_practice / total_questions * 100)) if total_questions > 0 else 0

    # 找出薄弱环节
    weak_categories = [c for c in categories if c['practiced'] == 0]
    strong_categories = [c for c in categories if c['practiced'] > 0 and (c['correct'] / c['practiced'] if c['practiced'] > 0 else 0) > 0.7]

    return {
        'report_type': 'weekly',
        'title': '本周学习报告',
        'period': '2026年2月10日 - 2026年2月16日',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'summary': {
            'total_practice': stats.get('total_practice_count', 0),
            'questions_answered': stats.get('total_questions_answered', 0),
            'streak_days': stats.get('current_streak', 0),
            'completion_rate': completion_rate,
            'time_spent_minutes': stats.get('total_time_minutes', 0)
        },
        'category_progress': categories,
        'highlights': [
            '本周完成了自我介绍分类的练习',
            '连续练习3天，保持良好习惯',
            '生活常识掌握度达到80%'
        ] if total_practice > 0 else [],
        'improvements': [
            '建议加强创意想象类题目练习',
            '处境题分类还未开始，建议尽快开始'
        ],
        'recommendations': [
            {'category': 'situational', 'title': '加强处境题练习', 'priority': 'high'},
            {'category': 'creative', 'title': '继续创意想象训练', 'priority': 'medium'}
        ],
        'streak_status': {
            'current': stats.get('current_streak', 0),
            'longest': stats.get('longest_streak', 0),
            'message': '继续坚持！明天就能打破记录' if stats.get('current_streak', 0) > 0 else '今天还没有练习，快开始吧'
        }
    }


def generate_monthly_report(user_id):
    """生成每月学习报告"""
    stats = get_user_stats(user_id or 0)
    categories = get_category_progress(user_id or 0)

    total_practice = sum(cat['practiced'] for cat in categories)
    total_questions = sum(cat['total'] for cat in categories)
    completion_rate = int((total_practice / total_questions * 100)) if total_questions > 0 else 0

    return {
        'report_type': 'monthly',
        'title': '本月学习报告',
        'period': '2026年2月1日 - 2026年2月28日',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'summary': {
            'total_practice': stats.get('total_practice_count', 0) * 4,
            'questions_answered': stats.get('total_questions_answered', 0) * 4,
            'streak_days': stats.get('longest_streak', 0),
            'completion_rate': completion_rate,
            'time_spent_minutes': stats.get('total_time_minutes', 0) * 4
        },
        'category_progress': categories,
        'achievements': [
            {'title': '初次尝试', 'desc': '完成第一次练习', 'icon': 'star'},
            {'title': '连续学习', 'desc': '连续练习3天', 'icon': 'local_fire_department'}
        ] if total_practice > 0 else [],
        'monthly_stats': {
            'week1': {'practice': 5, 'score': 75},
            'week2': {'practice': 8, 'score': 80},
            'week3': {'practice': 6, 'score': 78},
            'week4': {'practice': 0, 'score': 0}
        },
        'growth_insight': '相比上周，本周练习量增加了20%，正确率保持稳定。继续加油！' if total_practice > 0 else '本月刚开始使用，坚持练习会有明显进步！',
        'recommendations': [
            {'category': 'all', 'title': '保持每日练习习惯', 'priority': 'high'},
            {'category': 'situational', 'title': '重点加强处境题', 'priority': 'high'},
            {'category': 'self_intro', 'title': '巩固自我介绍', 'priority': 'medium'}
        ]
    }


def get_report_history(user_id):
    """获取历史报告列表"""
    return [
        {'id': 1, 'type': 'weekly', 'title': '第一周学习报告', 'date': '2026-02-09', 'completion_rate': 25},
        {'id': 2, 'type': 'weekly', 'title': '第二周学习报告', 'date': '2026-02-16', 'completion_rate': 35},
    ]


def generate_share_data(user_id):
    """生成分享数据"""
    stats = get_user_stats(user_id or 0)
    categories = get_category_progress(user_id or 0)

    total_practice = sum(cat['practiced'] for cat in categories)

    return {
        'title': '我的面试练习进度',
        'total_days': stats.get('current_streak', 0),
        'total_practice': stats.get('total_practice_count', 0),
        'categories_covered': len([c for c in categories if c['practiced'] > 0]),
        'total_categories': len(categories),
        'message': '坚持每天练习，面试成功在望！',
        'qr_code_url': '/api/qrcode?data=invite_user_123'
    }
