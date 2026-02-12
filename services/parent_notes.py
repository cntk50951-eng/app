"""
Parent Notes Service - 家长笔记功能
帮助家长记录孩子的练习情况和建议

功能：
- 记录每次练习的观察
- 添加个性化建议
- 查看历史记录
- 练习会话记录
"""

import os
import json
from datetime import datetime

# 笔记存储（开发阶段使用文件，生产环境应该用数据库）
NOTES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'parent_notes.json')
SESSIONS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'practice_sessions.json')

# 默认笔记模板
NOTE_TEMPLATES = {
    'self-introduction': {
        'questions': [
            '小朋友介紹自己時表現得點樣？',
            '有冇邊部分講得特別好？',
            '邊部分需要多啲練習？',
            '小朋友講嘢既音量同速度岩唔岩？',
            '眼神接觸做得好唔好？'
        ],
        'suggestions': [
            '可以對鏡練習，睇吓自己既表情同姿勢',
            '每日練習一次自我介紹，每次 5 分鐘',
            '鼓勵小朋友企直，望住對方眼睛'
        ]
    },
    'interests': {
        'questions': [
            '小朋友點樣描述自己既興趣？',
            '可以唔可以講出具體例子？',
            '講到自己鍾意既嘢時開唔開心？',
            '有冇用到咩形容詞？'
        ],
        'suggestions': [
            '用「因為...所以...」句式',
            '加啲動作或表情去表達',
            '準備多幾個興趣相關既詞彙'
        ]
    },
    'family': {
        'questions': [
            '小朋友識唔識介紹屋企人？',
            '可唔可以講出屋企人既特點？',
            '講到屋企人既時候開唔開心？'
        ],
        'suggestions': [
            '可以影啲家庭相，等小朋友指住嚟講',
            '教「我爸爸/媽咪好鍾意...」呢句式'
        ]
    },
    'observation': {
        'questions': [
            '小朋友有冇睇清楚張圖？',
            '講得出幾多樣野？',
            '描述既次序清唔清楚？',
            '用咗咩詞彙去描述？'
        ],
        'suggestions': [
            '教「由左到右、由上到下」咁睇',
            '玩「搵不同」遊戲訓練觀察力',
            '鼓勵小朋友講多啲細節'
        ]
    },
    'scenarios': {
        'questions': [
            '小朋友識唔識處理呢個情況？',
            '答案合理唔合理？',
            '有冇講出解決方法？'
        ],
        'suggestions': [
            '用角色扮演既方式練習',
            '教「首先...然後...最後...」',
            '睇圖畫書時可以問「如果係你呢？」'
        ]
    }
}


def get_notes_file():
    """获取笔记文件路径."""
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    return NOTES_FILE


def load_notes(user_id):
    """加载用户笔记."""
    try:
        file_path = get_notes_file()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(user_id, {'notes': []})
    except Exception as e:
        print(f"Error loading notes: {e}")
    return {'notes': []}


def save_notes(user_id, notes_data):
    """保存用户笔记."""
    try:
        file_path = get_notes_file()
        
        # 加载现有数据
        all_data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        
        # 更新用户数据
        all_data[user_id] = notes_data
        
        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving notes: {e}")
        return False


def create_note(user_id, topic_id, content, score=None):
    """创建新笔记."""
    notes_data = load_notes(user_id)
    
    note = {
        'id': f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'topic_id': topic_id,
        'content': content,
        'score': score,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    notes_data['notes'].append(note)
    save_notes(user_id, notes_data)
    
    return note


def get_topic_notes(user_id, topic_id):
    """获取某个主题的所有笔记."""
    notes_data = load_notes(user_id)
    
    return [
        note for note in notes_data['notes']
        if note['topic_id'] == topic_id
    ]


def get_latest_notes(user_id, limit=5):
    """获取最新笔记."""
    notes_data = load_notes(user_id)
    
    sorted_notes = sorted(
        notes_data['notes'],
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )
    
    return sorted_notes[:limit]


def delete_note(user_id, note_id):
    """删除笔记."""
    notes_data = load_notes(user_id)
    
    notes_data['notes'] = [
        note for note in notes_data['notes']
        if note['id'] != note_id
    ]
    
    save_notes(user_id, notes_data)
    
    return True


def get_template(topic_id):
    """获取笔记模板."""
    return NOTE_TEMPLATES.get(topic_id, {
        'questions': [
            '練習過程點樣？',
            '邊部分做得好？',
            '邊部分需要改進？'
        ],
        'suggestions': [
            '每日練習 5-10 分鐘',
            '鼓勵小朋友'
        ]
    })


def generate_practice_report(user_id):
    """生成练习报告."""
    notes_data = load_notes(user_id)

    if not notes_data['notes']:
        return None

    # 统计
    topic_counts = {}
    total_notes = len(notes_data['notes'])

    for note in notes_data['notes']:
        topic = note.get('topic_id', 'unknown')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # 计算平均分
    scores = [n.get('score') for n in notes_data['notes'] if n.get('score')]
    avg_score = sum(scores) / len(scores) if scores else None

    return {
        'total_notes': total_notes,
        'topic_breakdown': topic_counts,
        'average_score': round(avg_score, 1) if avg_score else None,
        'last_practice': notes_data['notes'][-1].get('created_at') if notes_data['notes'] else None,
        'topics_covered': list(topic_counts.keys())
    }


# ============ 额外缺失的函数 ============

def get_user_notes(user_id, topic_id=None):
    """获取用户所有笔记，可按主题筛选."""
    notes_data = load_notes(user_id)

    if topic_id:
        return [
            note for note in notes_data['notes']
            if note['topic_id'] == topic_id
        ]

    return notes_data['notes']


def get_notes_stats(user_id):
    """获取笔记统计."""
    notes_data = load_notes(user_id)
    notes = notes_data['notes']

    # 按主题统计
    topic_counts = {}
    total_notes = len(notes)

    for note in notes:
        topic = note.get('topic_id', 'unknown')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # 计算平均分
    scores = [n.get('score') for n in notes if n.get('score')]
    avg_score = sum(scores) / len(scores) if scores else None

    return {
        'total_notes': total_notes,
        'topic_breakdown': topic_counts,
        'average_score': round(avg_score, 1) if avg_score else None,
        'topics_with_notes': list(topic_counts.keys())
    }


def update_note(note_id, content):
    """更新笔记内容."""
    # 遍历所有用户查找笔记
    notes_file = get_notes_file()

    if not os.path.exists(notes_file):
        return None

    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)

        for user_id, data in all_data.items():
            for note in data.get('notes', []):
                if note.get('id') == note_id:
                    note['content'] = content
                    note['updated_at'] = datetime.now().isoformat()

                    with open(notes_file, 'w', encoding='utf-8') as f:
                        json.dump(all_data, f, ensure_ascii=False, indent=2)

                    return note

        return None
    except Exception as e:
        print(f"Error updating note: {e}")
        return None


def get_topic_questions(topic_id):
    """获取指定主题的引导问题."""
    template = get_template(topic_id)
    return template.get('questions', [])


# ============ 练习会话功能 ============

def get_sessions_file():
    """获取会话文件路径."""
    os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
    return SESSIONS_FILE


def load_sessions(user_id):
    """加载用户会话."""
    try:
        file_path = get_sessions_file()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(user_id, {'sessions': []})
    except Exception as e:
        print(f"Error loading sessions: {e}")
    return {'sessions': []}


def save_sessions(user_id, sessions_data):
    """保存用户会话."""
    try:
        file_path = get_sessions_file()

        # 加载现有数据
        all_data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

        # 更新用户数据
        all_data[user_id] = sessions_data

        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"Error saving sessions: {e}")
        return False


def record_practice_session(user_id, topic, duration_seconds, notes=None, rating=None):
    """记录练习会话."""
    sessions_data = load_sessions(user_id)

    session = {
        'id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'topic': topic,
        'duration_seconds': duration_seconds,
        'duration_minutes': round(duration_seconds / 60, 1),
        'notes': notes,
        'rating': rating,
        'created_at': datetime.now().isoformat()
    }

    sessions_data['sessions'].append(session)
    save_sessions(user_id, sessions_data)

    return session


def get_user_sessions(user_id, topic=None, limit=20):
    """获取用户练习会话，可按主题筛选."""
    sessions_data = load_sessions(user_id)
    sessions = sessions_data['sessions']

    if topic:
        sessions = [s for s in sessions if s.get('topic') == topic]

    # 按时间排序
    sorted_sessions = sorted(
        sessions,
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )

    return sorted_sessions[:limit]


def get_session_stats(user_id):
    """获取会话统计."""
    sessions_data = load_sessions(user_id)
    sessions = sessions_data['sessions']

    if not sessions:
        return {
            'total_sessions': 0,
            'total_minutes': 0,
            'average_session_minutes': 0,
            'topics_practiced': []
        }

    # 计算总时长
    total_seconds = sum(s.get('duration_seconds', 0) for s in sessions)
    total_minutes = round(total_seconds / 60, 1)

    # 按主题统计
    topic_counts = {}
    for session in sessions:
        topic = session.get('topic', 'unknown')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # 计算平均会话时长
    avg_minutes = round(total_minutes / len(sessions), 1) if sessions else 0

    return {
        'total_sessions': len(sessions),
        'total_minutes': total_minutes,
        'average_session_minutes': avg_minutes,
        'topics_practiced': list(topic_counts.keys()),
        'topic_breakdown': topic_counts
    }
