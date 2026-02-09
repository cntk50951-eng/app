"""
PDF Generator Service - 练习报告导出
"""

from datetime import datetime
import os

REPORTS_DIR = "/Users/yuki/.openclaw/workspace/data/reports"

def generate_practice_report(user_data, progress_data):
    """生成练习报告."""
    stats = progress_data.get('stats', {})
    topics = progress_data.get('topics', {})
    
    report = f"""
╔══════════════════════════════════════╗
║       AI Tutor - 練習報告           ║
╚══════════════════════════════════════╝

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}

╔══════════════════════════════════════╗
║         整體統計                     ║
╚══════════════════════════════════════╝

總練習次數: {stats.get('total_practice', 0)}
完成主題數: {stats.get('total_complete', 0)}
平均評分: {stats.get('average_score', 0):.1f}
涵蓋主題: {stats.get('topics_count', 0)}

╔══════════════════════════════════════╗
║         各主題進度                  ║
╚══════════════════════════════════════╝
"""
    
    topic_names = {
        'self-introduction': '自我介紹',
        'interests': '興趣愛好',
        'family': '家庭介紹',
        'observation': '觀察力',
        'scenarios': '情境對話'
    }
    
    for topic_id, topic in topics.items():
        name = topic_names.get(topic_id, topic_id)
        scores = topic.get('scores', [])
        avg = sum(scores) / len(scores) if scores else 0
        
        report += f"""
{name}:
  練習次數: {topic.get('practice_count', 0)}
  完成次數: {topic.get('complete_count', 0)}
  平均評分: {avg:.1f}
"""
    
    report += f"""
╔══════════════════════════════════════╗
║       報告由 AI Tutor 生成          ║
╚══════════════════════════════════════╝
"""
    
    return report

def save_report(report, user_id):
    """保存报告."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"{REPORTS_DIR}/report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filename
