#!/usr/bin/env python3
"""
Test script to verify database operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import (
    create_user, get_user_by_email, get_user_by_id,
    create_child_profile, get_child_profile_by_user_id,
    add_user_interest, get_user_interests,
    add_target_school, get_target_schools,
    create_complete_profile
)


def test_operations():
    """Test all database operations."""

    # Test creating a user
    print("1. Creating user...")
    user = create_user(
        email="test@example.com",
        name="Test User",
        picture=None,
        user_type="email"
    )
    print(f"   Created user: {user}")

    # Test getting user by email
    print("2. Getting user by email...")
    user = get_user_by_email("test@example.com")
    print(f"   Retrieved user: {user}")

    # Test creating child profile
    print("3. Creating child profile...")
    profile = create_child_profile(
        user_id=user['id'],
        child_name="小明",
        child_age="K3",
        child_gender="male"
    )
    print(f"   Created profile: {profile}")

    # Test adding interests
    print("4. Adding interests...")
    add_user_interest(profile['id'], 'dinosaurs')
    add_user_interest(profile['id'], 'lego')
    add_user_interest(profile['id'], 'art')
    interests = get_user_interests(profile['id'])
    print(f"   Interests: {interests}")

    # Test adding target schools
    print("5. Adding target schools...")
    add_target_school(profile['id'], 'academic')
    add_target_school(profile['id'], 'holistic')
    schools = get_target_schools(profile['id'])
    print(f"   Target schools: {schools}")

    # Test getting profile by user ID
    print("6. Getting profile by user ID...")
    profile = get_child_profile_by_user_id(user['id'])
    print(f"   Retrieved profile: {profile}")

    # Test creating complete profile at once
    print("7. Creating complete profile (all in one)...")
    result = create_complete_profile(
        user_data={
            'email': 'complete@example.com',
            'name': 'Complete User',
            'picture': None,
            'user_type': 'email'
        },
        child_data={
            'child_name': '小红',
            'child_age': 'K2',
            'child_gender': 'female'
        },
        interests=['music', 'reading', 'swimming'],
        target_schools_list=['international', 'traditional']
    )
    print(f"   Created: {result}")

    print("\nAll tests passed!")


if __name__ == '__main__':
    test_operations()
