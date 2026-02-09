"""
Progress Tracker Service - 进度追踪服务
"""

import json
from datetime import datetime, timedelta

PROGRESS_FILE = "/Users/yuki/.openclaw/workspace/data/progress.json"

def load_progress(user_id):
    """加载用户进度."""
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(user_id, {'topics': {}})
    except:
        return {'topics': {}}

def save_progress(user_id, progress):
    """保存用户进度."""
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    
    data[user_id] = progress
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_topic_progress(user_id, topic_id, action='practice', score=None):
    """更新主题进度."""
    progress = load_progress(user_id)
    
    if topic_id not in progress['topics']:
        progress['topics'][topic_id] = {
            'practice_count': 0,
            'complete_count': 0,
            'scores': [],
            'last_practiced': None,
            'first_practiced': None
        }
    
    topic = progress['topics'][topic_id]
    
    if action == 'practice':
        topic['practice_count'] += 1
        topic['last_practiced'] = datetime.now().isoformat()
        if not topic.get('first_practiced'):
            topic['first_practiced'] = datetime.now().isoformat()
        if score:
            topic['scores'].append(score)
    
    if action == 'complete':
        topic['complete_count'] += 1
    
    save_progress(user_id, progress)
    
    return progress

def get_topic_stats(user_id, topic_id):
    """获取主题统计."""
    progress = load_progress(user_id)
    
    if topic_id not in progress['topics']:
        return None
    
    topic = progress['topics'][topic_id]
    scores = topic.get('scores', [])
    
    return {
        'practice_count': topic['practice_count'],
        'complete_count': topic['complete_count'],
        'average_score': sum(scores) / len(scores) if scores else None,
        'last_practiced': topic.get('last_practiced'),
        'first_practiced': topic.get('first_practiced')
    }

def get_overall_stats(user_id):
    """获取整体统计."""
    progress = load_progress(user_id)
    
    total_practice = 0
    total_complete = 0
    all_scores = []
    
    for topic_id, topic in progress['topics'].items():
        total_practice += topic['practice_count']
        total_complete += topic['complete_count']
        all_scores.extend(topic.get('scores', []))
    
    # 计算连续天数
    streak = calculate_streak(progress)
    
    return {
        'total_practice': total_practice,
        'total_complete': total_complete,
        'average_score': sum(all_scores) / len(all_scores) if all_scores else None,
        'streak_days': streak,
        'topics_covered': len(progress['topics']),
        'last_active': max([
            topic.get('last_practiced') 
            for topic in progress['topics'].values() 
            if topic.get('last_practiced')
        ]) if progress['topics'] else None
    }

def calculate_streak(progress):
    """计算连续天数."""
    if not progress['topics']:
        return 0
    
    # 简化的连续计算
    return 1
