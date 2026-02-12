# 问题修复任务

## 目标

根据E2E测试发现的问题，进行系统性修复。

## 输入信息

### 1. 项目结构
- **项目根目录**: `/Volumes/Newsmy1 - m/app/web-poc`
- **模板目录**: `/Volumes/Newsmy1 - m/app/web-poc/templates/`
- **静态文件**: `/Volumes/Newsmy1 - m/app/web-poc/static/`
- **服务层**: `/Volumes/Newsmy1 - m/app/web-poc/services/`
- **数据库层**: `/Volumes/Newsmy1 - m/app/web-poc/db/`

### 2. 技术栈
- **后端**: Python Flask 2.3.0
- **数据库**: PostgreSQL
- **认证**: Google OAuth 2.0
- **AI服务**: MiniMax API
- **部署**: Render (Gunicorn)

## 修复类别

### 1. 模拟数据和虚假数据

**问题示例**:
- 使用硬编码的示例数据
- "Lorem ipsum"占位文本
- 示例图片使用占位图
- 固定的测试数据

**修复策略**:
```python
# 从数据库动态获取真实数据
# 创建数据生成器
# 实现真实数据的API端点
```

### 2. 页面格式和排版问题

**常见问题**:
- CSS样式未正确加载
- 布局错乱
- 字体大小/颜色问题
- 响应式布局失效
- 元素重叠
- 按钮样式不一致

**修复策略**:
```css
/* 修复CSS问题 */
.static/css/styles.css
```

### 3. 内容问题

**常见问题**:
- 中文文本不流畅
- 产品描述不准确
- 术语使用不当
- 文本缺失或错误

**修复策略**:
```jinja2
<!-- 修复模板 -->
templates/*.html
```

### 4. 功能性问题

**常见问题**:
- 表单验证失败
- 按钮点击无响应
- 导航链接错误
- API调用失败

**修复策略**:
```python
# 修复Flask路由和视图函数
app.py
services/*.py
```

## 修复优先级

1. **CRITICAL**: 修复功能性问题，确保应用可正常使用
2. **HIGH**: 修复严重影响用户体验的问题
3. **MEDIUM**: 修复中等影响的问题
4. **LOW**: 改进美观和次要问题

## 输出要求

返回JSON格式的修复结果：

```json
{
  "status": "completed|partial|failed",
  "timestamp": "修复时间戳",
  "total_issues": "修复的问题总数",
  "issues_fixed": [
    {
      "issue_id": "问题ID",
      "category": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "title": "问题标题",
      "original_description": "原始问题描述",
      "fix_applied": {
        "file": "修复的文件路径",
        "description": "修复说明",
        "code_change": {
          "before": "修复前代码",
          "after": "修复后代码"
        }
      },
      "verification": "如何验证修复效果"
    }
  ],
  "issues_pending": [
    {
      "issue_id": "待修复问题ID",
      "reason": "未修复原因",
      "suggested_approach": "建议修复方法"
    }
  ],
  "files_modified": [
    "修改的文件列表"
  ],
  "files_created": [
    "新创建的文件列表"
  ],
  "needs_git_commit": true/false,
  "commit_message": "建议的提交信息",
  "summary": "修复总结"
}
```

## Git提交规范

### 提交类型
- **feat**: 新功能
- **fix**: Bug修复
- **style**: 代码格式修复（不影响功能）
- **refactor**: 重构
- **content**: 内容修复（文本、描述等）

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 示例

```
fix(content): 修复首页虚假数据问题

- 将硬编码的示例数据替换为数据库动态查询
- 更新欢迎文本使其更符合产品定位
- 移除"Lorem ipsum"占位文本

Closes #123

---

feat(template): 添加响应式布局支持

- 为所有页面添加响应式CSS
- 修复移动端导航栏显示问题
- 优化小屏幕设备的布局
```

## 注意事项

1. **备份**: 修改前确保有版本控制
2. **测试**: 修复后进行基本功能测试
3. **文档**: 更新相关文档
4. **兼容性**: 确保修复不会影响其他功能
5. **风格**: 保持代码风格一致
6. **安全性**: 不要引入安全漏洞
7. **性能**: 避免不必要的性能下降

## 验证清单

修复完成后，确认：
- [ ] 问题已解决
- [ ] 相关功能正常工作
- [ ] 没有引入新的问题
- [ ] 代码风格一致
- [ ] 页面加载正常
- [ ] 没有破坏现有功能
