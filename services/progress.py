"""
Progress Service - 進度追蹤管理
香港升小面試 AI 導師 - 用戶學習進度追蹤

功能：
- 管理每個主題的完成狀態
- 追蹤練習次數和得分
- 提供進度統計
"""

import os
import json
from datetime import datetime


# ============ 配置 ============

# 存儲路徑（使用文件系統，簡化 POC）
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PROGRESS_FILE = os.path.join(DATA_DIR, 'progress.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ============ 主題配置 ============

TOPICS = {
    'self-introduction': {
        'id': 'self-introduction',
        'title': '自我介紹',
        'icon': 'person',
        'order': 1,
        'description': '學習自信地介紹自己的特點'
    },
    'interests': {
        'id': 'interests',
        'title': '興趣愛好',
        'icon': 'star',
        'order': 2,
        'description': '深入探討興趣細節'
    },
    'family': {
        'id': 'family',
        'title': '家庭介紹',
        'icon': 'group',
        'order': 3,
        'description': '家庭成員與關係'
    },
    'observation': {
        'id': 'observation',
        'title': '觀察力訓練',
        'icon': 'visibility',
        'order': 4,
        'description': '圖片描述與細節觀察'
    },
    'scenarios': {
        'id': 'scenarios',
        'title': '處境題',
        'icon': 'psychology',
        'order': 5,
        'description': '簡單情境處理'
    }
}


# ============ 數據管理 ============

def _load_progress():
    """加載進度數據"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading progress: {e}")
    return {}


def _save_progress(data):
    """保存進度數據"""
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving progress: {e}")


# ============ 核心功能 ============

def get_user_progress(user_id):
    """獲取用戶完整進度"""
    data = _load_progress()
    user_data = data.get(str(user_id), {})

    # 初始化用戶數據結構
    if not user_data:
        user_data = {
            'created_at': datetime.now().isoformat(),
            'topics': {}
        }

    # 確保所有主題都存在
    for topic_id, topic_config in TOPICS.items():
        if topic_id not in user_data['topics']:
            user_data['topics'][topic_id] = {
                'completed': False,
                'practices': 0,
                'last_practiced': None,
                'best_score': None,
                'time_spent_seconds': 0
            }

    return user_data


def update_progress(user_id, topic_id, action, data=None):
    """
    更新用戶進度

    Args:
        user_id: 用戶 ID
        topic_id: 主題 ID
        action: 動作（'start', 'practice', 'complete', 'score'）
        data: 額外數據（duration, score 等）
    """
    data = data or {}

    user_progress = get_user_progress(user_id)
    topic_data = user_progress['topics'].get(topic_id)

    if not topic_data:
        return None

    timestamp = datetime.now().isoformat()

    if action == 'start':
        # 開始練習
        topic_data['last_practiced'] = timestamp
        topic_data['practices'] += 1

    elif action == 'complete':
        # 完成練習
        topic_data['completed'] = True
        if data.get('duration_seconds'):
            topic_data['time_spent_seconds'] += data['duration_seconds']

    elif action == 'score':
        # 更新分數
        if data.get('score') and (not topic_data['best_score'] or data['score'] > topic_data['best_score']):
            topic_data['best_score'] = data['score']

    # 保存
    data = _load_progress()
    if str(user_id) not in data:
        data[str(user_id)] = user_progress

    data[str(user_id)] = user_progress
    _save_progress(data)

    return topic_data


def mark_topic_complete(user_id, topic_id, score=None, duration_seconds=None):
    """標記主題完成"""
    data = {}
    if score:
        data['score'] = score
    if duration_seconds:
        data['duration_seconds'] = duration_seconds

    return update_progress(user_id, topic_id, 'complete', data)


def get_topic_summary(user_id, topic_id):
    """獲取主題摘要"""
    progress = get_user_progress(user_id)
    topic_data = progress['topics'].get(topic_id, {})
    topic_config = TOPICS.get(topic_id, {})

    return {
        'id': topic_id,
        'title': topic_config.get('title', topic_id),
        'icon': topic_config.get('icon', 'category'),
        'completed': topic_data.get('completed', False),
        'practices': topic_data.get('practices', 0),
        'last_practiced': topic_data.get('last_practiced'),
        'best_score': topic_data.get('best_score'),
        'time_spent_minutes': round(topic_data.get('time_spent_seconds', 0) / 60, 1)
    }


def get_all_topic_summaries(user_id):
    """獲取所有主題摘要"""
    progress = get_user_progress(user_id)

    summaries = []
    for topic_id, topic_config in TOPICS.items():
        topic_data = progress['topics'].get(topic_id, {})

        summaries.append({
            'id': topic_id,
            'title': topic_config.get('title', topic_id),
            'icon': topic_config.get('icon', 'category'),
            'description': topic_config.get('description', ''),
            'completed': topic_data.get('completed', False),
            'practices': topic_data.get('practices', 0),
            'best_score': topic_data.get('best_score'),
            'progress_percent': _calculate_topic_progress(topic_data),
            'order': topic_config.get('order', 0)
        })

    # 按 order 排序
    summaries.sort(key=lambda x: x['order'])

    return summaries


def _calculate_topic_progress(topic_data):
    """計算主題完成百分比"""
    if topic_data.get('completed'):
        return 100

    practices = topic_data.get('practices', 0)
    if practices >= 3:
        return 75
    elif practices >= 2:
        return 50
    elif practices >= 1:
        return 25
    return 0


# ============ 統計功能 ============

def get_overall_stats(user_id):
    """獲取整體統計"""
    progress = get_user_progress(user_id)
    topics = progress['topics']

    completed = sum(1 for t in topics.values() if t.get('completed', False))
    total_practices = sum(t.get('practices', 0) for t in topics.values())
    total_time = sum(t.get('time_spent_seconds', 0) for t in topics.values())

    # 計算連續天數
    streak_days = _calculate_streak(user_id)

    return {
        'total_topics': len(TOPICS),
        'completed_topics': completed,
        'completion_percent': round(completed / len(TOPICS) * 100, 1) if TOPICS else 0,
        'total_practices': total_practices,
        'total_minutes': round(total_time / 60, 1),
        'streak_days': streak_days,
        'first_practice_date': progress.get('created_at'),
        'last_active': _get_last_active(user_id)
    }


def _calculate_streak(user_id):
    """計算連續練習天數"""
    # 簡化版本：返回假設值
    progress = get_user_progress(user_id)
    last_date = _get_last_active(user_id)

    if not last_date:
        return 0

    from datetime import datetime
    last_active = datetime.fromisoformat(last_date)
    today = datetime.now()

    if (today - last_active).days > 1:
        return 0

    return 1  # 簡化處理


def _get_last_active(user_id):
    """獲取最後活躍時間"""
    progress = get_user_progress(user_id)
    topics = progress['topics']

    last_dates = [t.get('last_practiced') for t in topics.values() if t.get('last_practiced')]
    return max(last_dates) if last_dates else None


def get_recommendations(user_id):
    """獲取下一步建議"""
    progress = get_user_progress(user_id)
    recommendations = []

    for topic_id, topic_config in TOPICS.items():
        topic_data = progress['topics'].get(topic_id, {})

        if not topic_data.get('completed'):
            if topic_data.get('practices', 0) == 0:
                recommendations.append({
                    'topic_id': topic_id,
                    'title': topic_config.get('title'),
                    'message': '呢個主題仲未開始，係時候試吓啦！',
                    'priority': 'high'
                })
            elif topic_data.get('practices', 0) < 3:
                recommendations.append({
                    'topic_id': topic_id,
                    'title': topic_config.get('title'),
                    'message': '再多練習幾次，就可以完成呢個主題！',
                    'priority': 'medium'
                })

    # 按 priority 排序
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 2))

    return recommendations[:3]


# ============ 重置功能 ============

def reset_user_progress(user_id):
    """重置用戶進度（慎用）"""
    data = _load_progress()

    if str(user_id) in data:
        del data[str(user_id)]
        _save_progress(data)
        print(f"🔄 Progress reset for user: {user_id}")
        return True

    return False


def generate_progress_report(user_id):
    """生成進度報告"""
    stats = get_overall_stats(user_id)
    topics = get_all_topic_summaries(user_id)
    recommendations = get_recommendations(user_id)

    return {
        'generated_at': datetime.now().isoformat(),
        'summary': stats,
        'topics': topics,
        'recommendations': recommendations
    }
