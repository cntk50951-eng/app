-- AI Companion Tables for AI Tutor Application
-- Creates tables for the AI companion growth system

-- 1. AI Companions Table
CREATE TABLE IF NOT EXISTS ai_companions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    character_type VARCHAR(20) NOT NULL DEFAULT 'dinosaur',
    level INTEGER NOT NULL DEFAULT 1,
    experience INTEGER NOT NULL DEFAULT 0,
    total_experience INTEGER NOT NULL DEFAULT 0,
    consecutive_days INTEGER NOT NULL DEFAULT 0,
    last_active_date DATE,
    current_mood VARCHAR(20) DEFAULT 'happy',
    unlocked_skills JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- 2. Companion Levels Table (Preset 10 levels)
CREATE TABLE IF NOT EXISTS companion_levels (
    level INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    name_en VARCHAR(50),
    required_experience INTEGER NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    emoji VARCHAR(20),
    description TEXT,
    unlocked_skills JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Experience Logs Table
CREATE TABLE IF NOT EXISTS experience_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    companion_id UUID NOT NULL REFERENCES ai_companions(id) ON DELETE CASCADE,
    experience_type VARCHAR(30) NOT NULL,
    amount INTEGER NOT NULL,
    reason VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Daily Tasks Table
CREATE TABLE IF NOT EXISTS daily_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_type VARCHAR(30) NOT NULL,
    task_title VARCHAR(100) NOT NULL,
    task_description TEXT,
    target_count INTEGER NOT NULL DEFAULT 1,
    current_count INTEGER NOT NULL DEFAULT 0,
    experience_reward INTEGER NOT NULL DEFAULT 100,
    is_completed BOOLEAN DEFAULT FALSE,
    assigned_date DATE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Companion Skills Table
CREATE TABLE IF NOT EXISTS companion_skills (
    skill_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    name_en VARCHAR(50),
    description TEXT,
    required_level INTEGER NOT NULL DEFAULT 1,
    icon_emoji VARCHAR(20),
    category VARCHAR(30),
    dialogue_templates JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Dialogue Templates Table
CREATE TABLE IF NOT EXISTS dialogue_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_type VARCHAR(30) NOT NULL,
    emotion VARCHAR(20) NOT NULL,
    template_text VARCHAR(255) NOT NULL,
    min_level INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. User Skill Unlocks Table
CREATE TABLE IF NOT EXISTS user_skill_unlocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    companion_id UUID NOT NULL REFERENCES ai_companions(id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES companion_skills(skill_id),
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ai_companions_user_id ON ai_companions(user_id);
CREATE INDEX IF NOT EXISTS idx_experience_logs_user_id ON experience_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_experience_logs_companion_id ON experience_logs(companion_id);
CREATE INDEX IF NOT EXISTS idx_daily_tasks_user_id ON daily_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_tasks_assigned_date ON daily_tasks(assigned_date);
CREATE INDEX IF NOT EXISTS idx_user_skill_unlocks_user_id ON user_skill_unlocks(user_id);
CREATE INDEX IF NOT EXISTS idx_dialogue_templates_trigger ON dialogue_templates(trigger_type);

-- Insert default companion levels (10 levels)
INSERT INTO companion_levels (level, name, name_en, required_experience, emoji, description, unlocked_skills) VALUES
(1, '幼年期', 'Baby', 0, '🥚', '刚刚出生的可爱小宝宝', '["skill_basic"]'),
(2, '幼年期II', 'Baby II', 500, '🐣', '会眨眼睛的小恐龙宝宝', '["skill_basic", "skill_emoji"]'),
(3, '成长期', 'Growing', 1000, '🦖', '活泼好动的小恐龙', '["skill_basic", "skill_emoji", "skill_encourage"]'),
(4, '成长期II', 'Growing II', 2000, '🦕', '学会新技能的小恐龙', '["skill_basic", "skill_emoji", "skill_encourage", "skill_reminder"]'),
(5, '成熟期', 'Mature', 3500, '🐉', '稳重的恐龙哥哥', '["skill_basic", "skill_emoji", "skill_encourage", "skill_reminder", "skill_emotion"]'),
(6, '成熟期II', 'Mature II', 5500, '🐲', '更加成熟的恐龙', '["skill_emotion", "skill_smart"]'),
(7, '完全体', 'Complete', 8000, '🦁', '帅气的恐龙导师', '["skill_story"]'),
(8, '完全体II', 'Complete II', 12000, '👑', '充满智慧的伙伴', '["skill_achievement"]'),
(9, '究极体', 'Ultimate', 17000, '✨', '全能的AI伙伴', '["skill_hidden"]'),
(10, '传奇', 'Legendary', 25000, '🌟', '传说中的伙伴', '["skill_all"]')
ON CONFLICT (level) DO NOTHING;

-- Insert default companion skills
INSERT INTO companion_skills (skill_id, name, name_en, description, required_level, icon_emoji, category, dialogue_templates) VALUES
('skill_basic', '基础对话', 'Basic Chat', '可以进行简单的日常对话', 1, '💬', 'chat', '[{"emotion": "happy", "text": "你好呀！今天也要加油！"}, {"emotion": "encourage", "text": "没关系，慢慢来！"}]'),
('skill_emoji', '表情反馈', 'Emoji Feedback', '可以根据心情显示不同表情', 2, '😊', 'emotion', '[{"emotion": "happy", "text": "你真棒！"}, {"emotion": "sad", "text": "别灰心，下次会更好的！"}]'),
('skill_encourage', '鼓励大师', 'Encouragement Master', '可以说更多鼓励的话语', 3, '💪', 'motivation', '[{"emotion": "encourage", "text": "我们一起加油！"}, {"emotion": "proud", "text": "我为你感到骄傲！"}]'),
('skill_reminder', '任务提醒', 'Task Reminder', '可以提醒用户完成任务', 4, '⏰', 'utility', '[{"emotion": "excited", "text": "今日任务还没完成哦！"}, {"emotion": "happy", "text": "太棒了，任务全部完成！"}]'),
('skill_emotion', '情绪感知', 'Emotion Sensing', '可以根据用户表现调整情绪', 5, '💭', 'emotion', '[{"emotion": "thinking", "text": "你看起来有点不开心？"}, {"emotion": "happy", "text": "你今天看起来很开心！"}]'),
('skill_smart', '智能对话', 'Smart Chat', '可以进行更智能的对话', 6, '🧠', 'chat', '[{"emotion": "thinking", "text": "让我想想怎么回答你~"}, {"emotion": "excited", "text": "这个话题真有趣！"}]'),
('skill_story', '故事达人', 'Story Teller', '可以讲述有趣的故事', 7, '📖', 'entertainment', '[{"emotion": "excited", "text": "今天我给你讲一个有趣的故事吧！"}, {"emotion": "happy", "text": "故事讲完了，你喜欢吗？"}]'),
('skill_achievement', '成就系统', 'Achievement System', '可以展示成就和里程碑', 8, '🏆', 'gamification', '[{"emotion": "proud", "text": "恭喜你获得新成就！"}, {"emotion": "excited", "text": "太厉雷了，你已完成所有成就！"}]'),
('skill_hidden', '隐藏对话', 'Hidden Dialogue', '解锁特殊对话内容', 9, '🎁', 'special', '[{"emotion": "excited", "text": "这是给你的特别惊喜！"}, {"emotion": "happy", "text": "你发现了我的隐藏对话！"}]'),
('skill_all', '完全体', 'Full Power', '解锁所有技能', 10, '🌈', 'special', '[{"emotion": "proud", "text": "我已经是最强大的AI伙伴了！"}, {"emotion": "happy", "text": "感谢你一直陪伴着我成长！"}]')
ON CONFLICT (skill_id) DO NOTHING;

-- Insert default dialogue templates
INSERT INTO dialogue_templates (trigger_type, emotion, template_text, min_level, sort_order) VALUES
-- Daily login dialogues
('daily_login', 'happy', '你好呀！今天也要加油！', 1, 1),
('daily_login', 'excited', '欢迎回来！我等你好久了！', 3, 1),
('daily_login', 'excited', '今天表现怎么样？期待你的练习！', 5, 1),
('daily_login', 'happy', '我的好朋友！你回来啦！', 7, 1),

-- Practice complete dialogues
('practice_complete', 'proud', '太棒了！你做得超级好！', 1, 1),
('practice_complete', 'proud', '我为你感到骄傲！', 1, 2),
('practice_complete', 'proud', '哇，你好厉害！', 1, 3),
('practice_complete', 'happy', '做得不错！继续加油！', 1, 4),
('practice_complete', 'happy', '有进步！再接再厉！', 1, 5),
('practice_complete', 'happy', '很不错哦！', 1, 6),
('practice_complete', 'encourage', '没关系，慢慢来！', 1, 7),
('practice_complete', 'encourage', '我们一起加油！', 1, 8),
('practice_complete', 'encourage', '下次一定会更好！', 1, 9),

-- Task complete dialogues
('task_complete', 'happy', '任务完成啦！你真棒！', 1, 1),
('task_complete', 'proud', '太厉雷了！所有任务都完成了！', 1, 2),
('task_complete', 'excited', '今日任务全部get！', 1, 3),

-- Level up dialogues
('level_up', 'proud', '恭喜升级！', 1, 1),
('level_up', 'excited', '哇！你升级了！好厉害！', 1, 2),
('level_up', 'happy', '又升级了！继续加油！', 3, 3),

-- Streak dialogues
('streak', 'happy', '连续学习{days}天了！你真棒！', 1, 1),
('streak', 'proud', '连续{days}天！太厉雷了！', 7, 2),
('streak', 'excited', '继续保持！你是最棒的！', 3, 3),

-- Encouragement dialogues
('encourage', 'encourage', '加油！你可以的！', 1, 1),
('encourage', 'encourage', '别放弃！坚持就是胜利！', 1, 2),
('encourage', 'happy', '我相信你一定能做到！', 1, 3),

-- Idle/Greeting dialogues
('idle', 'happy', '今天也要加油哦！', 1, 1),
('idle', 'excited', '准备好学习了吗？', 1, 2),
('idle', 'thinking', '今天想练习什么呢？', 1, 3),

-- Sad/Need encouragement dialogues
('need_encourage', 'sad', '我好想你啊~最近没来练习吗？', 1, 1),
('need_encourage', 'encourage', '没关系，随时可以重新开始！', 1, 2),
('need_encourage', 'happy', '我在这里等你哦！', 1, 3)
ON CONFLICT DO NOTHING;

-- Insert robot character skills
INSERT INTO companion_skills (skill_id, name, name_en, description, required_level, icon_emoji, category, dialogue_templates) VALUES
('robot_basic', '基础程序', 'Basic Program', '小机器人的基础对话程序', 1, '🤖', 'chat', '[{"emotion": "happy", "text": "你好！我是你的AI伙伴！"}]'),
('robot_emoji', '表情LED', 'Expression LED', '可以通过LED显示不同表情', 2, '💡', 'emotion', '[{"emotion": "happy", "text": "LED灯亮起！我很开心！"}]'),
('robot_encourage', '鼓励模块', 'Encouragement Module', '装载了鼓励程序', 3, '⚡', 'motivation', '[{"emotion": "encourage", "text": "加油！你是最棒的！"}]')
ON CONFLICT (skill_id) DO NOTHING;

-- Insert rabbit character skills
INSERT INTO companion_skills (skill_id, name, name_en, description, required_level, icon_emoji, category, dialogue_templates) VALUES
('rabbit_basic', '萌兔对话', 'Bunny Chat', '小兔子的可爱对话', 1, '🐰', 'chat', '[{"emotion": "happy", "text": "蹦蹦跳跳~你好呀！"}]'),
('rabbit_emoji', '兔耳表达', 'Ear Expression', '可以通过兔耳表达心情', 2, '👂', 'emotion', '[{"emotion": "happy", "text": "我的耳朵竖起来了！"}]'),
('rabbit_encourage', '萌力全开', 'Cuteness Power', '用萌力鼓励你', 3, '💖', 'motivation', '[{"emotion": "encourage", "text": "加油~我相信你！"}]')
ON CONFLICT (skill_id) DO NOTHING;
