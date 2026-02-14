"""
家长协作空间与社群服务
提供问答社区、经验分享、面试案例、家庭协作等功能
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://app_db_7x52_user:tJXrNcEBrKF9Mjw6yZlzgdNP9GiYCbQp@dpg-d646in94tr6s73a9mgjg-a.singapore-postgres.render.com/app_db_7x52')


def get_connection():
    """Get a database connection."""
    return psycopg2.connect(DATABASE_URL)


def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally fetch results."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            conn.commit()
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            return cursor.rowcount
    except Exception as e:
        print(f"Query error: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ============ 问题相关操作 ============

def get_questions(category=None, page=1, limit=10, keyword=None):
    """获取问题列表"""
    offset = (page - 1) * limit

    where_clauses = []
    params = []

    if category:
        where_clauses.append("category = %s")
        params.append(category)

    if keyword:
        where_clauses.append("(title ILIKE %s OR content ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = f"""
        SELECT q.*,
               u.name as author_name, u.picture as author_avatar
        FROM community_questions q
        LEFT JOIN users u ON q.user_id = u.id
        WHERE {where_sql}
        ORDER BY q.created_at DESC
        LIMIT %s OFFSET %s;
    """
    params.extend([limit, offset])

    questions = execute_query(query, params, fetch=True)

    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM community_questions q WHERE {where_sql}"
    count_result = execute_query(count_query, params[:-2], fetch=True)
    total = count_result[0]['total'] if count_result else 0

    return {
        'questions': questions,
        'total': total,
        'page': page,
        'total_pages': (total + limit - 1) // limit
    }


def get_question_by_id(question_id):
    """获取问题详情"""
    query = """
        SELECT q.*,
               u.name as author_name, u.picture as author_avatar
        FROM community_questions q
        LEFT JOIN users u ON q.user_id = u.id
        WHERE q.id = %s;
    """
    questions = execute_query(query, (question_id,), fetch=True)

    if not questions:
        return None

    question = questions[0]

    # Get answers
    answers_query = """
        SELECT a.*,
               u.name as author_name, u.picture as author_avatar
        FROM community_answers a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.question_id = %s
        ORDER BY a.is_best_answer DESC, a.like_count DESC, a.created_at ASC;
    """
    answers = execute_query(answers_query, (question_id,), fetch=True)
    question['answers'] = answers

    # Update view count
    execute_query("UPDATE community_questions SET view_count = view_count + 1 WHERE id = %s", (question_id,))

    return question


def create_question(user_id, category, title, content, is_anonymous=False):
    """创建问题"""
    query = """
        INSERT INTO community_questions (user_id, category, title, content, is_anonymous)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (user_id, category, title, content, is_anonymous), fetch=True)
    return result[0]['id'] if result else None


def update_question(question_id, user_id, title=None, content=None, category=None):
    """更新问题"""
    updates = []
    params = []

    if title:
        updates.append("title = %s")
        params.append(title)
    if content:
        updates.append("content = %s")
        params.append(content)
    if category:
        updates.append("category = %s")
        params.append(category)

    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([question_id, user_id])

    query = f"""
        UPDATE community_questions
        SET {', '.join(updates)}
        WHERE id = %s AND user_id = %s
        RETURNING id;
    """
    result = execute_query(query, params, fetch=True)
    return bool(result)


def delete_question(question_id, user_id):
    """删除问题"""
    query = "DELETE FROM community_questions WHERE id = %s AND user_id = %s RETURNING id;"
    result = execute_query(query, (question_id, user_id), fetch=True)
    return bool(result)


# ============ 回答相关操作 ============

def create_answer(question_id, user_id, content, is_anonymous=False):
    """创建回答"""
    query = """
        INSERT INTO community_answers (question_id, user_id, content, is_anonymous)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (question_id, user_id, content, is_anonymous), fetch=True)

    # Update answer count
    execute_query(
        "UPDATE community_questions SET answer_count = answer_count + 1 WHERE id = %s",
        (question_id,)
    )

    return result[0]['id'] if result else None


def like_answer(answer_id, user_id):
    """点赞回答"""
    # Check if already liked
    check_query = "SELECT id FROM answer_likes WHERE answer_id = %s AND user_id = %s;"
    existing = execute_query(check_query, (answer_id, user_id), fetch=True)

    if existing:
        # Unlike
        execute_query("DELETE FROM answer_likes WHERE answer_id = %s AND user_id = %s", (answer_id, user_id))
        execute_query("UPDATE community_answers SET like_count = like_count - 1 WHERE id = %s", (answer_id,))
        liked = False
    else:
        # Like
        execute_query("INSERT INTO answer_likes (answer_id, user_id) VALUES (%s, %s)", (answer_id, user_id))
        execute_query("UPDATE community_answers SET like_count = like_count + 1 WHERE id = %s", (answer_id,))
        liked = True

    # Get updated like count
    result = execute_query("SELECT like_count FROM community_answers WHERE id = %s", (answer_id,), fetch=True)
    like_count = result[0]['like_count'] if result else 0

    return {'liked': liked, 'like_count': like_count}


def set_best_answer(question_id, user_id, answer_id):
    """设为最佳回答"""
    # Verify ownership
    question = execute_query(
        "SELECT id FROM community_questions WHERE id = %s AND user_id = %s",
        (question_id, user_id),
        fetch=True
    )

    if not question:
        return None

    # Remove previous best answer
    execute_query(
        "UPDATE community_answers SET is_best_answer = FALSE WHERE question_id = %s",
        (question_id,)
    )

    # Set new best answer
    execute_query(
        "UPDATE community_answers SET is_best_answer = TRUE WHERE id = %s",
        (answer_id,)
    )

    # Update question
    execute_query(
        "UPDATE community_questions SET is_resolved = TRUE, best_answer_id = %s WHERE id = %s",
        (answer_id, question_id)
    )

    return {'message': '已设为最佳回答'}


def is_answer_liked(answer_id, user_id):
    """检查回答是否已点赞"""
    query = "SELECT id FROM answer_likes WHERE answer_id = %s AND user_id = %s;"
    result = execute_query(query, (answer_id, user_id), fetch=True)
    return bool(result)


# ============ 问题收藏相关操作 ============

def favorite_question(question_id, user_id):
    """收藏问题"""
    query = """
        INSERT INTO question_favorites (question_id, user_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    result = execute_query(query, (question_id, user_id), fetch=True)
    return bool(result)


def unfavorite_question(question_id, user_id):
    """取消收藏问题"""
    query = "DELETE FROM question_favorites WHERE question_id = %s AND user_id = %s;"
    execute_query(query, (question_id, user_id))
    return True


def is_question_favorited(question_id, user_id):
    """检查问题是否已收藏"""
    query = "SELECT id FROM question_favorites WHERE question_id = %s AND user_id = %s;"
    result = execute_query(query, (question_id, user_id), fetch=True)
    return bool(result)


# ============ 经验文章相关操作 ============

def get_posts(tag=None, page=1, limit=10, keyword=None):
    """获取经验文章列表"""
    offset = (page - 1) * limit

    where_clauses = ["is_published = TRUE"]
    params = []

    if tag:
        where_clauses.append("tags ILIKE %s")
        params.append(f"%{tag}%")

    if keyword:
        where_clauses.append("(title ILIKE %s OR content ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT p.*,
               u.name as author_name, u.picture as author_avatar
        FROM experience_posts p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE {where_sql}
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s;
    """
    params.extend([limit, offset])

    posts = execute_query(query, params, fetch=True)

    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM experience_posts p WHERE {where_sql}"
    count_result = execute_query(count_query, params[:-2], fetch=True)
    total = count_result[0]['total'] if count_result else 0

    return {
        'posts': posts,
        'total': total,
        'page': page,
        'total_pages': (total + limit - 1) // limit
    }


def get_post_by_id(post_id, user_id=None):
    """获取文章详情"""
    query = """
        SELECT p.*,
               u.name as author_name, u.picture as author_avatar
        FROM experience_posts p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.id = %s AND p.is_published = TRUE;
    """
    posts = execute_query(query, (post_id,), fetch=True)

    if not posts:
        return None

    post = posts[0]

    # Get comments
    comments_query = """
        SELECT c.*, u.name as author_name, u.picture as author_avatar
        FROM post_comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.post_id = %s
        ORDER BY c.created_at DESC;
    """
    comments = execute_query(comments_query, (post_id,), fetch=True)
    post['comments'] = comments

    # Check if liked/favorited by current user
    if user_id:
        post['is_liked'] = is_post_liked(post_id, user_id)
        post['is_favorited'] = is_post_favorited(post_id, user_id)
    else:
        post['is_liked'] = False
        post['is_favorited'] = False

    return post


def create_post(user_id, title, content, cover_image=None, tags=None):
    """创建经验文章"""
    tags_str = ",".join(tags) if tags else None

    query = """
        INSERT INTO experience_posts (user_id, title, content, cover_image, tags)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (user_id, title, content, cover_image, tags_str), fetch=True)
    return result[0]['id'] if result else None


def update_post(post_id, user_id, title=None, content=None, cover_image=None, tags=None):
    """更新经验文章"""
    updates = []
    params = []

    if title:
        updates.append("title = %s")
        params.append(title)
    if content:
        updates.append("content = %s")
        params.append(content)
    if cover_image is not None:
        updates.append("cover_image = %s")
        params.append(cover_image)
    if tags:
        updates.append("tags = %s")
        params.append(",".join(tags))

    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([post_id, user_id])

    query = f"""
        UPDATE experience_posts
        SET {', '.join(updates)}
        WHERE id = %s AND user_id = %s
        RETURNING id;
    """
    result = execute_query(query, params, fetch=True)
    return bool(result)


def delete_post(post_id, user_id):
    """删除经验文章"""
    query = "DELETE FROM experience_posts WHERE id = %s AND user_id = %s RETURNING id;"
    result = execute_query(query, (post_id, user_id), fetch=True)
    return bool(result)


def like_post(post_id, user_id):
    """点赞文章"""
    check_query = "SELECT id FROM post_likes WHERE post_id = %s AND user_id = %s;"
    existing = execute_query(check_query, (post_id, user_id), fetch=True)

    if existing:
        execute_query("DELETE FROM post_likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
        execute_query("UPDATE experience_posts SET like_count = like_count - 1 WHERE id = %s", (post_id,))
        liked = False
    else:
        execute_query("INSERT INTO post_likes (post_id, user_id) VALUES (%s, %s)", (post_id, user_id))
        execute_query("UPDATE experience_posts SET like_count = like_count + 1 WHERE id = %s", (post_id,))
        liked = True

    result = execute_query("SELECT like_count FROM experience_posts WHERE id = %s", (post_id,), fetch=True)
    like_count = result[0]['like_count'] if result else 0

    return {'liked': liked, 'like_count': like_count}


def is_post_liked(post_id, user_id):
    """检查文章是否已点赞"""
    query = "SELECT id FROM post_likes WHERE post_id = %s AND user_id = %s;"
    result = execute_query(query, (post_id, user_id), fetch=True)
    return bool(result)


def favorite_post(post_id, user_id):
    """收藏文章"""
    query = """
        INSERT INTO post_favorites (post_id, user_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    result = execute_query(query, (post_id, user_id), fetch=True)
    return {'message': '收藏成功' if result else '已收藏'}


def unfavorite_post(post_id, user_id):
    """取消收藏文章"""
    query = "DELETE FROM post_favorites WHERE post_id = %s AND user_id = %s;"
    execute_query(query, (post_id, user_id))
    return {'message': '取消收藏成功'}


def is_post_favorited(post_id, user_id):
    """检查文章是否已收藏"""
    query = "SELECT id FROM post_favorites WHERE post_id = %s AND user_id = %s;"
    result = execute_query(query, (post_id, user_id), fetch=True)
    return bool(result)


def create_post_comment(post_id, user_id, content):
    """创建文章评论"""
    query = """
        INSERT INTO post_comments (post_id, user_id, content)
        VALUES (%s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (post_id, user_id, content), fetch=True)

    # Update comment count
    execute_query(
        "UPDATE experience_posts SET comment_count = comment_count + 1 WHERE id = %s",
        (post_id,)
    )

    return result[0]['id'] if result else None


# ============ 面试案例相关操作 ============

def get_cases(school_type=None, school_name=None, page=1, limit=10):
    """获取面试案例列表"""
    offset = (page - 1) * limit

    where_clauses = ["status = 'approved'"]
    params = []

    if school_type:
        where_clauses.append("school_type = %s")
        params.append(school_type)

    if school_name:
        where_clauses.append("school_name ILIKE %s")
        params.append(f"%{school_name}%")

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT ic.*,
               u.name as author_name
        FROM interview_cases ic
        LEFT JOIN users u ON ic.user_id = u.id AND ic.is_anonymous = FALSE
        WHERE {where_sql}
        ORDER BY ic.created_at DESC
        LIMIT %s OFFSET %s;
    """
    params.extend([limit, offset])

    cases = execute_query(query, params, fetch=True)

    # Parse questions JSON
    for case in cases:
        if case.get('questions'):
            questions = case['questions']
            if isinstance(questions, str):
                questions = json.loads(questions)
            case['questions_preview'] = [q.get('question', '')[:50] for q in questions[:3]] if questions else []

    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM interview_cases ic WHERE {where_sql}"
    count_result = execute_query(count_query, params[:-2], fetch=True)
    total = count_result[0]['total'] if count_result else 0

    return {
        'cases': cases,
        'total': total,
        'page': page,
        'total_pages': (total + limit - 1) // limit
    }


def get_case_by_id(case_id, user_id=None):
    """获取案例详情"""
    query = """
        SELECT ic.*,
               u.name as author_name
        FROM interview_cases ic
        LEFT JOIN users u ON ic.user_id = u.id AND ic.is_anonymous = FALSE
        WHERE ic.id = %s AND ic.status = 'approved';
    """
    cases = execute_query(query, (case_id,), fetch=True)

    if not cases:
        return None

    case = cases[0]

    # Parse questions JSON
    if case.get('questions'):
        questions = case['questions']
        if isinstance(questions, str):
            case['questions'] = json.loads(questions)

    # Check if favorited by current user
    if user_id:
        case['is_favorited'] = is_case_favorited(case_id, user_id)
    else:
        case['is_favorited'] = False

    return case


def create_case(user_id, school_name, school_type, interview_date, questions,
                key_points=None, overall_rating=None, review_content=None, is_anonymous=True):
    """创建面试案例"""
    questions_json = json.dumps(questions) if isinstance(questions, list) else questions

    query = """
        INSERT INTO interview_cases (user_id, school_name, school_type, interview_date,
                                    questions, key_points, overall_rating, review_content, is_anonymous)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (
        user_id, school_name, school_type, interview_date, questions_json,
        key_points, overall_rating, review_content, is_anonymous
    ), fetch=True)
    return result[0]['id'] if result else None


def mark_case_helpful(case_id, user_id):
    """标记案例有帮助"""
    check_query = "SELECT id FROM case_helpful WHERE case_id = %s AND user_id = %s;"
    existing = execute_query(check_query, (case_id, user_id), fetch=True)

    if existing:
        execute_query("DELETE FROM case_helpful WHERE case_id = %s AND user_id = %s", (case_id, user_id))
        execute_query("UPDATE interview_cases SET helpful_count = helpful_count - 1 WHERE id = %s", (case_id,))
        marked = False
    else:
        execute_query("INSERT INTO case_helpful (case_id, user_id) VALUES (%s, %s)", (case_id, user_id))
        execute_query("UPDATE interview_cases SET helpful_count = helpful_count + 1 WHERE id = %s", (case_id,))
        marked = True

    result = execute_query("SELECT helpful_count FROM interview_cases WHERE id = %s", (case_id,), fetch=True)
    helpful_count = result[0]['helpful_count'] if result else 0

    return {'marked': marked, 'helpful_count': helpful_count}


def is_case_favorited(case_id, user_id):
    """检查案例是否已收藏"""
    query = "SELECT id FROM case_favorites WHERE case_id = %s AND user_id = %s;"
    result = execute_query(query, (case_id, user_id), fetch=True)
    return bool(result)


def favorite_case(case_id, user_id):
    """收藏案例"""
    query = """
        INSERT INTO case_favorites (case_id, user_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    result = execute_query(query, (case_id, user_id), fetch=True)
    return {'message': '收藏成功' if result else '已收藏'}


# ============ 学习目标相关操作 ============

def get_goals(user_id, child_profile_id=None, status=None):
    """获取学习目标列表"""
    where_clauses = ["user_id = %s"]
    params = [user_id]

    if child_profile_id:
        where_clauses.append("child_profile_id = %s")
        params.append(child_profile_id)

    if status:
        where_clauses.append("status = %s")
        params.append(status)

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT * FROM learning_goals
        WHERE {where_sql}
        ORDER BY
            CASE status
                WHEN 'active' THEN 1
                WHEN 'completed' THEN 2
                ELSE 3
            END,
            deadline ASC NULLS LAST,
            created_at DESC;
    """

    goals = execute_query(query, params, fetch=True)

    # Calculate progress percent
    for goal in goals:
        if goal['target_value'] > 0:
            goal['progress_percent'] = min(100, int(goal['current_value'] * 100 / goal['target_value']))
        else:
            goal['progress_percent'] = 0

    return {'goals': goals}


def create_goal(user_id, child_profile_id, title, goal_type, target_value, period, deadline=None):
    """创建学习目标"""
    query = """
        INSERT INTO learning_goals (user_id, child_profile_id, title, goal_type, target_value, period, deadline)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (
        user_id, child_profile_id, title, goal_type, target_value, period, deadline
    ), fetch=True)
    return result[0]['id'] if result else None


def update_goal_progress(goal_id, user_id, value):
    """更新目标进度"""
    # Get current goal
    query = "SELECT * FROM learning_goals WHERE id = %s AND user_id = %s;"
    goals = execute_query(query, (goal_id, user_id), fetch=True)

    if not goals:
        return None

    goal = goals[0]
    new_value = goal['current_value'] + value

    # Check if completed
    status = 'active'
    if new_value >= goal['target_value']:
        status = 'completed'
        new_value = goal['target_value']

    # Update goal
    update_query = """
        UPDATE learning_goals
        SET current_value = %s, status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *;
    """
    result = execute_query(update_query, (new_value, status, goal_id), fetch=True)

    # Record progress
    today = date.today()
    progress_query = """
        INSERT INTO goal_progress (goal_id, date, value)
        VALUES (%s, %s, %s)
        ON CONFLICT (goal_id, date) DO UPDATE SET value = goal_progress.value + %s;
    """
    execute_query(progress_query, (goal_id, today, value, value))

    progress_percent = int(new_value * 100 / goal['target_value']) if goal['target_value'] > 0 else 0

    return {
        'progress_percent': progress_percent,
        'status': status,
        'current_value': new_value
    }


def delete_goal(goal_id, user_id):
    """删除目标"""
    query = "DELETE FROM learning_goals WHERE id = %s AND user_id = %s RETURNING id;"
    result = execute_query(query, (goal_id, user_id), fetch=True)
    return bool(result)


# ============ 鼓励留言相关操作 ============

def get_encouragement_messages(user_id, child_profile_id):
    """获取鼓励留言"""
    query = """
        SELECT em.*, u.name as author_name
        FROM encouragement_messages em
        LEFT JOIN users u ON em.user_id = u.id
        WHERE em.child_profile_id = %s
        ORDER BY em.created_at DESC
        LIMIT 20;
    """
    return execute_query(query, (child_profile_id,), fetch=True)


def create_encouragement_message(user_id, child_profile_id, message):
    """发送鼓励留言"""
    query = """
        INSERT INTO encouragement_messages (user_id, child_profile_id, message)
        VALUES (%s, %s, %s)
        RETURNING id;
    """
    result = execute_query(query, (user_id, child_profile_id, message), fetch=True)
    return result[0]['id'] if result else None


def mark_message_read(message_id, user_id):
    """标记留言为已读"""
    query = "UPDATE encouragement_messages SET is_read = TRUE WHERE id = %s AND child_profile_id IN (SELECT id FROM child_profiles WHERE user_id = %s);"
    execute_query(query, (message_id, user_id))
    return True
