# 部署状态检查任务

## 目标

使用Playwright访问Render Dashboard，检查当前部署状态。

## 操作步骤

1. 使用Playwright访问: https://dashboard.render.com/web/srv-d64343cr85hc73bj13qg/events
2. 等待页面完全加载
3. 查找以下内容：
   - "Cancel deploy" 按钮或链接（表示正在部署中）
   - 任何部署失败的错误信息
   - 部署成功的状态指示
4. 如果需要更多信息，访问: https://dashboard.render.com/web/srv-d64343cr85hc73bj13qg/logs?r=1h

## 判断标准

### 正在部署中 (DEPLOYING)
- 页面显示 "Cancel deploy" 按钮或链接
- 状态显示为 "Deploying" 或 "In progress"

### 部署失败 (FAILED)
- 状态显示为 "Failed" 或 "Error"
- 看到红色错误提示
- 构建步骤失败

### 部署成功 (HEALTHY)
- 状态显示为 "Live" 或 "Deployed"
- 没有错误信息
- 最近一次部署显示成功

## 输出要求

请返回JSON格式的检查结果：

```json
{
  "status": "DEPLOYING|FAILED|HEALTHY|UNKNOWN",
  "timestamp": "当前时间戳",
  "url": "检查的URL",
  "observations": [
    "页面观察到的关键信息"
  ],
  "error_details": {
    // 仅在FAILED时填写
    "error_type": "错误类型",
    "error_message": "错误信息摘要",
    "failed_step": "失败的步骤"
  },
  "recommendation": "后续建议"
}
```

## 重要提示

- 耐心等待页面完全加载（最多30秒）
- **如果页面需要Google登录，使用以下账户**:
  - 邮箱: `cntk50951@gmail.com`
  - 凭证在 `.env` 文件中的 `GOOGLE_CLIENT_ID` 和 `GOOGLE_CLIENT_SECRET`
- 多次刷新确认状态，避免临时状态误判
