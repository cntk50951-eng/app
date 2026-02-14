-- AI Micro Lesson Workshop Database Tables
-- Run this script to create tables for micro-lesson functionality

-- Micro Lessons table - stores AI-generated micro lessons
CREATE TABLE IF NOT EXISTS micro_lessons (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    title_en VARCHAR(200),
    description TEXT,
    content TEXT NOT NULL, -- The lesson content (script for the micro lesson)
    duration_seconds INTEGER DEFAULT 60, -- Duration in seconds (60-180)
    difficulty VARCHAR(20) DEFAULT 'easy', -- 'easy', 'medium', 'hard'
    topic VARCHAR(100), -- Topic category
    target_age_min INTEGER,
    target_age_max INTEGER,
    thumbnail_url TEXT,
    video_url TEXT,
    audio_url TEXT,
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'ready', 'completed'
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Learning Progress - tracks user's progress on micro lessons
CREATE TABLE IF NOT EXISTS user_learning_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES micro_lessons(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
    progress_percent INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    last_position_seconds INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, lesson_id)
);

-- Daily Tasks - stores daily learning tasks for users
CREATE TABLE IF NOT EXISTS daily_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_date DATE NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- 'micro_lesson', 'quick_practice', 'voice_repeat', 'scenario_simulation'
    task_title VARCHAR(200) NOT NULL,
    task_description TEXT,
    difficulty VARCHAR(20) DEFAULT 'easy',
    duration_seconds INTEGER DEFAULT 60,
    target_lesson_id INTEGER REFERENCES micro_lessons(id) ON DELETE SET NULL,
    target_topic VARCHAR(100),
    points INTEGER DEFAULT 10,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'skipped'
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, task_date, task_type)
);

-- Practice Sessions - records for fragmentized practice activities
CREATE TABLE IF NOT EXISTS practice_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'quick_qa', 'voice_repeat', 'scenario_simulation'
    topic_id VARCHAR(100),
    lesson_id INTEGER REFERENCES micro_lessons(id) ON DELETE SET NULL,
    duration_seconds INTEGER NOT NULL,
    time_limit_seconds INTEGER NOT NULL, -- 60, 90, or 120 seconds
    score INTEGER,
    max_score INTEGER,
    correct_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    answers JSONB, -- Store Q&A pairs
    audio_url TEXT,
    transcript TEXT,
    feedback TEXT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lesson Favorites - user's favorite micro lessons
CREATE TABLE IF NOT EXISTS lesson_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES micro_lessons(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, lesson_id)
);

-- Lesson Ratings - user ratings for lessons
CREATE TABLE IF NOT EXISTS lesson_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES micro_lessons(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, lesson_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_micro_lessons_user_id ON micro_lessons(user_id);
CREATE INDEX IF NOT EXISTS idx_micro_lessons_topic ON micro_lessons(topic);
CREATE INDEX IF NOT EXISTS idx_micro_lessons_status ON micro_lessons(status);
CREATE INDEX IF NOT EXISTS idx_user_learning_progress_user_id ON user_learning_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_learning_progress_lesson_id ON user_learning_progress(lesson_id);
CREATE INDEX IF NOT EXISTS idx_daily_tasks_user_date ON daily_tasks(user_id, task_date);
CREATE INDEX IF NOT EXISTS idx_daily_tasks_status ON daily_tasks(status);
CREATE INDEX IF NOT EXISTS idx_practice_sessions_user_id ON practice_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_practice_sessions_type ON practice_sessions(session_type);
