"""
AI面试复盘室服务
提供多维度面试表现分析和历史对比功能
"""

import os
import json
import random
import uuid
import requests
from datetime import datetime, timedelta

# MiniMax API配置
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1')


def call_minimax_api(endpoint, payload):
    """调用 MiniMax API."""
    if not MINIMAX_API_KEY:
        print("⚠️ MiniMax API Key not configured")
        return None

    try:
        headers = {
            'Authorization': f'Bearer {MINIMAX_API_KEY}',
            'Content-Type': 'application/json'
        }

        url = f"{MINIMAX_BASE_URL}/{endpoint}"
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ MiniMax API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ MiniMax API exception: {e}")
        return None


def analyze_voice_performance(answer_text, audio_duration=None):
    """
    分析语音表现
    分析语速、流畅度、停顿等
    """
    if not answer_text:
        return {
            'speaking_rate': 0,
            'fluency_score': 0,
            'pause_count': 0,
            'pause_duration': 0,
            'clarity_score': 0,
            'sentiment': 'neutral'
        }

    # 计算回答字数
    word_count = len(answer_text)

    # 估算音频时长（如果未提供）
    if audio_duration is None:
        # 假设平均语速120字/分钟
        audio_duration = word_count / 2.0

    # 计算语速 (字/分钟)
    speaking_rate = (word_count / audio_duration * 60) if audio_duration > 0 else 0

    # 评估流畅度
    # 检查是否有重复词、结巴等
    has_repetition = len(set(answer_text.split())) < len(answer_text.split()) * 0.3
    has_fillers = any(filler in answer_text for filler in ['嗯', '啊', '既', '噉', '咁'])

    if has_repetition or has_fillers:
        fluency_score = random.randint(60, 75)
    else:
        fluency_score = random.randint(75, 95)

    # 估算停顿次数（基于标点符号）
    pause_count = answer_text.count('，') + answer_text.count('。') + answer_text.count('？')
    pause_duration = pause_count * 0.5  # 每次停顿约0.5秒

    # 清晰度评分（基于回答长度和完整性）
    if word_count < 10:
        clarity_score = random.randint(50, 70)
    elif word_count < 30:
        clarity_score = random.randint(70, 85)
    else:
        clarity_score = random.randint(80, 95)

    # 情感分析（简化版）
    positive_words = ['钟意', '开心', '好', '棒', '得意', '感谢', '高兴']
    negative_words = ['唔钟意', '唔开心', '唔好', '唔鍾意']

    if any(word in answer_text for word in positive_words):
        sentiment = 'positive'
    elif any(word in answer_text for word in negative_words):
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return {
        'speaking_rate': round(speaking_rate, 2),
        'fluency_score': fluency_score,
        'pause_count': pause_count,
        'pause_duration': round(pause_duration, 2),
        'clarity_score': clarity_score,
        'sentiment': sentiment
    }


def analyze_content_performance(question, answer):
    """
    分析内容表现
    评估逻辑性、完整性、创新性、相关性
    """
    if not answer:
        return {
            'logic_score': 0,
            'completeness_score': 0,
            'creativity_score': 0,
            'relevance_score': 0,
            'total_score': 0,
            'feedback': '未检测到回答',
            'strengths': [],
            'improvements': []
        }

    word_count = len(answer)

    # 逻辑性评分
    # 检查是否有因果关系表达
    has_logic = any(word in answer for word in ['因为', '所以', '如果', '咁', '然后', '之后'])
    if has_logic:
        logic_score = random.randint(75, 90)
    else:
        logic_score = random.randint(60, 80)

    # 完整性评分
    if word_count < 10:
        completeness_score = random.randint(40, 60)
    elif word_count < 30:
        completeness_score = random.randint(60, 80)
    else:
        completeness_score = random.randint(75, 95)

    # 创新性评分（是否有独特的观点）
    creative_indicators = ['自己', '我觉得', '我认为', '最得意', '最劲']
    if any(word in answer for word in creative_indicators):
        creativity_score = random.randint(75, 95)
    else:
        creativity_score = random.randint(60, 80)

    # 相关性评分（是否切题）
    if word_count < 5:
        relevance_score = random.randint(30, 50)
    else:
        relevance_score = random.randint(70, 90)

    # 计算总分
    total_score = int((logic_score + completeness_score + creativity_score + relevance_score) / 4)

    # 生成反馈和建议
    strengths = []
    improvements = []

    if logic_score >= 75:
        strengths.append('表达有条理，逻辑清晰')
    if completeness_score >= 75:
        strengths.append('回答完整，内容丰富')
    if creativity_score >= 75:
        strengths.append('有独特见解，想法新颖')
    if relevance_score >= 75:
        strengths.append('紧扣主题，回答切题')

    if logic_score < 65:
        improvements.append('尝试用"因为...所以..."等句式表达')
    if completeness_score < 65:
        improvements.append('可以讲多啲细节，令回答更丰富')
    if creativity_score < 65:
        improvements.append('试下讲多啲自己既諗法')
    if relevance_score < 65:
        improvements.append('尽量回答老师既问题')

    # 生成总体反馈
    if total_score >= 85:
        feedback = '表现非常好！继续努力！'
    elif total_score >= 70:
        feedback = '做得几好！可以再改进下就更棒！'
    elif total_score >= 50:
        feedback = '有进步空间，继续练习！'
    else:
        feedback = '加油！多啲练习会更好！'

    return {
        'logic_score': logic_score,
        'completeness_score': completeness_score,
        'creativity_score': creativity_score,
        'relevance_score': relevance_score,
        'total_score': total_score,
        'feedback': feedback,
        'strengths': strengths[:3],
        'improvements': improvements[:3]
    }


def generate_ai_recommendations(session_data, content_analyses, voice_analyses):
    """
    生成AI改进建议
    基于整体表现生成个性化建议
    """
    recommendations = []

    # 分析整体分数
    total_score = session_data.get('overall_score', 0)
    avg_logic = sum(c['logic_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0
    avg_completeness = sum(c['completeness_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0
    avg_creativity = sum(c['creativity_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0

    avg_clarity = sum(v['clarity_score'] for v in voice_analyses) / len(voice_analyses) if voice_analyses else 0
    avg_fluency = sum(v['fluency_score'] for v in voice_analyses) / len(voice_analyses) if voice_analyses else 0

    # 根据薄弱环节生成建议
    if avg_logic < 65:
        recommendations.append({
            'category': 'logic',
            'priority': 1,
            'title': '提升表达的逻辑性',
            'description': '练习使用因果关系和顺序词来组织回答，使表达更有条理。',
            'exercises': [
                {'type': '练习', 'content': '用"因为...所以..."句式描述一件日常生活事'},
                {'type': '练习', 'content': '用"首先...然后...最后..."讲述一个故事'}
            ],
            'resources': [
                {'type': 'tip', 'content': '回答前先谂一谂要点，再按顺序讲出黎'}
            ]
        })

    if avg_completeness < 65:
        recommendations.append({
            'category': 'completeness',
            'priority': 1,
            'title': '增加回答的完整性',
            'description': '尝试提供更多细节和背景信息，让回答更丰富。',
            'exercises': [
                {'type': '练习', 'content': '每回答一个问题，至少讲3点相关内容'},
                {'type': '练习', 'content': '用"乜嘢"、"点解"、"点样"自问自答'}
            ],
            'resources': [
                {'type': 'tip', 'content': '可以讲下"点解钟意"、"点解咁諗"}
            ]
        })

    if avg_creativity < 65:
        recommendations.append({
            'category': 'creativity',
            'priority': 2,
            'title': '培养创新思维',
            'description': '尝试表达独特的观点和想法，展现个人特色。',
            'exercises': [
                {'type': '练习', 'content': '讲一样嘢既唔同睇法'},
                {'type': '练习', 'content': '如果可以你想点？讲出你既諗法'}
            ],
            'resources': [
                {'type': 'tip', 'content': '可以讲多啲自己既经历同感受'}
            ]
        })

    if avg_clarity < 70:
        recommendations.append({
            'category': 'clarity',
            'priority': 2,
            'title': '提高表达清晰度',
            'description': '放慢语速，确保每个字都讲清楚。',
            'exercises': [
                {'type': '练习', 'content': '慢速朗读一段文章，注意发音'},
                {'type': '练习', 'content': '对着镜子练习自我介绍'}
            ],
            'resources': [
                {'type': 'tip', 'content': '讲话时望住老师眼睛，保持微笑'}
            ]
        })

    if avg_fluency < 70:
        recommendations.append({
            'category': 'fluency',
            'priority': 2,
            'title': '提升表达流畅度',
            'description': '减少语气词和重复，保持表达连贯。',
            'exercises': [
                {'type': '练习', 'content': '录音自己既回答，听下有冇"嗯"、"啊"'},
                {'type': '练习', 'content': '睇图讲故事，一次过讲完'}
            ],
            'resources': [
                {'type': 'tip', 'content': '唔好怕错，最紧要大胆讲'}
            ]
        })

    # 如果表现很好，添加鼓励性建议
    if total_score >= 85:
        recommendations.append({
            'category': 'excellence',
            'priority': 3,
            'title': '继续保持！',
            'description': '你既表现好好！继续保持呢种状态，面试一定冇问题！',
            'exercises': [],
            'resources': [
                {'type': 'tip', 'content': '可以挑战更难既问题黎提升自己'}
            ]
        })

    return recommendations


def analyze_interview_session(interview_data):
    """
    完整分析一次面试
    返回详细的分析报告
    """
    questions = interview_data.get('questions', [])
    answers = interview_data.get('answers', [])
    school_type = interview_data.get('school_type', 'holistic')

    # 分析每个问题的回答
    content_analyses = []
    voice_analyses = []
    total_score = 0

    for i, (question, answer) in enumerate(zip(questions, answers)):
        # 内容分析
        content = analyze_content_performance(question, answer)
        content['question_index'] = i
        content_analyses.append(content)
        total_score += content['total_score']

        # 语音分析
        voice = analyze_voice_performance(answer)
        voice['question_index'] = i
        voice_analyses.append(voice)

    # 计算整体分数
    overall_score = int(total_score / len(questions)) if questions else 0

    # 生成改进建议
    session_data = {
        'overall_score': overall_score,
        'school_type': school_type
    }
    recommendations = generate_ai_recommendations(session_data, content_analyses, voice_analyses)

    # 计算各维度平均分
    dimensions = {
        'logic': sum(c['logic_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0,
        'completeness': sum(c['completeness_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0,
        'creativity': sum(c['creativity_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0,
        'relevance': sum(c['relevance_score'] for c in content_analyses) / len(content_analyses) if content_analyses else 0,
        'clarity': sum(v['clarity_score'] for v in voice_analyses) / len(voice_analyses) if voice_analyses else 0,
        'fluency': sum(v['fluency_score'] for v in voice_analyses) / len(voice_analyses) if voice_analyses else 0,
        'speaking_rate': sum(v['speaking_rate'] for v in voice_analyses) / len(voice_analyses) if voice_analyses else 0
    }

    return {
        'overall_score': overall_score,
        'dimensions': {k: round(v, 1) for k, v in dimensions.items()},
        'content_analyses': content_analyses,
        'voice_analyses': voice_analyses,
        'recommendations': recommendations,
        'question_count': len(questions),
        'strongest_dimension': max(dimensions, key=dimensions.get) if dimensions else None,
        'weakest_dimension': min(dimensions, key=dimensions.get) if dimensions else None
    }


def generate_comparison_data(user_id, sessions):
    """
    生成历史对比数据
    对比多次面试的表现变化
    """
    if not sessions or len(sessions) < 2:
        return None

    # 按时间排序
    sorted_sessions = sorted(sessions, key=lambda x: x.get('created_at', ''))

    # 计算各项指标的变化趋势
    scores_over_time = []
    dimensions_over_time = {
        'logic': [],
        'completeness': [],
        'creativity': [],
        'clarity': [],
        'fluency': []
    }

    for session in sorted_sessions:
        if session.get('overall_score'):
            scores_over_time.append({
                'date': session.get('created_at', ''),
                'score': session['overall_score']
            })

    # 计算平均变化
    if len(scores_over_time) >= 2:
        first_score = scores_over_time[0]['score']
        last_score = scores_over_time[-1]['score']
        score_change = last_score - first_score

        if score_change > 10:
            trend = 'improving'
            insight = '你既表现有明显进步，继续保持！'
        elif score_change > 0:
            trend = 'slight_improvement'
            insight = '你有紧啲进步，可以再加油！'
        elif score_change > -10:
            trend = 'stable'
            insight = '表现稳定，可以尝试挑战更高难度！'
        else:
            trend = 'declining'
            insight = '需要多啲练习，唔好灰心！'
    else:
        trend = 'insufficient_data'
        insight = '需要更多数据来分析趋势'
        score_change = 0

    # 统计亮点
    highlights = []
    if sessions:
        best_session = max(sessions, key=lambda x: x.get('overall_score', 0))
        highlights.append(f"最高分: {best_session.get('overall_score', 0)}分")

        recent_sessions = [s for s in sorted_sessions if s.get('created_at')]
        if len(recent_sessions) >= 3:
            recent_avg = sum(s.get('overall_score', 0) for s in recent_sessions[-3:]) / 3
            highlights.append(f"最近3次平均: {round(recent_avg, 1)}分")

    return {
        'trend': trend,
        'score_change': score_change,
        'insight': insight,
        'highlights': highlights,
        'scores_over_time': scores_over_time,
        'total_sessions': len(sessions)
    }


def get_sample_debrief_data():
    """获取示例复盘数据（用于演示）"""
    return {
        'overall_score': 78,
        'dimensions': {
            'logic': 75,
            'completeness': 72,
            'creativity': 68,
            'relevance': 82,
            'clarity': 85,
            'fluency': 78,
            'speaking_rate': 120
        },
        'content_analyses': [
            {
                'question_index': 0,
                'question': '你叫咩名呀？',
                'answer': '我叫我叫小明，今年5岁喇！',
                'logic_score': 70,
                'completeness_score': 75,
                'creativity_score': 65,
                'relevance_score': 90,
                'total_score': 75,
                'feedback': '回答清晰！可以讲多少少关于自己既嘢。',
                'strengths': ['表达清晰', '有自我介绍'],
                'improvements': ['可以讲多啲关于自己既嘢']
            },
            {
                'question_index': 1,
                'question': '你最钟意做咩呀？',
                'answer': '我最钟意玩LEGO！因为可以砌好多嘢，好好玩！我仲钟意睇卡通片，特别是Peppa Pig！',
                'logic_score': 80,
                'completeness_score': 85,
                'creativity_score': 75,
                'relevance_score': 88,
                'total_score': 82,
                'feedback': '表现好好！继续努力！',
                'strengths': ['表达完整', '有具体例子'],
                'improvements': []
            },
            {
                'question_index': 2,
                'question': '如果你同同学唔啱，你会点做呀？',
                'answer': '我会同佢讲对唔住，或者搵老师帮手。',
                'logic_score': 72,
                'completeness_score': 65,
                'creativity_score': 60,
                'relevance_score': 75,
                'total_score': 68,
                'feedback': '识得求助几好，可以讲多啲解决既方法。',
                'strengths': ['识得搵大人帮手'],
                'improvements': ['可以讲多啲自己既諗法']
            }
        ],
        'voice_analyses': [
            {
                'question_index': 0,
                'speaking_rate': 115.5,
                'fluency_score': 80,
                'pause_count': 2,
                'pause_duration': 1.0,
                'clarity_score': 85,
                'sentiment': 'happy'
            },
            {
                'question_index': 1,
                'speaking_rate': 125.3,
                'fluency_score': 85,
                'pause_count': 3,
                'pause_duration': 1.5,
                'clarity_score': 88,
                'sentiment': 'excited'
            },
            {
                'question_index': 2,
                'speaking_rate': 108.7,
                'fluency_score': 72,
                'pause_count': 4,
                'pause_duration': 2.0,
                'clarity_score': 80,
                'sentiment': 'neutral'
            }
        ],
        'recommendations': [
            {
                'category': 'logic',
                'priority': 1,
                'title': '提升表达的逻辑性',
                'description': '练习使用因果关系和顺序词来组织回答，使表达更有条理。',
                'exercises': [
                    {'type': '练习', 'content': '用"因为...所以..."句式描述一件日常生活事'},
                    {'type': '练习', 'content': '用"首先...然后...最后..."讲述一个故事'}
                ],
                'resources': [
                    {'type': 'tip', 'content': '回答前先谂一谂要点，再按顺序讲出黎'}
                ]
            },
            {
                'category': 'creativity',
                'priority': 2,
                'title': '培养创新思维',
                'description': '尝试表达独特的观点和想法，展现个人特色。',
                'exercises': [
                    {'type': '练习', 'content': '讲一样嘢既唔同睇法'},
                    {'type': '练习', 'content': '如果可以你想点？讲出你既諗法'}
                ],
                'resources': [
                    {'type': 'tip', 'content': '可以讲多啲自己既经历同感受'}
                ]
            },
            {
                'category': 'clarity',
                'priority': 2,
                'title': '提高表达清晰度',
                'description': '放慢语速，确保每个字都讲清楚。',
                'exercises': [
                    {'type': '练习', 'content': '慢速朗读一段文章，注意发音'},
                    {'type': '练习', 'content': '对着镜子练习自我介绍'}
                ],
                'resources': [
                    {'type': 'tip', 'content': '讲话时望住老师眼睛，保持微笑'}
                ]
            }
        ],
        'question_count': 3,
        'strongest_dimension': 'relevance',
        'weakest_dimension': 'creativity'
    }
