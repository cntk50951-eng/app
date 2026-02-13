"""
Database connection and utilities for AI Tutor.
Uses psycopg2 for PostgreSQL database operations.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', '')


def get_connection():
    """Get a database connection."""
    global DATABASE_URL

    # Re-read environment variable in case it changed
    DATABASE_URL = os.getenv('DATABASE_URL', '')

    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        raise Exception(f"Failed to connect to database: {e}")
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally fetch results."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            conn.commit()  # Always commit the transaction
            if fetch:
                result = cursor.fetchall()
                # Convert to regular dict for JSON serialization
                return [dict(row) for row in result]
            return cursor.rowcount
    except Exception as e:
        print(f"Query error: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ============ User Operations ============

def create_user(email, name=None, picture=None, user_type='email', google_id=None):
    """Create a new user."""
    query = """
        INSERT INTO users (email, name, picture, user_type, google_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, email, name, picture, user_type, created_at;
    """
    result = execute_query(query, (email, name, picture, user_type, google_id), fetch=True)
    return result[0] if result else None


def get_user_by_email(email):
    """Get user by email."""
    query = """
        SELECT id, email, name, picture, user_type, created_at
        FROM users WHERE email = %s;
    """
    result = execute_query(query, (email,), fetch=True)
    return result[0] if result else None


def get_user_by_id(user_id):
    """Get user by ID."""
    query = """
        SELECT id, email, name, picture, user_type, created_at
        FROM users WHERE id = %s;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None


def get_user_by_google_id(google_id):
    """Get user by Google ID."""
    query = """
        SELECT id, email, name, picture, user_type, created_at
        FROM users WHERE google_id = %s;
    """
    result = execute_query(query, (google_id,), fetch=True)
    return result[0] if result else None


# ============ Child Profile Operations ============

def create_child_profile(user_id, child_name, child_age, child_gender=None):
    """Create a new child profile."""
    query = """
        INSERT INTO child_profiles (user_id, child_name, child_age, child_gender)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, child_name, child_age, child_gender, profile_complete, created_at;
    """
    result = execute_query(query, (user_id, child_name, child_age, child_gender), fetch=True)
    return result[0] if result else None


def update_child_profile(profile_id, child_name=None, child_age=None, child_gender=None):
    """Update child profile."""
    updates = []
    params = []

    if child_name:
        updates.append("child_name = %s")
        params.append(child_name)
    if child_age:
        updates.append("child_age = %s")
        params.append(child_age)
    if child_gender:
        updates.append("child_gender = %s")
        params.append(child_gender)

    if not updates:
        return None

    params.append(profile_id)
    query = f"""
        UPDATE child_profiles
        SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, user_id, child_name, child_age, child_gender, profile_complete, updated_at;
    """
    result = execute_query(query, params, fetch=True)
    return result[0] if result else None


def mark_profile_complete(profile_id):
    """Mark profile as complete."""
    query = """
        UPDATE child_profiles
        SET profile_complete = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, user_id, child_name, child_age, child_gender, profile_complete;
    """
    result = execute_query(query, (profile_id,), fetch=True)
    return result[0] if result else None


def get_child_profile_by_user_id(user_id):
    """Get child profile by user ID."""
    query = """
        SELECT id, user_id, child_name, child_age, child_gender, profile_complete, created_at, updated_at
        FROM child_profiles WHERE user_id = %s;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None


def get_child_profile_by_id(profile_id):
    """Get child profile by ID."""
    query = """
        SELECT id, user_id, child_name, child_age, child_gender, profile_complete, created_at, updated_at
        FROM child_profiles WHERE id = %s;
    """
    result = execute_query(query, (profile_id,), fetch=True)
    return result[0] if result else None


# ============ Interests Operations ============

def add_user_interest(profile_id, interest_id):
    """Add an interest to user's profile."""
    query = """
        INSERT INTO user_interests (child_profile_id, interest_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    result = execute_query(query, (profile_id, interest_id), fetch=True)
    return result


def remove_user_interest(profile_id, interest_id):
    """Remove an interest from user's profile."""
    query = """
        DELETE FROM user_interests
        WHERE child_profile_id = %s AND interest_id = %s;
    """
    execute_query(query, (profile_id, interest_id))


def get_user_interests(profile_id):
    """Get all interests for a user profile."""
    query = """
        SELECT i.id, i.name_zh, i.emoji
        FROM interests i
        INNER JOIN user_interests ui ON i.id = ui.interest_id
        WHERE ui.child_profile_id = %s;
    """
    return execute_query(query, (profile_id,), fetch=True)


def set_user_interests(profile_id, interest_ids):
    """Set user's interests (replaces existing)."""
    if not interest_ids:
        return

    # Delete existing
    query = "DELETE FROM user_interests WHERE child_profile_id = %s;"
    execute_query(query, (profile_id,))

    # Insert new
    for interest_id in interest_ids:
        add_user_interest(profile_id, interest_id)


# ============ Target Schools Operations ============

def add_target_school(profile_id, school_type_id):
    """Add a target school type to user's profile."""
    query = """
        INSERT INTO target_schools (child_profile_id, school_type_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    result = execute_query(query, (profile_id, school_type_id), fetch=True)
    return result


def remove_target_school(profile_id, school_type_id):
    """Remove a target school from user's profile."""
    query = """
        DELETE FROM target_schools
        WHERE child_profile_id = %s AND school_type_id = %s;
    """
    execute_query(query, (profile_id, school_type_id))


def get_target_schools(profile_id):
    """Get all target schools for a user profile."""
    query = """
        SELECT st.id, st.name_zh, st.examples
        FROM school_types st
        INNER JOIN target_schools ts ON st.id = ts.school_type_id
        WHERE ts.child_profile_id = %s;
    """
    return execute_query(query, (profile_id,), fetch=True)


def set_target_schools(profile_id, school_type_ids):
    """Set user's target schools (replaces existing)."""
    if not school_type_ids:
        return

    # Delete existing
    query = "DELETE FROM target_schools WHERE child_profile_id = %s;"
    execute_query(query, (profile_id,))

    # Insert new
    for school_type_id in school_type_ids:
        add_target_school(profile_id, school_type_id)


# ============ Complete Profile Creation ============

def create_complete_profile(user_data, child_data, interests=None, target_schools_list=None):
    """
    Create a complete profile with all data.
    user_data: dict with email, name, picture, user_type, google_id
    child_data: dict with child_name, child_age, child_gender
    interests: list of interest IDs
    target_schools_list: list of school type IDs
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Create user
            cursor.execute("""
                INSERT INTO users (email, name, picture, user_type, google_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (user_data['email'], user_data.get('name'), user_data.get('picture'),
                  user_data.get('user_type', 'email'), user_data.get('google_id')))
            user_id = cursor.fetchone()[0]

            # Create child profile
            cursor.execute("""
                INSERT INTO child_profiles (user_id, child_name, child_age, child_gender, profile_complete)
                VALUES (%s, %s, %s, %s, TRUE)
                RETURNING id;
            """, (user_id, child_data['child_name'], child_data['child_age'], child_data.get('child_gender')))
            profile_id = cursor.fetchone()[0]

            # Add interests
            if interests:
                for interest_id in interests:
                    cursor.execute("""
                        INSERT INTO user_interests (child_profile_id, interest_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (profile_id, interest_id))

            # Add target schools
            if target_schools_list:
                for school_type_id in target_schools_list:
                    cursor.execute("""
                        INSERT INTO target_schools (child_profile_id, school_type_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (profile_id, school_type_id))

            conn.commit()
            return {'user_id': user_id, 'profile_id': profile_id}

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating complete profile: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ============ Achievement & Badge Operations ============

def get_all_badges():
    """Get all available badges."""
    query = """
        SELECT * FROM badges ORDER BY rarity, points;
    """
    return execute_query(query, fetch=True)


def get_badge_by_id(badge_id):
    """Get badge by ID."""
    query = "SELECT * FROM badges WHERE id = %s;"
    result = execute_query(query, (badge_id,), fetch=True)
    return result[0] if result else None


def get_user_badges(user_id):
    """Get all badges earned by a user."""
    query = """
        SELECT b.*, ub.earned_at, ub.progress as badge_progress
        FROM badges b
        INNER JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id = %s
        ORDER BY ub.earned_at DESC;
    """
    return execute_query(query, (user_id,), fetch=True)


def get_user_badge_progress(user_id):
    """Get user's progress towards all badges."""
    query = """
        SELECT b.id, b.name_zh, b.name_en, b.description, b.icon_emoji,
               b.category, b.requirement_type, b.requirement_value, b.points, b.rarity,
               COALESCE(ub.progress, 0) as progress,
               CASE WHEN ub.earned_at IS NOT NULL THEN TRUE ELSE FALSE END as earned
        FROM badges b
        LEFT JOIN user_badges ub ON b.id = ub.badge_id AND ub.user_id = %s
        ORDER BY b.rarity, b.points;
    """
    return execute_query(query, (user_id,), fetch=True)


def award_badge(user_id, badge_id):
    """Award a badge to a user."""
    query = """
        INSERT INTO user_badges (user_id, badge_id, progress, earned_at)
        VALUES (%s, %s, 100, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id, badge_id) DO UPDATE SET
            progress = 100,
            earned_at = CURRENT_TIMESTAMP
        RETURNING id;
    """
    result = execute_query(query, (user_id, badge_id), fetch=True)
    return result[0] if result else None


def update_badge_progress(user_id, badge_id, progress):
    """Update user's progress towards a badge."""
    query = """
        INSERT INTO user_badges (user_id, badge_id, progress)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, badge_id) DO UPDATE SET
            progress = %s
        RETURNING id;
    """
    result = execute_query(query, (user_id, badge_id, progress, progress), fetch=True)
    return result[0] if result else None


# ============ User Progress Operations ============

def get_user_progress_by_topic(user_id, topic_id):
    """Get user's progress for a specific topic."""
    query = "SELECT * FROM user_progress WHERE user_id = %s AND topic_id = %s;"
    result = execute_query(query, (user_id, topic_id), fetch=True)
    return result[0] if result else None


def get_user_all_progress(user_id):
    """Get all progress for a user."""
    query = "SELECT * FROM user_progress WHERE user_id = %s ORDER BY updated_at DESC;"
    return execute_query(query, (user_id,), fetch=True)


def update_user_progress(user_id, topic_id, status=None, completion_percent=None, practice_count=None, score=None, duration_seconds=None):
    """Update or insert user progress for a topic."""
    # Check if progress exists
    existing = get_user_progress_by_topic(user_id, topic_id)

    updates = []
    params = []

    if status:
        updates.append("status = %s")
        params.append(status)
    if completion_percent is not None:
        updates.append("completion_percent = %s")
        params.append(completion_percent)
    if practice_count is not None:
        updates.append("practice_count = %s")
        params.append(practice_count)
    if score is not None:
        updates.append("best_score = COALESCE(best_score, %s)")
        params.append(score)
    if duration_seconds is not None:
        updates.append("total_time_seconds = total_time_seconds + %s")
        params.append(duration_seconds)

    updates.append("last_practiced_at = CURRENT_TIMESTAMP")
    updates.append("updated_at = CURRENT_TIMESTAMP")

    if existing:
        # Update existing
        params.append(user_id)
        params.append(topic_id)
        query = f"""
            UPDATE user_progress
            SET {', '.join(updates)}
            WHERE user_id = %s AND topic_id = %s
            RETURNING *;
        """
    else:
        # Insert new
        params.extend([user_id, topic_id, status or 'not_started', completion_percent or 0])
        query = """
            INSERT INTO user_progress (user_id, topic_id, status, completion_percent, last_practiced_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING *;
        """

    result = execute_query(query, params, fetch=True)
    return result[0] if result else None


def mark_topic_complete(user_id, topic_id):
    """Mark a topic as completed."""
    query = """
        UPDATE user_progress
        SET status = 'completed', completion_percent = 100, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND topic_id = %s
        RETURNING *;
    """
    result = execute_query(query, (user_id, topic_id), fetch=True)
    return result[0] if result else None


def get_user_stats(user_id):
    """Get overall user statistics."""
    # Get total topics completed
    query1 = "SELECT COUNT(*) as completed FROM user_progress WHERE user_id = %s AND status = 'completed';"
    result1 = execute_query(query1, (user_id,), fetch=True)
    completed = result1[0]['completed'] if result1 else 0

    # Get total practice time
    query2 = "SELECT COALESCE(SUM(total_time_seconds), 0) as total_time FROM user_progress WHERE user_id = %s;"
    result2 = execute_query(query2, (user_id,), fetch=True)
    total_time = result2[0]['total_time'] if result2 else 0

    # Get total practice count
    query3 = "SELECT COALESCE(SUM(practice_count), 0) as practices FROM user_progress WHERE user_id = %s;"
    result3 = execute_query(query3, (user_id,), fetch=True)
    practices = result3[0]['practices'] if result3 else 0

    # Get badges count
    query4 = "SELECT COUNT(*) as badges FROM user_badges WHERE user_id = %s;"
    result4 = execute_query(query4, (user_id,), fetch=True)
    badges = result4[0]['badges'] if result4 else 0

    return {
        'completed_topics': completed,
        'total_practice_time': total_time,
        'total_practices': practices,
        'badges_earned': badges
    }


# ============ Practice Session Operations ============

def record_practice_session(user_id, topic_id, duration_seconds, score=None, feedback_rating=None, notes=None):
    """Record a practice session."""
    query = """
        INSERT INTO practice_sessions (user_id, topic_id, duration_seconds, score, feedback_rating, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *;
    """
    result = execute_query(query, (user_id, topic_id, duration_seconds, score, feedback_rating, notes), fetch=True)
    return result[0] if result else None


def get_user_practice_sessions(user_id, limit=50):
    """Get user's practice sessions."""
    query = """
        SELECT * FROM practice_sessions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s;
    """
    return execute_query(query, (user_id, limit), fetch=True)


def get_practice_sessions_in_period(user_id, start_date, end_date):
    """Get practice sessions in a date range."""
    query = """
        SELECT * FROM practice_sessions
        WHERE user_id = %s AND created_at >= %s AND created_at <= %s
        ORDER BY created_at DESC;
    """
    return execute_query(query, (user_id, start_date, end_date), fetch=True)


# ============ Learning Report Operations ============

def create_learning_report(user_id, report_type, period_start, period_end, topics_completed, total_practice_time, average_score, streak_days, badges_earned, highlights=None, improvements=None, recommendation=None):
    """Create a learning report."""
    query = """
        INSERT INTO learning_reports (user_id, report_type, period_start, period_end, topics_completed, total_practice_time, average_score, streak_days, badges_earned, highlights, improvements, recommendation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *;
    """
    result = execute_query(query, (user_id, report_type, period_start, period_end, topics_completed, total_practice_time, average_score, streak_days, badges_earned, highlights, improvements, recommendation), fetch=True)
    return result[0] if result else None


def get_user_reports(user_id, report_type=None, limit=10):
    """Get user's learning reports."""
    if report_type:
        query = """
            SELECT * FROM learning_reports
            WHERE user_id = %s AND report_type = %s
            ORDER BY generated_at DESC
            LIMIT %s;
        """
        return execute_query(query, (user_id, report_type, limit), fetch=True)
    else:
        query = """
            SELECT * FROM learning_reports
            WHERE user_id = %s
            ORDER BY generated_at DESC
            LIMIT %s;
        """
        return execute_query(query, (user_id, limit), fetch=True)


def get_latest_report(user_id, report_type):
    """Get the latest report of a specific type."""
    query = """
        SELECT * FROM learning_reports
        WHERE user_id = %s AND report_type = %s
        ORDER BY generated_at DESC
        LIMIT 1;
    """
    result = execute_query(query, (user_id, report_type), fetch=True)
    return result[0] if result else None


if __name__ == '__main__':
    print("Database utilities loaded.")
    if DATABASE_URL:
        print(f"Database URL configured: {DATABASE_URL[:50]}...")
    else:
        print("WARNING: DATABASE_URL is not set!")
        print("Please set the DATABASE_URL environment variable.")
        sys.exit(1)
