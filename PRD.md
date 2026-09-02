# Codex Harness PRD

## 上下文与范围

本项目维护用户级 Codex harness 的可版本化副本。整体背景、维护方向和跨设备约束见
[`DEV_OVERVIEW.md`](DEV_OVERVIEW.md)。

## 已实现

- 已建立 2026-08-21 的当前设备用户级 Codex harness 基线，纳管用户级
  `AGENTS.md`、主配置、API profile、命令规则、prompt 和自定义 skills。
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
