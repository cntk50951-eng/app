# Web-POC 自动迭代测试 Cron Job

## 概述

本项目实现了一个全自动的CI/CD监控和测试系统，每10分钟自动执行以下任务：

1. **部署状态监控** - 检查Render部署状态
2. **自动问题修复** - 发现并修复部署问题
3. **E2E全面测试** - 测试所有页面和功能
4. **自动代码修复** - 修复发现的问题
5. **Git提交推送** - 自动提交修复

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Cron Job (每10分钟)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  部署状态检查  │───>│  部署失败?   │───>│  修复部署问题 │  │
│  │  Playwright  │    │  Claude AI   │    │  Claude AI   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │            │
│         │                   │                   │            │
│         v                   v                   v            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 部署正常 ✓   │    │ 正在部署中   │    │  提交GitHub   │  │
│  │              │    │ 等待下次检查  │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                              │
│         v                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  E2E全面测试  │───>│  发现问题?   │───>│  修复问题    │  │
│  │  Playwright  │    │  Claude AI   │    │  Claude AI   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │            │
│         │                   │                   │            │
│         v                   v                   v            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  测试通过 ✓  │    │  问题修复 ✓   │    │  提交GitHub   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 文件结构

```
web-poc/
├── scripts/
│   ├── web-poc-cron.sh          # 主cron脚本
│   └── cron-config.sh           # 配置文件
├── prompts/
│   ├── cron_system_prompt.md    # 系统提示词
│   ├── check_deployment_prompt.md  # 部署检查prompt
│   ├── e2e_test_prompt.md       # E2E测试prompt
│   ├── fix_deployment_prompt.md # 部署修复prompt
│   └── fix_issues_prompt.md     # 问题修复prompt
├── outputs/                      # 测试输出
│   ├── screenshots/             # 截图
│   ├── deployment_status_*.json  # 部署状态
│   ├── e2e_test_*.json          # E2E测试结果
│   └── issues_found_*.json      # 发现的问题
├── logs/
│   └── cron/                     # cron日志
├── .cron_status                  # 状态文件
├── .cron_lock                    # 锁文件
└── CRON_JOB_README.md           # 本文档
```

## 快速开始

### 1. 环境准备

```bash
# 确保在项目根目录
cd /Volumes/Newsmy1\ -m/app/web-poc

# 给予脚本执行权限
chmod +x scripts/web-poc-cron.sh

# 安装必要的依赖（如果需要）
pip install playwright
playwright install chromium
```

### 2. 配置环境变量

确保 `.env` 文件包含以下变量：

```bash
# GitHub配置（自动提交需要）
GITHUB_API_KEY=your_github_api_key

# MiniMax API（Claude调用需要）
MINIMAX_API_KEY=your_minimax_api_key

# 其他项目配置...
```

### 3. 手动测试脚本

```bash
# 手动运行一次cron任务
./scripts/web-poc-cron.sh

# 或者加上调试模式
DEBUG=true ./scripts/web-poc-cron.sh
```

### 4. 设置Cron定时任务

```bash
# 编辑crontab
crontab -e

# 添加以下行（每10分钟运行）
*/10 * * * * /Volumes/Newsmy1\ -m/app/web-poc/scripts/web-poc-cron.sh >> /Volumes/Newsmy1\ -m/app/web-poc/logs/cron/cron.log 2>&1

# 或者使用launchd（macOS推荐）
# 见下方"使用launchd替代cron"章节
```

### 5. 验证Cron设置

```bash
# 查看cron任务列表
crontab -l

# 查看cron日志
tail -f /Volumes/Newsmy1\ -m/app/web-poc/logs/cron/cron.log
```

## 使用launchd替代cron（macOS推荐）

macOS上推荐使用 `launchd` 来替代cron，因为：

1. cron在macOS休眠时不会运行
2. launchd更可靠，提供更好的日志

### 创建launchd plist文件

```bash
# 创建~/Library/LaunchAgents/com.web-poc.cron.plist
```

文件内容：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.web-poc.cron</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Volumes/Newsmy1 - m/app/web-poc/scripts/web-poc-cron.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>600</integer>  <!-- 600秒 = 10分钟 -->
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Volumes/Newsmy1 - m/app/web-poc/logs/cron/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Volumes/Newsmy1 - m/app/web-poc/logs/cron/launchd.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

### 启动launchd任务

```bash
# 加载任务
launchctl load ~/Library/LaunchAgents/com.web-poc.cron.plist

# 立即启动一次
launchctl start com.web-poc.cron

# 查看状态
launchctl list | grep web-poc

# 停止任务
launchctl unload ~/Library/LaunchAgents/com.web-poc.cron.plist
```

## Claude命令行使用

### 基本用法

```bash
# 调用Claude MiniMax模型
claude --model minimax-m2.1 --prompt "你的提示词"

# 指定输出文件
claude --model minimax-m2.1 --prompt "提示词" --output result.json
```

### 在脚本中使用

```bash
# 在web-poc-cron.sh中
claude --model minimax-m2.1 \
       --prompt "$(cat prompts/check_deployment_prompt.md)" \
       --output "$PROJECT_DIR/outputs/result.json"
```

## 工作流程详解

### 阶段1: 部署状态检查

1. 使用Playwright访问Render Dashboard
2. 检测以下状态：
   - **DEPLOYING**: 显示"Cancel deploy"按钮，等待下次检查
   - **FAILED**: 部署失败，进入修复流程
   - **HEALTHY**: 部署正常，继续E2E测试

### 阶段2: 部署失败处理

1. 访问日志页面获取详细错误信息
2. 分析错误类型：
   - 依赖问题
   - 环境变量缺失
   - 代码错误
   - 配置问题
3. 修复问题
4. 提交GitHub

### 阶段3: E2E测试

测试页面包括：
- 首页、登录页、注册页
- 仪表盘、课程页
- 个人资料页、设置页
- 录音页等

检查项目：
- 页面加载
- 模拟/虚假数据
- 排版格式
- 功能问题
- 内容质量

### 阶段4: 问题修复

按优先级修复：
1. **CRITICAL**: 功能性问题
2. **HIGH**: 严重体验问题
3. **MEDIUM**: 中等问题
4. **LOW**: 美观问题

### 阶段5: Git提交

自动提交格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型包括：feat, fix, style, refactor, content

## 日志和输出

### 日志位置

- **Cron日志**: `logs/cron/cron_YYYYMMDD_HHMMSS.log`
- **错误日志**: `logs/cron/errors_YYYYMMDD_HHMMSS.log`
- **Screenshot**: `outputs/screenshots/*.png`

### 状态文件

- `.cron_status`: 当前部署/测试状态
- `.cron_lock`: 防止并发执行
- `.cron_last_action`: 最后操作记录

## 故障排除

### 问题1: 脚本无法执行

```bash
# 检查权限
ls -l scripts/web-poc-cron.sh

# 修复权限
chmod +x scripts/web-poc-cron.sh

# 检查路径
bash -x scripts/web-poc-cron.sh
```

### 问题2: Playwright无法启动

```bash
# 安装浏览器
playwright install chromium

# 检查浏览器
which chromium
```

### 问题3: Git提交失败

```bash
# 检查Git配置
git config --global user.name
git config --global user.email

# 检查远程仓库
git remote -v

# 检查权限
ls -la .git
```

### 问题4: Claude调用失败

```bash
# 检查Claude CLI
which claude

# 检查模型配置
claude --version

# 测试API连接
claude --model minimax-m2.1 --prompt "test"
```

## 自定义配置

### 修改检查间隔

编辑 `scripts/cron-config.sh`：

```bash
CRON_EXPRESSION="*/5 * * * *"  # 改为5分钟
```

### 跳过某些测试

```bash
# 编辑scripts/web-poc-cron.sh
ENABLE_E2E_TEST=false  # 跳过E2E测试
ENABLE_AUTO_FIX=false   # 跳过自动修复
```

### 添加自定义检查

在 `scripts/web-poc-cron.sh` 的 `main()` 函数中添加：

```bash
# 自定义检查
custom_check() {
    log "执行自定义检查..."
    # 你的检查逻辑
}
```

## 监控和告警

### 检查运行状态

```bash
# 查看最近的运行记录
cat .cron_last_action

# 查看最新日志
ls -lt logs/cron/*.log | head -5
tail -100 logs/cron/cron_latest.log
```

### 设置告警（可选）

在脚本中添加告警逻辑：

```bash
# 发送Slack通知
if [ "$STATUS" = "FAILED" ]; then
    curl -X POST -d "{\"text\":\"Web-POC部署失败!\"}" $SLACK_WEBHOOK
fi
```

## 最佳实践

1. **定期清理日志**：
   ```bash
   # 添加到crontab
   0 0 * * 0 find /Volumes/Newsmy1 -m/app/web-poc/logs -name "*.log" -mtime +7 -delete
   ```

2. **监控磁盘空间**：确保outputs目录不会无限增长

3. **测试修复**：在生产环境应用修复前，先在本地测试

4. **版本控制**：所有prompt和脚本都应纳入版本控制

## 贡献指南

1. Fork本项目
2. 创建功能分支
3. 提交改进
4. 发起Pull Request

## 许可证

本项目采用MIT许可证。

## 联系

如有问题，请提交Issue或联系维护团队。
