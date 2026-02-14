# AI Tutor 竞技场挑战系统功能规格说明书

## 文档信息

- **项目名称**：AI Tutor 竞技场挑战系统
- **版本**：1.0
- **目标用户**：香港小学生（K1-P3）
- **产品定位**：面向香港小学生的AI面试练习助手 - 竞技场多人对战/练习功能
- **创建日期**：2026-02-14

---

## 1. 功能概述

### 1.1 系统定位

竞技场挑战系统是AI Tutor应用中的一项多人对战/练习功能，旨在让孩子可以与其他小朋友或AI进行面试技能比试，通过趣味性的竞争机制提升孩子的面试准备积极性。系统整合了现有的题库、成就徽章和学习进度系统，为用户提供完整的竞技体验。

### 1.2 核心功能模块

本系统包含以下七大核心功能模块：

1. **挑战模式**：选择题库类型进行挑战，包括自我介绍、逻辑思维、表达技巧等
2. **对战系统**：与AI对手或模拟真实用户进行对战
3. **计时赛**：在限定时间内回答最多问题，考验速度与准确性
4. **排行榜**：展示本周、本月最佳选手排名
5. **奖励系统**：获胜获得金币、徽章等奖励
6. **练习场**：单人练习模式，不计入排名和奖励
7. **段位系统**：青铜、白银、黄金、钻石等段位等级

### 1.3 设计原则

- **移动优先**：采用与现有Dashboard一致的移动端优先设计，最大宽度480px
- **游戏化体验**：借鉴游戏化设计元素，包括段位、徽章、金币、排行榜等
- **适龄性**：界面简洁友好，适合6-9岁儿童独立操作
- **激励导向**：通过即时反馈、段位升级、排行榜竞争等机制保持用户参与度

---

## 2. 用户故事

### 2.1 核心用户故事

| 编号 | 用户角色 | 用户故事 | 验收标准 |
|------|----------|----------|----------|
| US-001 | 小学生 | 我想选择一个面试主题进行挑战，这样可以有针对性地练习 | 可以选择至少3种题库类型，每种类型至少包含10道题目 |
| US-002 | 小学生 | 我想和AI进行对战，测试我的面试技巧 | 可以选择与AI对手对战，AI难度可分为简单/中等/困难 |
| US-003 | 小学生 | 我想和其他小朋友比赛，看看谁更厉害 | 可以匹配真实用户进行对战，系统自动匹配实力相近的对手 |
| US-004 | 小学生 | 我想在限定时间内回答尽可能多的问题 | 计时赛模式提供60秒/120秒/180秒三种时长选项 |
| US-005 | 小学生 | 我想知道我在排行榜上的名次 | 可以查看本周和本月排行榜，显示前100名玩家 |
| US-006 | 小学生 | 我想通过获胜获得金币和徽章 | 战斗胜利后即时获得金币和成就徽章 |
| US-007 | 小学生 | 我想先自己练习，不着急比赛 | 练习场模式不计入排名，提供充分的学习空间 |
| US-008 | 小学生 | 我想不断提升我的段位 | 获胜可获得段位积分，达到一定积分自动升级段位 |
| US-009 | 小学生 | 我想查看我的对战历史记录 | 可以查看过去30天的对战记录和统计数据 |
| US-010 | 小学生 | 我想和朋友分享我的战绩 | 可以生成分享图片，展示段位和胜率 |

### 2.2 用户流程图

```
用户进入竞技场
     │
     ├── 选择挑战模式
     │    ├── 挑战模式 → 选择题库 → 开始挑战 → 结算奖励
     │    ├── 对战系统 → 选择对手类型 → 匹配对手 → 对战 → 结算奖励
     │    ├── 计时赛 → 选择时长 → 开始答题 → 结算奖励
     │    └── 练习场 → 选择题库 → 开始练习 → 无奖励结算
     │
     ├── 查看排行榜
     │    ├── 本周排行
     │    └── 本月排行
     │
     ├── 查看我的资料
     │    ├── 当前段位
     │    ├── 胜率统计
     │    ├── 对战历史
     │    └── 奖励仓库
     │
     └── 练习场（单人模式）
```

---

## 3. 数据模型设计

### 3.1 核心实体

#### 3.1.1 用户段位表 (user_rank)

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键 | 1 |
| user_id | INTEGER | 用户ID | 1001 |
| current_rank | VARCHAR | 当前段位 | "gold" |
| rank_points | INTEGER | 当前段位积分 | 2500 |
| total_matches | INTEGER | 总对战次数 | 50 |
| wins | INTEGER | 胜利次数 | 35 |
| losses | INTEGER | 失败次数 | 15 |
| current_streak | INTEGER | 当前连胜 | 5 |
| best_streak | INTEGER | 最佳连胜 | 8 |
| created_at | DATETIME | 创建时间 | 2026-01-01 00:00:00 |
| updated_at | DATETIME | 更新时间 | 2026-02-14 12:00:00 |

#### 3.1.2 段位配置表 (rank_config)

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键 | 1 |
| rank_id | VARCHAR | 段位ID | "bronze" |
| rank_name_zh | VARCHAR | 段位中文名 | "青铜" |
| rank_name_en | VARCHAR | 段位英文名 | "Bronze" |
| rank_icon | VARCHAR | 段位图标emoji | "🥉" |
| min_points | INTEGER | 最低积分 | 0 |
| max_points | INTEGER | 最高积分 | 999 |
| color_primary | VARCHAR | 主色调 | "#cd7f32" |
| color_secondary | VARCHAR | 辅助色调 | "#8b4513" |

**段位等级配置**：

| 段位ID | 段位名称 | 图标 | 积分范围 | 颜色 |
|--------|----------|------|----------|------|
| bronze | 青铜 | 🥉 | 0-999 | #cd7f32 |
| silver | 白银 | 🥈 | 1000-2499 | #c0c0c0 |
| gold | 黄金 | 🥇 | 2500-4999 | #ffd700 |
| platinum | 白金 | 💎 | 5000-9999 | #e5e4e2 |
| diamond | 钻石 | 🏆 | 10000-19999 | #b9f2ff |
| master | 大师 | 👑 | 20000+ | #ff6b6b |

#### 3.1.3 对战记录表 (arena_match)

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键 | 1 |
| match_id | VARCHAR | 对战唯一ID | "match_20260214_001" |
| user_id | INTEGER | 用户ID | 1001 |
| opponent_type | VARCHAR | 对手类型(ai/user) | "ai" |
| opponent_id | INTEGER | 对手ID(AI为null) | null |
| opponent_name | VARCHAR | 对手名称 | "AI小博士" |
| opponent_avatar | VARCHAR | 对手头像 | "🤖" |
| difficulty | VARCHAR | 难度(easy/medium/hard) | "medium" |
| category | VARCHAR | 题库分类 | "self_intro" |
| match_type | VARCHAR | 对战类型(challenge/timed/practice) | "challenge" |
| time_limit | INTEGER | 时间限制(秒) | null |
| user_score | INTEGER | 用户得分 | 80 |
| opponent_score | INTEGER | 对手得分 | 75 |
| user_correct | INTEGER | 用户正确数 | 8 |
| user_total | INTEGER | 用户答题总数 | 10 |
| opponent_correct | INTEGER | 对手正确数 | 7 |
| opponent_total | INTEGER | 对手答题总数 | 10 |
| result | VARCHAR | 结果(win/lose/draw) | "win" |
| points_earned | INTEGER | 获得积分 | +25 |
| coins_earned | INTEGER | 获得金币 | +50 |
| badges_earned | VARCHAR | 获得徽章JSON | '["first_win"]' |
| duration | INTEGER | 对战时长(秒) | 180 |
| created_at | DATETIME | 对战时间 | 2026-02-14 14:30:00 |

#### 3.1.4 排行榜缓存表 (leaderboard_cache)

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键 | 1 |
| period_type | VARCHAR | 周期类型(weekly/monthly) | "weekly" |
| period_start | DATE | 周期开始日期 | 2026-02-10 |
| period_end | DATE | 周期结束日期 | 2026-02-16 |
| rank_data | TEXT | 排名数据JSON | '[{"user_id":...}]' |
| updated_at | DATETIME | 更新时间 | 2026-02-14 00:00:00 |

#### 3.1.5 金币流水表 (coin_transaction)

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键 | 1 |
| user_id | INTEGER | 用户ID | 1001 |
| amount | INTEGER | 金币数量(+/-) | +50 |
| transaction_type | VARCHAR | 交易类型 | "match_win" |
| reference_id | VARCHAR | 关联ID | "match_20260214_001" |
| balance_after | INTEGER | 交易后余额 | 550 |
| created_at | DATETIME | 交易时间 | 2026-02-14 14:30:00 |

#### 3.1.6 奖励配置表 (reward_config)

| 字段名 | 类型 | 描述 | 示例 |
|--------|------|------|------|
| id | INTEGER | 主键 | 1 |
| reward_id | VARCHAR | 奖励ID | "match_win" |
| reward_type | VARCHAR | 奖励类型(coin/badge/point) | "coin" |
| reward_value | VARCHAR | 奖励值 | "50" |
| condition_type | VARCHAR | 触发条件 | "match_result" |
| condition_value | VARCHAR | 条件值 | "win" |
| is_active | BOOLEAN | 是否启用 | true |

### 3.2 数据关系图

```
┌─────────────────┐     ┌─────────────────┐
│    user_rank    │     │  arena_match   │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ user_id (FK) ───┼────►│ match_id (UK)   │
│ current_rank    │     │ user_id (FK) ───┼──► user
│ rank_points     │     │ opponent_id     │
│ total_matches   │     │ category        │
│ wins/losses     │     │ match_type      │
│ streaks         │     │ result          │
└─────────────────┘     │ points_earned   │
                        │ coins_earned    │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ coin_transaction│
                        ├─────────────────┤
                        │ id (PK)         │
                        │ user_id (FK) ───┼──► user
                        │ amount          │
                        │ transaction_type│
                        │ reference_id    │
                        └─────────────────┘
```

---

## 4. API设计

### 4.1 API端点总览

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/arena/home | 获取竞技场首页数据 | 是 |
| GET | /api/arena/categories | 获取可选题库分类 | 是 |
| POST | /api/arena/start-challenge | 开始挑战 | 是 |
| POST | /api/arena/start-match | 开始对战匹配 | 是 |
| POST | /api/arena/start-timed | 开始计时赛 | 是 |
| POST | /api/arena/submit-answer | 提交答题结果 | 是 |
| POST | /api/arena/complete-match | 完成对战 | 是 |
| GET | /api/arena/leaderboard | 获取排行榜 | 是 |
| GET | /api/arena/profile | 获取用户竞技资料 | 是 |
| GET | /api/arena/match-history | 获取对战历史 | 是 |
| GET | /api/arena/rewards | 获取奖励仓库 | 是 |
| GET | /api/arena/practice/start | 开始练习模式 | 是 |

### 4.2 详细API规格

#### 4.2.1 获取竞技场首页

**请求**：
```
GET /api/arena/home
```

**响应**：
```json
{
  "success": true,
  "data": {
    "user_rank": {
      "rank_id": "gold",
      "rank_name": "黄金",
      "rank_icon": "🥇",
      "rank_points": 2500,
      "next_rank": {
        "rank_id": "platinum",
        "rank_name": "白金",
        "rank_icon": "💎",
        "points_needed": 2500
      },
      "stats": {
        "total_matches": 50,
        "wins": 35,
        "losses": 15,
        "win_rate": "70%",
        "current_streak": 5,
        "best_streak": 8
      }
    },
    "coins": {
      "balance": 1250,
      "today_earned": 150
    },
    "quick_stats": {
      "weekly_rank": 23,
      "monthly_rank": 45,
      "matches_this_week": 8
    },
    "recent_matches": [
      {
        "match_id": "match_001",
        "opponent_name": "AI小博士",
        "opponent_avatar": "🤖",
        "result": "win",
        "user_score": 85,
        "opponent_score": 70,
        "points_earned": 25,
        "category_name": "自我介绍",
        "created_at": "2026-02-14T14:30:00Z"
      }
    ],
    "categories": [
      {"id": "self_intro", "name": "自我介绍", "icon": "👤", "question_count": 50},
      {"id": "logic", "name": "逻辑思维", "icon": "🧠", "question_count": 40},
      {"id": "expression", "name": "表达技巧", "icon": "🎤", "question_count": 35},
      {"id": "social", "name": "社交互动", "icon": "👥", "question_count": 30}
    ]
  }
}
```

#### 4.2.2 开始挑战

**请求**：
```
POST /api/arena/start-challenge
Content-Type: application/json

{
  "category": "self_intro",
  "difficulty": "medium",
  "question_count": 10
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "challenge_id": "challenge_20260214_001",
    "category": "self_intro",
    "difficulty": "medium",
    "questions": [
      {
        "question_id": "q001",
        "question_text": "请介绍一下你自己？",
        "question_text_en": "Please introduce yourself",
        "options": [
          {"id": "A", "text": "我叫小明，今年6岁..."},
          {"id": "B", "text": "我喜欢玩玩具车..."},
          {"id": "C", "text": "我最喜欢上学的日子..."},
          {"id": "D", "text": "我的好朋友是小华..."}
        ],
        "correct_answer": "A",
        "time_limit": 30
      }
    ],
    "time_limit": 300,
    "start_time": "2026-02-14T14:30:00Z"
  }
}
```

#### 4.2.3 开始对战匹配

**请求**：
```
POST /api/arena/start-match
Content-Type: application/json

{
  "opponent_type": "ai",
  "difficulty": "medium",
  "category": "logic"
}
```

或与真实用户对战：
```
{
  "opponent_type": "user",
  "category": "expression"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "match_id": "match_20260214_001",
    "opponent": {
      "type": "ai",
      "name": "AI面试官",
      "avatar": "👨‍💼",
      "difficulty": "medium",
      "skill_level": 75
    },
    "category": "logic",
    "questions": [...],
    "match_config": {
      "question_count": 10,
      "time_per_question": 30,
      "total_time": 300
    },
    "estimated_wait_time": 5
  }
}
```

#### 4.2.4 开始计时赛

**请求**：
```
POST /api/arena/start-timed
Content-Type: application/json

{
  "category": "mixed",
  "duration": 120,
  "difficulty": "mixed"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "timed_id": "timed_20260214_001",
    "category": "mixed",
    "duration": 120,
    "start_time": "2026-02-14T14:30:00Z",
    "end_time": "2026-02-14T14:32:00Z"
  }
}
```

#### 4.2.5 提交答题结果

**请求**：
```
POST /api/arena/submit-answer
Content-Type: application/json

{
  "match_id": "match_20260214_001",
  "question_id": "q001",
  "answer": "A",
  "time_spent": 15
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "correct": true,
    "correct_answer": "A",
    "explanation": "正确的自我介绍应该先说明自己的姓名和年龄...",
    "score": 10,
    "running_score": 80,
    "remaining_questions": 7
  }
}
```

#### 4.2.6 完成对战

**请求**：
```
POST /api/arena/complete-match
Content-Type: application/json

{
  "match_id": "match_20260214_001",
  "total_score": 85,
  "correct_count": 8,
  "total_questions": 10,
  "total_time": 245
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "result": "win",
    "user_score": 85,
    "opponent_score": 70,
    "rewards": {
      "points_earned": 25,
      "points_total": 2525,
      "coins_earned": 50,
      "coins_balance": 1300,
      "badges": [
        {
          "badge_id": "streak_3",
          "badge_name": "三连胜",
          "badge_icon": "🔥",
          "is_new": true
        }
      ],
      "rank_up": null
    },
    "statistics": {
      "accuracy": "80%",
      "avg_time_per_question": "24.5秒",
      "streak": 5
    },
    "share_text": "我在竞技场中击败了AI面试官，获得了85分！当前段位：黄金"
  }
}
```

#### 4.2.7 获取排行榜

**请求**：
```
GET /api/arena/leaderboard?period=weekly&limit=50
```

**响应**：
```json
{
  "success": true,
  "data": {
    "period": "weekly",
    "period_label": "2026年2月第2周",
    "user_rank": {
      "rank": 23,
      "user_id": 1001,
      "user_name": "小明",
      "user_avatar": "👧",
      "points": 1250,
      "win_count": 15,
      "win_rate": "75%"
    },
    "top_players": [
      {
        "rank": 1,
        "user_id": 1005,
        "user_name": "小华",
        "user_avatar": "👦",
        "points": 2580,
        "rank_id": "gold",
        "rank_icon": "🥇",
        "win_count": 28,
        "win_rate": "85%"
      },
      {
        "rank": 2,
        "user_id": 1008,
        "user_name": "小红",
        "user_avatar": "👧",
        "points": 2420,
        "rank_id": "gold",
        "rank_icon": "🥇",
        "win_count": 25,
        "win_rate": "80%"
      }
    ],
    "updated_at": "2026-02-14T00:00:00Z"
  }
}
```

#### 4.2.8 获取对战历史

**请求**：
```
GET /api/arena/match-history?page=1&limit=20&filter=all
```

**响应**：
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "match_id": "match_001",
        "opponent_name": "AI小博士",
        "opponent_avatar": "🤖",
        "result": "win",
        "user_score": 85,
        "opponent_score": 70,
        "category_name": "自我介绍",
        "match_type": "challenge",
        "points_earned": 25,
        "created_at": "2026-02-14T14:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "total_pages": 8
    },
    "statistics": {
      "total_matches": 50,
      "wins": 35,
      "losses": 15,
      "avg_score": 78.5,
      "best_score": 100
    }
  }
}
```

---

## 5. 页面设计

### 5.1 页面结构总览

| 页面 | 路由 | 描述 |
|------|------|------|
| 竞技场首页 | /arena | 展示入口、用户段位、快速开始 |
| 挑战模式 | /arena/challenge | 选择题库和难度开始挑战 |
| 对战大厅 | /arena/match | 选择对手类型进行匹配 |
| 计时赛 | /arena/timed | 计时挑战模式 |
| 练习场 | /arena/practice | 单人练习模式 |
| 对战页面 | /arena/battle | 实时对战界面 |
| 排行榜 | /arena/leaderboard | 排行榜展示 |
| 我的战绩 | /arena/profile | 用户战绩统计 |
| 奖励仓库 | /arena/rewards | 获得的金币和徽章 |

### 5.2 页面详细设计

#### 5.2.1 竞技场首页 (/arena)

**页面结构**：

```
┌────────────────────────────────────────┐
│  ← 竞技场              🔔  │ Header
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  🥇 黄金段位                     │  │ 用户段位卡片
│  │  2500 积分  │  下一级: 500分    │  │
│  │  ████████░░  80%               │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
│  │挑战│ │对战│ │计时│ │练习│        │ │ 模式选择
│  │模式│ │    │ │赛  │ │    │        │
│  └────┘ └────┘ └────┘ └────┘        │
│                                        │
│  💰 1250    本週排名: 23    8场/週    │ 快速统计
│                                        │
│  ── 最近对战 ──────────────────────    │
│  ┌──────────────────────────────────┐  │
│  │ 👉 击败 AI面试官  +25分          │  │
│  │    85分 vs 70分  • 自我介绍     │  │ 历史记录
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ 👉 输给 逻辑高手  -15分          │  │
│  │    60分 vs 80分  • 逻辑思维     │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ── 排行榜预览 ───────────────────     │
│  🥇 小华    2580分  28胜 85%         │
│  🥇 小红    2420分  25胜 80%         │  Top 3
│  🥈 小明    2100分  22胜 78%         │
│                                        │
│  [查看完整排行榜]                      │
├────────────────────────────────────────┤
│  🏠  🎯  ⏱️  📊  👤                  │ 导航栏
└────────────────────────────────────────┘
```

**关键组件**：

1. **段位卡片**：展示当前段位、积分进度、距离下一级所需积分
2. **模式选择卡片**：四种模式入口，带图标和简短描述
3. **快速统计条**：金币数量、本周排名、本周对战场数
4. **最近对战列表**：展示最近5场对战结果
5. **排行榜预览**：显示Top 3玩家信息
6. **底部导航**：与Dashboard保持一致的导航结构

#### 5.2.2 挑战模式页 (/arena/challenge)

**页面结构**：

```
┌────────────────────────────────────────┐
│  ← 选择挑战              🔔  │ Header
├────────────────────────────────────────┤
│                                        │
│  选择题库类型                           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
│  │👤  │ │🧠  │ │🎤  │ │👥 │        │
│  │自我介绍│逻辑│ │表达│ │社交│        │
│  │50题 │ │40题│ │35题│ │30题│        │
│  └────┘ └────┘ └────┘ └────┘        │
│                                        │
│  选择难度                               │
│  ┌────────┐ ┌────────┐ ┌────────┐    │
│  │  🟢    │ │  🟡    │ │  🔴    │    │
│  │  简单  │ │  中等  │ │  困难  │    │
│  │ +10分  │ │ +25分  │ │ +50分  │    │
│  └────────┘ └────────┘ └────────┘    │
│                                        │
│  选择题数                               │
│  ○ 5题  ● 10题  ○ 15题               │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  预计用时: 5分钟                       │
│  预计奖励: +25积分, +50金币            │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │         🎮 开始挑战               │  │ 开始按钮
│  └──────────────────────────────────┘  │
│                                        │
├────────────────────────────────────────┤
│  🏠  🎯  ⏱️  📊  👤                  │ 导航栏
└────────────────────────────────────────┘
```

#### 5.2.3 对战页面 (/arena/battle)

**页面结构**：

```
┌────────────────────────────────────────┐
│  对战进行中...        ⏱️ 02:45         │ Header + 计时器
├────────────────────────────────────────┤
│                                        │
│  ┌─────┐         ┌─────┐              │
│  │ 👧 │  VS    │ 🤖 │              │ 对战双方
│  │小明│         │AI面试官│            │
│  │ 85 │         │  70 │              │ 即时比分
│  └─────┘         └─────┘              │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  问题 8/10                             │
│  ████████████░░░░░░░░  80%            │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │  你最喜欢什么动物？为什么？       │  │ 题目区域
│  │                                  │  │
│  │  (请用普通话回答这个问题)        │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
│  │ A  │ │ B  │ │ C  │ │ D  │        │ 选项区域
│  │🐶狗│ │🐱猫│ │🐰兔│ │🦁狮│        │
│  └────┘ └────┘ └────┘ └────┘        │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │ 答案提交倒计时: 15秒              │  │ 倒计时条
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░  75%          │  │
│  └──────────────────────────────────┘  │
│                                        │
│  👉 选择 A 后进入下一题                │
│                                        │
├────────────────────────────────────────┤
│  🏠  🎯  ⏱️  📊  👤                  │ 导航栏
└────────────────────────────────────────┘
```

**对战状态动画**：

1. **答题中**：显示当前题目和选项
2. **答案提交**：选项高亮，显示正确答案
3. **得分反馈**：+10 或 Correct 动画
4. **对手答题**：对方进度条动画
5. **对战结束**：显示结算画面

#### 5.2.4 计时赛页面 (/arena/timed)

**页面结构**：

```
┌────────────────────────────────────────┐
│  ← 计时赛              ⏱️ 01:23       │ Header
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐  │
│  │        🏃 冲刺阶段！              │  │ 状态提示
│  │        已答题: 12  正确: 10       │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  问题 12                              │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │  找出不同的那个图形：             │  │
│  │                                  │  │
│  │    ⭐   ⭐   ⭐   🌟   ⭐        │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
│  │ A  │ │ B  │ │ C  │ │ D  │        │ 选项
│  │    │ │    │ │    │ │ ✓  │        │
│  └────┘ └────┘ └────┘ └────┘        │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  ⏱️ 剩余时间: 0:57                      │ 剩余时间
│  ████████████████░░░  52%             │
│                                        │
├────────────────────────────────────────┤
│  🏠  🎯  ⏱️  📊  👤                  │ 导航栏
└────────────────────────────────────────┘
```

#### 5.2.5 排行榜页面 (/arena/leaderboard)

**页面结构**：

```
┌────────────────────────────────────────┐
│  ← 排行榜              🔔  │ Header
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  📅 本週  📅 本月               │  │ 周期切换
│  └──────────────────────────────────┘  │
  ═════════════════════════│                                        │
│═══════════   │
│                                        │
│  🥇                                    │
│  ┌────┐ 👦 小华         🥇 2580分    │
│  │ 1  │                    28胜 85% │  │
│  └────┘ 连续3週冠军                   │
│                                        │
│  🥈                                    │
│  ┌────┐ 👧 小红         🥇 2420分    │
│  │ 2  │                    25胜 80% │  │
│  └────┘ 上升 2 名                     │
│                                        │
│  🥉                                    │
│  ┌────┐ 👦 小明         🥇 2100分    │
│  │ 3  │                    22胜 78% │  │
│  └────┘ 新人                             │
│                                        │
│  ───────────────────────────────────    │
│                                        │
│  ┌────┐ 👦 玩家4        🥈 1950分    │
│  │ 4  │                    20胜 72% │
│  └────┘                               │
│                                        │
│  ┌────┐ 👧 玩家5        🥈 1800分    │
│  │ 5  │                    18胜 70% │
│  └────┘                               │
│                                        │
│  ...                                   │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  🏠  🎯  ⏱️  📊  👤                  │ 导航栏
└────────────────────────────────────────┘
```

#### 5.2.6 对战结算页面 (/arena/result)

**页面结构**：

```
┌────────────────────────────────────────┐
│           ✨ 对战结束 ✨               │ Header
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │            🏆                   │  │ 胜利标识
│  │                                  │  │
│  │          你 赢 了！             │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌────┐         ┌────┐                │
│  │ 👧 │   85   │ 🤖 │                │
│  │小明│   VS   │AI │                │
│  │ 85 │         │ 70 │                │
│  └────┘         └────┘                │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  📊 战绩统计                           │
│  正确率: 80%  │  平均答题: 24秒         │
│                                        │
│  ════════════════════════════════════   │
│                                        │
│  🎁 获得奖励                           │
│  ┌──────────────────────────────────┐  │
│  │  +25 积分        +50 金币        │  │
│  │  🔥 三连胜        ⭐ 首胜徽章    │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │        🎮 再来一局               │  │ 按钮
│  └──────────────────────────────────┘  │
│  ┌────────────┐ ┌────────────┐        │
│  │ 🏠 返回首页 │ │ 📊 详细数据 │        │
│  └────────────┘ └────────────┘        │
│                                        │
│  📤 分享战绩                           │
│  ┌──────────────────────────────────┐  │
│  │  [生成分享图片]                   │  │
│  └──────────────────────────────────┘  │
│                                        │
├────────────────────────────────────────┤
│  🏠  🎯  ⏱️  📊  👤                  │ 导航栏
└────────────────────────────────────────┘
```

### 5.3 视觉设计规范

#### 5.3.1 配色方案

| 用途 | 颜色名称 | 色值 | 使用场景 |
|------|----------|------|----------|
| 主色 | Primary Blue | #1E94F6 | 按钮、链接、主要元素 |
| 次色 | Secondary Purple | #8B5CF6 | 徽章、特殊奖励 |
| 成功 | Success Green | #22C55E | 正确答案、胜利 |
| 警告 | Warning Orange | #F59E0B | 连胜提示 |
| 错误 | Error Red | #EF4444 | 错误答案、失败 |
| 背景 | Background Light | #F8FAFC | 页面背景 |
| 卡片 | Card White | #FFFFFF | 卡片背景 |
| 文字主色 | Text Primary | #1F2937 | 主要文字 |
| 文字次色 | Text Secondary | #6B7280 | 次要文字 |

#### 5.3.2 段位颜色

| 段位 | 主色 | 渐变起始 | 渐变结束 |
|------|------|----------|----------|
| 青铜 | #CD7F32 | #CD7F32 | #8B4513 |
| 白银 | #C0C0C0 | #E8E8E8 | #A0A0A0 |
| 黄金 | #FFD700 | #FFD700 | #FFA500 |
| 白金 | #E5E4E2 | #E5E4E2 | #B0B0B0 |
| 钻石 | #B9F2FF | #B9F2FF | #89CFF0 |
| 大师 | #FF6B6B | #FF6B6B | #EE5A5A |

#### 5.3.3 动画效果

| 动画名称 | 持续时间 | 触发场景 |
|----------|----------|----------|
| 得分+10 | 0.5s | 回答正确 |
| 连胜火焰 | 1s | 触发连胜 |
| 段位升级 | 1.5s | 段位提升 |
| 徽章解锁 | 1s | 获得新徽章 |
| 对战倒计时 | 1s | 最后10秒 |
| 页面切换 | 0.3s | 路由切换 |

---

## 6. 奖励系统详细设计

### 6.1 金币系统

#### 6.1.1 金币获取

| 行为 | 金币数量 | 说明 |
|------|----------|------|
| 挑战胜利 | +50 | 基础奖励 |
| 挑战失败 | +10 | 参与奖 |
| 对战胜利 | +50 ~ +100 | 根据难度浮动 |
| 计时赛参与 | +20 | 基础奖励 |
| 计时赛额外正确 | +2/题 | 额外奖励 |
| 每日首次登录 | +10 | 签到奖励 |
| 连续7天登录 | +100 | 周签到奖励 |
| 分享战绩 | +5 | 社交奖励 |

#### 6.1.2 金币消耗

| 用途 | 金币数量 | 说明 |
|------|----------|------|
| 购买道具 | 50-500 | 暂时保留 |
| 兑换头像框 | 200 | 个性化装饰 |
| 解锁新主题 | 100 | 额外题库 |

### 6.2 徽章系统

#### 6.2.1 竞技场专属徽章

| 徽章ID | 名称 | 图标 | 稀有度 | 获取条件 |
|--------|------|------|--------|----------|
| arena_first | 初战告捷 | 🎯 | 普通 | 完成第一场对战 |
| arena_streak_3 | 三连胜 | 🔥 | 普通 | 连续3场胜利 |
| arena_streak_5 | 五连胜 | ⚡ | 稀有 | 连续5场胜利 |
| arena_streak_10 | 十连胜 | 🌟 | 史诗 | 连续10场胜利 |
| arena_win_10 | 战场新星 | ⭐ | 普通 | 累计10场胜利 |
| arena_win_50 | 战场老将 | 🏅 | 稀有 | 累计50场胜利 |
| arena_win_100 | 百战百胜 | 👑 | 传说 | 累计100场胜利 |
| arena_timed_master | 速答王 | 🏃 | 稀有 | 计时赛正确率90%+ |
| arena_perfect | 完美表现 | 💯 | 史诗 | 单场100%正确率 |
| arena_rank_gold | 黄金段位 | 🥇 | 普通 | 达到黄金段位 |
| arena_rank_diamond | 钻石段位 | 💎 | 稀有 | 达到钻石段位 |
| arena_rank_master | 大师段位 | 👑 | 传说 | 达到大师段位 |

### 6.3 积分系统

| 对战类型 | 胜利积分 | 失败积分 | 连胜加成 |
|----------|----------|----------|----------|
| 挑战模式-简单 | +10 | -5 | +5/场 |
| 挑战模式-中等 | +25 | -10 | +10/场 |
| 挑战模式-困难 | +50 | -15 | +20/场 |
| 对战模式-简单 | +15 | -8 | +5/场 |
| 对战模式-中等 | +30 | -12 | +10/场 |
| 对战模式-困难 | +60 | -18 | +20/场 |
| 计时赛 | +1/题 | +0 | 无 |

---

## 7. 技术实现说明

### 7.1 前端技术栈

- **框架**：React + TypeScript
- **路由**：React Router
- **状态管理**：Zustand
- **UI组件**：基于现有styles.css的自定义组件
- **动画**：Framer Motion 或 CSS Animation
- **HTTP客户端**：Axios

### 7.2 后端API架构

- **框架**：Flask (现有)
- **数据库**：SQLite (现有)
- **实时通信**：WebSocket (可选，用于对战匹配)
- **缓存**：内存缓存 (排行榜数据)

### 7.3 数据库扩展

需要在现有数据库中添加以下表：

```sql
-- 用户段位表
CREATE TABLE user_arena_rank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    current_rank VARCHAR(20) DEFAULT 'bronze',
    rank_points INTEGER DEFAULT 0,
    total_matches INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 对战记录表
CREATE TABLE arena_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    opponent_type VARCHAR(10) NOT NULL,
    opponent_id INTEGER,
    opponent_name VARCHAR(50),
    opponent_avatar VARCHAR(10),
    difficulty VARCHAR(10),
    category VARCHAR(30),
    match_type VARCHAR(20),
    time_limit INTEGER,
    user_score INTEGER,
    opponent_score INTEGER,
    user_correct INTEGER,
    user_total INTEGER,
    result VARCHAR(10),
    points_earned INTEGER,
    coins_earned INTEGER,
    badges_earned TEXT,
    duration INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 排行榜缓存表
CREATE TABLE leaderboard_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_type VARCHAR(10) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    rank_data TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period_type, period_start)
);

-- 金币流水表
CREATE TABLE coin_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    reference_id VARCHAR(50),
    balance_after INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 8. 验收标准

### 8.1 功能验收

| 功能模块 | 验收条件 | 测试场景 |
|----------|----------|----------|
| 挑战模式 | 用户可以选择题库类型、难度、题数并开始挑战 | 选择不同选项，验证题目加载正确 |
| 对战系统 | 用户可以选择AI或真实用户进行对战 | 模拟匹配流程，验证对战逻辑 |
| 计时赛 | 倒计时功能正常，答题数据正确记录 | 60/120/180秒三种模式测试 |
| 排行榜 | 排行榜数据正确，按周期刷新 | 验证周榜和月榜数据 |
| 奖励系统 | 胜利后金币、积分、徽章正确发放 | 多次对战验证奖励计算 |
| 练习场 | 练习数据不计入排行榜 | 验证练习模式数据隔离 |
| 段位系统 | 积分达到阈值自动升级 | 积累积分验证升级 |

### 8.2 性能验收

- 页面加载时间 < 2秒
- 对战匹配等待时间 < 10秒
- 排行榜加载时间 < 3秒
- 答题响应时间 < 500ms

### 8.3 用户体验验收

- 6-9岁儿童可独立完成一次完整对战
- 界面元素大小适合触摸操作
- 动画流畅不卡顿
- 错误提示清晰易懂

---

## 9. 后续迭代建议

### 9.1 Phase 2 功能

1. **好友系统**：添加好友、查看好友状态、好友对战
2. **公会系统**：创建/加入公会，团体竞技
3. **赛季系统**：定期赛季重置，赛季专属奖励
4. **观战系统**：观看高水平玩家对战

### 9.2 Phase 3 功能

1. **语音对战**：语音回答问题，AI评估
2. **多人竞赛**：3人以上同时对战
3. **主题活动**：节日限定挑战活动
4. **AR对战**：增强现实对战体验

---

## 附录

### A. 术语表

| 术语 | 定义 |
|------|------|
| 段位 | 用户实力的等级划分，青铜到大师 |
| 挑战模式 | 单人挑战题目库，计入排名 |
| 对战模式 | 与AI或真实用户竞技 |
| 计时赛 | 限定时间内答题数量竞赛 |
| 练习场 | 不计入排名的练习模式 |
| 连胜 | 连续多场战斗胜利 |
| 积分 | 决定段位的数值 |

### B. 相关文档

- [AI Companion规格说明](./ai_companion_spec.md)
- [家长社区需求说明](./parent-community-requirements.md)
- [现有题库结构](./templates/question-bank.html)
- [成就徽章系统](./templates/achievements.html)

---

**文档版本历史**：

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| 1.0 | 2026-02-14 | 产品经理 | 初始版本创建 |
