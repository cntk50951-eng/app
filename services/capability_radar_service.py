"""
面试能力分析服务
分析孩子在各维度的面试能力，生成雷达图数据
"""

# 面试能力维度定义
CAPABILITY_DIMENSIONS = {
    "communication": {
        "name": "沟通表达",
        "description": "清晰表达想法的能力",
        "school_weights": {
            "academic": 0.25,
            "holistic": 0.20,
            "international": 0.25,
            "traditional": 0.20
        }
    },
    "logic": {
        "name": "逻辑思维",
        "description": "思考和解决问题的能力",
        "school_weights": {
            "academic": 0.30,
            "holistic": 0.15,
            "international": 0.20,
            "traditional": 0.25
        }
    },
    "creativity": {
        "name": "创意思维",
        "description": "想象力和创新能力",
        "school_weights": {
            "academic": 0.10,
            "holistic": 0.25,
            "international": 0.25,
            "traditional": 0.10
        }
    },
    "confidence": {
        "name": "自信心",
        "description": "自我展示的自信程度",
        "school_weights": {
            "academic": 0.15,
            "holistic": 0.20,
            "international": 0.15,
            "traditional": 0.20
        }
    },
    "eye_contact": {
        "name": "眼神接触",
        "description": "与他人眼神交流的能力",
        "school_weights": {
            "academic": 0.10,
            "holistic": 0.10,
            "international": 0.10,
            "traditional": 0.15
        }
    },
    "manners": {
        "name": "礼貌礼仪",
        "description": "基本礼仪和社交礼貌",
        "school_weights": {
            "academic": 0.10,
            "holistic": 0.10,
            "international": 0.05,
            "traditional": 0.10
        }
    }
}

# 学校类型期望线（满分100）
SCHOOL_EXPECTATIONS = {
    "academic": {
        "communication": 80,
        "logic": 85,
        "creativity": 60,
        "confidence": 70,
        "eye_contact": 65,
        "manners": 75
    },
    "holistic": {
        "communication": 75,
        "logic": 65,
        "creativity": 80,
        "confidence": 75,
        "eye_contact": 70,
        "manners": 70
    },
    "international": {
        "communication": 80,
        "logic": 70,
        "creativity": 80,
        "confidence": 75,
        "eye_contact": 70,
        "manners": 65
    },
    "traditional": {
        "communication": 70,
        "logic": 75,
        "creativity": 55,
        "confidence": 65,
        "eye_contact": 75,
        "manners": 85
    }
}


def analyze_capabilities(profile_data, interview_history=None, school_type=None):
    """
    分析孩子的面试能力

    Args:
        profile_data: 孩子画像数据
        interview_history: 面试历史记录（可选）
        school_type: 目标学校类型（可选）

    Returns:
        dict: 能力分析结果
    """
    # 从画像数据计算能力分数
    capability_scores = calculate_base_capabilities(profile_data)

    # 如果有面试历史，结合历史表现
    if interview_history:
        capability_scores = combine_with_history(capability_scores, interview_history)

    # 计算与学校期望的差距
    gaps = {}
    if school_type and school_type in SCHOOL_EXPECTATIONS:
        expectations = SCHOOL_EXPECTATIONS[school_type]
        for dim, score in capability_scores.items():
            expected = expectations.get(dim, 70)
            gaps[dim] = {
                "score": score,
                "expected": expected,
                "gap": score - expected,
                "status": get_gap_status(score, expected)
            }
    else:
        for dim, score in capability_scores.items():
            gaps[dim] = {
                "score": score,
                "expected": 70,
                "gap": score - 70,
                "status": get_gap_status(score, 70)
            }

    # 计算综合得分
    if school_type and school_type in CAPABILITY_DIMENSIONS:
        weights = {dim: info["school_weights"].get(school_type, 0.15)
                  for dim, info in CAPABILITY_DIMENSIONS.items()}
    else:
        weights = {dim: 1.0/6 for dim in CAPABILITY_DIMENSIONS}

    overall_score = sum(score * weights.get(dim, 0.15)
                        for dim, score in capability_scores.items())

    # 生成改进建议
    suggestions = generate_suggestions(gaps, school_type)

    # 识别优势和改进点
    strengths = [dim for dim, data in gaps.items() if data["status"] == "excellent" or data["status"] == "good"]
    improvements = [dim for dim, data in gaps.items() if data["status"] == "warning" or data["status"] == "critical"]

    return {
        "overall_score": round(overall_score, 1),
        "capabilities": capability_scores,
        "gaps": gaps,
        "school_type": school_type,
        "expectations": SCHOOL_EXPECTATIONS.get(school_type, SCHOOL_EXPECTATIONS["academic"]),
        "suggestions": suggestions,
        "strengths": strengths,
        "improvements": improvements,
        "dimensions": CAPABILITY_DIMENSIONS
    }


def calculate_base_capabilities(profile_data):
    """
    基于孩子画像计算基础能力分数
    """
    scores = {}

    # 提取数据
    interests = profile_data.get('interests', [])
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(',') if i.strip()]

    strengths = profile_data.get('strengths', [])
    if isinstance(strengths, str):
        strengths = [s.strip() for s in strengths.split(',') if s.strip()]

    personality = profile_data.get('personality', '').lower()

    keywords = interests + strengths
    keywords_lower = [k.lower() for k in keywords]

    # 沟通表达能力
    comm_score = 50
    comm_keywords = ["说话", "讲故事", "朗诵", "演讲", "主持", "表达", "沟通"]
    for kw in keywords_lower:
        if any(k in kw for k in comm_keywords):
            comm_score += 12
    if any(p in personality for p in ["外向", "活泼", "健谈"]):
        comm_score += 10
    scores["communication"] = min(comm_score, 100)

    # 逻辑思维能力
    logic_score = 50
    logic_keywords = ["数学", "棋类", "编程", "逻辑", "思考", "解决问题"]
    for kw in keywords_lower:
        if any(k in kw for k in logic_keywords):
            logic_score += 12
    if any(p in personality for p in ["聪明", "理性", "爱思考"]):
        logic_score += 10
    scores["logic"] = min(logic_score, 100)

    # 创意思维
    creative_score = 50
    creative_keywords = ["绘画", "创意", "想象", "手工", "搭建", "音乐", "舞蹈", "艺术"]
    for kw in keywords_lower:
        if any(k in kw for k in creative_keywords):
            creative_score += 12
    if any(p in personality for p in ["创意", "想象丰富"]):
        creative_score += 10
    scores["creativity"] = min(creative_score, 100)

    # 自信心
    conf_score = 55
    conf_keywords = ["表演", "比赛", "展示", "领导", "组织"]
    for kw in keywords_lower:
        if any(k in kw for k in conf_keywords):
            conf_score += 10
    if any(p in personality for p in ["自信", "勇敢", "大方", "外向"]):
        conf_score += 15
    scores["confidence"] = min(conf_score, 100)

    # 眼神接触
    eye_score = 60
    if any(p in personality for p in ["大方", "自信", "外向"]):
        eye_score += 15
    else:
        eye_score += 5
    scores["eye_contact"] = min(eye_score, 100)

    # 礼貌礼仪
    manner_score = 55
    manner_keywords = ["礼貌", "尊重", "感谢", "帮忙", "分享"]
    for kw in keywords_lower:
        if any(k in kw for k in manner_keywords):
            manner_score += 12
    if any(p in personality for p in ["听话", "乖", "有礼貌"]):
        manner_score += 10
    scores["manners"] = min(manner_score, 100)

    return scores


def combine_with_history(base_scores, history):
    """
    结合面试历史调整分数
    """
    if not history:
        return base_scores

    # 取最近3次面试的平均分作为参考
    recent = history[:3] if len(history) > 3 else history

    # 如果有历史记录，稍微调整基础分数
    # 这里简化处理，实际应该根据历史评分调整
    adjustment = 0.1  # 10% 权重

    # 假设history包含类似能力的评分
    # 这里返回基础分数，实际需要根据真实历史数据调整
    return base_scores


def get_gap_status(score, expected):
    """
    获取差距状态
    """
    gap = score - expected
    if gap >= 10:
        return "excellent"
    elif gap >= 0:
        return "good"
    elif gap >= -10:
        return "warning"
    else:
        return "critical"


def generate_suggestions(gaps, school_type):
    """
    根据能力差距生成改进建议
    """
    suggestions = []

    for dim, data in gaps.items():
        if data["status"] in ["warning", "critical"]:
            if dim == "communication":
                suggestions.append({
                    "dimension": "沟通表达",
                    "priority": "high" if data["status"] == "critical" else "medium",
                    "title": "提升沟通表达能力",
                    "tips": [
                        "每天花10分钟让孩子复述故事或电视节目内容",
                        "练习自我介绍，控制在1-2分钟内",
                        "鼓励孩子回答开放式问题"
                    ]
                })
            elif dim == "logic":
                suggestions.append({
                    "dimension": "逻辑思维",
                    "priority": "high" if data["status"] == "critical" else "medium",
                    "title": "加强逻辑思维训练",
                    "tips": [
                        "玩棋类游戏如象棋、围棋",
                        "每天做简单的数学思维题",
                        "让孩子解释做事的步骤和原因"
                    ]
                })
            elif dim == "creativity":
                suggestions.append({
                    "dimension": "创意思维",
                    "priority": "high" if data["status"] == "critical" else "medium",
                    "title": "激发创意思维",
                    "tips": [
                        "进行创意绘画或手工制作",
                        "玩积木或乐高搭建",
                        '玩"假如...会怎样"的想象力游戏'
                    ]
                })
            elif dim == "confidence":
                suggestions.append({
                    "dimension": "自信心",
                    "priority": "high" if data["status"] == "critical" else "medium",
                    "title": "建立自信心",
                    "tips": [
                        "多给予正面鼓励和肯定",
                        "让孩子参与家庭决策",
                        "在安全环境下尝试新事物"
                    ]
                })
            elif dim == "eye_contact":
                suggestions.append({
                    "dimension": "眼神接触",
                    "priority": "high" if data["status"] == "critical" else "medium",
                    "title": "练习眼神交流",
                    "tips": [
                        "与孩子说话时提醒保持眼神接触",
                        "对着镜子练习自我介绍",
                        "玩"对视比赛"游戏"
                    ]
                })
            elif dim == "manners":
                suggestions.append({
                    "dimension": "礼貌礼仪",
                    "priority": "high" if data["status"] == "critical" else "medium",
                    "title": "培养良好礼仪",
                    "tips": [
                        "日常教育使用礼貌用语",
                        "模拟面试场景练习问好和道谢",
                        "观看礼仪教育视频"
                    ]
                })

    # 添加通用建议
    suggestions.append({
        "dimension": "通用",
        "priority": "low",
        "title": "模拟面试练习",
        "tips": [
            "使用AI模拟面试功能进行练习",
            "录制练习视频回看改进",
            "保持轻松愉快的练习氛围"
        ]
    })

    return suggestions[:6]  # 最多6条建议


def get_radar_chart_data(analysis_result):
    """
    生成雷达图所需的数据格式
    """
    capabilities = analysis_result.get("capabilities", {})
    expectations = analysis_result.get("expectations", {})

    labels = []
    scores = []
    expected = []

    dim_names = {
        "communication": "沟通表达",
        "logic": "逻辑思维",
        "creativity": "创意思维",
        "confidence": "自信心",
        "eye_contact": "眼神接触",
        "manners": "礼貌礼仪"
    }

    for dim, name in dim_names.items():
        labels.append(name)
        scores.append(capabilities.get(dim, 0))
        expected.append(expectations.get(dim, 70))

    return {
        "labels": labels,
        "scores": scores,
        "expected": expected
    }
