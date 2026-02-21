#!/usr/bin/env python3
import sys

sys.path.insert(0, "/Volumes/Newsmy1 - m/app/web-poc")

from app import app

with app.test_client() as client:
    print("Testing routes:")

    r1 = client.get("/parent-coach")
    print(f"/parent-coach: {r1.status_code}")

    r2 = client.get("/energy-station")
    print(f"/energy-station: {r2.status_code}")

    r3 = client.get("/parent-community")
    print(f"/parent-community: {r3.status_code}")

    r4 = client.get("/api/parent-coach/mistakes")
    print(f"/api/parent-coach/mistakes: {r4.status_code}")

    r5 = client.get("/api/energy-station/summary")
    print(f"/api/energy-station/summary: {r5.status_code}")
