#===============================================================================
# Web-POC Cron Job 配置文件
#===============================================================================

# 项目配置
PROJECT_NAME="web-poc"
PROJECT_DIR="/Volumes/Newsmy1 - m/app/web-poc"
APP_URL="https://app-cs6e.onrender.com"
DASHBOARD_URL="https://dashboard.render.com/web/srv-d64343cr85hc73bj13qg"

# Claude配置
CLAUDE_MODEL="minimax-m2.1"
CLAUDE_TIMEOUT=300

# Playwright配置
PLAYWRIGHT_TIMEOUT=30000
SCREENSHOT_DIR="$PROJECT_DIR/outputs/screenshots"

# Git配置
GIT_REMOTE="origin"
GIT_BRANCH="main"
GIT_SIGNED_OFF=true

# 日志配置
LOG_DIR="$PROJECT_DIR/logs/cron"
MAX_LOG_FILES=50
MAX_LOG_AGE_DAYS=7

# Cron配置
CRON_EXPRESSION="*/10 * * * *"
LOCK_FILE="$PROJECT_DIR/.cron_lock"

# 通知配置（可选）
NOTIFICATION_EMAIL=""
SLACK_WEBHOOK=""

# 功能开关
ENABLE_DEPLOY_CHECK=true
ENABLE_E2E_TEST=true
ENABLE_AUTO_FIX=true
ENABLE_GIT_COMMIT=true
ENABLE_GIT_PUSH=true

# 高级配置
SKIP_SCREENSHOTS=false
MAX_RETRIES=3
RETRY_DELAY=60

# 时区设置
TZ="Asia/Hong_Kong"
