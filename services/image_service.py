"""
Image Service - Visual Content Management
香港升小面试 AI 导师 - 视觉素材服务

功能：
- 预制图片库管理
- 根据主题和兴趣智能选图
- 图片 CDN URL 生成
"""

import os
import random
from services.prompts import get_template


# ============ 配置 ============

# 图片库基础 URL（可配置为 CDN）
IMAGE_BASE_URL = os.getenv('IMAGE_BASE_URL', 'https://cdn.example.com/images')
R2_PUBLIC_URL = os.getenv('R2_PUBLIC_URL', '')

# ============ 预制图片库定义 ============

IMAGE_LIBRARY = {
    # 自我介绍主题
    'introduction': {
        'description': '自我介绍相关图片',
        'images': [
            {'id': 'intro-01', 'name': '孩子问好', 'tags': ['greeting', 'happy'], 'url': None},
            {'id': 'intro-02', 'name': '孩子微笑', 'tags': ['smiling', 'confident'], 'url': None},
            {'id': 'intro-03', 'name': '自我介绍卡片', 'tags': ['card', 'name'], 'url': None},
            {'id': 'intro-04', 'name': '握手', 'tags': ['greeting', 'polite'], 'url': None},
            {'id': 'intro-05', 'name': '挥手', 'tags': ['wave', 'friendly'], 'url': None},
            {'id': 'intro-06', 'name': '站姿端正', 'tags': ['posture', 'confident'], 'url': None},
            {'id': 'intro-07', 'name': '眼神接触', 'tags': ['eye-contact', 'confident'], 'url': None},
            {'id': 'intro-08', 'name': '大声说话', 'tags': ['speaking', 'clear'], 'url': None},
        ]
    },
    
    # 兴趣爱好主题
    'interests': {
        'description': '兴趣爱好相关图片',
        'images': [
            # 恐龙
            {'id': 'dino-01', 'name': '恐龙玩具', 'tags': ['dinosaurs', 'toys'], 'interests': ['dinosaurs'], 'url': None},
            {'id': 'dino-02', 'name': '恐龙绘本', 'tags': ['dinosaurs', 'books'], 'interests': ['dinosaurs'], 'url': None},
            {'id': 'dino-03', 'name': '恐龙模型', 'tags': ['dinosaurs', 'models'], 'interests': ['dinosaurs'], 'url': None},
            
            # Lego
            {'id': 'lego-01', 'name': 'Lego城市', 'tags': ['lego', 'city'], 'interests': ['lego'], 'url': None},
            {'id': 'lego-02', 'name': 'Lego车', 'tags': ['lego', 'cars'], 'interests': ['lego'], 'url': None},
            {'id': 'lego-03', 'name': 'Lego建筑', 'tags': ['lego', 'building'], 'interests': ['lego'], 'url': None},
            
            # 画画
            {'id': 'art-01', 'name': '绘画', 'tags': ['art', 'drawing'], 'interests': ['art'], 'url': None},
            {'id': 'art-02', 'name': '颜料', 'tags': ['art', 'paints'], 'interests': ['art'], 'url': None},
            {'id': 'art-03', 'name': '画板', 'tags': ['art', 'easel'], 'interests': ['art'], 'url': None},
            
            # 运动
            {'id': 'sports-01', 'name': '足球', 'tags': ['sports', 'football'], 'interests': ['sports'], 'url': None},
            {'id': 'sports-02', 'name': '篮球', 'tags': ['sports', 'basketball'], 'interests': ['sports'], 'url': None},
            {'id': 'sports-03', 'name': '游泳', 'tags': ['sports', 'swimming'], 'interests': ['swimming'], 'url': None},
            
            # 音乐
            {'id': 'music-01', 'name': '钢琴', 'tags': ['music', 'piano'], 'interests': ['music'], 'url': None},
            {'id': 'music-02', 'name': '吉他', 'tags': ['music', 'guitar'], 'interests': ['music'], 'url': None},
            {'id': 'music-03', 'name': '唱歌', 'tags': ['music', 'singing'], 'interests': ['music'], 'url': None},
            
            # 阅读
            {'id': 'reading-01', 'name': '读书', 'tags': ['reading', 'books'], 'interests': ['reading'], 'url': None},
            {'id': 'reading-02', 'name': '图书馆', 'tags': ['reading', 'library'], 'interests': ['reading'], 'url': None},
            {'id': 'reading-03', 'name': '绘本', 'tags': ['reading', 'picture-book'], 'interests': ['reading'], 'url': None},
            
            # 科学
            {'id': 'science-01', 'name': '显微镜', 'tags': ['science', 'microscope'], 'interests': ['science'], 'url': None},
            {'id': 'science-02', 'name': '实验', 'tags': ['science', 'experiment'], 'interests': ['science'], 'url': None},
            {'id': 'science-03', 'name': '太空', 'tags': ['science', 'space'], 'interests': ['science'], 'url': None},
            
            # 动物
            {'id': 'animals-01', 'name': '小狗', 'tags': ['animals', 'dog'], 'interests': ['animals'], 'url': None},
            {'id': 'animals-02', 'name': '小猫', 'tags': ['animals', 'cat'], 'interests': ['animals'], 'url': None},
            {'id': 'animals-03', 'name': '动物园', 'tags': ['animals', 'zoo'], 'interests': ['animals'], 'url': None},
            
            # 其他兴趣
            {'id': 'cooking-01', 'name': '烹饪', 'tags': ['cooking', 'kitchen'], 'interests': ['cooking'], 'url': None},
            {'id': 'cars-01', 'name': '汽车', 'tags': ['cars', 'vehicle'], 'interests': ['cars'], 'url': None},
            {'id': 'planes-01', 'name': '飞机', 'tags': ['planes', 'flying'], 'interests': ['planes'], 'url': None},
            {'id': 'nature-01', 'name': '大自然', 'tags': ['nature', 'park'], 'interests': ['nature'], 'url': None},
            {'id': 'gaming-01', 'name': '游戏', 'tags': ['gaming', 'games'], 'interests': ['gaming'], 'url': None},
            {'id': 'performing-01', 'name': '表演', 'tags': ['performing', 'stage'], 'interests': ['performing'], 'url': None},
        ]
    },
    
    # 家庭介绍主题
    'family': {
        'description': '家庭相关图片',
        'images': [
            {'id': 'family-01', 'name': '家庭合照', 'tags': ['family', 'photo'], 'url': None},
            {'id': 'family-02', 'name': '爸爸妈妈', 'tags': ['parents', 'family'], 'url': None},
            {'id': 'family-03', 'name': '兄弟姐妹', 'tags': ['siblings', 'family'], 'url': None},
            {'id': 'family-04', 'name': '一起吃饭', 'tags': ['dinner', 'family'], 'url': None},
            {'id': 'family-05', 'name': '一起玩耍', 'tags': ['playing', 'family'], 'url': None},
            {'id': 'family-06', 'name': '拥抱', 'tags': ['hugging', 'love'], 'url': None},
            {'id': 'family-07', 'name': '讲故事', 'tags': ['story', 'bedtime'], 'url': None},
            {'id': 'family-08', 'name': '户外活动', 'tags': ['outdoor', 'family'], 'url': None},
        ]
    },
    
    # 观察力训练主题
    'observation': {
        'description': '观察力训练图片',
        'images': [
            {'id': 'obs-01', 'name': '凌乱房间', 'tags': ['room', 'messy'], 'url': None},
            {'id': 'obs-02', 'name': '整洁房间', 'tags': ['room', 'tidy'], 'url': None},
            {'id': 'obs-03', 'name': '公园场景', 'tags': ['park', 'scene'], 'url': None},
            {'id': 'obs-04', 'name': '课室', 'tags': ['classroom', 'school'], 'url': None},
            {'id': 'obs-05', 'name': '玩具箱', 'tags': ['toys', 'box'], 'url': None},
            {'id': 'obs-06', 'name': '厨房', 'tags': ['kitchen', 'home'], 'url': None},
            {'id': 'obs-07', 'name': '浴室', 'tags': ['bathroom', 'home'], 'url': None},
            {'id': 'obs-08', 'name': '花园', 'tags': ['garden', 'outdoor'], 'url': None},
        ]
    },
    
    # 处境题主题
    'scenarios': {
        'description': '处境题相关图片',
        'images': [
            {'id': 'sc-01', 'name': '分享玩具', 'tags': ['sharing', 'toys'], 'url': None},
            {'id': 'sc-02', 'name': '轮流玩耍', 'tags': ['taking-turns', 'play'], 'url': None},
            {'id': 'sc-03', 'name': '帮助朋友', 'tags': ['helping', 'friends'], 'url': None},
            {'id': 'sc-04', 'name': '说对不起', 'tags': ['apologizing', 'sorry'], 'url': None},
            {'id': 'sc-05', 'name': '等侯', 'tags': ['waiting', 'patient'], 'url': None},
            {'id': 'sc-06', 'name': '整理物品', 'tags': ['tidying', 'organizing'], 'url': None},
            {'id': 'sc-07', 'name': '穿衣', 'tags': ['dressing', 'clothes'], 'url': None},
            {'id': 'sc-08', 'name': '吃饭', 'tags': ['eating', 'mealtime'], 'url': None},
        ]
    }
}

# ============ 通用图片（用于没有匹配的情况）===========
GENERAL_IMAGES = [
    {'id': 'gen-01', 'name': '笑脸', 'tags': ['happy', 'smile'], 'url': None},
    {'id': 'gen-02', 'name': '竖起大拇指', 'tags': ['thumbs-up', 'good'], 'url': None},
    {'id': 'gen-03', 'name': '星星', 'tags': ['star', 'reward'], 'url': None},
    {'id': 'gen-04', 'name': '奖杯', 'tags': ['trophy', 'winner'], 'url': None},
    {'id': 'gen-05', 'name': '书本', 'tags': ['book', 'learning'], 'url': None},
]


# ============ 智能选图函数 ============

def select_images_for_topic(topic_id, interests=None, count=3):
    """
    根据主题和用户兴趣选择图片
    
    Args:
        topic_id: 主题 ID
        interests: 用户兴趣列表，如 ['dinosaurs', 'lego']
        count: 需要返回的图片数量
    
    Returns:
        list: 选中的图片列表
    """
    selected = []
    
    # 1. 获取主题相关图片
    topic_images = IMAGE_LIBRARY.get(topic_id, {}).get('images', [])
    
    if not topic_images:
        # 使用通用图片
        selected = random.sample(GENERAL_IMAGES, min(count, len(GENERAL_IMAGES)))
        return format_image_response(selected, topic_id)
    
    # 2. 根据兴趣优先选择
    if interests:
        interest_images = []
        for img in topic_images:
            # 检查图片是否有匹配的兴趣标签
            if 'interests' in img:
                matching = set(img['interests']) & set(interests)
                if matching:
                    interest_images.append(img)
        
        # 添加匹配的-interest图片
        if interest_images:
            selected.extend(random.sample(
                interest_images, 
                min(len(interest_images), count)
            ))
    
    # 3. 补充通用主题图片（如果需要）
    if len(selected) < count:
        # 排除已选的图片
        selected_ids = {img['id'] for img in selected}
        remaining = [img for img in topic_images if img['id'] not in selected_ids]
        
        # 随机补充
        to_add = min(count - len(selected), len(remaining))
        if to_add > 0:
            selected.extend(random.sample(remaining, to_add))
    
    # 4. 如果还是不够，用通用图片补充
    if len(selected) < count:
        selected_ids = {img['id'] for img in selected}
        general = [img for img in GENERAL_IMAGES if img['id'] not in selected_ids]
        
        to_add = min(count - len(selected), len(general))
        if to_add > 0:
            selected.extend(random.sample(general, to_add))
    
    # 5. 随机打乱顺序
    random.shuffle(selected)
    
    return format_image_response(selected[:count], topic_id)


def format_image_response(images, topic_id):
    """
    格式化图片响应
    
    Args:
        images: 图片列表
        topic_id: 主题 ID
    
    Returns:
        dict: 格式化的响应
    """
    # 生成完整 URL
    formatted_images = []
    for i, img in enumerate(images, 1):
        # 构建图片 URL（实际使用时替换为真实 CDN）
        image_url = img.get('url') or generate_image_url(img['id'], topic_id)
        
        formatted_images.append({
            'id': img['id'],
            'name': img['name'],
            'url': image_url,
            'position': i,
            'description': img.get('description', ''),
            'tags': img.get('tags', [])
        })
    
    return {
        'images': formatted_images,
        'total': len(formatted_images),
        'topic_id': topic_id
    }


def generate_image_url(image_id, topic_id):
    """
    生成图片 URL
    
    在实际生产环境中，这会返回 CDN 的完整 URL。
    开发环境使用占位图。
    """
    # 检查是否有配置的 R2/CDN
    if R2_PUBLIC_URL:
        return f"{R2_PUBLIC_URL}/images/{topic_id}/{image_id}.jpg"
    
    if IMAGE_BASE_URL and IMAGE_BASE_URL != 'https://cdn.example.com/images':
        return f"{IMAGE_BASE_URL}/{topic_id}/{image_id}.jpg"
    
    # 开发环境返回占位图 URL（可以使用 placeholder.com 或本地路径）
    return f"/static/images/{topic_id}/{image_id}.jpg"


def get_topic_image_count(topic_id):
    """获取主题的图片数量"""
    topic = IMAGE_LIBRARY.get(topic_id, {})
    return len(topic.get('images', []))


def list_all_topics():
    """列出所有可用的主题"""
    topics = []
    for topic_id, data in IMAGE_LIBRARY.items():
        topics.append({
            'id': topic_id,
            'name': data['description'],
            'image_count': len(data['images'])
        })
    return topics


def get_image_details(image_id):
    """获取图片详情"""
    for topic_id, data in IMAGE_LIBRARY.items():
        for img in data['images']:
            if img['id'] == image_id:
                return {
                    **img,
                    'topic_id': topic_id,
                    'topic_name': data['description'],
                    'url': generate_image_url(image_id, topic_id)
                }
    
    # 检查通用图片
    for img in GENERAL_IMAGES:
        if img['id'] == image_id:
            return {
                **img,
                'topic_id': 'general',
                'topic_name': '通用图片',
                'url': generate_image_url(image_id, 'general')
            }
    
    return None


# ============ 图片建议（Prompt 用途）===========

def get_image_suggestions(topic_id, interests=None):
    """
    获取图片使用建议
    
    返回图片的描述和使用提示，可用于生成更详细的教学指导。
    """
    images = select_images_for_topic(topic_id, interests, count=3)
    
    suggestions = []
    for img in images['images']:
        suggestions.append({
            'image_id': img['id'],
            'image_name': img['name'],
            'usage_tip': get_usage_tip(img['tags'], topic_id)
        })
    
    return suggestions


def get_usage_tip(tags, topic_id):
    """获取图片使用提示"""
    tips = {
        'introduction': [
            "指着图片问：'呢個小朋友做緊咩呀？'",
            "教小朋友点样同陌生人打招呼",
            "练习站姿和眼神接触"
        ],
        'interests': [
            "用图片引出话题：'你鍾意玩呢啲嘢嗎？'",
            "鼓励孩子描述图片中的活动",
            "延伸到孩子的实际兴趣爱好"
        ],
        'family': [
            "指着家庭成员图片问：'呢個係邊個？'",
            "教基本家庭关系词汇",
            "鼓励孩子分享家庭活动"
        ],
        'observation': [
            "玩'搵不同'游戏",
            "让孩子描述图片中的细节",
            "训练观察力和表达能力"
        ],
        'scenarios': [
            "讨论图片中的情境应该点做",
            "教基本社交礼仪",
            "模拟场景练习"
        ]
    }
    
    topic_tips = tips.get(topic_id, ["指着图片说话", "让孩子描述看到什么"])
    return random.choice(topic_tips)
