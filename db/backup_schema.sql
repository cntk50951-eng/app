-- AI Tutor 数据库备份
-- 备份时间: 2026-02-14
--

-- 表: answer_likes
CREATE TABLE IF NOT EXISTS answer_likes (
    id integer DEFAULT nextval('answer_likes_id_seq'::regclass) NOT NULL,
    answer_id integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (answer_id) REFERENCES community_answers(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX answer_likes_answer_id_user_id_key ON public.answer_likes USING btree (answer_id, user_id);

-- 表: badges
CREATE TABLE IF NOT EXISTS badges (
    id character varying NOT NULL,
    name_zh character varying NOT NULL,
    name_en character varying,
    description text,
    icon_emoji character varying,
    category character varying,
    requirement_type character varying,
    requirement_value integer,
    points integer DEFAULT 0,
    rarity character varying DEFAULT 'common'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
);

-- 表: case_favorites
CREATE TABLE IF NOT EXISTS case_favorites (
    id integer DEFAULT nextval('case_favorites_id_seq'::regclass) NOT NULL,
    case_id integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (case_id) REFERENCES interview_cases(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX case_favorites_case_id_user_id_key ON public.case_favorites USING btree (case_id, user_id);

-- 表: case_helpful
CREATE TABLE IF NOT EXISTS case_helpful (
    id integer DEFAULT nextval('case_helpful_id_seq'::regclass) NOT NULL,
    case_id integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (case_id) REFERENCES interview_cases(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX case_helpful_case_id_user_id_key ON public.case_helpful USING btree (case_id, user_id);

-- 表: child_profiles
CREATE TABLE IF NOT EXISTS child_profiles (
    id integer DEFAULT nextval('child_profiles_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    child_name character varying NOT NULL,
    child_age character varying NOT NULL,
    child_gender character varying,
    profile_complete boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_child_profiles_user_id ON public.child_profiles USING btree (user_id);

-- 表: community_answers
CREATE TABLE IF NOT EXISTS community_answers (
    id integer DEFAULT nextval('community_answers_id_seq'::regclass) NOT NULL,
    question_id integer,
    user_id integer,
    content text NOT NULL,
    is_best_answer boolean DEFAULT false,
    like_count integer DEFAULT 0,
    is_anonymous boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (question_id) REFERENCES community_questions(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_answers_question ON public.community_answers USING btree (question_id);
CREATE INDEX idx_answers_user ON public.community_answers USING btree (user_id);

-- 表: community_questions
CREATE TABLE IF NOT EXISTS community_questions (
    id integer DEFAULT nextval('community_questions_id_seq'::regclass) NOT NULL,
    user_id integer,
    category character varying NOT NULL,
    title character varying NOT NULL,
    content text NOT NULL,
    is_anonymous boolean DEFAULT false,
    view_count integer DEFAULT 0,
    answer_count integer DEFAULT 0,
    is_resolved boolean DEFAULT false,
    best_answer_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_questions_user ON public.community_questions USING btree (user_id);
CREATE INDEX idx_questions_category ON public.community_questions USING btree (category);
CREATE INDEX idx_questions_created ON public.community_questions USING btree (created_at DESC);

-- 表: encouragement_messages
CREATE TABLE IF NOT EXISTS encouragement_messages (
    id integer DEFAULT nextval('encouragement_messages_id_seq'::regclass) NOT NULL,
    user_id integer,
    child_profile_id integer,
    message text NOT NULL,
    is_read boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (child_profile_id) REFERENCES child_profiles(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 表: experience_posts
CREATE TABLE IF NOT EXISTS experience_posts (
    id integer DEFAULT nextval('experience_posts_id_seq'::regclass) NOT NULL,
    user_id integer,
    title character varying NOT NULL,
    content text NOT NULL,
    cover_image character varying,
    tags character varying,
    like_count integer DEFAULT 0,
    comment_count integer DEFAULT 0,
    is_published boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_posts_user ON public.experience_posts USING btree (user_id);
CREATE INDEX idx_posts_created ON public.experience_posts USING btree (created_at DESC);

-- 表: goal_progress
CREATE TABLE IF NOT EXISTS goal_progress (
    id integer DEFAULT nextval('goal_progress_id_seq'::regclass) NOT NULL,
    goal_id integer,
    date date NOT NULL,
    value integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (goal_id) REFERENCES learning_goals(id)
);
CREATE UNIQUE INDEX goal_progress_goal_id_date_key ON public.goal_progress USING btree (goal_id, date);

-- 表: interests
CREATE TABLE IF NOT EXISTS interests (
    id character varying NOT NULL,
    name_zh character varying NOT NULL,
    emoji character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
);

-- 表: interview_cases
CREATE TABLE IF NOT EXISTS interview_cases (
    id integer DEFAULT nextval('interview_cases_id_seq'::regclass) NOT NULL,
    user_id integer,
    school_name character varying NOT NULL,
    school_type character varying NOT NULL,
    interview_date date NOT NULL,
    questions jsonb NOT NULL,
    key_points text,
    overall_rating integer,
    review_content text NOT NULL,
    helpful_count integer DEFAULT 0,
    report_count integer DEFAULT 0,
    is_anonymous boolean DEFAULT true,
    status character varying DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_cases_school ON public.interview_cases USING btree (school_name);
CREATE INDEX idx_cases_type ON public.interview_cases USING btree (school_type);
CREATE INDEX idx_cases_date ON public.interview_cases USING btree (interview_date DESC);

-- 表: learning_goals
CREATE TABLE IF NOT EXISTS learning_goals (
    id integer DEFAULT nextval('learning_goals_id_seq'::regclass) NOT NULL,
    user_id integer,
    child_profile_id integer,
    title character varying NOT NULL,
    goal_type character varying NOT NULL,
    target_value integer NOT NULL,
    current_value integer DEFAULT 0,
    period character varying NOT NULL,
    deadline date,
    status character varying DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (child_profile_id) REFERENCES child_profiles(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_goals_user ON public.learning_goals USING btree (user_id);
CREATE INDEX idx_goals_child ON public.learning_goals USING btree (child_profile_id);
CREATE INDEX idx_goals_status ON public.learning_goals USING btree (status);

-- 表: learning_reports
CREATE TABLE IF NOT EXISTS learning_reports (
    id integer DEFAULT nextval('learning_reports_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    report_type character varying NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    topics_completed integer DEFAULT 0,
    total_practice_time integer DEFAULT 0,
    average_score numeric,
    streak_days integer DEFAULT 0,
    badges_earned integer DEFAULT 0,
    highlights text,
    improvements text,
    recommendation text,
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 表: post_comments
CREATE TABLE IF NOT EXISTS post_comments (
    id integer DEFAULT nextval('post_comments_id_seq'::regclass) NOT NULL,
    post_id integer,
    user_id integer,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (post_id) REFERENCES experience_posts(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 表: post_favorites
CREATE TABLE IF NOT EXISTS post_favorites (
    id integer DEFAULT nextval('post_favorites_id_seq'::regclass) NOT NULL,
    post_id integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (post_id) REFERENCES experience_posts(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX post_favorites_post_id_user_id_key ON public.post_favorites USING btree (post_id, user_id);

-- 表: post_likes
CREATE TABLE IF NOT EXISTS post_likes (
    id integer DEFAULT nextval('post_likes_id_seq'::regclass) NOT NULL,
    post_id integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (post_id) REFERENCES experience_posts(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX post_likes_post_id_user_id_key ON public.post_likes USING btree (post_id, user_id);

-- 表: practice_sessions
CREATE TABLE IF NOT EXISTS practice_sessions (
    id integer DEFAULT nextval('practice_sessions_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    topic_id character varying NOT NULL,
    duration_seconds integer NOT NULL,
    score integer,
    feedback_rating integer,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 表: question_favorites
CREATE TABLE IF NOT EXISTS question_favorites (
    id integer DEFAULT nextval('question_favorites_id_seq'::regclass) NOT NULL,
    question_id integer,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (question_id) REFERENCES community_questions(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX question_favorites_question_id_user_id_key ON public.question_favorites USING btree (question_id, user_id);

-- 表: school_types
CREATE TABLE IF NOT EXISTS school_types (
    id character varying NOT NULL,
    name_zh character varying NOT NULL,
    examples character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
);

-- 表: target_schools
CREATE TABLE IF NOT EXISTS target_schools (
    id integer DEFAULT nextval('target_schools_id_seq'::regclass) NOT NULL,
    child_profile_id integer NOT NULL,
    school_type_id character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (child_profile_id) REFERENCES child_profiles(id)
,    FOREIGN KEY (school_type_id) REFERENCES school_types(id)
);
CREATE UNIQUE INDEX target_schools_child_profile_id_school_type_id_key ON public.target_schools USING btree (child_profile_id, school_type_id);
CREATE INDEX idx_target_schools_profile_id ON public.target_schools USING btree (child_profile_id);

-- 表: user_badges
CREATE TABLE IF NOT EXISTS user_badges (
    id integer DEFAULT nextval('user_badges_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    badge_id character varying NOT NULL,
    earned_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    progress integer DEFAULT 0
,    PRIMARY KEY (id)
,    FOREIGN KEY (badge_id) REFERENCES badges(id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX user_badges_user_id_badge_id_key ON public.user_badges USING btree (user_id, badge_id);

-- 表: user_interests
CREATE TABLE IF NOT EXISTS user_interests (
    id integer DEFAULT nextval('user_interests_id_seq'::regclass) NOT NULL,
    child_profile_id integer NOT NULL,
    interest_id character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (child_profile_id) REFERENCES child_profiles(id)
,    FOREIGN KEY (interest_id) REFERENCES interests(id)
);
CREATE UNIQUE INDEX user_interests_child_profile_id_interest_id_key ON public.user_interests USING btree (child_profile_id, interest_id);
CREATE INDEX idx_user_interests_profile_id ON public.user_interests USING btree (child_profile_id);

-- 表: user_progress
CREATE TABLE IF NOT EXISTS user_progress (
    id integer DEFAULT nextval('user_progress_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    topic_id character varying NOT NULL,
    status character varying DEFAULT 'not_started'::character varying,
    completion_percent integer DEFAULT 0,
    practice_count integer DEFAULT 0,
    best_score integer,
    total_time_seconds integer DEFAULT 0,
    last_practiced_at timestamp without time zone,
    completed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
,    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX user_progress_user_id_topic_id_key ON public.user_progress USING btree (user_id, topic_id);

-- 表: users
CREATE TABLE IF NOT EXISTS users (
    id integer DEFAULT nextval('users_id_seq'::regclass) NOT NULL,
    email character varying NOT NULL,
    name character varying,
    picture character varying,
    user_type character varying DEFAULT 'email'::character varying NOT NULL,
    google_id character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
,    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);
CREATE INDEX idx_users_email ON public.users USING btree (email);