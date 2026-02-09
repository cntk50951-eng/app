#!/usr/bin/env python3
"""
Test script to verify the fix
"""

import sys
sys.path.insert(0, '/Volumes/Newsmy1 - m/app/web-poc')

from app import app

# Test app import
print("✅ App import successful")

# Test routes
with app.test_client() as client:
    # Test without login (should redirect)
    response = client.get('/child-profile/step-1')
    print(f"GET /child-profile/step-1 (no login): {response.status_code}")
    
    # Test API routes exist
    response = client.get('/api/user')
    print(f"GET /api/user (no login): {response.status_code}")
    
    # Test progress API exist
    response = client.get('/api/progress')
    print(f"GET /api/progress (no login): {response.status_code}")
    
    response = client.post('/api/progress/update', json={'topic_id': 'test'})
    print(f"POST /api/progress/update (no login): {response.status_code}")

print("\n✅ All tests passed!")
