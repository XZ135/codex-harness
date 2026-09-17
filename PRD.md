# Codex Harness PRD

## 上下文与范围

本项目维护用户级 Codex harness 的可版本化副本。整体背景、维护方向和跨设备约束见
[`DEV_OVERVIEW.md`](DEV_OVERVIEW.md)。

## 已实现

- 已建立并于 2026-09-02 更新当前设备的用户级 Codex harness 基线，纳管用户级
  `AGENTS.md`、主配置、API profile、命令规则、prompt 和自定义 skills；同步时会对照
  当前安装版本与最新官方 Codex 文档，仅纳入兼容且实际使用的声明式配置。
- 当前 API profile 使用 `gpt-5.6-sol`；用户指令统一使用 `local_docs` 作为临时文档目录，
  并通过 `personal-git` skill 约束个人文件双 Git 的初始化、提交、对齐与回退流程。
- 项目初始化时确定并在根级 `AGENTS.md` 记录文档管理模式：无隔离需求时不构建
  personal-git，文档统一由主 Git 管理；仅明确启用后才应用个人文件互斥、同名分支
  和锚点规则。已有项目保持当前模式，不因编辑文档自动初始化；模式转换须明确授权，
  初始化前先检查主仓已跟踪文档，模式记录与实际仓库冲突或个人仓缺失、损坏时不静默迁移。
- 已启用的 personal-git 规则保持兼容目标 Codex CLI 0.154.0：个人分支与项目分支同名，恢复限于对应
  分支的锚点历史；新分支基于明确来源快照，旧单分支迁移保留备份，detached HEAD
  不自动选择分支，多个 worktree 各自维护个人 Git 元数据。
- `tasks.md` 不属于 harness 约定文档，不按文件名给予特殊管理或忽略规则；是否创建、
  维护和跟踪由项目自身决定。personal-git 不再为该文件名提供专用 allowlist 条目；
  既有仓库的跟踪关系与历史不自动迁移。
- 插件启用配置随 `config.toml` 纳管；不保存 Codex 不直接消费的插件安装快照、
  缓存版本、远程 ID 或其他派生状态，实际安装状态由目标设备上的 Codex 插件管理命令确认。
- 已通过忽略规则排除认证信息、API key、会话、历史、memory、日志、运行数据库、
  缓存、临时状态、shell snapshot、安装 ID、内置 system skills 和插件缓存。
- 仓库配置文件只保存 API key 的环境变量名，不保存凭据值；迁移说明明确要求在目标设备
  单独配置认证信息，并复核设备绝对路径、provider endpoint 和项目信任状态。
- 项目的权威 Git 远程为 <https://github.com/XZ135/codex-harness.git>；harness 更新提交后
  应同步到该远程。

## 未实现

### 待确认

- 设备专属配置的表达方式，以及不同设备配置发生差异时的合并规则。
- 是否需要自动化的检查、安装或迁移流程；当前基线采用用户请求触发、人工审查后同步。

## 子文档索引

当前无子级需求文档。
