"""
Interview Guide Service
面试指南服务 - 礼仪、学校攻略、家长指南
"""

# 面试礼仪指南
INTERVIEW_ETIQUETTE = {
    'title': '面试礼仪大全',
    'sections': [
        {
            'title': '服装仪容',
            'icon': 'checkroom',
            'tips': [
                {'title': '着装要求', 'content': '穿着整齐干净，最好选择校服或正式服装。避免过于花哨或暴露的服装。'},
                {'title': '发型整洁', 'content': '保持头发整洁，避免染夸张的颜色或做夸张的发型。'},
                {'title': '指甲修剪', 'content': '修剪指甲，保持手部清洁，不要涂指甲油。'},
            ]
        },
        {
            'title': '礼貌用语',
            'icon': 'person',
            'tips': [
                {'title': '问好', 'content': '进入面试室时主动说"老师好"，离开时说"谢谢老师，老师再见"。'},
                {'title': '回答问题', 'content': '回答问题时要看着老师的眼睛，不要东张西望。回答前可以先说"是的"或"明白"。'},
                {'title': '感谢', 'content': '面试结束后记得说"谢谢老师"，表现出良好的教养。'},
            ]
        },
        {
            'title': '行为举止',
            'icon': 'directions_walk',
            'tips': [
                {'title': '站姿', 'content': '站立时要挺胸抬头，双脚自然分开，不要左右摇摆。'},
                {'title': '坐姿', 'content': '坐姿要端正，不要翘二郎腿或躺坐在椅子上。'},
                {'title': '眼神', 'content': '保持眼神交流，不要低头或眼神游离，这显示自信和尊重。'},
            ]
        },
        {
            'title': '回答技巧',
            'icon': 'chat',
            'tips': [
                {'title': '如实回答', 'content': '不知道的问题如实说"我不知道"或"我不明白"，不要乱猜或撒谎。'},
                {'title': '简短扼要', 'content': '回答问题要简洁，不要说太多废话或跑题。'},
                {'title': '积极正面', 'content': '即使问到不太好的事情，也要用积极正面的态度回答。'},
            ]
        },
    ]
}

# 学校类型攻略
SCHOOL_STRATEGIES = {
    'academic': {
        'name': '学术型学校',
        'examples': 'DBS / SPCC / 男拔 / 女拔',
        'characteristics': [
            '注重学术能力和学习成绩',
            '重视英语表达能力',
            '面试问题可能有难度较高的逻辑题',
            '倾向选拔全面发展的小朋友'
        ],
        'tips': [
            '准备好用英语自我介绍',
            '练习简单的数学和逻辑问题',
            '展示你对学习的兴趣和好奇心',
            '表现出良好的学习习惯'
        ],
        'common_questions': [
            '你最喜欢哪一科？为什么？',
            '你平时喜欢看什么书？',
            '用英语介绍一下自己',
            '1+1等于几？2+3呢？'
        ]
    },
    'holistic': {
        'name': '全人型学校',
        'examples': '英华 / TSL / 协恩',
        'characteristics': [
            '注重全面发展不仅仅是学业',
            '重视艺术、体育和课外活动',
            '喜欢有创意的孩子',
            '关注社交能力和情绪管理'
        ],
        'tips': [
            '展示你的多方面兴趣和才能',
            '准备好分享你的爱好和课外活动',
            '表现出团队合作精神',
            '展示创意和想象力'
        ],
        'common_questions': [
            '你有什么爱好？',
            '你最擅长什么？',
            '你喜欢和同学一起做什么？',
            '如果可以变成一种动物，你想变成什么？'
        ]
    },
    'international': {
        'name': '国际型学校',
        'examples': 'CKY / 港同 / 宣道',
        'characteristics': [
            '主要使用英语教学',
            '重视国际视野',
            '面试可能全英文进行',
            '注重创意和批判性思维'
        ],
        'tips': [
            '英语是关键，必须熟练掌握',
            '练习用英语回答日常问题',
            '展示你对不同文化的了解',
            '表现出开放和包容的态度'
        ],
        'common_questions': [
            'What is your name?',
            'What do you like to do?',
            'Can you introduce yourself in English?',
            'What country would you like to visit?'
        ]
    },
    'traditional': {
        'name': '传统名校',
        'examples': 'KTS / SFA / 玛利诺',
        'characteristics': [
            '注重学业成绩和学术基础',
            '重视中文能力',
            '可能有笔试题',
            '看重学习态度和习惯'
        ],
        'tips': [
            '准备好中英文自我介绍',
            '练习简单的中英文对话',
            '展示良好的学习习惯',
            '表现出对学校的向往和尊重'
        ],
        'common_questions': [
            '你叫什么名字？',
            '你今年几岁？',
            '你读哪所幼稚园？',
            '你为什么想来我们学校？'
        ]
    }
}

# 家长准备指南
PARENT_GUIDE = {
    'title': '家长面试准备指南',
    'sections': [
        {
            'title': '面试前准备',
            'icon': 'event_note',
            'tips': [
                {'title': '了解学校', 'content': '深入了解目标学校的教育理念、课程特色和面试风格。'},
                {'title': '准备资料', 'content': '准备好孩子的幼稚园推荐信、作品集、获奖证书等。'},
                {'title': '模拟练习', 'content': '在家和孩子进行模拟面试，熟悉流程。'},
                {'title': '心理建设', 'content': '帮助孩子放松，不要给予太大压力。'},
            ]
        },
        {
            'title': '当天注意事项',
            'icon': 'today',
            'tips': [
                {'title': '提前到场', 'content': '预留充足时间，避免迟到影响孩子心情。'},
                {'title': '注意着装', 'content': '家长也要穿着得体，展示对面试的重视。'},
                {'title': '保持冷静', 'content': '家长不要过度紧张，你的情绪会影响孩子。'},
                {'title': '正面鼓励', 'content': '出发前给孩子正面的鼓励和拥抱。'},
            ]
        },
        {
            'title': '常见家长问答',
            'icon': 'question_answer',
            'tips': [
                {'title': '为什么选择我们学校？', 'content': '表达对学校的了解和认可，强调与孩子特性的匹配。'},
                {'title': '孩子的优点和缺点？', 'content': '如实但正面地介绍，突出优点，提及可改进的地方。'},
                {'title': '如何配合学校教育？', 'content': '表达愿意积极参与家校合作的态度。'},
                {'title': '对孩子的期望？', 'content': '合理期望，注重全面发展而非单一成绩。'},
            ]
        },
    ]
}


def get_etiquette_guide():
    """获取面试礼仪指南"""
    return INTERVIEW_ETIQUETTE


def get_school_strategy(school_type):
    """获取特定学校类型的攻略"""
    return SCHOOL_STRATEGIES.get(school_type, {})


def get_all_school_strategies():
    """获取所有学校类型攻略"""
    return SCHOOL_STRATEGIES


def get_parent_guide():
    """获取家长准备指南"""
    return PARENT_GUIDE
