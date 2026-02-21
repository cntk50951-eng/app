"""
Parent-Child Challenge Service - 亲子共面挑战服务
香港升小面试 AI 导师 - 亲子协作面试功能

功能：
- 创建亲子挑战任务
- 记录双方答案
- AI 对比分析生成默契度评分
- 家长版答案优化建议
- 亲子 PK 榜单
- 合作勋章体系
"""

import os
import json
import time
import random
import uuid
from datetime import datetime, timedelta
import requests
from db.database import execute_query, get_connection


# ============ 配置 ============

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")


# ============ 默契度等级配置 ============

CHEMISTRY_LEVELS = {
    "bronze": {
        "min": 0,
        "max": 59,
        "name": "铜牌",
        "name_en": "Bronze",
        "color": "#CD7F32",
    },
    "silver": {
        "min": 60,
        "max": 74,
        "name": "银牌",
        "name_en": "Silver",
        "color": "#C0C0C0",
    },
    "gold": {
        "min": 75,
        "max": 89,
        "name": "金牌",
        "name_en": "Gold",
        "color": "#FFD700",
    },
    "diamond": {
        "min": 90,
        "max": 100,
        "name": "钻石",
        "name_en": "Diamond",
        "color": "#B9F2FF",
    },
}


# ============ 挑战类型配置 ============

CHALLENGE_TYPES = {
    "self_introduction": {
        "id": "self_introduction",
        "name": "自我介绍",
        "name_en": "Self Introduction",
        "icon": "👤",
        "description": "家长和孩子分别介绍自己",
        "question_template": "请介绍一下你自己",
    },
    "family": {
        "id": "family",
        "name": "家庭介绍",
        "name_en": "Family",
        "icon": "👨‍👩‍👧",
        "description": "描述家庭成员和家庭活动",
        "question_template": "介绍一下你的家庭",
    },
    "interests": {
        "id": "interests",
        "name": "兴趣爱好",
        "name_en": "Interests",
        "icon": "⭐",
        "description": "分享各自的兴趣爱好",
        "question_template": "你平时喜欢做什么？",
    },
    "dreams": {
        "id": "dreams",
        "name": "梦想未来",
        "name_en": "Dreams",
        "icon": "🌟",
        "description": "谈谈未来的梦想和期望",
        "question_template": "你长大后想做什么？",
    },
    "values": {
        "id": "values",
        "name": "价值观",
        "name_en": "Values",
        "icon": "💡",
        "description": "讨论重要的价值观和品格",
        "question_template": "你觉得什么品质最重要？",
    },
}


# ============ MiniMax API 调用 ============


def call_minimax_api(endpoint, payload):
    """调用 MiniMax API."""
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API Key not configured")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        url = f"{MINIMAX_BASE_URL}/{endpoint}"
        print(f"📡 Calling MiniMax API: {url}")

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"✅ MiniMax API success")
            return response.json()
        else:
            print(f"❌ MiniMax API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ MiniMax API exception: {e}")
        return None


# ============ 挑战管理功能 ============


def create_challenge(user_id, child_name, challenge_type, question=None):
    """创建新的亲子挑战任务"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 获取挑战类型信息
            challenge_info = CHALLENGE_TYPES.get(challenge_type, {})
            if not question:
                question = challenge_info.get("question_template", "请回答这个问题")

            # 创建挑战记录
            cursor.execute(
                """
                INSERT INTO parent_child_challenges 
                (user_id, child_name, challenge_type, question, status)
                VALUES (%s, %s, %s, %s, 'in_progress')
                RETURNING id, user_id, child_name, challenge_type, question, status, started_at;
                """,
                (user_id, child_name, challenge_type, question),
            )

            result = cursor.fetchone()
            conn.commit()

            return dict(result) if result else None

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating challenge: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_challenge(challenge_id):
    """获取挑战详情"""
    query = """
        SELECT * FROM parent_child_challenges WHERE id = %s;
    """
    result = execute_query(query, (challenge_id,), fetch=True)
    return dict(result[0]) if result else None


def get_user_challenges(user_id, limit=20, status=None):
    """获取用户的挑战列表"""
    if status:
        query = """
            SELECT * FROM parent_child_challenges 
            WHERE user_id = %s AND status = %s
            ORDER BY started_at DESC
            LIMIT %s;
        """
        result = execute_query(query, (user_id, status, limit), fetch=True)
    else:
        query = """
            SELECT * FROM parent_child_challenges 
            WHERE user_id = %s
            ORDER BY started_at DESC
            LIMIT %s;
        """
        result = execute_query(query, (user_id, limit), fetch=True)

    return [dict(row) for row in result] if result else []


def update_challenge_answer(challenge_id, user_type, answer, audio_url=None):
    """更新挑战答案（家长或孩子）"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            if user_type == "parent":
                cursor.execute(
                    """
                    UPDATE parent_child_challenges 
                    SET parent_answer = %s, 
                        parent_answer_audio_url = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *;
                    """,
                    (answer, audio_url, challenge_id),
                )
            else:  # child
                cursor.execute(
                    """
                    UPDATE parent_child_challenges 
                    SET child_answer = %s, 
                        child_answer_audio_url = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *;
                    """,
                    (answer, audio_url, challenge_id),
                )

            result = cursor.fetchone()
            conn.commit()
            return dict(result) if result else None

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating challenge answer: {e}")
        raise
    finally:
        if conn:
            conn.close()


def complete_challenge(challenge_id):
    """完成挑战并触发 AI 评分"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE parent_child_challenges 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *;
                """,
                (challenge_id,),
            )

            result = cursor.fetchone()
            conn.commit()
            return dict(result) if result else None

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error completing challenge: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ============ AI 评分分析功能 ============


def analyze_chemistry(parent_answer, child_answer, challenge_type, question):
    """
    使用 MiniMax API 分析亲子答案的默契度

    返回：
    - chemistry_score: 总体默契度分数 (0-100)
    - similarity_score: 答案相似度
    - cooperation_score: 协作度
    - communication_score: 沟通质量
    - creativity_score: 创意表现
    - ai_analysis: AI 对比分析文本
    - parent_feedback: 家长优化建议
    - strengths: 优势列表
    - improvements: 改进建议列表
    """

    prompt = f"""
你是一位专业的教育心理学家和亲子关系专家。请分析以下亲子对话答案的默契度。

**挑战类型**: {CHALLENGE_TYPES.get(challenge_type, {}).get("name", challenge_type)}
**问题**: {question}

**家长的回答**:
{parent_answer}

**孩子的回答**:
{child_answer}

请从以下维度进行分析和评分（每个维度 0-100 分）：
1. 相似度 (similarity_score): 两人回答的主题、观点是否一致
2. 协作度 (cooperation_score): 是否体现出良好的协作和配合
3. 沟通质量 (communication_score): 表达是否清晰，是否有情感交流
4. 创意表现 (creativity_score): 回答是否有创意和想象力

然后计算总体默契度分数 (chemistry_score)，并生成：
- 详细的对比分析（100-200 字）
- 给家长的优化建议（50-100 字）
- 3 个优势点
- 3 个改进建议

请以 JSON 格式返回，格式如下：
{{
    "similarity_score": 85,
    "cooperation_score": 90,
    "communication_score": 88,
    "creativity_score": 82,
    "chemistry_score": 86,
    "ai_analysis": "详细分析文本...",
    "parent_feedback": "给家长的建议...",
    "strengths": ["优势 1", "优势 2", "优势 3"],
    "improvements": ["改进建议 1", "改进建议 2", "改进建议 3"]
}}
"""

    payload = {
        "model": "MiniMax-Text-01",
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的教育心理学家和亲子关系专家，擅长分析亲子互动和提供教育建议。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
    }

    result = call_minimax_api("text/chatcompletion_v2", payload)

    if result and "choices" in result and len(result["choices"]) > 0:
        response_text = result["choices"][0]["message"]["content"]

        # 尝试解析 JSON 响应
        try:
            # 清理响应文本，提取 JSON 部分
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            analysis = json.loads(json_str)

            return {
                "similarity_score": float(analysis.get("similarity_score", 0)),
                "cooperation_score": float(analysis.get("cooperation_score", 0)),
                "communication_score": float(analysis.get("communication_score", 0)),
                "creativity_score": float(analysis.get("creativity_score", 0)),
                "chemistry_score": float(analysis.get("chemistry_score", 0)),
                "ai_analysis": analysis.get("ai_analysis", ""),
                "parent_feedback": analysis.get("parent_feedback", ""),
                "strengths": analysis.get("strengths", []),
                "improvements": analysis.get("improvements", []),
            }
        except Exception as e:
            print(f"Error parsing AI analysis: {e}")
            # 返回默认分析结果
            return generate_default_analysis(parent_answer, child_answer)

    return generate_default_analysis(parent_answer, child_answer)


def generate_default_analysis(parent_answer, child_answer):
    """生成默认分析结果（当 AI 分析失败时）"""
    # 简单的基于规则的分析
    similarity = calculate_text_similarity(parent_answer, child_answer)

    chemistry_score = min(100, max(0, similarity + random.randint(-10, 10)))

    return {
        "similarity_score": float(similarity),
        "cooperation_score": float(min(100, similarity + 10)),
        "communication_score": float(min(100, similarity + 5)),
        "creativity_score": float(min(100, similarity - 5)),
        "chemistry_score": float(chemistry_score),
        "ai_analysis": f"家长和孩子都给出了有意义的回答。相似度为{similarity}%。",
        "parent_feedback": "继续鼓励孩子表达自己的想法，多进行类似的亲子对话练习。",
        "strengths": ["积极互动", "表达清晰", "情感交流"],
        "improvements": ["增加细节描述", "更多创意表达", "加强情感连接"],
    }


def calculate_text_similarity(text1, text2):
    """简单的文本相似度计算（基于共同词汇）"""
    if not text1 or not text2:
        return 0

    # 分词（简单按字符分割）
    words1 = set(text1)
    words2 = set(text2)

    # 计算 Jaccard 相似度
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    if union == 0:
        return 0

    similarity = (intersection / union) * 100
    return min(100, max(0, similarity))


def save_challenge_score(challenge_id, user_id, analysis_result):
    """保存挑战评分结果"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 确定默契度等级
            chemistry_score = analysis_result.get("chemistry_score", 0)
            chemistry_level = get_chemistry_level(chemistry_score)

            # 插入评分记录
            cursor.execute(
                """
                INSERT INTO challenge_scores 
                (challenge_id, user_id, chemistry_score, chemistry_level,
                 similarity_score, cooperation_score, communication_score, creativity_score,
                 ai_analysis, parent_feedback, strengths, improvements)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    challenge_id,
                    user_id,
                    chemistry_score,
                    chemistry_level,
                    analysis_result.get("similarity_score", 0),
                    analysis_result.get("cooperation_score", 0),
                    analysis_result.get("communication_score", 0),
                    analysis_result.get("creativity_score", 0),
                    analysis_result.get("ai_analysis", ""),
                    analysis_result.get("parent_feedback", ""),
                    json.dumps(analysis_result.get("strengths", [])),
                    json.dumps(analysis_result.get("improvements", [])),
                ),
            )

            score_id = cursor.fetchone()[0]

            # 检查并授予勋章
            badges_earned = check_and_award_badges(
                user_id, challenge_id, chemistry_score
            )
            if badges_earned:
                cursor.execute(
                    """
                    UPDATE challenge_scores 
                    SET badges_earned = %s
                    WHERE id = %s;
                    """,
                    (json.dumps(badges_earned), score_id),
                )

            conn.commit()

            return {"score_id": score_id, "badges_earned": badges_earned}

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error saving challenge score: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_chemistry_level(score):
    """根据分数获取默契度等级"""
    for level, config in CHEMISTRY_LEVELS.items():
        if config["min"] <= score <= config["max"]:
            return level
    return "bronze"


# ============ 勋章系统功能 ============


def check_and_award_badges(user_id, challenge_id, chemistry_score):
    """检查并授予勋章"""
    badges_earned = []

    try:
        # 获取用户已完成的挑战数
        query = """
            SELECT COUNT(*) as count FROM parent_child_challenges 
            WHERE user_id = %s AND status = 'completed';
        """
        result = execute_query(query, (user_id,), fetch=True)
        completed_count = result[0]["count"] if result else 0

        # 检查勋章条件
        # 1. 第一次合作
        if completed_count == 1:
            badge = award_badge(user_id, "first_teamwork", challenge_id)
            if badge:
                badges_earned.append(badge)

        # 2. 协作小能手（完成 5 次）
        if completed_count == 5:
            badge = award_badge(user_id, "team_player", challenge_id)
            if badge:
                badges_earned.append(badge)

        # 3. 默契度达到 90 分以上
        if chemistry_score >= 90:
            badge = award_badge(user_id, "perfect_partnership", challenge_id)
            if badge:
                badges_earned.append(badge)

        # 4. 沟通小达人（沟通维度 80+）
        if chemistry_score >= 80:
            badge = award_badge(user_id, "good_communicator", challenge_id)
            if badge:
                badges_earned.append(badge)

        return badges_earned

    except Exception as e:
        print(f"Error checking badges: {e}")
        return []


def award_badge(user_id, badge_id, challenge_id=None):
    """授予用户勋章"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 检查是否已获得
            cursor.execute(
                """
                SELECT * FROM user_challenge_badges 
                WHERE user_id = %s AND badge_id = %s;
                """,
                (user_id, badge_id),
            )

            if cursor.fetchone():
                return None  # 已获得

            # 获取勋章信息
            cursor.execute(
                """
                SELECT * FROM challenge_badges WHERE id = %s;
                """,
                (badge_id,),
            )

            badge_info = cursor.fetchone()
            if not badge_info:
                return None

            # 插入勋章记录
            cursor.execute(
                """
                INSERT INTO user_challenge_badges 
                (user_id, badge_id, challenge_id)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (user_id, badge_id, challenge_id),
            )

            conn.commit()

            return {
                "id": badge_id,
                "name_zh": badge_info["name_zh"],
                "name_en": badge_info.get("name_en", ""),
                "icon_emoji": badge_info.get("icon_emoji", "⭐"),
            }

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error awarding badge: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_user_badges(user_id):
    """获取用户所有勋章"""
    query = """
        SELECT ucb.*, cb.name_zh, cb.name_en, cb.icon_emoji, cb.description, cb.category, cb.rarity
        FROM user_challenge_badges ucb
        JOIN challenge_badges cb ON ucb.badge_id = cb.id
        WHERE ucb.user_id = %s
        ORDER BY ucb.earned_at DESC;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return [dict(row) for row in result] if result else []


# ============ 排行榜功能 ============


def get_leaderboard(period_type="all_time", limit=50):
    """获取排行榜"""
    if period_type == "weekly":
        # 周排名
        query = """
            SELECT * FROM challenge_leaderboard 
            WHERE period_type = 'weekly' 
              AND period_start >= DATE_TRUNC('week', CURRENT_DATE)
            ORDER BY average_chemistry_score DESC, rank_points DESC
            LIMIT %s;
        """
    elif period_type == "monthly":
        # 月排名
        query = """
            SELECT * FROM challenge_leaderboard 
            WHERE period_type = 'monthly' 
              AND period_start >= DATE_TRUNC('month', CURRENT_DATE)
            ORDER BY average_chemistry_score DESC, rank_points DESC
            LIMIT %s;
        """
    else:
        # 总排名
        query = """
            SELECT * FROM challenge_leaderboard 
            WHERE period_type = 'all_time'
            ORDER BY average_chemistry_score DESC, rank_points DESC
            LIMIT %s;
        """

    result = execute_query(query, (limit,), fetch=True)
    return [dict(row) for row in result] if result else []


def get_user_rank(user_id):
    """获取用户排名信息"""
    query = """
        SELECT * FROM challenge_leaderboard 
        WHERE user_id = %s AND period_type = 'all_time';
    """
    result = execute_query(query, (user_id,), fetch=True)
    return dict(result[0]) if result else None


# ============ 统计功能 ============


def get_challenge_stats(user_id):
    """获取用户挑战统计"""
    query = """
        SELECT 
            COUNT(*) as total_challenges,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_challenges,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_challenges
        FROM parent_child_challenges
        WHERE user_id = %s;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return dict(result[0]) if result else None


def get_challenge_score_history(user_id, limit=10):
    """获取用户评分历史"""
    query = """
        SELECT cs.*, pcc.challenge_type, pcc.question, pcc.child_name
        FROM challenge_scores cs
        JOIN parent_child_challenges pcc ON cs.challenge_id = pcc.id
        WHERE cs.user_id = %s
        ORDER BY cs.created_at DESC
        LIMIT %s;
    """
    result = execute_query(query, (user_id, limit), fetch=True)
    return [dict(row) for row in result] if result else []
