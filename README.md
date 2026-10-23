# ToolBox 文字工具箱 (MVP v0.1)

免費、無需登入的繁體中文文字工具:文字去重複、文字清理器。文字只在瀏覽器本機處理,不上傳。

## 指令

```bash
npm install
npm run dev        # 開發伺服器 http://localhost:3000
npm run build      # 正式建置
npm start          # 啟動建置結果
npm test           # 單元測試 (vitest)
npm run lint       # ESLint
npm run typecheck  # TypeScript 型別檢查
```

## 結構

- `src/lib/text/`:純函式邏輯與單元測試(`splitLines`、`removeDuplicateLines`、`cleanText`)
- `src/lib/clipboard.ts`:複製工具(Clipboard API,失敗時退回 execCommand)
- `src/components/`:可重用元件(Button、CopyButton、Stat、Field、Checkbox、Header、Footer)與工具元件
- `src/app/`:頁面 `/`、`/remove-duplicate-lines`、`/text-cleaner`、`/privacy`、`/about`
