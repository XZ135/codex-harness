# Research skill 选型记录

核查日期：2026-09-17。任务：寻找公开分享且适合当前 Codex harness 的 research skill，
审查后加入本项目。根级 DEV_OVERVIEW、PRD 和 README 已阅读；现有 skills 保存在
`agents/skills/`，本次沿用该布局。

## 结论与选择条件

选用 `arjunprabhulal/agent-skills` 的 `deep-research` 原版，作为通用研究流程。
这是基于文件审查的适配性判断，不是经过模型横向评测的效果排名。

优先条件：完整阅读原始资料、追溯证据独立性、检索反证、解释来源冲突、标记推断和
未知项、合理控制输出、明确许可、能使用当前宿主工具。仓库热度仅作维护背景，
不能替代质量验证。本次未假设用户需要专门的医学系统综述或第三方托管研究服务。

## 主要候选比较

| 候选及一手来源 | 优点 | 本次判断 |
|---|---|---|
| [Arjun deep-research](https://github.com/arjunprabhulal/agent-skills/blob/42dd24080fce6d731d00e2a1134f398c3da4171b/skills/research/deep-research/SKILL.md) | 追溯原始来源、反证搜索、冲突解释、区分置信度；纯指令、MIT | 选用。适合当前通用技术调研；社区规模很小，缺少已公布的横向实测成绩 |
| [199-biotechnologies deep-research](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/f2f2c0fa4e7617ca84c86b63f4bb40f77a746933/SKILL.md) | 分阶段研究、来源与声明台账、引用验证脚本、渐进式报告生成 | 未选。默认要求较长报告、HTML/PDF、写入 Documents 并自动打开文件，适配改动较多；GitHub API 未识别出根许可证，不能仅凭公开可读视为已核清许可 |
| [Tavily research](https://github.com/tavily-ai/skills/blob/778122e5f9c680f541eeceda5a5b36405eb7980c/skills/tavily-research/SKILL.md) | 服务提供方维护、结构化输出、异步研究接口 | 未选。需要 `tvly` CLI 和认证，核心研究交给外部服务；当前没有此依赖需求 |
| [K-Dense literature-review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/330c8e764435a731eff571e3efdda70b363d0792/skills/literature-review/SKILL.md) | 多数据库检索、纳排标准、质量评价、引用核验、可复现检索记录 | 未选。定位学术综述，要求配套搜索与绘图 skills，PDF 还依赖系统工具；作为本项目默认通用研究入口过重 |

候选由公开网页搜索发现，实际决策检查了上游 SKILL.md、GitHub 仓库元信息，
并核对选中版本的完整 skill 目录和根 LICENSE。未安装仅出现在搜索摘要中而未经核查的资源。

GitHub API 查询时的背景数据（均为仓库级，非该 skill 的使用量或效果指标）：

| 仓库 | Stars | 最近 push 时间（UTC） |
|---|---:|---|
| arjunprabhulal/agent-skills | 2 | 2026-08-04 |
| 199-biotechnologies/claude-deep-research-skill | 1028 | 2026-04-11 |
| tavily-ai/skills | 481 | 2026-09-04 |
| K-Dense-AI/scientific-agent-skills | 45311 | 2026-09-14 |

## 安装与验证边界

使用 skill-installer 的安装脚本从固定提交导入，正文无修改，补充上游 MIT LICENSE
与 UPSTREAM.md。`.agents/skills/deep-research` 相对链接指向唯一正文目录；
[Codex 官方文档](https://learn.chatgpt.com/docs/build-skills)明确支持项目级 skill 目录及符号链接。

已核对上游原文字节与 SHA-256、许可证、链接目标、必需元数据及目录内容。
官方 `quick_validate.py` 格式校验返回 `Skill is valid!`，`git diff --check` 通过。
格式校验使用临时 PyYAML 环境，没有修改项目依赖。
上游 [evals/deep-research.json](https://github.com/arjunprabhulal/agent-skills/blob/42dd24080fce6d731d00e2a1134f398c3da4171b/evals/deep-research.json)
包含技术选型、向量数据库调研、反确认偏误三个预期行为案例；这些是评测输入和期望，
不是已通过的成绩。本次只做指令审查和安装检查，未运行独立模型评测或新会话发现测试。

没有修改业务代码或添加运行依赖，因此未新增 pytest 测试。当前环境下一轮应能发现新 skill；
若未显示，按官方文档重启 Codex 后检查。跨设备检出时需保留符号链接。
