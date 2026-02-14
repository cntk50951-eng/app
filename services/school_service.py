"""
学校真题库服务
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', '')

def get_db_connection():
    """获取数据库连接"""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def get_all_schools(filters=None):
    """
    获取所有学校列表
    filters: 可选过滤条件 {district, category, school_type}
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, name_zh, name_en, district, school_type, category,
                   description, interview_format, ranking, is_featured, image_url
            FROM schools
            WHERE 1=1
        """
        params = []

        if filters:
            if filters.get('district'):
                query += " AND district = %s"
                params.append(filters['district'])
            if filters.get('category'):
                query += " AND category = %s"
                params.append(filters['category'])
            if filters.get('school_type'):
                query += " AND school_type = %s"
                params.append(filters['school_type'])

        query += " ORDER BY ranking ASC NULLS LAST, name_zh ASC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # 转换日期时间
        for row in results:
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else row['created_at']

        return results
    except Exception as e:
        print(f"Error fetching schools: {e}")
        return []


def get_school_by_id(school_id):
    """根据ID获取学校详情"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM schools WHERE id = %s
        """, (school_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat() if isinstance(result['created_at'], datetime) else result['created_at']
        if result and result.get('updated_at'):
            result['updated_at'] = result['updated_at'].isoformat() if isinstance(result['updated_at'], datetime) else result['updated_at']

        return result
    except Exception as e:
        print(f"Error fetching school: {e}")
        return None


def get_school_questions(school_id, filters=None):
    """
    获取学校的真题
    filters: 可选过滤条件 {question_type, difficulty, year}
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, school_id, question_text, question_type, difficulty,
                   category, year, source, sample_answer, tips,
                   is_featured, view_count, like_count, created_at
            FROM school_question_bank
            WHERE school_id = %s
        """
        params = [school_id]

        if filters:
            if filters.get('question_type'):
                query += " AND question_type = %s"
                params.append(filters['question_type'])
            if filters.get('difficulty'):
                query += " AND difficulty = %s"
                params.append(filters['difficulty'])
            if filters.get('year'):
                query += " AND year = %s"
                params.append(filters['year'])

        query += " ORDER BY is_featured DESC, created_at DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # 转换日期时间
        for row in results:
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else row['created_at']

        return results
    except Exception as e:
        print(f"Error fetching school questions: {e}")
        return []


def get_question_by_id(question_id):
    """根据ID获取题目详情"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 增加查看次数
        cursor.execute("""
            UPDATE school_question_bank
            SET view_count = view_count + 1
            WHERE id = %s
        """, (question_id,))

        cursor.execute("""
            SELECT q.*, s.name_zh as school_name_zh, s.name_en as school_name_en
            FROM school_question_bank q
            LEFT JOIN schools s ON q.school_id = s.id
            WHERE q.id = %s
        """, (question_id,))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result and result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat() if isinstance(result['created_at'], datetime) else result['created_at']

        return result
    except Exception as e:
        print(f"Error fetching question: {e}")
        return None


def get_interview_timeline(school_id):
    """获取学校面试时间线"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM interview_timeline
            WHERE school_id = %s
            ORDER BY year DESC, stage_order ASC
        """, (school_id,))

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # 转换日期
        for row in results:
            if row.get('start_date'):
                row['start_date'] = str(row['start_date'])
            if row.get('end_date'):
                row['end_date'] = str(row['end_date'])
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else row['created_at']

        return results
    except Exception as e:
        print(f"Error fetching timeline: {e}")
        return []


def get_experience_list(filters=None):
    """
    获取面试经验列表
    filters: 可选过滤条件 {school_id, author_type, tags}
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT e.*, s.name_zh as school_name
            FROM interview_experience e
            LEFT JOIN schools s ON e.school_id = s.id
            WHERE e.is_published = TRUE
        """
        params = []

        if filters:
            if filters.get('school_id'):
                query += " AND e.school_id = %s"
                params.append(filters['school_id'])
            if filters.get('author_type'):
                query += " AND e.author_type = %s"
                params.append(filters['author_type'])
            if filters.get('tags'):
                query += " AND e.tags LIKE %s"
                params.append(f"%{filters['tags']}%")

        query += " ORDER BY e.is_featured DESC, e.created_at DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # 转换日期时间
        for row in results:
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat() if isinstance(row['created_at'], datetime) else row['created_at']
            if row.get('updated_at'):
                row['updated_at'] = row['updated_at'].isoformat() if isinstance(row['updated_at'], datetime) else row['updated_at']

        return results
    except Exception as e:
        print(f"Error fetching experience list: {e}")
        return []


def get_experience_by_id(experience_id):
    """根据ID获取经验详情"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 增加查看次数
        cursor.execute("""
            UPDATE interview_experience
            SET view_count = view_count + 1
            WHERE id = %s
        """, (experience_id,))

        cursor.execute("""
            SELECT e.*, s.name_zh as school_name
            FROM interview_experience e
            LEFT JOIN schools s ON e.school_id = s.id
            WHERE e.id = %s
        """, (experience_id,))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            if result.get('created_at'):
                result['created_at'] = result['created_at'].isoformat() if isinstance(result['created_at'], datetime) else result['created_at']
            if result.get('updated_at'):
                result['updated_at'] = result['updated_at'].isoformat() if isinstance(result['updated_at'], datetime) else result['updated_at']

        return result
    except Exception as e:
        print(f"Error fetching experience: {e}")
        return None


def like_question(question_id):
    """点赞题目"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE school_question_bank
            SET like_count = like_count + 1
            WHERE id = %s
        """, (question_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error liking question: {e}")
        return False


def like_experience(experience_id):
    """点赞经验"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE interview_experience
            SET like_count = like_count + 1
            WHERE id = %s
        """, (experience_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error liking experience: {e}")
        return False


def get_districts():
    """获取所有区域列表"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT DISTINCT district FROM schools WHERE district IS NOT NULL ORDER BY district")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r['district'] for r in results]
    except Exception as e:
        print(f"Error fetching districts: {e}")
        return []


def get_categories():
    """获取所有学校类别列表"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT DISTINCT category FROM schools WHERE category IS NOT NULL ORDER BY category")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [r['category'] for r in results]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []


def get_featured_schools():
    """获取推荐学校"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, name_zh, name_en, district, school_type, category,
                   description, interview_format, ranking, is_featured, image_url
            FROM schools
            WHERE is_featured = TRUE
            ORDER BY ranking ASC NULLS LAST
            LIMIT 10
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Error fetching featured schools: {e}")
        return []
