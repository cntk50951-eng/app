-- ============================================================
-- 目标学校智能题库 - 数据库表
-- ============================================================

-- 学校信息表
DROP TABLE IF EXISTS schools CASCADE;
CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    name_zh VARCHAR(200) NOT NULL,           -- 学校中文名称
    name_en VARCHAR(200),                    -- 学校英文名称
    district VARCHAR(50),                     -- 区域
    school_type VARCHAR(50) NOT NULL,        -- 学校类型: primary, secondary
    category VARCHAR(50),                     -- 类别: academic, holistic, international, traditional
    description TEXT,                        -- 学校简介
    admission_requirements TEXT,              -- 入学要求
    interview_format TEXT,                   -- 面试形式
    tuition_fee VARCHAR(100),                -- 学费
    location VARCHAR(200),                   -- 地址
    website VARCHAR(200),                    -- 官方网站
    image_url VARCHAR(500),                  -- 学校图片
    ranking INT,                             -- 排名
    is_featured BOOLEAN DEFAULT FALSE,       -- 是否推荐
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学校真题关联表
DROP TABLE IF EXISTS school_question_bank CASCADE;
CREATE TABLE school_question_bank (
    id SERIAL PRIMARY KEY,
    school_id INT NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    question_id INT,                         -- 关联的面试问题ID (可选)
    question_text TEXT NOT NULL,             -- 真题内容
    question_type VARCHAR(50) NOT NULL,      -- 题型: self_intro, family, hobbies, school, life, science, society, creative, situational, group, math, language, logic
    difficulty VARCHAR(20) DEFAULT 'medium', -- 难度: easy, medium, hard
    category VARCHAR(50),                   -- 分类标签
    year INT,                                -- 年份
    source VARCHAR(200),                    -- 来源
    sample_answer TEXT,                      -- 参考答案
    tips TEXT,                               -- 解题技巧
    is_featured BOOLEAN DEFAULT FALSE,       -- 是否精选
    view_count INT DEFAULT 0,                -- 查看次数
    like_count INT DEFAULT 0,                -- 点赞次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试时间线表
DROP TABLE IF EXISTS interview_timeline CASCADE;
CREATE TABLE interview_timeline (
    id SERIAL PRIMARY KEY,
    school_id INT NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    year INT NOT NULL,                       -- 年份
    stage VARCHAR(100) NOT NULL,              -- 阶段: 报名, 第一轮, 第二轮, 录取通知
    stage_order INT NOT NULL,                 -- 阶段顺序
    start_date DATE,                          -- 开始日期
    end_date DATE,                            -- 结束日期
    description TEXT,                        -- 说明
    tips TEXT,                               -- 注意事项
    is_estimated BOOLEAN DEFAULT FALSE,      -- 是否为预估时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试经验分享表
DROP TABLE IF EXISTS interview_experience CASCADE;
CREATE TABLE interview_experience (
    id SERIAL PRIMARY KEY,
    user_id INT,                              -- 发布用户 (可选)
    school_id INT REFERENCES schools(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,             -- 标题
    content TEXT NOT NULL,                   -- 内容
    author_name VARCHAR(100),                -- 作者名称
    author_type VARCHAR(50),                 -- 作者身份: parent, student, alumni
    child_grade VARCHAR(20),                 -- 孩子年级
    interview_result VARCHAR(50),            -- 面试结果: admitted, waitlisted, rejected
    tags VARCHAR(200),                       -- 标签
    view_count INT DEFAULT 0,                -- 查看次数
    like_count INT DEFAULT 0,                -- 点赞次数
    is_published BOOLEAN DEFAULT TRUE,       -- 是否发布
    is_featured BOOLEAN DEFAULT FALSE,       -- 是否精选
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户收藏真题表
DROP TABLE IF EXISTS user_favorite_questions CASCADE;
CREATE TABLE user_favorite_questions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    question_bank_id INT NOT NULL REFERENCES school_question_bank(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, question_bank_id)
);

-- 用户AI匹配记录表
DROP TABLE IF EXISTS ai_match_records CASCADE;
CREATE TABLE ai_match_records (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    school_id INT REFERENCES schools(id) ON DELETE SET NULL,
    child_profile_id INT,
    match_score FLOAT,                       -- 匹配度
    recommended_questions JSONB,             -- 推荐的题目
    strengths TEXT,                          -- 优势分析
    weaknesses TEXT,                          -- 需改进
    suggestions TEXT,                        -- 建议
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 索引
-- ============================================================
CREATE INDEX idx_schools_district ON schools(district);
CREATE INDEX idx_schools_category ON schools(category);
CREATE INDEX idx_schools_type ON schools(school_type);
CREATE INDEX idx_schools_ranking ON schools(ranking);

CREATE INDEX idx_question_bank_school_id ON school_question_bank(school_id);
CREATE INDEX idx_question_bank_type ON school_question_bank(question_type);
CREATE INDEX idx_question_bank_year ON school_question_bank(year);

CREATE INDEX idx_timeline_school_id ON interview_timeline(school_id);
CREATE INDEX idx_timeline_year ON interview_timeline(year);

CREATE INDEX idx_experience_school_id ON interview_experience(school_id);
CREATE INDEX idx_experience_author_type ON interview_experience(author_type);

-- ============================================================
-- 示例数据
-- ============================================================

-- 插入示例学校数据
INSERT INTO schools (name_zh, name_en, district, school_type, category, description, interview_format, ranking, is_featured) VALUES
('拔萃男書院', 'Diocesan Boys School', '九龍城', 'secondary', 'academic', '歷史悠久的男子寄宿中學，以學術卓越著稱', '個人面試 + 小組討論', 1, TRUE),
('聖保羅男女中學', 'St. Pauls Co-educational College', '中西區', 'secondary', 'academic', '傳統名校，男女合校，學術成績優異', '個人面試 + 筆試', 2, TRUE),
('香港道教聯合會鄧顯紀念中學', 'HKTA Donald Ling Primary School', '沙田區', 'primary', 'holistic', '注重學生全面發展，課外活動丰富', '輕鬆交談 + 遊戲活動', 3, FALSE),
('瑪利諾修院學校（小學部）', 'Maryknoll Convent School (Primary)', '灣仔區', 'primary', 'traditional', '傳統英女子小學，注重品格教育', '小組面試', 4, TRUE),
('喇沙小學', 'La Salle Primary School', '九龍城區', 'primary', 'academic', '傳統名校，注重學術與品格培养', '個人面試 + 遊戲', 5, TRUE);

-- 插入示例真题
INSERT INTO school_question_bank (school_id, question_text, question_type, difficulty, year, category, sample_answer, tips) VALUES
(1, '請自我介紹一下你自己', 'self_intro', 'easy', 2024, '必考', '你好，我叫XXX，今年6歲。我喜歡踢足球和看書...', '保持自然，聲音要清晰，可以提及興趣愛好'),
(1, '你為什麼選擇這間學校？', 'school', 'medium', 2024, '必考', '因為這間學校...', '提前了解學校特色，結合自身優點'),
(1, '你和家人平時有什麼活動？', 'family', 'easy', 2024, '常見', '我們會在週末去公園玩...', '可以提及家庭溫馨時光'),
(1, '你最喜歡的科目是什麼？為什麼？', 'school', 'medium', 2024, '常見', '我喜歡數學...', '說出真實想法並解釋原因'),
(1, '如果你是班長，你會怎樣幫助同學？', 'situational', 'hard', 2024, '挑戰題', '我會...', '展示領導能力和同理心'),

(2, 'Tell me about yourself', 'self_intro', 'medium', 2024, '必考', 'My name is...', '用簡單的英語回答，注意發音'),
(2, 'What do you like to do in your free time?', 'hobbies', 'easy', 2024, '常見', 'I like to...', '可以說喜歡的運動或興趣'),
(2, 'What is your favorite animal? Why?', 'creative', 'easy', 2024, '常見', 'I like dogs because...', '說出喜歡的原因'),

(3, '你喜歡玩什麼遊戲？', 'hobbies', 'easy', 2024, '必考', '我喜歡玩積木和拼圖...', '可以展示動手能力'),
(3, '你可以和同學分享你的玩具嗎？', 'situational', 'easy', 2024, '互動題', '可以...', '展示分享和社交能力'),

(4, 'Show me your favorite book', 'hobbies', 'easy', 2024, '活動題', '這是我最喜歡的書...', '可以帶自己喜歡的書'),
(5, '1+1等於多少？', 'math', 'easy', 2024, '筆試題', '等於2', '基礎數學要掌握');

-- 插入示例面试时间线
INSERT INTO interview_timeline (school_id, year, stage, stage_order, start_date, end_date, description, tips) VALUES
(1, 2025, '報名', 1, '2024-09-01', '2024-09-30', '網上報名，提交學生資料', '提早準備證件副本'),
(1, 2025, '第一輪面試', 2, '2024-10-15', '2024-10-20', '個人面試，约15分鐘', '保持冷靜，如實回答'),
(1, 2025, '第二輪面試', 3, '2024-11-05', '2024-11-10', '小組討論活動', '積極參與，展示團隊精神'),
(1, 2025, '錄取通知', 4, '2024-12-01', '2024-12-05', '公佈錄取結果', '留意電話或郵件'),

(2, 2025, '報名', 1, '2024-09-15', '2024-10-15', '郵遞報名', '確保資料齊全'),
(2, 2025, '筆試', 2, '2024-11-02', '2024-11-02', '中英文筆試', '提前熟悉題型'),
(2, 2025, '面試', 3, '2024-11-15', '2024-11-20', '個人面試', '衣著整潔'),
(2, 2025, '錄取', 4, '2024-12-15', '2024-12-20', '結果通知', '保持手機暢通'),

(3, 2025, '報名', 1, '2024-10-01', '2024-11-30', '開放日當天報名', '建議參加開放日'),
(3, 2025, '面試', 2, '2024-12-05', '2024-12-15', '遊戲活動觀察', '自然表現即可'),
(3, 2025, '錄取', 3, '2025-01-10', '2025-01-20', '結果發放', '留意學校通知');

-- 插入示例面试经验
INSERT INTO interview_experience (school_id, title, content, author_name, author_type, child_grade, interview_result, tags, is_featured) VALUES
(1, '2024年男拔面試經驗分享', '今天帶孩子去參加男拔的面試，整個過程很順利。面試分為兩部分...', 'William媽媽', 'parent', 'K3', 'admitted', '男拔,面試,2024', TRUE),
(2, '聖保羅男女中學面試心得', '第二批面試結束，孩子說老師很親切...', 'Jenny爸媽', 'parent', 'K3', 'admitted', '聖保羅,面試經驗', TRUE),
(3, '鄧顯小學面試遊戲環節分享', '原來面試沒有那麼可怕，就是讓孩子玩遊戲...', 'Tommy爸爸', 'parent', 'K2', 'admitted', '遊戲面試,經驗', FALSE),
(1, '男拔第二輪小組討論tips', '第二輪是小組討論，建議家長提前訓練孩子...', 'Mary媽媽', 'parent', 'K3', 'waitlisted', '小組討論,技巧', FALSE);
