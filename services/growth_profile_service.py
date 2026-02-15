"""
Growth Profile Service - 面霸成长档案服务
整合多维度数据，生成面试能力成长追踪和作品集PDF
"""

import os
import json
import random
from datetime import datetime, timedelta
from services.capability_radar_service import (
    analyze_capabilities,
    get_radar_chart_data,
    CAPABILITY_DIMENSIONS,
    SCHOOL_EXPECTATIONS,
)
from services.progress import get_user_progress, get_overall_stats
from services.analytics import get_user_analytics
from services.practice_data_service import get_user_stats, get_category_progress


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GROWTH_FILE = os.path.join(DATA_DIR, "growth_profiles.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def _load_growth_data():
    """加载成长档案数据"""
    if os.path.exists(GROWTH_FILE):
        try:
            with open(GROWTH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading growth data: {e}")
    return {}


def _save_growth_data(data):
    """保存成长档案数据"""
    try:
        with open(GROWTH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving growth data: {e}")


def get_growth_profile(user_id, profile_data=None):
    """
    获取用户成长档案

    Args:
        user_id: 用户ID
        profile_data: 孩子画像数据（可选）

    Returns:
        dict: 成长档案数据
    """
    user_id_str = str(user_id)
    growth_data = _load_growth_data()

    # 获取基础数据
    progress = get_user_progress(user_id)
    stats = get_overall_stats(user_id)
    analytics = get_user_analytics(user_id)
    question_progress = get_category_progress(user_id)
    practice_stats = get_user_stats(user_id or 0)

    # 构建能力雷达图数据
    if profile_data:
        capability_analysis = analyze_capabilities(profile_data)
    else:
        # 使用模拟数据
        capability_analysis = _generate_mock_capabilities(progress, stats)

    radar_data = get_radar_chart_data(capability_analysis)

    # 获取或初始化成长时间线
    timeline = _get_or_init_timeline(user_id_str, growth_data, progress, stats)

    # 生成横向对比数据
    comparison = _generate_age_comparison(stats, profile_data)

    # 计算综合成长评分
    overall_score = _calculate_overall_score(stats, analytics, question_progress)

    # 获取成长里程碑
    milestones = _get_milestones(stats, progress, analytics)

    # 整合所有数据
    growth_profile = {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(),
        "child_name": profile_data.get("child_name", "小明")
        if profile_data
        else "小明",
        "child_age": profile_data.get("child_age", "K2") if profile_data else "K2",
        # 能力雷达图数据
        "radar": radar_data,
        "capabilities": capability_analysis,
        # 练习数据统计
        "practice_stats": {
            "total_practices": stats.get("total_practices", 0),
            "total_minutes": stats.get("total_minutes", 0),
            "streak_days": stats.get("streak_days", 0),
            "topics_completed": stats.get("completed_topics", 0),
            "total_topics": stats.get("total_topics", 5),
        },
        # 题库正确率
        "question_stats": {
            "categories": question_progress,
            "overall_accuracy": _calculate_accuracy(question_progress),
        },
        # 成长时间线
        "timeline": timeline,
        # 横向对比
        "comparison": comparison,
        # 综合评分
        "overall_score": overall_score,
        # 成长里程碑
        "milestones": milestones,
        # 目标学校分析
        "school_analysis": _analyze_school_match(profile_data, capability_analysis)
        if profile_data
        else None,
    }

    return growth_profile


def _generate_mock_capabilities(progress, stats):
    """生成模拟能力数据"""
    # 基于练习进度计算能力分数
    completed = stats.get("completed_topics", 0)
    base_score = 50 + (completed * 8)

    capabilities = {
        "communication": min(base_score + random.randint(-5, 10), 95),
        "logic": min(base_score + random.randint(-5, 8), 95),
        "creativity": min(base_score + random.randint(-8, 10), 95),
        "confidence": min(base_score + random.randint(-5, 12), 95),
        "eye_contact": min(base_score + random.randint(-8, 8), 95),
        "manners": min(base_score + random.randint(-5, 5), 95),
    }

    # 构建分析结果
    gaps = {}
    for dim, score in capabilities.items():
        gaps[dim] = {
            "score": score,
            "expected": 70,
            "gap": score - 70,
            "status": "good" if score >= 70 else "warning",
        }

    return {
        "overall_score": sum(capabilities.values()) / len(capabilities),
        "capabilities": capabilities,
        "gaps": gaps,
        "strengths": [dim for dim, s in capabilities.items() if s >= 75],
        "improvements": [dim for dim, s in capabilities.items() if s < 65],
    }


def _get_or_init_timeline(user_id, growth_data, progress, stats):
    """获取或初始化成长时间线"""
    if user_id in growth_data and "timeline" in growth_data[user_id]:
        return growth_data[user_id]["timeline"]

    # 生成初始时间线数据
    timeline = []
    now = datetime.now()

    # 基于实际练习记录生成时间线
    topics = progress.get("topics", {})
    for topic_id, topic_data in topics.items():
        if topic_data.get("complete_count", 0) > 0:
            practice_count = topic_data.get("practice_count", 0)
            last_practice = topic_data.get("last_practice")

            timeline.append(
                {
                    "date": last_practice or now.isoformat(),
                    "type": "practice",
                    "topic": topic_id,
                    "title": _get_topic_name(topic_id),
                    "detail": f"完成{practice_count}次练习",
                    "score": topic_data.get("latest_score", 0),
                }
            )

    # 如果没有记录，生成模拟数据
    if not timeline:
        for i in range(5):
            days_ago = (4 - i) * 3
            date = now - timedelta(days=days_ago)
            topic = [
                "self-introduction",
                "interests",
                "family",
                "observation",
                "scenarios",
            ][i % 5]

            timeline.append(
                {
                    "date": date.isoformat(),
                    "type": "practice",
                    "topic": topic,
                    "title": _get_topic_name(topic),
                    "detail": f"完成{random.randint(2, 5)}次练习",
                    "score": random.randint(70, 95),
                }
            )

    # 按日期排序
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return timeline[:20]  # 只返回最近20条


def _get_topic_name(topic_id):
    """获取主题名称"""
    topic_names = {
        "self-introduction": "自我介紹",
        "interests": "興趣愛好",
        "family": "家庭介紹",
        "observation": "觀察力訓練",
        "scenarios": "處境題",
    }
    return topic_names.get(topic_id, topic_id)


def _generate_age_comparison(stats, profile_data):
    """生成同龄对比数据"""
    child_age = profile_data.get("child_age", "K2") if profile_data else "K2"

    # 根据年龄段生成对比数据
    age_group = _get_age_group(child_age)

    return {
        "age_group": age_group,
        "your_score": stats.get("completed_topics", 0) * 20,
        "average": 60 + random.randint(-10, 10),
        "top_10_percent": 85 + random.randint(-5, 10),
        "percentile": random.randint(40, 90),
    }


def _get_age_group(age):
    """获取年龄段"""
    if age.startswith("K"):
        return f"幼兒園{age}"
    elif age.isdigit():
        if int(age) <= 6:
            return "小一"
    return "K2"


def _calculate_accuracy(categories):
    """计算整体正确率"""
    if not categories:
        return 0

    total_correct = sum(cat.get("correct", 0) for cat in categories)
    total_practiced = sum(cat.get("practiced", 0) for cat in categories)

    if total_practiced == 0:
        return 0

    return int((total_correct / total_practiced) * 100)


def _calculate_overall_score(stats, analytics, question_progress):
    """计算综合成长评分"""
    # 权重分配
    practice_weight = 0.3
    progress_weight = 0.25
    accuracy_weight = 0.25
    streak_weight = 0.2

    # 练习频率得分
    practice_score = min(stats.get("total_practices", 0) * 10, 100)

    # 进度得分
    completed = stats.get("completed_topics", 0)
    total = stats.get("total_topics", 5)
    progress_score = (completed / total * 100) if total > 0 else 0

    # 正确率得分
    accuracy_score = _calculate_accuracy(question_progress)

    # 连续天数得分
    streak = stats.get("streak_days", 0)
    streak_score = min(streak * 10, 100)

    # 加权计算
    overall = (
        practice_score * practice_weight
        + progress_score * progress_weight
        + accuracy_score * accuracy_weight
        + streak_score * streak_weight
    )

    return round(overall, 1)


def _get_milestones(stats, progress, analytics):
    """获取成长里程碑"""
    milestones = []

    completed = stats.get("completed_topics", 0)
    total_practices = stats.get("total_practices", 0)
    streak = stats.get("streak_days", 0)

    # 基于实际数据生成里程碑
    if completed >= 1:
        milestones.append(
            {
                "id": "first_topic",
                "title": "初试锋芒",
                "description": "完成第一个主题练习",
                "icon": "star",
                "achieved": True,
                "date": datetime.now().isoformat(),
            }
        )

    if completed >= 3:
        milestones.append(
            {
                "id": "three_topics",
                "title": "三心二意",
                "description": "完成三个主题的练习",
                "icon": "school",
                "achieved": True,
                "date": datetime.now().isoformat(),
            }
        )

    if completed >= 5:
        milestones.append(
            {
                "id": "all_topics",
                "title": "全能面霸",
                "description": "完成所有主题练习",
                "icon": "emoji_events",
                "achieved": True,
                "date": datetime.now().isoformat(),
            }
        )

    if total_practices >= 10:
        milestones.append(
            {
                "id": "ten_practices",
                "title": "勤学苦练",
                "description": "完成10次练习",
                "icon": "fitness_center",
                "achieved": True,
                "date": datetime.now().isoformat(),
            }
        )

    if streak >= 3:
        milestones.append(
            {
                "id": "three_day_streak",
                "title": "持之以恒",
                "description": "连续练习3天",
                "icon": "local_fire_department",
                "achieved": True,
                "date": datetime.now().isoformat(),
            }
        )

    if streak >= 7:
        milestones.append(
            {
                "id": "week_streak",
                "title": "一周之星",
                "description": "连续练习7天",
                "icon": "whatshot",
                "achieved": True,
                "date": datetime.now().isoformat(),
            }
        )

    # 添加未达成的里程碑作为目标
    all_milestones = [
        {
            "id": "perfect_score",
            "title": "满分达成",
            "description": "获得一次满分",
            "icon": "verified",
            "achieved": False,
        },
        {
            "id": "interview_ready",
            "title": "面试就绪",
            "description": "完成全部能力提升",
            "icon": "workspace_premium",
            "achieved": False,
        },
    ]

    for m in all_milestones:
        if m["id"] not in [x["id"] for x in milestones]:
            milestones.append(m)

    return milestones


def _analyze_school_match(profile_data, capability_analysis):
    """分析学校匹配度"""
    target_schools = profile_data.get("target_schools", [])

    if not target_schools:
        return None

    capabilities = capability_analysis.get("capabilities", {})

    matches = []
    for school_type in target_schools:
        if school_type in SCHOOL_EXPECTATIONS:
            expectations = SCHOOL_EXPECTATIONS[school_type]

            # 计算匹配度
            total_gap = 0
            for dim, expected in expectations.items():
                score = capabilities.get(dim, 0)
                total_gap += score - expected

            match_score = 100 + total_gap  # 简单计算

            matches.append(
                {
                    "school_type": school_type,
                    "match_score": max(0, min(100, match_score)),
                    "status": "excellent"
                    if match_score >= 85
                    else "good"
                    if match_score >= 70
                    else "needs_improvement",
                }
            )

    return matches


def record_practice_milestone(user_id, topic_id, score):
    """记录练习里程碑"""
    user_id_str = str(user_id)
    growth_data = _load_growth_data()

    if user_id_str not in growth_data:
        growth_data[user_id_str] = {"timeline": []}

    # 添加新的时间线记录
    timeline_entry = {
        "date": datetime.now().isoformat(),
        "type": "practice",
        "topic": topic_id,
        "title": _get_topic_name(topic_id),
        "detail": f"获得{score}分",
        "score": score,
    }

    growth_data[user_id_str].setdefault("timeline", [])
    growth_data[user_id_str]["timeline"].append(timeline_entry)

    # 保持最近20条
    growth_data[user_id_str]["timeline"] = growth_data[user_id_str]["timeline"][-20:]

    _save_growth_data(growth_data)

    return timeline_entry


def generate_portfolio_summary(growth_profile):
    """生成作品集摘要（用于PDF）"""
    return {
        "title": f"{growth_profile['child_name']}的面试成长档案",
        "generated_at": growth_profile["generated_at"],
        "overall_score": growth_profile["overall_score"],
        "radar": growth_profile["radar"],
        "practice_stats": growth_profile["practice_stats"],
        "milestones": [m for m in growth_profile["milestones"] if m.get("achieved")],
        "strengths": growth_profile["capabilities"].get("strengths", []),
    }


def generate_personalized_feedback(growth_profile):
    """使用MiniMax API生成个性化成长评语"""
    try:
        from services.ai_generator import call_minimax_api

        child_name = growth_profile.get("child_name", "小朋友")
        overall_score = growth_profile.get("overall_score", 0)
        practice_stats = growth_profile.get("practice_stats", {})
        capabilities = growth_profile.get("capabilities", {})
        strengths = capabilities.get("strengths", [])
        improvements = capabilities.get("improvements", [])

        strength_names = {
            "communication": "沟通表达",
            "logic": "逻辑思维",
            "creativity": "创意思维",
            "confidence": "自信心",
            "eye_contact": "眼神接触",
            "manners": "礼貌礼仪",
        }

        strength_text = (
            "、".join([strength_names.get(s, s) for s in strengths])
            if strengths
            else "暂无突出优势"
        )
        improvement_text = (
            "、".join([strength_names.get(s, s) for s in improvements])
            if improvements
            else "暂无待提升领域"
        )

        system_prompt = """你是一位专业的幼儿面试导师，善于用温暖鼓励的语气给家长和孩子提供成长反馈。"""

        user_prompt = f"""请为以下面试成长档案生成个性化的成长评语：

孩子姓名：{child_name}
综合成长评分：{overall_score}分
练习次数：{practice_stats.get("total_practices", 0)}次
连续练习：{practice_stats.get("streak_days", 0)}天
完成主题：{practice_stats.get("topics_completed", 0)}个

能力优势：{strength_text}
需要提升：{improvement_text}

请生成：
1. 一段对孩子的鼓励评语（50字以内）
2. 对家长的建议（80字以内）

用温暖、专业但不官方的语气。"""

        payload = {
            "model": "abab6.5s-chat",
            "tokens": 500,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        result = call_minimax_api("text/chatcompletion_v2", payload)

        if result and "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            parts = content.split("\n\n")
            return {
                "child_feedback": parts[0]
                if len(parts) > 0
                else f"{child_name}继续加油！",
                "parent_advice": parts[1]
                if len(parts) > 1
                else "建议每天保持练习习惯。",
            }
    except Exception as e:
        print(f"⚠️ Error generating personalized feedback: {e}")

    return {
        "child_feedback": f"{child_name}继续加油！保持练习就能进步！",
        "parent_advice": "建议每天保持15分钟的有效练习，关注孩子的兴趣和自信心培养。",
    }
