-- Parent-Child Challenge Tables
-- 亲子共面挑战功能数据库表

-- 亲子挑战记录表
CREATE TABLE IF NOT EXISTS parent_child_challenges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_name VARCHAR(100) NOT NULL,
    challenge_type VARCHAR(50) NOT NULL, -- 'self_introduction', 'family', 'interests', etc.
    question TEXT NOT NULL,
    parent_answer TEXT,
    child_answer TEXT,
    parent_answer_audio_url VARCHAR(500),
    child_answer_audio_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 默契度评分表
CREATE TABLE IF NOT EXISTS challenge_scores (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES parent_child_challenges(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 默契度评分
    chemistry_score DECIMAL(5,2) DEFAULT 0, -- 0-100
    chemistry_level VARCHAR(20) DEFAULT 'bronze', -- 'bronze', 'silver', 'gold', 'diamond'
    
    -- 详细评分维度
    similarity_score DECIMAL(5,2) DEFAULT 0, -- 答案相似度
    cooperation_score DECIMAL(5,2) DEFAULT 0, -- 协作度
    communication_score DECIMAL(5,2) DEFAULT 0, -- 沟通质量
    creativity_score DECIMAL(5,2) DEFAULT 0, -- 创意表现
    
    -- AI 分析结果
    ai_analysis TEXT, -- AI 对比分析文本
    parent_feedback TEXT, -- 家长答案优化建议
    strengths JSONB, -- 优势列表
    improvements JSONB, -- 改进建议列表
    
    -- 勋章奖励
    badges_earned JSONB, -- 获得的勋章列表
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 亲子 PK 榜单表
CREATE TABLE IF NOT EXISTS challenge_leaderboard (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_name VARCHAR(100) NOT NULL,
    
    -- 统计信息
    total_challenges INTEGER DEFAULT 0, -- 总挑战次数
    completed_challenges INTEGER DEFAULT 0, -- 完成挑战数
    average_chemistry_score DECIMAL(5,2) DEFAULT 0, -- 平均默契度
    highest_score DECIMAL(5,2) DEFAULT 0, -- 最高默契度
    
    -- 排名信息
    total_badges INTEGER DEFAULT 0, -- 总勋章数
    rank_points INTEGER DEFAULT 0, -- 排名积分
    weekly_rank INTEGER, -- 周排名
    monthly_rank INTEGER, -- 月排名
    
    -- 时间周期
    period_type VARCHAR(20) DEFAULT 'all_time', -- 'weekly', 'monthly', 'all_time'
    period_start DATE,
    period_end DATE,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, period_type, period_start)
);

-- 合作勋章定义表
CREATE TABLE IF NOT EXISTS challenge_badges (
    id VARCHAR(50) PRIMARY KEY,
    name_zh VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    icon_emoji VARCHAR(10),
    category VARCHAR(50), -- 'cooperation', 'communication', 'creativity', 'milestone'
    requirement_type VARCHAR(50), -- 'challenge_completed', 'high_chemistry', 'perfect_score'
    requirement_value INTEGER,
    points INTEGER DEFAULT 0,
    rarity VARCHAR(20) DEFAULT 'common', -- 'common', 'rare', 'epic', 'legendary'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户合作勋章表
CREATE TABLE IF NOT EXISTS user_challenge_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id VARCHAR(50) NOT NULL REFERENCES challenge_badges(id),
    challenge_id INTEGER REFERENCES parent_child_challenges(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress INTEGER DEFAULT 0,
    UNIQUE(user_id, badge_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_parent_child_challenges_user_id ON parent_child_challenges(user_id);
CREATE INDEX IF NOT EXISTS idx_parent_child_challenges_status ON parent_child_challenges(status);
CREATE INDEX IF NOT EXISTS idx_challenge_scores_challenge_id ON challenge_scores(challenge_id);
CREATE INDEX IF NOT EXISTS idx_challenge_scores_user_id ON challenge_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_challenge_leaderboard_user_id ON challenge_leaderboard(user_id);
CREATE INDEX IF NOT EXISTS idx_challenge_leaderboard_period ON challenge_leaderboard(period_type, period_start);
CREATE INDEX IF NOT EXISTS idx_user_challenge_badges_user_id ON user_challenge_badges(user_id);

-- 插入合作勋章定义
INSERT INTO challenge_badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity) VALUES
-- 协作勋章
('first_teamwork', '第一次合作', 'First Teamwork', '完成第一次亲子共面挑战', '🤝', 'cooperation', 'challenge_completed', 1, 10, 'common'),
('team_player', '协作小能手', 'Team Player', '完成 5 次亲子挑战', '👫', 'cooperation', 'challenge_completed', 5, 20, 'rare'),
('perfect_partnership', '完美搭档', 'Perfect Partnership', '连续 3 次获得高默契度评价', '💯', 'cooperation', 'high_chemistry', 3, 30, 'epic'),
-- 沟通勋章
('good_communicator', '沟通小达人', 'Good Communicator', '沟通维度获得 80 分以上', '💬', 'communication', 'high_score', 80, 15, 'common'),
('story_master', '故事大师', 'Story Master', '创意维度获得 90 分以上', '📖', 'creativity', 'high_score', 90, 25, 'rare'),
-- 里程碑勋章
('week_champion', '週冠军', 'Week Champion', '一周内完成 7 次挑战', '🏆', 'milestone', 'weekly_challenges', 7, 50, 'rare'),
('month_master', '月冠军', 'Month Master', '一月内完成 30 次挑战', '👑', 'milestone', 'monthly_challenges', 30, 100, 'legendary'),
('chemistry_expert', '默契大师', 'Chemistry Expert', '累计默契度达到 500 分', '⭐', 'milestone', 'total_chemistry', 500, 40, 'epic');

-- 插入初始排行榜数据函数
CREATE OR REPLACE FUNCTION update_challenge_leaderboard()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新用户排行榜统计
    INSERT INTO challenge_leaderboard (user_id, child_name, total_challenges, completed_challenges, average_chemistry_score, highest_score, total_badges, rank_points, period_type, period_start, period_end, updated_at)
    SELECT 
        pcc.user_id,
        pcc.child_name,
        COUNT(DISTINCT pcc.id),
        COUNT(DISTINCT CASE WHEN pcc.status = 'completed' THEN pcc.id END),
        COALESCE(AVG(cs.chemistry_score), 0),
        COALESCE(MAX(cs.chemistry_score), 0),
        (SELECT COUNT(*) FROM user_challenge_badges ucb WHERE ucb.user_id = pcc.user_id),
        (SELECT COALESCE(SUM(cs.chemistry_score), 0) FROM challenge_scores cs 
         JOIN parent_child_challenges pcc2 ON cs.challenge_id = pcc2.id 
         WHERE pcc2.user_id = pcc.user_id),
        'all_time',
        DATE_TRUNC('month', CURRENT_DATE),
        NULL,
        CURRENT_TIMESTAMP
    FROM parent_child_challenges pcc
    LEFT JOIN challenge_scores cs ON pcc.id = cs.challenge_id
    WHERE pcc.user_id = NEW.user_id
    GROUP BY pcc.user_id, pcc.child_name
    ON CONFLICT (user_id, period_type, period_start) 
    DO UPDATE SET
        total_challenges = EXCLUDED.total_challenges,
        completed_challenges = EXCLUDED.completed_challenges,
        average_chemistry_score = EXCLUDED.average_chemistry_score,
        highest_score = EXCLUDED.highest_score,
        total_badges = EXCLUDED.total_badges,
        rank_points = EXCLUDED.rank_points,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_leaderboard_after_challenge
AFTER INSERT OR UPDATE ON parent_child_challenges
FOR EACH ROW
EXECUTE FUNCTION update_challenge_leaderboard();

CREATE TRIGGER trigger_update_leaderboard_after_score
AFTER INSERT OR UPDATE ON challenge_scores
FOR EACH ROW
EXECUTE FUNCTION update_challenge_leaderboard();
