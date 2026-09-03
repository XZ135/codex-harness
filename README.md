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

当前基线依据 2026-09-02 的本机状态更新，并按当前安装的 Codex CLI 0.151.0、
官方最新的 Codex CLI 0.152.1 与配置文档检查兼容性。Codex 主配置的位置和作用可参考
[OpenAI Codex Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)。

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
