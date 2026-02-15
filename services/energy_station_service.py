"""
面试能量站服务
提供心理建设系统的核心功能：
- 面试心理微课
- AI心理陪伴导师
- 考前能量包
- 家长心理课
"""

import json
import random
from datetime import datetime, date
from services.ai_generator import call_minimax_api, generate_text_content


# 面试心理微课内容库
PSYCHOLOGY_MICRO_LESSONS = [
    {
        "id": "meeting_stranger",
        "title": "如何面對陌生人",
        "title_en": "Meeting Strangers",
        "description": "教孩子如何自信地與陌生人交流",
        "duration": 180,
        "difficulty": "easy",
        "emoji": "👋",
        "color": "#4CAF50",
        "content": {
            "intro": "小朋友，面試的時候你會見到很多陌生的老師和考官",
            "main_points": [
                "保持微笑是最好的见面礼",
                "主动问好显示礼貌",
                "眼神交流很重要",
                "站姿端正有自信",
            ],
            "practice": "对着镜子练习微笑和问好",
            "encouragement": "记住：陌生人也可以成为新朋友！",
        },
    },
    {
        "id": "handling_nervous",
        "title": "緊張時怎麼辦",
        "title_en": "What to Do When Nervous",
        "description": "教孩子缓解面试紧张情绪的技巧",
        "duration": 180,
        "difficulty": "easy",
        "emoji": "🧘",
        "color": "#2196F3",
        "content": {
            "intro": "緊張是正常的，我們一起來學會控制它",
            "main_points": [
                "深呼吸：吸氣...呼氣...重複3次",
                "握緊拳頭再放鬆，重複幾次",
                "在心裡說：我可以的！",
                "想像自己是最棒的小朋友",
            ],
            "practice": "每天練習深呼吸3分鐘",
            "encouragement": "緊張是因為你在乎，做到最好就行！",
        },
    },
    {
        "id": "interview_manners",
        "title": "面試禮貌用語",
        "title_en": "Interview Manners",
        "description": "学习面试中常用的礼貌表达",
        "duration": 180,
        "difficulty": "easy",
        "emoji": "🙇",
        "color": "#9C27B0",
        "content": {
            "intro": "有禮貌的小朋友人人喜歡",
            "main_points": [
                "見面要說：老師好！",
                "回答問題要說：謝謝老師！",
                "需要幫助要說：請問...謝謝",
                "離開要說：老師再見！",
            ],
            "practice": "和家人模擬見面問好",
            "encouragement": "一句簡單的問好，給人好印象！",
        },
    },
    {
        "id": "listening_attention",
        "title": "認真傾聽的技巧",
        "title_en": "Listening Skills",
        "description": "培养面试中认真倾听的能力",
        "duration": 180,
        "difficulty": "medium",
        "emoji": "👂",
        "color": "#FF9800",
        "content": {
            "intro": "會聽問題才能回答好問題",
            "main_points": [
                "眼睛看著說話的人",
                "身體稍微向前傾",
                "不要中途打斷",
                "聽完再思考怎麼回答",
            ],
            "practice": "和家人玩答非所問的遊戲",
            "encouragement": "認真聆聽的寶貝最可愛！",
        },
    },
    {
        "id": "self_intro",
        "title": "自我介紹的藝術",
        "title_en": "The Art of Self Introduction",
        "description": "如何做一个出色的自我介绍",
        "duration": 180,
        "difficulty": "medium",
        "emoji": "📢",
        "color": "#E91E63",
        "content": {
            "intro": "自我介紹是面試的必考題",
            "main_points": [
                "先說名字和年齡",
                "說說自己的愛好",
                "介紹家庭成員",
                "表現自己的優點",
            ],
            "practice": "對著鏡子練習1分鐘自我介紹",
            "encouragement": "你是獨一無二的，勇敢展示自己！",
        },
    },
    {
        "id": "positive_thinking",
        "title": "正向思考的力量",
        "title_en": "Power of Positive Thinking",
        "description": "培养积极乐观的心态",
        "duration": 180,
        "difficulty": "medium",
        "emoji": "🌟",
        "color": "#FFC107",
        "content": {
            "intro": "正向思考讓你更自信",
            "main_points": [
                "我雖然年紀小，但我很棒！",
                "答錯了也沒關係，學習就好",
                "每個人都有優點",
                "相信自己一定能做到",
            ],
            "practice": "每天對著鏡子說：我很棒！",
            "encouragement": "你的笑容是最美的陽光！",
        },
    },
]


# 考前能量包内容
PRE_INTERVIEW_ENERGY_PACKS = [
    {
        "id": "morning_energy_1",
        "title": "今日能量包 - 自信滿滿",
        "type": "morning",
        "message": "親愛的小朋友，今天是面試的大日子！記住，你是最棒的！深呼吸，帶著笑容去迎接挑戰吧！",
        "action": "對著鏡子說：我準備好了！我一定行！",
        "emoji": "💪",
    },
    {
        "id": "morning_energy_2",
        "title": "今日能量包 - 勇氣十足",
        "type": "morning",
        "message": "面試就像打怪獸一樣，只要勇氣足夠，就能戰勝它！記住：勇敢的孩子運氣最好！",
        "action": "做一個你最喜歡的動作，給自己加滿能量！",
        "emoji": "🦸",
    },
    {
        "id": "morning_energy_3",
        "title": "今日能量包 - 放鬆心情",
        "type": "morning",
        "message": "面試只是一次特别的见面会，就像认识新朋友一样。保持轻松的心情，展现最真实的自己！",
        "action": "深呼吸3次，輕輕鬆鬆去面試！",
        "emoji": "🌈",
    },
]


# AI心理陪伴导师角色
COMPANION_PERSONAS = {
    "dinosaur": {
        "name": "小勇士",
        "emoji": "🦖",
        "personality": "勇敢、活潑、充滿正能量",
        "greetings": [
            "嗨！我是小勇士！今天有什麼心事想跟我說嗎？",
            "你好呀！看到你我好開心！",
            "哇！是誰來了？原來是我的好朋友！",
        ],
    },
    "rabbit": {
        "name": "小乖乖",
        "emoji": "🐰",
        "personality": "溫柔、貼心、善解人意",
        "greetings": [
            "嗨！我是小乖乖，有什麼心事可以告訴我哦～",
            "你好呀！看起來你有些心事，願意跟我說說嗎？",
            "嘿！我的好朋友來了！",
        ],
    },
    "bear": {
        "name": "小棕熊",
        "emoji": "🐻",
        "personality": "穩重、可靠、給人安全感",
        "greetings": [
            "你好！我是小棕熊，有什麼煩惱可以跟我說！",
            "嗨！看到你我很開心，有什麼需要幫忙的嗎？",
            "嘿！我的好朋友來了！",
        ],
    },
}


# 家长心理课内容
PARENT_PSYCHOLOGY_LESSONS = [
    {
        "id": "parent_lesson_1",
        "title": "如何幫孩子減壓",
        "description": "家長如何幫助孩子在面試前緩解壓力",
        "emoji": "🧘",
        "content": {
            "points": [
                "保持平常心，不要給孩子過多壓力",
                "多鼓勵、少批評，建立孩子自信心",
                "模擬面試時，給予正面反饋",
                "保證充足睡眠和營養",
                "傾聽孩子的擔心，給予理解和支持",
            ],
            "practices": [
                "每天花10分鐘和孩子聊天，了解他們的想法",
                "創造輕鬆的家庭氛圍",
                "避免在孩子面前討論升學壓力",
            ],
        },
    },
    {
        "id": "parent_lesson_2",
        "title": "家庭模擬面試技巧",
        "description": "如何在家進行有效的模擬面試",
        "emoji": "🏠",
        "content": {
            "points": [
                "營造輕鬆愉快的氛圍",
                "問題要由淺入深",
                "給孩子充分的準備時間",
                "扮演不同類型的面試官",
                "每次練習後給予具體表揚",
            ],
            "practices": ["每天練習5-10分鐘", "用遊戲的方式進行", "讓孩子主導部分對話"],
        },
    },
    {
        "id": "parent_lesson_3",
        "title": "面試當天注意事項",
        "description": "面試當天家長必須知道的事項",
        "emoji": "📅",
        "content": {
            "points": [
                "提前規劃路線，預留充足時間",
                "穿著得體，給孩子樹立榜樣",
                "保持冷靜，不要把焦慮傳染給孩子",
                "給孩子一個擁抱，說相信你",
                "不要在考場外過度叮囑",
            ],
            "practices": [
                "前一晚準備好所有物品",
                "設定合理的期望",
                "給孩子積極的心理暗示",
            ],
        },
    },
    {
        "id": "parent_lesson_4",
        "title": "如何面對面試結果",
        "description": "無論結果如何，家長應該如何應對",
        "emoji": "🤝",
        "content": {
            "points": [
                "無論結果如何都表揚孩子的努力",
                "如果失敗，幫助孩子正確看待",
                "不要把情緒寫在臉上",
                "給孩子一個溫暖的擁抱",
                "做好下一步規劃",
            ],
            "practices": [
                "告訴努力孩子：過就不後悔",
                "一起回顧面試過程中的優點",
                "為孩子創造更多練習機會",
            ],
        },
    },
]


def get_micro_lessons():
    """获取所有面试心理微课"""
    return {
        "success": True,
        "data": [
            {
                "id": lesson["id"],
                "title": lesson["title"],
                "title_en": lesson["title_en"],
                "description": lesson["description"],
                "duration": lesson["duration"],
                "difficulty": lesson["difficulty"],
                "emoji": lesson["emoji"],
                "color": lesson["color"],
            }
            for lesson in PSYCHOLOGY_MICRO_LESSONS
        ],
    }


def get_micro_lesson_detail(lesson_id):
    """获取微课详细内容"""
    for lesson in PSYCHOLOGY_MICRO_LESSONS:
        if lesson["id"] == lesson_id:
            return {"success": True, "data": lesson}
    return {"success": False, "error": "Lesson not found"}


def get_pre_interview_energy_pack():
    """获取考前能量包（随机）"""
    pack = random.choice(PRE_INTERVIEW_ENERGY_PACKS)
    return {"success": True, "data": pack}


def get_parent_lessons():
    """获取家长心理课列表"""
    return {
        "success": True,
        "data": [
            {
                "id": lesson["id"],
                "title": lesson["title"],
                "description": lesson["description"],
                "emoji": lesson["emoji"],
            }
            for lesson in PARENT_PSYCHOLOGY_LESSONS
        ],
    }


def get_parent_lesson_detail(lesson_id):
    """获取家长心理课详细内容"""
    for lesson in PARENT_PSYCHOLOGY_LESSONS:
        if lesson["id"] == lesson_id:
            return {"success": True, "data": lesson}
    return {"success": False, "error": "Lesson not found"}


def get_companion_persona(character_type="dinosaur"):
    """获取AI心理陪伴导师角色信息"""
    """"""
    persona = COMPANION_PERSONAS.get(character_type, COMPANION_PERSONAS["dinosaur"])
    greeting = random.choice(persona["greetings"])
    return {
        "success": True,
        "data": {
            "character_type": character_type,
            "name": persona["name"],
            "emoji": persona["emoji"],
            "personality": persona["personality"],
            "greeting": greeting,
        },
    }


async def get_ai_companion_response(
    user_message, character_type="dinosaur", conversation_history=None
):
    """
    获取AI心理陪伴导师的回复
    使用MiniMax API生成个性化回复
    """
    persona = COMPANION_PERSONAS.get(character_type, COMPANION_PERSONAS["dinosaur"])

    system_prompt = f"""你是一位專為小朋友設計的AI心理陪伴導師，名叫{persona["name"]}（{persona["emoji"]}）。
你的特點是：{persona["personality"]}

主要任務：
1. 傾聽孩子的煩惱和擔心
2. 用溫暖、正面的方式回應
3. 幫助孩子克服面試前的緊張
4. 給予勇氣和鼓勵
5. 可以和孩子玩角色扮演模擬面試

說話風格：
- 使用簡單、友善的語言
- 適當使用表情符號
- 保持積極樂觀的態度
- 像朋友一樣傾聽，不要說教
- 每次回應要短小精悍，适合孩子理解

千萬記住：
- 不要批評孩子
- 不要給予過大壓力
- 永遠支持、鼓勵孩子
- 如果孩子說很緊張，要教他們深呼吸等放鬆技巧"""

    user_prompt = f"""
孩子對你說：{user_message}

請用溫暖、鼓勵的方式回應孩子。回應要簡短（50-100字），充滿正能量。
"""

    try:
        result = generate_text_content(system_prompt, user_prompt)
        if result and "raw_content" in result:
            response = result["raw_content"]
        elif result:
            response = result.get(
                "response", result.get("content", "記住，你是最棒的！加油！")
            )
        else:
            response = _get_fallback_response(user_message)

        return {"success": True, "data": {"response": response}}
    except Exception as e:
        print(f"Error getting AI companion response: {e}")
        return {
            "success": True,
            "data": {"response": _get_fallback_response(user_message)},
        }


def _get_fallback_response(user_message):
    """当API调用失败时，返回预设的回复"""
    message_lower = user_message.lower()

    if "緊張" in message_lower or "怕" in message_lower:
        return "我理解你的心情！緊張是正常的。來，我們一起深呼吸：吸氣...呼氣...重複3次。現在感覺好多了嗎？記住，你是最棒的！💪"
    elif "怕" in message_lower or "不敢" in message_lower:
        return "勇敢的小朋友！其實面試一點都不可怕，就像認識新朋友一樣。記住：勇氣是戰勝恐懼最好的法寶！🌟"
    elif "不會" in message_lower or "不懂" in message_lower:
        return "不會沒關係呀！每個人都是從不會到會的。重要的是你有努力的心，這才是最棒的！👍"
    elif "練習" in message_lower:
        return "練習讓我們更棒！讓我們一起練習吧。你可以先介紹自己：你好，我叫...然後說說你的愛好。繼續加油！🎯"
    elif "累" in message_lower or "辛苦" in message_lower:
        return (
            "你辛苦了！記得要多休息，吃飽飽的人才有力氣。休息好了，我們再一起加油！💤"
        )
    else:
        responses = [
            "我明白！你是最棒的！加油！🌟",
            "听到你这么说，我好想给你一个大大的拥抱！记住，你很棒！💖",
            "没关系，慢慢来，我相信你一定可以的！💪",
            "你是最独特的孩子，有着属于自己的光芒！✨",
        ]
        return random.choice(responses)


def get_all_content_summary():
    """获取能量站所有内容摘要"""
    return {
        "success": True,
        "data": {
            "micro_lessons_count": len(PSYCHOLOGY_MICRO_LESSONS),
            "parent_lessons_count": len(PARENT_PSYCHOLOGY_LESSONS),
            "energy_packs_count": len(PRE_INTERVIEW_ENERGY_PACKS),
            "companion_types": list(COMPANION_PERSONAS.keys()),
        },
    }
