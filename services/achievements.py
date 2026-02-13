"""
Achievements Service - Manages badges, progress tracking, and learning reports.
"""

import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '')

if DATABASE_URL:
    from db.database import (
        get_all_badges, get_user_badges, get_user_badge_progress,
        award_badge, update_badge_progress, update_user_progress,
        mark_topic_complete, get_user_stats, record_practice_session,
        get_user_practice_sessions, create_learning_report, get_user_reports,
        get_latest_report, get_user_all_progress
    )


def calculate_badge_progress(user_id, stats):
    """
    Calculate and update progress for all badges based on user stats.
    Returns list of newly earned badges.
    """
    if not DATABASE_URL:
        return []

    newly_earned = []
    badges = get_all_badges()

    for badge in badges:
        badge_id = badge['id']
        req_type = badge['requirement_type']
        req_value = badge['requirement_value']

        # Get current progress
        progress = 0

        if req_type == 'topics_completed':
            # Progress towards completing topics
            progress = min(100, (stats.get('completed_topics', 0) / req_value) * 100) if req_value else 0

            if stats.get('completed_topics', 0) >= req_value:
                # Check if already earned
                user_badges = get_user_badges(user_id)
                if not any(b['id'] == badge_id for b in user_badges):
                    award_badge(user_id, badge_id)
                    newly_earned.append(badge)
            else:
                update_badge_progress(user_id, badge_id, int(progress))

        elif req_type == 'practice_count':
            # Progress towards practice count
            progress = min(100, (stats.get('total_practices', 0) / req_value) * 100) if req_value else 0

            if stats.get('total_practices', 0) >= req_value:
                user_badges = get_user_badges(user_id)
                if not any(b['id'] == badge_id for b in user_badges):
                    award_badge(user_id, badge_id)
                    newly_earned.append(badge)
            else:
                update_badge_progress(user_id, badge_id, int(progress))

        elif req_type == 'streak_days':
            # Progress towards streak days
            progress = min(100, (stats.get('streak_days', 0) / req_value) * 100) if req_value else 0

            if stats.get('streak_days', 0) >= req_value:
                user_badges = get_user_badges(user_id)
                if not any(b['id'] == badge_id for b in user_badges):
                    award_badge(user_id, badge_id)
                    newly_earned.append(badge)
            else:
                update_badge_progress(user_id, badge_id, int(progress))

        elif req_type == 'perfect_score':
            # Progress towards perfect scores
            progress = min(100, (stats.get('perfect_scores', 0) / req_value) * 100) if req_value else 0

            if stats.get('perfect_scores', 0) >= req_value:
                user_badges = get_user_badges(user_id)
                if not any(b['id'] == badge_id for b in user_badges):
                    award_badge(user_id, badge_id)
                    newly_earned.append(badge)
            else:
                update_badge_progress(user_id, badge_id, int(progress))

    return newly_earned


def check_and_award_badges(user_id, topic_id=None):
    """
    Check and award badges based on user activity.
    Returns list of newly earned badges.
    """
    if not DATABASE_URL:
        return []

    stats = get_user_stats(user_id)

    # Calculate streak days (simplified - would need proper date tracking)
    stats['streak_days'] = 3  # Mock value for now

    # Calculate perfect scores
    sessions = get_user_practice_sessions(user_id, limit=100)
    perfect_scores = sum(1 for s in sessions if s.get('score') == 100)
    stats['perfect_scores'] = perfect_scores

    return calculate_badge_progress(user_id, stats)


def get_achievement_summary(user_id):
    """Get achievement summary for user."""
    if not DATABASE_URL:
        # Return mock data for development
        return {
            'total_badges': 13,
            'earned_badges': 2,
            'total_points': 20,
            'badges': [
                {'id': 'first_step', 'name_zh': '第一步', 'icon_emoji': '🌟', 'earned': True, 'rarity': 'common'},
                {'id': 'streak_3', 'name_zh': '小試牛刀', 'icon_emoji': '💪', 'earned': True, 'rarity': 'common'},
            ]
        }

    badges = get_user_badge_progress(user_id)
    earned = [b for b in badges if b.get('earned')]
    total_points = sum(b.get('points', 0) for b in earned)

    return {
        'total_badges': len(badges),
        'earned_badges': len(earned),
        'total_points': total_points,
        'badges': [
            {
                'id': b['id'],
                'name_zh': b['name_zh'],
                'name_en': b.get('name_en'),
                'description': b.get('description'),
                'icon_emoji': b.get('icon_emoji'),
                'category': b.get('category'),
                'rarity': b.get('rarity'),
                'earned': b.get('earned', False),
                'progress': b.get('progress', 0),
                'earned_at': b.get('earned_at')
            }
            for b in badges
        ]
    }


def get_progress_summary(user_id):
    """Get learning progress summary."""
    if not DATABASE_URL:
        # Return mock data for development
        return {
            'total_topics': 9,
            'completed_topics': 1,
            'in_progress_topics': 1,
            'not_started_topics': 7,
            'total_practices': 7,
            'total_minutes': 45,
            'completion_percent': 11,
            'current_streak': 3,
            'longest_streak': 5,
            'recent_activity': []
        }

    progress = get_user_all_progress(user_id) if 'get_user_all_progress' in dir() else []
    sessions = get_user_practice_sessions(user_id, limit=10)
    stats = get_user_stats(user_id)

    completed = [p for p in progress if p.get('status') == 'completed']
    in_progress = [p for p in progress if p.get('status') == 'in_progress']
    not_started = [p for p in progress if p.get('status') == 'not_started']

    total_minutes = stats.get('total_practice_time', 0) // 60 if stats else 0

    # Calculate completion percent (assuming 9 topics)
    total_topics = 9
    completion_percent = int((len(completed) / total_topics) * 100) if total_topics else 0

    return {
        'total_topics': total_topics,
        'completed_topics': len(completed),
        'in_progress_topics': len(in_progress),
        'not_started_topics': len(not_started),
        'total_practices': stats.get('total_practices', 0),
        'total_minutes': total_minutes,
        'completion_percent': completion_percent,
        'current_streak': 3,  # Would need proper streak calculation
        'longest_streak': 5,
        'recent_activity': [
            {
                'topic_id': s['topic_id'],
                'date': s['created_at'].isoformat() if s.get('created_at') else None,
                'duration': s.get('duration_seconds', 0) // 60,
                'score': s.get('score')
            }
            for s in sessions[:5]
        ]
    }


def generate_weekly_report(user_id):
    """Generate weekly learning report."""
    if not DATABASE_URL:
        # Return mock data
        return {
            'report_type': 'weekly',
            'period_start': (date.today() - timedelta(days=7)).isoformat(),
            'period_end': date.today().isoformat(),
            'topics_completed': 1,
            'total_practice_time': 45,
            'average_score': 85,
            'streak_days': 3,
            'badges_earned': 1,
            'highlights': ['完成了自我介紹主題', '連續練習3天'],
            'improvements': ['可以多練習眼神接觸'],
            'recommendation': '下週目標：完成興趣愛好主題'
        }

    # Get stats for the past week
    stats = get_user_stats(user_id)
    sessions = get_user_practice_sessions(user_id, limit=100)

    # Calculate weekly stats
    week_ago = datetime.now() - timedelta(days=7)
    week_sessions = [s for s in sessions if s.get('created_at') and s['created_at'] >= week_ago]

    topics_completed = 0  # Would need to calculate from progress
    total_practice_time = sum(s.get('duration_seconds', 0) for s in week_sessions) // 60
    scores = [s.get('score') for s in week_sessions if s.get('score')]
    average_score = sum(scores) / len(scores) if scores else 0

    # Get recent badges
    earned_badges = get_user_badges(user_id)
    recent_badges = [b for b in earned_badges if b.get('earned_at') and b['earned_at'] >= week_ago]

    # Create report
    report = create_learning_report(
        user_id=user_id,
        report_type='weekly',
        period_start=date.today() - timedelta(days=7),
        period_end=date.today(),
        topics_completed=topics_completed,
        total_practice_time=total_practice_time,
        average_score=round(average_score, 2),
        streak_days=stats.get('streak_days', 0),
        badges_earned=len(recent_badges),
        highlights=['完成了自我介紹主題'] if topics_completed > 0 else [],
        improvements=['可以多練習眼神接觸'],
        recommendation='下週目標：完成興趣愛好主題'
    )

    return report


def generate_monthly_report(user_id):
    """Generate monthly learning report."""
    if not DATABASE_URL:
        return {
            'report_type': 'monthly',
            'period_start': (date.today() - timedelta(days=30)).isoformat(),
            'period_end': date.today().isoformat(),
            'topics_completed': 2,
            'total_practice_time': 180,
            'average_score': 82,
            'streak_days': 7,
            'badges_earned': 2,
            'highlights': ['本月完成2個主題', '獲得「第一步」徽章'],
            'improvements': ['需要加強邏輯思維練習'],
            'recommendation': '下月目標：完成全部基礎主題'
        }

    # Similar to weekly but for the past month
    stats = get_user_stats(user_id)
    sessions = get_user_practice_sessions(user_id, limit=200)

    month_ago = datetime.now() - timedelta(days=30)
    month_sessions = [s for s in sessions if s.get('created_at') and s['created_at'] >= month_ago]

    topics_completed = 0
    total_practice_time = sum(s.get('duration_seconds', 0) for s in month_sessions) // 60
    scores = [s.get('score') for s in month_sessions if s.get('score')]
    average_score = sum(scores) / len(scores) if scores else 0

    earned_badges = get_user_badges(user_id)
    recent_badges = [b for b in earned_badges if b.get('earned_at') and b['earned_at'] >= month_ago]

    report = create_learning_report(
        user_id=user_id,
        report_type='monthly',
        period_start=date.today() - timedelta(days=30),
        period_end=date.today(),
        topics_completed=topics_completed,
        total_practice_time=total_practice_time,
        average_score=round(average_score, 2),
        streak_days=stats.get('streak_days', 0),
        badges_earned=len(recent_badges),
        highlights=[f'本月完成{topics_completed}個主題'] if topics_completed > 0 else [],
        improvements=['需要加強邏輯思維練習'],
        recommendation='下月目標：完成全部基礎主題'
    )

    return report


def get_share_data(user_id):
    """Generate shareable data for social media."""
    summary = get_progress_summary(user_id)
    achievements = get_achievement_summary(user_id)

    return {
        'child_name': '小明',  # Would get from session/profile
        'topics_completed': summary.get('completed_topics', 0),
        'total_topics': summary.get('total_topics', 9),
        'streak_days': summary.get('current_streak', 0),
        'total_minutes': summary.get('total_minutes', 0),
        'badges_earned': achievements.get('earned_badges', 0),
        'total_badges': achievements.get('total_badges', 13),
        'completion_percent': summary.get('completion_percent', 0),
        'message': f"小朋友已經完成 {summary.get('completed_topics', 0)}/9 個面試主題練習！連續練習 {summary.get('current_streak', 0)} 日！",
        'generated_at': datetime.now().isoformat()
    }
