"""
AI Tutor - Web POC Application
Flask-based web application for personalized primary school interview preparation.
"""

import os
import sys
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
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
app.secret_key = os.getenv('SECRET_KEY') or os.urandom(32).hex()

# Initialize DotEnv for environment variables (this reads from .env file)
env = DotEnv()
env.init_app(app, verbose_mode=False)

# Force reload environment variables from system/Render
os.environ.update(os.environ)

# Database URL - must be read from environment
DATABASE_URL = os.getenv('DATABASE_URL', '')

if not DATABASE_URL:
    print("WARNING: DATABASE_URL environment variable is not set!")
    print("Database operations will fail until DATABASE_URL is configured.")
    print("Please set DATABASE_URL in your environment or .env file.")


def get_db_functions():
    """Lazy import database functions."""
    try:
        from db.database import (
            create_user, get_user_by_email, get_user_by_google_id, get_user_by_id,
            create_child_profile, get_child_profile_by_user_id, update_child_profile,
            set_user_interests, get_user_interests,
            set_target_schools, get_target_schools,
            create_complete_profile
        )
        return {
            'create_user': create_user,
            'get_user_by_email': get_user_by_email,
            'get_user_by_google_id': get_user_by_google_id,
            'get_user_by_id': get_user_by_id,
            'create_child_profile': create_child_profile,
            'get_child_profile_by_user_id': get_child_profile_by_user_id,
            'update_child_profile': update_child_profile,
            'set_user_interests': set_user_interests,
            'get_user_interests': get_user_interests,
            'set_target_schools': set_target_schools,
            'get_target_schools': get_target_schools,
            'create_complete_profile': create_complete_profile
        }
    except Exception as e:
        print(f"Error importing database functions: {e}")
        return None


# Configure OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'  # Force HTTPS in production
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

# Scopes for Google OAuth
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# Routes that don't require authentication
PUBLIC_ROUTES = ['/', '/login', '/signup', '/auth/google', '/auth/google/callback', '/unlock-full-access', '/mock-interview', '/mock-interview/start', '/mock-interview/result', '/school-advisor', '/school-advisor/analyze']


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to continue', 'warning')
            return redirect(url_for('login', next=request.full_path))
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
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    return flow


def get_user_info(access_token):
    """Fetch user info from Google API."""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
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
    user = db['get_user_by_id'](user_id)
    if not user:
        return False

    # Store user info in session
    session['logged_in'] = True
    session['user_id'] = user['id']
    session['email'] = user['email']
    session['name'] = user.get('name')
    session['picture'] = user.get('picture')
    session['user_type'] = user['user_type']

    # Get child profile
    profile = db['get_child_profile_by_user_id'](user_id)
    if profile:
        session['profile_id'] = profile['id']
        session['child_name'] = profile['child_name']
        session['child_age'] = profile['child_age']
        session['child_gender'] = profile.get('child_gender')
        session['profile_complete'] = profile['profile_complete']

        # Get interests
        interests = db['get_user_interests'](profile['id'])
        session['child_interests'] = [i['id'] for i in interests]

        # Get target schools
        schools = db['get_target_schools'](profile['id'])
        session['target_schools'] = [s['id'] for s in schools]

    return True


@app.before_request
def require_login():
    """Check if user is logged in for protected routes."""
    # Allow public routes
    if request.path in PUBLIC_ROUTES:
        return

    # Check if user is logged in
    if not session.get('logged_in'):
        # Store the original URL for redirect after login
        if request.is_json:
            return jsonify({'error': 'Unauthorized', 'message': 'Please log in'}), 401
        return redirect(url_for('login', next=request.full_path))


@app.route('/')
def index():
    """Welcome/Landing page."""
    return render_template('welcome.html')


@app.route('/favicon.ico')
def favicon():
    """Return empty response for favicon to avoid 404."""
    return '', 204


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login selection page."""
    # If already logged in, redirect to dashboard
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    next_url = request.args.get('next', '/dashboard')

    return render_template('login.html', next_url=next_url)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page."""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    next_url = request.args.get('next', '/dashboard')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        next_url = request.form.get('next', '/dashboard')

        # Basic validation
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')

        # Get database functions
        db = get_db_functions()
        if not db:
            flash('Database is not configured. Please contact support.', 'error')
            return render_template('signup.html')

        # Check if user already exists
        user = db['get_user_by_email'](email)

        if not user:
            # Create new user in database
            user = db['create_user'](
                email=email,
                name=email.split('@')[0],
                user_type='email'
            )

        # Directly set session values
        session['logged_in'] = True
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['name'] = user.get('name')
        session['picture'] = user.get('picture')
        session['user_type'] = user['user_type']

        # Check for child profile
        profile = db['get_child_profile_by_user_id'](user['id'])
        if profile:
            session['profile_id'] = profile['id']
            session['child_name'] = profile['child_name']
            session['child_age'] = profile['child_age']
            session['child_gender'] = profile.get('child_gender')
            session['profile_complete'] = profile['profile_complete']

        flash('Welcome back!' if profile else 'Account created successfully!', 'success')

        # Redirect to child profile setup if profile is incomplete
        if not session.get('profile_complete'):
            return redirect(url_for('child_profile_step1'))

        return redirect(next_url)

    return render_template('signup.html', next_url=next_url)


@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow."""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    # Save the next URL to session for redirect after login
    next_url = request.args.get('next', '/dashboard')
    session['next_url'] = next_url

    flow = get_google_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/auth/google/callback')
def auth_google_callback():
    """Handle Google OAuth callback."""
    # Verify state to prevent CSRF
    state = session.get('oauth_state')
    if not state or state != request.args.get('state'):
        flash('Invalid OAuth state', 'error')
        return redirect(url_for('login'))

    try:
        flow = get_google_oauth_flow()
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        access_token = credentials.token

        # Get user info from Google
        user_info = get_user_info(access_token)

        if user_info:
            google_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name')
            picture = user_info.get('picture')

            # Get database functions
            db = get_db_functions()
            if not db:
                flash('Database is not configured. Please contact support.', 'error')
                return redirect(url_for('login'))

            # Check if user already exists
            user = db['get_user_by_email'](email)
            if not user:
                user = db['get_user_by_google_id'](google_id)

            if not user:
                # Create new user in database
                user = db['create_user'](
                    email=email,
                    name=name,
                    picture=picture,
                    user_type='google',
                    google_id=google_id
                )

            # Directly set session values
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['name'] = user.get('name')
            session['picture'] = user.get('picture')
            session['user_type'] = user['user_type']

            # Check for child profile
            profile = db['get_child_profile_by_user_id'](user['id'])
            if profile:
                session['profile_id'] = profile['id']
                session['child_name'] = profile['child_name']
                session['child_age'] = profile['child_age']
                session['child_gender'] = profile.get('child_gender')
                session['profile_complete'] = profile['profile_complete']

                # Get interests
                interests = db['get_user_interests'](profile['id'])
                session['child_interests'] = [i['id'] for i in interests]

                # Get target schools
                schools = db['get_target_schools'](profile['id'])
                session['target_schools'] = [s['id'] for s in schools]

            flash(f'Welcome, {name}!', 'success')

            # Redirect to child profile setup if profile is incomplete
            if not session.get('profile_complete'):
                return redirect(url_for('child_profile_step1'))

            # Redirect to intended URL or dashboard
            next_url = session.pop('next_url', None)
            if not next_url or next_url == '/':
                next_url = '/dashboard'
            return redirect(next_url)
        else:
            flash('Failed to get user information', 'error')
            return redirect(url_for('login'))

    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Log out the user."""
    # Clear session
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/child-profile/step-1', methods=['GET', 'POST'])
@login_required
def child_profile_step1():
    """Child profile creation - Step 1: Basic Info."""
    db = get_db_functions()
    user_id = session.get('user_id')
    profile = db['get_child_profile_by_user_id'](user_id) if db else None

    # Pre-fill data if profile exists
    initial_data = {}
    if profile:
        initial_data = {
            'child_name': profile['child_name'],
            'child_age': profile['child_age'],
            'child_gender': profile.get('child_gender')
        }

    if request.method == 'POST':
        child_name = request.form.get('child_name')
        child_age = request.form.get('child_age')
        child_gender = request.form.get('child_gender')

        # Validate input
        if not child_name or not child_age or not child_gender:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('child_profile_step1'))

        if not db:
            # Mock profile for development (no database)
            session['child_name'] = child_name
            session['child_age'] = child_age
            session['child_gender'] = child_gender
            session['profile_id'] = f'mock_{user_id}'
            flash('Profile saved! (Development mode)', 'success')
            return redirect(url_for('child_profile_step2'))

        try:
            if profile:
                # Update existing profile
                profile = db['update_child_profile'](
                    profile_id=profile['id'],
                    child_name=child_name,
                    child_age=child_age,
                    child_gender=child_gender
                )
            else:
                # Create new profile
                profile = db['create_child_profile'](
                    user_id=user_id,
                    child_name=child_name,
                    child_age=child_age,
                    child_gender=child_gender
                )
        except Exception as e:
            print(f"Database error in child_profile_step1: {e}")
            import traceback
            traceback.print_exc()
            flash('Failed to save profile. Please try again or contact support.', 'error')
            return redirect(url_for('child_profile_step1'))

        # Update session
        session['child_name'] = child_name
        session['child_age'] = child_age
        session['child_gender'] = child_gender
        session['profile_id'] = profile['id']

        flash('Profile saved!', 'success')
        return redirect(url_for('child_profile_step2'))

    return render_template('child-profile-step-1.html', initial_data=initial_data)


@app.route('/child-profile/step-2', methods=['GET', 'POST'])
@login_required
def child_profile_step2():
    """Child profile creation - Step 2: Interests Selection."""
    interests = [
        {'id': 'dinosaurs', 'emoji': '🦕', 'name': '恐龍'},
        {'id': 'lego', 'emoji': '🧱', 'name': 'Lego'},
        {'id': 'art', 'emoji': '🎨', 'name': '畫畫'},
        {'id': 'sports', 'emoji': '⚽', 'name': '運動'},
        {'id': 'music', 'emoji': '🎵', 'name': '音樂'},
        {'id': 'reading', 'emoji': '📚', 'name': '閱讀'},
        {'id': 'science', 'emoji': '🔬', 'name': '科學'},
        {'id': 'cooking', 'emoji': '🍳', 'name': '煮飯仔'},
        {'id': 'cars', 'emoji': '🚗', 'name': '車'},
        {'id': 'planes', 'emoji': '✈️', 'name': '飛機'},
        {'id': 'animals', 'emoji': '🐶', 'name': '動物'},
        {'id': 'nature', 'emoji': '🌳', 'name': '大自然'},
        {'id': 'performing', 'emoji': '🎭', 'name': '表演'},
        {'id': 'gaming', 'emoji': '🎮', 'name': '遊戲'},
        {'id': 'swimming', 'emoji': '🏊', 'name': '游泳'},
    ]

    profile_id = session.get('profile_id')

    # Check if user has completed Step 1 - redirect if not
    if not profile_id:
        flash('Please complete Step 1 first to create your child profile.', 'error')
        return redirect(url_for('child_profile_step1'))

    selected_interests = session.get('child_interests', [])

    if request.method == 'POST':
        # Support both getlist (multiple values) and comma-separated string
        interests_value = request.form.get('interests', '')
        if interests_value:
            # Handle comma-separated string
            selected_interests = [i.strip() for i in interests_value.split(',') if i.strip()]
        else:
            selected_interests = request.form.getlist('interests')

        db = get_db_functions()
        if db and profile_id:
            try:
                db['set_user_interests'](profile_id, selected_interests)
            except Exception as e:
                print(f"Database error in child_profile_step2: {e}")
                import traceback
                traceback.print_exc()
                flash('Failed to save interests. Please try again or contact support.', 'error')
                return redirect(url_for('child_profile_step2'))

        session['child_interests'] = selected_interests
        flash('Interests saved!', 'success')
        return redirect(url_for('child_profile_step3'))

    return render_template('child-profile-step-2.html', interests=interests, selected_interests=selected_interests)


@app.route('/child-profile/step-3', methods=['GET', 'POST'])
@login_required
def child_profile_step3():
    """Child profile creation - Step 3: Target Schools."""
    school_types = [
        {'id': 'academic', 'name': '學術型', 'examples': 'DBS/SPCC'},
        {'id': 'holistic', 'name': '全人型', 'examples': '英華/TSL'},
        {'id': 'international', 'name': '國際型', 'examples': 'CKY/港同'},
        {'id': 'traditional', 'name': '傳統名校', 'examples': 'KTS/SFA'},
    ]

    profile_id = session.get('profile_id')

    # Check if user has completed Step 1 - redirect if not
    if not profile_id:
        flash('Please complete Step 1 first to create your child profile.', 'error')
        return redirect(url_for('child_profile_step1'))

    selected_schools = session.get('target_schools', [])

    if request.method == 'POST':
        target_schools = request.form.getlist('target_schools')

        db = get_db_functions()
        if db and profile_id:
            try:
                db['set_target_schools'](profile_id, target_schools)
            except Exception as e:
                print(f"Database error in child_profile_step3: {e}")
                import traceback
                traceback.print_exc()
                flash('Failed to save target schools. Please try again or contact support.', 'error')
                return redirect(url_for('child_profile_step3'))

        session['target_schools'] = target_schools
        session['profile_complete'] = True

        flash('Profile completed successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('child-profile-step-3.html', school_types=school_types, selected_schools=selected_schools)


@app.route('/dashboard')
@login_required
def dashboard():
    """Parent dashboard page."""
    # Reload user data from database to ensure freshness
    user_id = session.get('user_id')
    if user_id:
        load_user_session(user_id)

    return render_template('dashboard.html')


@app.route('/settings')
@login_required
def settings():
    """Parent settings / console page."""
    user_id = session.get('user_id')

    # Get user subscription status
    subscription_status = 'trial'
    trial_topics_used = 0

    if user_id:
        try:
            db_funcs = get_db_functions()
            if db_funcs and 'get_user_by_id' in db_funcs:
                user = db_funcs['get_user_by_id'](user_id)
                if user:
                    subscription_status = user.get('subscription_status', 'trial')
                    trial_topics_used = user.get('trial_topics_used', 0)
        except Exception as e:
            print(f"Error fetching user: {e}")

    return render_template(
        'settings.html',
        subscription_status=subscription_status,
        trial_topics_used=trial_topics_used
    )


@app.route('/lesson')
@app.route('/lesson/')
def lesson_redirect():
    """Redirect /lesson to dashboard or default topic."""
    return redirect(url_for('dashboard'))


@app.route('/lesson/<topic_id>')
@login_required
def lesson(topic_id):
    """Lesson content page."""
    topics = {
        'self-introduction': {
            'id': 'self-introduction',
            'title': '自我介紹',
            'description': '學習自信地介紹自己的特點',
            'icon': 'person',
            'progress': 1,
            'total': 5,
        },
        'interests': {
            'id': 'interests',
            'title': '興趣愛好',
            'description': '深入探討興趣細節',
            'icon': 'star',
            'progress': 2,
            'total': 5,
        },
        'family': {
            'id': 'family',
            'title': '家庭介紹',
            'description': '家庭成員與關係',
            'icon': 'group',
            'progress': 3,
            'total': 5,
        },
        'observation': {
            'id': 'observation',
            'title': '觀察力訓練',
            'description': '圖片描述與細節觀察',
            'icon': 'visibility',
            'progress': 4,
            'total': 5,
        },
        'scenarios': {
            'id': 'scenarios',
            'title': '處境題',
            'description': '簡單情境處理',
            'icon': 'psychology',
            'progress': 5,
            'total': 5,
        },
    }

    topic = topics.get(topic_id)
    if not topic:
        return redirect(url_for('dashboard'))

    return render_template('lesson.html', topic=topic)


@app.route('/api/generate', methods=['POST'])
@login_required
def generate_content():
    """
    API endpoint for generating AI teaching content.
    Integrates with MiniMax API for text generation.
    """
    data = request.json
    topic = data.get('topic')
    force_regenerate = data.get('force_regenerate', False)

    # Get profile from session/database
    user_id = session.get('user_id')
    profile_id = session.get('profile_id')

    if not topic:
        return jsonify({'error': 'Topic is required', 'message': '請指定要生成的主題'}), 400

    # Build profile dict from session (always available)
    profile = {
        'id': profile_id or f'mock_{user_id}',
        'child_name': session.get('child_name'),
        'child_age': session.get('child_age'),
        'child_gender': session.get('child_gender'),
        'interests': session.get('child_interests', []),
        'target_schools': session.get('target_schools', [])
    }

    # Try to enhance with database data if available
    db = get_db_functions()
    if db:
        # Get from database if not in session
        if not profile['child_name']:
            try:
                child_profile = db['get_child_profile_by_user_id'](user_id)
                if child_profile:
                    profile['id'] = child_profile['id']
                    profile['child_name'] = child_profile['child_name']
                    profile['child_age'] = child_profile['child_age']
                    profile['child_gender'] = child_profile.get('child_gender')
            except Exception as e:
                print(f"Warning: Could not fetch child profile: {e}")

        if not profile['interests'] and profile.get('id'):
            try:
                interests = db['get_user_interests'](profile['id'])
                profile['interests'] = [i['id'] for i in interests]
            except Exception as e:
                print(f"Warning: Could not fetch interests: {e}")

        if not profile['target_schools'] and profile.get('id'):
            try:
                schools = db['get_target_schools'](profile['id'])
                profile['target_schools'] = [s['id'] for s in schools]
            except Exception as e:
                print(f"Warning: Could not fetch target schools: {e}")

    if not profile['child_name']:
        # Use default values for development/demo mode
        print("⚠️ Profile incomplete, using default values")
        profile['child_name'] = '小明'
        profile['child_age'] = 'K2'
        profile['child_gender'] = '不透露'
        profile['interests'] = ['lego', 'sports']
        profile['target_schools'] = ['academic']

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
            return jsonify({
                'error': 'Content generation failed',
                'message': '內容生成失敗，請稍後再試',
                'fallback': True
            }), 200

        return jsonify(content)
    except Exception as e:
        print(f"Error generating content: {e}")
        return jsonify({
            'error': 'Generation failed',
            'message': '生成內容失敗，請稍後再試'
        }), 500


@app.route('/unlock-full-access')
def unlock_full_access():
    """Paywall page for unlocking full access."""
    return render_template('unlock-full-access.html')


@app.route('/profile/edit')
@login_required
def profile_edit():
    """编辑孩子资料页面."""
    return render_template('profile-edit.html')


@app.route('/parent-notes')
@login_required
def parent_notes():
    """家长笔记页面."""
    return render_template('parent-notes.html')


@app.route('/recording')
@login_required
def recording():
    """录音练习页面."""
    return render_template('recording.html')


@app.route('/api/user')
@login_required
def get_user():
    """Get current user info."""
    return jsonify({
        'logged_in': session.get('logged_in', False),
        'name': session.get('name'),
        'email': session.get('email'),
        'picture': session.get('picture'),
        'profile_complete': session.get('profile_complete', False),
        'child_name': session.get('child_name'),
        'child_age': session.get('child_age')
    })


@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_child_profile():
    """获取孩子画像信息."""
    user_id = session.get('user_id')
    try:
        db = get_db_functions()
        if db and 'get_child_profile_by_user_id' in db:
            profile = db['get_child_profile_by_user_id'](user_id)
            if profile:
                return jsonify(profile)
        # Return mock data if no database
        return jsonify({
            'child_name': session.get('child_name'),
            'child_age': session.get('child_age'),
            'child_gender': session.get('child_gender'),
            'profile_complete': session.get('profile_complete', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/stats')
@login_required
def get_user_stats():
    """获取用户使用统计（整合 analytics + progress 服务）."""
    user_id = session.get('user_id')

    # 使用 analytics 服务
    try:
        from services.analytics import get_user_analytics, get_topic_progress
        analytics_data = get_user_analytics(user_id)
        topic_progress = get_topic_progress(user_id)
    except ImportError:
        # 回退到 mock 数据
        analytics_data = {
            'topics_completed': session.get('topics_completed', 0),
            'total_minutes': session.get('total_minutes', 0),
            'notes_created': 0,
            'feedback_submitted': 0,
            'last_active': session.get('last_active')
        }
        topic_progress = {}

    # 使用 progress 服务获取详细统计
    try:
        from services.progress import get_overall_stats, get_all_topic_summaries
        overall_stats = get_overall_stats(user_id)
        topic_summaries = get_all_topic_summaries(user_id)
    except ImportError:
        overall_stats = {
            'total_topics': 5,
            'completed_topics': analytics_data.get('topics_completed', 0),
            'completion_percent': 0,
            'total_practices': 0,
            'total_minutes': analytics_data.get('total_minutes', 0),
            'streak_days': session.get('streak_days', 0),
            'first_practice_date': None,
            'last_active': analytics_data.get('last_active')
        }
        topic_summaries = []

    stats = {
        'topics_completed': overall_stats.get('completed_topics', analytics_data.get('topics_completed', 0)),
        'total_minutes': overall_stats.get('total_minutes', analytics_data.get('total_minutes', 0)),
        'streak_days': overall_stats.get('streak_days', session.get('streak_days', 0)),
        'last_active': overall_stats.get('last_active', analytics_data.get('last_active')),
        'total_practices': overall_stats.get('total_practices', 0),
        'notes_created': analytics_data.get('notes_created', 0),
        'completion_percent': overall_stats.get('completion_percent', 0),
        'topics': topic_summaries
    }

    return jsonify(stats)


@app.route('/api/progress/start', methods=['POST'])
@login_required
def start_lesson_progress():
    """記錄練習開始."""
    user_id = session.get('user_id')
    data = request.json
    topic_id = data.get('topic_id')

    if not topic_id:
        return jsonify({'error': 'Topic ID is required'}), 400

    try:
        from services.progress import update_progress
        from services.analytics import track_event

        # 更新進度
        update_progress(user_id, topic_id, 'start')

        # 追蹤事件
        track_event(user_id, 'LESSON_START', {'topic_id': topic_id})

        return jsonify({'success': True, 'message': '練習開始記錄'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/complete', methods=['POST'])
@login_required
def complete_lesson_progress():
    """記錄練習完成."""
    user_id = session.get('user_id')
    data = request.json
    topic_id = data.get('topic_id')
    score = data.get('score')
    duration_seconds = data.get('duration_seconds')

    if not topic_id:
        return jsonify({'error': 'Topic ID is required'}), 400

    try:
        from services.progress import update_progress, mark_topic_complete
        from services.analytics import track_event

        # 更新進度
        mark_topic_complete(user_id, topic_id, score, duration_seconds)

        # 追蹤事件
        track_event(user_id, 'LESSON_COMPLETE', {
            'topic_id': topic_id,
            'score': score,
            'duration_minutes': round(duration_seconds / 60, 2) if duration_seconds else None
        })

        return jsonify({'success': True, 'message': '練習完成！'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/recommendations')
@login_required
def get_recommendations():
    """獲取練習推薦."""
    user_id = session.get('user_id')

    try:
        from services.progress import get_recommendations
        recommendations = get_recommendations(user_id)
        return jsonify({'recommendations': recommendations})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/report')
@login_required
def get_progress_report():
    """獲取進度報告."""
    user_id = session.get('user_id')

    try:
        from services.progress import generate_progress_report
        report = generate_progress_report(user_id)
        return jsonify(report)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/event', methods=['POST'])
@login_required
def track_analytics_event():
    """手動追蹤分析事件."""
    user_id = session.get('user_id')
    data = request.json

    event_type = data.get('event_type')
    properties = data.get('properties', {})

    if not event_type:
        return jsonify({'error': 'Event type is required'}), 400

    try:
        from services.analytics import track_event
        track_event(user_id, event_type, properties)
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/summary')
@login_required
def get_analytics_summary():
    """獲取用戶分析摘要."""
    user_id = session.get('user_id')

    try:
        from services.analytics import get_user_analytics
        summary = get_user_analytics(user_id)
        return jsonify(summary)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/stats/update', methods=['POST'])
@login_required
def update_user_stats():
    """更新用户使用统计."""
    data = request.json
    topic_id = data.get('topic_id')
    action = data.get('action', 'practice')
    
    # 更新 session
    if topic_id:
        topics_completed = session.get('topics_completed', 0)
        if action == 'complete':
            # 标记主题为完成
            session['topics_completed'] = topics_completed + 1
            
            # 更新最后活跃时间
            session['last_active'] = datetime.now().isoformat()
    
    return jsonify({'success': True})


# ============ Settings API ============

@app.route('/api/user/settings', methods=['GET'])
@login_required
def get_user_settings():
    """获取用户设置."""
    user_id = session.get('user_id')

    try:
        db = get_db_functions()
        if db and 'get_user_by_id' in db:
            user = db['get_user_by_id'](user_id)
            if user:
                return jsonify({
                    'language': user.get('preferred_language', 'cantonese'),
                    'notifications': {
                        'dailyReminder': user.get('notify_daily', True),
                        'newTopic': user.get('notify_new_topic', True),
                        'weeklyReport': user.get('notify_weekly', False),
                        'marketing': user.get('notify_marketing', False)
                    }
                })
    except Exception as e:
        print(f"Error fetching settings: {e}")

    # Return default settings if no database
    return jsonify({
        'language': 'cantonese',
        'notifications': {
            'dailyReminder': True,
            'newTopic': True,
            'weeklyReport': False,
            'marketing': False
        }
    })


@app.route('/api/user/settings/language', methods=['POST'])
@login_required
def update_language():
    """更新语言偏好."""
    user_id = session.get('user_id')
    data = request.json
    language = data.get('language', 'cantonese')
    
    try:
        db.update_user(user_id, preferred_language=language)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/settings/notifications', methods=['POST'])
@login_required
def update_notifications():
    """更新通知设置."""
    user_id = session.get('user_id')
    data = request.json
    setting = data.get('setting')
    value = data.get('value', False)
    
    # Map setting name to database field
    field_map = {
        'dailyReminder': 'notify_daily',
        'newTopic': 'notify_new_topic',
        'weeklyReport': 'notify_weekly',
        'marketing': 'notify_marketing'
    }
    
    field = field_map.get(setting)
    if field:
        try:
            db.update_user(user_id, **{field: value})
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid setting'}), 400


@app.route('/api/user/settings', methods=['POST'])
@login_required
def update_settings():
    """批量更新用户设置."""
    user_id = session.get('user_id')
    data = request.json
    
    try:
        update_data = {}
        
        if 'language' in data:
            update_data['preferred_language'] = data['language']
        
        if 'notifications' in data:
            notifs = data['notifications']
            update_data.update({
                'notify_daily': notifs.get('dailyReminder', True),
                'notify_new_topic': notifs.get('newTopic', True),
                'notify_weekly': notifs.get('weeklyReport', False),
                'notify_marketing': notifs.get('marketing', False)
            })
        
        if update_data:
            db.update_user(user_id, **update_data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ Parent Notes API ============

@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    """获取家长笔记列表."""
    user_id = session.get('user_id')
    
    try:
        from services.parent_notes import get_latest_notes
        limit = request.args.get('limit', 10, type=int)
        notes = get_latest_notes(user_id, limit)
        return jsonify({'notes': notes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    """创建新笔记."""
    user_id = session.get('user_id')
    data = request.json
    
    try:
        from services.parent_notes import create_note
        
        note = create_note(
            user_id=user_id,
            topic_id=data.get('topic_id'),
            content=data.get('content'),
            score=data.get('score')
        )
        
        return jsonify({'success': True, 'note': note})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/template/<topic_id>')
@login_required
def get_note_template(topic_id):
    """获取笔记模板."""
    try:
        from services.parent_notes import get_template
        template = get_template(topic_id)
        return jsonify(template)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/report')
@login_required
def get_notes_report():
    """获取练习报告."""
    user_id = session.get('user_id')
    
    try:
        from services.parent_notes import generate_practice_report
        report = generate_practice_report(user_id)
        return jsonify(report or {'message': 'No data yet'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """提交练习反馈."""
    user_id = session.get('user_id')
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('rating'):
            return jsonify({'error': 'Rating is required'}), 400
        
        # Save feedback (simplified - uses session storage for now)
        feedback_data = {
            'user_id': user_id,
            'topic_id': data.get('topic_id'),
            'rating': data.get('rating'),
            'difficulties': data.get('difficulties', []),
            'comment': data.get('comment', ''),
            'child_feeling': data.get('child_feeling'),
            'submitted_at': datetime.now().isoformat()
        }
        
        # Store in session for now (would be database in production)
        if 'feedback_history' not in session:
            session['feedback_history'] = []
        
        session['feedback_history'].insert(0, feedback_data)
        session['feedback_history'] = session['feedback_history'][:100]  # Keep last 100
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_data['submitted_at']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/history')
@login_required
def get_feedback_history():
    """获取反馈历史."""
    user_id = session.get('user_id')
    
    try:
        history = session.get('feedback_history', [])
        return jsonify({'feedback': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ 练习记录 API ============

@app.route('/api/sessions', methods=['POST'])
@login_required
def record_session():
    """记录练习会话."""
    user_id = session.get('user_id')
    data = request.json

    topic = data.get('topic')
    duration_seconds = data.get('duration_seconds')
    notes = data.get('notes')
    rating = data.get('rating')

    if not topic or not duration_seconds:
        return jsonify({'error': 'Topic and duration are required'}), 400

    try:
        from services.parent_notes import record_practice_session

        session = record_practice_session(
            user_id=user_id,
            topic=topic,
            duration_seconds=duration_seconds,
            notes=notes,
            rating=rating
        )

        return jsonify({
            'success': True,
            'session': session,
            'message': '練習記錄已保存'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions')
@login_required
def get_sessions():
    """获取用户练习记录."""
    user_id = session.get('user_id')

    try:
        from services.parent_notes import get_user_sessions, get_session_stats

        sessions = get_user_sessions(user_id)
        stats = get_session_stats(user_id)

        return jsonify({
            'success': True,
            'sessions': sessions,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ 分享功能 API ============

@app.route('/api/share/progress')
@login_required
def share_progress():
    """生成分享链接数据."""
    user_id = session.get('user_id')

    try:
        from services.analytics import get_user_analytics
        from services.progress import get_user_progress
        from services.parent_notes import get_session_stats

        analytics = get_user_analytics(user_id)
        progress = get_user_progress(user_id)
        session_stats = get_session_stats(user_id)

        # 生成分享数据
        child_name = session.get('child_name', '小朋友')
        completed_topics = progress.get('completed', [])
        streak_days = analytics.get('streak_days', 0)

        share_data = {
            'child_name': child_name,
            'topics_completed': len(completed_topics),
            'total_topics': 5,
            'streak_days': streak_days,
            'total_minutes': session_stats.get('total_minutes', 0),
            'message': f'{child_name}已經完成 {len(completed_topics)}/5 個面試主題練習！連續練習 {streak_days} 日！',
            'generated_at': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'share_data': share_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ Achievements API ============

@app.route('/api/achievements')
@login_required
def get_achievements():
    """获取用户成就信息."""
    user_id = session.get('user_id')

    try:
        from services.achievements import get_achievement_summary
        achievements = get_achievement_summary(user_id)
        return jsonify(achievements)
    except Exception as e:
        print(f"Error getting achievements: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/achievements/check', methods=['POST'])
@login_required
def check_achievements():
    """检查并更新用户成就."""
    user_id = session.get('user_id')
    data = request.json or {}
    topic_id = data.get('topic_id')

    try:
        from services.achievements import check_and_award_badges

        newly_earned = check_and_award_badges(user_id, topic_id)

        return jsonify({
            'success': True,
            'new_badges': [
                {
                    'id': b['id'],
                    'name_zh': b['name_zh'],
                    'icon_emoji': b.get('icon_emoji')
                }
                for b in newly_earned
            ]
        })
    except Exception as e:
        print(f"Error checking achievements: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/summary')
@login_required
def get_progress_summary():
    """获取学习进度摘要."""
    user_id = session.get('user_id')

    try:
        from services.achievements import get_progress_summary
        progress = get_progress_summary(user_id)
        return jsonify(progress)
    except Exception as e:
        print(f"Error getting progress summary: {e}")
        return jsonify({'error': str(e)}), 500


# ============ Learning Reports API ============

@app.route('/api/reports/weekly')
@login_required
def get_weekly_report():
    """获取本周学习报告."""
    user_id = session.get('user_id')

    try:
        from services.achievements import generate_weekly_report
        report = generate_weekly_report(user_id)
        return jsonify(report)
    except Exception as e:
        print(f"Error generating weekly report: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/monthly')
@login_required
def get_monthly_report():
    """获取本月学习报告."""
    user_id = session.get('user_id')

    try:
        from services.achievements import generate_monthly_report
        report = generate_monthly_report(user_id)
        return jsonify(report)
    except Exception as e:
        print(f"Error generating monthly report: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports')
@login_required
def get_reports():
    """获取用户学习报告列表."""
    user_id = session.get('user_id')
    report_type = request.args.get('type')

    try:
        from services.achievements import get_share_data
        from db.database import get_user_reports

        reports = get_user_reports(user_id, report_type)

        return jsonify({
            'reports': [
                {
                    'id': r['id'],
                    'report_type': r['report_type'],
                    'period_start': r['period_start'].isoformat() if r.get('period_start') else None,
                    'period_end': r['period_end'].isoformat() if r.get('period_end') else None,
                    'topics_completed': r['topics_completed'],
                    'total_practice_time': r['total_practice_time'],
                    'average_score': float(r['average_score']) if r.get('average_score') else None,
                    'streak_days': r['streak_days'],
                    'badges_earned': r['badges_earned'],
                    'generated_at': r['generated_at'].isoformat() if r.get('generated_at') else None
                }
                for r in reports
            ]
        })
    except Exception as e:
        print(f"Error getting reports: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/share/learning-progress')
@login_required
def share_learning_progress():
    """生成分享到社交媒体的学习进度数据."""
    user_id = session.get('user_id')

    try:
        from services.achievements import get_share_data
        share_data = get_share_data(user_id)

        return jsonify({
            'success': True,
            'share_data': share_data
        })
    except Exception as e:
        print(f"Error generating share data: {e}")
        return jsonify({'error': str(e)}), 500


# ============ New Pages Routes ============

@app.route('/achievements')
@login_required
def achievements_page():
    """成就徽章页面."""
    return render_template('achievements.html')


@app.route('/reports')
@login_required
def reports_page():
    """学习报告页面."""
    return render_template('reports.html')


# ============ Mock Interview Routes ============

@app.route('/mock-interview')
def mock_interview():
    """AI 模拟面试入口页."""
    return render_template('mock-interview.html')


@app.route('/mock-interview/start')
@login_required
def mock_interview_start():
    """开始模拟面试页面."""
    school_type = request.args.get('school_type', 'holistic')
    return render_template('mock-interview-start.html', school_type=school_type)


@app.route('/mock-interview/result')
@login_required
def mock_interview_result():
    """面试结果页面."""
    session_id = request.args.get('session_id')
    return render_template('mock-interview-result.html', session_id=session_id)


# ============ School Advisor Routes ============

@app.route('/school-advisor')
def school_advisor():
    """智能择校顾问入口页."""
    from services.school_advisor_service import get_school_types

    logged_in = 'user_id' in session
    school_types = get_school_types()

    return render_template(
        'school-advisor.html',
        logged_in=logged_in,
        school_types=school_types
    )


@app.route('/school-advisor/analyze')
@login_required
def school_advisor_analyze():
    """智能择校分析结果页."""
    from services.school_advisor_service import analyze_school_match

    school_type = request.args.get('school_type', 'holistic')

    # 获取用户的孩子画像
    user_id = session.get('user_id')

    # 查询孩子的画像数据
    profile_data = {
        'interests': [],
        'strengths': [],
        'personality': ''
    }

    try:
        from db.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # 尝试从children表获取
        cursor.execute(
            "SELECT interests, strengths, personality FROM children WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            profile_data['interests'] = row['interests'].split(',') if row['interests'] else []
            profile_data['strengths'] = row['strengths'].split(',') if row['strengths'] else []
            profile_data['personality'] = row['personality'] or ''

        conn.close()
    except Exception as e:
        print(f"Error fetching profile: {e}")

    # 分析匹配度
    result = analyze_school_match(profile_data, school_type)

    return render_template(
        'school-advisor-result.html',
        result=result
    )


# ============ Mock Interview API ============

@app.route('/api/mock-interview/start', methods=['POST'])
@login_required
def api_mock_interview_start():
    """开始模拟面试，生成问题."""
    data = request.json or {}
    school_type = data.get('school_type', 'holistic')
    num_questions = data.get('num_questions', 5)

    user_id = session.get('user_id')

    # Get profile from session
    profile = {
        'child_name': session.get('child_name', '小朋友'),
        'child_age': session.get('child_age', '5岁'),
        'child_gender': session.get('child_gender', '不透露'),
        'interests': session.get('child_interests', []),
        'target_schools': session.get('target_schools', [])
    }

    try:
        from services.mock_interview_service import (
            generate_mock_interview_questions,
            save_interview_session,
            SCHOOL_TYPES
        )

        # Generate questions
        questions = generate_mock_interview_questions(profile, school_type, num_questions)

        # Save session
        session_data = {
            'school_type': school_type,
            'school_type_name': SCHOOL_TYPES.get(school_type, {}).get('name', '模拟面试'),
            'questions': questions,
            'answers': [],
            'user_id': user_id
        }

        session_id = save_interview_session(user_id, session_data)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'questions': questions
        })

    except Exception as e:
        print(f"Error starting mock interview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/mock-interview/audio', methods=['POST'])
@login_required
def api_mock_interview_audio():
    """生成面试问题语音."""
    data = request.json or {}
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        from services.mock_interview_service import generate_question_audio

        audio_url = generate_question_audio(text)

        return jsonify({
            'success': True,
            'audio_url': audio_url
        })

    except Exception as e:
        print(f"Error generating audio: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mock-interview/followup', methods=['POST'])
@login_required
def api_mock_interview_followup():
    """生成追问问题."""
    data = request.json or {}
    session_id = data.get('session_id')
    question = data.get('question', '')
    answer = data.get('answer', '')

    user_id = session.get('user_id')

    # Get profile from session
    profile = {
        'child_name': session.get('child_name', '小朋友'),
        'child_age': session.get('child_age', '5岁')
    }

    try:
        from services.mock_interview_service import generate_ai_follow_up

        follow_up = generate_ai_follow_up(question, answer, profile)

        return jsonify({
            'success': True,
            'follow_up': follow_up
        })

    except Exception as e:
        print(f"Error generating follow-up: {e}")
        # Return default follow-up on error
        return jsonify({
            'success': True,
            'follow_up': '可以话多啲俾老师知吗？'
        })


@app.route('/api/mock-interview/finish', methods=['POST'])
@login_required
def api_mock_interview_finish():
    """完成面试，生成评估报告."""
    data = request.json or {}
    session_id = data.get('session_id')
    answers = data.get('answers', [])
    school_type = data.get('school_type', 'holistic')

    user_id = session.get('user_id')

    # Get profile from session
    profile = {
        'child_name': session.get('child_name', '小朋友'),
        'child_age': session.get('child_age', '5岁')
    }

    try:
        from services.mock_interview_service import (
            get_interview_session,
            evaluate_answer,
            save_interview_session,
            SCHOOL_TYPES
        )

        # Get session
        session_data = get_interview_session(user_id, session_id)

        if not session_data:
            return jsonify({'error': 'Session not found'}), 404

        # Evaluate each answer
        evaluations = []
        total_score = 0

        for answer_data in answers:
            question = answer_data.get('question', '')
            answer = answer_data.get('answer', '')

            evaluation = evaluate_answer(question, answer, profile, school_type)
            evaluations.append({
                'question': question,
                'answer': answer,
                'evaluation': evaluation
            })
            total_score += evaluation.get('score', 0)

        # Calculate average score
        avg_score = total_score // len(evaluations) if evaluations else 0

        # Update session with answers and score
        session_data['answers'] = answers
        session_data['evaluations'] = evaluations
        session_data['score'] = avg_score
        session_data['school_type'] = school_type
        session_data['school_type_name'] = SCHOOL_TYPES.get(school_type, {}).get('name', '模拟面试')

        save_interview_session(user_id, session_data)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'score': avg_score,
            'evaluations': evaluations
        })

    except Exception as e:
        print(f"Error finishing interview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/mock-interview/history', methods=['GET'])
@login_required
def api_mock_interview_history():
    """获取面试历史记录."""
    user_id = session.get('user_id')

    try:
        from services.mock_interview_service import get_interview_sessions

        sessions = get_interview_sessions(user_id, 10)

        # Convert to simple format
        history = []
        for session in sessions:
            history.append({
                'session_id': session.get('session_id'),
                'school_type_name': session.get('school_type_name', '模拟面试'),
                'score': session.get('score', 0),
                'created_at': session.get('created_at', '')
            })

        return jsonify({
            'success': True,
            'sessions': history
        })

    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mock-interview/<session_id>', methods=['GET'])
@login_required
def api_mock_interview_detail(session_id):
    """获取特定面试会话详情."""
    user_id = session.get('user_id')

    try:
        from services.mock_interview_service import get_interview_session

        session_data = get_interview_session(user_id, session_id)

        if not session_data:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'success': True,
            'session': session_data
        })

    except Exception as e:
        print(f"Error getting session: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting AI Tutor application...")
    print(f"Database configured: {bool(DATABASE_URL)}")
    app.run(host='0.0.0.0', port=5000, debug=True)
