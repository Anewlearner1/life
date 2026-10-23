# 像素人生：都市與鄉村

手機優先的 16-bit 像素生活模擬網頁遊戲（MVP）。

```bash
npm install
npm run dev      # 開發伺服器
npm test         # 邏輯單元測試
npm run build    # 型別檢查 + 打包到 dist/
```

- 架構與模組契約：`docs/ARCHITECTURE.md`
- 可調數值（時間倍率、需求、薪資、好感度門檻）：`src/game/GameConfig.ts`
- 美術規格與素材追蹤：`assets/SPEC.md`、`assets/asset_tracker.csv`
