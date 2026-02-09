"""
AI Suggestions Service - AI 建议生成
"""

from datetime import datetime
import random

SUGGESTIONS = {
    'self-introduction': [
        '今日可以練習「你好，我叫...」呢句嘢',
        '鼓勵小朋友望住鏡頭練習',
        '可以加多啲關於自己既嘢，例如「我最鍾意...」'
    ],
    'interests': [
        '準備多啲關於興趣既詞彙',
        '用「因為...所以...」呢個句式',
        '可以講吓學到咩嘢'
    ],
    'family': [
        '指住家庭相片練習',
        '教「我屋企有...」呢個句式',
        '可以講吓屋企人鍾意做咩'
    ],
    'observation': [
        '玩「搵不同」遊戲',
        '由左到右、由上到下咁睇',
        '數吓圖入面有幾多人/嘢'
    ],
    'scenarios': [
        '用角色扮演既方式練習',
        '教「如果...我可以...」呢個句式',
        '鼓勵小朋友講多啲'
    ]
}

DAILY_TIPS = [
    '今日記得同小朋友練習5分鐘面試！',
    '鼓勵小朋友望住對方眼睛。',
    '講嘢要大聲、清楚。',
    '可以對住鏡頭練習自我介紹。',
    '用「因為...所以...」呢個句式。',
    '練習完要讚一讚小朋友！',
    '每日進步一小步！'
]

def get_suggestions(topic_id, progress_data=None):
    """获取建议."""
    suggestions = SUGGESTIONS.get(topic_id, [
        '今日練習咗未？',
        '記得對住鏡頭講嘢',
        '大聲啲、清楚啲'
    ])
    
    practice_count = progress_data.get('practice_count', 0) if progress_data else 0
    
    if practice_count < 3:
        return suggestions[:2]
    elif practice_count < 10:
        return suggestions[1:3]
    else:
        return suggestions

def generate_daily_tip():
    """生成每日提示."""
    return random.choice(DAILY_TIPS)
