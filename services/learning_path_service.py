"""
Learning Path Service
智能学习路径规划服务 - 生成和管理个性化学习路径
"""

import random
import time
from datetime import datetime
from services.capability_radar_service import (
    CAPABILITY_DIMENSIONS,
    SCHOOL_EXPECTATIONS,
    analyze_capabilities
)
from services.mock_interview_service import SCHOOL_TYPES


# ============ 阶段和里程碑定义 ============

# 阶段定义
PHASES = {
    1: {
        "id": 1,
        "name": "基础巩固",
        "name_en": "Foundation",
        "description": "建立面试基础能力和自信心",
        "color": "#4CAF50",
        "icon": "📚"
    },
    2: {
        "id": 2,
        "name": "能力提升",
        "name_en": "Skill Enhancement",
        "description": "针对薄弱环节强化训练",
        "color": "#2196F3",
        "icon": "🚀"
    },
    3: {
        "id": 3,
        "name": "冲刺准备",
        "name_en": "Final Sprint",
        "description": "模拟面试演练和综合提升",
        "color": "#FF9800",
        "icon": "🎯"
    },
    4: {
        "id": 4,
        "name": "考前冲刺",
        "name_en": "Pre-Interview",
        "description": "全面准备迎接面试",
        "color": "#E91E63",
        "icon": "🏆"
    }
}

# 里程碑定义
MILESTONES = {
    # 阶段1: 基础巩固
    "1.1": {
        "id": "1.1",
        "phase": 1,
        "name": "自我介绍掌握",
        "description": "能够自信流利地进行1-2分钟自我介绍",
        "skills": ["communication", "confidence"],
        "type": "core",
        "estimated_time": "30分钟",
        "resources": ["self-introduction"]
    },
    "1.2": {
        "id": "1.2",
        "phase": 1,
        "name": "基本礼仪",
        "description": "掌握面试基本礼仪：问好、道谢、坐姿",
        "skills": ["manners", "eye_contact"],
        "type": "core",
        "estimated_time": "20分钟",
        "resources": ["etiquette"]
    },

    # 阶段2: 能力提升
    "2.1": {
        "id": "2.1",
        "phase": 2,
        "name": "逻辑思维训练",
        "description": "练习简单因果关系表达",
        "skills": ["logic"],
        "type": "custom",
        "estimated_time": "40分钟",
        "resources": ["logic-training"]
    },
    "2.2": {
        "id": "2.2",
        "phase": 2,
        "name": "创意思维激发",
        "description": "培养想象力和创意表达能力",
        "skills": ["creativity"],
        "type": "custom",
        "estimated_time": "40分钟",
        "resources": ["creative-thinking"]
    },

    # 阶段3: 冲刺准备
    "3.1": {
        "id": "3.1",
        "phase": 3,
        "name": "模拟面试演练",
        "description": "完整模拟面试流程",
        "skills": ["communication", "confidence", "logic"],
        "type": "core",
        "estimated_time": "60分钟",
        "resources": ["mock-interview"]
    },
    "3.2": {
        "id": "3.2",
        "phase": 3,
        "name": "综合表现优化",
        "description": "整体表现微调和优化",
        "skills": ["communication", "confidence", "eye_contact", "manners"],
        "type": "core",
        "estimated_time": "45分钟",
        "resources": ["performance"]
    },

    # 阶段4: 考前冲刺
    "4.1": {
        "id": "4.1",
        "phase": 4,
        "name": "全面准备就绪",
        "description": "所有技能达标，迎接面试",
        "skills": ["communication", "logic", "creativity", "confidence", "eye_contact", "manners"],
        "type": "core",
        "estimated_time": "60分钟",
        "resources": ["final-prep"]
    }
}

# 学校类型学习重点（优先级排序）
SCHOOL_FOCUS_PRIORITIES = {
    "academic": {
        "priority_order": ["logic", "communication", "manners", "confidence", "eye_contact", "creativity"],
        "recommended_milestones": ["1.1", "1.2", "2.1", "3.1", "3.2", "4.1"]
    },
    "holistic": {
        "priority_order": ["creativity", "confidence", "communication", "eye_contact", "manners", "logic"],
        "recommended_milestones": ["1.1", "1.2", "2.2", "3.1", "3.2", "4.1"]
    },
    "international": {
        "priority_order": ["creativity", "communication", "confidence", "eye_contact", "logic", "manners"],
        "recommended_milestones": ["1.1", "1.2", "2.2", "3.1", "3.2", "4.1"]
    },
    "traditional": {
        "priority_order": ["logic", "manners", "eye_contact", "communication", "confidence", "creativity"],
        "recommended_milestones": ["1.1", "1.2", "2.1", "3.1", "3.2", "4.1"]
    }
}

# ============ 内存存储（生产环境应使用数据库） ============

learning_paths = {}
user_progress = {}


# ============ 核心功能函数 ============

def generate_diagnostic_test(user_id, school_type="academic"):
    """
    生成入门测试题目

    Args:
        user_id: 用户ID
        school_type: 学校类型

    Returns:
        dict: 包含测试题目的结果
    """
    # 能力诊断问题
    diagnostic_questions = [
        {
            "id": "d1",
            "category": "self_intro",
            "question": "小朋友，你叫咩名呀？可以介绍一下自己吗？",
            "evaluation_criteria": {
                "confidence": "是否有自信回答",
                "communication": "表达是否清晰",
                "completeness": "是否包含基本信息（姓名、年龄、幼儿园）"
            },
            "difficulty": "easy"
        },
        {
            "id": "d2",
            "category": "logic",
            "question": "你钟意食咩生果呀？点解你咁钟意食啲生果？",
            "evaluation_criteria": {
                "logic": "是否能说明原因",
                "communication": "表达是否连贯"
            },
            "difficulty": "easy"
        },
        {
            "id": "d3",
            "category": "creativity",
            "question": "如果你可以变一样嘢，你会变咩呀？点解呀？",
            "evaluation_criteria": {
                "creativity": "想象力是否丰富",
                "communication": "表达是否具体"
            },
            "difficulty": "medium"
        },
        {
            "id": "d4",
            "category": "confidence",
            "question": "你可以望住老师，重复一次你啱先讲嘅嘢吗？",
            "evaluation_criteria": {
                "confidence": "是否愿意配合",
                "eye_contact": "眼神交流如何"
            },
            "difficulty": "easy"
        },
        {
            "id": "d5",
            "category": "manners",
            "question": "如果老师帮咗你，你要同老师讲咩呀？",
            "evaluation_criteria": {
                "manners": "是否知道感谢",
                "communication": "表达是否有礼貌"
            },
            "difficulty": "easy"
        }
    ]

    return {
        "test_id": f"diagnostic_{int(time.time())}",
        "school_type": school_type,
        "questions": diagnostic_questions,
        "estimated_time": "10分钟",
        "instructions": "请家长陪同孩子完成以下5道题目，观察孩子的表现并记录。"
    }


def assess_capabilities(user_id, answers, profile_data):
    """
    评估用户能力

    Args:
        user_id: 用户ID
        answers: 用户回答数据
        profile_data: 用户画像数据

    Returns:
        dict: 能力评估结果
    """
    # 基于回答评估各维度能力
    capabilities = {
        "communication": 50,
        "logic": 50,
        "creativity": 50,
        "confidence": 50,
        "eye_contact": 50,
        "manners": 50
    }

    # 结合画像数据分析
    if profile_data:
        profile_analysis = analyze_capabilities(profile_data, None, None)
        # 取画像分析结果和测试结果的综合
        for dim in capabilities:
            if dim in profile_analysis.get("capabilities", {}):
                # 60% 测试结果 + 40% 画像分析
                test_score = capabilities[dim]
                profile_score = profile_analysis["capabilities"][dim]
                capabilities[dim] = int(test_score * 0.6 + profile_score * 0.4)

    # 评估每个维度
    evaluation = {}
    for dim, score in capabilities.items():
        evaluation[dim] = {
            "score": score,
            "name": CAPABILITY_DIMENSIONS.get(dim, {}).get("name", dim),
            "level": get_level_from_score(score)
        }

    return {
        "capabilities": capabilities,
        "evaluation": evaluation,
        "overall_score": sum(capabilities.values()) / len(capabilities)
    }


def get_level_from_score(score):
    """根据分数获取能力等级"""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "fair"
    else:
        return "needs_improvement"


def generate_learning_path(user_id, school_type, capabilities):
    """
    生成学习路径

    Args:
        user_id: 用户ID
        school_type: 学校类型
        capabilities: 能力评估结果

    Returns:
        dict: 学习路径数据
    """
    path_id = f"path_{user_id}_{int(time.time())}"

    # 获取学校类型配置
    school_config = SCHOOL_TYPES.get(school_type, SCHOOL_TYPES["academic"])
    focus_config = SCHOOL_FOCUS_PRIORITIES.get(school_type, SCHOOL_FOCUS_PRIORITIES["academic"])

    # 获取期望能力
    expectations = SCHOOL_EXPECTATIONS.get(school_type, SCHOOL_EXPECTATIONS["academic"])

    # 计算能力差距
    gaps = {}
    priority_dims = focus_config["priority_order"]

    for dim in priority_dims:
        current = capabilities.get(dim, 50)
        expected = expectations.get(dim, 70)
        gap = expected - current

        if gap > 0:
            gaps[dim] = {
                "current": current,
                "expected": expected,
                "gap": gap,
                "priority": priority_dims.index(dim) + 1
            }

    # 生成阶段和里程碑
    phases = []

    # 阶段1: 基础巩固 - 所有人都需要
    phase1_milestones = [
        create_milestone_data(MILESTONES["1.1"], capabilities),
        create_milestone_data(MILESTONES["1.2"], capabilities)
    ]
    phases.append(create_phase_data(1, phase1_milestones, len(phase1_milestones)))

    # 阶段2: 能力提升 - 根据能力差距定制
    phase2_milestones = []
    if "logic" in gaps or "creativity" in gaps:
        if "logic" in gaps:
            phase2_milestones.append(create_milestone_data(MILESTONES["2.1"], capabilities))
        if "creativity" in gaps:
            phase2_milestones.append(create_milestone_data(MILESTONES["2.2"], capabilities))

    # 如果没有特定差距，添加默认里程碑
    if not phase2_milestones:
        phase2_milestones.append(create_milestone_data(MILESTONES["2.1"], capabilities))

    phases.append(create_phase_data(2, phase2_milestones, len(phase2_milestones)))

    # 阶段3: 冲刺准备
    phase3_milestones = [
        create_milestone_data(MILESTONES["3.1"], capabilities),
        create_milestone_data(MILESTONES["3.2"], capabilities)
    ]
    phases.append(create_phase_data(3, phase3_milestones, len(phase3_milestones)))

    # 阶段4: 考前冲刺
    phase4_milestones = [
        create_milestone_data(MILESTONES["4.1"], capabilities)
    ]
    phases.append(create_phase_data(4, phase4_milestones, len(phase4_milestones)))

    # 计算路径总时间
    total_time = sum([int(m["estimated_time"].replace("分钟", ""))
                     for p in phases for m in p["milestones"]])

    path_data = {
        "path_id": path_id,
        "user_id": user_id,
        "school_type": school_type,
        "school_type_name": school_config.get("name", "学术型"),
        "phases": phases,
        "gaps": gaps,
        "capabilities": capabilities,
        "expectations": expectations,
        "total_time_minutes": total_time,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }

    # 保存到内存存储
    learning_paths[user_id] = path_data
    if user_id not in user_progress:
        user_progress[user_id] = {
            "current_phase": 1,
            "completed_milestones": [],
            "started_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }

    return path_data


def create_milestone_data(milestone_template, capabilities):
    """创建里程碑数据"""
    milestone = dict(milestone_template)

    # 计算该里程碑相关的技能是否达标
    skills_status = {}
    for skill in milestone["skills"]:
        score = capabilities.get(skill, 50)
        skills_status[skill] = {
            "score": score,
            "status": "ready" if score >= 50 else "needs_work"
        }

    # 简化版里程碑（不包含依赖逻辑）
    milestone.update({
        "status": "available",
        "skills_status": skills_status,
        "completed_at": None
    })

    return milestone


def create_phase_data(phase_num, milestones, total_milestones):
    """创建阶段数据"""
    phase_template = PHASES[phase_num]
    completed = sum(1 for m in milestones if m.get("status") == "completed")

    return {
        **phase_template,
        "milestones": milestones,
        "total_milestones": len(milestones),
        "completed_milestones": completed,
        "progress_percent": int((completed / len(milestones)) * 100) if milestones else 0
    }


def get_learning_path(user_id):
    """获取用户的学习路径"""
    return learning_paths.get(user_id)


def get_learning_map(user_id):
    """获取学习地图数据"""
    path = learning_paths.get(user_id)

    if not path:
        return None

    # 构建地图数据
    map_data = {
        "path_id": path["path_id"],
        "school_type": path["school_type"],
        "school_type_name": path["school_type_name"],
        "phases": [],
        "overall_progress": calculate_overall_progress(user_id)
    }

    for phase in path["phases"]:
        phase_data = {
            "id": phase["id"],
            "name": phase["name"],
            "description": phase["description"],
            "color": phase["color"],
            "icon": phase["icon"],
            "milestones": [],
            "progress_percent": phase["progress_percent"]
        }

        for milestone in phase["milestones"]:
            milestone_data = {
                "id": milestone["id"],
                "name": milestone["name"],
                "description": milestone["description"],
                "status": milestone["status"],
                "type": milestone["type"],
                "skills": milestone["skills"],
                "estimated_time": milestone["estimated_time"]
            }
            phase_data["milestones"].append(milestone_data)

        map_data["phases"].append(phase_data)

    return map_data


def calculate_overall_progress(user_id):
    """计算总体进度"""
    if user_id not in user_progress:
        return 0

    progress = user_progress[user_id]
    completed = len(progress.get("completed_milestones", []))

    # 假设总共8个里程碑
    total_milestones = 8

    return int((completed / total_milestones) * 100)


def get_progress_data(user_id):
    """获取进度数据"""
    path = learning_paths.get(user_id)
    progress = user_progress.get(user_id, {})

    if not path:
        return {
            "has_path": False,
            "message": "请先进行能力诊断以生成学习路径"
        }

    # 汇总各阶段进度
    phase_progress = []
    for phase in path["phases"]:
        completed = sum(1 for m in phase["milestones"] if m.get("status") == "completed")
        total = len(phase["milestones"])

        phase_progress.append({
            "phase_id": phase["id"],
            "phase_name": phase["name"],
            "completed": completed,
            "total": total,
            "progress_percent": int((completed / total) * 100) if total > 0 else 0
        })

    # 计算总进度
    total_completed = sum(p["completed"] for p in phase_progress)
    total_milestones = sum(p["total"] for p in phase_progress)
    overall_percent = int((total_completed / total_milestones) * 100) if total_milestones > 0 else 0

    # 计算能力提升
    current_capabilities = path.get("capabilities", {})
    expectations = path.get("expectations", {})

    capability_improvement = []
    for dim, expected in expectations.items():
        current = current_capabilities.get(dim, 0)
        improvement = max(0, expected - current)
        capability_improvement.append({
            "dimension": dim,
            "name": CAPABILITY_DIMENSIONS.get(dim, {}).get("name", dim),
            "current": current,
            "expected": expected,
            "improvement_needed": improvement
        })

    return {
        "has_path": True,
        "path_id": path["path_id"],
        "school_type": path["school_type"],
        "school_type_name": path["school_type_name"],
        "current_phase": progress.get("current_phase", 1),
        "phase_progress": phase_progress,
        "overall_percent": overall_percent,
        "total_completed": total_completed,
        "total_milestones": total_milestones,
        "capability_improvement": capability_improvement,
        "started_at": progress.get("started_at"),
        "last_active": progress.get("last_active")
    }


def update_milestone_progress(user_id, milestone_id, status="completed"):
    """更新里程碑进度"""
    if user_id not in learning_paths:
        return False

    path = learning_paths[user_id]

    # 查找并更新里程碑
    for phase in path["phases"]:
        for milestone in phase["milestones"]:
            if milestone["id"] == milestone_id:
                milestone["status"] = status
                if status == "completed":
                    milestone["completed_at"] = datetime.now().isoformat()

                    # 更新进度记录
                    if user_id not in user_progress:
                        user_progress[user_id] = {
                            "current_phase": 1,
                            "completed_milestones": [],
                            "started_at": datetime.now().isoformat()
                        }

                    if milestone_id not in user_progress[user_id].get("completed_milestones", []):
                        if "completed_milestones" not in user_progress[user_id]:
                            user_progress[user_id]["completed_milestones"] = []
                        user_progress[user_id]["completed_milestones"].append(milestone_id)

                    # 更新当前阶段
                    milestone_phase = milestone["phase"]
                    user_progress[user_id]["current_phase"] = min(milestone_phase + 1, 4)

                user_progress[user_id]["last_active"] = datetime.now().isoformat()
                return True

    return False


def optimize_path(user_id, practice_data=None):
    """
    根据练习数据优化学习路径

    Args:
        user_id: 用户ID
        practice_data: 练习数据（可选）

    Returns:
        dict: 优化后的学习路径
    """
    path = learning_paths.get(user_id)

    if not path:
        return None

    # 如果有练习数据，根据数据调整
    if practice_data:
        # 提取练习中表现好的技能
        strong_skills = practice_data.get("strong_skills", [])
        weak_skills = practice_data.get("weak_skills", [])

        # 调整里程碑优先级
        for phase in path["phases"]:
            for milestone in phase["milestones"]:
                # 跳过已完成的
                if milestone["status"] == "completed":
                    continue

                # 检查里程碑涉及技能
                milestone_skills = milestone.get("skills", [])

                # 如果所有技能都是弱的，标记为高优先级
                if all(s in weak_skills for s in milestone_skills):
                    milestone["priority"] = "high"
                elif any(s in strong_skills for s in milestone_skills):
                    milestone["priority"] = "low"

    # 更新路径状态
    path["last_optimized"] = datetime.now().isoformat()
    path["optimization_count"] = path.get("optimization_count", 0) + 1

    return path


def reset_learning_path(user_id):
    """重置学习路径"""
    if user_id in learning_paths:
        del learning_paths[user_id]
    if user_id in user_progress:
        del user_progress[user_id]
    return True


# ============ 工具函数 ============

def get_school_type_info(school_type):
    """获取学校类型信息"""
    school_config = SCHOOL_TYPES.get(school_type, {})
    focus_config = SCHOOL_FOCUS_PRIORITIES.get(school_type, {})

    return {
        "school_type": school_type,
        "name": school_config.get("name", ""),
        "description": school_config.get("description", ""),
        "focus_order": focus_config.get("priority_order", []),
        "focus_names": [
            CAPABILITY_DIMENSIONS.get(dim, {}).get("name", dim)
            for dim in focus_config.get("priority_order", [])
        ]
    }


def get_all_milestones():
    """获取所有里程碑定义"""
    return MILESTONES


def get_all_phases():
    """获取所有阶段定义"""
    return PHASES
