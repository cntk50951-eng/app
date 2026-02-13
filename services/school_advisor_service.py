"""
校长视角智能择校顾问服务
帮助家长从校长视角分析孩子与目标学校的匹配度，提供个性化面试策略
"""

# 香港热门小学偏好数据（基于公开信息和行业经验）
SCHOOL_PREFERENCES = {
    "academic": {
        "name": "学术型",
        "examples": "DBS / SPCC / 女拔萃 / 皇仁书院",
        "values": ["学术卓越", "传统价值观", "学业成绩", "考试能力"],
        "questions_style": "学术导向",
        "focus_areas": ["学业表现", "阅读习惯", "学习态度", "学科兴趣"],
        "interview_tips": [
            "准备好介绍最近阅读的书籍",
            "展示良好的学习习惯和时间管理",
            "能清晰表达对某个学科的兴趣",
            "展示自主学习能力"
        ],
        "parent_interview_focus": ["教育理念", "学业期望", "如何支持学习"]
    },
    "holistic": {
        "name": "全人型",
        "examples": "英华 / TSL / 圣士提反书院",
        "values": ["全面发展", "品格教育", "课外活动", "创造力"],
        "questions_style": "活动导向",
        "focus_areas": ["兴趣爱好", "课外活动", "团队合作", "领导力"],
        "interview_tips": [
            "展示多样的兴趣爱好和才能",
            "能讲述参与活动的收获和成长",
            "展示团队合作和领导能力",
            "表达对社会服务的热忱"
        ],
        "parent_interview_focus": ["全面发展理念", "课外活动安排", "品格教育"]
    },
    "international": {
        "name": "国际型",
        "examples": "CKY / 港同 / 韩国国际学校",
        "values": ["国际视野", "英语能力", "创新思维", "独立性"],
        "questions_style": "创意导向",
        "focus_areas": ["英语能力", "创意思维", "国际视野", "独立思考"],
        "interview_tips": [
            "能用英语简单自我介绍",
            "展示开放的心态和好奇心",
            "能表达对不同文化的兴趣",
            "展示解决问题的创新能力"
        ],
        "parent_interview_focus": ["国际化教育期望", "语言学习计划", "海外升学规划"]
    },
    "traditional": {
        "name": "传统名校",
        "examples": "KTS / SFA / 合一堂",
        "values": ["纪律严谨", "学业基础", "中文能力", "礼仪教养"],
        "questions_style": "规範导向",
        "focus_areas": ["中文能力", "纪律性", "礼仪表现", "学业基础"],
        "interview_tips": [
            "展示良好的礼貌和礼仪",
            "能用广东话流利表达",
            "展示基础学业能力和学习态度",
            "遵守课堂纪律的意识"
        ],
        "parent_interview_focus": ["传统教育期望", "纪律要求", "家校配合"]
    }
}

# 匹配度评估维度
MATCH_DIMENSIONS = {
    "academic": {
        "学业表现": 0.3,
        "阅读习惯": 0.25,
        "学习态度": 0.25,
        "学科兴趣": 0.2
    },
    "holistic": {
        "兴趣爱好": 0.3,
        "课外活动": 0.25,
        "团队合作": 0.25,
        "领导力": 0.2
    },
    "international": {
        "英语能力": 0.3,
        "创意思维": 0.25,
        "国际视野": 0.25,
        "独立思考": 0.2
    },
    "traditional": {
        "中文能力": 0.3,
        "纪律性": 0.25,
        "礼仪表现": 0.25,
        "学业基础": 0.2
    }
}


def analyze_school_match(profile_data, school_type):
    """
    分析孩子与目标学校的匹配度

    Args:
        profile_data: 孩子画像数据
        school_type: 学校类型 (academic/holistic/international/traditional)

    Returns:
        dict: 匹配度分析结果
    """
    if school_type not in SCHOOL_PREFERENCES:
        school_type = "holistic"

    school_pref = SCHOOL_PREFERENCES[school_type]
    dimensions = MATCH_DIMENSIONS[school_type]

    # 提取孩子画像信息
    interests = profile_data.get('interests', [])
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(',') if i.strip()]

    strengths = profile_data.get('strengths', [])
    if isinstance(strengths, str):
        strengths = [s.strip() for s in strengths.split(',') if s.strip()]

    personality = profile_data.get('personality', '')

    # 计算各维度匹配度
    dimension_scores = {}
    for dim, weight in dimensions.items():
        score = calculate_dimension_score(dim, interests, strengths, personality, school_type)
        dimension_scores[dim] = score

    # 计算总分
    total_score = sum(score * weight for score, (_, weight) in zip(
        dimension_scores.values(), dimensions.items()
    ))

    # 生成匹配等级
    if total_score >= 80:
        match_level = "excellent"
        match_text = "非常匹配"
    elif total_score >= 60:
        match_level = "good"
        match_text = "比较匹配"
    elif total_score >= 40:
        match_level = "moderate"
        match_text = "一般匹配"
    else:
        match_level = "low"
        match_text = "需要加强"

    # 生成建议
    suggestions = generate_suggestions(dimension_scores, school_pref, interests, strengths)

    return {
        "school_type": school_type,
        "school_name": school_pref["name"],
        "school_examples": school_pref["examples"],
        "school_values": school_pref["values"],
        "total_score": round(total_score, 1),
        "match_level": match_level,
        "match_text": match_text,
        "dimension_scores": dimension_scores,
        "interview_tips": school_pref["interview_tips"],
        "parent_interview_focus": school_pref["parent_interview_focus"],
        "suggestions": suggestions,
        "focus_areas": school_pref["focus_areas"]
    }


def calculate_dimension_score(dimension, interests, strengths, personality, school_type):
    """
    计算特定维度的匹配分数
    """
    # 将兴趣和优势合并为关键词列表
    keywords = interests + strengths
    keywords_lower = [k.lower() for k in keywords]

    # 根据维度计算分数
    if dimension == "学业表现":
        score = 60  # 基础分
        academic_keywords = ["阅读", "数学", "学习", "成绩", "考试", "拼音", "写字"]
        for kw in keywords_lower:
            if any(k in kw for k in academic_keywords):
                score += 10
        return min(score, 100)

    elif dimension == "阅读习惯":
        score = 50
        reading_keywords = ["阅读", "看书", "绘本", "故事", "图书馆"]
        for kw in keywords_lower:
            if any(k in kw for k in reading_keywords):
                score += 15
        return min(score, 100)

    elif dimension == "学习态度":
        score = 65
        attitude_keywords = ["主动", "认真", "努力", "专注", "好奇"]
        for kw in keywords_lower:
            if any(k in kw for k in attitude_keywords):
                score += 10
        return min(score, 100)

    elif dimension == "学科兴趣":
        score = 55
        subject_keywords = ["科学", "数学", "英语", "中文", "音乐", "美术", "体育"]
        for kw in keywords_lower:
            if any(k in kw for k in subject_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "兴趣爱好":
        score = 55
        hobby_keywords = ["跳舞", "绘画", "音乐", "运动", "游泳", "足球", "篮球", "钢琴", "唱歌"]
        for kw in keywords_lower:
            if any(k in kw for k in hobby_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "课外活动":
        score = 55
        activity_keywords = ["活动", "比赛", "表演", "义工", "服务", "探险", "露营"]
        for kw in keywords_lower:
            if any(k in kw for k in activity_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "团队合作":
        score = 60
        team_keywords = ["合作", "分享", "帮助", "带领", "组织", "队长"]
        for kw in keywords_lower:
            if any(k in kw for k in team_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "领导力":
        score = 55
        leader_keywords = ["领导", "组织", "队长", "负责", "安排", "指挥"]
        for kw in keywords_lower:
            if any(k in kw for k in leader_keywords):
                score += 15
        return min(score, 100)

    elif dimension == "英语能力":
        score = 50
        english_keywords = ["英语", "英文", "phonics", "英语会话", "英文歌"]
        for kw in keywords_lower:
            if any(k in kw for k in english_keywords):
                score += 15
        return min(score, 100)

    elif dimension == "创意思维":
        score = 55
        creative_keywords = ["创意", "想象", "绘画", "手工", "搭建", "发明"]
        for kw in keywords_lower:
            if any(k in kw for k in creative_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "国际视野":
        score = 55
        global_keywords = ["旅行", "国际", "外国", "文化", "交流", "海外"]
        for kw in keywords_lower:
            if any(k in kw for k in global_keywords):
                score += 15
        return min(score, 100)

    elif dimension == "独立思考":
        score = 60
        independent_keywords = ["自己", "独立", "思考", "选择", "决定"]
        for kw in keywords_lower:
            if any(k in kw for k in independent_keywords):
                score += 10
        return min(score, 100)

    elif dimension == "中文能力":
        score = 55
        chinese_keywords = ["中文", "广东话", "普通话", "讲故事", "认字", "写字"]
        for kw in keywords_lower:
            if any(k in kw for k in chinese_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "纪律性":
        score = 65
        discipline_keywords = ["守规则", "听话", "有礼貌", "尊重", "排队"]
        for kw in keywords_lower:
            if any(k in kw for k in discipline_keywords):
                score += 10
        return min(score, 100)

    elif dimension == "礼仪表现":
        score = 60
        manner_keywords = ["礼貌", "问好", "谢谢", "对不起", "请", "礼仪"]
        for kw in keywords_lower:
            if any(k in kw for k in manner_keywords):
                score += 12
        return min(score, 100)

    elif dimension == "学业基础":
        score = 55
        basic_keywords = ["基础", "写字", "数数", "拼音", "笔画", "数学基础"]
        for kw in keywords_lower:
            if any(k in kw for k in basic_keywords):
                score += 12
        return min(score, 100)

    return 60  # 默认分数


def generate_suggestions(dimension_scores, school_pref, interests, strengths):
    """
    根据匹配分析生成个性化建议
    """
    suggestions = []

    # 找出需要加强的维度
    weak_dims = [(dim, score) for dim, score in dimension_scores.items() if score < 70]
    weak_dims.sort(key=lambda x: x[1])

    # 找出需要继续保持的维度
    strong_dims = [(dim, score) for dim, score in dimension_scores.items() if score >= 80]

    # 生成加强建议
    if weak_dims:
        for dim, score in weak_dims[:2]:
            if dim == "学业表现":
                suggestions.append({
                    "type": "improve",
                    "title": "加强学业表现",
                    "content": "建议每天安排15-20分钟的学习时间，培养良好的学习习惯。可以从阅读绘本开始，逐步建立对学习的兴趣。"
                })
            elif dim == "阅读习惯":
                suggestions.append({
                    "type": "improve",
                    "title": "培养阅读习惯",
                    "content": "建议家长每天固定时间陪孩子阅读绘本，可以从15分钟开始，逐步增加。推荐选择孩子感兴趣的主题。"
                })
            elif dim == "英语能力":
                suggestions.append({
                    "type": "improve",
                    "title": "提升英语能力",
                    "content": "建议通过英文儿歌、动画片和简单的英语绘本开始启蒙。日常生活中可以用简单的英语指令与孩子互动。"
                })
            elif dim == "课外活动":
                suggestions.append({
                    "type": "improve",
                    "title": "增加课外活动",
                    "content": "建议报名参加1-2项课外活动，如音乐班、绘画班或体育活动，丰富孩子的经历和视野。"
                })
            elif dim == "中文能力":
                suggestions.append({
                    "type": "improve",
                    "title": "加强中文基础",
                    "content": "建议通过讲故事、认字卡片和简单写作练习来提升中文能力。每天10-15分钟即可。"
                })
            elif dim == "礼仪表现":
                suggestions.append({
                    "type": "improve",
                    "title": "注重礼仪训练",
                    "content": "在家中模拟面试场景，练习问好、自我介绍和回答问题的礼仪。提醒孩子保持微笑和眼神接触。"
                })

    # 生成保持建议
    if strong_dims:
        for dim, score in strong_dims[:1]:
            suggestions.append({
                "type": "keep",
                "title": f"继续保持{dim}",
                "content": f"孩子在{dim}方面表现优秀，继续保持并在此基础上进一步发展。"
            })

    # 添加面试通用建议
    suggestions.append({
        "type": "general",
        "title": "面试准备建议",
        "content": "除了关注上述具体建议外，建议进行模拟面试练习，让孩子熟悉面试流程，减少紧张感。"
    })

    return suggestions[:5]  # 最多返回5条建议


def get_school_types():
    """
    获取所有学校类型列表
    """
    return [
        {
            "id": "academic",
            "name": "学术型",
            "description": "重视学业成绩和学术能力",
            "examples": "DBS / SPCC / 女拔萃 / 皇仁书院",
            "icon": "school"
        },
        {
            "id": "holistic",
            "name": "全人型",
            "description": "重视全面发展及课外活动",
            "examples": "英华 / TSL / 圣士提反书院",
            "icon": "psychology"
        },
        {
            "id": "international",
            "name": "国际型",
            "description": "重视国际视野和英语能力",
            "examples": "CKY / 港同 / 韩国国际学校",
            "icon": "public"
        },
        {
            "id": "traditional",
            "name": "传统名校",
            "description": "重视纪律和中文基础",
            "examples": "KTS / SFA / 合一堂",
            "icon": "account_balance"
        }
    ]


def get_school_preference(school_type):
    """
    获取特定学校类型的偏好数据
    """
    return SCHOOL_PREFERENCES.get(school_type, SCHOOL_PREFERENCES["holistic"])
