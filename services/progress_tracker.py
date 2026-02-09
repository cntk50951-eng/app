"""
Progress Tracker Service - 进度追踪服务
"""

import json
from datetime import datetime, timedelta
import os

PROGRESS_DIR = "/Users/yuki/.openclaw/workspace/data"
PROGRESS_FILE = f"{PROGRESS_DIR}/progress.json"

def load_progress(user_id):
    """加载用户进度."""
    os.makedirs(PROGRESS_DIR, exist_ok=True)
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(str(user_id), {'topics': {}, 'stats': {}})
    except (FileNotFoundError, json.JSONDecodeError):
        return {'topics': {}, 'stats': {}}

def save_progress(user_id, progress):
    """保存用户进度."""
    os.makedirs(PROGRESS_DIR, exist_ok=True)
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    data[str(user_id)] = progress
    
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
            topic['scores'].append(int(score))
    
    if action == 'complete':
        topic['complete_count'] += 1
    
    # 更新统计
    total_practice = sum(t['practice_count'] for t in progress['topics'].values())
    all_scores = []
    for t in progress['topics'].values():
        all_scores.extend(t.get('scores', []))
    
    progress['stats'] = {
        'total_practice': total_practice,
        'total_complete': sum(t['complete_count'] for t in progress['topics'].values()),
        'average_score': sum(all_scores) / len(all_scores) if all_scores else 0,
        'topics_count': len(progress['topics']),
        'last_updated': datetime.now().isoformat()
    }
    
    save_progress(user_id, progress)
    return progress

def get_topic_stats(user_id, topic_id):
    """获取主题统计."""
    progress = load_progress(user_id)
    return progress['topics'].get(topic_id, {})

def get_overall_stats(user_id):
    """获取整体统计."""
    progress = load_progress(user_id)
    return progress.get('stats', {})
