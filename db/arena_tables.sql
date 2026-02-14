-- ========================================
-- AI Tutor Arena Challenge System Database Schema
-- ========================================

-- User Rank Table - stores user ranking and arena statistics
CREATE TABLE IF NOT EXISTS user_rank (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_rank VARCHAR(20) DEFAULT 'bronze',
    rank_points INTEGER DEFAULT 0,
    total_matches INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Rank Config Table - stores rank level configurations
CREATE TABLE IF NOT EXISTS rank_config (
    id SERIAL PRIMARY KEY,
    rank_id VARCHAR(20) UNIQUE NOT NULL,
    rank_name_zh VARCHAR(50) NOT NULL,
    rank_name_en VARCHAR(50) NOT NULL,
    rank_icon VARCHAR(10) NOT NULL,
    min_points INTEGER NOT NULL,
    max_points INTEGER NOT NULL,
    color_primary VARCHAR(20) NOT NULL,
    color_secondary VARCHAR(20) NOT NULL
);

-- Arena Match Table - stores match records
CREATE TABLE IF NOT EXISTS arena_match (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    opponent_type VARCHAR(10) NOT NULL DEFAULT 'ai',
    opponent_id INTEGER,
    opponent_name VARCHAR(100),
    opponent_avatar VARCHAR(20),
    difficulty VARCHAR(10) DEFAULT 'medium',
    category VARCHAR(50),
    match_type VARCHAR(20) NOT NULL DEFAULT 'challenge',
    time_limit INTEGER,
    user_score INTEGER DEFAULT 0,
    opponent_score INTEGER DEFAULT 0,
    user_correct INTEGER DEFAULT 0,
    user_total INTEGER DEFAULT 0,
    opponent_correct INTEGER DEFAULT 0,
    opponent_total INTEGER DEFAULT 0,
    result VARCHAR(10),
    points_earned INTEGER DEFAULT 0,
    coins_earned INTEGER DEFAULT 0,
    badges_earned TEXT,
    duration INTEGER,
    status VARCHAR(20) DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leaderboard Cache Table - stores cached leaderboard data
CREATE TABLE IF NOT EXISTS leaderboard_cache (
    id SERIAL PRIMARY KEY,
    period_type VARCHAR(10) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    rank_data TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period_type, period_start)
);

-- Coin Transaction Table - stores coin balance changes
CREATE TABLE IF NOT EXISTS coin_transaction (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    reference_id VARCHAR(50),
    balance_after INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reward Config Table - stores reward configurations
CREATE TABLE IF NOT EXISTS reward_config (
    id SERIAL PRIMARY KEY,
    reward_id VARCHAR(50) UNIQUE NOT NULL,
    reward_type VARCHAR(20) NOT NULL,
    reward_value VARCHAR(100) NOT NULL,
    condition_type VARCHAR(30) NOT NULL,
    condition_value VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);

-- User Coins Table - stores user coin balance
CREATE TABLE IF NOT EXISTS user_coins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Insert rank configurations
INSERT INTO rank_config (rank_id, rank_name_zh, rank_name_en, rank_icon, min_points, max_points, color_primary, color_secondary)
VALUES
    ('bronze', '青銅', 'Bronze', '🥉', 0, 999, '#cd7f32', '#8b4513'),
    ('silver', '白銀', 'Silver', '🥈', 1000, 2499, '#c0c0c0', '#a0a0a0'),
    ('gold', '黃金', 'Gold', '🥇', 2500, 4999, '#ffd700', '#ffa500'),
    ('platinum', '白金', 'Platinum', '💎', 5000, 9999, '#e5e4e2', '#b0b0b0'),
    ('diamond', '鑽石', 'Diamond', '💎', 10000, 19999, '#b9f2ff', '#89cff0'),
    ('master', '大師', 'Master', '👑', 20000, 999999, '#ff6b6b', '#ee5a5a')
ON CONFLICT (rank_id) DO NOTHING;

-- Insert reward configurations
INSERT INTO reward_config (reward_id, reward_type, reward_value, condition_type, condition_value, is_active)
VALUES
    ('match_win', 'coin', '50', 'match_result', 'win', true),
    ('match_lose', 'coin', '10', 'match_result', 'lose', true),
    ('match_draw', 'coin', '25', 'match_result', 'draw', true),
    ('match_win_easy', 'point', '10', 'match_difficulty', 'easy', true),
    ('match_win_medium', 'point', '25', 'match_difficulty', 'medium', true),
    ('match_win_hard', 'point', '50', 'match_difficulty', 'hard', true),
    ('match_lose_easy', 'point', '-5', 'match_difficulty', 'easy', true),
    ('match_lose_medium', 'point', '-10', 'match_difficulty', 'medium', true),
    ('match_lose_hard', 'point', '-15', 'match_difficulty', 'hard', true),
    ('timed_match', 'coin', '20', 'match_type', 'timed', true),
    ('timed_correct', 'coin', '2', 'match_type', 'timed_correct', true),
    ('streak_3', 'badge', 'arena_streak_3', 'streak', '3', true),
    ('streak_5', 'badge', 'arena_streak_5', 'streak', '5', true),
    ('streak_10', 'badge', 'arena_streak_10', 'streak', '10', true),
    ('first_match', 'badge', 'arena_first', 'milestone', 'first', true),
    ('win_10', 'badge', 'arena_win_10', 'milestone', 'win_10', true),
    ('win_50', 'badge', 'arena_win_50', 'milestone', 'win_50', true),
    ('win_100', 'badge', 'arena_win_100', 'milestone', 'win_100', true),
    ('perfect_match', 'badge', 'arena_perfect', 'milestone', 'perfect', true),
    ('timed_master', 'badge', 'arena_timed_master', 'milestone', 'timed_90', true)
ON CONFLICT (reward_id) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_arena_match_user_id ON arena_match(user_id);
CREATE INDEX IF NOT EXISTS idx_arena_match_created_at ON arena_match(created_at);
CREATE INDEX IF NOT EXISTS idx_arena_match_status ON arena_match(status);
CREATE INDEX IF NOT EXISTS idx_user_rank_points ON user_rank(rank_points DESC);
CREATE INDEX IF NOT EXISTS idx_coin_transaction_user_id ON coin_transaction(user_id);
