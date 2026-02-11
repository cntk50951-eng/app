"""
Gamification Service - 成就和徽章系统
"""

from datetime import datetime

BADGES = {
    'first_practice': {'name': '🌟 首次練習', 'description': '完成第一次練習', 'icon': '⭐'},
    'streak_3': {'name': '🔥 連續3日', 'description': '連續練習3日', 'icon': '🔥'},
    'streak_7': {'name': '💪 連續7日', 'description': '連續練習7日', 'icon': '💪'},
    'complete_all': {'name': '🎉 全部完成', 'description': '完成所有主題', 'icon': '🎉'},
    'perfect_score': {'name': '🌈 完美分數', 'description': '獲得5分評價', 'icon': '🌈'}
}

def check_badges(progress_data):
    """检查获得的新徽章."""
    earned = []
    stats = progress_data.get('stats', {})
    
    if stats.get('total_practice', 0) >= 1:
        earned.append('first_practice')
    if stats.get('streak_days', 0) >= 3:
        earned.append('streak_3')
    if stats.get('streak_days', 0) >= 7:
        earned.append('streak_7')
    
    return list(set(earned))

def get_badge_info(badge_id):
    return BADGES.get(badge_id, {'name': 'Unknown', 'description': '', 'icon': '❓'})
