-- AI Tutor Database Schema
-- Run this script to create all required tables

-- Drop existing tables (in correct order for foreign key constraints)
DROP TABLE IF EXISTS user_interests CASCADE;
DROP TABLE IF EXISTS target_schools CASCADE;
DROP TABLE IF EXISTS child_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS interests CASCADE;
DROP TABLE IF EXISTS school_types CASCADE;

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

-- Comments
COMMENT ON TABLE users IS 'Stores user authentication information';
COMMENT ON TABLE child_profiles IS 'Stores child profile information linked to users';
COMMENT ON TABLE interests IS 'Reference table for interest options';
COMMENT ON TABLE school_types IS 'Reference table for school type options';
COMMENT ON TABLE user_interests IS 'Links child profiles to interests';
COMMENT ON TABLE target_schools IS 'Links child profiles to target school types';
