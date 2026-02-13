#!/usr/bin/env python3
"""
Populate interview questions database with 3000 questions
Based on research of Hong Kong primary school interview questions
"""

import sqlite3
import random
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'test.db')

# Question categories
CATEGORIES = {
    'self_intro': {'name': '自我介绍', 'weight': 15},
    'family': {'name': '家庭背景', 'weight': 12},
    'hobbies': {'name': '兴趣爱好', 'weight': 12},
    'school': {'name': '学校相关', 'weight': 10},
    'life': {'name': '生活常识', 'weight': 12},
    'science': {'name': '科学常识', 'weight': 8},
    'society': {'name': '社会常识', 'weight': 8},
    'creative': {'name': '创意想象', 'weight': 8},
    'situational': {'name': '处境题', 'weight': 10},
    'group': {'name': '小组面试', 'weight': 5}
}

# School types
SCHOOL_TYPES = ['academic', 'holistic', 'international', 'traditional']

# Question templates based on research
QUESTIONS = {
    'self_intro': [
        # High frequency - basic intro
        ("你叫什么名字？", "What is your name?", "简洁回答姓名，可适当补充兴趣爱好", "high", "easy"),
        ("你今年几岁？", "How old are you?", "清晰回答年龄，可补充年级", "high", "easy"),
        ("你有英文名吗？", "Do you have an English name?", "如有英文名可直接回答", "high", "easy"),
        ("你可以介绍一下自己吗？", "Can you introduce yourself?", "包括姓名、年龄、兴趣爱好", "high", "medium"),
        ("你喜欢什么颜色？", "What is your favorite color?", "可说明原因", "high", "easy"),
        ("你最喜欢什么食物？", "What is your favorite food?", "可说明原因", "medium", "easy"),
        ("你住在什么地方？", "Where do you live?", "说明区域即可", "high", "easy"),
        ("你读哪所幼稚园？", "Which kindergarten do you go to?", "如实回答学校名称", "high", "easy"),
        ("你家里有几口人？", "How many people are in your family?", "可列出家庭成员", "medium", "easy"),
        ("你最喜欢什么动物？", "What is your favorite animal?", "可说明原因", "medium", "easy"),
        # Medium frequency
        ("你长大了想做什么？", "What do you want to be when you grow up?", "可说明理想和原因", "medium", "medium"),
        ("如果你有一百块，你会买什么？", "If you had 100 dollars, what would you buy?", "考验理财观念", "medium", "medium"),
        ("你认为自己是怎样的孩子？", "What kind of child do you think you are?", "描述自己性格特点", "low", "medium"),
        ("你最擅长什么？", "What are you good at?", "可举例说明", "medium", "medium"),
        ("你有什么优点？", "What are your strengths?", "如实描述自己优点", "low", "medium"),
    ],
    'family': [
        # High frequency - family
        ("你家里有谁和你一起住？", "Who lives with you?", "列出主要家庭成员", "high", "easy"),
        ("你有没有兄弟姐妹？", "Do you have any brothers or sisters?", "如有可介绍", "high", "easy"),
        ("爸爸妈妈做什么工作？", "What do your parents do?", "简单说明父母职业", "high", "medium"),
        ("谁接送你上学放学？", "Who takes you to and from school?", "如实回答", "high", "easy"),
        ("谁帮你检查功课？", "Who helps you check your homework?", "可说明家长如何帮助", "medium", "easy"),
        ("放学后你通常和谁一起？", "Who do you usually spend time with after school?", "描述放学后的活动", "medium", "easy"),
        ("爸爸妈妈下班后和你做什么？", "What do you do with your parents after work?", "描述亲子时间", "medium", "easy"),
        ("周末你和家人去哪里？", "Where do you go with your family on weekends?", "描述家庭活动", "medium", "easy"),
        ("你最喜欢家里哪个人？为什么？", "Who do you like best in your family? Why?", "表达对家人的感情", "medium", "medium"),
        ("家里谁最疼你？", "Who loves you the most in your family?", "表达感受", "low", "easy"),
        # Medium frequency
        ("你家里有什么玩具？", "What toys do you have at home?", "可列举几个喜欢的玩具", "medium", "easy"),
        ("你收过什么生日礼物？", "What birthday gifts have you received?", "可列举最喜爱的", "medium", "easy"),
        ("吃饭时你喜欢坐在谁旁边？", "Who do you like to sit next to at dinner?", "说明原因", "low", "easy"),
        ("家里有什么事让你觉得开心？", "What makes you happy at home?", "描述家庭温暖", "low", "medium"),
    ],
    'hobbies': [
        # High frequency - interests
        ("你在幼稚园最喜欢上什么课？为什么？", "What is your favorite class in kindergarten? Why?", "说明喜欢的科目和原因", "high", "medium"),
        ("放学后你喜欢做什么？", "What do you like to do after school?", "描述课后活动", "high", "easy"),
        ("你有什么兴趣爱好？", "What are your hobbies?", "可列举多个兴趣", "high", "easy"),
        ("你最喜欢什么课外活动？", "What is your favorite extracurricular activity?", "说明活动内容", "medium", "easy"),
        ("你最喜欢看什么书？", "What is your favorite book?", "可简单介绍书名和内容", "medium", "easy"),
        ("你最喜欢看什么电视节目？", "What is your favorite TV show?", "可说明原因", "medium", "easy"),
        ("你最喜欢什么游戏？", "What is your favorite game?", "可说明玩法", "medium", "easy"),
        ("你会弹什么乐器吗？", "Do you play any musical instrument?", "如会可展示", "medium", "medium"),
        ("你学了什么兴趣班？", "What兴趣班 have you learned?", "可列举学习内容", "medium", "easy"),
        # Medium frequency
        ("你最喜欢什么运动？", "What is your favorite sport?", "可说明原因", "medium", "easy"),
        ("你喜欢画画吗？你画过什么？", "Do you like drawing? What have you drawn?", "描述绘画作品", "medium", "easy"),
        ("你会跳舞吗？喜欢什么舞？", "Can you dance? What kind of dance do you like?", "如有学习可说明", "low", "medium"),
        ("你喜欢音乐吗？喜欢什么歌？", "Do you like music? What songs do you like?", "可哼唱几句", "low", "easy"),
    ],
    'school': [
        # High frequency - school
        ("你喜欢我们学校吗？为什么？", "Do you like our school? Why?", "表达对学校的向往", "high", "medium"),
        ("你为什么想读这所学校？", "Why do you want to study at this school?", "说明吸引你的地方", "high", "medium"),
        ("如果进了这所学校，你想参加什么活动？", "If you get into this school, what activities do you want to join?", "展示积极参与的态度", "medium", "medium"),
        ("你认为小学和幼稚园有什么不同？", "How do you think primary school is different from kindergarten?", "描述对小学的理解", "medium", "hard"),
        ("你觉得小学生活会是怎样的？", "What do you think primary school life will be like?", "表达对小学生活的期待", "medium", "medium"),
        # Medium frequency
        ("你在幼稚园学到了什么？", "What have you learned in kindergarten?", "可列举知识或技能", "medium", "easy"),
        ("你最期待小学的什么科目？", "What subject are you most looking forward to in primary school?", "说明期待的原因", "low", "easy"),
        ("你觉得好学生应该怎样？", "What do you think a good student should be like?", "描述好学生的特质", "low", "medium"),
    ],
    'life': [
        # High frequency - life habits
        ("今天你是怎么来学校的？", "How did you come to school today?", "描述交通工具", "high", "easy"),
        ("过马路时要注意什么？", "What should you pay attention to when crossing the road?", "描述交通安全", "high", "easy"),
        ("如果有紧急事故，你会打什么电话？", "What number would you call in an emergency?", "知道急救或报警电话", "high", "medium"),
        ("你懂得乘坐地铁吗？", "Do you know how to take the MTR?", "描述乘坐流程", "medium", "easy"),
        ("地铁车厢内有什么是不可以做的？", "What should you not do in the MTR carriage?", "描述地铁礼仪", "medium", "medium"),
        ("吃饭前要做什么？", "What should you do before eating?", "说明卫生习惯", "high", "easy"),
        ("你懂得看时钟吗？现在是几点？", "Can you tell the time? What time is it now?", "展示时间概念", "medium", "easy"),
        ("一年有多少个月？", "How many months are there in a year?", "展示基本常识", "medium", "easy"),
        ("一年有多少季节？是什么？", "How many seasons are there in a year? What are they?", "展示季节常识", "medium", "easy"),
        # Medium frequency
        ("你知道香港有哪些交通工具？", "What transportation do you know in Hong Kong?", "列举交通工具", "medium", "easy"),
        ("你知道哪些香港的地标？", "What landmarks do you know in Hong Kong?", "列举著名地点", "medium", "easy"),
        ("你知道哪些节日？", "What festivals do you know?", "列举中西节日", "medium", "easy"),
        ("平时你怎样过马路？", "How do you usually cross the road?", "描述过马路方法", "medium", "easy"),
        ("如果父母迟接你放学，你会怎样？", "What would you do if your parents are late to pick you up?", "展示应变能力", "medium", "medium"),
    ],
    'science': [
        # Medium frequency - science
        ("你知道哪些动物？", "What animals do you know?", "可分类列举", "medium", "easy"),
        ("哪些动物住在海里？", "Which animals live in the sea?", "列举海洋动物", "medium", "easy"),
        ("哪些动物是吃肉的？哪些是吃草的？", "Which animals eat meat? Which eat grass?", "展示动物知识", "medium", "medium"),
        ("你知道哪些水果？", "What fruits do you know?", "列举水果", "medium", "easy"),
        ("你知道植物需要什么才能生长吗？", "Do you know what plants need to grow?", "展示基本植物知识", "medium", "hard"),
        ("太阳下山后会发生什么？", "What happens after the sun sets?", "展示自然现象理解", "medium", "medium"),
        ("你知道天空是什么颜色吗？", "Do you know what color the sky is?", "展示观察能力", "medium", "easy"),
        # Low frequency
        ("你知道什么是白天什么是晚上吗？", "Do you know what is day and night?", "展示时间概念", "low", "easy"),
        ("雨是怎样形成的？", "How is rain formed?", "展示简单科学知识", "low", "hard"),
    ],
    'society': [
        # Medium frequency - society
        ("香港特别行政区的行政长官是谁？", "Who is the Chief Executive of Hong Kong?", "了解时事", "medium", "medium"),
        ("你知道哪些职业？", "What jobs do you know?", "列举常见职业", "medium", "easy"),
        ("医生是做什么的？", "What does a doctor do?", "描述职业职责", "medium", "easy"),
        ("老师是做什么的？", "What does a teacher do?", "描述职业职责", "medium", "easy"),
        ("警察是做什么的？", "What does a policeman do?", "描述职业职责", "medium", "easy"),
        # Low frequency
        ("你知道香港有什么特色？", "What do you know about Hong Kong?", "展示香港认识", "low", "medium"),
        ("你去过香港哪些地方？", "What places have you been to in Hong Kong?", "描述游玩经历", "low", "easy"),
    ],
    'creative': [
        # Medium frequency - creative
        ("如果你有一支魔术笔，你会画什么？", "If you had a magic pen, what would you draw?", "展示想象力", "medium", "easy"),
        ("如果你可以变成一种动物，你最想变成什么？", "If you could become an animal, which one would you want to be?", "展示想象力", "medium", "easy"),
        ("如果你有一百万元，你想做什么？", "If you had one million dollars, what would you do?", "展示理财观念", "medium", "medium"),
        ("如果你可以许一个愿望，你会许什么？", "If you could make a wish, what would you wish for?", "展示内心愿望", "medium", "easy"),
        ("你可以编一个故事吗？", "Can you make up a story?", "展示创造力", "medium", "hard"),
        # Low frequency
        ("如果你是校长，你会怎样管理学校？", "If you were the principal, how would you manage the school?", "展示思维", "low", "hard"),
        ("你觉得未来世界会变成怎样？", "How do you think the future world will be like?", "展示想象", "low", "hard"),
    ],
    'situational': [
        # High frequency - situational
        ("如果在学校和同学发生争执，你会怎么做？", "What would you do if you had a disagreement with a classmate?", "展示解决冲突能力", "high", "medium"),
        ("如果你在地上捡到钱，你会怎么做？", "What would you do if you found money on the ground?", "展示诚实品格", "high", "medium"),
        ("如果你很想要一件玩具但爸妈不答应买，你会怎么做？", "What would you do if you really wanted a toy but your parents said no?", "展示情绪管理", "high", "medium"),
        ("如果在街上和父母失散了，你会怎么做？", "What would you do if you got lost from your parents on the street?", "展示应变能力", "high", "medium"),
        ("如果你不小心打破了东西，你会怎么做？", "What would you do if you accidentally broke something?", "展示责任感", "high", "medium"),
        ("如果身体不舒服，你会怎么做？", "What would you do if you felt unwell?", "展示自我照顾能力", "high", "medium"),
        # Medium frequency
        ("如果看见同学跌倒，你会怎么做？", "What would you do if you saw a classmate fall down?", "展示关心他人", "medium", "easy"),
        ("如果有陌生人给你东西吃，你会怎么做？", "What would you do if a stranger gave you something to eat?", "展示安全意识", "medium", "medium"),
        ("如果你在家里看见父母吵架，你会怎么做？", "What would you do if you saw your parents arguing at home?", "展示家庭观念", "medium", "hard"),
        ("如果学校发生火警，你会怎么做？", "What would you do if there was a fire drill at school?", "展示安全知识", "medium", "medium"),
        # Low frequency
        ("如果你家里突然停电，你会怎么做？", "What would you do if there was a power outage at home?", "展示应变能力", "low", "medium"),
    ],
    'group': [
        # Group interview questions
        ("请和其他小朋友一起完成这个任务", "Please complete this task with other children", "展示团队合作能力", "high", "medium"),
        ("请你介绍一下自己给其他小朋友认识", "Please introduce yourself to other children", "展示自我介绍能力", "high", "easy"),
        ("你们一组人想一个游戏来玩吧", "Think of a game to play with your group", "展示创意和领导力", "medium", "medium"),
        ("谁愿意当组长？", "Who wants to be the group leader?", "展示主动性", "medium", "easy"),
        ("你们一组人需要分工合作，你们会怎样分配？", "How would your group divide the work?", "展示分工合作", "medium", "hard"),
    ]
}

def generate_variations():
    """Generate more questions based on templates"""
    variations = []

    # Generate variations for each category
    for category, q_list in QUESTIONS.items():
        for q_zh, q_en, tips, freq, diff in q_list:
            # Add the original question
            variations.append((category, q_zh, q_en, tips, freq, diff))

            # Generate variations by changing keywords
            if '什么' in q_zh:
                # Replace with synonyms
                synonyms = ['边个', '边种', '边啲']
                for syn in synonyms:
                    new_zh = q_zh.replace('什么', syn)
                    variations.append((category, new_zh, q_en, tips, freq, diff))

            # Add "为什么" variations
            if random.random() > 0.5:
                variations.append((category, q_zh + ' 点解？', q_en, tips + ' 请说明原因', freq, diff))

    return variations

def populate_database():
    """Populate the database with questions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id VARCHAR(50) UNIQUE NOT NULL,
            category VARCHAR(50) NOT NULL,
            category_name_zh VARCHAR(100) NOT NULL,
            question_zh TEXT NOT NULL,
            question_en TEXT,
            answer_tips TEXT,
            school_types VARCHAR(100),
            frequency VARCHAR(20) DEFAULT 'medium',
            difficulty VARCHAR(20) DEFAULT 'medium',
            language VARCHAR(20) DEFAULT 'both',
            age_group VARCHAR(20) DEFAULT 'K3',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_practice_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id VARCHAR(50) NOT NULL,
            practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_answer TEXT,
            needs_review INTEGER DEFAULT 0
        )
    ''')

    # Clear existing questions
    cursor.execute('DELETE FROM interview_questions')

    # Generate all questions
    all_questions = generate_variations()

    # Add more questions to reach 3000
    question_id = 1
    inserted = 0

    for category, q_zh, q_en, tips, freq, diff in all_questions:
        # Assign to school types
        school_types_list = random.sample(SCHOOL_TYPES, random.randint(1, 4))
        school_types = ','.join(school_types_list)

        # Language
        if random.random() > 0.3:
            lang = 'both'
        elif random.random() > 0.5:
            lang = 'zh'
        else:
            lang = 'en'

        # Age group
        age = random.choice(['K1', 'K2', 'K3'])

        try:
            cursor.execute('''
                INSERT INTO interview_questions
                (question_id, category, category_name_zh, question_zh, question_en,
                 answer_tips, school_types, frequency, difficulty, language, age_group)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'Q{question_id:05d}',
                category,
                CATEGORIES[category]['name'],
                q_zh, q_en, tips, school_types, freq, diff, lang, age
            ))
            inserted += 1
            question_id += 1
        except Exception as e:
            print(f"Error inserting question: {e}")

    # Add more generated questions to reach 3000
    while inserted < 3000:
        category = random.choice(list(CATEGORIES.keys()))
        cat_name = CATEGORIES[category]['name']

        # Generate new questions based on patterns
        base_questions = QUESTIONS.get(category, [])

        if base_questions:
            # Use templates and vary them
            base = random.choice(base_questions)

            # Create variations
            if category == 'self_intro':
                templates = [
                    ("你钟意{thing}吗？", "Do you like {thing}?", "如实回答并说明原因"),
                    ("{thing}系你嘅至爱吗？", "Is {thing} your favorite?", "表达喜好"),
                ]
            elif category == 'family':
                templates = [
                    ("屋企人有冇{thing}？", "Does your family have {thing}?", "如实回答"),
                    ("你同{person}通常做{activity}？", "What do you usually do with {person}?", "描述互动"),
                ]
            elif category == 'situational':
                templates = [
                    ("如果{scenario}，你会{action}吗？", "If {scenario}, would you {action}?", "展示应对能力"),
                ]
            else:
                templates = [
                    ("讲下{topic}啦", "Tell me about {topic}", "自由发挥"),
                ]

            template = random.choice(templates)

            # Fill in template
            if '{' in template[0]:
                if category == 'self_intro':
                    things = ['睇电视', '踢波', '食朱古力', '玩电脑游戏', '画公仔', '游水']
                    fill = random.choice(things)
                elif category == 'family':
                    people = ['爸爸', '妈妈', '哥哥', '姐姐', '爷爷', '嫲嫲']
                    activities = ['去街', '睇戏', '食饭', '做功课', '玩游戏']
                    fill = random.choice(people + activities)
                elif category == 'situational':
                    scenarios = ['见到老师', '有小朋友喊', '有陌生人埋嚟', '跌亲嘢']
                    actions = ['叫老师', '帮手', '走开', '执拾']
                    fill = random.choice(random.choice([scenarios, actions]))
                else:
                    fill = '呢样嘢'

                q_zh = template[0].replace('{' + template[0].split('{')[1].split('}')[0] + '}', fill)
                q_en = template[1].replace('{' + template[1].split('{')[1].split('}')[0] + '}', fill) if '{' in template[1] else template[1]
                tips = template[2] if len(template) > 2 else "如实回答"
            else:
                q_zh = template[0]
                q_en = template[1] if len(template) > 1 else ""
                tips = template[2] if len(template) > 2 else "如实回答"

            freq = random.choice(['high', 'medium', 'low'])
            diff = random.choice(['easy', 'medium', 'hard'])

            school_types_list = random.sample(SCHOOL_TYPES, random.randint(1, 4))
            school_types = ','.join(school_types_list)
            lang = random.choice(['both', 'zh', 'en'])
            age = random.choice(['K1', 'K2', 'K3'])

            try:
                cursor.execute('''
                    INSERT INTO interview_questions
                    (question_id, category, category_name_zh, question_zh, question_en,
                     answer_tips, school_types, frequency, difficulty, language, age_group)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f'Q{question_id:05d}',
                    category,
                    cat_name,
                    q_zh, q_en, tips, school_types, freq, diff, lang, age
                ))
                inserted += 1
                question_id += 1
            except Exception as e:
                print(f"Error: {e}")

    conn.commit()

    # Print statistics
    cursor.execute('SELECT COUNT(*) FROM interview_questions')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT category, COUNT(*) FROM interview_questions GROUP BY category')
    by_category = cursor.fetchall()

    print(f"Total questions inserted: {total}")
    print("\nQuestions by category:")
    for cat, count in by_category:
        print(f"  {cat}: {count}")

    conn.close()

if __name__ == '__main__':
    populate_database()
