# E2E全面测试任务

## 目标

对 https://app-cs6e.onrender.com/ 进行全面的端到端测试，检测所有页面和功能的问题。

## 测试范围

### 需要测试的页面

1. **首页/欢迎页**: https://app-cs6e.onrender.com/
2. **登录页**: https://app-cs6e.onrender.com/login
3. **注册页**: https://app-cs6e.onrender.com/signup
4. **仪表盘**: https://app-cs6e.onrender.com/dashboard
5. **课程页**: https://app-cs6e.onrender.com/lesson
6. **个人资料编辑页**: https://app-cs6e.onrender.com/profile/edit
7. **设置页**: https://app-cs6e.onrender.com/settings
8. **录音页**: https://app-cs6e.onrender.com/recording
9. **解锁完整访问页**: https://app-cs6e.onrender.com/unlock-full-access

## 检查项目

### 1. 页面加载问题
- [ ] 页面能否正常加载
- [ ] 加载时间是否过长（超过5秒）
- [ ] 是否有404错误
- [ ] 是否有500服务器错误

### 2. 模拟数据和虚假数据检测
- [ ] 是否使用硬编码的示例数据
- [ ] 是否有"Lorem ipsum"文本
- [ ] 图片是否为占位符
- [ ] 是否有明显的测试数据

### 3. 页面格式和排版问题
- [ ] CSS样式是否正确加载
- [ ] 布局是否混乱
- [ ] 字体大小是否合适
- [ ] 颜色对比度是否正常
- [ ] 响应式布局是否正常
- [ ] 元素是否重叠
- [ ] 按钮和链接是否可点击

### 4. 功能性问题
- [ ] 表单是否能提交
- [ ] 验证消息是否正确
- [ ] 导航链接是否正常
- [ ] 认证流程是否正常

### 5. 内容问题
- [ ] 中文文本是否正确显示
- [ ] 是否有乱码
- [ ] 文本是否流畅自然
- [ ] 产品描述是否准确

## 测试步骤

1. 依次访问每个页面
2. 等待页面完全加载
3. 进行上述所有检查
4. 截图记录问题页面（保存到 outputs/screenshots/）
5. 详细记录所有发现的问题

## 问题分类

将发现的问题分为以下类别：

1. **CRITICAL**: 阻止用户使用的功能性问题
2. **HIGH**: 严重影响用户体验的问题
3. **MEDIUM**: 中等影响的问题
4. **LOW**: 轻微影响或美观问题
5. **INFO**: 建议改进

## 输出要求

返回JSON格式的测试结果：

```json
{
  "status": "completed",
  "timestamp": "测试时间戳",
  "app_url": "被测应用URL",
  "total_pages_tested": "测试的页面数量",
  "issues_found": "发现问题的总数",
  "page_results": [
    {
      "url": "页面URL",
      "page_name": "页面名称",
      "load_status": "success|failed|partial",
      "load_time_ms": "加载时间(毫秒)",
      "issues": [
        {
          "type": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
          "category": "功能|内容|排版|数据|安全性|性能",
          "title": "问题标题",
          "description": "详细描述",
          "element_selector": "问题元素的CSS选择器",
          "severity": "严重程度",
          "suggested_fix": "建议修复方案"
        }
      ],
      "screenshots": ["截图文件路径"]
    }
  ],
  "summary": {
    "critical_count": 0,
    "high_count": 0,
    "medium_count": 0,
    "low_count": 0,
    "info_count": 0
  },
  "recommendations": [
    "整体改进建议"
  ],
  "needs_git_commit": true/false
}
```

## 注意事项

- **如果需要Google登录进行测试**:
  - 邮箱: `cntk50951@gmail.com`
  - 凭证从 `.env` 文件读取
- 所有截图保存到: `/Volumes/Newsmy1 - m/app/web-poc/outputs/screenshots/`
- 问题描述要具体，包含复现步骤
- 对于数据问题，指出具体是哪些数据需要替换
- 对于排版问题，指出具体的CSS问题
