# 上游来源与使用说明

- 项目：<https://github.com/arjunprabhulal/agent-skills>
- 作者：Arjun Prabhulal
- 许可证：MIT，完整声明见 [LICENSE](LICENSE)。
- 引入日期：2026-09-17
- 固定提交：`42dd24080fce6d731d00e2a1134f398c3da4171b`
- 上游文件：[`skills/research/deep-research/SKILL.md`](https://github.com/arjunprabhulal/agent-skills/blob/42dd24080fce6d731d00e2a1134f398c3da4171b/skills/research/deep-research/SKILL.md)
- 原文 SHA-256：`2646cdf3942d918e84febf020b289fbfb7b5cf601e43ee7e7349e6c5105941c5`

`SKILL.md` 保持上游原文。本目录额外保留许可证和本说明，未引入上游其他 skills。
更新时人工审查新版本的指令、依赖和许可证，并同步提交号及原文校验值。

## 使用

适合技术选型、方案比较和需要多来源证据的开放问题研究。调用示例：

```text
$deep-research 调研适合本项目的向量检索方案，结合现有技术栈比较，
核验官方资料和原始基准，说明反证、适用边界、置信度与未知项。
用中文输出，将完整报告保存到 local_docs/vector-search-research.md。
```

使用宿主已提供的搜索和网页读取能力，没有额外 Python、Node、MCP 或账号依赖。
若宿主无法联网，只能研究已提供的材料，不能声称核验过外部来源。
报告路径由用户和项目规则确定；本仓库使用 `local_docs/`。

本仓库通过 `.agents/skills/deep-research` 的相对链接提供项目级发现入口。
迁移到其他设备时，也可按仓库既有约定将本目录复制到 `~/.agents/skills/deep-research/`。
当前设备已安装到 `~/.agents/skills/deep-research/`，可供其他项目使用；
用户级目录保存独立副本，更新时需同步。本 skill 使用默认发现机制，无需在
`~/.codex/config.toml` 中增加条目。

## 能力边界

这是研究方法指令，不是独立的搜索引擎、后台 research agent 或系统综述自动化平台。
实际效果取决于模型、工具、可访问资料和任务范围。上游提供三个预期行为案例，
但未据此提供可复现的横向效果成绩；本次不宣称其质量优于所有候选。
