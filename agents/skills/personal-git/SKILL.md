---
name: personal-git
description: 管理项目内与主仓共享工作区的个人 Git（.personal-git）。在初始化、查看、提交或回退 PRD、AGENTS、DEV_OVERVIEW、.codex、tasks、local_docs、local_scripts 等个人文件，或需要按项目 Git 提交锚点同步个人文件版本时使用。不要用于普通项目 Git 提交。
---

# Personal Git

在项目根目录内维护第二套 Git 元数据 `.personal-git/`，与项目 Git 共享工作区，但只监管个人文件。全部操作使用原生 Git 命令，不依赖脚本、插件或远程服务。

## 不变量

1. 项目 Git 与个人 Git 的 tracked file set 必须互斥。
2. 个人 Git 只允许监管下列路径：
   - 任意层级：`*PRD.md`、`AGENTS.md`、`PROJECT_IMPROVEMENTS.md`、`DEV_OVERVIEW.md`、`tasks.md`；
   - 仓库根目录：`.codex/**`、`local_scripts/**`、`local_docs/**`。
3. 个人 Git 元数据固定为 `<repo-root>/.personal-git/`，不得被任一仓库提交。
4. 每个正常的个人 Git 提交都必须包含提交尾注：`Project-Anchor: <项目 Git HEAD 的完整 SHA>`。
5. 不自动添加 remote、push、改写项目 Git 历史或迁移主仓已跟踪文件。
6. 回退前保留备份引用；不得使用个人 Git 的 `clean`，不得在含 `.personal-git/` 的项目执行 `git clean -x` 或 `git clean -X`。

## 命令上下文

每次先确定项目根目录；后续所有个人 Git 命令都显式指定 git-dir 和 work-tree：

```bash
ROOT="$(git rev-parse --show-toplevel)"
PGIT="$ROOT/.personal-git"

git --git-dir="$PGIT" --work-tree="$ROOT" <command>
```

不得在不确认仓库根目录的情况下把当前目录 `.` 当成 work-tree。

## 初始化

仅当 `$PGIT` 不存在时初始化；若路径已存在但不是有效 Git 目录，停止并报告，不得覆盖。

```bash
git init --bare --initial-branch=main "$PGIT"
```

在项目 Git 的 `info/exclude` 中维护以下区块；用 `git rev-parse --git-path info/exclude` 定位实际文件，不假定 `.git` 一定是目录：

```gitignore
# BEGIN personal-git
/.personal-git/
*PRD.md
AGENTS.md
PROJECT_IMPROVEMENTS.md
DEV_OVERVIEW.md
tasks.md
/.codex/
/local_scripts/
/local_docs/
# END personal-git
```

在 `$PGIT/info/exclude` 中维护以下 allowlist。其作用是默认忽略所有文件，只重新放行个人文件：

```gitignore
# Ignore all files by default, but continue traversing directories.
*
!*/

# Never expose Git metadata.
/.git/
/.personal-git/

# Personal files allowed at any depth.
!*PRD.md
!AGENTS.md
!PROJECT_IMPROVEMENTS.md
!DEV_OVERVIEW.md
!tasks.md

# Personal directories allowed at repository root.
!/.codex/
!/.codex/**
!/local_scripts/
!/local_scripts/**
!/local_docs/
!/local_docs/**
```

初始化后检查项目 Git 已跟踪文件。若主仓仍跟踪任何个人路径，停止：`info/exclude` 不会让 tracked 文件自动解除跟踪。只有用户明确要求迁移并理解其会形成主仓删除变更时，才可对准确文件执行 `git rm --cached`。首个个人提交也必须按后述提交流程写入项目锚点。

## 查看状态

用户可在项目根目录直接运行：

```bash
# 个人 Git 状态与差异
git --git-dir=.personal-git --work-tree=. status -sb
git --git-dir=.personal-git --work-tree=. diff
git --git-dir=.personal-git --work-tree=. diff --cached

# 最近提交及其项目锚点
git --git-dir=.personal-git --work-tree=. log -10 \
  --format='%h %ad %s%n  Project-Anchor: %(trailers:key=Project-Anchor,valueonly)' \
  --date=short

# 两个仓库的 tracked 文件交集；无输出才符合互斥要求
comm -12 \
  <(git ls-files | sort) \
  <(git --git-dir=.personal-git --work-tree=. ls-files | sort)
```

当前对应关系可分别查看：

```bash
git rev-parse HEAD
git --git-dir=.personal-git --work-tree=. log -1 \
  --format='%(trailers:key=Project-Anchor,valueonly)'
```

## 提交个人改动

按以下顺序执行：

1. 确认 `.personal-git` 有效，且两个仓库的 tracked 文件交集为空。
2. 检查个人 Git 已跟踪文件和 `status --short --untracked-files=all` 输出；出现非允许路径时停止并修复边界。
3. 项目 Git 必须已有 `HEAD`。用 `git -C "$ROOT" diff --quiet` 和 `git -C "$ROOT" diff --cached --quiet` 确认 tracked staged/unstaged 改动为空，否则锚点不能准确代表当前项目状态；不要把未提交代码状态伪装成已提交锚点。
4. 取得完整锚点：

   ```bash
   ANCHOR="$(git -C "$ROOT" rev-parse HEAD)"
   ```

5. 读取上一条个人提交的 `Project-Anchor`。若其不是当前 `$ANCHOR` 的祖先，说明项目历史发生了回退、切支或改写；先执行“按项目版本对齐”，不得把新提交直接叠加在错误的个人历史上。
6. 检查差异后执行 `add -A`。该命令仅在 allowlist 和 tracked-set 检查通过后使用：

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" add -A
   git --git-dir="$PGIT" --work-tree="$ROOT" diff --cached --name-status
   ```

7. 若暂存区为空，不创建空提交。否则使用简洁主题，并以独立段落写入锚点：

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" commit \
     -m "docs(personal): <summary>" \
     -m "Project-Anchor: $ANCHOR"
   ```

8. 提交后再次核对 trailer、状态和 tracked 文件交集。除非用户明确要求，不使用 `--amend`、rebase 或 force 操作。

## 按项目版本对齐或回退

将用户指定的项目版本解析为完整提交：

```bash
TARGET="$(git -C "$ROOT" rev-parse '<target>^{commit}')"
```

先用 `git -C "$ROOT" ls-tree -r --name-only "$TARGET"` 检查目标项目提交没有跟踪个人路径；若有，停止，避免项目 checkout/reset 覆盖个人文件。

个人提交选择规则：

1. 优先查找 trailer 与 `$TARGET` 完全相同的最新个人提交，例如：

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" log --all \
     --fixed-strings --grep="Project-Anchor: $TARGET" -1 --format=%H
   ```
2. 无完全匹配时，遍历 `git rev-list --all`：读取每个提交的 `Project-Anchor`，仅保留该锚点是 `$TARGET` 祖先的提交；用 `git rev-list --count "$ANCHOR..$TARGET"` 计算距离，选择距离最小者。同一锚点有多个提交时选择最新者。
3. 若没有有效候选，停止并说明该项目版本没有可恢复的个人快照；不得猜测或直接清空个人文件。

执行对齐前：

- 若个人工作区有未提交改动，先用个人 Git `stash push -u` 保存，绝不直接丢弃；
- 在当前个人 `HEAD` 创建备份分支，例如：

  ```bash
  BACKUP="backup/before-align-$(date +%Y%m%d-%H%M%S)-$(git --git-dir="$PGIT" rev-parse --short HEAD)"
  git --git-dir="$PGIT" branch "$BACKUP" HEAD
  ```

然后只重置个人 Git：

```bash
git --git-dir="$PGIT" --work-tree="$ROOT" reset --hard <personal-commit>
```

不得运行 `clean`。完成后报告：目标项目 SHA、所选个人提交、其锚点、是完全匹配还是最近祖先匹配、距离、备份分支和 stash 情况。

若用户明确要求同时回退项目 Git，应先完成双方状态检查、目标树冲突检查和个人提交定位，再执行项目 Git 的 checkout/reset，最后执行个人 Git reset。未经明确要求，不替用户重置项目 Git。

## 撤销单个个人提交

不跟随项目版本、只撤销某条个人提交时，优先生成新的反向提交，不改写历史：

```bash
ANCHOR="$(git -C "$ROOT" rev-parse HEAD)"
git --git-dir="$PGIT" --work-tree="$ROOT" revert --no-commit <personal-commit>
git --git-dir="$PGIT" --work-tree="$ROOT" commit \
  -m "revert(personal): <summary>" \
  -m "Project-Anchor: $ANCHOR"
```

若发生冲突，停止并展示冲突文件；不得擅自选择内容。

## 恢复与最终报告

需要恢复时优先检查：

```bash
git --git-dir=.personal-git --work-tree=. branch --all
git --git-dir=.personal-git --work-tree=. reflog
git --git-dir=.personal-git --work-tree=. stash list
```

每次操作结束说明：执行了哪种个人 Git 操作、项目锚点、个人提交、涉及文件、互斥检查结果、是否创建备份或 stash，以及仍存在的风险。不要声称项目与个人版本已对齐，除非 trailer 和实际目标提交已经核对。
