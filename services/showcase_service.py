"""
Showcase Service - 学习成果社交秀服务
生成可分享的学习成就海报和进度周报
"""

import os
import json
import base64
import uuid
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# AI生成海报模板
POSTER_TEMPLATES = [
    {
        'id': 'achievement_basic',
        'name': '基础成就卡',
        'description': '展示学习成就的精美卡片',
        'category': 'achievement',
        'background': '#667eea',
        'elements': ['avatar', 'badge', 'title', 'date']
    },
    {
        'id': 'achievement_gradient',
        'name': '渐变成就卡',
        'description': '使用渐变背景的精美海报',
        'category': 'achievement',
        'background': 'gradient',
        'elements': ['avatar', 'badge', 'title', 'stats', 'date']
    },
    {
        'id': 'weekly_report',
        'name': '进度周报',
        'description': '每周学习进度的详细报告',
        'category': 'report',
        'background': '#10b981',
        'elements': ['avatar', 'week_summary', 'progress', 'goals', 'date']
    },
    {
        'id': 'streak_celebration',
        'name': '连续学习庆祝',
        'description': '庆祝连续学习成就',
        'category': 'streak',
        'background': 'gradient_orange',
        'elements': ['avatar', 'streak_count', 'fire', 'encouragement', 'date']
    },
    {
        'id': 'master_certificate',
        'name': '学习大师证书',
        'description': '展示成为某领域大师的证书',
        'category': 'master',
        'background': 'gradient_gold',
        'elements': ['avatar', 'master_badge', 'title', 'description', 'date', 'signature']
    }
]

# 成就类型
ACHIEVEMENT_TYPES = {
    'first_practice': {'icon': '🌟', 'title': '首次练习', 'color': '#fbbf24'},
    'streak_3': {'icon': '🔥', 'title': '连续3日', 'color': '#f97316'},
    'streak_7': {'icon': '💪', 'title': '连续7日', 'color': '#ef4444'},
    'streak_30': {'icon': '👑', 'title': '连续30日', 'color': '#8b5cf6'},
    'perfect_score': {'icon': '🌈', 'title': '满分达人', 'color': '#06b6d4'},
    'master_interview': {'icon': '🎓', 'title': '面试大师', 'color': '#10b981'},
    'expression_master': {'icon': '🎤', 'title': '表达大师', 'color': '#ec4899'},
    'week_warrior': {'icon': '🏆', 'title': '周冠军', 'color': '#f59e0b'},
    'month_master': {'icon': '👑', 'title': '月冠军', 'color': '#6366f1'}
}


def get_templates(category=None):
    """获取海报模板列表"""
    if category:
        return [t for t in POSTER_TEMPLATES if t['category'] == category]
    return POSTER_TEMPLATES


def get_template(template_id):
    """获取指定模板"""
    for template in POSTER_TEMPLATES:
        if template['id'] == template_id:
            return template
    return None


def generate_poster_data(user_data, template_id, achievement_data=None):
    """
    生成海报数据
    user_data: {'name': '孩子名字', 'avatar': '头像URL', 'stats': {...}}
    template_id: 模板ID
    achievement_data: 成就数据
    """
    template = get_template(template_id)
    if not template:
        return None

    # 构建海报数据
    poster_data = {
        'template_id': template_id,
        'template_name': template['name'],
        'background': template['background'],
        'elements': template['elements'],
        'user': user_data,
        'achievement': achievement_data,
        'generated_at': datetime.now().isoformat()
    }

    # 根据模板类型添加特定数据
    if template['category'] == 'achievement':
        poster_data['title'] = achievement_data.get('title', '学习成就') if achievement_data else '学习成就'
        poster_data['subtitle'] = achievement_data.get('description', '恭喜获得新成就！') if achievement_data else '恭喜获得新成就！'
        poster_data['icon'] = achievement_data.get('icon', '🏆') if achievement_data else '🏆'

    elif template['category'] == 'report':
        poster_data['week_number'] = achievement_data.get('week_number', 1) if achievement_data else 1
        poster_data['total_time'] = achievement_data.get('total_time', 0) if achievement_data else 0
        poster_data['completed_lessons'] = achievement_data.get('completed_lessons', 0) if achievement_data else 0
        poster_data['accuracy'] = achievement_data.get('accuracy', 0) if achievement_data else 0

    elif template['category'] == 'streak':
        poster_data['streak_days'] = achievement_data.get('streak_days', 0) if achievement_data else 0
        poster_data['encouragement'] = get_encouragement_message(achievement_data.get('streak_days', 0) if achievement_data else 0)

    return poster_data


def get_encouragement_message(streak_days):
    """根据连续天数获取鼓励消息"""
    messages = {
        0: '加油！明天继续努力！',
        1: '良好的开始！继续保持！',
        3: '太棒了！已经连续3天！',
        7: '一周的坚持！为你骄傲！',
        14: '两周的努力！太厉害了！',
        30: '一个月的坚持！你太棒了！',
        60: '两个月的坚持！你太优秀了！',
        90: '三个月的坚持！你就是榜样！',
    }

    # 找到最接近的里程碑
    for days in sorted(messages.keys(), reverse=True):
        if streak_days >= days:
            return messages[days]

    return messages[0]


def create_share_record(user_id, poster_type, poster_data, platform=None):
    """
    创建分享记录
    返回分享记录ID
    """
    from db.database import execute_query

    share_id = str(uuid.uuid4())
    query = """
        INSERT INTO showcase_shares (id, user_id, poster_type, poster_data, platform, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """

    try:
        result = execute_query(
            query,
            (share_id, user_id, poster_type, json.dumps(poster_data), platform, datetime.now()),
            fetch=True
        )
        return result[0]['id'] if result else None
    except Exception as e:
        print(f"Error creating share record: {e}")
        return None


def get_user_showcase_history(user_id, limit=10):
    """获取用户的历史展示记录"""
    from db.database import execute_query

    query = """
        SELECT id, poster_type, poster_data, platform, created_at
        FROM showcase_shares
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s;
    """

    try:
        result = execute_query(query, (user_id, limit), fetch=True)
        return result
    except Exception as e:
        print(f"Error fetching showcase history: {e}")
        return []


def get_popular_showcases(limit=20):
    """获取热门展示案例"""
    from db.database import execute_query

    query = """
        SELECT s.id, s.poster_type, s.poster_data, s.platform, s.created_at,
               u.name as user_name
        FROM showcase_shares s
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
        LIMIT %s;
    """

    try:
        result = execute_query(query, (limit,), fetch=True)
        return result
    except Exception as e:
        print(f"Error fetching popular showcases: {e}")
        return []


def generate_share_image(poster_data):
    """
    生成分享图片（返回base64编码的图片）
    这是一个简单的实现，实际可以使用更复杂的Canvas库
    """
    # 创建简单的海报图片
    width, height = 600, 800

    # 根据背景类型设置颜色
    bg = poster_data.get('background', '#667eea')
    if bg == 'gradient':
        # 创建渐变背景
        img = Image.new('RGB', (width, height), color='#667eea')
    elif bg == 'gradient_orange':
        img = Image.new('RGB', (width, height), color='#f97316')
    elif bg == 'gradient_gold':
        img = Image.new('RGB', (width, height), color='#f59e0b')
    else:
        img = Image.new('RGB', (width, height), color=bg)

    draw = ImageDraw.Draw(img)

    # 绘制装饰元素
    draw.ellipse([50, 50, 150, 150], fill=(255, 255, 255, 30))
    draw.ellipse([450, 600, 550, 700], fill=(255, 255, 255, 30))

    # 绘制标题
    title = poster_data.get('title', '学习成就')
    draw.text((width//2, 200), title, fill=(255, 255, 255), anchor='mm')

    # 绘制图标
    icon = poster_data.get('icon', '🏆')
    draw.text((width//2, 300), icon, anchor='mm')

    # 绘制用户信息
    user_name = poster_data.get('user', {}).get('name', '同学')
    draw.text((width//2, 400), f'{user_name}的成就', fill=(255, 255, 255), anchor='mm')

    # 绘制日期
    date_str = datetime.now().strftime('%Y年%m月%d日')
    draw.text((width//2, 700), date_str, fill=(255, 255, 255), anchor='mm')

    # 转换为base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f'data:image/png;base64,{img_str}'


# 成功案例数据
SUCCESS_CASES = [
    {
        'id': 1,
        'child_name': '小明',
        'age': 6,
        'school': 'XX小学',
        'achievement': '面试成功',
        'experience': '通过每天练习模拟面试，我变得更有自信了！',
        'tips': '坚持每天练习，多听多说很重要',
        'avatar': '👦'
    },
    {
        'id': 2,
        'child_name': '小红',
        'age': 7,
        'school': 'YY国际学校',
        'achievement': '表达能力的提升',
        'experience': '以前不敢说话，现在能流畅表达了',
        'tips': '不要害怕犯错，勇于尝试',
        'avatar': '👧'
    },
    {
        'id': 3,
        'child_name': '小华',
        'age': 6,
        'school': 'ZZ实验小学',
        'achievement': '连续学习30天',
        'experience': '每天坚持学习，形成了很好的习惯',
        'tips': '让学习成为日常的一部分',
        'avatar': '👦'
    }
]


def get_success_cases(category=None):
    """获取成功案例"""
    if category:
        return [c for c in SUCCESS_CASES if c.get('category') == category]
    return SUCCESS_CASES
