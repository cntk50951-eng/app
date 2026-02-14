-- AI Tutor 数据备份
-- 备份时间: 2026-02-14
--

-- 数据: interests
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('dinosaurs', '恐龍', '🦕', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('lego', 'Lego', '🧱', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('art', '畫畫', '🎨', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('sports', '運動', '⚽', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('music', '音樂', '🎵', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('reading', '閱讀', '📚', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('science', '科學', '🔬', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('cooking', '煮飯仔', '🍳', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('cars', '車', '🚗', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('planes', '飛機', '✈️', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('animals', '動物', '🐶', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('nature', '大自然', '🌳', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('performing', '表演', '🎭', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('gaming', '遊戲', '🎮', 2026-02-08 10:53:43.359414);
INSERT INTO interests (id, name_zh, emoji, created_at) VALUES ('swimming', '游泳', '🏊', 2026-02-08 10:53:43.359414);

-- 数据: school_types
INSERT INTO school_types (id, name_zh, examples, created_at) VALUES ('academic', '學術型', 'DBS/SPCC', 2026-02-08 10:53:43.359414);
INSERT INTO school_types (id, name_zh, examples, created_at) VALUES ('holistic', '全人型', '英華/TSL', 2026-02-08 10:53:43.359414);
INSERT INTO school_types (id, name_zh, examples, created_at) VALUES ('international', '國際型', 'CKY/港同', 2026-02-08 10:53:43.359414);
INSERT INTO school_types (id, name_zh, examples, created_at) VALUES ('traditional', '傳統名校', 'KTS/SFA', 2026-02-08 10:53:43.359414);

-- 数据: badges
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('first_step', '第一步', 'First Step', '完成第一個面試主題', '🌟', 'achievement', 'topics_completed', 1, 10, 'common', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('expression_master', '表達大師', 'Expression Master', '完成5次表達類主題練習', '🎤', 'achievement', 'practice_count', 5, 20, 'rare', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('logic_genius', '邏輯小天才', 'Logic Genius', '完成所有邏輯思維主題', '🧠', 'achievement', 'topics_completed', 3, 30, 'rare', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('polite_star', '禮貌之星', 'Polite Star', '連續3次練習使用禮貌用語', '🙇', 'achievement', 'streak_days', 3, 15, 'common', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('diligent_practitioner', '勤奮練習者', 'Diligent Practitioner', '一週內完成10次練習', '📚', 'achievement', 'practice_count', 10, 25, 'rare', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('week_warrior', '週冠軍', 'Week Warrior', '連續練習7天', '🔥', 'milestone', 'streak_days', 7, 50, 'rare', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('month_master', '月冠軍', 'Month Master', '連續練習30天', '👑', 'milestone', 'streak_days', 30, 100, 'legendary', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('streak_3', '小試牛刀', 'Streak Starter', '連續練習3天', '💪', 'streak', 'streak_days', 3, 10, 'common', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('streak_5', '五天不懈', 'Five Day Fighter', '連續練習5天', '⭐', 'streak', 'streak_days', 5, 15, 'common', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('streak_10', '十天突破', 'Ten Day Champion', '連續練習10天', '🏆', 'streak', 'streak_days', 10, 30, 'rare', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('interview_master', '面試大師', 'Interview Master', '完成所有9個面試主題', '🎓', 'master', 'topics_completed', 9, 100, 'legendary', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('perfect_score', '滿分達人', 'Perfect Score', '獲得3次滿分評價', '💯', 'master', 'perfect_score', 3, 40, 'epic', 2026-02-13 06:52:53.826140);
INSERT INTO badges (id, name_zh, name_en, description, icon_emoji, category, requirement_type, requirement_value, points, rarity, created_at) VALUES ('explorer', '勇敢探索者', 'Explorer', '嘗試至少5個不同主題', '🗺️', 'master', 'topics_started', 5, 20, 'common', 2026-02-13 06:52:53.826140);