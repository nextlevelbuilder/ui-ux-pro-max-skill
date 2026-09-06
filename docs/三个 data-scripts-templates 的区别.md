# 三处 data / scripts / templates 的区别

## 三处分别是什么

| 位置 | 作用 | 能删吗 |
|------|------|--------|
| **src/ui-ux-pro-max/** | **唯一源码**。所有 CSV、脚本、模板都在这里改，是“唯一真相来源”。 | ❌ 不能删，这是你要维护的那一份。 |
| **.claude/skills/ui-ux-pro-max/** | 给 **Claude Code** 使用的 Skill。`SKILL.md` 手工维护；`data/` 和 `scripts/` 是从 `src` 同步的真实文件副本。 | ❌ 不能删，也不要改成符号链接；符号链接会在 Windows 的 Git 检出中失效。 |
| **cli/assets/** | 给 **npm 包 ui-ux-pro-max-cli** 打包用。用户执行 `npm i -g ui-ux-pro-max-cli` 再 `uipro init` 时，安装的是这里打包的 data/scripts/templates 和子 Skill。 | ❌ 不能删；发布前用脚本同步。 |

## 可以只保留一个吗？

- **不能**只保留一个“物理目录”：三处**用途不同**，都要存在。
- **只手工维护一份内容**：在 **src/ui-ux-pro-max/** 修改 data、scripts 和 templates，再用 `cli/scripts/sync-assets.mjs` 将它们复制到 `cli/assets/`，并将 data、scripts 复制到本地 Claude Skill 目录。
- `.claude/skills/ui-ux-pro-max/SKILL.md` 是例外：它不由模板生成，需要直接维护。

这样 data、scripts 和 templates 只在 `src` 维护，镜像目录由同步脚本更新。

## 推荐工作流

1. 只改 **src/ui-ux-pro-max/data/**、**scripts/**、**templates/**。
2. 不要直接修改 `cli/assets/data/`、`cli/assets/scripts/` 或 `.claude/skills/ui-ux-pro-max/{data,scripts}/`。
3. 提交或发布 npm 前执行：

   ```bash
   cd cli
   npm run sync:assets
   npm run check:assets
   ```

   `check:assets` 也由 “Check asset sync” CI 工作流执行。
