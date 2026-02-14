"""
Arena Service - Business logic for AI Tutor Arena Challenge System
"""

import uuid
import random
import json
from datetime import datetime, timedelta
from db.database import execute_query, get_connection


# ==================== Rank Config ====================

def get_rank_config(rank_id=None):
    """Get rank configuration by rank_id or all ranks."""
    if rank_id:
        query = "SELECT * FROM rank_config WHERE rank_id = %s;"
        result = execute_query(query, (rank_id,), fetch=True)
        return result[0] if result else None
    else:
        query = "SELECT * FROM rank_config ORDER BY min_points;"
        return execute_query(query, fetch=True)


def get_rank_by_points(points):
    """Get rank configuration based on points."""
    query = "SELECT * FROM rank_config WHERE min_points <= %s AND max_points >= %s;"
    result = execute_query(query, (points, points), fetch=True)
    return result[0] if result else None


# ==================== User Rank Operations ====================

def get_or_create_user_rank(user_id):
    """Get or create user rank record."""
    # Check if user rank exists
    query = "SELECT * FROM user_rank WHERE user_id = %s;"
    result = execute_query(query, (user_id,), fetch=True)

    if result:
        return result[0]

    # Create new user rank
    query = """
        INSERT INTO user_rank (user_id, current_rank, rank_points, total_matches, wins, losses, draws, current_streak, best_streak)
        VALUES (%s, 'bronze', 0, 0, 0, 0, 0, 0, 0)
        RETURNING *;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None


def update_user_rank(user_id, points_change=0, win=None):
    """
    Update user rank based on match result.
    win: True = win, False = lose, None = draw
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Get current rank
            cursor.execute("SELECT * FROM user_rank WHERE user_id = %s;", (user_id,))
            row = cursor.fetchone()
            if not row:
                # Create new rank
                cursor.execute("""
                    INSERT INTO user_rank (user_id, current_rank, rank_points, total_matches, wins, losses, draws, current_streak, best_streak)
                    VALUES (%s, 'bronze', 0, 0, 0, 0, 0, 0, 0)
                    RETURNING *;
                """, (user_id,))
                row = cursor.fetchone()

            # Calculate new stats
            current_points = row['rank_points']
            total_matches = row['total_matches'] + 1
            wins = row['wins']
            losses = row['losses']
            draws = row['draws']
            current_streak = row['current_streak']
            best_streak = row['best_streak']

            # Update based on result
            if win is True:
                wins += 1
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            elif win is False:
                losses += 1
                current_streak = 0
            else:
                draws += 1

            # Calculate streak bonus
            streak_bonus = 0
            if win is True:
                if current_streak >= 10:
                    streak_bonus = 20
                elif current_streak >= 5:
                    streak_bonus = 10
                elif current_streak >= 3:
                    streak_bonus = 5

            new_points = max(0, current_points + points_change + streak_bonus)

            # Check for rank upgrade
            new_rank = get_rank_by_points(new_points)
            new_rank_id = new_rank['rank_id'] if new_rank else 'bronze'

            # Update user rank
            cursor.execute("""
                UPDATE user_rank
                SET rank_points = %s,
                    current_rank = %s,
                    total_matches = %s,
                    wins = %s,
                    losses = %s,
                    draws = %s,
                    current_streak = %s,
                    best_streak = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                RETURNING *;
            """, (new_points, new_rank_id, total_matches, wins, losses, draws,
                  current_streak, best_streak, user_id))

            result = cursor.fetchone()
            conn.commit()
            return result

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error updating user rank: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ==================== User Coins Operations ====================

def get_or_create_user_coins(user_id):
    """Get or create user coins record."""
    query = "SELECT * FROM user_coins WHERE user_id = %s;"
    result = execute_query(query, (user_id,), fetch=True)

    if result:
        return result[0]

    # Create new user coins
    query = """
        INSERT INTO user_coins (user_id, balance, total_earned, total_spent)
        VALUES (%s, 0, 0, 0)
        RETURNING *;
    """
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None


def add_coins(user_id, amount, transaction_type, reference_id=None):
    """Add coins to user balance and create transaction record."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Get current balance
            cursor.execute("SELECT * FROM user_coins WHERE user_id = %s;", (user_id,))
            row = cursor.fetchone()

            if not row:
                # Create new coins record
                cursor.execute("""
                    INSERT INTO user_coins (user_id, balance, total_earned, total_spent)
                    VALUES (%s, 0, 0, 0)
                    RETURNING *;
                """, (user_id,))
                row = cursor.fetchone()

            new_balance = row['balance'] + amount
            total_earned = row['total_earned'] + amount if amount > 0 else row['total_earned']

            # Update balance
            cursor.execute("""
                UPDATE user_coins
                SET balance = %s, total_earned = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                RETURNING *;
            """, (new_balance, total_earned, user_id))

            # Create transaction record
            cursor.execute("""
                INSERT INTO coin_transaction (user_id, amount, transaction_type, reference_id, balance_after)
                VALUES (%s, %s, %s, %s, %s);
            """, (user_id, amount, transaction_type, reference_id, new_balance))

            conn.commit()
            return {'balance': new_balance, 'amount': amount}

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error adding coins: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ==================== Match Operations ====================

def create_match(user_id, opponent_type='ai', opponent_name='AI面試官', opponent_avatar='🤖',
                difficulty='medium', category=None, match_type='challenge', time_limit=None):
    """Create a new arena match."""
    match_id = f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    query = """
        INSERT INTO arena_match (
            match_id, user_id, opponent_type, opponent_name, opponent_avatar,
            difficulty, category, match_type, time_limit, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'in_progress')
        RETURNING *;
    """

    result = execute_query(query, (
        match_id, user_id, opponent_type, opponent_name, opponent_avatar,
        difficulty, category, match_type, time_limit
    ), fetch=True)

    return result[0] if result else None


def get_match(match_id):
    """Get match by match_id."""
    query = "SELECT * FROM arena_match WHERE match_id = %s;"
    result = execute_query(query, (match_id,), fetch=True)
    return result[0] if result else None


def get_user_active_match(user_id):
    """Get user's active (in_progress) match."""
    query = "SELECT * FROM arena_match WHERE user_id = %s AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1;"
    result = execute_query(query, (user_id,), fetch=True)
    return result[0] if result else None


def update_match_result(match_id, user_score, user_correct, user_total,
                       opponent_score, opponent_correct, opponent_total,
                       result, points_earned, coins_earned, duration, badges_earned=None):
    """Update match with results."""
    badges_json = json.dumps(badges_earned) if badges_earned else None

    query = """
        UPDATE arena_match
        SET user_score = %s,
            user_correct = %s,
            user_total = %s,
            opponent_score = %s,
            opponent_correct = %s,
            opponent_total = %s,
            result = %s,
            points_earned = %s,
            coins_earned = %s,
            badges_earned = %s,
            duration = %s,
            status = 'completed',
            finished_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE match_id = %s
        RETURNING *;
    """

    result = execute_query(query, (
        user_score, user_correct, user_total,
        opponent_score, opponent_correct, opponent_total,
        result, points_earned, coins_earned,
        badges_json, duration, match_id
    ), fetch=True)

    return result[0] if result else None


# ==================== Leaderboard Operations ====================

def get_leaderboard(period='weekly', limit=50):
    """
    Get leaderboard for a period.
    period: 'weekly' or 'monthly'
    """
    # Check cache first
    today = datetime.now().date()

    if period == 'weekly':
        # Get start of week (Monday)
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    else:  # monthly
        start = today.replace(day=1)
        # Get end of month
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    # Check cache
    query = "SELECT * FROM leaderboard_cache WHERE period_type = %s AND period_start = %s;"
    result = execute_query(query, (period, start), fetch=True)

    if result:
        cached_data = json.loads(result[0]['rank_data'])
        return {
            'period': period,
            'period_start': str(start),
            'period_end': str(end),
            'data': cached_data,
            'updated_at': str(result[0]['updated_at'])
        }

    # Generate leaderboard from matches
    query = """
        SELECT
            u.id as user_id,
            u.name as user_name,
            u.picture as user_avatar,
            COALESCE(ur.current_rank, 'bronze') as rank_id,
            COALESCE(rc.rank_icon, '🥉') as rank_icon,
            COALESCE(ur.rank_points, 0) as points,
            COALESCE(ur.wins, 0) as wins,
            COALESCE(ur.total_matches, 0) as total_matches,
            CASE WHEN COALESCE(ur.total_matches, 0) > 0
                 THEN ROUND(COALESCE(ur.wins, 0)::numeric / ur.total_matches * 100, 0)
                 ELSE 0 END as win_rate
        FROM users u
        LEFT JOIN user_rank ur ON u.id = ur.user_id
        LEFT JOIN rank_config rc ON ur.current_rank = rc.rank_id
        WHERE ur.rank_points > 0 OR ur.total_matches > 0
        ORDER BY points DESC
        LIMIT %s;
    """

    leaderboard_data = execute_query(query, (limit,), fetch=True)

    # Convert to list
    leaderboard = []
    for i, row in enumerate(leaderboard_data):
        leaderboard.append({
            'rank': i + 1,
            'user_id': row['user_id'],
            'user_name': row['user_name'] or '匿名用戶',
            'user_avatar': row['user_avatar'] or '👤',
            'rank_id': row['rank_id'],
            'rank_icon': row['rank_icon'],
            'points': row['points'],
            'wins': row['wins'],
            'total_matches': row['total_matches'],
            'win_rate': f"{row['win_rate']}%"
        })

    # Cache the result
    query = """
        INSERT INTO leaderboard_cache (period_type, period_start, period_end, rank_data)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (period_type, period_start)
        DO UPDATE SET rank_data = %s, updated_at = CURRENT_TIMESTAMP;
    """

    json_data = json.dumps(leaderboard)
    execute_query(query, (period, start, end, json_data, json_data))

    return {
        'period': period,
        'period_start': str(start),
        'period_end': str(end),
        'data': leaderboard,
        'updated_at': datetime.now().isoformat()
    }


# ==================== Match History Operations ====================

def get_match_history(user_id, page=1, limit=20, filter_type='all'):
    """
    Get user's match history.
    filter_type: 'all', 'win', 'lose', 'draw'
    """
    offset = (page - 1) * limit

    # Build filter
    filter_clause = ""
    params = [user_id]

    if filter_type == 'win':
        filter_clause = "AND result = 'win'"
    elif filter_type == 'lose':
        filter_clause = "AND result = 'lose'"
    elif filter_type == 'draw':
        filter_clause = "AND result = 'draw'"

    # Get total count
    count_query = f"""
        SELECT COUNT(*) as total
        FROM arena_match
        WHERE user_id = %s AND status = 'completed' {filter_clause};
    """
    count_result = execute_query(count_query, params, fetch=True)
    total = count_result[0]['total'] if count_result else 0

    # Get matches
    query = f"""
        SELECT *
        FROM arena_match
        WHERE user_id = %s AND status = 'completed' {filter_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s;
    """

    params.extend([limit, offset])
    matches = execute_query(query, params, fetch=True)

    # Parse badges
    for match in matches:
        if match['badges_earned']:
            match['badges_earned'] = json.loads(match['badges_earned'])
        else:
            match['badges_earned'] = []

    return {
        'matches': matches,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': (total + limit - 1) // limit
        }
    }


# ==================== Reward Calculation ====================

def calculate_rewards(user_id, match_type, result, difficulty, user_correct, user_total, current_streak):
    """Calculate rewards for a match."""
    rewards = {
        'points': 0,
        'coins': 0,
        'badges': []
    }

    # Get reward configs
    query = "SELECT * FROM reward_config WHERE is_active = true;"
    configs = execute_query(query, fetch=True)

    # Calculate based on result
    if result == 'win':
        # Base points
        if difficulty == 'easy':
            rewards['points'] = 10
        elif difficulty == 'medium':
            rewards['points'] = 25
        else:  # hard
            rewards['points'] = 50

        # Base coins
        rewards['coins'] = 50

        # Check for badges
        # First match badge
        query = "SELECT total_matches FROM user_rank WHERE user_id = %s;"
        result_check = execute_query(query, (user_id,), fetch=True)
        if result_check and result_check[0]['total_matches'] == 0:
            rewards['badges'].append({
                'badge_id': 'arena_first',
                'badge_name': '初戰告捷',
                'badge_icon': '🎯'
            })

        # Streak badges
        if current_streak >= 3:
            rewards['badges'].append({
                'badge_id': 'arena_streak_3',
                'badge_name': '三連勝',
                'badge_icon': '🔥'
            })
        if current_streak >= 5:
            rewards['badges'].append({
                'badge_id': 'arena_streak_5',
                'badge_name': '五連勝',
                'badge_icon': '⚡'
            })
        if current_streak >= 10:
            rewards['badges'].append({
                'badge_id': 'arena_streak_10',
                'badge_name': '十連勝',
                'badge_icon': '🌟'
            })

        # Perfect score badge
        if user_total > 0 and user_correct == user_total:
            rewards['badges'].append({
                'badge_id': 'arena_perfect',
                'badge_name': '完美表現',
                'badge_icon': '💯'
            })

    elif result == 'lose':
        rewards['points'] = -5 if difficulty == 'easy' else (-10 if difficulty == 'medium' else -15)
        rewards['coins'] = 10
    else:  # draw
        rewards['points'] = 0
        rewards['coins'] = 25

    # Timed match bonus
    if match_type == 'timed':
        rewards['coins'] += 20  # Participation bonus
        rewards['coins'] += user_correct * 2  # Per correct answer

        # Timed master badge
        if user_total > 0 and user_correct / user_total >= 0.9:
            rewards['badges'].append({
                'badge_id': 'arena_timed_master',
                'badge_name': '速答王',
                'badge_icon': '🏃'
            })

    # Check for win milestones
    query = "SELECT wins FROM user_rank WHERE user_id = %s;"
    result_check = execute_query(query, (user_id,), fetch=True)
    if result_check:
        wins = result_check[0]['wins']
        if wins >= 10:
            rewards['badges'].append({
                'badge_id': 'arena_win_10',
                'badge_name': '戰場新星',
                'badge_icon': '⭐'
            })
        if wins >= 50:
            rewards['badges'].append({
                'badge_id': 'arena_win_50',
                'badge_name': '戰場老將',
                'badge_icon': '🏅'
            })
        if wins >= 100:
            rewards['badges'].append({
                'badge_id': 'arena_win_100',
                'badge_name': '百戰百勝',
                'badge_icon': '👑'
            })

    return rewards


# ==================== AI Opponent ====================

def generate_ai_score(difficulty, user_correct=None, user_total=None):
    """
    Generate AI opponent score based on difficulty.
    Returns (opponent_score, opponent_correct, opponent_total)
    """
    if difficulty == 'easy':
        # Easy: 30-50% correct
        correct_rate = random.uniform(0.3, 0.5)
    elif difficulty == 'medium':
        # Medium: 50-70% correct
        correct_rate = random.uniform(0.5, 0.7)
    else:  # hard
        # Hard: 70-90% correct
        correct_rate = random.uniform(0.7, 0.9)

    # Adjust based on user's performance if provided
    if user_correct is not None and user_total is not None and user_total > 0:
        user_rate = user_correct / user_total
        # Make it competitive - AI should be slightly above or below user
        if random.random() < 0.6:  # 60% chance to be close to user
            correct_rate = max(0.2, min(0.95, user_rate + random.uniform(-0.15, 0.15)))

    total = user_total if user_total else 10
    correct = int(total * correct_rate)
    score = int((correct / total) * 100) if total > 0 else 0

    return score, correct, total


# ==================== Arena Home Data ====================

def get_arena_home_data(user_id):
    """Get all data needed for arena home page."""
    # Get user rank
    rank_data = get_or_create_user_rank(user_id)
    rank_config = get_rank_config(rank_data['current_rank'])
    next_rank_config = get_rank_config_by_next(rank_data['current_rank'])

    # Get user coins
    coins_data = get_or_create_user_coins(user_id)

    # Get recent matches
    recent_matches = get_match_history(user_id, page=1, limit=5)

    # Get weekly rank
    leaderboard = get_leaderboard('weekly', limit=100)
    user_rank = None
    for entry in leaderboard['data']:
        if entry['user_id'] == user_id:
            user_rank = entry['rank']
            break

    # Get match count this week
    week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
    query = """
        SELECT COUNT(*) as count
        FROM arena_match
        WHERE user_id = %s AND status = 'completed' AND created_at >= %s;
    """
    result = execute_query(query, (user_id, week_start), fetch=True)
    matches_this_week = result[0]['count'] if result else 0

    # Calculate win rate
    win_rate = 0
    if rank_data['total_matches'] > 0:
        win_rate = int(rank_data['wins'] / rank_data['total_matches'] * 100)

    # Get categories
    categories = get_arena_categories()

    return {
        'user_rank': {
            'rank_id': rank_data['current_rank'],
            'rank_name': rank_config['rank_name_zh'] if rank_config else '青銅',
            'rank_icon': rank_config['rank_icon'] if rank_config else '🥉',
            'rank_points': rank_data['rank_points'],
            'next_rank': {
                'rank_id': next_rank_config['rank_id'] if next_rank_config else None,
                'rank_name': next_rank_config['rank_name_zh'] if next_rank_config else None,
                'rank_icon': next_rank_config['rank_icon'] if next_rank_config else None,
                'points_needed': (next_rank_config['min_points'] - rank_data['rank_points']) if next_rank_config else 0
            } if next_rank_config else None,
            'stats': {
                'total_matches': rank_data['total_matches'],
                'wins': rank_data['wins'],
                'losses': rank_data['losses'],
                'win_rate': f'{win_rate}%',
                'current_streak': rank_data['current_streak'],
                'best_streak': rank_data['best_streak']
            }
        },
        'coins': {
            'balance': coins_data['balance'],
            'today_earned': get_today_earned_coins(user_id)
        },
        'quick_stats': {
            'weekly_rank': user_rank or '未上榜',
            'monthly_rank': get_monthly_rank(user_id),
            'matches_this_week': matches_this_week
        },
        'recent_matches': recent_matches['matches'],
        'categories': categories
    }


def get_rank_config_by_next(current_rank_id):
    """Get the next rank config."""
    ranks = get_rank_config()
    current_index = None
    for i, r in enumerate(ranks):
        if r['rank_id'] == current_rank_id:
            current_index = i
            break

    if current_index is not None and current_index < len(ranks) - 1:
        return ranks[current_index + 1]
    return None


def get_today_earned_coins(user_id):
    """Get coins earned today."""
    today = datetime.now().date()
    query = """
        SELECT COALESCE(SUM(amount), 0) as total
        FROM coin_transaction
        WHERE user_id = %s AND amount > 0 AND created_at >= %s;
    """
    result = execute_query(query, (user_id, today), fetch=True)
    return result[0]['total'] if result else 0


def get_monthly_rank(user_id):
    """Get user's rank for monthly leaderboard."""
    leaderboard = get_leaderboard('monthly', limit=100)
    for entry in leaderboard['data']:
        if entry['user_id'] == user_id:
            return entry['rank']
    return '未上榜'


def get_arena_categories():
    """Get available categories for arena."""
    # These would ideally come from the question bank
    return [
        {'id': 'self_intro', 'name': '自我介紹', 'icon': '👤', 'question_count': 50},
        {'id': 'logic', 'name': '邏輯思維', 'icon': '🧠', 'question_count': 40},
        {'id': 'expression', 'name': '表達技巧', 'icon': '🎤', 'question_count': 35},
        {'id': 'social', 'name': '社交互動', 'icon': '👥', 'question_count': 30}
    ]
