"""
AI Tutor - Web POC Application
Flask-based web application for personalized primary school interview preparation.
"""

import os
import sys
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
)
from flask_dotenv import DotEnv
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import requests

# Load environment variables from .env file FIRST
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure secret key - use environment variable or generate fallback
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(32).hex()

# Initialize DotEnv for environment variables (this reads from .env file)
env = DotEnv()
env.init_app(app, verbose_mode=False)

# Force reload environment variables from system/Render
os.environ.update(os.environ)

# Database URL - must be read from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    print("WARNING: DATABASE_URL environment variable is not set!")
    print("Database operations will fail until DATABASE_URL is configured.")
    print("Please set DATABASE_URL in your environment or .env file.")


def get_db_functions():
    """Lazy import database functions."""
    try:
        from db.database import (
            create_user,
            get_user_by_email,
            get_user_by_google_id,
            get_user_by_id,
            create_child_profile,
            get_child_profile_by_user_id,
            update_child_profile,
            set_user_interests,
            get_user_interests,
            set_target_schools,
            get_target_schools,
            create_complete_profile,
        )

        return {
            "create_user": create_user,
            "get_user_by_email": get_user_by_email,
            "get_user_by_google_id": get_user_by_google_id,
            "get_user_by_id": get_user_by_id,
            "create_child_profile": create_child_profile,
            "get_child_profile_by_user_id": get_child_profile_by_user_id,
            "update_child_profile": update_child_profile,
            "set_user_interests": set_user_interests,
            "get_user_interests": get_user_interests,
            "set_target_schools": set_target_schools,
            "get_target_schools": get_target_schools,
            "create_complete_profile": create_complete_profile,
        }
    except Exception as e:
        print(f"Error importing database functions: {e}")
        return None


# Configure OAuth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"  # Force HTTPS in production
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Scopes for Google OAuth
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/login",
    "/signup",
    "/auth/google",
    "/auth/google/callback",
    "/unlock-full-access",
    "/mock-interview",
    "/mock-interview/start",
    "/mock-interview/result",
    "/mock-interview/voice",
    "/school-advisor",
    "/school-advisor/analyze",
    "/capability-radar",
    "/question-bank",
    "/question-bank/practice",
    "/practice",
    "/practice/daily-challenge",
    "/practice/wrong-questions",
    "/practice/favorites",
    "/practice/recommended",
    "/practice/progress",
    "/interview-guide",
    "/reports",
    "/learning-path",
    "/parent-interview",
    "/parent-interview/voice",
    "/parent-interview/result",
    "/parent-interview/history",
    "/school-questions",
    "/school-questions/schools",
    "/school-questions/school",
    "/school-questions/ai-match",
    "/interview-experience",
    "/interview-timeline",
    "/api/schools",
    "/api/schools",
    "/api/ai-match/recommend",
    "/api/experience",
    "/api/timeline",
    "/api/questions/like",
    "/api/experience/like",
    "/micro-lessons",
    "/daily-tasks",
    "/practice/quick",
    "/practice/voice",
    "/api/micro-lessons",
    "/api/micro-lessons/generate",
    "/api/daily-tasks",
    "/api/daily-tasks/complete",
    "/api/practice/submit",
    "/api/practice/history",
    "/showcase",
    "/showcase/generate",
    "/showcase/share/<share_type>",
    "/api/showcase/generate",
    "/api/showcase/templates",
    "/api/showcase/share",
    "/energy-station",
    "/api/energy-station/summary",
    "/api/energy-station/micro-lessons",
    "/api/energy-station/micro-lesson/<lesson_id>",
    "/api/energy-station/energy-pack",
    "/api/energy-station/parent-lessons",
    "/api/energy-station/parent-lesson/<lesson_id>",
    "/api/energy-station/companion/persona",
    "/api/energy-station/companion/chat",
    "/parent-coach",
    "/api/parent-coach/questions",
    "/api/parent-coach/session",
    "/api/parent-coach/mistakes",
    "/confidence-training",
    "/api/confidence-training/summary",
    "/api/confidence-training/breathing",
    "/api/confidence-training/breathing/<exercise_id>",
    "/api/confidence-training/affirmation",
    "/api/confidence-training/affirmation/generate",
    "/api/confidence-training/pressure-test",
    "/api/confidence-training/pressure-test/<int:level>",
    "/api/confidence-training/courses",
    "/api/confidence-training/course/<course_id>",
    "/api/confidence-training/emotion/analyze",
    "/api/confidence-training/emotion/analyze-answer",
    "/growth-profile",
    "/growth-profile/generate-pdf",
    "/api/growth-profile",
    "/api/growth-profile/pdf",
    "/api/growth-profile/feedback",
    "/parent-child-challenge",
    "/api/parent-child-challenge/start",
    "/api/parent-child-challenge/submit",
    "/api/parent-child-challenge/leaderboard",
    "/api/parent-child-challenge/badges",
]


def login_required(f):
    """Decorator to require login for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to continue", "warning")
            return redirect(url_for("login", next=request.full_path))
        return f(*args, **kwargs)

    return decorated_function


def get_google_oauth_flow():
    """Create Google OAuth flow instance."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "project_id": "ai-tutor-poc",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )
    return flow


def get_user_info(access_token):
    """Fetch user info from Google API."""
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching user info: {e}")
    return None


def load_user_session(user_id):
    """Load user and profile data from database into session."""
    db = get_db_functions()
    if not db:
        return False

    # Get user from database
    user = db["get_user_by_id"](user_id)
    if not user:
        return False

    # Store user info in session
    session["logged_in"] = True
    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["name"] = user.get("name")
    session["picture"] = user.get("picture")
    session["user_type"] = user["user_type"]

    # Get child profile
    profile = db["get_child_profile_by_user_id"](user_id)
    if profile:
        session["profile_id"] = profile["id"]
        session["child_name"] = profile["child_name"]
        session["child_age"] = profile["child_age"]
        session["child_gender"] = profile.get("child_gender")
        session["profile_complete"] = profile["profile_complete"]

        # Get interests
        interests = db["get_user_interests"](profile["id"])
        session["child_interests"] = [i["id"] for i in interests]

        # Get target schools
        schools = db["get_target_schools"](profile["id"])
        session["target_schools"] = [s["id"] for s in schools]

    return True


@app.before_request
def require_login():
    """Check if user is logged in for protected routes."""
    # Allow public routes (exact match)
    if request.path in PUBLIC_ROUTES:
        return

    # Allow dynamic public routes and prefix matches
    for route in PUBLIC_ROUTES:
        # Check prefix match for routes (especially those with parameters)
        if request.path.startswith(route.rstrip("/")):
            return

    # Check if user is logged in
    if not session.get("logged_in"):
        # Store the original URL for redirect after login
        if request.is_json:
            return jsonify({"error": "Unauthorized", "message": "Please log in"}), 401
        return redirect(url_for("login", next=request.full_path))


@app.route("/")
def index():
    """Welcome/Landing page."""
    return render_template("welcome.html")


@app.route("/favicon.ico")
def favicon():
    """Return empty response for favicon to avoid 404."""
    return "", 204


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login selection page."""
    # If already logged in, redirect to dashboard
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    next_url = request.args.get("next", "/dashboard")

    if request.method == "POST":
        # Handle email login
        email = request.form.get("email")
        next_url = request.form.get("next", "/dashboard")

        if not email:
            flash("Please enter your email", "error")
            return render_template("login.html", next_url=next_url)

        # Get database functions
        db = get_db_functions()
        if not db:
            flash("Database is not configured.", "error")
            return render_template("login.html", next_url=next_url)

        # Check if user exists, create if not
        user = db["get_user_by_email"](email)
        if not user:
            user = db["create_user"](
                email=email, name=email.split("@")[0], user_type="email"
            )

        # Set session
        session["logged_in"] = True
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["name"] = user.get("name")
        session["picture"] = user.get("picture")
        session["user_type"] = user["user_type"]

        # Check for child profile
        profile = db["get_child_profile_by_user_id"](user["id"])
        if profile:
            session["profile_id"] = profile["id"]
            session["child_name"] = profile["child_name"]
            session["child_age"] = profile["child_age"]
            session["child_gender"] = profile.get("child_gender")
            session["profile_complete"] = profile["profile_complete"]

        flash("Welcome back!", "success")

        # Redirect to child profile setup only if profile_complete is explicitly False
        if session.get("profile_complete") is False:
            return redirect(url_for("child_profile_step1"))

        return redirect(next_url)

    return render_template("login.html", next_url=next_url)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Signup page."""
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    next_url = request.args.get("next", "/dashboard")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        next_url = request.form.get("next", "/dashboard")

        # Basic validation
        if not email or not password:
            flash("Please fill in all fields", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("signup.html")

        # Get database functions
        db = get_db_functions()
        if not db:
            flash("Database is not configured. Please contact support.", "error")
            return render_template("signup.html")

        # Check if user already exists
        user = db["get_user_by_email"](email)

        if not user:
            # Create new user in database
            user = db["create_user"](
                email=email, name=email.split("@")[0], user_type="email"
            )

        # Directly set session values
        session["logged_in"] = True
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["name"] = user.get("name")
        session["picture"] = user.get("picture")
        session["user_type"] = user["user_type"]

        # Check for child profile
        profile = db["get_child_profile_by_user_id"](user["id"])
        if profile:
            session["profile_id"] = profile["id"]
            session["child_name"] = profile["child_name"]
            session["child_age"] = profile["child_age"]
            session["child_gender"] = profile.get("child_gender")
            session["profile_complete"] = profile["profile_complete"]

        flash(
            "Welcome back!" if profile else "Account created successfully!", "success"
        )

        # Redirect to child profile setup if profile is incomplete
        if session.get("profile_complete") is False:
            return redirect(url_for("child_profile_step1"))

        return redirect(next_url)

    return render_template("signup.html", next_url=next_url)


@app.route("/auth/google")
def auth_google():
    """Initiate Google OAuth flow."""
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    # Save the next URL to session for redirect after login
    next_url = request.args.get("next", "/dashboard")
    session["next_url"] = next_url

    flow = get_google_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/auth/google/callback")
def auth_google_callback():
    """Handle Google OAuth callback."""
    # Verify state to prevent CSRF
    state = session.get("oauth_state")
    if not state or state != request.args.get("state"):
        flash("Invalid OAuth state", "error")
        return redirect(url_for("login"))

    try:
        flow = get_google_oauth_flow()
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        access_token = credentials.token

        # Get user info from Google
        user_info = get_user_info(access_token)

        if user_info:
            google_id = user_info.get("id")
            email = user_info.get("email")
            name = user_info.get("name")
            picture = user_info.get("picture")

            # Get database functions
            db = get_db_functions()
            if not db:
                flash("Database is not configured. Please contact support.", "error")
                return redirect(url_for("login"))

            # Check if user already exists
            user = db["get_user_by_email"](email)
            if not user:
                user = db["get_user_by_google_id"](google_id)

            if not user:
                # Create new user in database
                user = db["create_user"](
                    email=email,
                    name=name,
                    picture=picture,
                    user_type="google",
                    google_id=google_id,
                )

            # Directly set session values
            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["name"] = user.get("name")
            session["picture"] = user.get("picture")
            session["user_type"] = user["user_type"]

            # Check for child profile
            profile = db["get_child_profile_by_user_id"](user["id"])
            if profile:
                session["profile_id"] = profile["id"]
                session["child_name"] = profile["child_name"]
                session["child_age"] = profile["child_age"]
                session["child_gender"] = profile.get("child_gender")
                session["profile_complete"] = profile["profile_complete"]

                # Get interests
                interests = db["get_user_interests"](profile["id"])
                session["child_interests"] = [i["id"] for i in interests]

                # Get target schools
                schools = db["get_target_schools"](profile["id"])
                session["target_schools"] = [s["id"] for s in schools]

            flash(f"Welcome, {name}!", "success")

            # Redirect to child profile setup if profile is incomplete
            if session.get("profile_complete") is False:
                return redirect(url_for("child_profile_step1"))

            # Redirect to intended URL or dashboard
            next_url = session.pop("next_url", None)
            if not next_url or next_url == "/":
                next_url = "/dashboard"
            return redirect(next_url)
        else:
            flash("Failed to get user information", "error")
            return redirect(url_for("login"))

    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash("Login failed. Please try again.", "error")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """Log out the user."""
    # Clear session
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


@app.route("/child-profile/step-1", methods=["GET", "POST"])
@login_required
def child_profile_step1():
    """Child profile creation - Step 1: Basic Info."""
    db = get_db_functions()
    user_id = session.get("user_id")
    profile = db["get_child_profile_by_user_id"](user_id) if db else None

    # Pre-fill data if profile exists
    initial_data = {}
    if profile:
        initial_data = {
            "child_name": profile["child_name"],
            "child_age": profile["child_age"],
            "child_gender": profile.get("child_gender"),
        }

    if request.method == "POST":
        child_name = request.form.get("child_name")
        child_age = request.form.get("child_age")
        child_gender = request.form.get("child_gender")

        # Validate input
        if not child_name or not child_age or not child_gender:
            flash("Please fill in all fields", "error")
            return redirect(url_for("child_profile_step1"))

        if not db:
            # Mock profile for development (no database)
            session["child_name"] = child_name
            session["child_age"] = child_age
            session["child_gender"] = child_gender
            session["profile_id"] = f"mock_{user_id}"
            flash("Profile saved! (Development mode)", "success")
            return redirect(url_for("child_profile_step2"))

        try:
            if profile:
                # Update existing profile
                profile = db["update_child_profile"](
                    profile_id=profile["id"],
                    child_name=child_name,
                    child_age=child_age,
                    child_gender=child_gender,
                )
            else:
                # Create new profile
                profile = db["create_child_profile"](
                    user_id=user_id,
                    child_name=child_name,
                    child_age=child_age,
                    child_gender=child_gender,
                )
        except Exception as e:
            print(f"Database error in child_profile_step1: {e}")
            import traceback

            traceback.print_exc()
            flash(
                "Failed to save profile. Please try again or contact support.", "error"
            )
            return redirect(url_for("child_profile_step1"))

        # Update session
        session["child_name"] = child_name
        session["child_age"] = child_age
        session["child_gender"] = child_gender
        session["profile_id"] = profile["id"]

        flash("Profile saved!", "success")
        return redirect(url_for("child_profile_step2"))

    return render_template("child-profile-step-1.html", initial_data=initial_data)


@app.route("/child-profile/step-2", methods=["GET", "POST"])
@login_required
def child_profile_step2():
    """Child profile creation - Step 2: Interests Selection."""
    interests = [
        {"id": "dinosaurs", "emoji": "🦕", "name": "恐龍"},
        {"id": "lego", "emoji": "🧱", "name": "Lego"},
        {"id": "art", "emoji": "🎨", "name": "畫畫"},
        {"id": "sports", "emoji": "⚽", "name": "運動"},
        {"id": "music", "emoji": "🎵", "name": "音樂"},
        {"id": "reading", "emoji": "📚", "name": "閱讀"},
        {"id": "science", "emoji": "🔬", "name": "科學"},
        {"id": "cooking", "emoji": "🍳", "name": "煮飯仔"},
        {"id": "cars", "emoji": "🚗", "name": "車"},
        {"id": "planes", "emoji": "✈️", "name": "飛機"},
        {"id": "animals", "emoji": "🐶", "name": "動物"},
        {"id": "nature", "emoji": "🌳", "name": "大自然"},
        {"id": "performing", "emoji": "🎭", "name": "表演"},
        {"id": "gaming", "emoji": "🎮", "name": "遊戲"},
        {"id": "swimming", "emoji": "🏊", "name": "游泳"},
    ]

    profile_id = session.get("profile_id")

    # Check if user has completed Step 1 - redirect if not
    if not profile_id:
        flash("Please complete Step 1 first to create your child profile.", "error")
        return redirect(url_for("child_profile_step1"))

    selected_interests = session.get("child_interests", [])

    if request.method == "POST":
        # Support both getlist (multiple values) and comma-separated string
        interests_value = request.form.get("interests", "")
        if interests_value:
            # Handle comma-separated string
            selected_interests = [
                i.strip() for i in interests_value.split(",") if i.strip()
            ]
        else:
            selected_interests = request.form.getlist("interests")

        db = get_db_functions()
        if db and profile_id:
            try:
                db["set_user_interests"](profile_id, selected_interests)
            except Exception as e:
                print(f"Database error in child_profile_step2: {e}")
                import traceback

                traceback.print_exc()
                flash(
                    "Failed to save interests. Please try again or contact support.",
                    "error",
                )
                return redirect(url_for("child_profile_step2"))

        session["child_interests"] = selected_interests
        flash("Interests saved!", "success")
        return redirect(url_for("child_profile_step3"))

    return render_template(
        "child-profile-step-2.html",
        interests=interests,
        selected_interests=selected_interests,
    )


@app.route("/child-profile/step-3", methods=["GET", "POST"])
@login_required
def child_profile_step3():
    """Child profile creation - Step 3: Target Schools."""
    school_types = [
        {"id": "academic", "name": "學術型", "examples": "DBS/SPCC"},
        {"id": "holistic", "name": "全人型", "examples": "英華/TSL"},
        {"id": "international", "name": "國際型", "examples": "CKY/港同"},
        {"id": "traditional", "name": "傳統名校", "examples": "KTS/SFA"},
    ]

    profile_id = session.get("profile_id")

    # Check if user has completed Step 1 - redirect if not
    if not profile_id:
        flash("Please complete Step 1 first to create your child profile.", "error")
        return redirect(url_for("child_profile_step1"))

    selected_schools = session.get("target_schools", [])

    if request.method == "POST":
        target_schools = request.form.getlist("target_schools")

        db = get_db_functions()
        if db and profile_id:
            try:
                db["set_target_schools"](profile_id, target_schools)
            except Exception as e:
                print(f"Database error in child_profile_step3: {e}")
                import traceback

                traceback.print_exc()
                flash(
                    "Failed to save target schools. Please try again or contact support.",
                    "error",
                )
                return redirect(url_for("child_profile_step3"))

        session["target_schools"] = target_schools
        session["profile_complete"] = True

        flash("Profile completed successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "child-profile-step-3.html",
        school_types=school_types,
        selected_schools=selected_schools,
    )


@app.route("/dashboard")
@login_required
def dashboard():
    """Parent dashboard page."""
    # Reload user data from database to ensure freshness
    user_id = session.get("user_id")
    if user_id:
        load_user_session(user_id)

    return render_template("dashboard.html")


@app.route("/settings")
@login_required
def settings():
    """Parent settings / console page."""
    user_id = session.get("user_id")

    # Get user subscription status
    subscription_status = "trial"
    trial_topics_used = 0

    if user_id:
        try:
            db_funcs = get_db_functions()
            if db_funcs and "get_user_by_id" in db_funcs:
                user = db_funcs["get_user_by_id"](user_id)
                if user:
                    subscription_status = user.get("subscription_status", "trial")
                    trial_topics_used = user.get("trial_topics_used", 0)
        except Exception as e:
            print(f"Error fetching user: {e}")

    return render_template(
        "settings.html",
        subscription_status=subscription_status,
        trial_topics_used=trial_topics_used,
    )


@app.route("/lesson")
@app.route("/lesson/")
def lesson_redirect():
    """Redirect /lesson to dashboard or default topic."""
    return redirect(url_for("dashboard"))


@app.route("/lesson/<topic_id>")
@login_required
def lesson(topic_id):
    """Lesson content page."""
    topics = {
        "self-introduction": {
            "id": "self-introduction",
            "title": "自我介紹",
            "description": "學習自信地介紹自己的特點",
            "icon": "person",
            "progress": 1,
            "total": 5,
        },
        "interests": {
            "id": "interests",
            "title": "興趣愛好",
            "description": "深入探討興趣細節",
            "icon": "star",
            "progress": 2,
            "total": 5,
        },
        "family": {
            "id": "family",
            "title": "家庭介紹",
            "description": "家庭成員與關係",
            "icon": "group",
            "progress": 3,
            "total": 5,
        },
        "observation": {
            "id": "observation",
            "title": "觀察力訓練",
            "description": "圖片描述與細節觀察",
            "icon": "visibility",
            "progress": 4,
            "total": 5,
        },
        "scenarios": {
            "id": "scenarios",
            "title": "處境題",
            "description": "簡單情境處理",
            "icon": "psychology",
            "progress": 5,
            "total": 5,
        },
    }

    topic = topics.get(topic_id)
    if not topic:
        return redirect(url_for("dashboard"))

    return render_template("lesson.html", topic=topic)


@app.route("/api/generate", methods=["POST"])
@login_required
def generate_content():
    """
    API endpoint for generating AI teaching content.
    Integrates with MiniMax API for text generation.
    """
    data = request.json
    topic = data.get("topic")
    force_regenerate = data.get("force_regenerate", False)

    # Get profile from session/database
    user_id = session.get("user_id")
    profile_id = session.get("profile_id")

    if not topic:
        return jsonify(
            {"error": "Topic is required", "message": "請指定要生成的主題"}
        ), 400

    # Build profile dict from session (always available)
    profile = {
        "id": profile_id or f"mock_{user_id}",
        "child_name": session.get("child_name"),
        "child_age": session.get("child_age"),
        "child_gender": session.get("child_gender"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    # Try to enhance with database data if available
    db = get_db_functions()
    if db:
        # Get from database if not in session
        if not profile["child_name"]:
            try:
                child_profile = db["get_child_profile_by_user_id"](user_id)
                if child_profile:
                    profile["id"] = child_profile["id"]
                    profile["child_name"] = child_profile["child_name"]
                    profile["child_age"] = child_profile["child_age"]
                    profile["child_gender"] = child_profile.get("child_gender")
            except Exception as e:
                print(f"Warning: Could not fetch child profile: {e}")

        if not profile["interests"] and profile.get("id"):
            try:
                interests = db["get_user_interests"](profile["id"])
                profile["interests"] = [i["id"] for i in interests]
            except Exception as e:
                print(f"Warning: Could not fetch interests: {e}")

        if not profile["target_schools"] and profile.get("id"):
            try:
                schools = db["get_target_schools"](profile["id"])
                profile["target_schools"] = [s["id"] for s in schools]
            except Exception as e:
                print(f"Warning: Could not fetch target schools: {e}")

    if not profile["child_name"]:
        # Use default values for development/demo mode
        print("⚠️ Profile incomplete, using default values")
        profile["child_name"] = "小明"
        profile["child_age"] = "K2"
        profile["child_gender"] = "不透露"
        profile["interests"] = ["lego", "sports"]
        profile["target_schools"] = ["academic"]

    # Clear cache if force regenerate
    if force_regenerate:
        try:
            from services.ai_generator import clear_cache

            clear_cache(profile_id)
        except Exception as e:
            print(f"Warning: Could not clear cache: {e}")

    # Generate content
    try:
        from services.ai_generator import generate_teaching_content_with_audio

        content = generate_teaching_content_with_audio(profile, topic)

        # Ensure content has required fields
        if not content:
            return jsonify(
                {
                    "error": "Content generation failed",
                    "message": "內容生成失敗，請稍後再試",
                    "fallback": True,
                }
            ), 200

        return jsonify(content)
    except Exception as e:
        print(f"Error generating content: {e}")
        return jsonify(
            {"error": "Generation failed", "message": "生成內容失敗，請稍後再試"}
        ), 500


@app.route("/unlock-full-access")
def unlock_full_access():
    """Paywall page for unlocking full access."""
    user_id = session.get("user_id")

    subscription_status = "trial"
    trial_topics_used = 0

    if user_id:
        try:
            db_funcs = get_db_functions()
            if db_funcs and "get_user_by_id" in db_funcs:
                user = db_funcs["get_user_by_id"](user_id)
                if user:
                    subscription_status = user.get("subscription_status", "trial")
                    trial_topics_used = user.get("trial_topics_used", 0)
        except Exception as e:
            print(f"Error fetching user: {e}")

    return render_template(
        "unlock-full-access.html",
        subscription_status=subscription_status,
        trial_topics_used=trial_topics_used,
    )


@app.route("/profile/edit")
@login_required
def profile_edit():
    """编辑孩子资料页面."""
    return render_template("profile-edit.html")


@app.route("/parent-notes")
@login_required
def parent_notes():
    """家长笔记页面."""
    return render_template("parent-notes.html")


@app.route("/recording")
@login_required
def recording():
    """录音练习页面."""
    return render_template("recording.html")


@app.route("/api/user")
@login_required
def get_user():
    """Get current user info."""
    return jsonify(
        {
            "logged_in": session.get("logged_in", False),
            "name": session.get("name"),
            "email": session.get("email"),
            "picture": session.get("picture"),
            "profile_complete": session.get("profile_complete", False),
            "child_name": session.get("child_name"),
            "child_age": session.get("child_age"),
        }
    )


@app.route("/api/user/profile", methods=["GET"])
@login_required
def get_child_profile():
    """获取孩子画像信息."""
    user_id = session.get("user_id")
    try:
        db = get_db_functions()
        if db and "get_child_profile_by_user_id" in db:
            profile = db["get_child_profile_by_user_id"](user_id)
            if profile:
                return jsonify(profile)
        # Return mock data if no database
        return jsonify(
            {
                "child_name": session.get("child_name"),
                "child_age": session.get("child_age"),
                "child_gender": session.get("child_gender"),
                "profile_complete": session.get("profile_complete", False),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/stats")
@login_required
def get_user_stats():
    """获取用户使用统计（整合 analytics + progress 服务）."""
    user_id = session.get("user_id")

    # 使用 analytics 服务
    try:
        from services.analytics import get_user_analytics, get_topic_progress

        analytics_data = get_user_analytics(user_id)
        topic_progress = get_topic_progress(user_id)
    except ImportError:
        # 回退到 mock 数据
        analytics_data = {
            "topics_completed": session.get("topics_completed", 0),
            "total_minutes": session.get("total_minutes", 0),
            "notes_created": 0,
            "feedback_submitted": 0,
            "last_active": session.get("last_active"),
        }
        topic_progress = {}

    # 使用 progress 服务获取详细统计
    try:
        from services.progress import get_overall_stats, get_all_topic_summaries

        overall_stats = get_overall_stats(user_id)
        topic_summaries = get_all_topic_summaries(user_id)
    except ImportError:
        overall_stats = {
            "total_topics": 5,
            "completed_topics": analytics_data.get("topics_completed", 0),
            "completion_percent": 0,
            "total_practices": 0,
            "total_minutes": analytics_data.get("total_minutes", 0),
            "streak_days": session.get("streak_days", 0),
            "first_practice_date": None,
            "last_active": analytics_data.get("last_active"),
        }
        topic_summaries = []

    stats = {
        "topics_completed": overall_stats.get(
            "completed_topics", analytics_data.get("topics_completed", 0)
        ),
        "total_minutes": overall_stats.get(
            "total_minutes", analytics_data.get("total_minutes", 0)
        ),
        "streak_days": overall_stats.get("streak_days", session.get("streak_days", 0)),
        "last_active": overall_stats.get(
            "last_active", analytics_data.get("last_active")
        ),
        "total_practices": overall_stats.get("total_practices", 0),
        "notes_created": analytics_data.get("notes_created", 0),
        "completion_percent": overall_stats.get("completion_percent", 0),
        "topics": topic_summaries,
    }

    return jsonify(stats)


@app.route("/api/progress/start", methods=["POST"])
@login_required
def start_lesson_progress():
    """記錄練習開始."""
    user_id = session.get("user_id")
    data = request.json
    topic_id = data.get("topic_id")

    if not topic_id:
        return jsonify({"error": "Topic ID is required"}), 400

    try:
        from services.progress import update_progress
        from services.analytics import track_event

        # 更新進度
        update_progress(user_id, topic_id, "start")

        # 追蹤事件
        track_event(user_id, "LESSON_START", {"topic_id": topic_id})

        return jsonify({"success": True, "message": "練習開始記錄"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/progress/complete", methods=["POST"])
@login_required
def complete_lesson_progress():
    """記錄練習完成."""
    user_id = session.get("user_id")
    data = request.json
    topic_id = data.get("topic_id")
    score = data.get("score")
    duration_seconds = data.get("duration_seconds")

    if not topic_id:
        return jsonify({"error": "Topic ID is required"}), 400

    try:
        from services.progress import update_progress, mark_topic_complete
        from services.analytics import track_event

        # 更新進度
        mark_topic_complete(user_id, topic_id, score, duration_seconds)

        # 追蹤事件
        track_event(
            user_id,
            "LESSON_COMPLETE",
            {
                "topic_id": topic_id,
                "score": score,
                "duration_minutes": round(duration_seconds / 60, 2)
                if duration_seconds
                else None,
            },
        )

        return jsonify({"success": True, "message": "練習完成！"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/progress/recommendations")
@login_required
def get_recommendations():
    """獲取練習推薦."""
    user_id = session.get("user_id")

    try:
        from services.progress import get_recommendations

        recommendations = get_recommendations(user_id)
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/progress/report")
@login_required
def get_progress_report():
    """獲取進度報告."""
    user_id = session.get("user_id")

    try:
        from services.progress import generate_progress_report

        report = generate_progress_report(user_id)
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/event", methods=["POST"])
@login_required
def track_analytics_event():
    """手動追蹤分析事件."""
    user_id = session.get("user_id")
    data = request.json

    event_type = data.get("event_type")
    properties = data.get("properties", {})

    if not event_type:
        return jsonify({"error": "Event type is required"}), 400

    try:
        from services.analytics import track_event

        track_event(user_id, event_type, properties)
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/summary")
@login_required
def get_analytics_summary():
    """獲取用戶分析摘要."""
    user_id = session.get("user_id")

    try:
        from services.analytics import get_user_analytics

        summary = get_user_analytics(user_id)
        return jsonify(summary)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/stats/update", methods=["POST"])
@login_required
def update_user_stats():
    """更新用户使用统计."""
    data = request.json
    topic_id = data.get("topic_id")
    action = data.get("action", "practice")

    # 更新 session
    if topic_id:
        topics_completed = session.get("topics_completed", 0)
        if action == "complete":
            # 标记主题为完成
            session["topics_completed"] = topics_completed + 1

            # 更新最后活跃时间
            session["last_active"] = datetime.now().isoformat()

    return jsonify({"success": True})


# ============ Settings API ============


@app.route("/api/user/settings", methods=["GET"])
@login_required
def get_user_settings():
    """获取用户设置."""
    user_id = session.get("user_id")

    try:
        db = get_db_functions()
        if db and "get_user_by_id" in db:
            user = db["get_user_by_id"](user_id)
            if user:
                return jsonify(
                    {
                        "language": user.get("preferred_language", "cantonese"),
                        "notifications": {
                            "dailyReminder": user.get("notify_daily", True),
                            "newTopic": user.get("notify_new_topic", True),
                            "weeklyReport": user.get("notify_weekly", False),
                            "marketing": user.get("notify_marketing", False),
                        },
                    }
                )
    except Exception as e:
        print(f"Error fetching settings: {e}")

    # Return default settings if no database
    return jsonify(
        {
            "language": "cantonese",
            "notifications": {
                "dailyReminder": True,
                "newTopic": True,
                "weeklyReport": False,
                "marketing": False,
            },
        }
    )


@app.route("/api/user/settings/language", methods=["POST"])
@login_required
def update_language():
    """更新语言偏好."""
    user_id = session.get("user_id")
    data = request.json
    language = data.get("language", "cantonese")

    try:
        db.update_user(user_id, preferred_language=language)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/settings/notifications", methods=["POST"])
@login_required
def update_notifications():
    """更新通知设置."""
    user_id = session.get("user_id")
    data = request.json
    setting = data.get("setting")
    value = data.get("value", False)

    # Map setting name to database field
    field_map = {
        "dailyReminder": "notify_daily",
        "newTopic": "notify_new_topic",
        "weeklyReport": "notify_weekly",
        "marketing": "notify_marketing",
    }

    field = field_map.get(setting)
    if field:
        try:
            db.update_user(user_id, **{field: value})
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid setting"}), 400


@app.route("/api/user/settings", methods=["POST"])
@login_required
def update_settings():
    """批量更新用户设置."""
    user_id = session.get("user_id")
    data = request.json

    try:
        update_data = {}

        if "language" in data:
            update_data["preferred_language"] = data["language"]

        if "notifications" in data:
            notifs = data["notifications"]
            update_data.update(
                {
                    "notify_daily": notifs.get("dailyReminder", True),
                    "notify_new_topic": notifs.get("newTopic", True),
                    "notify_weekly": notifs.get("weeklyReport", False),
                    "notify_marketing": notifs.get("marketing", False),
                }
            )

        if update_data:
            db.update_user(user_id, **update_data)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ Parent Notes API ============


@app.route("/api/notes", methods=["GET"])
@login_required
def get_notes():
    """获取家长笔记列表."""
    user_id = session.get("user_id")

    try:
        from services.parent_notes import get_latest_notes

        limit = request.args.get("limit", 10, type=int)
        notes = get_latest_notes(user_id, limit)
        return jsonify({"notes": notes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notes", methods=["POST"])
@login_required
def create_note():
    """创建新笔记."""
    user_id = session.get("user_id")
    data = request.json

    try:
        from services.parent_notes import create_note

        note = create_note(
            user_id=user_id,
            topic_id=data.get("topic_id"),
            content=data.get("content"),
            score=data.get("score"),
        )

        return jsonify({"success": True, "note": note})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notes/template/<topic_id>")
@login_required
def get_note_template(topic_id):
    """获取笔记模板."""
    try:
        from services.parent_notes import get_template

        template = get_template(topic_id)
        return jsonify(template)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notes/report")
@login_required
def get_notes_report():
    """获取练习报告."""
    user_id = session.get("user_id")

    try:
        from services.parent_notes import generate_practice_report

        report = generate_practice_report(user_id)
        return jsonify(report or {"message": "No data yet"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
@login_required
def submit_feedback():
    """提交练习反馈."""
    user_id = session.get("user_id")

    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("rating"):
            return jsonify({"error": "Rating is required"}), 400

        # Save feedback (simplified - uses session storage for now)
        feedback_data = {
            "user_id": user_id,
            "topic_id": data.get("topic_id"),
            "rating": data.get("rating"),
            "difficulties": data.get("difficulties", []),
            "comment": data.get("comment", ""),
            "child_feeling": data.get("child_feeling"),
            "submitted_at": datetime.now().isoformat(),
        }

        # Store in session for now (would be database in production)
        if "feedback_history" not in session:
            session["feedback_history"] = []

        session["feedback_history"].insert(0, feedback_data)
        session["feedback_history"] = session["feedback_history"][:100]  # Keep last 100
        session.modified = True

        return jsonify(
            {
                "success": True,
                "message": "Feedback submitted successfully",
                "feedback_id": feedback_data["submitted_at"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback/history")
@login_required
def get_feedback_history():
    """获取反馈历史."""
    user_id = session.get("user_id")

    try:
        history = session.get("feedback_history", [])
        return jsonify({"feedback": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ 练习记录 API ============


@app.route("/api/sessions", methods=["POST"])
@login_required
def record_session():
    """记录练习会话."""
    user_id = session.get("user_id")
    data = request.json

    topic = data.get("topic")
    duration_seconds = data.get("duration_seconds")
    notes = data.get("notes")
    rating = data.get("rating")

    if not topic or not duration_seconds:
        return jsonify({"error": "Topic and duration are required"}), 400

    try:
        from services.parent_notes import record_practice_session

        session = record_practice_session(
            user_id=user_id,
            topic=topic,
            duration_seconds=duration_seconds,
            notes=notes,
            rating=rating,
        )

        return jsonify(
            {"success": True, "session": session, "message": "練習記錄已保存"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions")
@login_required
def get_sessions():
    """获取用户练习记录."""
    user_id = session.get("user_id")

    try:
        from services.parent_notes import get_user_sessions, get_session_stats

        sessions = get_user_sessions(user_id)
        stats = get_session_stats(user_id)

        return jsonify({"success": True, "sessions": sessions, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ 分享功能 API ============


@app.route("/api/share/progress")
@login_required
def share_progress():
    """生成分享链接数据."""
    user_id = session.get("user_id")

    try:
        from services.analytics import get_user_analytics
        from services.progress import get_user_progress
        from services.parent_notes import get_session_stats

        analytics = get_user_analytics(user_id)
        progress = get_user_progress(user_id)
        session_stats = get_session_stats(user_id)

        # 生成分享数据
        child_name = session.get("child_name", "小朋友")
        completed_topics = progress.get("completed", [])
        streak_days = analytics.get("streak_days", 0)

        share_data = {
            "child_name": child_name,
            "topics_completed": len(completed_topics),
            "total_topics": 5,
            "streak_days": streak_days,
            "total_minutes": session_stats.get("total_minutes", 0),
            "message": f"{child_name}已經完成 {len(completed_topics)}/5 個面試主題練習！連續練習 {streak_days} 日！",
            "generated_at": datetime.now().isoformat(),
        }

        return jsonify({"success": True, "share_data": share_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ Achievements API ============


@app.route("/api/achievements")
@login_required
def get_achievements():
    """获取用户成就信息."""
    user_id = session.get("user_id")

    try:
        from services.achievements import get_achievement_summary

        achievements = get_achievement_summary(user_id)
        return jsonify(achievements)
    except Exception as e:
        print(f"Error getting achievements: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/achievements/check", methods=["POST"])
@login_required
def check_achievements():
    """检查并更新用户成就."""
    user_id = session.get("user_id")
    data = request.json or {}
    topic_id = data.get("topic_id")

    try:
        from services.achievements import check_and_award_badges

        newly_earned = check_and_award_badges(user_id, topic_id)

        return jsonify(
            {
                "success": True,
                "new_badges": [
                    {
                        "id": b["id"],
                        "name_zh": b["name_zh"],
                        "icon_emoji": b.get("icon_emoji"),
                    }
                    for b in newly_earned
                ],
            }
        )
    except Exception as e:
        print(f"Error checking achievements: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/progress/summary")
def get_progress_summary():
    """获取学习进度摘要."""
    user_id = session.get("user_id", 0)

    try:
        from services.achievements import get_progress_summary

        progress = get_progress_summary(user_id)
        return jsonify(progress)
    except Exception as e:
        print(f"Error getting progress summary: {e}")
        # Return fallback data
        return jsonify(
            {
                "completed_topics": 1,
                "in_progress_topics": 1,
                "total_minutes": 45,
                "current_streak": 3,
                "completion_percent": 11,
            }
        )


# ============ Learning Reports API ============


@app.route("/api/reports/weekly")
def get_weekly_report():
    """获取本周学习报告."""
    user_id = session.get("user_id", 0)

    try:
        from services.achievements import generate_weekly_report

        report = generate_weekly_report(user_id)
        return jsonify(report)
    except Exception as e:
        print(f"Error generating weekly report: {e}")
        return jsonify(
            {
                "topics_completed": 1,
                "total_practice_time": 45,
                "average_score": 85,
                "streak_days": 3,
                "highlights": ["完成了自我介紹主題", "連續練習 3 天"],
                "suggestions": ["下週目標：完成興趣愛好主題"],
            }
        )


@app.route("/api/reports/monthly")
def get_monthly_report():
    """获取本月学习报告."""
    user_id = session.get("user_id", 0)

    try:
        from services.achievements import generate_monthly_report

        report = generate_monthly_report(user_id)
        return jsonify(report)
    except Exception as e:
        print(f"Error generating monthly report: {e}")
        return jsonify(
            {
                "topics_completed": 2,
                "total_practice_time": 180,
                "average_score": 82,
                "badges_earned": 2,
                "achievements": ["初次嘗試", "連續學習"],
            }
        )


@app.route("/api/reports")
def get_reports():
    """获取用户学习报告列表."""
    user_id = session.get("user_id", 0)
    report_type = request.args.get("type")

    try:
        from services.achievements import get_share_data

        # Return mock data for demo
        return jsonify(
            {
                "reports": [
                    {
                        "id": 1,
                        "report_type": "weekly",
                        "period_start": "2026-02-10",
                        "period_end": "2026-02-16",
                        "topics_completed": 1,
                        "total_practice_time": 45,
                        "average_score": 85,
                        "streak_days": 3,
                        "badges_earned": 0,
                        "generated_at": "2026-02-16T10:00:00",
                    },
                    {
                        "id": 2,
                        "report_type": "weekly",
                        "period_start": "2026-02-03",
                        "period_end": "2026-02-09",
                        "topics_completed": 1,
                        "total_practice_time": 30,
                        "average_score": 80,
                        "streak_days": 2,
                        "badges_earned": 0,
                        "generated_at": "2026-02-09T10:00:00",
                    },
                ]
            }
        )
    except Exception as e:
        print(f"Error getting reports: {e}")
        return jsonify({"reports": []})


@app.route("/api/share/learning-progress")
def share_learning_progress():
    """生成分享到社交媒体的学习进度数据."""
    user_id = session.get("user_id", 0)

    try:
        from services.achievements import get_share_data

        share_data = get_share_data(user_id)

        return jsonify({"success": True, "share_data": share_data})
    except Exception as e:
        print(f"Error generating share data: {e}")
        return jsonify(
            {
                "success": True,
                "share_data": {
                    "total_days": 3,
                    "total_practice": 5,
                    "categories_covered": 1,
                    "total_categories": 9,
                    "message": "堅持每天練習，面試成功在望！",
                },
            }
        )


# ============ New Pages Routes ============


@app.route("/achievements")
@login_required
def achievements_page():
    """成就徽章页面."""
    return render_template("achievements.html")


@app.route("/reports")
def reports_page():
    """学习报告页面."""
    return render_template("reports.html")


# ============ Mock Interview Routes ============


@app.route("/mock-interview")
def mock_interview():
    """AI 模拟面试入口页."""
    return render_template("mock-interview.html")


@app.route("/mock-interview/start")
@login_required
def mock_interview_start():
    """开始模拟面试页面."""
    school_type = request.args.get("school_type", "holistic")
    return render_template("mock-interview-start.html", school_type=school_type)


@app.route("/mock-interview/result")
@login_required
def mock_interview_result():
    """面试结果页面."""
    session_id = request.args.get("session_id")
    return render_template("mock-interview-result.html", session_id=session_id)


# ============ School Advisor Routes ============


@app.route("/school-advisor")
def school_advisor():
    """智能择校顾问入口页."""
    from services.school_advisor_service import get_school_types

    logged_in = "user_id" in session
    school_types = get_school_types()

    return render_template(
        "school-advisor.html", logged_in=logged_in, school_types=school_types
    )


@app.route("/school-advisor/analyze")
@login_required
def school_advisor_analyze():
    """智能择校分析结果页."""
    from services.school_advisor_service import analyze_school_match

    school_type = request.args.get("school_type", "holistic")

    # 获取用户的孩子画像
    user_id = session.get("user_id")

    # 查询孩子的画像数据
    profile_data = {"interests": [], "strengths": [], "personality": ""}

    try:
        from db.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # 尝试从children表获取
        cursor.execute(
            "SELECT interests, strengths, personality FROM children WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()

        if row:
            profile_data["interests"] = (
                row["interests"].split(",") if row["interests"] else []
            )
            profile_data["strengths"] = (
                row["strengths"].split(",") if row["strengths"] else []
            )
            profile_data["personality"] = row["personality"] or ""

        conn.close()
    except Exception as e:
        print(f"Error fetching profile: {e}")

    # 分析匹配度
    result = analyze_school_match(profile_data, school_type)

    return render_template("school-advisor-result.html", result=result)


# ============ Capability Radar Routes ============


@app.route("/capability-radar")
def capability_radar():
    """面试能力分析页面."""
    from services.capability_radar_service import (
        analyze_capabilities,
        get_radar_chart_data,
    )

    logged_in = "user_id" in session
    school_type = request.args.get("school_type", "academic")

    analysis = None
    chart_data = None
    overall_score = 0

    dimension_names = {
        "communication": "沟通表达",
        "logic": "逻辑思维",
        "creativity": "创意思维",
        "confidence": "自信心",
        "eye_contact": "眼神接触",
        "manners": "礼貌礼仪",
    }

    dimension_descriptions = {
        "communication": "清晰表达想法的能力",
        "logic": "思考和解决问题的能力",
        "creativity": "想象力和创新能力",
        "confidence": "自我展示的自信程度",
        "eye_contact": "与他人眼神交流的能力",
        "manners": "基本礼仪和社交礼貌",
    }

    if logged_in:
        user_id = session.get("user_id")

        # 获取孩子画像
        profile_data = {"interests": [], "strengths": [], "personality": ""}

        try:
            from db.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT interests, strengths, personality FROM children WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )
            row = cursor.fetchone()

            if row:
                profile_data["interests"] = (
                    row["interests"].split(",") if row["interests"] else []
                )
                profile_data["strengths"] = (
                    row["strengths"].split(",") if row["strengths"] else []
                )
                profile_data["personality"] = row["personality"] or ""

            conn.close()
        except Exception as e:
            print(f"Error fetching profile: {e}")

        # 分析能力
        analysis = analyze_capabilities(profile_data, None, school_type)
        chart_data = get_radar_chart_data(analysis)
        overall_score = analysis.get("overall_score", 0)

    return render_template(
        "capability-radar.html",
        logged_in=logged_in,
        school_type=school_type,
        analysis=analysis,
        chart_data=chart_data,
        overall_score=overall_score,
        dimension_names=dimension_names,
        dimension_descriptions=dimension_descriptions,
    )


# ============ Question Bank Routes ============


@app.route("/question-bank")
def question_bank():
    """面试真题库主页."""
    from services.question_bank_service import (
        get_all_categories,
        get_question_statistics,
    )

    school_type = request.args.get("school_type", "")
    categories = get_all_categories()
    stats = get_question_statistics()

    selected_categories = []

    return render_template(
        "question-bank.html",
        school_type=school_type,
        categories=categories,
        stats=stats,
        selected_categories=selected_categories,
        questions=None,
    )


@app.route("/question-bank/practice")
def question_bank_practice():
    """真题练习页面."""
    from services.question_bank_service import get_random_questions, get_all_categories

    school_type = request.args.get("school_type", "")
    categories_str = request.args.get("categories", "")
    categories = categories_str.split(",") if categories_str else []
    limit = int(request.args.get("limit", 20))

    all_categories = get_all_categories()

    if categories and len(categories) > 0:
        questions = get_random_questions(
            school_type=school_type if school_type else None,
            categories=categories,
            limit=limit,
        )
    elif school_type:
        questions = get_random_questions(school_type=school_type, limit=limit)
    else:
        questions = get_random_questions(limit=limit)

    stats = {"total": 3000, "by_category": all_categories}

    return render_template(
        "question-bank.html",
        school_type=school_type,
        categories=all_categories,
        stats=stats,
        selected_categories=categories,
        questions=questions,
    )


@app.route("/api/questions/random", methods=["GET"])
def api_questions_random():
    """获取随机题目API."""
    from services.question_bank_service import get_random_questions

    school_type = request.args.get("school_type", "")
    categories_str = request.args.get("categories", "")
    categories = categories_str.split(",") if categories_str else []
    limit = int(request.args.get("limit", 10))

    questions = get_random_questions(
        school_type=school_type if school_type else None,
        categories=categories,
        limit=limit,
    )

    return jsonify({"success": True, "questions": questions})


@app.route("/api/questions/statistics")
def api_questions_statistics():
    """获取题目统计API."""
    from services.question_bank_service import get_question_statistics

    stats = get_question_statistics()

    return jsonify({"success": True, "statistics": stats})


# ============ Practice Center Routes ============
# 练习中心 - 错题本、进度追踪、每日挑战


@app.route("/practice")
def practice_center():
    """练习中心主页"""
    from services.practice_data_service import get_category_progress, get_user_stats

    user_id = session.get("user_id")
    categories = get_category_progress(user_id or 0)
    stats = get_user_stats(user_id or 0)

    return render_template("practice.html", categories=categories, stats=stats)


@app.route("/practice/daily-challenge")
def daily_challenge():
    """每日挑战页面"""
    from services.practice_data_service import get_daily_challenge
    from services.question_bank_service import get_all_categories

    user_id = session.get("user_id")
    challenge = get_daily_challenge(user_id or 0)
    categories = get_all_categories()

    return render_template(
        "question-bank.html",
        school_type="",
        categories=categories,
        stats={"total": 3000, "by_category": categories},
        selected_categories=[],
        questions=challenge["questions"],
    )


@app.route("/practice/wrong-questions")
def wrong_questions():
    """错题本页面"""
    from services.practice_data_service import get_wrong_questions
    from services.question_bank_service import get_all_categories, get_question_by_id

    user_id = session.get("user_id")
    wrong_ids = get_wrong_questions(user_id or 0)

    # 获取错题详情
    wrong_list = []
    for wid in wrong_ids:
        q = get_question_by_id(wid)
        if q:
            wrong_list.append(q)

    categories = get_all_categories()

    return render_template(
        "question-bank.html",
        school_type="",
        categories=categories,
        stats={"total": len(wrong_list), "by_category": categories},
        selected_categories=[],
        questions=wrong_list,
    )


@app.route("/practice/favorites")
def favorites():
    """收藏夹页面"""
    from services.practice_data_service import get_favorites
    from services.question_bank_service import get_all_categories, get_question_by_id

    user_id = session.get("user_id")
    fav_ids = get_favorites(user_id or 0)

    # 获取收藏题详情
    fav_list = []
    for fid in fav_ids:
        q = get_question_by_id(fid)
        if q:
            fav_list.append(q)

    categories = get_all_categories()

    return render_template(
        "question-bank.html",
        school_type="",
        categories=categories,
        stats={"total": len(fav_list), "by_category": categories},
        selected_categories=[],
        questions=fav_list,
    )


@app.route("/practice/recommended")
def recommended():
    """智能推荐页面"""
    from services.practice_data_service import get_recommended_questions
    from services.question_bank_service import get_all_categories

    user_id = session.get("user_id")
    questions = get_recommended_questions(user_id or 0, limit=20)
    categories = get_all_categories()

    return render_template(
        "question-bank.html",
        school_type="",
        categories=categories,
        stats={"total": 3000, "by_category": categories},
        selected_categories=[],
        questions=questions,
    )


@app.route("/practice/progress")
def progress_detail():
    """练习进度详情页"""
    from services.practice_data_service import get_category_progress, get_user_stats

    user_id = session.get("user_id")
    categories = get_category_progress(user_id or 0)
    stats = get_user_stats(user_id or 0)

    return render_template("practice.html", categories=categories, stats=stats)


# ============ Practice API Endpoints ============


@app.route("/api/practice/record", methods=["POST"])
@login_required
def api_record_practice():
    """记录练习结果API"""
    from services.practice_data_service import record_practice

    data = request.json or {}
    user_id = session.get("user_id")
    question_id = data.get("question_id")
    is_correct = data.get("is_correct", True)

    result = record_practice(user_id, question_id, is_correct)

    return jsonify({"success": result})


@app.route("/api/practice/favorite", methods=["POST"])
@login_required
def api_add_favorite():
    """添加收藏API"""
    from services.practice_data_service import add_favorite

    data = request.json or {}
    user_id = session.get("user_id")
    question_id = data.get("question_id")

    result = add_favorite(user_id, question_id)

    return jsonify({"success": result})


@app.route("/api/practice/wrong", methods=["POST"])
@login_required
def api_mark_wrong():
    """标记错题API"""
    from services.practice_data_service import mark_wrong

    data = request.json or {}
    user_id = session.get("user_id")
    question_id = data.get("question_id")

    result = mark_wrong(user_id, question_id)

    return jsonify({"success": result})


# ============ Interview Guide Routes ============


@app.route("/interview-guide")
def interview_guide():
    """面试指南页面"""
    from services.interview_guide_service import (
        get_etiquette_guide,
        get_all_school_strategies,
        get_parent_guide,
    )

    etiquette = get_etiquette_guide()
    school_strategies = get_all_school_strategies()
    parent_guide = get_parent_guide()

    return render_template(
        "interview-guide.html",
        etiquette=etiquette,
        school_strategies=school_strategies,
        parent_guide=parent_guide,
    )


# ============ Mock Interview API ============


@app.route("/api/mock-interview/start", methods=["POST"])
@login_required
def api_mock_interview_start():
    """开始模拟面试，生成问题."""
    data = request.json or {}
    school_type = data.get("school_type", "holistic")
    num_questions = data.get("num_questions", 5)
    interviewer_style = data.get("interviewer_style", "friendly")
    stage_fright_level = data.get("stage_fright_level", 1)

    user_id = session.get("user_id")

    # Get profile from session
    profile = {
        "child_name": session.get("child_name", "小朋友"),
        "child_age": session.get("child_age", "5岁"),
        "child_gender": session.get("child_gender", "不透露"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    try:
        from services.mock_interview_service import (
            generate_mock_interview_questions,
            save_interview_session,
            SCHOOL_TYPES,
            INTERVIEWER_STYLES,
            STAGE_FRIGHT_LEVELS,
        )

        # Generate questions
        questions = generate_mock_interview_questions(
            profile, school_type, num_questions
        )

        # Get interviewer style and stage fright config
        style_config = INTERVIEWER_STYLES.get(
            interviewer_style, INTERVIEWER_STYLES["friendly"]
        )
        fright_config = STAGE_FRIGHT_LEVELS.get(
            stage_fright_level, STAGE_FRIGHT_LEVELS[1]
        )

        # Save session
        session_data = {
            "school_type": school_type,
            "school_type_name": SCHOOL_TYPES.get(school_type, {}).get(
                "name", "模拟面试"
            ),
            "interviewer_style": interviewer_style,
            "interviewer_style_name": style_config.get("name", "亲和型"),
            "stage_fright_level": stage_fright_level,
            "stage_fright_name": fright_config.get("name", "初阶"),
            "questions": questions,
            "answers": [],
            "user_id": user_id,
        }

        session_id = save_interview_session(user_id, session_data)

        return jsonify(
            {
                "success": True,
                "session_id": session_id,
                "questions": questions,
                "interviewer_style": interviewer_style,
                "stage_fright_level": stage_fright_level,
            }
        )

    except Exception as e:
        print(f"Error starting mock interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/audio", methods=["POST"])
@login_required
def api_mock_interview_audio():
    """生成面试问题语音."""
    data = request.json or {}
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        from services.mock_interview_service import generate_question_audio

        audio_url = generate_question_audio(text)

        return jsonify({"success": True, "audio_url": audio_url})

    except Exception as e:
        print(f"Error generating audio: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/followup", methods=["POST"])
@login_required
def api_mock_interview_followup():
    """生成追问问题."""
    data = request.json or {}
    session_id = data.get("session_id")
    question = data.get("question", "")
    answer = data.get("answer", "")

    user_id = session.get("user_id")

    # Get profile from session
    profile = {
        "child_name": session.get("child_name", "小朋友"),
        "child_age": session.get("child_age", "5岁"),
    }

    try:
        from services.mock_interview_service import generate_ai_follow_up

        follow_up = generate_ai_follow_up(question, answer, profile)

        return jsonify({"success": True, "follow_up": follow_up})

    except Exception as e:
        print(f"Error generating follow-up: {e}")
        # Return default follow-up on error
        return jsonify({"success": True, "follow_up": "可以话多啲俾老师知吗？"})


@app.route("/api/mock-interview/finish", methods=["POST"])
@login_required
def api_mock_interview_finish():
    """完成面试，生成评估报告."""
    data = request.json or {}
    session_id = data.get("session_id")
    answers = data.get("answers", [])
    school_type = data.get("school_type", "holistic")

    user_id = session.get("user_id")

    # Get profile from session
    profile = {
        "child_name": session.get("child_name", "小朋友"),
        "child_age": session.get("child_age", "5岁"),
    }

    try:
        from services.mock_interview_service import (
            get_interview_session,
            evaluate_answer,
            save_interview_session,
            SCHOOL_TYPES,
        )

        # Get session
        session_data = get_interview_session(user_id, session_id)

        if not session_data:
            return jsonify({"error": "Session not found"}), 404

        # Evaluate each answer
        evaluations = []
        total_score = 0

        for answer_data in answers:
            question = answer_data.get("question", "")
            answer = answer_data.get("answer", "")

            evaluation = evaluate_answer(question, answer, profile, school_type)
            evaluations.append(
                {"question": question, "answer": answer, "evaluation": evaluation}
            )
            total_score += evaluation.get("score", 0)

        # Calculate average score
        avg_score = total_score // len(evaluations) if evaluations else 0

        # Update session with answers and score
        session_data["answers"] = answers
        session_data["evaluations"] = evaluations
        session_data["score"] = avg_score
        session_data["school_type"] = school_type
        session_data["school_type_name"] = SCHOOL_TYPES.get(school_type, {}).get(
            "name", "模拟面试"
        )

        save_interview_session(user_id, session_data)

        return jsonify(
            {
                "success": True,
                "session_id": session_id,
                "score": avg_score,
                "evaluations": evaluations,
            }
        )

    except Exception as e:
        print(f"Error finishing interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/history", methods=["GET"])
@login_required
def api_mock_interview_history():
    """获取面试历史记录."""
    user_id = session.get("user_id")

    try:
        from services.mock_interview_service import get_interview_sessions

        sessions = get_interview_sessions(user_id, 10)

        # Convert to simple format
        history = []
        for session in sessions:
            history.append(
                {
                    "session_id": session.get("session_id"),
                    "school_type_name": session.get("school_type_name", "模拟面试"),
                    "score": session.get("score", 0),
                    "created_at": session.get("created_at", ""),
                }
            )

        return jsonify({"success": True, "sessions": history})

    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/<session_id>", methods=["GET"])
@login_required
def api_mock_interview_detail(session_id):
    """获取特定面试会话详情."""
    user_id = session.get("user_id")

    try:
        from services.mock_interview_service import get_interview_session

        session_data = get_interview_session(user_id, session_id)

        if not session_data:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({"success": True, "session": session_data})

    except Exception as e:
        print(f"Error getting session: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/mock-interview/voice")
@login_required
def mock_interview_voice():
    """AI 语音面试入口页面."""
    school_type = request.args.get("school_type", "holistic")
    return render_template("mock-interview-voice.html", school_type=school_type)


# ============ Voice Interview API ============


@app.route("/api/mock-interview/voice/start", methods=["POST"])
@login_required
def api_voice_interview_start():
    """开始语音面试，生成问题."""
    data = request.json or {}
    school_type = data.get("school_type", "holistic")
    num_questions = data.get("num_questions", 5)
    interviewer_style = data.get("interviewer_style", "friendly")
    stage_fright_level = data.get("stage_fright_level", 1)

    user_id = session.get("user_id")

    # Get profile from session
    profile = {
        "child_name": session.get("child_name", "小朋友"),
        "child_age": session.get("child_age", "5岁"),
        "child_gender": session.get("child_gender", "不透露"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    try:
        from services.voice_interview_service import create_voice_session

        session_data = create_voice_session(
            user_id, school_type, profile, num_questions
        )

        # Store interviewer style and stage fright level in session
        session_data["interviewer_style"] = interviewer_style
        session_data["stage_fright_level"] = stage_fright_level

        return jsonify(
            {
                "success": True,
                "session_id": session_data["session_id"],
                "questions": session_data["questions"],
                "interviewer_style": interviewer_style,
                "stage_fright_level": stage_fright_level,
            }
        )

    except Exception as e:
        print(f"Error starting voice interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/voice/recognize", methods=["POST"])
@login_required
def api_voice_recognize():
    """语音识别 - 处理录音并识别文字."""
    session_id = request.form.get("session_id")

    if "audio" not in request.files:
        # 尝试从 JSON 获取 base64 音频
        data = request.json or {}
        if "audio_data" in data:
            import base64

            audio_data = base64.b64decode(data["audio_data"])
        else:
            return jsonify({"error": "No audio file", "fallback": True}), 400
    else:
        audio_file = request.files["audio"]
        audio_data = audio_file.read()

    if not audio_data:
        return jsonify({"error": "Empty audio data", "fallback": True}), 400

    try:
        from services.voice_interview_service import recognize_speech

        result = recognize_speech(audio_data)

        return jsonify(
            {
                "success": result["success"],
                "text": result.get("text", ""),
                "fallback": result.get("fallback", False),
            }
        )

    except Exception as e:
        print(f"Error recognizing speech: {e}")
        return jsonify({"error": str(e), "fallback": True}), 500


@app.route("/api/mock-interview/voice/followup", methods=["POST"])
@login_required
def api_voice_followup():
    """生成语音面试的追问问题."""
    data = request.json or {}
    session_id = data.get("session_id")
    question = data.get("question", "")
    answer = data.get("answer", "")

    user_id = session.get("user_id")

    # Get profile
    profile = {
        "child_name": session.get("child_name", "小朋友"),
        "child_age": session.get("child_age", "5岁"),
    }

    try:
        from services.voice_interview_service import generate_voice_follow_up

        result = generate_voice_follow_up(question, answer, profile)

        return jsonify(
            {
                "success": True,
                "follow_up": result.get("follow_up", ""),
                "needs_follow_up": result.get("needs_follow_up", False),
            }
        )

    except Exception as e:
        print(f"Error generating follow-up: {e}")
        # Return default follow-up on error
        return jsonify(
            {
                "success": True,
                "follow_up": "可以话多啲俾老师知吗？",
                "needs_follow_up": True,
            }
        )


@app.route("/api/mock-interview/voice/tts", methods=["POST"])
@login_required
def api_voice_tts():
    """生成语音面试的 TTS 音频."""
    data = request.json or {}
    text = data.get("text", "")
    session_id = data.get("session_id")
    language = data.get("language", "cantonese")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        from services.voice_interview_service import generate_voice_audio

        result = generate_voice_audio(text, language=language)

        return jsonify(
            {
                "success": True,
                "audio_url": result.get("audio_url"),
                "audio_data": result.get("audio_data"),
            }
        )

    except Exception as e:
        print(f"Error generating TTS: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/voice/answer", methods=["POST"])
@login_required
def api_voice_answer():
    """保存语音面试的回答."""
    data = request.json or {}
    session_id = data.get("session_id")
    question = data.get("question", "")
    answer = data.get("answer", "")
    follow_up_question = data.get("follow_up_question")
    follow_up_answer = data.get("follow_up_answer")

    user_id = session.get("user_id")

    try:
        from services.voice_interview_service import (
            save_voice_answer,
            get_voice_session,
        )

        session = get_voice_session(user_id, session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Save answer
        answer_data = {
            "question": question,
            "answer": answer,
            "answer_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save follow-up if exists
        if follow_up_question and follow_up_answer:
            answer_data["follow_up"] = follow_up_question
            answer_data["follow_up_answer"] = follow_up_answer

        save_voice_answer(user_id, session_id, answer_data)

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error saving answer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/voice/next", methods=["POST"])
@login_required
def api_voice_next():
    """进入语音面试的下一题."""
    data = request.json or {}
    session_id = data.get("session_id")

    user_id = session.get("user_id")

    try:
        from services.voice_interview_service import get_voice_session

        session = get_voice_session(user_id, session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get current question index
        current_index = session.get("current_question_index", 0)
        questions = session.get("questions", [])

        # Check if there are more questions
        if current_index >= len(questions) - 1:
            return jsonify({"success": True, "has_next": False})

        # Move to next question
        session["current_question_index"] = current_index + 1

        return jsonify(
            {
                "success": True,
                "has_next": True,
                "next_question": questions[current_index + 1],
            }
        )

    except Exception as e:
        print(f"Error going to next question: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/voice/finish", methods=["POST"])
@login_required
def api_voice_finish():
    """完成语音面试，生成评估报告."""
    data = request.json or {}
    session_id = data.get("session_id")

    user_id = session.get("user_id")

    try:
        from services.voice_interview_service import (
            complete_voice_session,
            generate_voice_report,
        )

        # Complete session
        session = complete_voice_session(user_id, session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Generate report
        report = generate_voice_report(user_id, session_id)
        if not report:
            return jsonify({"error": "Failed to generate report"}), 500

        # Get score message
        score = report.get("score", 0)
        if score >= 90:
            message = "劲劲劲！你叻晒！"
        elif score >= 80:
            message = "表现好好！继续努力！"
        elif score >= 70:
            message = "几好呀，继续加油！"
        elif score >= 60:
            message = "既嘢讲得不错，继续练习！"
        else:
            message = "再接再厉！"

        return jsonify(
            {
                "success": True,
                "session_id": session_id,
                "score": score,
                "message": message,
                "report": report,
            }
        )

    except Exception as e:
        print(f"Error finishing voice interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/mock-interview/voice/history", methods=["GET"])
@login_required
def api_voice_history():
    """获取语音面试历史记录."""
    user_id = session.get("user_id")

    try:
        from services.voice_interview_service import get_voice_interview_history

        history = get_voice_interview_history(user_id, 10)

        return jsonify({"success": True, "sessions": history})

    except Exception as e:
        print(f"Error getting voice history: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Learning Path Routes ============


@app.route("/learning-path")
def learning_path_page():
    """智能学习路径规划页面"""
    from services.learning_path_service import get_school_type_info, get_all_phases

    logged_in = "user_id" in session
    user_id = session.get("user_id")

    # 获取可用的学校类型
    school_types = []
    from services.mock_interview_service import SCHOOL_TYPES

    for st_id, st_info in SCHOOL_TYPES.items():
        school_types.append(
            {
                "id": st_id,
                "name": st_info.get("name", ""),
                "name_en": st_info.get("name_en", ""),
                "description": st_info.get("description", ""),
            }
        )

    # 获取阶段信息
    phases = get_all_phases()

    # 如果已登录，获取学习路径数据
    path_data = None
    progress_data = None

    if logged_in and user_id:
        try:
            from services.learning_path_service import (
                get_learning_path,
                get_progress_data,
            )

            path_data = get_learning_path(user_id)
            progress_data = get_progress_data(user_id)
        except Exception as e:
            print(f"Error loading learning path: {e}")

    return render_template(
        "learning-path.html",
        logged_in=logged_in,
        school_types=school_types,
        phases=phases,
        path_data=path_data,
        progress_data=progress_data,
    )


# ============ Learning Path API Endpoints ============


@app.route("/api/learning-path/diagnostic-test", methods=["POST"])
@login_required
def api_diagnostic_test():
    """生成入门测试题目"""
    user_id = session.get("user_id")
    data = request.json or {}
    school_type = data.get("school_type", "academic")

    try:
        from services.learning_path_service import generate_diagnostic_test

        result = generate_diagnostic_test(user_id, school_type)

        return jsonify({"success": True, "test": result})
    except Exception as e:
        print(f"Error generating diagnostic test: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/assessment", methods=["POST"])
@login_required
def api_assessment():
    """能力评估"""
    user_id = session.get("user_id")
    data = request.json or {}
    answers = data.get("answers", [])

    # 获取用户画像数据
    profile_data = {
        "interests": session.get("child_interests", []),
        "strengths": [],
        "personality": "",
    }

    try:
        from services.learning_path_service import assess_capabilities

        result = assess_capabilities(user_id, answers, profile_data)

        return jsonify({"success": True, "assessment": result})
    except Exception as e:
        print(f"Error in assessment: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/generate", methods=["POST"])
@login_required
def api_generate_path():
    """生成学习路径"""
    user_id = session.get("user_id")
    data = request.json or {}
    school_type = data.get("school_type", "academic")
    capabilities = data.get("capabilities", {})

    # 如果没有提供能力数据，从画像中获取
    if not capabilities:
        try:
            from services.capability_radar_service import analyze_capabilities

            profile_data = {
                "interests": session.get("child_interests", []),
                "strengths": [],
                "personality": "",
            }
            analysis = analyze_capabilities(profile_data, None, school_type)
            capabilities = analysis.get("capabilities", {})
        except Exception as e:
            print(f"Error getting capabilities: {e}")
            # 使用默认能力值
            capabilities = {
                "communication": 50,
                "logic": 50,
                "creativity": 50,
                "confidence": 50,
                "eye_contact": 50,
                "manners": 50,
            }

    try:
        from services.learning_path_service import generate_learning_path

        path = generate_learning_path(user_id, school_type, capabilities)

        return jsonify({"success": True, "path": path})
    except Exception as e:
        print(f"Error generating path: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/map", methods=["GET"])
@login_required
def api_learning_map():
    """获取学习地图"""
    user_id = session.get("user_id")

    try:
        from services.learning_path_service import get_learning_map

        map_data = get_learning_map(user_id)

        if not map_data:
            return jsonify(
                {"success": False, "message": "尚未生成学习路径，请先进行能力诊断"}
            ), 404

        return jsonify({"success": True, "map": map_data})
    except Exception as e:
        print(f"Error getting learning map: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/progress", methods=["GET"])
@login_required
def api_learning_progress():
    """获取进度数据"""
    user_id = session.get("user_id")

    try:
        from services.learning_path_service import get_progress_data

        progress = get_progress_data(user_id)

        return jsonify({"success": True, "progress": progress})
    except Exception as e:
        print(f"Error getting progress: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/optimize", methods=["POST"])
@login_required
def api_optimize_path():
    """优化学习路径"""
    user_id = session.get("user_id")
    data = request.json or {}

    # 提取练习数据
    practice_data = {
        "strong_skills": data.get("strong_skills", []),
        "weak_skills": data.get("weak_skills", []),
    }

    try:
        from services.learning_path_service import optimize_path

        optimized_path = optimize_path(user_id, practice_data)

        if not optimized_path:
            return jsonify({"success": False, "message": "尚未生成学习路径"}), 404

        return jsonify({"success": True, "path": optimized_path})
    except Exception as e:
        print(f"Error optimizing path: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/milestone", methods=["POST"])
@login_required
def api_update_milestone():
    """更新里程碑进度"""
    user_id = session.get("user_id")
    data = request.json or {}

    milestone_id = data.get("milestone_id")
    status = data.get("status", "completed")

    if not milestone_id:
        return jsonify({"error": "milestone_id is required"}), 400

    try:
        from services.learning_path_service import update_milestone_progress

        result = update_milestone_progress(user_id, milestone_id, status)

        if not result:
            return jsonify(
                {"success": False, "message": "更新失败，学习路径不存在"}
            ), 404

        return jsonify({"success": True, "message": "里程碑进度已更新"})
    except Exception as e:
        print(f"Error updating milestone: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/learning-path/reset", methods=["POST"])
@login_required
def api_reset_path():
    """重置学习路径"""
    user_id = session.get("user_id")

    try:
        from services.learning_path_service import reset_learning_path

        reset_learning_path(user_id)

        return jsonify({"success": True, "message": "学习路径已重置"})
    except Exception as e:
        print(f"Error resetting path: {e}")
        return jsonify({"error": str(e)}), 500


# ============ 家长协作空间与社群路由 ============


@app.route("/parent-community")
@login_required
def parent_community():
    """家长协作空间主页"""
    return render_template("parent-community.html", active_page="community")


# 问答社区 API
@app.route("/api/community/questions")
@login_required
def api_questions():
    """获取问题列表"""
    from services.parent_community_service import get_questions

    category = request.args.get("category")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    keyword = request.args.get("keyword")

    try:
        result = get_questions(
            category=category, page=page, limit=limit, keyword=keyword
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error getting questions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/questions", methods=["POST"])
@login_required
def api_create_question():
    """创建问题"""
    from services.parent_community_service import create_question

    user_id = session.get("user_id")
    data = request.get_json()

    category = data.get("category")
    title = data.get("title")
    content = data.get("content")
    is_anonymous = data.get("is_anonymous", False)

    if not category or not title or not content:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        question_id = create_question(user_id, category, title, content, is_anonymous)
        return jsonify({"id": question_id, "message": "问题发布成功"})
    except Exception as e:
        print(f"Error creating question: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/questions/<int:question_id>")
@login_required
def api_question_detail(question_id):
    """获取问题详情"""
    from services.parent_community_service import get_question_by_id

    try:
        question = get_question_by_id(question_id)
        if not question:
            return jsonify({"error": "问题不存在"}), 404
        return jsonify(question)
    except Exception as e:
        print(f"Error getting question: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/questions/<int:question_id>/answers", methods=["POST"])
@login_required
def api_create_answer(question_id):
    """回答问题"""
    from services.parent_community_service import create_answer

    user_id = session.get("user_id")
    data = request.get_json()

    content = data.get("content")
    is_anonymous = data.get("is_anonymous", False)

    if not content:
        return jsonify({"error": "回答内容不能为空"}), 400

    try:
        answer_id = create_answer(question_id, user_id, content, is_anonymous)
        return jsonify({"id": answer_id, "message": "回答发布成功"})
    except Exception as e:
        print(f"Error creating answer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/answers/<int:answer_id>/like", methods=["POST"])
@login_required
def api_like_answer(answer_id):
    """点赞回答"""
    from services.parent_community_service import like_answer

    user_id = session.get("user_id")

    try:
        result = like_answer(answer_id, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error liking answer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/questions/<int:question_id>/best-answer", methods=["POST"])
@login_required
def api_set_best_answer(question_id):
    """设为最佳回答"""
    from services.parent_community_service import set_best_answer

    user_id = session.get("user_id")
    data = request.get_json()
    answer_id = data.get("answer_id")

    if not answer_id:
        return jsonify({"error": "缺少回答ID"}), 400

    try:
        result = set_best_answer(question_id, user_id, answer_id)
        if not result:
            return jsonify({"error": "无权操作"}), 403
        return jsonify(result)
    except Exception as e:
        print(f"Error setting best answer: {e}")
        return jsonify({"error": str(e)}), 500


# 经验分享 API
@app.route("/api/community/experiences")
@login_required
def api_experiences():
    """获取经验文章列表"""
    from services.parent_community_service import get_posts

    tag = request.args.get("tag")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    keyword = request.args.get("keyword")

    try:
        result = get_posts(tag=tag, page=page, limit=limit, keyword=keyword)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting posts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/experiences", methods=["POST"])
@login_required
def api_create_experience():
    """发布经验文章"""
    from services.parent_community_service import create_post

    user_id = session.get("user_id")
    data = request.get_json()

    title = data.get("title")
    content = data.get("content")
    cover_image = data.get("cover_image")
    tags = data.get("tags", [])

    if not title or not content:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        post_id = create_post(user_id, title, content, cover_image, tags)
        return jsonify({"id": post_id, "message": "文章发布成功"})
    except Exception as e:
        print(f"Error creating post: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/experiences/<int:post_id>")
@login_required
def api_experience_detail(post_id):
    """获取经验文章详情"""
    from services.parent_community_service import get_post_by_id

    user_id = session.get("user_id")

    try:
        post = get_post_by_id(post_id, user_id)
        if not post:
            return jsonify({"error": "文章不存在"}), 404
        return jsonify(post)
    except Exception as e:
        print(f"Error getting post: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/experiences/<int:post_id>/like", methods=["POST"])
@login_required
def api_like_experience(post_id):
    """点赞经验文章"""
    from services.parent_community_service import like_post

    user_id = session.get("user_id")

    try:
        result = like_post(post_id, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error liking post: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/experiences/<int:post_id>/favorite", methods=["POST"])
@login_required
def api_favorite_experience(post_id):
    """收藏经验文章"""
    from services.parent_community_service import favorite_post

    user_id = session.get("user_id")

    try:
        result = favorite_post(post_id, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error favoriting post: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/experiences/<int:post_id>/comments", methods=["POST"])
@login_required
def api_create_comment(post_id):
    """评论经验文章"""
    from services.parent_community_service import create_post_comment

    user_id = session.get("user_id")
    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"error": "评论内容不能为空"}), 400

    try:
        comment_id = create_post_comment(post_id, user_id, content)
        return jsonify({"id": comment_id, "message": "评论发布成功"})
    except Exception as e:
        print(f"Error creating comment: {e}")
        return jsonify({"error": str(e)}), 500


# 面试案例 API
@app.route("/api/community/cases")
@login_required
def api_cases():
    """获取面试案例列表"""
    from services.parent_community_service import get_cases

    school_type = request.args.get("school_type")
    school_name = request.args.get("school_name")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    try:
        result = get_cases(
            school_type=school_type, school_name=school_name, page=page, limit=limit
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error getting cases: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/cases", methods=["POST"])
@login_required
def api_create_case():
    """提交面试案例"""
    from services.parent_community_service import create_case

    user_id = session.get("user_id")
    data = request.get_json()

    school_name = data.get("school_name")
    school_type = data.get("school_type")
    interview_date = data.get("interview_date")
    questions = data.get("questions")
    key_points = data.get("key_points")
    overall_rating = data.get("overall_rating")
    review_content = data.get("review_content")
    is_anonymous = data.get("is_anonymous", True)

    if (
        not school_name
        or not school_type
        or not interview_date
        or not questions
        or not review_content
    ):
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        case_id = create_case(
            user_id,
            school_name,
            school_type,
            interview_date,
            questions,
            key_points,
            overall_rating,
            review_content,
            is_anonymous,
        )
        return jsonify({"id": case_id, "message": "案例提交成功，待审核后发布"})
    except Exception as e:
        print(f"Error creating case: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/cases/<int:case_id>")
@login_required
def api_case_detail(case_id):
    """获取案例详情"""
    from services.parent_community_service import get_case_by_id

    user_id = session.get("user_id")

    try:
        case = get_case_by_id(case_id, user_id)
        if not case:
            return jsonify({"error": "案例不存在"}), 404
        return jsonify(case)
    except Exception as e:
        print(f"Error getting case: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/cases/<int:case_id>/helpful", methods=["POST"])
@login_required
def api_case_helpful(case_id):
    """标记案例有帮助"""
    from services.parent_community_service import mark_case_helpful

    user_id = session.get("user_id")

    try:
        result = mark_case_helpful(case_id, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error marking case helpful: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/cases/<int:case_id>/favorite", methods=["POST"])
@login_required
def api_favorite_case(case_id):
    """收藏案例"""
    from services.parent_community_service import favorite_case

    user_id = session.get("user_id")

    try:
        result = favorite_case(case_id, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error favoriting case: {e}")
        return jsonify({"error": str(e)}), 500


# 学习目标 API
@app.route("/api/community/goals")
@login_required
def api_goals():
    """获取学习目标列表"""
    from services.parent_community_service import get_goals

    user_id = session.get("user_id")
    child_profile_id = request.args.get("child_id")
    status = request.args.get("status")

    try:
        result = get_goals(user_id, child_profile_id, status)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting goals: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/goals", methods=["POST"])
@login_required
def api_create_goal():
    """创建学习目标"""
    from services.parent_community_service import create_goal

    user_id = session.get("user_id")
    data = request.get_json()

    child_profile_id = data.get("child_id")
    title = data.get("title")
    goal_type = data.get("goal_type")
    target_value = data.get("target_value")
    period = data.get("period")
    deadline = data.get("deadline")

    if (
        not child_profile_id
        or not title
        or not goal_type
        or not target_value
        or not period
    ):
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        goal_id = create_goal(
            user_id, child_profile_id, title, goal_type, target_value, period, deadline
        )
        return jsonify({"id": goal_id, "message": "目标创建成功"})
    except Exception as e:
        print(f"Error creating goal: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/goals/<int:goal_id>/progress", methods=["POST"])
@login_required
def api_update_goal_progress(goal_id):
    """更新目标进度"""
    from services.parent_community_service import update_goal_progress

    user_id = session.get("user_id")
    data = request.get_json()
    value = data.get("value", 1)

    try:
        result = update_goal_progress(goal_id, user_id, value)
        if not result:
            return jsonify({"error": "目标不存在"}), 404
        return jsonify(result)
    except Exception as e:
        print(f"Error updating goal progress: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/goals/<int:goal_id>", methods=["DELETE"])
@login_required
def api_delete_goal(goal_id):
    """删除学习目标"""
    from services.parent_community_service import delete_goal

    user_id = session.get("user_id")

    try:
        result = delete_goal(goal_id, user_id)
        if not result:
            return jsonify({"error": "目标不存在"}), 404
        return jsonify({"message": "目标删除成功"})
    except Exception as e:
        print(f"Error deleting goal: {e}")
        return jsonify({"error": str(e)}), 500


# 鼓励留言 API
@app.route("/api/community/encouragement-messages")
@login_required
def api_encouragement_messages():
    """获取鼓励留言"""
    from services.parent_community_service import get_encouragement_messages

    user_id = session.get("user_id")
    child_profile_id = request.args.get("child_id")

    if not child_profile_id:
        return jsonify({"error": "缺少孩子ID"}), 400

    try:
        messages = get_encouragement_messages(user_id, int(child_profile_id))
        return jsonify({"messages": messages})
    except Exception as e:
        print(f"Error getting messages: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/community/encouragement-messages", methods=["POST"])
@login_required
def api_create_encouragement_message():
    """发送鼓励留言"""
    from services.parent_community_service import create_encouragement_message

    user_id = session.get("user_id")
    data = request.get_json()

    child_profile_id = data.get("child_id")
    message = data.get("message")

    if not child_profile_id or not message:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        message_id = create_encouragement_message(user_id, child_profile_id, message)
        return jsonify({"id": message_id, "message": "留言发送成功"})
    except Exception as e:
        print(f"Error creating message: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Parent Interview Routes ============


@app.route("/parent-interview")
def parent_interview_page():
    """家长面试首页/题库页面"""
    from services.parent_interview_service import (
        get_question_categories,
        get_school_types,
    )

    logged_in = "user_id" in session
    user_id = session.get("user_id")

    # 获取题库分类
    categories = get_question_categories()

    # 获取学校类型
    school_types = get_school_types()

    return render_template(
        "parent-interview.html",
        logged_in=logged_in,
        categories=categories,
        school_types=school_types,
    )


@app.route("/parent-interview/voice")
def parent_interview_voice_page():
    """家长语音模拟面试页面"""
    school_type = request.args.get("school_type", "academic")

    return render_template("parent-interview-voice.html", school_type=school_type)


@app.route("/parent-interview/result")
def parent_interview_result_page():
    """家长面试报告页面"""
    session_id = request.args.get("session_id", "")

    return render_template("parent-interview-result.html", session_id=session_id)


@app.route("/parent-interview/history")
def parent_interview_history_page():
    """家长面试历史记录页面"""
    logged_in = "user_id" in session

    return render_template("parent-interview-history.html", logged_in=logged_in)


# ============ Parent Interview API Endpoints ============


@app.route("/api/parent-interview/questions", methods=["GET"])
def api_parent_interview_questions():
    """获取家长面试题库"""
    category = request.args.get("category")
    limit = int(request.args.get("limit", 10))

    try:
        from services.parent_interview_service import (
            get_question_categories,
            get_questions_by_category,
        )

        if category:
            questions = get_questions_by_category(category, limit)
            return jsonify({"success": True, "questions": questions})
        else:
            categories = get_question_categories()
            return jsonify({"success": True, "categories": categories})

    except Exception as e:
        print(f"Error getting questions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/voice/start", methods=["POST"])
def api_parent_interview_voice_start():
    """启动家长语音面试"""
    data = request.json or {}
    school_type = data.get("school_type", "academic")
    num_questions = int(data.get("num_questions", 5))

    try:
        from services.parent_interview_service import parent_interview_session

        # 创建会话
        session = parent_interview_session.create_session(
            user_id="anonymous", school_type=school_type, num_questions=num_questions
        )

        return jsonify(
            {
                "success": True,
                "session_id": session["session_id"],
                "questions": session["questions"],
                "school_type": school_type,
            }
        )

    except Exception as e:
        print(f"Error starting interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/voice/next", methods=["POST"])
def api_parent_interview_voice_next():
    """获取下一道面试问题"""
    data = request.json or {}
    session_id = data.get("session_id")

    try:
        from services.parent_interview_service import parent_interview_session

        session = parent_interview_session.get_session(session_id)
        if not session:
            return jsonify({"error": "会话不存在"}), 404

        current_index = session.get("current_index", 0)
        questions = session.get("questions", [])

        if current_index < len(questions):
            question = questions[current_index]
            return jsonify(
                {
                    "success": True,
                    "question": question,
                    "current_index": current_index,
                    "total": len(questions),
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "finished": True,
                    "current_index": current_index,
                    "total": len(questions),
                }
            )

    except Exception as e:
        print(f"Error getting next question: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/voice/answer", methods=["POST"])
def api_parent_interview_voice_answer():
    """提交回答"""
    data = request.json or {}
    session_id = data.get("session_id")
    question = data.get("question")
    answer = data.get("answer")
    follow_up_question = data.get("follow_up_question")
    follow_up_answer = data.get("follow_up_answer")

    if not session_id or not question or not answer:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        from services.parent_interview_service import parent_interview_session

        session = parent_interview_session.get_session(session_id)
        if not session:
            return jsonify({"error": "会话不存在"}), 404

        # 添加回答
        answer_data = parent_interview_session.add_answer(
            session_id, question, answer, follow_up_question, follow_up_answer
        )

        return jsonify({"success": True, "answer": answer_data})

    except Exception as e:
        print(f"Error saving answer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/voice/followup", methods=["POST"])
def api_parent_interview_voice_followup():
    """生成追问问题"""
    data = request.json or {}
    base_question = data.get("question")
    previous_answer = data.get("answer")

    if not base_question or not previous_answer:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        from services.parent_interview_service import generate_follow_up_question

        follow_up = generate_follow_up_question(base_question, previous_answer)

        return jsonify({"success": True, "follow_up": follow_up})

    except Exception as e:
        print(f"Error generating follow-up: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/voice/finish", methods=["POST"])
def api_parent_interview_voice_finish():
    """完成面试"""
    data = request.json or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "缺少会话ID"}), 400

    try:
        from services.parent_interview_service import (
            parent_interview_session,
            generate_interview_report,
        )

        session = parent_interview_session.finish_session(session_id)
        if not session:
            return jsonify({"error": "会话不存在"}), 404

        # 生成报告
        report = generate_interview_report(session_id)

        # 生成消息
        score = report.get("total_score", 0)
        if score >= 85:
            message = "表现非常出色！您的教育理念和育儿经验都很棒。"
        elif score >= 70:
            message = "回答不错！建议可以更具体一些会更好。"
        elif score >= 50:
            message = "回答还行，建议多举例说明您的观点。"
        else:
            message = "建议更详细地表达您的想法和做法。"

        return jsonify(
            {
                "success": True,
                "score": score,
                "message": message,
                "session_id": session_id,
            }
        )

    except Exception as e:
        print(f"Error finishing interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/feedback", methods=["POST"])
def api_parent_interview_feedback():
    """获取面试反馈"""
    data = request.json or {}
    question = data.get("question")
    answer = data.get("answer")
    school_type = data.get("school_type", "academic")

    if not question or not answer:
        return jsonify({"error": "缺少必要字段"}), 400

    try:
        from services.parent_interview_service import generate_detailed_feedback

        feedback = generate_detailed_feedback(question, answer, school_type)

        return jsonify({"success": True, "feedback": feedback})

    except Exception as e:
        print(f"Error generating feedback: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/report/<session_id>", methods=["GET"])
def api_parent_interview_report(session_id):
    """获取面试报告"""
    try:
        from services.parent_interview_service import generate_interview_report

        report = generate_interview_report(session_id)

        if not report:
            return jsonify({"error": "报告不存在"}), 404

        return jsonify({"success": True, "report": report})

    except Exception as e:
        print(f"Error getting report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/history", methods=["GET"])
def api_parent_interview_history():
    """获取面试历史记录"""
    try:
        from services.parent_interview_service import parent_interview_session

        sessions = parent_interview_session.get_all_sessions()

        # 格式化历史记录
        history = []
        for session in sessions:
            history.append(
                {
                    "session_id": session.get("session_id"),
                    "school_type": session.get("school_type"),
                    "total_questions": len(session.get("questions", [])),
                    "answered_questions": len(session.get("answers", [])),
                    "total_score": session.get("total_score", 0),
                    "created_at": session.get("created_at"),
                    "status": session.get("status"),
                }
            )

        return jsonify({"success": True, "history": history})

    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-interview/school-types", methods=["GET"])
def api_parent_interview_school_types():
    """获取学校类型"""
    try:
        from services.parent_interview_service import get_school_types

        school_types = get_school_types()

        return jsonify({"success": True, "school_types": school_types})

    except Exception as e:
        print(f"Error getting school types: {e}")
        return jsonify({"error": str(e)}), 500


# ============ 学校真题库 Routes ============


@app.route("/school-questions")
def school_questions():
    """学校真题库首页"""
    from services.school_service import (
        get_featured_schools,
        get_districts,
        get_categories,
    )

    featured_schools = get_featured_schools()
    districts = get_districts()
    categories = get_categories()

    return render_template(
        "school-questions.html",
        featured_schools=featured_schools,
        districts=districts,
        categories=categories,
        active_page="school-questions",
    )


@app.route("/school-questions/schools")
def school_list():
    """学校列表页"""
    from services.school_service import get_all_schools, get_districts, get_categories

    district = request.args.get("district", "")
    category = request.args.get("category", "")
    school_type = request.args.get("type", "")

    filters = {}
    if district:
        filters["district"] = district
    if category:
        filters["category"] = category
    if school_type:
        filters["school_type"] = school_type

    schools = get_all_schools(filters if filters else None)
    districts = get_districts()
    categories = get_categories()

    return render_template(
        "school-list.html",
        schools=schools,
        districts=districts,
        categories=categories,
        selected_district=district,
        selected_category=category,
        selected_type=school_type,
        active_page="school-questions",
    )


@app.route("/school-questions/school/<int:school_id>")
def school_detail(school_id):
    """学校详情页"""
    from services.school_service import (
        get_school_by_id,
        get_school_questions,
        get_interview_timeline,
    )

    school = get_school_by_id(school_id)
    if not school:
        flash("学校不存在", "error")
        return redirect(url_for("school_questions"))

    questions = get_school_questions(school_id)
    timeline = get_interview_timeline(school_id)

    return render_template(
        "school-detail.html",
        school=school,
        questions=questions,
        timeline=timeline,
        active_page="school-questions",
    )


@app.route("/school-questions/ai-match")
def ai_match():
    """AI智能匹配页"""
    from services.school_service import get_all_schools
    from services.ai_matching_service import get_question_types, get_match_history

    schools = get_all_schools()
    question_types = get_question_types()

    # 如果已登录，获取历史记录
    history = []
    if session.get("logged_in"):
        history = get_match_history(session.get("user_id"), limit=5)

    return render_template(
        "ai-match.html",
        schools=schools,
        question_types=question_types,
        history=history,
        active_page="ai-match",
    )


@app.route("/interview-experience")
def interview_experience():
    """面试经验分享页"""
    from services.school_service import get_experience_list, get_all_schools

    school_id = request.args.get("school_id", "")
    author_type = request.args.get("author_type", "")

    filters = {}
    if school_id:
        filters["school_id"] = school_id
    if author_type:
        filters["author_type"] = author_type

    experiences = get_experience_list(filters if filters else None)
    schools = get_all_schools()

    return render_template(
        "interview-experience.html",
        experiences=experiences,
        schools=schools,
        selected_school=school_id,
        selected_author=author_type,
        active_page="experience",
    )


@app.route("/interview-timeline")
def interview_timeline():
    """面试时间线页"""
    from services.school_service import get_all_schools

    schools = get_all_schools()
    school_id = request.args.get("school_id", "")

    timeline = []
    school = None
    if school_id:
        from services.school_service import get_school_by_id, get_interview_timeline

        school = get_school_by_id(school_id)
        timeline = get_interview_timeline(school_id)

    return render_template(
        "interview-timeline.html",
        schools=schools,
        timeline=timeline,
        selected_school=school_id,
        school=school,
        active_page="timeline",
    )


# ============ 学校真题库 API Routes ============


@app.route("/api/schools", methods=["GET"])
def api_schools():
    """获取学校列表API"""
    try:
        from services.school_service import get_all_schools

        district = request.args.get("district", "")
        category = request.args.get("category", "")
        school_type = request.args.get("type", "")

        filters = {}
        if district:
            filters["district"] = district
        if category:
            filters["category"] = category
        if school_type:
            filters["school_type"] = school_type

        schools = get_all_schools(filters if filters else None)

        return jsonify({"success": True, "schools": schools})
    except Exception as e:
        print(f"Error fetching schools: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/schools/<int:school_id>", methods=["GET"])
def api_school_detail(school_id):
    """获取学校详情API"""
    try:
        from services.school_service import get_school_by_id

        school = get_school_by_id(school_id)
        if not school:
            return jsonify({"error": "School not found"}), 404

        return jsonify({"success": True, "school": school})
    except Exception as e:
        print(f"Error fetching school: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/schools/<int:school_id>/questions", methods=["GET"])
def api_school_questions(school_id):
    """获取学校真题API"""
    try:
        from services.school_service import get_school_questions

        question_type = request.args.get("type", "")
        difficulty = request.args.get("difficulty", "")
        year = request.args.get("year", "")

        filters = {}
        if question_type:
            filters["question_type"] = question_type
        if difficulty:
            filters["difficulty"] = difficulty
        if year:
            filters["year"] = int(year)

        questions = get_school_questions(school_id, filters if filters else None)

        return jsonify({"success": True, "questions": questions})
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai-match/recommend", methods=["POST"])
def api_ai_match_recommend():
    """AI推荐API"""
    try:
        from services.ai_matching_service import recommend_questions

        data = request.get_json() or {}
        user_id = session.get("user_id") or 1  # 默认用户
        school_id = data.get("school_id")
        profile_id = data.get("profile_id")

        result = recommend_questions(user_id, school_id, profile_id)

        return jsonify({"success": True, "result": result})
    except Exception as e:
        print(f"Error in AI match: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/experience", methods=["GET"])
def api_experience():
    """获取经验列表API"""
    try:
        from services.school_service import get_experience_list

        school_id = request.args.get("school_id", "")
        author_type = request.args.get("author_type", "")

        filters = {}
        if school_id:
            filters["school_id"] = int(school_id)
        if author_type:
            filters["author_type"] = author_type

        experiences = get_experience_list(filters if filters else None)

        return jsonify({"success": True, "experiences": experiences})
    except Exception as e:
        print(f"Error fetching experiences: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/timeline/<int:school_id>", methods=["GET"])
def api_timeline(school_id):
    """获取面试时间线API"""
    try:
        from services.school_service import get_interview_timeline

        timeline = get_interview_timeline(school_id)

        return jsonify({"success": True, "timeline": timeline})
    except Exception as e:
        print(f"Error fetching timeline: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/questions/like", methods=["POST"])
def api_like_question():
    """点赞题目API"""
    try:
        from services.school_service import like_question

        data = request.get_json() or {}
        question_id = data.get("question_id")

        if not question_id:
            return jsonify({"error": "Question ID required"}), 400

        success = like_question(question_id)

        return jsonify({"success": success})
    except Exception as e:
        print(f"Error liking question: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Micro Lesson Workshop Routes ============


@app.route("/micro-lessons")
def micro_lessons_page():
    """微课工坊首页"""
    return render_template("micro-lessons.html")


@app.route("/micro-lesson/<int:lesson_id>")
def micro_lesson_detail(lesson_id):
    """微课详情页"""
    return render_template("micro-lesson-detail.html", lesson_id=lesson_id)


@app.route("/daily-tasks")
def daily_tasks_page():
    """每日任务页面"""
    return render_template("daily-tasks.html")


@app.route("/practice/quick/<topic>")
def quick_practice_page(topic):
    """快速问答练习页面"""
    return render_template("practice-quick.html", topic=topic)


@app.route("/practice/voice/<int:lesson_id>")
def voice_practice_page(lesson_id):
    """语音跟读练习页面"""
    return render_template("practice-voice.html", lesson_id=lesson_id)


# ============ Micro Lesson API Endpoints ============


@app.route("/api/micro-lessons", methods=["GET"])
def api_micro_lessons_list():
    """获取微课列表API"""
    try:
        from services.micro_lesson_service import get_user_lessons

        user_id = session.get("user_id")
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)

        lessons = get_user_lessons(user_id, limit, offset)

        return jsonify({"success": True, "lessons": lessons, "count": len(lessons)})
    except Exception as e:
        print(f"Error fetching micro lessons: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/micro-lessons/generate", methods=["POST"])
def api_generate_micro_lesson():
    """生成微课API"""
    try:
        from services.micro_lesson_service import (
            generate_micro_lesson,
            save_micro_lesson,
        )

        data = request.get_json() or {}
        topic = data.get("topic", "general knowledge")
        difficulty = data.get("difficulty", "easy")
        duration = data.get("duration", 60)

        # Get user profile
        user_profile = {
            "child_name": session.get("child_name", "小朋友"),
            "child_age": session.get("child_age", 6),
            "preferred_language": session.get("preferred_language", "zh"),
        }

        # Generate lesson
        lesson_data = generate_micro_lesson(user_profile, topic, difficulty, duration)

        # Save to database
        user_id = session.get("user_id")
        saved_lesson = save_micro_lesson(user_id, lesson_data)

        return jsonify({"success": True, "lesson": saved_lesson or lesson_data})
    except Exception as e:
        print(f"Error generating micro lesson: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/micro-lessons/<int:lesson_id>", methods=["GET"])
def api_micro_lesson_detail(lesson_id):
    """获取微课详情API"""
    try:
        from db.database import execute_query

        query = "SELECT * FROM micro_lessons WHERE id = %s"
        lessons = execute_query(query, (lesson_id,), fetch=True)

        if not lessons:
            return jsonify({"error": "Lesson not found"}), 404

        return jsonify({"success": True, "lesson": lessons[0]})
    except Exception as e:
        print(f"Error fetching lesson detail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/micro-lessons/<int:lesson_id>/progress", methods=["POST"])
def api_update_lesson_progress(lesson_id):
    """更新微课学习进度API"""
    try:
        from services.micro_lesson_service import update_lesson_progress

        data = request.get_json() or {}
        progress_percent = data.get("progress_percent", 0)
        time_spent = data.get("time_spent", 0)

        user_id = session.get("user_id")
        result = update_lesson_progress(
            user_id, lesson_id, progress_percent, time_spent
        )

        return jsonify({"success": True, "progress": result})
    except Exception as e:
        print(f"Error updating progress: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Daily Tasks API Endpoints ============


@app.route("/api/daily-tasks", methods=["GET"])
def api_daily_tasks():
    """获取每日任务API"""
    try:
        from services.micro_lesson_service import get_daily_tasks
        from datetime import datetime

        user_id = session.get("user_id")
        task_date = request.args.get("date")

        # Get user profile for task generation
        user_profile = {
            "child_name": session.get("child_name", "小朋友"),
            "child_age": session.get("child_age", 6),
            "topics": session.get("child_interests", ["science", "math", "language"]),
            "child_interests": session.get("child_interests", []),
        }

        if task_date:
            task_date = datetime.strptime(task_date, "%Y-%m-%d").date()
        else:
            task_date = None

        tasks = get_daily_tasks(user_id, user_profile, task_date)

        return jsonify({"success": True, "tasks": tasks, "count": len(tasks)})
    except Exception as e:
        print(f"Error fetching daily tasks: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/daily-tasks/complete", methods=["POST"])
def api_complete_task():
    """完成任务API"""
    try:
        from services.micro_lesson_service import complete_task

        data = request.get_json() or {}
        task_id = data.get("task_id")
        score = data.get("score")

        if not task_id:
            return jsonify({"error": "Task ID required"}), 400

        user_id = session.get("user_id")
        result = complete_task(user_id, task_id, score)

        if not result:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"success": True, "task": result})
    except Exception as e:
        print(f"Error completing task: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Practice API Endpoints ============


@app.route("/api/practice/quick", methods=["GET"])
def api_quick_practice():
    """获取快速问答练习API"""
    try:
        from services.micro_lesson_service import generate_quick_practice

        topic = request.args.get("topic", "general")
        difficulty = request.args.get("difficulty", "easy")

        user_profile = {
            "child_name": session.get("child_name", "小朋友"),
            "child_age": session.get("child_age", 6),
            "preferred_language": session.get("preferred_language", "zh"),
        }

        practice = generate_quick_practice(user_profile, topic, difficulty)

        return jsonify({"success": True, "practice": practice})
    except Exception as e:
        print(f"Error generating quick practice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/practice/voice", methods=["GET"])
def api_voice_practice():
    """获取语音跟读练习API"""
    try:
        from services.micro_lesson_service import generate_voice_repeat_practice

        lesson_id = request.args.get("lesson_id", type=int)
        topic = request.args.get("topic", "general")

        user_profile = {
            "child_name": session.get("child_name", "小朋友"),
            "child_age": session.get("child_age", 6),
            "preferred_language": session.get("preferred_language", "zh"),
        }

        practice = generate_voice_repeat_practice(user_profile, lesson_id, topic)

        return jsonify({"success": True, "practice": practice})
    except Exception as e:
        print(f"Error generating voice practice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/practice/scenario", methods=["GET"])
def api_scenario_practice():
    """获取情景模拟练习API"""
    try:
        from services.micro_lesson_service import generate_scenario_simulation

        topic = request.args.get("topic", "general")
        difficulty = request.args.get("difficulty", "easy")

        user_profile = {
            "child_name": session.get("child_name", "小朋友"),
            "child_age": session.get("child_age", 6),
            "preferred_language": session.get("preferred_language", "zh"),
        }

        practice = generate_scenario_simulation(user_profile, topic, difficulty)

        return jsonify({"success": True, "practice": practice})
    except Exception as e:
        print(f"Error generating scenario practice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/practice/submit", methods=["POST"])
def api_submit_practice():
    """提交练习结果API"""
    try:
        from services.micro_lesson_service import record_practice_session

        data = request.get_json() or {}

        session_data = {
            "session_type": data.get("session_type"),
            "topic_id": data.get("topic_id"),
            "lesson_id": data.get("lesson_id"),
            "duration_seconds": data.get("duration_seconds"),
            "time_limit_seconds": data.get("time_limit_seconds"),
            "score": data.get("score"),
            "max_score": data.get("max_score"),
            "correct_count": data.get("correct_count", 0),
            "total_count": data.get("total_count", 0),
            "answers": data.get("answers", []),
            "audio_url": data.get("audio_url"),
            "transcript": data.get("transcript"),
            "feedback": data.get("feedback"),
        }

        user_id = session.get("user_id")
        result = record_practice_session(user_id, session_data)

        return jsonify({"success": True, "session": result})
    except Exception as e:
        print(f"Error submitting practice: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/practice/history", methods=["GET"])
def api_practice_history():
    """获取练习历史API"""
    try:
        from services.micro_lesson_service import get_practice_history

        user_id = session.get("user_id")
        session_type = request.args.get("type")
        limit = request.args.get("limit", 10, type=int)

        history = get_practice_history(user_id, session_type, limit)

        return jsonify({"success": True, "history": history, "count": len(history)})
    except Exception as e:
        print(f"Error fetching practice history: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Showcase Routes (学习成果社交秀) ============


@app.route("/showcase")
def showcase_page():
    """学习成果社交秀首页"""
    child_name = session.get("child_name", "同学")
    return render_template("showcase.html", child_name=child_name)


@app.route("/showcase/generate")
def showcase_generate():
    """生成成就海报页面"""
    child_name = session.get("child_name", "同学")
    share_type = request.args.get("type", "achievement")
    return render_template(
        "showcase_generate.html", child_name=child_name, share_type=share_type
    )


@app.route("/showcase/share/<share_type>")
def showcase_share(share_type="wechat"):
    """分享页面"""
    child_name = session.get("child_name", "同学")
    return render_template(
        "showcase_share.html", child_name=child_name, share_type=share_type
    )


@app.route("/api/showcase/templates", methods=["GET"])
def api_showcase_templates():
    """获取海报模板API"""
    try:
        from services.showcase_service import get_templates

        category = request.args.get("category")
        templates = get_templates(category)

        return jsonify({"success": True, "templates": templates})
    except Exception as e:
        print(f"Error fetching templates: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/showcase/generate", methods=["POST"])
def api_showcase_generate():
    """生成成就海报API"""
    try:
        from services.showcase_service import (
            generate_poster_data,
            create_share_record,
            generate_share_image,
        )

        data = request.get_json() or {}
        poster_type = data.get("type", "achievement")
        template_id = data.get("template", "achievement_basic")

        # Get user data
        user_id = session.get("user_id")
        child_name = session.get("child_name", "同学")

        # Build user data
        user_data = {"name": child_name, "avatar": session.get("picture")}

        # Get achievement data (mock data for demo)
        achievement_data = {
            "title": "学习成就",
            "description": "恭喜获得新成就！",
            "icon": "🏆",
            "streak_days": 7,
            "badges_count": 5,
        }

        # Generate poster data
        poster_data = generate_poster_data(user_data, template_id, achievement_data)

        # Generate share image
        image_url = generate_share_image(poster_data)

        # Create share record if user is logged in
        if user_id:
            create_share_record(user_id, poster_type, poster_data)

        return jsonify(
            {"success": True, "poster_data": poster_data, "image_url": image_url}
        )
    except Exception as e:
        print(f"Error generating poster: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/showcase/share", methods=["POST"])
def api_showcase_share():
    """分享记录API"""
    try:
        from services.showcase_service import create_share_record

        data = request.get_json() or {}
        platform = data.get("platform", "wechat")
        poster_type = data.get("type", "achievement")
        poster_data = data.get("poster_data", {})

        user_id = session.get("user_id")

        if user_id:
            share_id = create_share_record(user_id, poster_type, poster_data, platform)
            return jsonify({"success": True, "share_id": share_id})
        else:
            return jsonify({"success": True, "message": "Share recorded (guest mode)"})
    except Exception as e:
        print(f"Error recording share: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# AI面试复盘室页面和API
# ============================================


@app.route("/debrief")
@login_required
def debrief_index():
    """复盘室首页"""
    return render_template("debrief/index.html")


@app.route("/debrief/session/<session_id>")
@login_required
def debrief_session(session_id):
    """单次面试复盘详情"""
    return render_template("debrief/session.html", session_id=session_id)


@app.route("/debrief/history")
@login_required
def debrief_history():
    """历史复盘记录"""
    return render_template("debrief/history.html")


@app.route("/debrief/compare")
@login_required
def debrief_compare():
    """历史对比分析"""
    return render_template("debrief/compare.html")


@app.route("/api/debrief/sessions", methods=["GET"])
@login_required
def api_debrief_sessions():
    """获取面试复盘列表"""
    user_id = session.get("user_id")
    limit = request.args.get("limit", 20, type=int)
    status = request.args.get("status", None)

    try:
        from db.database import get_debrief_sessions, get_debrief_statistics

        sessions = get_debrief_sessions(user_id, limit, status)
        stats = get_debrief_statistics(user_id)

        return jsonify({"success": True, "sessions": sessions, "statistics": stats})
    except Exception as e:
        print(f"Error fetching debrief sessions: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/debrief/session/<session_id>", methods=["GET"])
@login_required
def api_debrief_session(session_id):
    """获取单次复盘详情"""
    user_id = session.get("user_id")

    try:
        from db.database import (
            get_debrief_session,
            get_content_analyses,
            get_voice_analyses,
            get_recommendations,
        )

        session = get_debrief_session(session_id)

        if not session:
            return jsonify({"error": "Session not found"}), 404

        if session.get("user_id") != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        # 获取详细分析数据
        content_analyses = get_content_analyses(session_id)
        voice_analyses = get_voice_analyses(session_id)
        recommendations = get_recommendations(session_id)

        return jsonify(
            {
                "success": True,
                "session": session,
                "content_analyses": content_analyses,
                "voice_analyses": voice_analyses,
                "recommendations": recommendations,
            }
        )
    except Exception as e:
        print(f"Error fetching debrief session: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/debrief/analyze", methods=["POST"])
@login_required
def api_debrief_analyze():
    """分析面试表现"""
    user_id = session.get("user_id")

    try:
        from db.database import (
            create_debrief_session,
            update_debrief_session,
            add_content_analysis,
            add_voice_analysis,
            add_recommendation,
        )
        from services.debrief_service import (
            analyze_interview_session,
            get_sample_debrief_data,
        )

        data = request.get_json() or {}

        # 获取面试数据
        interview_type = data.get("interview_type", "mock")
        school_type = data.get("school_type", "holistic")
        interview_session_id = data.get("interview_session_id")
        questions = data.get("questions", [])
        answers = data.get("answers", [])

        # 创建复盘会话
        session_data = create_debrief_session(
            user_id=user_id,
            interview_session_id=interview_session_id,
            interview_type=interview_type,
            school_type=school_type,
        )

        session_id = session_data["id"]

        # 使用示例数据进行演示
        # 在实际生产环境中，应该使用真实分析
        analysis_result = get_sample_debrief_data()

        # 保存内容分析
        for content in analysis_result.get("content_analyses", []):
            add_content_analysis(
                debrief_session_id=session_id,
                question_index=content.get("question_index"),
                question=content.get("question"),
                answer=content.get("answer"),
                logic_score=content.get("logic_score"),
                completeness_score=content.get("completeness_score"),
                creativity_score=content.get("creativity_score"),
                relevance_score=content.get("relevance_score"),
                total_score=content.get("total_score"),
                feedback=content.get("feedback"),
                strengths=content.get("strengths"),
                improvements=content.get("improvements"),
            )

        # 保存语音分析
        for voice in analysis_result.get("voice_analyses", []):
            add_voice_analysis(
                debrief_session_id=session_id,
                question_index=voice.get("question_index"),
                speaking_rate=voice.get("speaking_rate"),
                fluency_score=voice.get("fluency_score"),
                pause_count=voice.get("pause_count"),
                pause_duration=voice.get("pause_duration"),
                clarity_score=voice.get("clarity_score"),
                sentiment=voice.get("sentiment"),
            )

        # 保存建议
        for rec in analysis_result.get("recommendations", []):
            add_recommendation(
                debrief_session_id=session_id,
                category=rec.get("category"),
                priority=rec.get("priority"),
                title=rec.get("title"),
                description=rec.get("description"),
                exercises=rec.get("exercises"),
                resources=rec.get("resources"),
            )

        # 更新会话状态为完成
        from datetime import datetime

        update_debrief_session(
            session_id=session_id,
            finished_at=datetime.now().isoformat(),
            duration_seconds=data.get("duration", 300),
            total_questions=len(questions) or analysis_result.get("question_count"),
            overall_score=analysis_result.get("overall_score"),
            status="completed",
        )

        return jsonify(
            {"success": True, "session_id": session_id, "analysis": analysis_result}
        )

    except Exception as e:
        print(f"Error analyzing interview: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/debrief/compare", methods=["GET"])
@login_required
def api_debrief_compare():
    """历史对比数据"""
    user_id = session.get("user_id")

    try:
        from db.database import get_debrief_sessions
        from services.debrief_service import generate_comparison_data

        # 获取所有已完成会话
        sessions = get_debrief_sessions(user_id, limit=50, status="completed")

        # 生成对比数据
        comparison = generate_comparison_data(user_id, sessions)

        return jsonify(
            {"success": True, "comparison": comparison, "sessions": sessions}
        )
    except Exception as e:
        print(f"Error generating comparison: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/debrief/recommendations", methods=["GET"])
@login_required
def api_debrief_recommendations():
    """获取待完成的改进建议"""
    user_id = session.get("user_id")

    try:
        from db.database import get_user_pending_recommendations

        recommendations = get_user_pending_recommendations(user_id, limit=10)

        return jsonify({"success": True, "recommendations": recommendations})
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route(
    "/api/debrief/recommendations/<recommendation_id>/complete", methods=["POST"]
)
@login_required
def api_debrief_complete_recommendation(recommendation_id):
    """标记建议为已完成"""
    try:
        from db.database import mark_recommendation_completed

        result = mark_recommendation_completed(recommendation_id)

        return jsonify({"success": True, "recommendation": result})
    except Exception as e:
        print(f"Error completing recommendation: {e}")
        return jsonify({"error": str(e)}), 500


# ============ AI Companion Routes ============


@app.route("/companion")
@login_required
def companion_page():
    """AI Companion main page."""
    return render_template("companion.html")


@app.route("/api/companion", methods=["GET"])
@login_required
def api_companion_info():
    """Get user's AI companion information."""
    try:
        from services.ai_companion_service import (
            get_companion_info,
            create_or_get_user_companion,
        )

        user_id = session.get("user_id")

        # Get or create companion
        companion = create_or_get_user_companion(user_id)

        if not companion:
            return jsonify({"error": "Failed to get companion"}), 500

        # Get full info
        info = get_companion_info(user_id)

        return jsonify({"success": True, "data": info})
    except Exception as e:
        print(f"Error getting companion info: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/create", methods=["POST"])
@login_required
def api_companion_create():
    """Create a new AI companion."""
    try:
        from services.ai_companion_service import create_user_companion

        user_id = session.get("user_id")
        data = request.get_json() or {}

        name = data.get("name", "").strip()
        character_type = data.get("characterType", "dinosaur")

        if not name:
            return jsonify({"error": "Please provide a name"}), 400

        if len(name) > 10:
            return jsonify({"error": "Name must be 10 characters or less"}), 400

        companion = create_user_companion(user_id, name, character_type)

        if not companion:
            return jsonify({"error": "Failed to create companion"}), 500

        return jsonify(
            {
                "success": True,
                "data": {
                    "id": str(companion["id"]),
                    "name": companion["name"],
                    "characterType": companion["character_type"],
                    "level": companion["level"],
                    "experience": companion["experience"],
                    "totalExperience": companion["total_experience"],
                    "consecutiveDays": companion["consecutive_days"],
                    "currentMood": companion["current_mood"],
                    "unlockedSkills": companion["unlocked_skills"],
                    "createdAt": companion["created_at"].isoformat()
                    if companion.get("created_at")
                    else None,
                },
            }
        )
    except Exception as e:
        print(f"Error creating companion: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/experience", methods=["POST"])
@login_required
def api_companion_experience():
    """Add experience to companion."""
    try:
        from services.ai_companion_service import add_experience

        user_id = session.get("user_id")
        data = request.get_json() or {}

        experience_type = data.get("experienceType", "practice_time")
        amount = data.get("amount", 0)
        reason = data.get("reason", "")

        if amount <= 0:
            return jsonify({"error": "Invalid experience amount"}), 400

        result = add_experience(user_id, experience_type, amount, reason)

        if not result:
            return jsonify({"error": "Failed to add experience"}), 500

        return jsonify({"success": True, "data": result})
    except Exception as e:
        print(f"Error adding experience: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/tasks", methods=["GET"])
@login_required
def api_companion_tasks():
    """Get daily tasks for companion."""
    try:
        from services.ai_companion_service import get_daily_tasks

        user_id = session.get("user_id")
        date_str = request.args.get("date")

        from datetime import datetime

        task_date = None
        if date_str:
            try:
                task_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        tasks = get_daily_tasks(user_id, task_date)

        return jsonify({"success": True, "data": tasks})
    except Exception as e:
        print(f"Error getting tasks: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/tasks/complete", methods=["POST"])
@login_required
def api_companion_task_complete():
    """Complete a daily task."""
    try:
        from services.ai_companion_service import complete_task

        user_id = session.get("user_id")
        data = request.get_json() or {}

        task_id = data.get("taskId")

        if not task_id:
            return jsonify({"error": "Task ID is required"}), 400

        result = complete_task(user_id, task_id)

        if not result:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"success": True, "data": result})
    except Exception as e:
        print(f"Error completing task: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/skills", methods=["GET"])
@login_required
def api_companion_skills():
    """Get companion skills."""
    try:
        from services.ai_companion_service import (
            get_available_skills,
            get_companion_info,
        )

        user_id = session.get("user_id")

        # Get companion info first to ensure companion exists
        companion_info = get_companion_info(user_id)
        if not companion_info:
            return jsonify({"error": "Companion not found"}), 404

        skills = get_available_skills(user_id)

        return jsonify(
            {
                "success": True,
                "data": {"companion_level": companion_info["level"], "skills": skills},
            }
        )
    except Exception as e:
        print(f"Error getting skills: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/skills/unlock", methods=["POST"])
@login_required
def api_companion_skill_unlock():
    """Unlock a companion skill."""
    try:
        from services.ai_companion_service import unlock_skill

        user_id = session.get("user_id")
        data = request.get_json() or {}

        skill_id = data.get("skillId")

        if not skill_id:
            return jsonify({"error": "Skill ID is required"}), 400

        result = unlock_skill(user_id, skill_id)

        return jsonify(
            {
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "data": result.get("skill"),
            }
        )
    except Exception as e:
        print(f"Error unlocking skill: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/dialogue", methods=["GET"])
@login_required
def api_companion_dialogue():
    """Get companion dialogue."""
    try:
        from services.ai_companion_service import get_companion_dialogue

        user_id = session.get("user_id")
        trigger_type = request.args.get("trigger", "idle")
        emotion = request.args.get("emotion")

        dialogue = get_companion_dialogue(user_id, trigger_type, emotion)

        return jsonify({"success": True, "data": dialogue})
    except Exception as e:
        print(f"Error getting dialogue: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/companion/mood", methods=["POST"])
@login_required
def api_companion_mood():
    """Update companion mood."""
    try:
        from services.ai_companion_service import update_mood, get_user_companion

        user_id = session.get("user_id")
        data = request.get_json() or {}

        mood = data.get("mood")

        # If no mood provided, calculate automatically
        if not mood:
            from services.ai_companion_service import calculate_mood

            mood = calculate_mood(user_id)
        else:
            update_mood(user_id, mood)

        companion = get_user_companion(user_id)

        return jsonify(
            {
                "success": True,
                "data": {
                    "mood": mood,
                    "companion": {
                        "name": companion["name"],
                        "character_type": companion["character_type"]
                        if companion
                        else None,
                    },
                },
            }
        )
    except Exception as e:
        print(f"Error updating mood: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== Energy Station Routes (面试能量站) ====================


@app.route("/energy-station")
def energy_station():
    """面试能量站主页"""
    return render_template("energy-station.html")


@app.route("/api/energy-station/summary", methods=["GET"])
def api_energy_station_summary():
    """获取能量站内容摘要"""
    try:
        from services.energy_station_service import get_all_content_summary

        result = get_all_content_summary()
        return jsonify(result)
    except Exception as e:
        print(f"Error getting energy station summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/micro-lessons", methods=["GET"])
def api_energy_station_micro_lessons():
    """获取面试心理微课列表"""
    try:
        from services.energy_station_service import get_micro_lessons

        result = get_micro_lessons()
        return jsonify(result)
    except Exception as e:
        print(f"Error getting micro lessons: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/micro-lesson/<lesson_id>", methods=["GET"])
def api_energy_station_micro_lesson_detail(lesson_id):
    """获取微课详细内容"""
    try:
        from services.energy_station_service import get_micro_lesson_detail

        result = get_micro_lesson_detail(lesson_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting micro lesson detail: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/energy-pack", methods=["GET"])
def api_energy_station_energy_pack():
    """获取考前能量包"""
    try:
        from services.energy_station_service import get_pre_interview_energy_pack

        result = get_pre_interview_energy_pack()
        return jsonify(result)
    except Exception as e:
        print(f"Error getting energy pack: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/parent-lessons", methods=["GET"])
def api_energy_station_parent_lessons():
    """获取家长心理课列表"""
    try:
        from services.energy_station_service import get_parent_lessons

        result = get_parent_lessons()
        return jsonify(result)
    except Exception as e:
        print(f"Error getting parent lessons: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/parent-lesson/<lesson_id>", methods=["GET"])
def api_energy_station_parent_lesson_detail(lesson_id):
    """获取家长心理课详细内容"""
    try:
        from services.energy_station_service import get_parent_lesson_detail

        result = get_parent_lesson_detail(lesson_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting parent lesson detail: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/companion/persona", methods=["GET"])
def api_energy_station_companion_persona():
    """获取AI心理陪伴导师角色信息"""
    try:
        from services.energy_station_service import get_companion_persona

        character_type = request.args.get("character_type", "dinosaur")
        result = get_companion_persona(character_type)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting companion persona: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/energy-station/companion/chat", methods=["POST"])
def api_energy_station_companion_chat():
    """AI心理陪伴导师对话"""
    try:
        from services.energy_station_service import get_ai_companion_response
        import asyncio

        data = request.get_json() or {}
        user_message = data.get("message", "")
        character_type = data.get("character_type", "dinosaur")
        conversation_history = data.get("history", [])

        if not user_message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                get_ai_companion_response(
                    user_message, character_type, conversation_history
                )
            )
        finally:
            loop.close()

        return jsonify(result)
    except Exception as e:
        print(f"Error in companion chat: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Confidence Training Routes ====================


@app.route("/confidence-training")
def confidence_training():
    """面霸心理训练营主页"""
    return render_template("confidence-training.html")


@app.route("/api/confidence-training/summary", methods=["GET"])
def api_confidence_training_summary():
    """获取心理训练营内容摘要"""
    try:
        from services.confidence_training_service import get_confidence_training_summary

        return jsonify(get_confidence_training_summary())
    except Exception as e:
        print(f"Error getting confidence training summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/breathing", methods=["GET"])
def api_confidence_training_breathing():
    """获取所有呼吸训练列表"""
    try:
        from services.confidence_training_service import get_breathing_exercises

        return jsonify(get_breathing_exercises())
    except Exception as e:
        print(f"Error getting breathing exercises: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/breathing/<exercise_id>", methods=["GET"])
def api_confidence_training_breathing_detail(exercise_id):
    """获取呼吸训练详细内容"""
    try:
        from services.confidence_training_service import get_breathing_exercise_detail

        return jsonify(get_breathing_exercise_detail(exercise_id))
    except Exception as e:
        print(f"Error getting breathing exercise detail: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/affirmation", methods=["GET"])
def api_confidence_training_affirmation():
    """获取随机积极心理暗示"""
    try:
        from services.confidence_training_service import get_random_affirmation

        return jsonify(get_random_affirmation())
    except Exception as e:
        print(f"Error getting affirmation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/affirmation/generate", methods=["POST"])
def api_confidence_training_affirmation_generate():
    """生成个性化心理暗示"""
    try:
        from services.confidence_training_service import (
            generate_personalized_affirmation,
        )
        import asyncio

        data = request.get_json() or {}
        user_context = data.get("context")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                generate_personalized_affirmation(user_context)
            )
        finally:
            loop.close()

        return jsonify(result)
    except Exception as e:
        print(f"Error generating affirmation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/pressure-test", methods=["GET"])
def api_confidence_training_pressure_test_levels():
    """获取压力测试所有级别"""
    try:
        from services.confidence_training_service import get_pressure_test_levels

        return jsonify(get_pressure_test_levels())
    except Exception as e:
        print(f"Error getting pressure test levels: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/pressure-test/<int:level>", methods=["GET"])
def api_confidence_training_pressure_test_scenario(level):
    """获取特定级别的压力测试场景"""
    try:
        from services.confidence_training_service import get_pressure_test_scenario

        return jsonify(get_pressure_test_scenario(level))
    except Exception as e:
        print(f"Error getting pressure test scenario: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/courses", methods=["GET"])
def api_confidence_training_courses():
    """获取所有心理准备动画课程"""
    try:
        from services.confidence_training_service import get_animation_courses

        return jsonify(get_animation_courses())
    except Exception as e:
        print(f"Error getting animation courses: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/course/<course_id>", methods=["GET"])
def api_confidence_training_course_detail(course_id):
    """获取动画课程详细内容"""
    try:
        from services.confidence_training_service import get_animation_course_detail

        return jsonify(get_animation_course_detail(course_id))
    except Exception as e:
        print(f"Error getting course detail: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/emotion/analyze", methods=["POST"])
def api_confidence_training_emotion_analyze():
    """分析用户情绪"""
    try:
        from services.confidence_training_service import analyze_emotion

        data = request.get_json() or {}
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        return jsonify(analyze_emotion(user_message))
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/confidence-training/emotion/analyze-answer", methods=["POST"])
def api_confidence_training_emotion_analyze_answer():
    """分析答题时的情绪状态"""
    try:
        from services.confidence_training_service import analyze_answer_emotion
        import asyncio

        data = request.get_json() or {}
        answer_text = data.get("answer", "")
        question_text = data.get("question")

        if not answer_text:
            return jsonify({"success": False, "error": "Answer is required"}), 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                analyze_answer_emotion(answer_text, question_text)
            )
        finally:
            loop.close()

        return jsonify(result)
    except Exception as e:
        print(f"Error analyzing answer emotion: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== Arena Routes ====================


@app.route("/arena")
@login_required
def arena():
    """Arena homepage."""
    return render_template("arena.html")


@app.route("/api/arena/rank", methods=["GET"])
@login_required
def api_arena_rank():
    """Get user's arena rank information."""
    try:
        from services.arena_service import get_or_create_user_rank, get_rank_config

        user_id = session.get("user_id")
        rank_data = get_or_create_user_rank(user_id)
        rank_config = get_rank_config(rank_data["current_rank"])

        # Calculate win rate
        win_rate = 0
        if rank_data["total_matches"] > 0:
            win_rate = int(rank_data["wins"] / rank_data["total_matches"] * 100)

        return jsonify(
            {
                "success": True,
                "data": {
                    "rank_id": rank_data["current_rank"],
                    "rank_name": rank_config["rank_name_zh"] if rank_config else "青銅",
                    "rank_icon": rank_config["rank_icon"] if rank_config else "🥉",
                    "rank_points": rank_data["rank_points"],
                    "total_matches": rank_data["total_matches"],
                    "wins": rank_data["wins"],
                    "losses": rank_data["losses"],
                    "win_rate": f"{win_rate}%",
                    "current_streak": rank_data["current_streak"],
                    "best_streak": rank_data["best_streak"],
                },
            }
        )
    except Exception as e:
        print(f"Error getting arena rank: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/arena/start", methods=["POST"])
@login_required
def api_arena_start():
    """Start a new arena match."""
    try:
        from services.arena_service import create_match, get_or_create_user_rank
        from services.question_bank_service import get_random_questions

        user_id = session.get("user_id")
        data = request.get_json() or {}

        match_type = data.get("match_type", "challenge")  # challenge, timed, practice
        category = data.get("category", "self_intro")
        difficulty = data.get("difficulty", "medium")
        time_limit = data.get("time_limit", 300)  # seconds

        # Check if user has an active match
        from services.arena_service import get_user_active_match

        active_match = get_user_active_match(user_id)
        if active_match:
            return jsonify({"success": False, "error": "你還有一場對戰正在进行中"}), 400

        # Get opponent info
        opponent_names = {
            "ai": ["AI面試官", "AI小博士", "AI老師", "AI教練"],
            "self_intro": "自我介紹大師",
            "logic": "邏輯高手",
            "expression": "表達達人",
            "social": "社交高手",
        }

        if data.get("opponent_type") == "user":
            opponent_name = "對手玩家"
            opponent_avatar = "👤"
            opponent_type = "user"
        else:
            opponent_name = opponent_names.get(category, opponent_names["ai"][0])
            opponent_avatar = "🤖"
            opponent_type = "ai"

        # Create match
        match = create_match(
            user_id=user_id,
            opponent_type=opponent_type,
            opponent_name=opponent_name,
            opponent_avatar=opponent_avatar,
            difficulty=difficulty,
            category=category,
            match_type=match_type,
            time_limit=time_limit if match_type == "timed" else None,
        )

        # Get questions for the match
        question_count = 10 if match_type != "timed" else 50
        questions = get_random_questions(categories=[category], limit=question_count)

        # If no questions from database, generate sample questions
        if not questions:
            questions = generate_sample_questions(category, question_count)

        # Store match in session for tracking
        session["arena_match_id"] = match["match_id"]
        session["arena_questions"] = questions
        session["arena_current_q"] = 0
        session["arena_score"] = 0
        session["arena_correct"] = 0
        session["arena_start_time"] = datetime.now().isoformat()

        return jsonify(
            {
                "success": True,
                "data": {
                    "match_id": match["match_id"],
                    "opponent": {
                        "type": opponent_type,
                        "name": opponent_name,
                        "avatar": opponent_avatar,
                        "difficulty": difficulty,
                    },
                    "category": category,
                    "match_type": match_type,
                    "time_limit": time_limit if match_type == "timed" else None,
                    "question_count": len(questions),
                    "questions": questions[:5],  # Send first 5 questions
                    "start_time": match["started_at"].isoformat()
                    if match.get("started_at")
                    else datetime.now().isoformat(),
                },
            }
        )
    except Exception as e:
        print(f"Error starting arena match: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/arena/answer", methods=["POST"])
@login_required
def api_arena_answer():
    """Submit answer for a question."""
    try:
        from services.arena_service import get_match

        user_id = session.get("user_id")
        data = request.get_json() or {}

        match_id = data.get("match_id")
        question_id = data.get("question_id")
        answer = data.get("answer")
        time_spent = data.get("time_spent", 0)

        if not match_id or not answer:
            return jsonify({"success": False, "error": "缺少必要參數"}), 400

        # Get questions from session
        questions = session.get("arena_questions", [])
        current_q = session.get("arena_current_q", 0)

        # Find the question
        question = None
        for q in questions:
            if str(q.get("id")) == str(question_id):
                question = q
                break

        if not question:
            return jsonify({"success": False, "error": "題目不存在"}), 400

        # Check answer
        correct_answer = question.get("correct_answer", "").upper()
        is_correct = answer.upper() == correct_answer

        # Update score
        score = session.get("arena_score", 0)
        correct = session.get("arena_correct", 0)

        if is_correct:
            score += 10
            correct += 1

        session["arena_score"] = score
        session["arena_correct"] = correct
        session["arena_current_q"] = current_q + 1

        return jsonify(
            {
                "success": True,
                "data": {
                    "correct": is_correct,
                    "correct_answer": correct_answer,
                    "explanation": question.get("explanation", ""),
                    "score": score,
                    "running_score": score,
                    "correct_count": correct,
                    "remaining_questions": len(questions) - current_q - 1,
                },
            }
        )
    except Exception as e:
        print(f"Error submitting answer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/arena/finish", methods=["POST"])
@login_required
def api_arena_finish():
    """Finish arena match and calculate results."""
    try:
        from services.arena_service import (
            get_match,
            update_match_result,
            update_user_rank,
            add_coins,
            calculate_rewards,
            generate_ai_score,
        )

        user_id = session.get("user_id")
        data = request.get_json() or {}

        match_id = data.get("match_id")

        if not match_id:
            return jsonify({"success": False, "error": "缺少對戰ID"}), 400

        # Get match details
        match = get_match(match_id)
        if not match:
            return jsonify({"success": False, "error": "對戰不存在"}), 400

        # Get user's answers/results
        user_score = session.get("arena_score", 0)
        user_correct = session.get("arena_correct", 0)
        questions = session.get("arena_questions", [])
        user_total = len(questions)

        # Calculate duration
        start_time = session.get("arena_start_time")
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            duration = int((datetime.now() - start_dt).total_seconds())
        else:
            duration = 0

        # Generate AI score
        opponent_score, opponent_correct, opponent_total = generate_ai_score(
            match["difficulty"], user_correct, user_total
        )

        # Determine result
        if user_score > opponent_score:
            result = "win"
        elif user_score < opponent_score:
            result = "lose"
        else:
            result = "draw"

        # Get current streak before update
        from services.arena_service import get_or_create_user_rank

        rank_data = get_or_create_user_rank(user_id)
        current_streak = rank_data["current_streak"]

        # Calculate rewards
        rewards = calculate_rewards(
            user_id=user_id,
            match_type=match["match_type"],
            result=result,
            difficulty=match["difficulty"],
            user_correct=user_correct,
            user_total=user_total,
            current_streak=current_streak + (1 if result == "win" else 0),
        )

        # Update match result
        updated_match = update_match_result(
            match_id=match_id,
            user_score=user_score,
            user_correct=user_correct,
            user_total=user_total,
            opponent_score=opponent_score,
            opponent_correct=opponent_correct,
            opponent_total=opponent_total,
            result=result,
            points_earned=rewards["points"],
            coins_earned=rewards["coins"],
            duration=duration,
            badges_earned=rewards["badges"],
        )

        # Update user rank
        updated_rank = update_user_rank(
            user_id=user_id,
            points_change=rewards["points"],
            win=(result == "win") if result != "draw" else None,
        )

        # Add coins
        coin_result = add_coins(
            user_id=user_id,
            amount=rewards["coins"],
            transaction_type=f"match_{result}",
            reference_id=match_id,
        )

        # Get updated user rank info
        from services.arena_service import get_rank_config

        rank_config = get_rank_config(updated_rank["current_rank"])

        # Get user coins
        from services.arena_service import get_or_create_user_coins

        coins_data = get_or_create_user_coins(user_id)

        # Clear session
        session.pop("arena_match_id", None)
        session.pop("arena_questions", None)
        session.pop("arena_current_q", None)
        session.pop("arena_score", None)
        session.pop("arena_correct", None)
        session.pop("arena_start_time", None)

        return jsonify(
            {
                "success": True,
                "data": {
                    "result": result,
                    "user_score": user_score,
                    "opponent_score": opponent_score,
                    "user_correct": user_correct,
                    "user_total": user_total,
                    "accuracy": f"{int(user_correct / user_total * 100) if user_total > 0 else 0}%",
                    "duration": duration,
                    "rewards": {
                        "points_earned": rewards["points"],
                        "points_total": updated_rank["rank_points"],
                        "coins_earned": rewards["coins"],
                        "coins_balance": coin_result["balance"],
                        "badges": rewards["badges"],
                    },
                    "rank_info": {
                        "current_rank": updated_rank["current_rank"],
                        "rank_name": rank_config["rank_name_zh"]
                        if rank_config
                        else "青銅",
                        "rank_icon": rank_config["rank_icon"] if rank_config else "🥉",
                    },
                },
            }
        )
    except Exception as e:
        print(f"Error finishing arena match: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/arena/leaderboard", methods=["GET"])
@login_required
def api_arena_leaderboard():
    """Get arena leaderboard."""
    try:
        from services.arena_service import get_leaderboard

        period = request.args.get("period", "weekly")
        limit = int(request.args.get("limit", 50))

        user_id = session.get("user_id")
        leaderboard_data = get_leaderboard(period, limit)

        # Find user's rank
        user_rank = None
        for entry in leaderboard_data["data"]:
            if entry["user_id"] == user_id:
                user_rank = entry
                break

        return jsonify(
            {
                "success": True,
                "data": {
                    "period": leaderboard_data["period"],
                    "period_label": f"{leaderboard_data['period_start']} - {leaderboard_data['period_end']}",
                    "user_rank": user_rank,
                    "top_players": leaderboard_data["data"][:10],
                    "updated_at": leaderboard_data["updated_at"],
                },
            }
        )
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/arena/history", methods=["GET"])
@login_required
def api_arena_history():
    """Get user's arena match history."""
    try:
        from services.arena_service import get_match_history, get_or_create_user_rank

        user_id = session.get("user_id")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        filter_type = request.args.get("filter", "all")

        history = get_match_history(user_id, page, limit, filter_type)

        # Get overall stats
        rank_data = get_or_create_user_rank(user_id)

        # Calculate avg score
        avg_score = 0
        if history["matches"]:
            total_score = sum(m["user_score"] or 0 for m in history["matches"])
            avg_score = int(total_score / len(history["matches"]))

        best_score = 0
        if history["matches"]:
            best_score = max(m["user_score"] or 0 for m in history["matches"])

        return jsonify(
            {
                "success": True,
                "data": {
                    "matches": history["matches"],
                    "pagination": history["pagination"],
                    "statistics": {
                        "total_matches": rank_data["total_matches"],
                        "wins": rank_data["wins"],
                        "losses": rank_data["losses"],
                        "avg_score": avg_score,
                        "best_score": best_score,
                    },
                },
            }
        )
    except Exception as e:
        print(f"Error getting arena history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/arena/home", methods=["GET"])
@login_required
def api_arena_home():
    """Get arena home data."""
    try:
        from services.arena_service import get_arena_home_data

        user_id = session.get("user_id")
        data = get_arena_home_data(user_id)

        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"Error getting arena home: {e}")
        return jsonify({"error": str(e)}), 500


def generate_sample_questions(category, count):
    """Generate sample questions for arena."""
    questions_db = {
        "self_intro": [
            {
                "id": 1,
                "question": "請介紹你自己？",
                "question_en": "Please introduce yourself",
                "options": [
                    {"id": "A", "text": "我叫小明，今年6歲..."},
                    {"id": "B", "text": "我喜歡玩玩具車..."},
                    {"id": "C", "text": "我最喜歡上學的日子..."},
                    {"id": "D", "text": "我的好朋友是小華..."},
                ],
                "correct_answer": "A",
                "explanation": "自我介紹應該先說明自己的姓名和年齡。",
            },
            {
                "id": 2,
                "question": "你最喜歡什麼？",
                "question_en": "What do you like most?",
                "options": [
                    {"id": "A", "text": "我喜歡畫畫..."},
                    {"id": "B", "text": "我不喜歡上學..."},
                    {"id": "C", "text": "我最討厭吃飯..."},
                    {"id": "D", "text": "我不喜歡和朋友玩..."},
                ],
                "correct_answer": "A",
                "explanation": "回答應該積極正面。",
            },
            {
                "id": 3,
                "question": "你長大後想做什麼？",
                "question_en": "What do you want to be when you grow up?",
                "options": [
                    {"id": "A", "text": "我想做醫生..."},
                    {"id": "B", "text": "我不想長大..."},
                    {"id": "C", "text": "我不知道..."},
                    {"id": "D", "text": "隨便啦..."},
                ],
                "correct_answer": "A",
                "explanation": "回答應該展現夢想和目標。",
            },
            {
                "id": 4,
                "question": "你最擅長什麼？",
                "question_en": "What are you best at?",
                "options": [
                    {"id": "A", "text": "我最擅長畫畫..."},
                    {"id": "B", "text": "我甚麼都不擅長..."},
                    {"id": "C", "text": "我不懂..."},
                    {"id": "D", "text": "我沒有擅長的..."},
                ],
                "correct_answer": "A",
                "explanation": "應該自信地展示自己的優點。",
            },
            {
                "id": 5,
                "question": "你喜歡上學嗎？",
                "question_en": "Do you like going to school?",
                "options": [
                    {"id": "A", "text": "喜歡！因為可以學新知識..."},
                    {"id": "B", "text": "不喜歡，因為要早起..."},
                    {"id": "C", "text": "一般般..."},
                    {"id": "D", "text": "討厭上學..."},
                ],
                "correct_answer": "A",
                "explanation": "積極正面的回答會給面試官好印象。",
            },
            {
                "id": 6,
                "question": "你的好朋友是誰？",
                "question_en": "Who is your best friend?",
                "options": [
                    {"id": "A", "text": "我的好朋友是小華，我們一起玩..."},
                    {"id": "B", "text": "我沒有好朋友..."},
                    {"id": "C", "text": "很多人都是我的朋友..."},
                    {"id": "D", "text": "我不喜歡交朋友..."},
                ],
                "correct_answer": "A",
                "explanation": "具體說明朋友是誰，做什麼活動。",
            },
            {
                "id": 7,
                "question": "你喜歡什麼顏色？",
                "question_en": "What color do you like?",
                "options": [
                    {"id": "A", "text": "我喜歡藍色，因為像天空..."},
                    {"id": "B", "text": "我沒有特別喜歡..."},
                    {"id": "C", "text": "顏色不重要..."},
                    {"id": "D", "text": "我討厭所有顏色..."},
                ],
                "correct_answer": "A",
                "explanation": "可以加上一點理由讓回答更完整。",
            },
            {
                "id": 8,
                "question": "你最喜歡什麼動物？",
                "question_en": "What animal do you like best?",
                "options": [
                    {"id": "A", "text": "我最喜歡小狗，因為牠很可愛..."},
                    {"id": "B", "text": "我沒有喜歡的動物..."},
                    {"id": "C", "text": "動物都一樣..."},
                    {"id": "D", "text": "我害怕動物..."},
                ],
                "correct_answer": "A",
                "explanation": "說明理由讓回答更有說服力。",
            },
            {
                "id": 9,
                "question": "假日你會做什麼？",
                "question_en": "What do you do on holidays?",
                "options": [
                    {"id": "A", "text": "假日我會和家人去公園玩..."},
                    {"id": "B", "text": "假日我都在睡覺..."},
                    {"id": "C", "text": "假日很無聊..."},
                    {"id": "D", "text": "我討厭假日..."},
                ],
                "correct_answer": "A",
                "explanation": "展示你的興趣和愛好。",
            },
            {
                "id": 10,
                "question": "你在家都做什麼？",
                "question_en": "What do you do at home?",
                "options": [
                    {"id": "A", "text": "我會看書、畫畫、玩玩具..."},
                    {"id": "B", "text": "我都在看電視..."},
                    {"id": "C", "text": "我甚麼都不做..."},
                    {"id": "D", "text": "我不喜歡待在家..."},
                ],
                "correct_answer": "A",
                "explanation": "展示多元化的興趣愛好。",
            },
        ],
        "logic": [
            {
                "id": 101,
                "question": "1 + 1 = ?",
                "options": [
                    {"id": "A", "text": "2"},
                    {"id": "B", "text": "3"},
                    {"id": "C", "text": "1"},
                    {"id": "D", "text": "0"},
                ],
                "correct_answer": "A",
                "explanation": "1加1等於2。",
            },
            {
                "id": 102,
                "question": "5 + 3 = ?",
                "options": [
                    {"id": "A", "text": "8"},
                    {"id": "B", "text": "7"},
                    {"id": "C", "text": "9"},
                    {"id": "D", "text": "6"},
                ],
                "correct_answer": "A",
                "explanation": "5加3等於8。",
            },
            {
                "id": 103,
                "question": "10 - 4 = ?",
                "options": [
                    {"id": "A", "text": "6"},
                    {"id": "B", "text": "5"},
                    {"id": "C", "text": "7"},
                    {"id": "D", "text": "4"},
                ],
                "correct_answer": "A",
                "explanation": "10減4等於6。",
            },
            {
                "id": 104,
                "question": "2 x 3 = ?",
                "options": [
                    {"id": "A", "text": "6"},
                    {"id": "B", "text": "5"},
                    {"id": "C", "text": "8"},
                    {"id": "D", "text": "4"},
                ],
                "correct_answer": "A",
                "explanation": "2乘3等於6。",
            },
            {
                "id": 105,
                "question": "哪個是紅色的？",
                "options": [
                    {"id": "A", "text": "蘋果"},
                    {"id": "B", "text": "香蕉"},
                    {"id": "C", "text": "青瓜"},
                    {"id": "D", "text": "茄子"},
                ],
                "correct_answer": "A",
                "explanation": "蘋果是紅色的。",
            },
            {
                "id": 106,
                "question": "找出不同的那個：",
                "options": [
                    {"id": "A", "text": "狗狗"},
                    {"id": "B", "text": "貓咪"},
                    {"id": "C", "text": "小鳥"},
                    {"id": "D", "text": "魚"},
                ],
                "correct_answer": "C",
                "explanation": "鳥是天上跑的，其他是寵物。",
            },
            {
                "id": 107,
                "question": "7 + 8 = ?",
                "options": [
                    {"id": "A", "text": "15"},
                    {"id": "B", "text": "14"},
                    {"id": "C", "text": "16"},
                    {"id": "D", "text": "13"},
                ],
                "correct_answer": "A",
                "explanation": "7加8等於15。",
            },
            {
                "id": 108,
                "question": "哪個圖形是圓的？",
                "options": [
                    {"id": "A", "text": "氣球"},
                    {"id": "B", "text": "書"},
                    {"id": "C", "text": "門"},
                    {"id": "D", "text": "枱"},
                ],
                "correct_answer": "A",
                "explanation": "氣球是圓形的。",
            },
            {
                "id": 109,
                "question": "12 - 5 = ?",
                "options": [
                    {"id": "A", "text": "7"},
                    {"id": "B", "text": "6"},
                    {"id": "C", "text": "8"},
                    {"id": "D", "text": "5"},
                ],
                "correct_answer": "A",
                "explanation": "12減5等於7。",
            },
            {
                "id": 110,
                "question": "哪個是水果？",
                "options": [
                    {"id": "A", "text": "橙"},
                    {"id": "B", "text": "紅蘿蔔"},
                    {"id": "C", "text": "西蘭花"},
                    {"id": "D", "text": "薯仔"},
                ],
                "correct_answer": "A",
                "explanation": "橙是水果，其他是蔬菜。",
            },
        ],
        "expression": [
            {
                "id": 201,
                "question": "如果有人摔倒，你會怎樣？",
                "options": [
                    {"id": "A", "text": "上前扶起他..."},
                    {"id": "B", "text": "笑他..."},
                    {"id": "C", "text": "走開..."},
                    {"id": "D", "text": "不知道..."},
                ],
                "correct_answer": "A",
                "explanation": "應該表現出關心和幫助。",
            },
            {
                "id": 202,
                "question": "你會怎樣介紹自己？",
                "options": [
                    {"id": "A", "text": "大家好，我叫..."},
                    {"id": "B", "text": "我不想說..."},
                    {"id": "C", "text": "隨便啦..."},
                    {"id": "D", "text": "你好..."},
                ],
                "correct_answer": "A",
                "explanation": "自我介紹要有禮貌。",
            },
            {
                "id": 203,
                "question": "遇到陌生人怎麼辦？",
                "options": [
                    {"id": "A", "text": "有禮貌地打招呼..."},
                    {"id": "B", "text": "馬上跑開..."},
                    {"id": "C", "text": "大聲喊叫..."},
                    {"id": "D", "text": "不理會..."},
                ],
                "correct_answer": "A",
                "explanation": "表現禮貌和自信。",
            },
            {
                "id": 204,
                "question": "怎樣說謝謝？",
                "options": [
                    {"id": "A", "text": "多謝你！"},
                    {"id": "B", "text": "嗯..."},
                    {"id": "C", "text": "不用謝..."},
                    {"id": "D", "text": "好了..."},
                ],
                "correct_answer": "A",
                "explanation": "表達感謝要真誠。",
            },
            {
                "id": 205,
                "question": "別人說你好時，你會？",
                "options": [
                    {"id": "A", "text": "說多謝，也讚回對方..."},
                    {"id": "B", "text": "不接受..."},
                    {"id": "C", "text": "不說話..."},
                    {"id": "D", "text": "說我不好..."},
                ],
                "correct_answer": "A",
                "explanation": "謙虛地接受讚美。",
            },
            {
                "id": 206,
                "question": "你想借玩具，怎樣說？",
                "options": [
                    {"id": "A", "text": "請問可以借我嗎？"},
                    {"id": "B", "text": "給我！"},
                    {"id": "C", "text": "我要！"},
                    {"id": "D", "text": "不理會..."},
                ],
                "correct_answer": "A",
                "explanation": "請求時要有禮貌。",
            },
            {
                "id": 207,
                "question": "排隊時應該？",
                "options": [
                    {"id": "A", "text": "排好隊，等候輪流..."},
                    {"id": "B", "text": "插隊..."},
                    {"id": "C", "text": "推開別人..."},
                    {"id": "D", "text": "走來走去..."},
                ],
                "correct_answer": "A",
                "explanation": "排隊是基本的社會規則。",
            },
            {
                "id": 208,
                "question": "做錯事了應該？",
                "options": [
                    {"id": "A", "text": "承認錯誤並道歉..."},
                    {"id": "B", "text": "逃避..."},
                    {"id": "C", "text": "怪別人..."},
                    {"id": "D", "text": "不承認..."},
                ],
                "correct_answer": "A",
                "explanation": "勇於承擔責任是正確的。",
            },
            {
                "id": 209,
                "question": "收到禮物時應該？",
                "options": [
                    {"id": "A", "text": "多謝並表現開心..."},
                    {"id": "B", "text": "不喜歡就黑面..."},
                    {"id": "C", "text": "不收..."},
                    {"id": "D", "text": "隨便放一邊..."},
                ],
                "correct_answer": "A",
                "explanation": "要表現出感謝和珍惜。",
            },
            {
                "id": 210,
                "question": "和老師說話時要？",
                "options": [
                    {"id": "A", "text": "有禮貌，認真聽..."},
                    {"id": "B", "text": "東張西望..."},
                    {"id": "C", "text": "大聲喊..."},
                    {"id": "D", "text": "不說話..."},
                ],
                "correct_answer": "A",
                "explanation": "尊重師長是基本的禮貌。",
            },
        ],
        "social": [
            {
                "id": 301,
                "question": "新同學來了，你會？",
                "options": [
                    {"id": "A", "text": "主動打招呼並一起玩..."},
                    {"id": "B", "text": "欺負他..."},
                    {"id": "C", "text": "不理的..."},
                    {"id": "D", "text": "笑他..."},
                ],
                "correct_answer": "A",
                "explanation": "應該友善地接納新朋友。",
            },
            {
                "id": 302,
                "question": "和朋友吵架了怎麼辦？",
                "options": [
                    {"id": "A", "text": "冷靜後和好..."},
                    {"id": "B", "text": "永遠不理他..."},
                    {"id": "C", "text": "打他..."},
                    {"id": "D", "text": "告訴家長讓他處罰..."},
                ],
                "correct_answer": "A",
                "explanation": "冷靜處理衝突是正確的。",
            },
            {
                "id": 303,
                "question": "看到同學不開心，你會？",
                "options": [
                    {"id": "A", "text": "關心並安慰他..."},
                    {"id": "B", "text": "笑他..."},
                    {"id": "C", "text": "走開..."},
                    {"id": "D", "text": "跟着他不開心..."},
                ],
                "correct_answer": "A",
                "explanation": "關心朋友是正確的。",
            },
            {
                "id": 304,
                "question": "玩的時候應該？",
                "options": [
                    {"id": "A", "text": "輪流玩，分享玩具..."},
                    {"id": "B", "text": "自己玩，不理別人..."},
                    {"id": "C", "text": "搶別人的玩具..."},
                    {"id": "D", "text": "自己玩到夠..."},
                ],
                "correct_answer": "A",
                "explanation": "分享和輪流是良好的社交行為。",
            },
            {
                "id": 305,
                "question": "別人有困難時？",
                "options": [
                    {"id": "A", "text": "盡力幫助他..."},
                    {"id": "B", "text": "取笑他..."},
                    {"id": "C", "text": "不理的..."},
                    {"id": "D", "text": "走開..."},
                ],
                "correct_answer": "A",
                "explanation": "幫助他人是正確的。",
            },
            {
                "id": 306,
                "question": "在公共場所要？",
                "options": [
                    {"id": "A", "text": "保持安靜，守規則..."},
                    {"id": "B", "text": "大聲喧嘩..."},
                    {"id": "C", "text": "隨便跑..."},
                    {"id": "D", "text": "不理會別人..."},
                ],
                "correct_answer": "A",
                "explanation": "公共場所要守規矩。",
            },
            {
                "id": 307,
                "question": "想和朋友一起玩？",
                "options": [
                    {"id": "A", "text": "禮貌地問可以一起嗎..."},
                    {"id": "B", "text": "直接加入不打招乎..."},
                    {"id": "C", "text": "趕走他們..."},
                    {"id": "D", "text": "自己一個玩..."},
                ],
                "correct_answer": "A",
                "explanation": "邀請時要有禮貌。",
            },
            {
                "id": 308,
                "question": "吃東西時應該？",
                "options": [
                    {"id": "A", "text": "細嚼慢嚥，不放聲..."},
                    {"id": "B", "text": "大聲咀嚼..."},
                    {"id": "C", "text": "邊吃邊說..."},
                    {"id": "D", "text": "狼吞虎嚥..."},
                ],
                "correct_answer": "A",
                "explanation": "用餐禮儀是重要的社交技能。",
            },
            {
                "id": 309,
                "question": "別人生氣時你會？",
                "options": [
                    {"id": "A", "text": "等他冷靜再說..."},
                    {"id": "B", "text": "跟着生氣..."},
                    {"id": "C", "text": "刺激他..."},
                    {"id": "D", "text": "走開不管..."},
                ],
                "correct_answer": "A",
                "explanation": "要理解和體諒他人的情緒。",
            },
            {
                "id": 310,
                "question": "老師讚賞你時？",
                "options": [
                    {"id": "A", "text": "謙虛地說多謝..."},
                    {"id": "B", "text": "自大..."},
                    {"id": "C", "text": "不接受..."},
                    {"id": "D", "text": "說是應該的..."},
                ],
                "correct_answer": "A",
                "explanation": "謙虛接受讚美是正確的。",
            },
        ],
    }

    import random

    questions = questions_db.get(category, questions_db["self_intro"])
    return random.sample(questions, min(count, len(questions)))


print("Starting AI Tutor application...")
print(f"Database configured: {bool(DATABASE_URL)}")
app.run(host="0.0.0.0", port=5000, debug=True)


# ============ Parent Coach Routes ============
# 家长面试教练 - 帮助家长学习如何当面试陪练


@app.route("/parent-coach")
def parent_coach():
    """家长面试教练主页"""
    from services.parent_coach_service import get_all_categories, get_mistakes_summary

    categories = get_all_categories()
    mistakes = get_mistakes_summary()

    return render_template(
        "parent-coach.html",
        active_page="parent-coach",
        categories=categories,
        mistakes=mistakes,
    )


@app.route("/api/parent-coach/questions")
def api_parent_coach_questions():
    """获取教练题目列表"""
    from services.parent_coach_service import get_coach_questions, get_question_by_id

    question_id = request.args.get("id")

    if question_id:
        question = get_question_by_id(question_id)
        if question:
            return jsonify({"success": True, "question": question})
        return jsonify({"error": "题目不存在"}), 404

    questions = get_coach_questions()
    return jsonify({"success": True, "questions": questions})


@app.route("/api/parent-coach/session", methods=["POST"])
def api_parent_coach_session():
    """创建教练会话"""
    from services.parent_coach_service import parent_coach_session

    data = request.get_json()
    user_id = session.get("user_id", "anonymous")
    question_id = data.get("question_id")

    session_data = parent_coach_session.create_session(user_id, question_id)

    return jsonify(
        {
            "success": True,
            "session_id": session_data["session_id"],
            "question": session_data["selected_question"],
        }
    )


@app.route("/api/parent-coach/session/<session_id>", methods=["GET"])
def api_parent_coach_session_get(session_id):
    """获取教练会话"""
    from services.parent_coach_service import parent_coach_session

    session_data = parent_coach_session.get_session(session_id)

    if not session_data:
        return jsonify({"error": "会话不存在"}), 404

    return jsonify({"success": True, "session": session_data})


@app.route("/api/parent-coach/practice", methods=["POST"])
def api_parent_coach_practice():
    """提交练习并获取反馈"""
    from services.parent_coach_service import parent_coach_session

    data = request.get_json()
    session_id = data.get("session_id")
    parent_words = data.get("parent_words")

    if not session_id or not parent_words:
        return jsonify({"error": "缺少必要参数"}), 400

    session_data = parent_coach_session.get_session(session_id)
    if not session_data:
        return jsonify({"error": "会话不存在"}), 404

    result = parent_coach_session.record_practice(session_id, parent_words)

    return jsonify({"success": True, "evaluation": result["evaluation"]})


@app.route("/api/parent-coach/finish", methods=["POST"])
def api_parent_coach_finish():
    """完成教练会话"""
    from services.parent_coach_service import parent_coach_session

    data = request.get_json()
    session_id = data.get("session_id")

    result = parent_coach_session.finish_session(session_id)

    if not result:
        return jsonify({"error": "会话不存在"}), 404

    return jsonify({"success": True, "session": result})


@app.route("/api/parent-coach/mistakes")
def api_parent_coach_mistakes():
    """获取常见误区"""
    from services.parent_coach_service import get_mistakes_summary

    mistakes = get_mistakes_summary()
    return jsonify({"success": True, "mistakes": mistakes})


# ============ Debug Routes ============


@app.route("/debug/tts")
def debug_tts():
    """Debug TTS configuration"""
    import os

    return jsonify(
        {
            "MINIMAX_API_KEY": "set" if os.getenv("MINIMAX_API_KEY") else "missing",
            "MINIMAX_BASE_URL": os.getenv("MINIMAX_BASE_URL", "not set"),
            "MINIMAX_TTS_BASE_URL": os.getenv("MINIMAX_TTS_BASE_URL", "not set"),
        }
    )


@app.route("/debug/tts/test")
def debug_tts_test():
    """Test TTS generation"""
    from services.tts_service import call_tts_api

    result = call_tts_api("你好，测试语音", voice="male-qn-qingse")
    return jsonify(
        {"success": result is not None, "audio_size": len(result) if result else 0}
    )


# ============ Growth Profile Routes (面霸成长档案) ============


@app.route("/growth-profile")
@login_required
def growth_profile_page():
    """面霸成长档案主页"""
    user_id = session.get("user_id")

    profile_data = {
        "child_name": session.get("child_name"),
        "child_age": session.get("child_age"),
        "child_gender": session.get("child_gender"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    return render_template(
        "growth-profile.html",
        profile=profile_data,
        user_id=user_id,
    )


@app.route("/growth-profile/generate-pdf")
@login_required
def generate_growth_profile_pdf():
    """生成成长档案PDF"""
    user_id = session.get("user_id")

    profile_data = {
        "child_name": session.get("child_name"),
        "child_age": session.get("child_age"),
        "child_gender": session.get("child_gender"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    try:
        from services.growth_profile_pdf import (
            generate_growth_profile_pdf as generate_pdf,
        )

        pdf_content = generate_pdf(user_id, profile_data)

        from flask import send_file, make_response
        import io

        response = make_response(pdf_content)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f"attachment; filename=growth_profile_{user_id}.pdf"
        )

        return response
    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash("PDF生成失败，请稍后重试", "error")
        return redirect(url_for("growth_profile_page"))


@app.route("/api/growth-profile", methods=["GET"])
@login_required
def api_growth_profile():
    """获取成长档案API"""
    user_id = session.get("user_id")

    profile_data = {
        "child_name": session.get("child_name"),
        "child_age": session.get("child_age"),
        "child_gender": session.get("child_gender"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    try:
        from services.growth_profile_service import get_growth_profile

        growth_profile = get_growth_profile(user_id, profile_data)

        return jsonify({"success": True, "profile": growth_profile})
    except Exception as e:
        print(f"Error getting growth profile: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/growth-profile/pdf", methods=["POST"])
@login_required
def api_growth_profile_pdf():
    """生成并返回PDF API"""
    user_id = session.get("user_id")

    profile_data = {
        "child_name": session.get("child_name"),
        "child_age": session.get("child_age"),
        "child_gender": session.get("child_gender"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    try:
        from services.growth_profile_pdf import generate_growth_profile_pdf

        pdf_content = generate_growth_profile_pdf(user_id, profile_data)

        import base64

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        return jsonify({"success": True, "pdf": pdf_base64, "message": "PDF生成成功"})
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/growth-profile/feedback", methods=["POST"])
@login_required
def api_growth_profile_feedback():
    """获取个性化成长评语"""
    user_id = session.get("user_id")

    profile_data = {
        "child_name": session.get("child_name"),
        "child_age": session.get("child_age"),
        "child_gender": session.get("child_gender"),
        "interests": session.get("child_interests", []),
        "target_schools": session.get("target_schools", []),
    }

    try:
        from services.growth_profile_service import (
            get_growth_profile,
            generate_personalized_feedback,
        )

        growth_profile = get_growth_profile(user_id, profile_data)
        feedback = generate_personalized_feedback(growth_profile)

        return jsonify({"success": True, "feedback": feedback})
    except Exception as e:
        print(f"Error generating feedback: {e}")
        return jsonify({"error": str(e)}), 500


# ============ Parent-Child Challenge Routes ============


@app.route("/parent-child-challenge")
@login_required
def parent_child_challenge():
    """亲子共面挑战页面"""
    return render_template("parent-child-challenge.html")


@app.route("/api/parent-child-challenge/start", methods=["POST"])
@login_required
def api_parent_child_challenge_start():
    """开始新的挑战"""
    user_id = session.get("user_id")
    data = request.json
    challenge_type = data.get("challenge_type")

    if not challenge_type:
        return jsonify({"error": "挑战类型不能为空"}), 400

    try:
        from services.parent_child_challenge_service import create_challenge

        child_name = session.get("child_name", "小朋友")
        challenge = create_challenge(user_id, child_name, challenge_type)

        return jsonify({"success": True, "challenge": challenge})
    except Exception as e:
        print(f"Error starting challenge: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-child-challenge/submit", methods=["POST"])
@login_required
def api_parent_child_challenge_submit():
    """提交挑战答案并获取评分"""
    user_id = session.get("user_id")
    data = request.json
    challenge_id = data.get("challenge_id")
    parent_answer = data.get("parent_answer")
    child_answer = data.get("child_answer")

    if not challenge_id or not parent_answer or not child_answer:
        return jsonify({"error": "请填写完整答案"}), 400

    try:
        from services.parent_child_challenge_service import (
            update_challenge_answer,
            complete_challenge,
            analyze_chemistry,
            save_challenge_score,
        )
        from services.parent_child_challenge_service import CHALLENGE_LEVELS

        # 更新家长答案
        update_challenge_answer(challenge_id, "parent", parent_answer)

        # 更新孩子答案
        update_challenge_answer(challenge_id, "child", child_answer)

        # 完成挑战
        challenge = complete_challenge(challenge_id)

        # 获取挑战详情
        from services.parent_child_challenge_service import get_challenge

        challenge = get_challenge(challenge_id)

        # AI 分析默契度
        analysis = analyze_chemistry(
            parent_answer,
            child_answer,
            challenge["challenge_type"],
            challenge["question"],
        )

        # 保存评分
        score_result = save_challenge_score(challenge_id, user_id, analysis)

        # 准备返回数据
        chemistry_level = analysis.get("chemistry_score", 0)
        if chemistry_level >= 90:
            chemistry_level_name = "钻石"
        elif chemistry_level >= 75:
            chemistry_level_name = "金牌"
        elif chemistry_level >= 60:
            chemistry_level_name = "银牌"
        else:
            chemistry_level_name = "铜牌"

        score_data = {
            "chemistry_score": analysis.get("chemistry_score", 0),
            "chemistry_level": analysis.get("chemistry_level", "bronze"),
            "chemistry_level_name": chemistry_level_name,
            "similarity_score": analysis.get("similarity_score", 0),
            "cooperation_score": analysis.get("cooperation_score", 0),
            "communication_score": analysis.get("communication_score", 0),
            "creativity_score": analysis.get("creativity_score", 0),
            "ai_analysis": analysis.get("ai_analysis", ""),
            "parent_feedback": analysis.get("parent_feedback", ""),
            "strengths": analysis.get("strengths", []),
            "improvements": analysis.get("improvements", []),
        }

        return jsonify(
            {
                "success": True,
                "score": score_data,
                "badges_earned": score_result.get("badges_earned", []),
            }
        )
    except Exception as e:
        print(f"Error submitting challenge: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-child-challenge/leaderboard", methods=["GET"])
@login_required
def api_parent_child_challenge_leaderboard():
    """获取排行榜"""
    try:
        from services.parent_child_challenge_service import get_leaderboard

        leaderboard = get_leaderboard(period_type="all_time", limit=50)
        return jsonify({"success": True, "leaderboard": leaderboard})
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/parent-child-challenge/badges", methods=["GET"])
@login_required
def api_parent_child_challenge_badges():
    """获取用户勋章"""
    user_id = session.get("user_id")

    try:
        from services.parent_child_challenge_service import get_user_badges

        badges = get_user_badges(user_id)
        return jsonify({"success": True, "badges": badges})
    except Exception as e:
        print(f"Error getting badges: {e}")
        return jsonify({"error": str(e)}), 500
