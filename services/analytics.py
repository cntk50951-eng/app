"""
Analytics Service - 使用数据追踪
香港升小面試 AI 導師 - 用戶行為追蹤引擎

功能：
- 追蹤關鍵用戶行為事件
- 統計數據聚合
- 支持 Google Analytics / Mixpanel
"""

import os
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict


# ============ 配置 ============

ANALYTICS_ENABLED = os.getenv('ANALYTICS_ENABLED', 'true')
GA_TRACKING_ID = os.getenv('GA_TRACKING_ID', '')
MIXPANEL_TOKEN = os.getenv('MIXPANEL_TOKEN', '')

# 內存存儲（生產環境應使用數據庫）
event_log = []
user_stats = {}


# ============ 事件類型 ============

EVENT_TYPES = {
    'USER_REGISTER': {'category': 'User', 'action': 'Register', 'label': None},
    'USER_LOGIN': {'category': 'User', 'action': 'Login', 'label': None},
    'PROFILE_CREATE': {'category': 'Profile', 'action': 'Create', 'label': None},
    'PROFILE_UPDATE': {'category': 'Profile', 'action': 'Update', 'label': None},
    'LESSON_START': {'category': 'Lesson', 'action': 'Start', 'label': None},
    'LESSON_COMPLETE': {'category': 'Lesson', 'action': 'Complete', 'label': None},
    'CONTENT_GENERATE': {'category': 'Content', 'action': 'Generate', 'label': None},
    'NOTE_CREATE': {'category': 'Notes', 'action': 'Create', 'label': None},
    'AUDIO_PLAY': {'category': 'Audio', 'action': 'Play', 'label': None},
    'IMAGE_VIEW': {'category': 'Image', 'action': 'View', 'label': None},
    'FEEDBACK_SUBMIT': {'category': 'Feedback', 'action': 'Submit', 'label': None},
    'PAYWALL_VIEW': {'category': 'Paywall', 'action': 'View', 'label': None},
    'PAYMENT_START': {'category': 'Payment', 'action': 'Start', 'label': None},
    'PAYMENT_COMPLETE': {'category': 'Payment', 'action': 'Complete', 'label': None},
}


# ============ 核心追蹤函數 ============

def track_event(user_id, event_type, properties=None):
    """
    追蹤用戶事件

    Args:
        user_id: 用戶 ID
        event_type: 事件類型（如 'LESSON_START'）
        properties: 額外屬性（dict）
    """
    if ANALYTICS_ENABLED != 'true':
        return

    event_config = EVENT_TYPES.get(event_type, {})
    timestamp = datetime.now().isoformat()

    event = {
        'user_id': user_id,
        'event_type': event_type,
        'category': event_config.get('category', 'Other'),
        'action': event_config.get('action', event_type),
        'label': properties.get('label') if properties else event_config.get('label'),
        'properties': properties or {},
        'timestamp': timestamp,
        'session_id': get_session_id(user_id),
    }

    # 內存存儲
    event_log.append(event)

    # 更新用戶統計
    update_user_stats(user_id, event_type, properties)

    # 發送到外部服務
    _send_to_ga(event)
    _send_to_mixpanel(event)

    print(f"📊 Tracked event: {event_type} - User: {user_id}")


def get_session_id(user_id):
    """獲取或創建會話 ID"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            'session_id': f"sess_{int(time.time())}",
            'first_seen': datetime.now().isoformat(),
            'total_events': 0,
            'events': []
        }
    return user_stats[user_id]['session_id']


def update_user_stats(user_id, event_type, properties=None):
    """更新用戶統計"""
    properties = properties or {}

    if user_id not in user_stats:
        user_stats[user_id] = {
            'first_seen': datetime.now().isoformat(),
            'last_seen': None,
            'total_events': 0,
            'topics_completed': 0,
            'total_minutes': 0,
            'notes_created': 0,
            'feedback_submitted': 0,
            'events': []
        }

    stats = user_stats[user_id]
    stats['last_seen'] = datetime.now().isoformat()
    stats['total_events'] += 1
    stats['events'].append({
        'type': event_type,
        'timestamp': stats['last_seen'],
        'properties': properties
    })

    # 更新特定計數
    if event_type == 'LESSON_COMPLETE':
        stats['topics_completed'] += 1
        if properties.get('duration_minutes'):
            stats['total_minutes'] += properties['duration_minutes']

    elif event_type == 'NOTE_CREATE':
        stats['notes_created'] += 1

    elif event_type == 'FEEDBACK_SUBMIT':
        stats['feedback_submitted'] += 1


# ============ 外部服務集成 ============

def _send_to_ga(event):
    """發送事件到 Google Analytics"""
    if not GA_TRACKING_ID:
        return

    try:
        # GA4 Measurement Protocol
        import requests

        data = {
            'client_id': str(event['user_id']),
            'events': [{
                'name': event['event_type'].lower(),
                'params': {
                    'category': event['category'],
                    'action': event['action'],
                    'label': event.get('label') or '',
                    'timestamp': event['timestamp']
                }
            }]
        }

        # 實際發送代碼（簡化）
        print(f"📈 GA Event: {event['event_type']}")

    except Exception as e:
        print(f"⚠️ GA tracking error: {e}")


def _send_to_mixpanel(event):
    """發送事件到 Mixpanel"""
    if not MIXPANEL_TOKEN:
        return

    try:
        print(f"📊 Mixpanel Event: {event['event_type']}")
        # 實際發送代碼需要 Mixpanel SDK

    except Exception as e:
        print(f"⚠️ Mixpanel tracking error: {e}")


# ============ 查詢函數 ============

def get_user_analytics(user_id):
    """獲取用戶分析數據"""
    if user_id not in user_stats:
        return {
            'topics_completed': 0,
            'total_minutes': 0,
            'notes_created': 0,
            'feedback_submitted': 0,
            'last_active': None,
            'events_count': 0
        }

    stats = user_stats[user_id]
    return {
        'topics_completed': stats['topics_completed'],
        'total_minutes': stats['total_minutes'],
        'notes_created': stats['notes_created'],
        'feedback_submitted': stats['feedback_submitted'],
        'first_seen': stats['first_seen'],
        'last_active': stats['last_seen'],
        'events_count': stats['total_events']
    }


def get_topic_progress(user_id):
    """獲取主題完成進度"""
    if user_id not in user_stats:
        return {
            'self-introduction': {'completed': False, 'score': None, 'practices': 0},
            'interests': {'completed': False, 'score': None, 'practices': 0},
            'family': {'completed': False, 'score': None, 'practices': 0},
            'observation': {'completed': False, 'score': None, 'practices': 0},
            'scenarios': {'completed': False, 'score': None, 'practices': 0}
        }

    topics = {
        'self-introduction': {'completed': False, 'score': None, 'practices': 0},
        'interests': {'completed': False, 'score': None, 'practices': 0},
        'family': {'completed': False, 'score': None, 'practices': 0},
        'observation': {'completed': False, 'score': None, 'practices': 0},
        'scenarios': {'completed': False, 'score': None, 'practices': 0}
    }

    # 從事件中統計
    for event in user_stats[user_id]['events']:
        if event['type'] == 'LESSON_START':
            topic_id = event['properties'].get('topic_id')
            if topic_id and topic_id in topics:
                topics[topic_id]['practices'] += 1

        elif event['type'] == 'LESSON_COMPLETE':
            topic_id = event['properties'].get('topic_id')
            if topic_id and topic_id in topics:
                topics[topic_id]['completed'] = True
                if event['properties'].get('score'):
                    topics[topic_id]['score'] = event['properties']['score']

    return topics


def get_all_analytics():
    """獲取全局分析數據（管理用）"""
    total_users = len(user_stats)
    total_events = sum(s['total_events'] for s in user_stats.values())
    total_topics = sum(s['topics_completed'] for s in user_stats.values())
    total_minutes = sum(s['total_minutes'] for s in user_stats.values())

    return {
        'total_users': total_users,
        'total_events': total_events,
        'total_topics_completed': total_topics,
        'total_minutes': total_minutes,
        'average_topics_per_user': round(total_topics / total_users, 2) if total_users > 0 else 0,
        'average_minutes_per_user': round(total_minutes / total_users, 2) if total_users > 0 else 0
    }


# ============ 實用工具 ============

def get_retention_rate(days=7):
    """計算留存率"""
    cutoff = datetime.now() - timedelta(days=days)
    active_users = sum(1 for s in user_stats.values() if s['last_seen'] and datetime.fromisoformat(s['last_seen']) > cutoff)
    return round(active_users / len(user_stats) * 100, 2) if user_stats else 0


def export_events(user_id=None):
    """導出事件日誌"""
    if user_id:
        return [e for e in event_log if e['user_id'] == user_id]
    return event_log


def clear_user_data(user_id):
    """清除用戶數據（GDPR 合規）"""
    if user_id in user_stats:
        del user_stats[user_id]

    # 標記事件為已刪除
    for event in event_log:
        if event['user_id'] == user_id:
            event['deleted'] = True

    print(f"🗑️ User data cleared: {user_id}")
