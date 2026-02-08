"""
AI Tutor - Web POC Application
Flask-based web application for personalized primary school interview preparation.
"""

import os
import sys
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
            create_child_profile, get_child_profile_by_user_id,
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
PUBLIC_ROUTES = ['/', '/login', '/signup', '/auth/google', '/auth/google/callback', '/unlock-full-access']


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
        existing_user = db['get_user_by_email'](email)
        if existing_user:
            # User exists, load their session
            load_user_session(existing_user['id'])
            flash('Welcome back!', 'success')
        else:
            # Create new user in database
            user = db['create_user'](
                email=email,
                name=email.split('@')[0],
                user_type='email'
            )
            load_user_session(user['id'])

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

            # Get database functions
            db = get_db_functions()
            if not db:
                flash('Database is not configured. Please contact support.', 'error')
                return redirect(url_for('login'))

            # Check if user already exists
            existing_user = db['get_user_by_email'](email)
            if existing_user:
                # User exists, load their session
                load_user_session(existing_user['id'])
            elif db['get_user_by_google_id'](google_id):
                # User exists with Google ID, load session
                load_user_session(db['get_user_by_google_id'](google_id)['id'])
            else:
                # Create new user in database
                user = db['create_user'](
                    email=email,
                    name=user_info.get('name'),
                    picture=user_info.get('picture'),
                    user_type='google',
                    google_id=google_id
                )
                load_user_session(user['id'])

            flash(f'Welcome, {session.get("name")}!', 'success')

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

        if profile:
            # Update existing profile
            profile = db['create_child_profile'](
                user_id=user_id,
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
    selected_interests = session.get('child_interests', [])

    if request.method == 'POST':
        selected_interests = request.form.getlist('interests')

        db = get_db_functions()
        if db and profile_id:
            db['set_user_interests'](profile_id, selected_interests)

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
    selected_schools = session.get('target_schools', [])

    if request.method == 'POST':
        target_schools = request.form.getlist('target_schools')

        db = get_db_functions()
        if db and profile_id:
            db['set_target_schools'](profile_id, target_schools)

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
    """API endpoint for generating AI content."""
    data = request.json
    topic = data.get('topic')
    profile_id = data.get('profile_id')

    # Mock response - in production, call MiniMax API
    content = {
        'teaching_goal': '教小朋友自信地介紹自己的特點，展示個性。',
        'parent_script': '家長可以先問：「寶寶，你最鍾意做咩呀？」然後引導佢講多啲細節...',
        'sample_questions': [
            '你叫咩名？今年幾歲？',
            '你最鍾意玩咩玩具？點解鍾意？',
            '你有咩特別既地方？'
        ],
        'model_answer': '我叫小明，今年 5 歲。我最鍾意砌 Lego 同埋恐龍，因為我想做建築師...',
        'tips': [
            '望住對方眼睛，唔好望地下',
            '講大聲啲、清楚啲',
            '可以加入自己既特點，例如：「我記性好好」'
        ]
    }

    return jsonify(content)


@app.route('/unlock-full-access')
@login_required
def unlock_full_access():
    """Paywall page for unlocking full access."""
    return render_template('unlock-full-access.html')


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


if __name__ == '__main__':
    print("Starting AI Tutor application...")
    print(f"Database configured: {bool(DATABASE_URL)}")
    app.run(host='0.0.0.0', port=5000, debug=True)
