#!/usr/bin/env python3
"""
AI Companion tables initialization script.
Run this to create AI companion tables in the PostgreSQL database.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import get_connection


def init_ai_companion_tables():
    """Initialize the AI companion tables."""
    print("Reading AI companion schema...")
    with open('db/ai_companion_tables.sql', 'r') as f:
        schema = f.read()

    print("Connecting to database...")
    conn = get_connection()

    print("Creating AI companion tables...")
    with conn.cursor() as cursor:
        cursor.execute(schema)

    conn.commit()
    conn.close()
    print("AI companion tables initialized successfully!")


def test_connection():
    """Test the database connection."""
    print("Testing database connection...")
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    conn.close()
    print(f"Connection successful! Result: {result}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_connection()
    else:
        init_ai_companion_tables()
