# 家长协作空间与社群功能需求文档

**项目名称**: AI Tutor - 个性化小学面试准备平台

**功能名称**: 家长协作空间与社群 (Parent Collaboration Space & Community)

**版本**: 1.0

**日期**: 2026-02-14

---

## 1. 功能概述

### 1.1 背景说明

AI Tutor 平台目前的核心功能以孩子为中心，专注于面试题库练习、AI模拟面试、学习路径规划等学习相关功能。然而，家长作为孩子教育的重要参与者，在整个面试准备过程中承担着关键角色——他们需要了解选校信息、与其他家长交流经验、掌握面试官关注的重点，并与孩子共同设定学习目标。

现有功能对家长的支持不足，导致家长参与度低、无法获取有价值的社群支持。因此，我们需要构建一个「家长协作空间与社群」模块，为家长提供一个专属的交流平台。

### 1.2 功能定位

家长协作空间与社群是一个独立的模块，通过以下四个核心功能帮助家长更好地参与孩子的面试准备过程：

- **家长问答社区**: 家长可以提问/回答关于选校、面试准备的问题
- **经验分享**: 家长分享面试准备经验、择校心得
- **面试经验库**: 收集并展示真实面试案例
- **家庭协作**: 家长与孩子共同设定学习目标、追踪进度

### 1.3 目标用户

- 正在为孩子准备小学面试的家长
- 希望与其他家长交流经验的家长
- 需要获取选校/面试信息的家长
- 希望参与孩子学习目标设定的家长

---

## 2. 用户故事

### 2.1 家长问答社区

| 编号 | 用户故事 | 优先级 |
|------|----------|--------|
| US-Q1 | 作为家长，我可以浏览所有问题，查看问题标题、分类、回答数、发布时间 | P0 |
| US-Q2 | 作为家长，我可以发起新问题，选择分类（选校/面试准备/经验分享/其他）、填写标题和详细描述 | P0 |
| US-Q3 | 作为家长，我可以回答其他家长的问题，提供有价值的建议和经验 | P0 |
| US-Q4 | 作为家长，我可以对自己提出的问题进行编辑和删除 | P1 |
| US-Q5 | 作为家长，我可以对有用的回答进行点赞 | P1 |
| US-Q6 | 作为家长，我可以搜索问题关键词，找到相关内容 | P2 |
| US-Q7 | 作为家长，我可以按分类筛选问题 | P2 |
| US-Q8 | 作为家长，我可以收藏问题，之后查看 | P2 |

### 2.2 经验分享

| 编号 | 用户故事 | 优先级 |
|------|----------|--------|
| US-E1 | 作为家长，我可以发布经验分享文章，包含标题、内容、图片 | P0 |
| US-E2 | 作为家长，我可以浏览其他家长的经验分享 | P0 |
| US-E3 | 作为家长，我可以对经验文章进行点赞和收藏 | P1 |
| US-E4 | 作为家长，我可以评论其他家长的经验文章 | P1 |
| US-E5 | 作为家长，我可以编辑和删除自己发布的文章 | P1 |
| US-E6 | 作为家长，我可以按标签筛选经验文章 | P2 |

### 2.3 面试经验库

| 编号 | 用户故事 | 优先级 |
|------|----------|--------|
| US-C1 | 作为家长，我可以浏览真实面试案例（包含学校名称、面试问题、孩子反馈） | P0 |
| US-C2 | 作为家长，我可以提交自己的面试经验案例 | P0 |
| US-C3 | 作为家长，我可以按学校类型筛选面试案例 | P1 |
| US-C4 | 作为家长，我可以按学校名称搜索面试案例 | P1 |
| US-C5 | 作为家长，我可以对面试案例进行评分，帮助其他家长判断可信度 | P2 |
| US-C6 | 作为家长，我可以收藏面试案例以便后续查看 | P2 |

### 2.4 家庭协作

| 编号 | 用户故事 | 优先级 |
|------|----------|--------|
| US-F1 | 作为家长，我可以为孩子设定每日/每周学习目标 | P0 |
| US-F2 | 作为家长，我可以查看孩子的学习进度统计 | P0 |
| US-F3 | 作为家长，我可以与孩子一起回顾学习成果 | P1 |
| US-F4 | 作为家长，我可以发送鼓励留言给孩子 | P1 |
| US-F5 | 作为家长，我可以设置目标提醒 | P2 |
| US-F6 | 作为家长和孩子，我可以共同完成任务获得奖励 | P2 |

---

## 3. 功能需求详情

### 3.1 家长问答社区

#### 3.1.1 问题列表页

**页面结构**:
- 顶部搜索栏
- 分类筛选标签（全部/选校/面试准备/经验分享/其他）
- 问题列表（无限滚动加载，每次加载10条）
- 悬浮「提问」按钮

**问题卡片展示内容**:
- 问题标题（最多显示2行，超出省略）
- 问题分类标签（彩色标签）
- 回答数量图标 + 数量
- 发布时间和作者头像/昵称
- 简短预览（前100字）

**交互行为**:
- 点击问题卡片 -> 跳转至问题详情页
- 点击搜索图标 -> 展开搜索框，输入关键词后实时搜索
- 点击分类标签 -> 筛选对应分类的问题
- 点击提问按钮 -> 展开提问表单

#### 3.1.2 问题详情页

**页面结构**:
- 问题标题（大字展示）
- 问题详情内容（支持Markdown渲染）
- 分类标签
- 发布时间和作者信息
- 回答列表
- 回答输入框（固定在底部）

**回答卡片展示内容**:
- 回答作者头像、昵称、发布的时间
- 回答内容（支持Markdown）
- 点赞按钮和数量
- 「最佳回答」标记（提问者可选）

**交互行为**:
- 点击点赞按钮 -> 点赞数+1，再次点击取消点赞
- 点击「设为最佳回答」-> 该回答标记为最佳回答
- 滚动至底部 -> 显示回答输入框
- 点击回答输入框 -> 展开输入界面

#### 3.1.3 提问/编辑页面

**表单字段**:
- 分类选择（必选，下拉选择）
- 问题标题（必填，最多100字）
- 问题详情（必填，支持Markdown，最少20字）
- 匿名发布选项（可选，默认不匿名）

**校验规则**:
- 标题不能为空，最少5字
- 详情最少20字
- 禁止发布敏感词、违规内容

### 3.2 经验分享

#### 3.2.1 文章列表页

**页面结构**:
- 顶部搜索栏
- 热门标签筛选
- 文章卡片列表（瀑布流布局）
- 悬浮「发布」按钮

**文章卡片展示内容**:
- 封面图（如果有）
- 文章标题（最多显示2行）
- 文章摘要（前80字）
- 作者头像和昵称
- 发布时间
- 点赞数和评论数

**交互行为**:
- 点击卡片 -> 跳转至文章详情页
- 点击标签 -> 筛选对应标签的文章

#### 3.2.2 文章详情页

**页面结构**:
- 封面图（大图展示）
- 文章标题
- 作者信息和发布时间
- 文章正文（支持Markdown、图片）
- 点赞和收藏按钮
- 评论列表

**交互行为**:
- 点击点赞 -> 点赞数+1
- 点击收藏 -> 添加到我的收藏
- 滚动至底部 -> 展开评论输入框

#### 3.2.3 发布/编辑页面

**表单字段**:
- 封面图上传（可选，支持拖拽上传）
- 标题（必填，最多100字）
- 正文内容（必填，支持Markdown）
- 标签选择（可选，最多选择3个）

### 3.3 面试经验库

#### 3.3.1 案例列表页

**页面结构**:
- 搜索栏（可搜索学校名称）
- 学校类型筛选（学类型/全人型/国际型/传统名校/全部）
- 案例卡片列表
- 「分享经验」按钮

**案例卡片展示内容**:
- 学校名称（加粗显示）
- 面试日期
- 面试问题摘要（最多显示3条）
- 整体评价星级
- 收集的报告数量

#### 3.3.2 案例详情页

**页面结构**:
- 学校信息卡片（学校名称、类型、地理位置）
- 面试时间
- 面试问题列表（每条包含问题+家长反馈）
- 面试官重点考察内容总结
- 整体评分和评价详情
- 提交者信息
- 相关推荐

**交互行为**:
- 点击「有帮助」-> 评价为有帮助
- 点击「收藏」-> 添加到我的收藏

#### 3.3.3 提交案例页面

**表单字段**:
- 学校名称（必填，支持搜索自动补全）
- 学校类型（必选）
- 面试日期（必选，日期选择器）
- 面试问题（必填，可添加多条，每条包含问题描述）
- 面试官考察重点（可选）
- 整体评分（必选，1-5星）
- 详细评价（必填，最少50字）
- 是否匿名（可选）

### 3.4 家庭协作

#### 3.4.1 目标设定页

**页面结构**:
- 当前周期（本周/今日）进度概览
- 目标列表
- 添加目标按钮
- 与孩子共同完成的进度展示

**目标卡片内容**:
- 目标名称
- 目标类型（学习时长/练习次数/主题完成/自定义）
- 目标值和当前进度
- 截止日期
- 状态（进行中/已完成/已过期）

**添加目标表单**:
- 目标名称（必填）
- 目标类型（必选）
- 目标值（必填，数字）
- 周期（必选：每日/每周）
- 截止日期（可选）

#### 3.4.2 进度追踪页

**页面结构**:
- 孩子学习统计（本周练习次数、总时长、主题完成数）
- 目标完成进度（圆环图）
- 目标完成历史
- 鼓励留言板

**鼓励留言功能**:
- 家长可以发送鼓励话语
- 孩子可以在学习时看到这些留言
- 孩子也可以回复感谢

---

## 4. 数据库设计

### 4.1 新建数据库表

#### 4.1.1 问题表 (community_questions)

```sql
CREATE TABLE community_questions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- 'school_selection', 'interview_prep', 'experience', 'other'
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
```

**索引**:
- `idx_questions_user`: community_questions(user_id)
- `idx_questions_category`: community_questions(category)
- `idx_questions_created`: community_questions(created_at DESC)

#### 4.1.2 回答表 (community_answers)

```sql
CREATE TABLE community_answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES community_questions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_best_answer BOOLEAN DEFAULT FALSE,
    like_count INTEGER DEFAULT 0,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**索引**:
- `idx_answers_question`: community_answers(question_id)
- `idx_answers_user`: community_answers(user_id)

#### 4.1.3 回答点赞表 (answer_likes)

```sql
CREATE TABLE answer_likes (
    id SERIAL PRIMARY KEY,
    answer_id INTEGER NOT NULL REFERENCES community_answers(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(answer_id, user_id)
);
```

#### 4.1.4 经验文章表 (experience_posts)

```sql
CREATE TABLE experience_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    cover_image VARCHAR(500),
    tags VARCHAR(255), -- comma-separated tags
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**索引**:
- `idx_posts_user`: experience_posts(user_id)
- `idx_posts_created`: experience_posts(created_at DESC)

#### 4.1.5 文章点赞表 (post_likes)

```sql
CREATE TABLE post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES experience_posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);
```

#### 4.1.6 文章收藏表 (post_favorites)

```sql
CREATE TABLE post_favorites (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES experience_posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);
```

#### 4.1.7 文章评论表 (post_comments)

```sql
CREATE TABLE post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES experience_posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.8 面试案例表 (interview_cases)

```sql
CREATE TABLE interview_cases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    school_name VARCHAR(200) NOT NULL,
    school_type VARCHAR(50) NOT NULL, -- 'academic', 'holistic', 'international', 'traditional'
    interview_date DATE NOT NULL,
    questions JSONB NOT NULL, -- Array of {question: string, feedback: string}
    key_points TEXT, -- 面试官考察重点
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    review_content TEXT NOT NULL,
    helpful_count INTEGER DEFAULT 0,
    report_count INTEGER DEFAULT 0,
    is_anonymous BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**索引**:
- `idx_cases_school`: interview_cases(school_name)
- `idx_cases_type`: interview_cases(school_type)
- `idx_cases_date`: interview_cases(interview_date DESC)

#### 4.1.9 面试案例有帮助表 (case_helpful)

```sql
CREATE TABLE case_helpful (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES interview_cases(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, user_id)
);
```

#### 4.1.10 面试案例收藏表 (case_favorites)

```sql
CREATE TABLE case_favorites (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES interview_cases(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, user_id)
);
```

#### 4.1.11 学习目标表 (learning_goals)

```sql
CREATE TABLE learning_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_profile_id INTEGER NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    goal_type VARCHAR(50) NOT NULL, -- 'practice_duration', 'practice_count', 'topic_completion', 'custom'
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    period VARCHAR(20) NOT NULL, -- 'daily', 'weekly'
    deadline DATE,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'expired'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**索引**:
- `idx_goals_user`: learning_goals(user_id)
- `idx_goals_child`: learning_goals(child_profile_id)
- `idx_goals_status`: learning_goals(status)

#### 4.1.12 目标进度记录表 (goal_progress)

```sql
CREATE TABLE goal_progress (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER NOT NULL REFERENCES learning_goals(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    value INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(goal_id, date)
);
```

#### 4.1.13 鼓励留言表 (encouragement_messages)

```sql
CREATE TABLE encouragement_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    child_profile_id INTEGER NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.1.14 问题收藏表 (question_favorites)

```sql
CREATE TABLE question_favorites (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES community_questions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(question_id, user_id)
);
```

### 4.2 数据库连接信息

- **DATABASE_URL**: postgresql://app_db_7x52_user:tJXrNcEBrKF9Mjw6yZlzgdNP9GiYCbQp@dpg-d646in94tr6s73a9mgjg-a.singapore-postgres.render.com/app_db_7x52

---

## 5. API 设计

### 5.1 问答社区 API

#### 获取问题列表
```
GET /api/community/questions

Query Parameters:
- category: string (optional) - 分类筛选
- page: int (optional, default: 1) - 页码
- limit: int (optional, default: 10) - 每页数量
- keyword: string (optional) - 搜索关键词

Response:
{
  "questions": [
    {
      "id": 1,
      "title": "选择DBS还是SPCC好？",
      "category": "school_selection",
      "content_preview": "我家孩子今年K3...",
      "answer_count": 5,
      "is_resolved": true,
      "author": {
        "id": 1,
        "name": "家长A",
        "avatar": "url"
      },
      "created_at": "2026-02-10T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "total_pages": 10
}
```

#### 获取问题详情
```
GET /api/community/questions/:id

Response:
{
  "id": 1,
  "title": "选择DBS还是SPCC好？",
  "category": "school_selection",
  "content": "我家孩子今年K3...",
  "is_anonymous": false,
  "view_count": 120,
  "answer_count": 5,
  "is_resolved": true,
  "best_answer_id": 3,
  "author": {
    "id": 1,
    "name": "家长A",
    "avatar": "url"
  },
  "answers": [
    {
      "id": 1,
      "content": "我认为...",
      "is_best_answer": false,
      "like_count": 10,
      "author": {
        "id": 2,
        "name": "家长B",
        "avatar": "url"
      },
      "created_at": "2026-02-10T11:00:00Z"
    }
  ],
  "created_at": "2026-02-10T10:00:00Z"
}
```

#### 发起问题
```
POST /api/community/questions

Request Body:
{
  "category": "school_selection",
  "title": "选择DBS还是SPCC好？",
  "content": "我家孩子今年K3...",
  "is_anonymous": false
}

Response:
{
  "id": 1,
  "message": "问题发布成功"
}
```

#### 回答问题
```
POST /api/community/questions/:id/answers

Request Body:
{
  "content": "我认为...",
  "is_anonymous": false
}

Response:
{
  "id": 1,
  "message": "回答发布成功"
}
```

#### 点赞回答
```
POST /api/community/answers/:id/like

Response:
{
  "like_count": 11
}
```

#### 设为最佳回答
```
POST /api/community/questions/:id/best-answer

Request Body:
{
  "answer_id": 1
}

Response:
{
  "message": "已设为最佳回答"
}
```

### 5.2 经验分享 API

#### 获取文章列表
```
GET /api/community/posts

Query Parameters:
- tag: string (optional) - 标签筛选
- page: int (optional, default: 1)
- limit: int (optional, default: 10)
- keyword: string (optional)

Response:
{
  "posts": [
    {
      "id": 1,
      "title": "我的面试准备经验分享",
      "content_preview": "经过半年准备...",
      "cover_image": "url",
      "tags": ["面试技巧", "经验"],
      "like_count": 50,
      "comment_count": 10,
      "author": {
        "id": 1,
        "name": "家长A",
        "avatar": "url"
      },
      "created_at": "2026-02-10T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1
}
```

#### 获取文章详情
```
GET /api/community/posts/:id

Response:
{
  "id": 1,
  "title": "我的面试准备经验分享",
  "content": "经过半年准备...",
  "cover_image": "url",
  "tags": ["面试技巧", "经验"],
  "like_count": 50,
  "comment_count": 10,
  "is_liked": true,
  "is_favorited": false,
  "author": {
    "id": 1,
    "name": "家长A",
    "avatar": "url"
  },
  "comments": [...],
  "created_at": "2026-02-10T10:00:00Z"
}
```

#### 发布文章
```
POST /api/community/posts

Request Body:
{
  "title": "我的面试准备经验分享",
  "content": "经过半年准备...",
  "cover_image": "url",
  "tags": ["面试技巧", "经验"]
}

Response:
{
  "id": 1,
  "message": "文章发布成功"
}
```

#### 点赞文章
```
POST /api/community/posts/:id/like

Response:
{
  "like_count": 51
}
```

#### 收藏文章
```
POST /api/community/posts/:id/favorite

Response:
{
  "message": "收藏成功"
}
```

### 5.3 面试案例 API

#### 获取案例列表
```
GET /api/community/cases

Query Parameters:
- school_type: string (optional)
- school_name: string (optional)
- page: int (optional, default: 1)
- limit: int (optional, default: 10)

Response:
{
  "cases": [
    {
      "id": 1,
      "school_name": "DBS",
      "school_type": "academic",
      "interview_date": "2026-01-15",
      "questions_preview": ["你叫什么名字？", "你喜欢什么？"],
      "overall_rating": 4,
      "report_count": 20,
      "created_at": "2026-02-10T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1
}
```

#### 获取案例详情
```
GET /api/community/cases/:id

Response:
{
  "id": 1,
  "school_name": "DBS",
  "school_type": "academic",
  "interview_date": "2026-01-15",
  "questions": [
    {"question": "你叫什么名字？", "feedback": "孩子回答得很清晰"}
  ],
  "key_points": "考察孩子的表达能力",
  "overall_rating": 4,
  "review_content": "整体感觉...",
  "helpful_count": 15,
  "is_favorited": false,
  "created_at": "2026-02-10T10:00:00Z"
}
```

#### 提交案例
```
POST /api/community/cases

Request Body:
{
  "school_name": "DBS",
  "school_type": "academic",
  "interview_date": "2026-01-15",
  "questions": [
    {"question": "你叫什么名字？", "feedback": "孩子回答得很清晰"}
  ],
  "key_points": "考察孩子的表达能力",
  "overall_rating": 4,
  "review_content": "整体感觉...",
  "is_anonymous": true
}

Response:
{
  "id": 1,
  "message": "案例提交成功，待审核后发布"
}
```

#### 评价案例有帮助
```
POST /api/community/cases/:id/helpful

Response:
{
  "helpful_count": 16
}
```

### 5.4 家庭协作 API

#### 获取目标列表
```
GET /api/goals

Query Parameters:
- child_id: int (optional) - 孩子ID
- status: string (optional) - 状态筛选

Response:
{
  "goals": [
    {
      "id": 1,
      "title": "完成自我介绍主题",
      "goal_type": "topic_completion",
      "target_value": 1,
      "current_value": 0,
      "period": "weekly",
      "deadline": "2026-02-20",
      "status": "active",
      "progress_percent": 0
    }
  ]
}
```

#### 创建目标
```
POST /api/goals

Request Body:
{
  "child_id": 1,
  "title": "完成自我介绍主题",
  "goal_type": "topic_completion",
  "target_value": 1,
  "period": "weekly",
  "deadline": "2026-02-20"
}

Response:
{
  "id": 1,
  "message": "目标创建成功"
}
```

#### 更新目标进度
```
POST /api/goals/:id/progress

Request Body:
{
  "value": 1
}

Response:
{
  "progress_percent": 100,
  "status": "completed"
}
```

#### 获取鼓励留言
```
GET /api/encouragement-messages

Query Parameters:
- child_id: int (required)

Response:
{
  "messages": [
    {
      "id": 1,
      "message": "加油！你是最棒的！",
      "is_read": false,
      "created_at": "2026-02-10T10:00:00Z"
    }
  ]
}
```

#### 发送鼓励留言
```
POST /api/encouragement-messages

Request Body:
{
  "child_id": 1,
  "message": "加油！你是最棒的！"
}

Response:
{
  "id": 1,
  "message": "留言发送成功"
}
```

---

## 6. 页面设计要求

### 6.1 整体设计原则

1. **风格一致性**: 与现有AI Tutor平台风格保持一致，使用相同的配色方案、字体、圆角等
2. **移动优先**: 专为移动端优化，适配手机屏幕
3. **简洁清晰**: 避免信息过载，保持页面简洁易读

### 6.2 配色方案

- 主色: `#1E94F6` (蓝色)
- 辅助色: `#8B5CF6` (紫色)
- 成功色: `#22C55E` (绿色)
- 警告色: `#F59E0B` (橙色)
- 错误色: `#EF4444` (红色)
- 背景色: `#F9FAFB` (浅灰)
- 文字主色: `#111827` (深灰)
- 文字次色: `#6B7280` (中灰)

### 6.3 分类标签颜色

- 选校 (school_selection): `#3B82F6` (蓝色)
- 面试准备 (interview_prep): `#8B5CF6` (紫色)
- 经验分享 (experience): `#22C55E` (绿色)
- 其他 (other): `#6B7280` (灰色)

### 6.4 页面布局要求

#### 6.4.1 导航设计

在底部导航栏增加「社群」入口:
- 图标: `forum` (Material Symbols)
- 文字: 「社群」
- 点击后进入家长协作空间首页

#### 6.4.2 首页布局

```
+---------------------------+
|     顶部搜索栏            |
+---------------------------+
| [选校][面试][经验][其他] |  <- 分类标签
+---------------------------+
|                           |
|    问题/文章/案例列表     |
|    (Tab切换)             |
|                           |
+---------------------------+
|       [+悬浮按钮]         |
+---------------------------+
| [首页][社群][练习][报告] |
+---------------------------+
```

#### 6.4.3 详情页布局

- 返回按钮在左上角
- 标题在返回按钮下方
- 作者信息在标题下方
- 主内容区域
- 底部固定操作栏（点赞、收藏、评论等）

### 6.5 动画效果

- 页面切换: 淡入淡出 (200ms)
- 按钮点击: 轻微缩放 (scale 0.98)
- 点赞: 心跳动画
- 卡片加载: 骨架屏动画
- 列表滚动: 惯性滚动

---

## 7. 验收标准

### 7.1 功能验收

#### 问答社区
- [ ] 用户可以浏览所有问题列表，支持分页加载
- [ ] 用户可以按分类筛选问题
- [ ] 用户可以搜索问题关键词
- [ ] 用户可以发起新问题，包含标题、分类、详情
- [ ] 用户可以回答问题
- [ ] 用户可以对自己问题的回答设为最佳
- [ ] 用户可以点赞回答
- [ ] 用户可以收藏问题

#### 经验分享
- [ ] 用户可以浏览经验文章列表
- [ ] 用户可以发布新文章，包含标题、封面图、正文、标签
- [ ] 用户可以点赞文章
- [ ] 用户可以收藏文章
- [ ] 用户可以评论文章
- [ ] 用户可以编辑和删除自己发布的文章

#### 面试经验库
- [ ] 用户可以浏览面试案例列表
- [ ] 用户可以按学校类型筛选
- [ ] 用户可以按学校名称搜索
- [ ] 用户可以提交面试案例（需审核）
- [ ] 用户可以评价案例有帮助
- [ ] 用户可以收藏案例

#### 家庭协作
- [ ] 用户可以为孩子设定学习目标
- [ ] 用户可以查看目标进度
- [ ] 用户可以发送鼓励留言
- [ ] 用户可以查看孩子的学习统计

### 7.2 性能验收

- 页面加载时间 < 2秒
- 列表滚动流畅，无卡顿
- API响应时间 < 500ms

### 7.3 兼容性验收

- iOS Safari 最新版本
- Android Chrome 最新版本
- 各种屏幕尺寸 (iPhone SE ~ iPhone 15 Pro Max)

### 7.4 安全验收

- 用户输入内容进行XSS过滤
- 所有API需要用户登录验证
- 敏感操作需要CSRF防护
- 匿名发布时隐藏用户信息

---

## 8. 项目路径

项目根目录: `/Volumes/Newsmy1 - m/app/web-poc`

关键文件结构:
```
/Volumes/Newsmy1 - m/app/web-poc/
├── app.py                    # Flask应用主文件
├── db/
│   ├── schema.sql            # 数据库Schema
│   └── database.py           # 数据库操作函数
├── templates/                # HTML模板
│   ├── community/            # 新增家长社群模板
│   └── ...
├── services/                 # 服务层
│   └── community_service.py  # 新增社群服务
└── static/
    └── css/
        └── styles.css        # 全局样式
```

---

## 9. 后续迭代

### Phase 2 (v1.1)
- 消息通知系统（新回答、新评论、新点赞）
- 用户信誉系统
- 热门问题/文章推荐算法

### Phase 3 (v1.2)
- 家长线下活动组织
- 专家问答（邀请学校老师、面试官）
- 付费社群功能

---

**文档结束**
