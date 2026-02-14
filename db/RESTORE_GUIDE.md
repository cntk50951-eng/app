# 数据库恢复指南

## 概述

本文档说明如何从备份文件恢复 AI Tutor 数据库的表结构和数据。

## 备份文件位置

- 表结构: `db/backup_schema.sql`
- 基础数据: `db/backup_data.sql`
- 社区表结构: `db/community_tables.sql`

## 恢复方法

### 方法1: 使用 psql 命令行（推荐）

```bash
# 1. 恢复表结构
psql $DATABASE_URL -f db/backup_schema.sql

# 2. 恢复基础数据（如 interests, school_types, badges）
psql $DATABASE_URL -f db/backup_data.sql

# 3. 恢复社区表（如需重建社区功能）
psql $DATABASE_URL -f db/community_tables.sql
```

其中 `DATABASE_URL` 格式为：
```
postgresql://username:password@host:port/database_name
```

### 方法2: 使用 Python 脚本

```python
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'your_database_url_here')

def execute_sql_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print(f"已执行: {filepath}")

# 执行恢复
execute_sql_file('db/backup_schema.sql')
execute_sql_file('db/backup_data.sql')
execute_sql_file('db/community_tables.sql')

print("数据库恢复完成!")
```

### 方法3: 手动执行 SQL

1. 连接到数据库（使用 pgAdmin、DBeaver 或 psql）
2. 依次打开并执行：
   - `db/backup_schema.sql`
   - `db/backup_data.sql`
   - `db/community_tables.sql`

## 数据库连接信息

```
主机: dpg-d646in94tr6s73a9mgjg-a.singapore-postgres.render.com
端口: 5432
数据库: app_db_7x52
用户名: app_db_7x52_user
密码: tJXrNcEBrKF9Mjw6yZlzgdNP9GiYCbQp
```

完整连接字符串：
```
postgresql://app_db_7x52_user:tJXrNcEBrKF9Mjw6yZlzgdNP9GiYCbQp@dpg-d646in94tr6s73a9mgjg-a.singapore-postgres.render.com/app_db_7x52
```

## 备份内容说明

### 表结构 (backup_schema.sql)

包含 25 个表的完整结构：

| 类别 | 表名 |
|------|------|
| 用户系统 | users, child_profiles, user_interests, target_schools |
| 学习进度 | user_progress, practice_sessions, learning_reports |
| 成就系统 | badges, user_badges |
| 社区功能 | community_questions, community_answers, answer_likes, question_favorites |
| 内容分享 | experience_posts, post_likes, post_favorites, post_comments |
| 面试案例 | interview_cases, case_helpful, case_favorites |
| 学习目标 | learning_goals, goal_progress |
| 鼓励留言 | encouragement_messages |

### 基础数据 (backup_data.sql)

包含系统配置数据：
- interests - 兴趣标签
- school_types - 学校类型
- badges - 成就徽章

### 社区表结构 (community_tables.sql)

家长社群功能专用表（已在 backup_schema.sql 中包含）

## 注意事项

1. **数据丢失风险**: 如果在备份之后有新数据，恢复将覆盖现有数据
2. **外键约束**: 恢复表结构时需要注意外键依赖顺序
3. **索引**: 备份已包含索引定义，无需手动重建
4. **用户数据**: users 和 child_profiles 表包含真实用户数据，不包含在 backup_data.sql 中

## 定期备份建议

建议使用以下命令定期备份：

```bash
# 备份整个数据库
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

## 联系方式

如有问题，请检查：
1. DATABASE_URL 环境变量是否正确
2. 网络连接是否正常
3. 数据库权限是否足够
