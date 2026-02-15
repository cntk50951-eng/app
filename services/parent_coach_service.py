"""
家长面试教练服务
Parent Interview Coach Service

功能：
- AI示范正确的引导方式（话术、语气、时机）
- 家长实际演练
- AI实时点评家长的引导技巧
- 常见误区知识库
"""

import os
import json
import uuid
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")


# ============ 常见误区知识库 ============


def get_common_mistakes():
    """获取常见误区知识库"""
    return {
        "over_answering": {
            "name": "过度替答",
            "description": "家长直接替孩子回答问题，没有给孩子思考和表达的机会",
            "examples": [
                "老师问：你叫什么名字？家长答：他叫小明，今年6岁...",
                "老师问：你喜欢什么？家长答：他喜欢画画、跳舞、弹钢琴...",
            ],
            "impact": "面试官无法了解孩子的真实能力和表达",
            "suggestion": "让孩子自己回答，家长可以适当补充",
        },
        "over_pressuring": {
            "name": "追问过难",
            "description": "家长在孩子回答后追问过难或过于复杂的问题",
            "examples": [
                "孩子说喜欢画画，家长问：那你介绍一下印象派和后印象派的区别？",
                "孩子说喜欢玩，家长问：那你说说玩游戏的利弊以及如何平衡学习和娱乐？",
            ],
            "impact": "给孩子造成压力，可能导致孩子紧张或回答不上来",
            "suggestion": "追问要符合孩子年龄，循序渐进",
        },
        "negative_feedback": {
            "name": "否定打击",
            "description": "在孩子回答后进行否定或批评",
            "examples": [
                "孩子回答后，家长说：不对不对，你应该这样说...",
                "孩子说错了，家长立刻纠正：你说得不对，是这样的...",
            ],
            "impact": "打击孩子自信心，影响后续表现",
            "suggestion": "先肯定孩子的表现，再温和地引导",
        },
        "interrupting": {
            "name": "打断孩子",
            "description": "在孩子回答过程中过早打断",
            "examples": [
                "孩子才开始说，家长就打断：行了行了，说重点",
                "孩子还没说完，家长就替他说完了",
            ],
            "impact": "打乱孩子思路，显得不尊重孩子",
            "suggestion": "耐心听完孩子的回答，再进行引导",
        },
        "too_many_hints": {
            "name": "提示过多",
            "description": "一次性给出太多提示或答案",
            "examples": [
                "你说是不是那个...就是那个...红色的...苹果...",
                "你想想看嘛，就是我们上次去的那个地方...",
            ],
            "impact": "孩子依赖家长提示，失去独立思考能力",
            "suggestion": "给适当的思考时间，逐步引导",
        },
        "no_feedback": {
            "name": "无反馈",
            "description": "孩子回答后没有任何回应",
            "examples": [
                "孩子说完，家长没有任何表示，直接问下一个问题",
                "孩子回答完，家长沉默不语",
            ],
            "impact": "孩子不知道自己的回答是否正确",
            "suggestion": "及时给予积极反馈，增强孩子信心",
        },
        "rushing": {
            "name": "过于急促",
            "description": "没有给孩子足够的思考时间就催促",
            "examples": ["快点说呀，怎么不说话？", "你到底会不会？快点！"],
            "impact": "孩子因为紧张而更加说不出话",
            "suggestion": "给孩子2-3秒的思考时间，耐心等待",
        },
        "perfect_expectation": {
            "name": "期望过高",
            "description": "期望孩子回答完美，不断要求重说",
            "examples": ["再说一次，这次说得好一点", "你这样不行，重新说，要说得完整"],
            "impact": "给孩子过大压力，可能导致抗拒",
            "suggestion": "肯定孩子的努力，接受不完美的回答",
        },
    }


# ============ 面试题目 ============


def get_coach_questions():
    """获取教练模式的面试题目"""
    return [
        {
            "id": "self_intro",
            "category": "自我介绍",
            "question": "请介绍一下你自己吧",
            "child_level": "基础",
            "ai示范": {
                "话术": "宝贝，老师想知道你叫什么名字呀？你可以告诉老师吗？（微笑眼神鼓励）",
                "时机": "在孩子情绪稳定后开始，保持眼神接触",
                "语气": "温柔、缓慢，给孩子足够的反应时间",
                "要点": "问题简单明确，等孩子回应后再进行下一步",
            },
            "bad_example": "他叫XXX，今年6岁，在XX幼儿园上学...（家长直接替答）",
        },
        {
            "id": "hobbies",
            "category": "兴趣爱好",
            "question": "你有什么兴趣爱好吗？",
            "child_level": "基础",
            "ai示范": {
                "话术": "老师想知道你平时喜欢做什么呀？想一想，告诉我们一件你喜欢的事情好不好？（点头鼓励）",
                "时机": "等孩子思考，不要催促",
                "语气": "好奇、期待，让孩子感受到被倾听",
                "要点": "即使孩子说的简单，也要给予肯定",
            },
            "bad_example": "他喜欢画画，还喜欢唱歌，还会弹钢琴...（一次性说太多）",
        },
        {
            "id": "favorite_book",
            "category": "兴趣爱好",
            "question": "你最喜欢哪本书呀？",
            "child_level": "基础",
            "ai示范": {
                "话术": "呀，你喜欢看书呀，真棒！那你能不能告诉老师，你最喜欢哪本书呢？（身体微微前倾，表示感兴趣）",
                "时机": "先肯定孩子的兴趣，再追问细节",
                "语气": "惊喜、欣赏",
                "要点": "即使孩子说的书很简单，也要尊重孩子的喜好",
            },
            "bad_example": "不对，你应该说《三字经》或者《唐诗三百首》，那些才是好书...（否定孩子的选择）",
        },
        {
            "id": "friends",
            "category": "社交能力",
            "question": "你在学校有好朋友吗？",
            "child_level": "基础",
            "ai示范": {
                "话术": "老师好想知道你在学校有没有好朋友呀？你能告诉老师一个你的好朋友是谁吗？（轻轻歪头）",
                "时机": "在孩子放松后提出，语气轻松",
                "语气": "像聊天一样，不要像审问",
                "要点": "即使孩子说没有，也要平和对待",
            },
            "bad_example": "你怎么回事？怎么没有好朋友？你是不是不合群？（追问过难）",
        },
        {
            "id": "family",
            "category": "家庭背景",
            "question": "家里有谁呀？",
            "child_level": "基础",
            "ai示范": {
                "话术": "老师好想知道你家都有谁呀？你能数给老师听吗？（眼神温和）",
                "时机": "可以让孩子扳着手指数",
                "语气": "轻松愉快",
                "要点": "如果孩子紧张，可以先让孩子放松下来",
            },
            "bad_example": "这么简单的问题都不会？家里几口人还不知道？（否定打击）",
        },
        {
            "id": "future",
            "category": "未来规划",
            "question": "你长大想做什么？",
            "child_level": "中等",
            "ai示范": {
                "话术": "老师好想知道你长大后想做什么呀？有没有什么梦想呢？（眼睛发亮，表示期待）",
                "时机": "在孩子状态好的时候",
                "语气": "充满期待，鼓励孩子大胆说",
                "要点": "不要否定孩子的梦想，即使听起来不切实际",
            },
            "bad_example": "当什么医生老师不好，非要当那个...（否定打击）",
        },
        {
            "id": "problem_solving",
            "category": "解决问题",
            "question": "如果你和好朋友吵架了，你会怎么办？",
            "child_level": "中等",
            "ai示范": {
                "话术": "哎呀，如果有这样的情况肯定很伤心对不对？（先共情）那你觉得可以怎么做呢？（引导思考）",
                "时机": "先表达理解，再引导",
                "语气": "理解、体贴",
                "要点": "不要急于给答案，让孩子自己想",
            },
            "bad_example": "这还用想？肯定是道歉啊！这么简单都不知道？（过于急促）",
        },
        {
            "id": "strengths",
            "category": "自我认知",
            "question": "你觉得自己有什么优点？",
            "child_level": "中等",
            "ai示范": {
                "话术": "老师觉得你好棒呀！（具体举例）那你觉得自己有什么优点呢？（引导孩子发现自己的长处）",
                "时机": "先给孩子一些信心后",
                "语气": "真诚、鼓励",
                "要点": "可以先举例，让孩子更容易回答",
            },
            "bad_example": "你有什么优点？说不出来？每天就知道玩...（否定打击）",
        },
        {
            "id": "handling_difficulty",
            "category": "困难应对",
            "question": "如果你遇到困难了，你会怎么办？",
            "child_level": "中等",
            "ai示范": {
                "话术": "每个人都会遇到困难的时候，这很正常。那你觉得遇到困难时可以找谁帮忙呢？（引导而非直接给答案）",
                "时机": "可以让孩子想想",
                "语气": "平和、不给压力",
                "要点": "强调遇到困难是正常的",
            },
            "bad_example": "这点困难都解决不了？你也太没用了吧！（否定打击）",
        },
        {
            "id": "reading",
            "category": "学习习惯",
            "question": "你平时喜欢看书吗？",
            "child_level": "基础",
            "ai示范": {
                "话术": "哇，喜欢看书的小朋友都很棒！那你能告诉老师你看的是什么书吗？（具体化问题）",
                "时机": "孩子表现出兴趣时深入",
                "语气": "欣赏、好奇",
                "要点": "具体化问题，引导孩子描述",
            },
            "bad_example": "看书？看得懂吗你？（质疑否定）",
        },
    ]


# ============ MiniMax API 调用 ============


def call_minimax_api(endpoint, payload):
    """调用 MiniMax API."""
    if not MINIMAX_API_KEY:
        print("WARNING: MiniMax API Key not configured")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        url = f"{MINIMAX_BASE_URL}/{endpoint}"
        print(f"Calling MiniMax API: {url}")

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"MiniMax API success")
            return response.json()
        else:
            print(f"MiniMax API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"MiniMax API exception: {e}")
        return None


# ============ AI 教练功能 ============


def generate_coach_demo(question_data, child_age=6):
    """
    生成AI示范内容

    Args:
        question_data: 题目数据
        child_age: 孩子年龄

    Returns:
        dict: 示范内容
    """
    question = question_data.get("question", "")
    category = question_data.get("category", "")

    system_prompt = """你是一位专业的幼升小面试教练，专门指导家长如何正确地引导孩子回答面试问题。
你的任务是生成一个完美的示范，展示正确的引导方式。
    
请从以下几个方面进行示范：
1. 话术：具体应该怎么说
2. 时机：什么时候说
3. 语气：用什么语气
4. 要点：关键注意事项
    
请用简洁、易懂的中文表达，方便家长学习。"""

    user_prompt = f"""题目：{question}
分类：{category}
孩子年龄：{child_age}岁

请生成一个正确的引导示范，包括：
1. 具体的引导话术（家长应该说的话）
2. 合适的时机
3. 适当的语气
4. 关键要点

请用JSON格式返回：
{{
    "话术": "...",
    "时机": "...",
    "语气": "...",
    "要点": "..."
}}"""

    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and "choices" in result:
        try:
            content = result["choices"][0]["message"]["content"]
            # 尝试解析JSON
            import re

            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Error parsing AI response: {e}")

    # 如果API失败，返回默认内容
    return question_data.get(
        "ai示范",
        {
            "话术": "宝贝，老师想知道...",
            "时机": "在孩子情绪稳定后",
            "语气": "温柔、缓慢",
            "要点": "问题简单明确",
        },
    )


def evaluate_parent_coaching(parent_words, question_data):
    """
    评估家长的引导表现

    Args:
        parent_words: 家长说的话
        question_data: 题目数据

    Returns:
        dict: 评估结果
    """
    question = question_data.get("question", "")
    category = question_data.get("category", "")

    system_prompt = """你是一位专业的幼升小面试教练，专门评估家长在引导孩子回答面试问题时的表现。

你需要评估家长在以下方面的表现：
1. 话术是否合适
2. 是否有过度替答
3. 是否有追问过难
4. 是否有否定打击
5. 是否打断孩子
6. 是否给了过多提示
7. 是否有反馈
8. 是否过于急促
9. 期望是否合理

请给出具体的评估和改进建议。"""

    user_prompt = f"""面试题目：{question}
分类：{category}

家长的引导语：
{parent_words}

请从以下几个方面进行评估：
1. 优点（做得好的是什么）
2. 问题（有什么问题需要注意）
3. 建议（具体如何改进）

请用中文回答，保持专业、友善的语气。"""

    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and "choices" in result:
        content = result["choices"][0]["message"]["content"]

        # 简单解析评估结果
        evaluation = {"feedback": content, "score": calculate_basic_score(parent_words)}

        # 检测常见误区
        mistakes = detect_mistakes(parent_words)
        evaluation["detected_mistakes"] = mistakes

        return evaluation

    # 如果API失败，使用基础评估
    return {
        "feedback": "感谢您的练习！建议继续学习正确的引导技巧。",
        "score": calculate_basic_score(parent_words),
        "detected_mistakes": detect_mistakes(parent_words),
    }


def calculate_basic_score(parent_words):
    """基础评分"""
    score = 70  # 基础分

    # 检查是否有否定词
    negative_words = [
        "不对",
        "不对不对",
        "错了",
        "不行",
        "不会",
        "你怎么",
        "太笨了",
        "没用",
    ]
    if any(word in parent_words for word in negative_words):
        score -= 15

    # 检查是否有催促
    hurry_words = ["快点", "快说", "赶紧", "快点说", "怎么不说话"]
    if any(word in parent_words for word in hurry_words):
        score -= 10

    # 检查是否有替答（过长）
    if len(parent_words) > 50 and "他" in parent_words or "她" in parent_words:
        score -= 15

    # 检查是否有鼓励
    good_words = ["真棒", "很好", "不错", "可以的", "没关系", "想一下"]
    if any(word in parent_words for word in good_words):
        score += 10

    return max(0, min(100, score))


def detect_mistakes(parent_words):
    """检测常见误区"""
    mistakes = []

    # 过度替答
    if len(parent_words) > 80:
        if "他叫" in parent_words or "她叫" in parent_words:
            mistakes.append(
                {
                    "type": "over_answering",
                    "name": "过度替答",
                    "suggestion": "让孩子自己回答，家长可以适当补充",
                }
            )

    # 否定打击
    negative_words = [
        ("不对", "不要直接否定孩子的回答"),
        ("错了", "不要直接说孩子错了"),
        ("不行", "不要否定孩子的能力"),
        ("你怎么", "不要用质疑的语气问孩子"),
        ("太笨了", "不要用负面评价"),
        ("没用", "不要否定孩子"),
    ]
    for word, suggestion in negative_words:
        if word in parent_words:
            mistakes.append(
                {
                    "type": "negative_feedback",
                    "name": "否定打击",
                    "suggestion": suggestion,
                }
            )
            break

    # 追问过难
    complex_words = ["为什么", "什么意思", "分析", "解释", "说说看为什么"]
    if any(word in parent_words for word in complex_words):
        if len(parent_words) < 30:  # 问题太短
            mistakes.append(
                {
                    "type": "over_pressuring",
                    "name": "追问过难",
                    "suggestion": "追问要符合孩子年龄，循序渐进",
                }
            )

    # 催促
    hurry_words = ["快点", "快说", "赶紧", "怎么不说话", "说呀"]
    if any(word in parent_words for word in hurry_words):
        mistakes.append(
            {
                "type": "rushing",
                "name": "过于急促",
                "suggestion": "给孩子2-3秒的思考时间，耐心等待",
            }
        )

    # 提示过多
    hint_words = ["是不是", "那个", "就是", "你想想"]
    if parent_words.count("?") == 0 and len(parent_words) > 30:
        if any(word in parent_words for word in hint_words):
            mistakes.append(
                {
                    "type": "too_many_hints",
                    "name": "提示过多",
                    "suggestion": "给适当的思考时间，逐步引导",
                }
            )

    return mistakes


# ============ 教练会话管理 ============


class ParentCoachSession:
    """家长教练会话管理"""

    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id, question_id=None):
        """创建新的教练会话"""
        session_id = str(uuid.uuid4())

        # 获取题目列表
        questions = get_coach_questions()

        # 如果指定了题目，使用指定题目
        selected_question = None
        if question_id:
            for q in questions:
                if q["id"] == question_id:
                    selected_question = q
                    break

        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "questions": questions,
            "selected_question": selected_question or questions[0],
            "current_step": "intro",  # intro -> demo -> practice -> feedback
            "practice_recordings": [],
            "created_at": datetime.now().isoformat(),
            "status": "in_progress",
        }

        return self.sessions[session_id]

    def get_session(self, session_id):
        """获取会话"""
        return self.sessions.get(session_id)

    def update_step(self, session_id, step):
        """更新当前步骤"""
        session = self.sessions.get(session_id)
        if session:
            session["current_step"] = step
        return session

    def record_practice(self, session_id, parent_words):
        """记录练习内容"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # 评估表现
        question_data = session["selected_question"]
        evaluation = evaluate_parent_coaching(parent_words, question_data)

        practice_record = {
            "parent_words": parent_words,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat(),
        }

        session["practice_recordings"].append(practice_record)

        return practice_record

    def finish_session(self, session_id):
        """完成会话"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        session["status"] = "completed"
        session["finished_at"] = datetime.now().isoformat()

        # 计算平均分
        if session["practice_recordings"]:
            scores = [
                r["evaluation"].get("score", 0) for r in session["practice_recordings"]
            ]
            session["avg_score"] = sum(scores) / len(scores)

        return session

    def get_all_sessions(self, user_id=None):
        """获取所有会话"""
        if user_id:
            return [s for s in self.sessions.values() if s.get("user_id") == user_id]
        return list(self.sessions.values())


# 全局会话管理
parent_coach_session = ParentCoachSession()


# ============ 获取数据 ============


def get_question_by_id(question_id):
    """根据ID获取题目"""
    questions = get_coach_questions()
    for q in questions:
        if q["id"] == question_id:
            return q
    return None


def get_all_categories():
    """获取所有分类"""
    questions = get_coach_questions()
    categories = {}
    for q in questions:
        cat = q.get("category", "其他")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)
    return categories


def get_mistakes_summary():
    """获取误区总结"""
    mistakes = get_common_mistakes()
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "examples": v["examples"][:2],
            "suggestion": v["suggestion"],
        }
        for k, v in mistakes.items()
    ]
