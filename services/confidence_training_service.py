"""
面霸心理训练营服务
提供面试场景情绪管理模块：
- 放松呼吸训练
- 积极心理暗示
- 模拟压力测试
- 考前心理准备动画课程
- AI情绪识别与调节建议
"""

import json
import random
from datetime import datetime
from services.ai_generator import call_minimax_api, generate_text_content


# 放松呼吸训练内容
BREATHING_EXERCISES = [
    {
        "id": "breathing_1",
        "name": "4-7-8 放松呼吸",
        "description": "吸气4秒，屏住呼吸7秒，呼气8秒",
        "steps": [
            {"action": "吸气", "duration": 4, "instruction": "用鼻子慢慢吸气，数到4"},
            {"action": "屏住", "duration": 7, "instruction": "保持呼吸，数到7"},
            {"action": "呼气", "duration": 8, "instruction": "用嘴巴慢慢呼气，数到8"},
        ],
        "cycles": 3,
        "emoji": "🌬️",
        "color": "#4FC3F7",
    },
    {
        "id": "breathing_2",
        "name": "深海放松法",
        "description": "像小鱼一样慢慢呼吸",
        "steps": [
            {
                "action": "吸气",
                "duration": 3,
                "instruction": "想象自己是一条小鱼，慢慢吸水",
            },
            {"action": "呼气", "duration": 4, "instruction": "慢慢吐出气泡，放松身体"},
        ],
        "cycles": 5,
        "emoji": "🐟",
        "color": "#4DD0E1",
    },
    {
        "id": "breathing_3",
        "name": "波浪呼吸",
        "description": "像海浪一样起伏",
        "steps": [
            {"action": "吸气", "duration": 3, "instruction": "海浪涌上来，慢慢吸气"},
            {"action": "呼气", "duration": 3, "instruction": "海浪退下去，慢慢呼气"},
        ],
        "cycles": 6,
        "emoji": "🌊",
        "color": "#29B6F6",
    },
    {
        "id": "breathing_4",
        "name": "气球呼吸",
        "description": "把紧张变成气球飞走",
        "steps": [
            {"action": "吸气", "duration": 3, "instruction": "想象吹气球，慢慢吸气"},
            {"action": "呼气", "duration": 4, "instruction": "放开气球，让紧张飞走"},
        ],
        "cycles": 4,
        "emoji": "🎈",
        "color": "#FFB74D",
    },
]


# 积极心理暗示语料库
POSITIVE_AFFIRMATIONS = [
    "我是最棒的小朋友！",
    "我准备得很充分，一定可以的！",
    "面试就像认识新朋友一样轻松！",
    "我的答案很棒，老师会喜欢我的！",
    "紧张是因为我在乎，我会把它变成动力！",
    "我有许多优点，今天要展示出来！",
    "无论结果如何，我都是最独特的！",
    "我相信自己可以的！",
    "每一次练习都让我更进步！",
    "我的笑容是最美的！",
]


# 模拟压力测试场景
PRESSURE_TEST_SCENARIOS = [
    {
        "level": 1,
        "title": "轻松开场",
        "scenario": "面试官对你微笑点头",
        "questions": [
            "你好呀，能介绍一下自己吗？",
            "你最喜欢什么玩具呀？",
        ],
        "pressure_tips": "保持微笑，正常回答就好",
    },
    {
        "level": 2,
        "title": "稍微紧张",
        "scenario": "面试官表情变得严肃",
        "questions": [
            "如果你和同学吵架了，你会怎么办？",
            "你最不擅长的事情是什么？",
        ],
        "pressure_tips": "深呼吸，诚实回答即可",
    },
    {
        "level": 3,
        "title": "压力考验",
        "scenario": "面试官连续提问，不给思考时间",
        "questions": [
            "如果老师批评你了，你会怎么想？",
            "你觉得你有什么需要改进的地方？",
        ],
        "pressure_tips": "快速思考，如实回答，不要慌张",
    },
    {
        "level": 4,
        "title": "高压场景",
        "scenario": "面试官说：你这个问题回答得不太好",
        "questions": [
            "那你可以重新回答一下吗？",
            "你确定这是最好的答案吗？",
        ],
        "pressure_tips": "保持冷静，尝试给出更好的答案",
    },
    {
        "level": 5,
        "title": "终极挑战",
        "scenario": "面试官看起来不太满意",
        "questions": [
            "我觉得你可能不太适合我们学校。",
            "你有信心说服我吗？",
        ],
        "pressure_tips": "展现自信，说明自己的优势",
    },
]


# 考前心理准备动画课程
ANIMATION_COURSES = [
    {
        "id": "course_1",
        "title": "面试紧张怎么办？",
        "title_en": "What to Do When Nervous",
        "duration": 180,
        "description": "教孩子认识紧张情绪，学会放松技巧",
        "emoji": "🧘",
        "color": "#7E57C2",
        "sections": [
            {
                "title": "认识紧张",
                "content": "紧张是正常的生理反应，说明你在乎这次面试",
            },
            {"title": "放松技巧", "content": "深呼吸、放松肌肉、给自己积极暗示"},
            {"title": "实战演练", "content": "跟着视频做放松练习"},
        ],
    },
    {
        "id": "course_2",
        "title": "自信满满的技巧",
        "title_en": "Confidence Building",
        "duration": 180,
        "description": "建立自信心的实用方法",
        "emoji": "💪",
        "color": "#FF7043",
        "sections": [
            {"title": "自信姿势", "content": "站立挺直、抬头看人、保持微笑"},
            {"title": "积极自我暗示", "content": "每天对自己说我可以"},
            {"title": "成功回忆", "content": "想想以前做过的成功的事情"},
        ],
    },
    {
        "id": "course_3",
        "title": "应对意外情况",
        "title_en": "Handling Surprises",
        "duration": 150,
        "description": "遇到意外情况如何保持冷静",
        "emoji": "🎯",
        "color": "#26A69A",
        "sections": [
            {"title": "意外很正常", "content": "面试中可能会遇到各种意外"},
            {"title": "保持冷静", "content": "深呼吸，思考解决方案"},
            {"title": "求助礼貌", "content": "可以说：请问可以再说一次吗？"},
        ],
    },
    {
        "id": "course_4",
        "title": "面试当天心理准备",
        "title_en": "Interview Day Prep",
        "duration": 200,
        "description": "面试当天的心理调适方法",
        "emoji": "📅",
        "color": "#42A5F5",
        "sections": [
            {"title": "早上准备", "content": "吃好早餐、穿好衣服、保持好心情"},
            {"title": "路上放松", "content": "听喜欢的音乐、想象成功场景"},
            {"title": "考场门口", "content": "深呼吸、给自己一个大大的微笑"},
        ],
    },
]


# 情绪识别关键词
EMOTION_KEYWORDS = {
    "紧张": ["紧张", "害怕", "怕", "担心", "慌", "不敢", "发抖", "心跳"],
    "自信": ["可以", "没问题", "有信心", "准备好了", "不怕"],
    "沮丧": ["不会", "不行", "做不好", "笨", "不想"],
    "平静": ["放松", "不紧张", "还好", "平静", "淡定"],
    "兴奋": ["开心", "期待", "高兴", "兴奋", "太好了"],
}


def get_breathing_exercises():
    """获取所有呼吸训练列表"""
    return {
        "success": True,
        "data": [
            {
                "id": ex["id"],
                "name": ex["name"],
                "description": ex["description"],
                "emoji": ex["emoji"],
                "color": ex["color"],
            }
            for ex in BREATHING_EXERCISES
        ],
    }


def get_breathing_exercise_detail(exercise_id):
    """获取呼吸训练详细内容"""
    for ex in BREATHING_EXERCISES:
        if ex["id"] == exercise_id:
            return {"success": True, "data": ex}
    return {"success": False, "error": "Exercise not found"}


def get_random_affirmation():
    """获取随机积极心理暗示"""
    affirmation = random.choice(POSITIVE_AFFIRMATIONS)
    return {"success": True, "data": {"affirmation": affirmation}}


async def generate_personalized_affirmation(user_context=None):
    """
    使用AI生成个性化心理暗示
    """
    system_prompt = """你是一位专为小朋友设计的心理鼓励师，专门帮助孩子建立面试信心。

要求：
- 生成简短（20字以内）、充满正能量的心理暗示
- 语言要简单易懂，适合小学生
- 要有力量感，能增强自信
- 可以使用一些可爱的emoji
- 用普通话"""

    user_prompt = f"""请为面试的孩子生成一句鼓励的话。如果知道孩子的特点：{user_context or "请根据一般情况生成"}"""

    try:
        result = generate_text_content(system_prompt, user_prompt)
        if result and "raw_content" in result:
            affirmation = result["raw_content"].strip()
        elif result:
            affirmation = result.get(
                "response", result.get("content", random.choice(POSITIVE_AFFIRMATIONS))
            )
        else:
            affirmation = random.choice(POSITIVE_AFFIRMATIONS)

        return {"success": True, "data": {"affirmation": affirmation}}
    except Exception as e:
        print(f"Error generating personalized affirmation: {e}")
        return {
            "success": True,
            "data": {"affirmation": random.choice(POSITIVE_AFFIRMATIONS)},
        }


def get_pressure_test_levels():
    """获取压力测试所有级别"""
    return {
        "success": True,
        "data": [
            {
                "level": s["level"],
                "title": s["title"],
                "scenario": s["scenario"],
                "pressure_tips": s["pressure_tips"],
            }
            for s in PRESSURE_TEST_SCENARIOS
        ],
    }


def get_pressure_test_scenario(level):
    """获取特定级别的压力测试场景"""
    for s in PRESSURE_TEST_SCENARIOS:
        if s["level"] == level:
            return {"success": True, "data": s}
    return {"success": False, "error": "Level not found"}


def get_animation_courses():
    """获取所有心理准备动画课程"""
    return {
        "success": True,
        "data": [
            {
                "id": c["id"],
                "title": c["title"],
                "title_en": c["title_en"],
                "duration": c["duration"],
                "description": c["description"],
                "emoji": c["emoji"],
                "color": c["color"],
            }
            for c in ANIMATION_COURSES
        ],
    }


def get_animation_course_detail(course_id):
    """获取动画课程详细内容"""
    for c in ANIMATION_COURSES:
        if c["id"] == course_id:
            return {"success": True, "data": c}
    return {"success": False, "error": "Course not found"}


def analyze_emotion(user_message):
    """
    分析用户消息中的情绪
    返回情绪类型和调节建议
    """
    message_lower = user_message.lower()

    # 检测情绪
    detected_emotions = []
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                detected_emotions.append(emotion)
                break

    if not detected_emotions:
        detected_emotions = ["平静"]

    # 生成调节建议
    advice = _get_advice_for_emotion(detected_emotions)

    return {
        "success": True,
        "data": {
            "detected_emotions": detected_emotions,
            "primary_emotion": detected_emotions[0],
            "advice": advice,
        },
    }


def _get_advice_for_emotion(emotions):
    """根据情绪类型获取调节建议"""
    advice_map = {
        "紧张": [
            "来，我们一起做深呼吸：吸气...呼气...",
            "紧张是正常的，试着放松肩膀，深呼吸",
            "你可以的！先停下来，深深吸一口气",
        ],
        "自信": [
            "太棒了！保持这种状态！",
            "很好！把你的信心传递给面试官",
        ],
        "沮丧": [
            "别灰心，你已经很棒了！",
            "每个人都会遇到困难，这很正常",
            "想想你以前做成功的那些事",
        ],
        "平静": [
            "继续保持这种放松的状态",
            "很好，你已经很平静了",
        ],
        "兴奋": [
            "兴奋是好的，但也要保持冷静哦",
            "把兴奋转化为面试的动力吧",
        ],
    }

    all_advice = []
    for emotion in emotions:
        if emotion in advice_map:
            all_advice.extend(advice_map[emotion])

    if all_advice:
        return random.choice(all_advice)
    return "保持放松，相信自己，你是最棒的！"


async def analyze_answer_emotion(answer_text, question_text=None):
    """
    使用AI分析答题时的情绪状态并给出调节建议
    """
    system_prompt = """你是一位儿童心理分析师，专门分析小朋友在面试答题时的情绪状态。

分析内容：
1. 判断情绪状态（紧张/自信/平静/不确定等）
2. 给出调节建议

输出格式（JSON）：
{
    "emotion": "紧张/自信/平静/不确定",
    "confidence_score": 0-100,
    "analysis": "简短分析",
    "suggestions": ["建议1", "建议2"]
}

注意：
- 分析要温和，鼓励为主
- 建议要简单实用，适合孩子理解"""

    user_prompt = f"""小朋友的回答：{answer_text}
问题：{question_text or "未提供"}
请分析这个小朋友答题时的情绪状态。"""

    try:
        result = generate_text_content(system_prompt, user_prompt)
        if result and "raw_content" in result:
            content = result["raw_content"]
            # 尝试解析JSON
            try:
                data = json.loads(content)
                return {"success": True, "data": data}
            except:
                pass

        # 如果解析失败，使用基础分析
        return analyze_emotion(answer_text)
    except Exception as e:
        print(f"Error analyzing answer emotion: {e}")
        return analyze_emotion(answer_text)


def get_confidence_training_summary():
    """获取心理训练营内容摘要"""
    return {
        "success": True,
        "data": {
            "breathing_exercises_count": len(BREATHING_EXERCISES),
            "affirmations_count": len(POSITIVE_AFFIRMATIONS),
            "pressure_test_levels": len(PRESSURE_TEST_SCENARIOS),
            "animation_courses_count": len(ANIMATION_COURSES),
        },
    }
