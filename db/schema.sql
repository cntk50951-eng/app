-- AI Tutor Database Schema
-- Run this script to create all required tables

-- Drop existing tables (in correct order for foreign key constraints)
DROP TABLE IF EXISTS user_badges CASCADE;
DROP TABLE IF EXISTS badges CASCADE;
DROP TABLE IF EXISTS learning_reports CASCADE;
DROP TABLE IF EXISTS practice_sessions CASCADE;
DROP TABLE IF EXISTS user_progress CASCADE;
DROP TABLE IF EXISTS user_interests CASCADE;
DROP TABLE IF EXISTS target_schools CASCADE;
DROP TABLE IF EXISTS child_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS interests CASCADE;
DROP TABLE IF EXISTS school_types CASCADE;

-- Reference table: Badge definitions
CREATE TABLE badges (
    id VARCHAR(50) PRIMARY KEY,
    name_zh VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    icon_emoji VARCHAR(10),
    category VARCHAR(50), -- 'achievement', 'milestone', 'streak', 'master'
    requirement_type VARCHAR(50), -- 'topics_completed', 'streak_days', 'practice_count', 'perfect_score'
    requirement_value INTEGER,
    points INTEGER DEFAULT 0,
    rarity VARCHAR(20) DEFAULT 'common', -- 'common', 'rare', 'epic', 'legendary'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User earned badges
CREATE TABLE user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id VARCHAR(50) NOT NULL REFERENCES badges(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress INTEGER DEFAULT 0, -- Progress towards the badge (0-100)
    UNIQUE(user_id, badge_id)
);

-- User progress tracking
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
    completion_percent INTEGER DEFAULT 0,
    practice_count INTEGER DEFAULT 0,
    best_score INTEGER,
    total_time_seconds INTEGER DEFAULT 0,
    last_practiced_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, topic_id)
);

-- Practice sessions
CREATE TABLE practice_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id VARCHAR(50) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    score INTEGER,
    feedback_rating INTEGER, -- 1-5 stars
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning reports (weekly/monthly)
CREATE TABLE learning_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(20) NOT NULL, -- 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    topics_completed INTEGER DEFAULT 0,
    total_practice_time INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    streak_days INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0,
    highlights TEXT,
    improvements TEXT,
    recommendation TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reference table: Interest options
CREATE TABLE interests (
    id VARCHAR(50) PRIMARY KEY,
    name_zh VARCHAR(100) NOT NULL,
    emoji VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reference table: School type options
CREATE TABLE school_types (
    id VARCHAR(50) PRIMARY KEY,
    name_zh VARCHAR(100) NOT NULL,
    examples VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table - stores user login information
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    picture VARCHAR(500),
    user_type VARCHAR(20) NOT NULL DEFAULT 'email', -- 'email' or 'google'
    google_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Child profiles table - stores child's basic information
CREATE TABLE child_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_name VARCHAR(100) NOT NULL,
    child_age VARCHAR(20) NOT NULL, -- K1, K2, K3
    child_gender VARCHAR(20),
    profile_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table: User interests (many-to-many)
CREATE TABLE user_interests (
    id SERIAL PRIMARY KEY,
    child_profile_id INTEGER NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    interest_id VARCHAR(50) NOT NULL REFERENCES interests(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(child_profile_id, interest_id)
);

-- Junction table: User target schools (many-to-many)
CREATE TABLE target_schools (
    id SERIAL PRIMARY KEY,
    child_profile_id INTEGER NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    school_type_id VARCHAR(50) NOT NULL REFERENCES school_types(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(child_profile_id, school_type_id)
);

-- Insert interest options
INSERT INTO interests (id, name_zh, emoji) VALUES
('dinosaurs', '恐龍', '🦕'),
('lego', 'Lego', '🧱'),
('art', '畫畫', '🎨'),
('sports', '運動', '⚽'),
('music', '音樂', '🎵'),
('reading', '閱讀', '📚'),
('science', '科學', '🔬'),
('cooking', '煮飯仔', '🍳'),
('cars', '車', '🚗'),
('planes', '飛機', '✈️'),
('animals', '動物', '🐶'),
('nature', '大自然', '🌳'),
('performing', '表演', '🎭'),
('gaming', '遊戲', '🎮'),
('swimming', '游泳', '🏊');

-- Insert school type options
INSERT INTO school_types (id, name_zh, examples) VALUES
('academic', '學術型', 'DBS/SPCC'),
('holistic', '全人型', '英華/TSL'),
('international', '國際型', 'CKY/港同'),
('traditional', '傳統名校', 'KTS/SFA');

-- Create indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_child_profiles_user_id ON child_profiles(user_id);
CREATE INDEX idx_user_interests_profile_id ON user_interests(child_profile_id);
CREATE INDEX idx_target_schools_profile_id ON target_schools(child_profile_id);
CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_practice_sessions_user_id ON practice_sessions(user_id);
CREATE INDEX idx_learning_reports_user_id ON learning_reports(user_id);

-- Insert badge definitions
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity) VALUES
-- Achievement badges
('first_step', '第一步', 'First Step', '完成第一個面試主題', '🌟', 'achievement', 'topics_completed', 1, 10, 'common'),
('expression_master', '表達大師', 'Expression Master', '完成5次表達類主題練習', '🎤', 'achievement', 'practice_count', 5, 20, 'rare'),
('logic_genius', '邏輯小天才', 'Logic Genius', '完成所有邏輯思維主題', '🧠', 'achievement', 'topics_completed', 3, 30, 'rare'),
('polite_star', '禮貌之星', 'Polite Star', '連續3次練習使用禮貌用語', '🙇', 'achievement', 'streak_days', 3, 15, 'common'),
('diligent_practitioner', '勤奮練習者', 'Diligent Practitioner', '一週內完成10次練習', '📚', 'achievement', 'practice_count', 10, 25, 'rare'),
-- Milestone badges
('week_warrior', '週冠軍', 'Week Warrior', '連續練習7天', '🔥', 'milestone', 'streak_days', 7, 50, 'rare'),
('month_master', '月冠軍', 'Month Master', '連續練習30天', '👑', 'milestone', 'streak_days', 30, 100, 'legendary'),
-- Streak badges
('streak_3', '小試牛刀', 'Streak Starter', '連續練習3天', '💪', 'streak', 'streak_days', 3, 10, 'common'),
('streak_5', '五天不懈', 'Five Day Fighter', '連續練習5天', '⭐', 'streak', 'streak_days', 5, 15, 'common'),
('streak_10', '十天突破', 'Ten Day Champion', '連續練習10天', '🏆', 'streak', 'streak_days', 10, 30, 'rare'),
-- Master badges
('interview_master', '面試大師', 'Interview Master', '完成所有9個面試主題', '🎓', 'master', 'topics_completed', 9, 100, 'legendary'),
('perfect_score', '滿分達人', 'Perfect Score', '獲得3次滿分評價', '💯', 'master', 'perfect_score', 3, 40, 'epic'),
('explorer', '勇敢探索者', 'Explorer', '嘗試至少5個不同主題', '🗺️', 'master', 'topics_started', 5, 20, 'common');

-- Comments
COMMENT ON TABLE users IS 'Stores user authentication information';
COMMENT ON TABLE child_profiles IS 'Stores child profile information linked to users';
COMMENT ON TABLE interests IS 'Reference table for interest options';
COMMENT ON TABLE school_types IS 'Reference table for school type options';
COMMENT ON TABLE user_interests IS 'Links child profiles to interests';
COMMENT ON TABLE target_schools IS 'Links child profiles to target school types';
COMMENT ON TABLE badges IS 'Achievement badge definitions';
COMMENT ON TABLE user_badges IS 'User earned badges';
COMMENT ON TABLE user_progress IS 'User learning progress by topic';
COMMENT ON TABLE practice_sessions IS 'Practice session history';
COMMENT ON TABLE learning_reports IS 'Generated learning reports';

-- Interview Question Bank
-- 面试真题库 - 存储各类面试题目
CREATE TABLE interview_questions (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'self_intro', 'family', 'hobbies', 'school', 'life', 'science', 'society', 'creative', 'situational', 'group'
    category_name_zh VARCHAR(100) NOT NULL,
    question_zh TEXT NOT NULL,
    question_en TEXT,
    answer_tips TEXT,
    school_types VARCHAR(100), -- comma-separated: academic,holistic,international,traditional
    frequency VARCHAR(20) DEFAULT 'medium', -- 'high', 'medium', 'low'
    difficulty VARCHAR(20) DEFAULT 'medium', -- 'easy', 'medium', 'hard'
    language VARCHAR(20) DEFAULT 'both', -- 'zh', 'en', 'both'
    age_group VARCHAR(20) DEFAULT 'K3', -- 'K1', 'K2', 'K3'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question practice history
CREATE TABLE question_practice_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL,
    practiced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_answer TEXT,
    needs_review BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_questions_category ON interview_questions(category);
CREATE INDEX idx_questions_school_types ON interview_questions(school_types);
CREATE INDEX idx_questions_frequency ON interview_questions(frequency);
CREATE INDEX idx_practice_history_user ON question_practice_history(user_id);

-- ============ 练习数据扩展 ============

-- 用户收藏的题目
CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, question_id)
);

-- 用户错题记录
CREATE TABLE user_wrong_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL,
    times_wrong INTEGER DEFAULT 1,
    last_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mastered BOOLEAN DEFAULT FALSE, -- 是否已掌握
    mastered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, question_id)
);

-- 用户分类练习进度
CREATE TABLE category_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    total_practiced INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    last_practiced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category)
);

-- 每日挑战记录
CREATE TABLE daily_challenges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_date DATE NOT NULL,
    questions_completed INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 10,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, challenge_date)
);

-- 用户练习统计
CREATE TABLE user_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_practice_count INTEGER DEFAULT 0,
    total_questions_answered INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_practice_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

CREATE INDEX idx_favorites_user ON user_favorites(user_id);
CREATE INDEX idx_wrong_user ON user_wrong_answers(user_id);
CREATE INDEX idx_category_progress_user ON category_progress(user_id);
CREATE INDEX idx_daily_challenge_user ON daily_challenges(user_id, challenge_date);
CREATE INDEX idx_user_stats_user ON user_stats(user_id);

-- 学习成果社交秀分享记录表
CREATE TABLE IF NOT EXISTS showcase_shares (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    poster_type VARCHAR(50) NOT NULL,
    poster_data JSONB,
    platform VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_showcase_shares_user ON showcase_shares(user_id);
CREATE INDEX idx_showcase_shares_created ON showcase_shares(created_at);

-- ============================================
-- AI面试复盘室表结构
-- ============================================

-- 面试复盘主表
CREATE TABLE IF NOT EXISTS debrief_sessions (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    interview_session_id VARCHAR(100),
    interview_type VARCHAR(50) NOT NULL DEFAULT 'mock',
    school_type VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    duration_seconds INTEGER,
    total_questions INTEGER DEFAULT 0,
    overall_score INTEGER,
    status VARCHAR(20) DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 语音表现分析表
CREATE TABLE IF NOT EXISTS debrief_voice_analysis (
    id UUID PRIMARY KEY,
    debrief_session_id UUID REFERENCES debrief_sessions(id) ON DELETE CASCADE,
    question_index INTEGER,
    speaking_rate_words_per_minute DECIMAL(5,2),
    fluency_score INTEGER,
    pause_count INTEGER,
    pause_duration_seconds DECIMAL(6,2),
    clarity_score INTEGER,
    sentiment VARCHAR(20),
    audio_duration_seconds DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 内容维度分析表
CREATE TABLE IF NOT EXISTS debrief_content_analysis (
    id UUID PRIMARY KEY,
    debrief_session_id UUID REFERENCES debrief_sessions(id) ON DELETE CASCADE,
    question_index INTEGER,
    question TEXT,
    answer TEXT,
    logic_score INTEGER,
    completeness_score INTEGER,
    creativity_score INTEGER,
    relevance_score INTEGER,
    total_score INTEGER,
    feedback TEXT,
    strengths TEXT[],
    improvements TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 改进建议表
CREATE TABLE IF NOT EXISTS debrief_recommendations (
    id UUID PRIMARY KEY,
    debrief_session_id UUID REFERENCES debrief_sessions(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 1,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    exercises JSONB,
    resources JSONB,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 历史对比数据表
CREATE TABLE IF NOT EXISTS debrief_comparison (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    comparison_type VARCHAR(50) NOT NULL,
    period_start DATE,
    period_end DATE,
    data JSONB NOT NULL,
    insights TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_debrief_sessions_user ON debrief_sessions(user_id);
CREATE INDEX idx_debrief_sessions_status ON debrief_sessions(status);
CREATE INDEX idx_debrief_sessions_created ON debrief_sessions(created_at);
CREATE INDEX idx_debrief_voice_analysis_session ON debrief_voice_analysis(debrief_session_id);
CREATE INDEX idx_debrief_content_analysis_session ON debrief_content_analysis(debrief_session_id);
CREATE INDEX idx_debrief_recommendations_session ON debrief_recommendations(debrief_session_id);
CREATE INDEX idx_debrief_comparison_user ON debrief_comparison(user_id);
