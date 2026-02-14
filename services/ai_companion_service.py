"""
AI Companion Service for AI Tutor Application.
Provides business logic for AI companion growth system.
"""

import os
import uuid
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

# Import database functions
from db.database import execute_query, get_connection


# ============ Companion CRUD Operations ============

def create_user_companion(user_id, name, character_type='dinosaur'):
    """Create a new AI companion for a user."""
    query = """
        INSERT INTO ai_companions (user_id, name, character_type, level, experience, total_experience, consecutive_days, last_active_date, current_mood, unlocked_skills)
        VALUES (%s, %s, %s, 1, 0, 0, 0, CURRENT_DATE, 'happy', '[]')
        RETURNING id, user_id, name, character_type, level, experience, total_experience, consecutive_days, last_active_date, current_mood, unlocked_skills, created_at;
    """
    result = execute_query(query, (user_id, name, character_type), fetch=True)
    if result:
        # Also create initial daily tasks for the user
        create_daily_tasks(user_id)
    return result[0] if result else None


def get_user_companion(user_id):
    """Get AI companion for a user."""
    query = """
        SELECT * FROM ai_companions WHERE user_id = %s;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None


def get_companion_by_id(companion_id):
    """Get AI companion by ID."""
    query = "SELECT * FROM ai_companions WHERE id = %s;"
    result = execute_query(query, (companion_id,), fetch=True)
    return result[0] if result else None


def update_companion(companion_id, **kwargs):
    """Update companion fields."""
    allowed_fields = ['name', 'character_type', 'level', 'experience', 'total_experience',
                     'consecutive_days', 'last_active_date', 'current_mood', 'unlocked_skills']

    updates = []
    params = []

    for field in allowed_fields:
        if field in kwargs:
            updates.append(f"{field} = %s")
            params.append(kwargs[field])

    if not updates:
        return None

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(companion_id)

    query = f"""
        UPDATE ai_companions
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING *;
    """
    result = execute_query(query, params, fetch=True)
    return result[0] if result else None


def create_or_get_user_companion(user_id, name=None, character_type='dinosaur'):
    """Create or get user companion."""
    companion = get_user_companion(user_id)
    if companion:
        # Update consecutive days if needed
        companion = update_streak(user_id)
        return companion

    # Create new companion
    name = name or get_default_name(character_type)
    return create_user_companion(user_id, name, character_type)


def get_default_name(character_type):
    """Get default name based on character type."""
    names = {
        'dinosaur': '小智',
        'robot': '小机',
        'rabbit': '小兔'
    }
    return names.get(character_type, '小伙伴')


# ============ Experience Operations ============

def add_experience(user_id, experience_type, amount, reason=None):
    """Add experience to companion and check for level up."""
    companion = get_user_companion(user_id)
    if not companion:
        return None

    previous_experience = companion['experience']
    previous_level = companion['level']
    new_experience = previous_experience + amount
    new_total_experience = companion['total_experience'] + amount

    # Get level info
    level_info = get_level_info(previous_level + 1) if previous_level < 10 else None

    # Check for level up
    level_up = False
    current_level = previous_level
    new_level_info = None

    while current_level < 10:
        next_level_info = get_level_info(current_level + 1)
        if next_level_info and new_total_experience >= next_level_info['required_experience']:
            current_level += 1
            level_up = True
            new_level_info = next_level_info
        else:
            break

    # Calculate experience for current level
    current_level_info = get_level_info(current_level)
    level_start_exp = current_level_info['required_experience'] if current_level_info else 0
    next_level_exp = get_level_info(current_level + 1)['required_experience'] if current_level < 10 else new_total_experience

    experience_for_current_level = new_total_experience - level_start_exp
    experience_needed = next_level_exp - level_start_exp if next_level_exp > level_start_exp else 1

    # Update companion
    unlocked_skills = companion['unlocked_skills']
    if isinstance(unlocked_skills, str):
        import json
        unlocked_skills = json.loads(unlocked_skills)

    # Add new skills if leveled up
    if level_up and new_level_info:
        for skill in new_level_info.get('unlocked_skills', []):
            if skill not in unlocked_skills:
                unlocked_skills.append(skill)

    # Log experience
    log_experience(user_id, companion['id'], experience_type, amount, reason)

    # Update companion record
    query = """
        UPDATE ai_companions
        SET experience = %s, total_experience = %s, level = %s, unlocked_skills = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *;
    """
    result = execute_query(query, (experience_for_current_level, new_total_experience, current_level,
                                   unlocked_skills, companion['id']), fetch=True)

    # Update mood based on recent activity
    update_mood(user_id)

    return {
        'previous_experience': previous_experience,
        'added_experience': amount,
        'new_experience': experience_for_current_level,
        'level_up': level_up,
        'previous_level': previous_level,
        'current_level': current_level,
        'level_up_message': f"恭喜！{companion['name']}升级到{new_level_info['name']}了！" if level_up and new_level_info else None,
        'new_level_info': new_level_info,
        'next_level_experience': next_level_exp,
        'experience_needed': experience_needed
    }


def log_experience(user_id, companion_id, experience_type, amount, reason):
    """Log experience gain."""
    query = """
        INSERT INTO experience_logs (user_id, companion_id, experience_type, amount, reason)
        VALUES (%s, %s, %s, %s, %s);
    """
    execute_query(query, (user_id, companion_id, experience_type, amount, reason))


def get_experience_logs(user_id, limit=50):
    """Get experience logs for a user."""
    query = """
        SELECT * FROM experience_logs
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s;
    """
    return execute_query(query, (user_id, limit), fetch=True)


# ============ Level Operations ============

def get_level_info(level):
    """Get level information."""
    if level > 10:
        level = 10
    query = "SELECT * FROM companion_levels WHERE level = %s;"
    result = execute_query(query, (level,), fetch=True)
    return result[0] if result else None


def get_all_levels():
    """Get all level information."""
    query = "SELECT * FROM companion_levels ORDER BY level;"
    return execute_query(query, fetch=True)


# ============ Mood Operations ============

def calculate_mood(user_id):
    """Calculate and update companion mood based on user activity."""
    companion = get_user_companion(user_id)
    if not companion:
        return 'happy'

    consecutive_days = companion['consecutive_days']
    last_active = companion.get('last_active_date')

    if last_active:
        today = date.today()
        if last_active == today:
            # User active today
            if consecutive_days >= 7:
                return 'proud'
            elif consecutive_days >= 3:
                return 'happy'
            elif consecutive_days >= 1:
                return 'excited'
        elif last_active == today - timedelta(days=1):
            # User was active yesterday
            return 'encourage'
        else:
            # User inactive for more than 1 day
            days_diff = (today - last_active).days
            if days_diff > 2:
                return 'sad'
            return 'encourage'

    return 'happy'


def update_mood(user_id, mood=None):
    """Update companion mood."""
    if mood is None:
        mood = calculate_mood(user_id)

    companion = get_user_companion(user_id)
    if companion:
        query = """
            UPDATE ai_companions
            SET current_mood = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """
        execute_query(query, (mood, companion['id']))

    return mood


# ============ Streak Operations ============

def update_streak(user_id):
    """Update consecutive learning days."""
    companion = get_user_companion(user_id)
    if not companion:
        return None

    today = date.today()
    last_active = companion.get('last_active_date')
    consecutive_days = companion['consecutive_days']

    if last_active:
        if last_active == today:
            # Already updated today
            return companion
        elif last_active == today - timedelta(days=1):
            # Continuing streak
            consecutive_days += 1
        else:
            # Streak broken
            consecutive_days = 1
    else:
        consecutive_days = 1

    query = """
        UPDATE ai_companions
        SET consecutive_days = %s, last_active_date = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *;
    """
    result = execute_query(query, (consecutive_days, today, companion['id']), fetch=True)
    return result[0] if result else None


# ============ Daily Tasks Operations ============

def create_daily_tasks(user_id):
    """Create daily tasks for a user."""
    task_templates = [
        {
            'task_type': 'practice',
            'task_title': '练习自我介绍',
            'task_description': '完成一次完整的自我介绍练习',
            'target_count': 1,
            'experience_reward': 100
        },
        {
            'task_type': 'speaking',
            'task_title': '口语大挑战',
            'task_description': '完成3道口语题目',
            'target_count': 3,
            'experience_reward': 150
        },
        {
            'task_type': 'watch_video',
            'task_title': '观看教学视频',
            'task_description': '观看1个面试技巧视频',
            'target_count': 1,
            'experience_reward': 50
        }
    ]

    today = date.today()

    for task in task_templates:
        query = """
            INSERT INTO daily_tasks (user_id, task_type, task_title, task_description, target_count, experience_reward, assigned_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        execute_query(query, (user_id, task['task_type'], task['task_title'],
                              task['task_description'], task['target_count'],
                              task['experience_reward'], today))


def get_daily_tasks(user_id, task_date=None):
    """Get daily tasks for a user."""
    if task_date is None:
        task_date = date.today()

    query = """
        SELECT * FROM daily_tasks
        WHERE user_id = %s AND assigned_date = %s
        ORDER BY created_at;
    """
    tasks = execute_query(query, (user_id, task_date), fetch=True)

    # If no tasks for today, create them
    if not tasks:
        create_daily_tasks(user_id)
        tasks = execute_query(query, (user_id, task_date), fetch=True)

    # Calculate progress for each task
    result_tasks = []
    completed_count = 0
    total_reward = 0

    for task in tasks:
        task_dict = dict(task)
        task_dict['progress'] = int((task['current_count'] / task['target_count']) * 100) if task['target_count'] > 0 else 0
        result_tasks.append(task_dict)

        if task['is_completed']:
            completed_count += 1
        total_reward += task['experience_reward']

    return {
        'date': task_date.isoformat(),
        'tasks': result_tasks,
        'completed_count': completed_count,
        'total_count': len(result_tasks),
        'total_reward': total_reward
    }


def complete_task(user_id, task_id):
    """Mark a task as completed and award experience."""
    # Get task info
    query = "SELECT * FROM daily_tasks WHERE id = %s AND user_id = %s;"
    task = execute_query(query, (task_id, user_id), fetch=True)

    if not task:
        return None

    task = task[0]

    if task['is_completed']:
        return {'already_completed': True, 'task': task}

    # Update task
    query = """
        UPDATE daily_tasks
        SET is_completed = TRUE, current_count = target_count, completed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *;
    """
    updated_task = execute_query(query, (task_id,), fetch=True)

    # Award experience
    reward = task['experience_reward']
    exp_result = add_experience(user_id, 'task_complete', reward, f"完成任务: {task['task_title']}")

    return {
        'already_completed': False,
        'task': updated_task[0] if updated_task else None,
        'experience_awarded': reward,
        'level_up': exp_result.get('level_up', False) if exp_result else False,
        'current_level': exp_result.get('current_level', 1) if exp_result else 1
    }


def update_task_progress(user_id, task_type, increment=1):
    """Update task progress (called when user completes relevant action)."""
    today = date.today()

    # Find the task
    query = """
        SELECT * FROM daily_tasks
        WHERE user_id = %s AND task_type = %s AND assigned_date = %s AND is_completed = FALSE;
    """
    task = execute_query(query, (user_id, task_type, today), fetch=True)

    if not task:
        return None

    task = task[0]
    new_count = min(task['current_count'] + increment, task['target_count'])
    is_completed = new_count >= task['target_count']

    query = """
        UPDATE daily_tasks
        SET current_count = %s, is_completed = %s, completed_at = CASE WHEN %s = TRUE THEN CURRENT_TIMESTAMP ELSE completed_at END
        WHERE id = %s
        RETURNING *;
    """
    result = execute_query(query, (new_count, is_completed, is_completed, task['id']), fetch=True)

    return result[0] if result else None


# ============ Skills Operations ============

def get_all_skills():
    """Get all available skills."""
    query = "SELECT * FROM companion_skills ORDER BY required_level;"
    return execute_query(query, fetch=True)


def get_available_skills(user_id):
    """Get skills available for user to unlock based on level."""
    companion = get_user_companion(user_id)
    if not companion:
        return []

    user_level = companion['level']
    unlocked_skills = companion['unlocked_skills']
    if isinstance(unlocked_skills, str):
        import json
        unlocked_skills = json.loads(unlocked_skills)

    # Get all skills
    all_skills = get_all_skills()

    # Filter skills by level
    available = []
    for skill in all_skills:
        skill_dict = dict(skill)
        skill_dict['is_unlocked'] = skill['skill_id'] in unlocked_skills
        skill_dict['can_unlock'] = user_level >= skill['required_level'] and skill['skill_id'] not in unlocked_skills
        available.append(skill_dict)

    return available


def unlock_skill(user_id, skill_id):
    """Unlock a skill for user's companion."""
    companion = get_user_companion(user_id)
    if not companion:
        return {'success': False, 'message': 'Companion not found'}

    # Check if skill exists
    skill_query = "SELECT * FROM companion_skills WHERE skill_id = %s;"
    skill = execute_query(skill_query, (skill_id,), fetch=True)
    if not skill:
        return {'success': False, 'message': 'Skill not found'}

    skill = skill[0]

    # Check if user meets level requirement
    if companion['level'] < skill['required_level']:
        return {'success': False, 'message': f'需要达到等级 {skill["required_level"]} 才能解锁此技能'}

    # Check if already unlocked
    unlocked_skills = companion['unlocked_skills']
    if isinstance(unlocked_skills, str):
        import json
        unlocked_skills = json.loads(unlocked_skills)

    if skill_id in unlocked_skills:
        return {'success': False, 'message': '技能已解锁'}

    # Unlock skill
    unlocked_skills.append(skill_id)

    query = """
        UPDATE ai_companions
        SET unlocked_skills = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """
    execute_query(query, (unlocked_skills, companion['id']))

    # Also record in user_skill_unlocks table
    unlock_query = """
        INSERT INTO user_skill_unlocks (user_id, companion_id, skill_id)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """
    execute_query(unlock_query, (user_id, companion['id'], skill_id))

    return {'success': True, 'message': f'成功解锁技能: {skill["name"]}', 'skill': skill}


# ============ Dialogue Operations ============

def get_dialogue_templates(trigger_type=None, emotion=None, min_level=1):
    """Get dialogue templates based on filters."""
    conditions = []
    params = []

    if trigger_type:
        conditions.append("trigger_type = %s")
        params.append(trigger_type)
    if emotion:
        conditions.append("emotion = %s")
        params.append(emotion)
    if min_level:
        conditions.append("min_level <= %s")
        params.append(min_level)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT * FROM dialogue_templates
        WHERE {where_clause}
        ORDER BY sort_order;
    """
    return execute_query(query, params, fetch=True)


def get_companion_dialogue(user_id, trigger_type='idle', emotion=None):
    """Get AI companion dialogue based on trigger and mood."""
    companion = get_user_companion(user_id)
    if not companion:
        return {'dialogue': '你好！我是你的AI伙伴！', 'emotion': 'happy'}

    current_mood = emotion or companion['current_mood']
    user_level = companion['level']

    # Get dialogue templates
    templates = get_dialogue_templates(trigger_type=trigger_type, min_level=user_level)

    if not templates:
        templates = get_dialogue_templates(min_level=user_level)

    if not templates:
        # Default dialogues
        defaults = {
            'happy': '今天也要加油哦！',
            'excited': '准备好学习了吗？',
            'encourage': '加油！你可以的！',
            'proud': '太棒了！你真厉害！',
            'sad': '我在这里等你哦~',
            'thinking': '今天想练习什么呢？',
            'sleeping': 'Zzz... 让我休息一下~'
        }
        return {
            'dialogue': defaults.get(current_mood, '你好呀！'),
            'emotion': current_mood
        }

    # Select random template
    import random
    template = random.choice(templates)

    # Replace placeholders
    dialogue_text = template['template_text']
    if '{days}' in dialogue_text:
        dialogue_text = dialogue_text.replace('{days}', str(companion['consecutive_days']))

    return {
        'dialogue': dialogue_text,
        'emotion': template['emotion'],
        'companion_name': companion['name'],
        'character_type': companion['character_type'],
        'level': companion['level']
    }


# ============ Companion Info Full ============

def get_companion_info(user_id):
    """Get full companion information including level details."""
    companion = get_user_companion(user_id)
    if not companion:
        return None

    # Get level info
    level_info = get_level_info(companion['level'])
    next_level_info = get_level_info(companion['level'] + 1) if companion['level'] < 10 else None

    # Calculate experience progress
    current_level_exp = level_info['required_experience'] if level_info else 0
    next_level_exp = next_level_info['required_experience'] if next_level_info else companion['total_experience']

    experience_in_level = companion['total_experience'] - current_level_exp
    experience_needed = next_level_exp - current_level_exp if next_level_exp > current_level_exp else 1

    # Get unlocked skills details
    unlocked_skills = companion['unlocked_skills']
    if isinstance(unlocked_skills, str):
        import json
        unlocked_skills = json.loads(unlocked_skills)

    skills_query = "SELECT * FROM companion_skills WHERE skill_id = ANY(%s);"
    skills = execute_query(skills_query, (unlocked_skills,), fetch=True)

    # Get daily tasks
    tasks = get_daily_tasks(user_id)

    return {
        'id': str(companion['id']),
        'user_id': str(companion['user_id']),
        'name': companion['name'],
        'character_type': companion['character_type'],
        'level': companion['level'],
        'experience': experience_in_level,
        'experience_to_next_level': experience_needed,
        'total_experience': companion['total_experience'],
        'consecutive_days': companion['consecutive_days'],
        'last_active_date': companion['last_active_date'].isoformat() if companion.get('last_active_date') else None,
        'current_mood': companion['current_mood'],
        'level_info': level_info,
        'unlocked_skills': skills,
        'daily_tasks': tasks,
        'created_at': companion['created_at'].isoformat() if companion.get('created_at') else None
    }


# ============ Character Type Emoji Mapping ============

def get_character_emoji(character_type, mood='happy'):
    """Get emoji representation of character."""
    emojis = {
        'dinosaur': {
            'happy': '🦖',
            'excited': '🦕',
            'encourage': '🐲',
            'proud': '🐉',
            'sad': '🥚',
            'thinking': '🤔',
            'sleeping': '😴'
        },
        'robot': {
            'happy': '🤖',
            'excited': '⚡',
            'encourage': '💪',
            'proud': '🏆',
            'sad': '😢',
            'thinking': '🧠',
            'sleeping': '🔋'
        },
        'rabbit': {
            'happy': '🐰',
            'excited': '🐇',
            'encourage': '💖',
            'proud': '👑',
            'sad': '🥕',
            'thinking': '🤔',
            'sleeping': '😴'
        }
    }

    return emojis.get(character_type, emojis['dinosaur']).get(mood, '🦖')


if __name__ == '__main__':
    print("AI Companion Service loaded.")
