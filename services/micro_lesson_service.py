"""
AI Micro Lesson Service
Handles AI-powered micro lesson generation and management.
"""

import json
import random
from datetime import datetime, date, timedelta
from services.ai_generator import call_minimax_api


def generate_micro_lesson(user_profile, topic, difficulty='easy', duration=60):
    """
    Generate an AI-powered micro lesson based on user profile and topic.

    Args:
        user_profile: dict - User/child profile information
        topic: str - The topic for the micro lesson
        difficulty: str - 'easy', 'medium', or 'hard'
        duration: int - Duration in seconds (60, 90, 120, 180)

    Returns:
        dict - Generated micro lesson content
    """
    child_name = user_profile.get('child_name', '小朋友')
    child_age = user_profile.get('child_age', 6)

    # Determine language based on profile
    language = user_profile.get('preferred_language', 'zh')

    # Build prompt for micro lesson generation
    if language == 'en':
        prompt = _build_english_prompt(child_name, child_age, topic, difficulty, duration)
    else:
        prompt = _build_chinese_prompt(child_name, child_age, topic, difficulty, duration)

    try:
        response = call_minimax_api(
            prompt=prompt,
            system_prompt="你是一个专业的儿童教育内容专家，专门为小学生创建有趣、简洁的微课内容。微课时长控制在1-3分钟，内容要生动有趣，适合儿童理解。"
        )

        # Parse the response to extract lesson content
        lesson_data = _parse_lesson_response(response, topic, difficulty, duration)

        return lesson_data
    except Exception as e:
        print(f"Error generating micro lesson: {e}")
        # Return fallback content
        return _get_fallback_lesson(topic, difficulty, duration, language)


def _build_chinese_prompt(child_name, child_age, topic, difficulty, duration):
    """Build Chinese prompt for micro lesson generation."""
    duration_desc = {
        60: "1分钟",
        90: "1分半钟",
        120: "2分钟",
        180: "3分钟"
    }.get(duration, "1-2分钟")

    difficulty_desc = {
        'easy': "简单有趣，适合初学者",
        'medium': "中等难度，稍有挑战",
        'hard': "较难，需要动脑筋"
    }.get(difficulty, "简单有趣")

    return f"""请为一位{child_age}岁的孩子创建一个{duration_desc}的微课，主题是"{topic}"。
难度：{difficulty_desc}

要求：
1. 内容要生动有趣，符合儿童认知水平
2. 语言简洁明了，易于理解
3. 包含适当的互动元素
4. 可以包含小故事或生活中的例子

请用JSON格式返回，包含以下字段：
- title: 课程标题（简短有趣）
- title_en: 英文标题
- description: 课程简介（1-2句话）
- content: 课程正文内容（适合{duration_desc}朗读的量）
- key_points: 3个要点（数组）
- quiz: 2个简单问题（可选）
"""


def _build_english_prompt(child_name, child_age, topic, difficulty, duration):
    """Build English prompt for micro lesson generation."""
    duration_desc = {
        60: "1 minute",
        90: "1.5 minutes",
        120: "2 minutes",
        180: "3 minutes"
    }.get(duration, "1-2 minutes")

    difficulty_desc = {
        'easy': "simple and fun for beginners",
        'medium': "moderate difficulty with some challenge",
        'hard': "challenging, requires thinking"
    }.get(difficulty, "simple and fun")

    return f"""Create a {duration_desc} micro lesson for a {child_age}-year-old child about "{topic}".
Difficulty: {difficulty_desc}

Requirements:
1. Content should be fun and engaging, appropriate for children's understanding
2. Clear and concise language
3. Include interactive elements
4. Can include small stories or everyday examples

Return in JSON format with these fields:
- title: Lesson title (short and fun)
- title_en: English title
- description: Brief introduction (1-2 sentences)
- content: Main lesson content (suitable for {duration_desc} reading)
- key_points: 3 key points (array)
- quiz: 2 simple questions (optional)
"""


def _parse_lesson_response(response, topic, difficulty, duration):
    """Parse AI response into structured lesson data."""
    try:
        # Try to extract JSON from response
        if isinstance(response, str):
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
            else:
                data = {'content': response}
        else:
            data = response

        return {
            'title': data.get('title', f'{topic}微课'),
            'title_en': data.get('title_en', topic),
            'description': data.get('description', f'学习{topic}的有趣微课'),
            'content': data.get('content', ''),
            'key_points': data.get('key_points', []),
            'quiz': data.get('quiz', []),
            'topic': topic,
            'difficulty': difficulty,
            'duration_seconds': duration,
            'status': 'ready'
        }
    except Exception as e:
        print(f"Error parsing lesson response: {e}")
        return _get_fallback_lesson(topic, difficulty, duration, 'zh')


def _get_fallback_lesson(topic, difficulty, duration, language):
    """Get fallback lesson content when AI generation fails."""
    if language == 'en':
        return {
            'title': f"Learn About {topic}",
            'title_en': f"Learn About {topic}",
            'description': f"A fun mini lesson about {topic}!",
            'content': f"Today we're going to learn about {topic}! {topic} is really interesting and important. Let's explore together!",
            'key_points': [
                f"{topic} is an interesting topic",
                "We can learn many things about it",
                "Let's practice together!"
            ],
            'quiz': [],
            'topic': topic,
            'difficulty': difficulty,
            'duration_seconds': duration,
            'status': 'ready'
        }
    else:
        return {
            'title': f'{topic}微课',
            'title_en': f'Learn About {topic}',
            'description': f'学习{topic}的有趣微课！',
            'content': f'今天我们要学习{topic}！{topic}是一个非常有趣的话题。让我们一起来探索吧！',
            'key_points': [
                f'{topic}是一个有趣的话题',
                '我们可以学到很多关于它的知识',
                '让我们一起练习吧！'
            ],
            'quiz': [],
            'topic': topic,
            'difficulty': difficulty,
            'duration_seconds': duration,
            'status': 'ready'
        }


def generate_quick_practice(user_profile, topic, difficulty='easy'):
    """
    Generate a quick Q&A practice (60 seconds).

    Args:
        user_profile: dict - User profile
        topic: str - Topic for practice
        difficulty: str - Difficulty level

    Returns:
        dict - Quick practice questions
    """
    child_name = user_profile.get('child_name', '小朋友')
    language = user_profile.get('preferred_language', 'zh')

    if language == 'en':
        prompt = f"""Create a 60-second quick Q&A practice about "{topic}" for a child.
Generate 3-5 quick questions with answers.

Return JSON format:
- questions: array of {{question, answer, options (if multiple choice)}}
- time_limit: 60
"""
    else:
        prompt = f"""创建一个关于"{topic}"的60秒快速问答练习，适合儿童。
生成3-5个快速问答题目。

返回JSON格式：
- questions: 数组，每个元素包含question(问题), answer(答案), options(选项，如果是选择题)
- time_limit: 60
"""

    try:
        response = call_minimax_api(
            prompt=prompt,
            system_prompt="你是一个儿童教育专家，创建快速有趣的问答练习。"
        )

        # Parse response
        practice_data = _parse_practice_response(response)
        practice_data['session_type'] = 'quick_qa'
        practice_data['time_limit_seconds'] = 60
        return practice_data
    except Exception as e:
        print(f"Error generating quick practice: {e}")
        return _get_fallback_practice(topic, 'quick_qa', 60, language)


def generate_voice_repeat_practice(user_profile, lesson_id, topic):
    """
    Generate a voice repeat practice (90 seconds).

    Args:
        user_profile: dict - User profile
        lesson_id: int - Related lesson ID
        topic: str - Topic for practice

    Returns:
        dict - Voice repeat practice content
    """
    language = user_profile.get('preferred_language', 'zh')

    # Script for child to repeat
    if language == 'en':
        script = f"Hello! Today we're going to practice speaking about {topic}. Listen carefully and repeat after me!"
        prompt = f"""Create a 90-second voice repeat exercise about "{topic}".
Include sentences for the child to repeat after hearing.
Return JSON format:
- sentences: array of sentences to repeat
- audio_text: the text to convert to speech for the child to listen to
- time_limit: 90
"""
    else:
        script = f"你好！今天我们要练习关于{topic}的跟读。仔细听，然后跟我读！"
        prompt = f"""创建一个关于"{topic}"的90秒语音跟读练习。
包含让孩子听后跟读的句子。
返回JSON格式：
- sentences: 要跟读的句子数组
- audio_text: 要转换成语音让孩子听的文本
- time_limit: 90
"""

    try:
        response = call_minimax_api(
            prompt=prompt,
            system_prompt="你是一个儿童语言教育专家，创建跟读练习内容。"
        )

        practice_data = _parse_voice_response(response)
        practice_data['session_type'] = 'voice_repeat'
        practice_data['lesson_id'] = lesson_id
        practice_data['time_limit_seconds'] = 90
        practice_data['audio_text'] = script + " " + practice_data.get('audio_text', '')
        return practice_data
    except Exception as e:
        print(f"Error generating voice repeat: {e}")
        return _get_fallback_practice(topic, 'voice_repeat', 90, language)


def generate_scenario_simulation(user_profile, topic, difficulty='easy'):
    """
    Generate a scenario simulation practice (120 seconds).

    Args:
        user_profile: dict - User profile
        topic: str - Topic for simulation
        difficulty: str - Difficulty level

    Returns:
        dict - Scenario simulation content
    """
    language = user_profile.get('preferred_language', 'zh')

    if language == 'en':
        prompt = f"""Create a 120-second scenario simulation about "{topic}" for a child.
Create a realistic scenario where the child needs to respond.
Return JSON format:
- scenario: description of the situation
- role: child's role in the scenario
- context: background information
- suggested_responses: 2-3 example responses
- evaluation_criteria: how to evaluate the response
- time_limit: 120
"""
    else:
        prompt = f"""创建一个关于"{topic}"的120秒情景模拟练习，适合儿童。
创建一个需要孩子回应的真实场景。
返回JSON格式：
- scenario: 场景描述
- role: 孩子的角色
- context: 背景信息
- suggested_responses: 2-3个示例回复
- evaluation_criteria: 如何评估回复
- time_limit: 120
"""

    try:
        response = call_minimax_api(
            prompt=prompt,
            system_prompt="你是一个儿童教育专家，创建情景模拟练习。"
        )

        practice_data = _parse_scenario_response(response)
        practice_data['session_type'] = 'scenario_simulation'
        practice_data['time_limit_seconds'] = 120
        return practice_data
    except Exception as e:
        print(f"Error generating scenario simulation: {e}")
        return _get_fallback_practice(topic, 'scenario_simulation', 120, language)


def _parse_practice_response(response):
    """Parse practice response from AI."""
    try:
        if isinstance(response, str):
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        return response if isinstance(response, dict) else {'questions': []}
    except:
        return {'questions': []}


def _parse_voice_response(response):
    """Parse voice repeat response from AI."""
    try:
        if isinstance(response, str):
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        return response if isinstance(response, dict) else {'sentences': []}
    except:
        return {'sentences': []}


def _parse_scenario_response(response):
    """Parse scenario simulation response from AI."""
    try:
        if isinstance(response, str):
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        return response if isinstance(response, dict) else {}
    except:
        return {}


def _get_fallback_practice(topic, practice_type, time_limit, language):
    """Get fallback practice when AI generation fails."""
    if language == 'en':
        return {
            'session_type': practice_type,
            'time_limit_seconds': time_limit,
            'topic': topic,
            'questions': [
                {'question': f'What is {topic}?', 'answer': f'{topic} is interesting!'}
            ] if practice_type == 'quick_qa' else [],
            'sentences': [f"Let's learn about {topic}!"] if practice_type == 'voice_repeat' else [],
            'scenario': {
                'scenario': f'Imagine you are talking about {topic}',
                'role': 'Student',
                'context': f'We are learning about {topic} today'
            } if practice_type == 'scenario_simulation' else {}
        }
    else:
        return {
            'session_type': practice_type,
            'time_limit_seconds': time_limit,
            'topic': topic,
            'questions': [
                {'question': f'什么是{topic}？', 'answer': f'{topic}很有趣！'}
            ] if practice_type == 'quick_qa' else [],
            'sentences': [f'让我们学习{topic}！'] if practice_type == 'voice_repeat' else [],
            'scenario': {
                'scenario': f'想象你在谈论{topic}',
                'role': '学生',
                'context': f'今天我们学习{topic}'
            } if practice_type == 'scenario_simulation' else {}
        }


def get_daily_tasks(user_id, user_profile, task_date=None):
    """
    Get or generate daily tasks for a user.

    Args:
        user_id: int - User ID
        user_profile: dict - User profile
        task_date: date - Date for tasks (default: today)

    Returns:
        list - List of daily tasks
    """
    from db.database import execute_query

    if task_date is None:
        task_date = date.today()

    # Check if tasks exist for this date
    query = """
        SELECT * FROM daily_tasks
        WHERE user_id = %s AND task_date = %s
        ORDER BY id
    """
    existing_tasks = execute_query(query, (user_id, task_date), fetch=True)

    if existing_tasks:
        return existing_tasks

    # Generate new tasks
    topics = user_profile.get('topics', ['science', 'math', 'language', 'arts', 'sports'])
    child_interests = user_profile.get('child_interests', [])

    # Create 3-5 tasks with difficulty gradient
    tasks = []

    # Task 1: Micro lesson (easy)
    tasks.append({
        'task_type': 'micro_lesson',
        'task_title': f"{random.choice(topics)}微课学习",
        'task_description': '观看并学习一个有趣的微课',
        'difficulty': 'easy',
        'duration_seconds': 60,
        'target_topic': random.choice(topics),
        'points': 10
    })

    # Task 2: Quick practice (easy-medium)
    tasks.append({
        'task_type': 'quick_practice',
        'task_title': '快速问答挑战',
        'task_description': '60秒快速回答问题',
        'difficulty': 'easy',
        'duration_seconds': 60,
        'target_topic': random.choice(topics),
        'points': 15
    })

    # Task 3: Voice repeat (medium)
    tasks.append({
        'task_type': 'voice_repeat',
        'task_title': '语音跟读练习',
        'task_description': '90秒跟读练习',
        'difficulty': 'medium',
        'duration_seconds': 90,
        'target_topic': random.choice(topics),
        'points': 20
    })

    # Task 4: Another micro lesson
    tasks.append({
        'task_type': 'micro_lesson',
        'task_title': f"{random.choice(topics)}进阶微课",
        'task_description': '学习进阶微课内容',
        'difficulty': 'medium',
        'duration_seconds': 120,
        'target_topic': random.choice(topics),
        'points': 15
    })

    # Task 5: Scenario simulation (hard)
    tasks.append({
        'task_type': 'scenario_simulation',
        'task_title': '情景模拟挑战',
        'task_description': '120秒情景模拟练习',
        'difficulty': 'hard',
        'duration_seconds': 120,
        'target_topic': random.choice(topics),
        'points': 25
    })

    # Insert tasks into database
    for task in tasks:
        query = """
            INSERT INTO daily_tasks
            (user_id, task_date, task_type, task_title, task_description,
             difficulty, duration_seconds, target_topic, points, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """
        execute_query(query, (
            user_id, task_date, task['task_type'], task['task_title'],
            task['task_description'], task['difficulty'], task['duration_seconds'],
            task['target_topic'], task['points']
        ))

    # Return the created tasks
    return execute_query(query, (user_id, task_date), fetch=True)


def complete_task(user_id, task_id, score=None):
    """Mark a daily task as completed."""
    from db.database import execute_query

    query = """
        UPDATE daily_tasks
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND id = %s
        RETURNING *
    """
    result = execute_query(query, (user_id, task_id), fetch=True)
    return result[0] if result else None


def get_user_lessons(user_id, limit=20, offset=0):
    """Get user's micro lessons."""
    from db.database import execute_query

    query = """
        SELECT * FROM micro_lessons
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    return execute_query(query, (user_id, limit, offset), fetch=True)


def save_micro_lesson(user_id, lesson_data):
    """Save a generated micro lesson to database."""
    from db.database import execute_query

    query = """
        INSERT INTO micro_lessons
        (user_id, title, title_en, description, content, duration_seconds,
         difficulty, topic, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    result = execute_query(query, (
        user_id,
        lesson_data.get('title'),
        lesson_data.get('title_en'),
        lesson_data.get('description'),
        lesson_data.get('content'),
        lesson_data.get('duration_seconds', 60),
        lesson_data.get('difficulty', 'easy'),
        lesson_data.get('topic'),
        lesson_data.get('status', 'ready')
    ), fetch=True)
    return result[0] if result else None


def record_practice_session(user_id, session_data):
    """Record a practice session."""
    from db.database import execute_query

    query = """
        INSERT INTO practice_sessions
        (user_id, session_type, topic_id, lesson_id, duration_seconds,
         time_limit_seconds, score, max_score, correct_count, total_count,
         answers, audio_url, transcript, feedback)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    result = execute_query(query, (
        user_id,
        session_data.get('session_type'),
        session_data.get('topic_id'),
        session_data.get('lesson_id'),
        session_data.get('duration_seconds'),
        session_data.get('time_limit_seconds'),
        session_data.get('score'),
        session_data.get('max_score'),
        session_data.get('correct_count', 0),
        session_data.get('total_count', 0),
        json.dumps(session_data.get('answers', [])),
        session_data.get('audio_url'),
        session_data.get('transcript'),
        session_data.get('feedback')
    ), fetch=True)
    return result[0] if result else None


def get_practice_history(user_id, session_type=None, limit=10):
    """Get user's practice session history."""
    from db.database import execute_query

    if session_type:
        query = """
            SELECT * FROM practice_sessions
            WHERE user_id = %s AND session_type = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return execute_query(query, (user_id, session_type, limit), fetch=True)
    else:
        query = """
            SELECT * FROM practice_sessions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return execute_query(query, (user_id, limit), fetch=True)


def update_lesson_progress(user_id, lesson_id, progress_percent, time_spent):
    """Update user's progress on a lesson."""
    from db.database import execute_query

    status = 'completed' if progress_percent >= 100 else 'in_progress'

    query = """
        INSERT INTO user_learning_progress
        (user_id, lesson_id, status, progress_percent, time_spent_seconds, last_position_seconds)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, lesson_id)
        DO UPDATE SET
            status = EXCLUDED.status,
            progress_percent = EXCLUDED.progress_percent,
            time_spent_seconds = user_learning_progress.time_spent_seconds + EXCLUDED.time_spent_seconds,
            last_position_seconds = EXCLUDED.last_position_seconds,
            updated_at = CURRENT_TIMESTAMP,
            completed_at = CASE WHEN EXCLUDED.status = 'completed' THEN CURRENT_TIMESTAMP ELSE user_learning_progress.completed_at END
        RETURNING *
    """
    result = execute_query(query, (
        user_id, lesson_id, status, progress_percent, time_spent, time_spent
    ), fetch=True)
    return result[0] if result else None
