# Codex Harness

本仓库保存当前用户级 Codex harness 的可迁移基线，用于版本追踪、跨设备迁移和共同维护。

## 仓库布局

| 仓库路径 | 用户级来源 | 内容 |
|---|---|---|
| `codex/AGENTS.md` | `~/.codex/AGENTS.md` | 用户级 Codex 工作指令 |
| `codex/config.toml` | `~/.codex/config.toml` | 主配置、项目信任和插件开关 |
| `codex/api.config.toml` | `~/.codex/api.config.toml` | API provider profile |
| `codex/rules/` | `~/.codex/rules/` | 命令规则 |
| `codex/prompts/` | `~/.codex/prompts/` | 用户 prompt |
| `agents/skills/` | `~/.agents/skills/` | 用户安装或维护的 skills |

当前基线于 2026-09-15 调整 personal-git 分支规则，本机版本与本次兼容目标均为
`codex-cli 0.154.0`。已核对[官方 0.154.0 发布说明](https://learn.chatgpt.com/docs/changelog)：
本仓库未使用已移除的 `codex mcp-server`，本次不启用实验开关或更换模型。
Codex 主配置的位置和作用可参考
[OpenAI Codex Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)。

项目初始化时确定并在项目根级 `AGENTS.md` 记录文档管理模式：不需要隔离个人文档时，
不构建 personal-git，项目文档统一由主 Git 管理；需要隔离时才明确启用双 Git。
已有项目不因编辑文档自动启用，后续模式迁移需单独确认。

启用后，个人 Git 与项目 Git 使用同名分支（如 `main` → `main`、`feature/x` → `feature/x`），
每条个人提交继续记录 `Project-Anchor`。切支、新分支来源、旧单分支迁移和分支内回退见
[`personal-git` skill](agents/skills/personal-git/SKILL.md)。CLI 0.154.0 新增的实验 worktree
能力不自动同步个人文件；每个 checkout 独立维护 `.personal-git/`。

## 安全边界

仓库不会纳管以下内容：

- `auth.json`、API key、OAuth token 或其他凭据；
- 会话、history、memory、日志和 SQLite 运行数据库；
- cache、临时目录、锁文件、shell snapshot 和安装 ID；
- Codex 内置 system skills 与可重新下载的插件缓存。

`config.toml` 只引用 `OPENAI_API_KEY` 环境变量，不保存其值。提交前必须检查暂存区，
确认没有凭据或新的运行态文件被纳入。

## 更新流程

1. 在用户明确要求时盘点当前设备的用户级 Codex 配置。
2. 将可迁移且会被 Codex 消费的声明式配置同步到本仓库对应目录；插件启用配置随
   `config.toml` 同步，不保存安装状态或缓存快照。
3. 对照当前安装版本与最新官方 Codex 文档，只纳入已配置、维持既有工作流所必需，
   或经用户确认启用的新能力；不因出现新配置项就保存默认值或实验开关。
4. 对源文件与仓库副本进行内容比对，并校验 TOML、JSON、YAML 和 Python 文件。
5. 执行敏感信息扫描并人工检查 `git diff` 与待提交文件。
6. 提交变更并推送到 `origin`。

## 迁移说明

迁移到其他设备时，将 `codex/` 和 `agents/` 下的内容分别恢复到 `~/.codex/` 与
`~/.agents/` 的对应位置，并根据插件清单重新安装插件。恢复前必须复核：

- `config.toml` 中以 `/Users/hao.a.zeng/` 开头的项目路径；
- Azure provider endpoint 和目标设备的 `OPENAI_API_KEY` 环境变量；
- 目标设备是否需要沿用所有项目的信任状态；
- 通过目标设备的 Codex 插件管理命令确认所需插件已安装并启用。

认证信息必须在目标设备单独配置，不能从本仓库恢复。
