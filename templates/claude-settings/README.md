# Claude Settings 範本

`/setup-claude` skill 會把 `settings.json.template` 的內容 deep merge 到使用者的 `~/.claude/settings.json`。

## 範本內容（最小化）

目前只含**核心安全規則**——對所有人、所有場景都適用、且零成本零負擔的設定：

- `permissions.deny`：17 條破壞性指令黑名單（rm -rf、force push、reset --hard、sudo、kubectl delete、docker volume rm…）
- `permissions.ask`：17 條須二次確認的指令（rm、git checkout --、docker exec、kubectl apply、npm install -g、psql / mysql / sqlcmd / mongo / redis-cli 等 DB CLI 連線…）

完整清單見 `settings.json.template`。設計理由與更廣的安全護欄論述見根 README 的「安全注意事項與護欄」章節。

**不包含 plugins 與 marketplaces**——任何 plugin（superpowers、commit-commands、skill-creator、claude-mem 等）都由學員依需要自行決定何時安裝。未來版本可能會新增「建議 plugin 介紹」說明文件。

## Merge 策略

`/setup-claude` 對 `~/.claude/settings.json` 的處理：

- **不覆寫**：學員原有 key 一律保留，範本僅補上缺漏的 key
- **陣列取聯集去重**：`permissions.deny` / `permissions.ask` 兩端合併、去重
- **執行前自動備份**：`settings.json.bak.{timestamp}`
