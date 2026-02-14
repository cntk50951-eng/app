-- 家长协作空间与社群数据库表结构
-- 创建时间: 2026-02-14

-- 问题表
CREATE TABLE IF NOT EXISTS community_questions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    answer_count INTEGER DEFAULT 0,
    is_resolved BOOLEAN DEFAULT FALSE,
    best_answer_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_user ON community_questions(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_category ON community_questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_created ON community_questions(created_at DESC);

-- 回答表
CREATE TABLE IF NOT EXISTS community_answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES community_questions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_best_answer BOOLEAN DEFAULT FALSE,
    like_count INTEGER DEFAULT 0,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_answers_question ON community_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_answers_user ON community_answers(user_id);

-- 回答点赞表
CREATE TABLE IF NOT EXISTS answer_likes (
    id SERIAL PRIMARY KEY,
    answer_id INTEGER REFERENCES community_answers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(answer_id, user_id)
);

-- 问题收藏表
CREATE TABLE IF NOT EXISTS question_favorites (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES community_questions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(question_id, user_id)
);

-- 经验文章表
CREATE TABLE IF NOT EXISTS experience_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    cover_image VARCHAR(500),
    tags VARCHAR(255),
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_posts_user ON experience_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created ON experience_posts(created_at DESC);

-- 文章点赞表
CREATE TABLE IF NOT EXISTS post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES experience_posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

-- 文章收藏表
CREATE TABLE IF NOT EXISTS post_favorites (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES experience_posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

-- 文章评论表
CREATE TABLE IF NOT EXISTS post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES experience_posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试案例表
CREATE TABLE IF NOT EXISTS interview_cases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    school_name VARCHAR(200) NOT NULL,
    school_type VARCHAR(50) NOT NULL,
    interview_date DATE NOT NULL,
    questions JSONB NOT NULL,
    key_points TEXT,
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    review_content TEXT NOT NULL,
    helpful_count INTEGER DEFAULT 0,
    report_count INTEGER DEFAULT 0,
    is_anonymous BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cases_school ON interview_cases(school_name);
CREATE INDEX IF NOT EXISTS idx_cases_type ON interview_cases(school_type);
CREATE INDEX IF NOT EXISTS idx_cases_date ON interview_cases(interview_date DESC);

-- 面试案例有帮助表
CREATE TABLE IF NOT EXISTS case_helpful (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES interview_cases(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, user_id)
);

-- 面试案例收藏表
CREATE TABLE IF NOT EXISTS case_favorites (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES interview_cases(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, user_id)
);

-- 学习目标表
CREATE TABLE IF NOT EXISTS learning_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    child_profile_id INTEGER REFERENCES child_profiles(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    goal_type VARCHAR(50) NOT NULL,
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    period VARCHAR(20) NOT NULL,
    deadline DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_goals_user ON learning_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_child ON learning_goals(child_profile_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON learning_goals(status);

-- 目标进度记录表
CREATE TABLE IF NOT EXISTS goal_progress (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES learning_goals(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    value INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(goal_id, date)
);

-- 鼓励留言表
CREATE TABLE IF NOT EXISTS encouragement_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    child_profile_id INTEGER REFERENCES child_profiles(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
