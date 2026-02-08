# Web POC - AI 個性化升小私人導師

## 項目概述

這是 Web 版本的 POC（概念驗證），用於快速驗證核心功能和用戶體驗。

### 目標
- 快速驗證 AI 教學生成功能
- 測試用戶畫像收集流程
- 驗證 MiniMax API 集成
- 收集早期用戶反饋

### 技術棧
- **前端框架：** React + TypeScript
- **UI 庫：** Ant Design / Material-UI
- **狀態管理：** Redux Toolkit / Zustand
- **路由：** React Router
- **HTTP 客戶端：** Axios
- **構建工具：** Vite

### 開發計劃
1. Week 1-2: 環境搭建 + 基礎頁面
2. Week 3-4: 核心功能開發
3. Week 5: 測試與優化

### 快速開始

```bash
# 安裝依賴
npm install

# 啟動開發服務器
npm run dev

# 構建生產版本
npm run build
```

### 項目結構

```
web-poc/
├── src/
│   ├── components/      # 可復用組件
│   ├── pages/           # 頁面組件
│   ├── services/        # API 服務
│   ├── store/           # 狀態管理
│   ├── utils/           # 工具函數
│   ├── types/           # TypeScript 類型定義
│   └── App.tsx          # 根組件
├── public/              # 靜態資源
└── package.json
```

### 環境變量

創建 `.env` 文件：

```
VITE_API_BASE_URL=http://localhost:3000/api
VITE_MINIMAX_API_KEY=your_api_key_here
```

---

**注意：** 此為 POC 版本，成功驗證後將遷移到 Android App。
