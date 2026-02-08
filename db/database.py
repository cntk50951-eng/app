"""
Database connection and utilities for AI Tutor.
Uses SQLAlchemy for database operations.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Database configuration - set DATABASE_URL in environment or .env file
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    """Get a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
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
            if fetch:
                result = cursor.fetchall()
                # Convert to regular dict for JSON serialization
                return [dict(row) for row in result]
            conn.commit()
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


if __name__ == '__main__':
    print("Database utilities loaded.")
    print(f"Database URL: {DATABASE_URL[:50]}...")
