#!/bin/bash

#===============================================================================
# Web-POC 自动迭代测试 Cron 脚本
# 运行频率: 每10分钟
# 功能: 自动化部署监控、E2E测试、错误修复、GitHub提交
#===============================================================================

# 设置工作目录
PROJECT_DIR="/Volumes/Newsmy1 - m/app/web-poc"
cd "$PROJECT_DIR"

# 加载环境变量
source "$PROJECT_DIR/.env"

# 加载cron配置
source "$PROJECT_DIR/scripts/cron-config.sh"

# 日志配置
LOG_DIR="$PROJECT_DIR/logs/cron"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/cron_$(date +%Y%m%d_%H%M%S).log"
ERROR_LOG="$LOG_DIR/errors_$(date +%Y%m%d_%H%M%S).log"

# 状态文件
STATUS_FILE="$PROJECT_DIR/.cron_status"
LAST_ACTION_FILE="$PROJECT_DIR/.cron_last_action"

# 锁定文件（防止并发执行）
LOCK_FILE="$PROJECT_DIR/.cron_lock"

#===============================================================================
# 工具函数
#===============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >> "$ERROR_LOG"
}

check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        PID=$(cat "$LOCK_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "另一个cron任务正在运行 (PID: $PID)，退出"
            exit 0
        else
            log "清理旧的锁文件 (PID: $PID已不存在)"
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

cleanup() {
    rm -f "$LOCK_FILE"
    log "cron任务完成"
}

trap cleanup EXIT

#===============================================================================
# Claude AI 助手调用函数
#===============================================================================

call_claude_minimax() {
    local prompt_file="$1"
    local task_type="$2"
    local output_file="$3"

    log "调用Claude MiniMax模型执行任务: $task_type"

    # 构建完整prompt（包含系统上下文）
    full_prompt=$(cat "$PROJECT_DIR/prompts/cron_system_prompt.md")
    full_prompt+=$(cat "$prompt_file")

    # 调用claude命令行，输出到文件
    # 使用 --dangerously-skip-permissions 跳过权限确认
    claude -p "$full_prompt" \
           --dangerously-skip-permissions \
           --output-format json \
           > "$output_file" 2>&1

    # 记录到日志
    cat "$output_file" >> "$LOG_FILE"

    return 0
}

# 解析Claude返回的JSON结果
parse_claude_result() {
    local output_file="$1"
    local field="$2"

    python3 -c "
import json
import sys
with open('$output_file', 'r') as f:
    data = json.load(f)
    result = data.get('result', '')
    # 去掉markdown代码块标记
    result = result.replace('\`\`\`json', '').replace('\`\`\`', '').strip()
    # 解码JSON字符串中的转义字符
    inner = json.loads(result) if result.startswith('{') else result
    if isinstance(inner, dict):
        print(inner.get('$field', ''))
    else:
        print('')
" 2>/dev/null
}

#===============================================================================
# 阶段1: 检查部署状态
#===============================================================================

check_deployment_status() {
    log "=== 阶段1: 检查部署状态 ==="

    local prompt_file="$PROJECT_DIR/prompts/check_deployment_prompt.md"
    local output_file="$PROJECT_DIR/outputs/deployment_status_$(date +%Y%m%d_%H%M%S).json"

    mkdir -p "$PROJECT_DIR/outputs"

    # 调用Claude检查部署状态
    call_claude_minimax "$prompt_file" "check_deployment" "$output_file"

    # 使用Python解析JSON
    local status=$(parse_claude_result "$output_file" "status")

    # 转换为大写
    status=$(echo "$status" | tr '[:lower:]' '[:upper:]')

    case "$status" in
        "DEPLOYING")
            log "当前正在部署中，等待下次检查"
            echo "DEPLOYING" > "$STATUS_FILE"
            return 2
            ;;
        "FAILED"|"FAILURE")
            log "检测到部署失败，开始查询日志并修复"
            echo "FAILED" > "$STATUS_FILE"
            return 3
            ;;
        "HEALTHY"|"READY"|"SUCCESS")
            log "部署状态正常，可以进行测试"
            echo "HEALTHY" > "$STATUS_FILE"
            return 0
            ;;
        *)
            log "未知部署状态，尝试直接检查网站..."
            # 备用方案：直接检查网站是否可访问
            if curl -s -o /dev/null -w "%{http_code}" "$APP_URL" | grep -q "200\|302"; then
                log "网站可访问，假设部署正常"
                echo "HEALTHY" > "$STATUS_FILE"
                return 0
            else
                log "无法访问网站，假设需要等待"
                echo "UNKNOWN" > "$STATUS_FILE"
                return 1
            fi
            ;;
    esac
}

#===============================================================================
# 阶段2: 处理部署失败
#===============================================================================

handle_deployment_failure() {
    log "=== 阶段2: 处理部署失败 ==="

    local prompt_file="$PROJECT_DIR/prompts/fix_deployment_prompt.md"
    local output_file="$PROJECT_DIR/outputs/fix_deployment_$(date +%Y%m%d_%H%M%S).json"

    # 调用Claude分析日志并修复
    if ! call_claude_minimax "$prompt_file" "fix_deployment" "$output_file"; then
        error "修复部署失败失败"
        return 1
    fi

    # 检查是否需要提交修复
    local needs_commit=$(cat "$output_file" | grep -o '"needs_git_commit":[^,]*' | cut -d':' -f2 | tr -d ' ')
    if [ "$needs_commit" = "true" ]; then
        log "需要提交修复到GitHub"
        commit_and_push "修复部署问题"
    fi

    return 0
}

#===============================================================================
# 阶段3: E2E全面测试
#===============================================================================

run_e2e_tests() {
    log "=== 阶段3: E2E全面测试 ==="

    local prompt_file="$PROJECT_DIR/prompts/e2e_test_prompt.md"
    local output_file="$PROJECT_DIR/outputs/e2e_test_$(date +%Y%m%d_%H%M%S).json"
    local issues_file="$PROJECT_DIR/outputs/issues_found_$(date +%Y%m%d_%H%M%S).json"

    # 调用Claude进行E2E测试
    call_claude_minimax "$prompt_file" "e2e_test" "$output_file"

    # 使用Python解析JSON获取问题数量
    local issues_count=$(parse_claude_result "$output_file" "issues_found")
    local critical_count=$(parse_claude_result "$output_file" "critical_count")

    # 确保是数字，默认0
    issues_count=${issues_count:-0}
    critical_count=${critical_count:-0}

    if [ "$issues_count" -gt 0 ] || [ "$critical_count" -gt 0 ]; then
        log "发现 $issues_count 个问题 ($critical_count 个严重)，开始修复"
        echo "$issues_count" > "$STATUS_FILE"
        return 10  # 返回特殊码表示有问题需要修复
    fi

    log "E2E测试通过，未发现问题"
    echo "CLEAN" > "$STATUS_FILE"
    return 0
}

#===============================================================================
# 阶段4: 修复发现的问题
#===============================================================================

fix_issues() {
    log "=== 阶段4: 修复发现的问题 ==="

    local issue_file="$1"

    # 附加问题文件到prompt
    local full_prompt=$(cat "$PROJECT_DIR/prompts/cron_system_prompt.md")
    full_prompt+=$(cat "$PROJECT_DIR/prompts/fix_issues_prompt.md")
    full_prompt+="\n\n=== 需要修复的问题 ===\n"
    full_prompt+=$(cat "$issue_file")

    local output_file="$PROJECT_DIR/outputs/fix_issues_$(date +%Y%m%d_%H%M%S).json"

    # 调用Claude修复问题
    log "调用Claude MiniMax模型执行任务: fix_issues"
    echo "$full_prompt" | claude -p - \
           --dangerously-skip-permissions \
           --output-format json \
           > "$output_file" 2>&1

    # 记录到日志
    cat "$output_file" >> "$LOG_FILE"

    # 检查修复是否需要提交
    local needs_commit=$(cat "$output_file" | grep -o '"needs_git_commit":[^,]*' | cut -d':' -f2 | tr -d ' ')
    if [ "$needs_commit" = "true" ]; then
        local issue_type=$(cat "$issue_file" | grep -o '"type":"[^"]*"' | cut -d'"' -f4)
        commit_and_push "修复$issue_type问题"
    fi

    return 0
}

#===============================================================================
# 阶段5: GitHub提交
#===============================================================================

commit_and_push() {
    local commit_message="$1"
    log "=== GitHub提交: $commit_message ==="

    cd "$PROJECT_DIR"

    # 添加所有更改
    git add -A

    # 检查是否有更改
    if git diff --cached --quiet; then
        log "没有需要提交的更改"
        return 0
    fi

    # 提交
    git commit -m "$commit_message [auto-cron $(date +%Y%m%d_%H%M%S)]" \
               -m "Generated by Web-POC Auto-Cron Job" \
               -m "Changes: $(git diff --cached --name-only | tr '\n' ', ')" \
               --signoff

    if [ $? -ne 0 ]; then
        error "Git提交失败"
        return 1
    fi

    log "Git提交成功: $(git log -1 --oneline)"

    # 推送到远程
    git push origin main

    if [ $? -ne 0 ]; then
        error "Git推送失败"
        return 1
    fi

    log "Git推送成功"

    # 记录最后操作
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $commit_message" >> "$LAST_ACTION_FILE"

    return 0
}

#===============================================================================
# 主流程
#===============================================================================

main() {
    log "========================================="
    log "Web-POC Cron任务开始执行"
    log "========================================="

    check_lock

    # 记录开始时间
    START_TIME=$(date +%s)

    # 阶段1: 检查部署状态
    check_deployment_status
    DEPLOY_STATUS=$?

    case $DEPLOY_STATUS in
        2)  # 正在部署
            log "部署中，跳过本次测试循环"
            exit 0
            ;;
        3)  # 部署失败
            handle_deployment_failure
            if [ $? -eq 0 ]; then
                log "部署问题已修复，等待下次检查"
            fi
            exit 0
            ;;
        1)  # 检查失败
            error "无法确定部署状态，退出"
            exit 1
            ;;
        0)  # 部署正常
            log "部署状态正常，继续E2E测试"
            ;;
    esac

    # 阶段2: E2E测试
    run_e2e_tests
    E2E_STATUS=$?

    if [ $E2E_STATUS -eq 10 ]; then
        # 发现问题，进行修复
        LATEST_ISSUES=$(ls -t "$PROJECT_DIR/outputs/issues_found_"*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_ISSUES" ]; then
            fix_issues "$LATEST_ISSUES"
        else
            error "未找到问题文件"
        fi
    elif [ $E2E_STATUS -ne 0 ]; then
        error "E2E测试执行异常"
    fi

    # 计算执行时间
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    log "========================================="
    log "Cron任务执行完成，耗时: ${DURATION}秒"
    log "========================================="
}

#===============================================================================
# 启动入口
#===============================================================================

# 检查是否在正确的目录
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "错误: 找不到 $PROJECT_DIR/app.py，请检查项目路径"
    exit 1
fi

# 运行主流程
main "$@"
