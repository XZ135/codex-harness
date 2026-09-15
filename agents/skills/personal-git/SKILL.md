---
name: personal-git
description: 管理与主仓共享工作区、分支同名对应的个人 Git（.personal-git）。在初始化、查看、提交、切支对齐或回退个人文档与配置，或按项目提交锚点恢复个人文件时使用。不要用于普通项目 Git 提交。
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
7. 正常写入时，个人 Git 分支必须与当前项目分支同名（包括 `/` 等字符），不得用一个个人分支承接多个项目分支。分支隔离历史，`Project-Anchor` 定位分支内的项目版本，两者都必须检查。

## 命令上下文

每次先确定项目根目录；后续所有个人 Git 命令都显式指定 git-dir 和 work-tree：

```bash
ROOT="$(git rev-parse --show-toplevel)"
PGIT="$ROOT/.personal-git"
PROJECT_BRANCH="$(git -C "$ROOT" symbolic-ref --quiet --short HEAD)"

git --git-dir="$PGIT" --work-tree="$ROOT" <command>
```

不得在不确认仓库根目录的情况下把当前目录 `.` 当成 work-tree。

若项目为 detached HEAD，允许只读检查；正常初始化、提交、撤销与自动切支停止，不能把 `HEAD` 当分支名。用户明确要求恢复此 SHA 时，必须指定个人来源分支，按下述候选规则恢复到个人 detached HEAD，保留原分支引用。

Codex CLI 0.154.0 的 `--worktree` / `/worktree` 是实验能力。本 skill 不要求启用它；在 linked worktree 中，`ROOT` 必须是当前 checkout 根目录，每个 worktree 使用自己的 `.personal-git/`，不得通过主仓 common-dir 共享个人 HEAD/index。新 worktree 不会自动带上被忽略的个人文件和历史；缺失时说明情况，只有来源明确时才从指定个人仓导入快照。

## 初始化

仅当 `$PGIT` 不存在时初始化；若路径已存在但不是有效 Git 目录，停止并报告，不得覆盖。

```bash
git init --bare --initial-branch="$PROJECT_BRANCH" "$PGIT"
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

## 分支对齐

只读查看不切支。每次个人写操作前、项目切支后，重新读取双方分支与项目 HEAD；同一项目提交可能属于多个分支，不能仅凭锚点相同就跳过分支检查。

1. 若个人分支已同名，继续校验锚点。若不同，先检查当前个人 tracked set、allowlist 和双方互斥关系，再检查目标个人树也只包含允许路径，且与当前项目 tracked set 无交集。目标树可能覆盖的未跟踪或忽略文件也必须先保全；`stash -u` 不保存忽略文件。
2. 切支前记录原个人分支和 HEAD。未提交个人改动用 `stash push -u -m "before-switch: <原分支> -> <目标分支>"` 保存，并记录 stash 的完整对象 ID；确认个人工作区和暂存区均干净。没有首个提交时不能 stash，先停止并保全文件。不得自动将旧分支 stash 应用到新分支。
3. 同名个人分支已存在时，用以下命令切换，然后检查该分支锚点是否为当前项目 HEAD 的祖先；不是则执行“按项目版本对齐或回退”。不要为了对齐而重命名或覆盖另一个已有分支。

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" switch "$PROJECT_BRANCH"
   ```

4. 同名个人分支不存在时，确定项目新分支的来源分支及分叉点。只在该来源的个人分支中，按下述候选规则选出锚点等于分叉点或其最近祖先的个人提交。来源无法从本次切支操作或明确历史证据确定时，询问来源，不从所有分支猜测。选定并完成目标树检查后创建：

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" switch -c "$PROJECT_BRANCH" <personal-base>
   ```

   没有可用来源快照时停止并说明，不能把当前其他分支的最新个人文件直接作为新分支基线。真正全新个人仓则走“初始化”。
5. 项目合并、重命名或删除分支不会自动合并、重命名或删除个人分支。保留原历史；需要时按用户指定范围处理。

### 旧单分支迁移

先在自定义引用 `refs/personal-backup/<唯一标识>` 保存旧个人 HEAD（用 `git update-ref <ref> HEAD ""`，要求引用尚不存在），记录旧分支、锚点和未提交状态。备份引用不占用同名项目分支命名空间。

旧 `main` 不意味着它属于项目 `main`。先根据锚点、reflog 和用户已知上下文确认旧历史对应的项目分支；若旧历史混合多个项目分支，锚点可达性不能证明归属，需明确迁移来源快照。确认旧分支完全属于当前项目分支且目标不存在时可用 `branch -m "$PROJECT_BRANCH"` 保留历史；否则保留旧引用，从确认的快照创建目标分支。目标已存在则使用其历史，不覆盖。其余项目分支按需建立，不批量复制同一个 HEAD。

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
git symbolic-ref --quiet --short HEAD
git --git-dir=.personal-git --work-tree=. symbolic-ref --quiet --short HEAD
git --git-dir=.personal-git --work-tree=. log -1 \
  --format='%(trailers:key=Project-Anchor,valueonly)'
```

## 提交个人改动

按以下顺序执行：

1. 确认 `.personal-git` 有效，完成“分支对齐”，且两个仓库的 tracked 文件交集为空。
2. 检查个人 Git 已跟踪文件和 `status --short --untracked-files=all` 输出；出现非允许路径时停止并修复边界。
3. 项目 Git 必须已有 `HEAD`。用 `git -C "$ROOT" diff --quiet` 和 `git -C "$ROOT" diff --cached --quiet` 确认 tracked staged/unstaged 改动为空，否则锚点不能准确代表当前项目状态；不要把未提交代码状态伪装成已提交锚点。
4. 取得完整锚点：

   ```bash
   ANCHOR="$(git -C "$ROOT" rev-parse HEAD)"
   ```

5. 读取当前同名个人分支上一条提交的 `Project-Anchor`。首个提交无前序可跳过；其余情况若 trailer 缺失、重复或不是有效项目提交，停止并修复来源。若锚点不是当前 `$ANCHOR` 的祖先，先执行“按项目版本对齐”，不得把新提交直接叠加在错误的个人历史上。
6. 检查差异后执行 `add -A`。该命令仅在 allowlist 和 tracked-set 检查通过后使用：

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" add -A
   git --git-dir="$PGIT" --work-tree="$ROOT" diff --cached --name-status
   ```

7. 若暂存区为空，不创建空提交。否则先重新核对项目分支、HEAD 和干净状态未变化，再使用简洁主题，并以独立段落写入锚点：

   ```bash
   git --git-dir="$PGIT" --work-tree="$ROOT" commit \
     -m "docs(personal): <summary>" \
     -m "Project-Anchor: $ANCHOR"
   ```

8. 提交后再次核对双方分支、trailer、状态和 tracked 文件交集。除非用户明确要求，不使用 `--amend`、rebase 或 force 操作。

## 按项目版本对齐或回退

将用户指定的项目版本解析为完整提交：

```bash
TARGET="$(git -C "$ROOT" rev-parse '<target>^{commit}')"
```

先用 `git -C "$ROOT" ls-tree -r --name-only "$TARGET"` 检查目标项目提交没有跟踪个人路径；若有，停止，避免项目 checkout/reset 覆盖个人文件。

先确定目标项目分支；默认是当前项目分支，明确切支任务则使用目标分支。裸 SHA 不携带分支归属，不从 `branch --contains` 猜测。个人搜索范围固定为 `refs/heads/<目标项目分支>`；新建分支时仅使用已确认的来源个人分支。禁止用 `--all` 扫描其他分支、stash 或备份来自动匹配。

个人提交选择规则：

1. 用 `git --git-dir="$PGIT" rev-list --first-parent "$PERSONAL_REF"` 从选定分支尖端向后遍历。逐条解析 `%(trailers:key=Project-Anchor,valueonly)`，要求恰好一个有效完整项目 SHA；不能用提交正文 grep 代替 trailer 校验。
2. 优先选择锚点与 `$TARGET` 完全相同的第一个提交；否则仅保留锚点是 `$TARGET` 祖先的候选，用项目 Git 的 `rev-list --count "$ANCHOR..$TARGET"` 计算距离，选择最小者。距离相同时取上述遍历中最先出现者，不依赖提交时间。first-parent 避免从个人 merge 的其他父线意外选择快照。
3. 没有有效候选时停止并说明该分支没有可恢复快照；不得跨分支兜底或清空文件。显式恢复旧备份时，可以使用用户指定的备份引用作为搜索范围。

执行对齐前：

- 校验所选个人提交的树只含允许路径，并与当前及目标项目 tracked set 互斥；检查会被覆盖的未跟踪/忽略文件，先保全再操作；
- 若个人工作区有未提交改动，先用个人 Git `stash push -u` 保存，记录来源分支和 stash 对象 ID，确认保存成功且工作区干净；
- 在当前个人 `HEAD` 创建备份引用，例如（重名则换唯一标识，不覆盖）：

  ```bash
  BACKUP="refs/personal-backup/before-align-$(date +%Y%m%d-%H%M%S)-$(git --git-dir="$PGIT" rev-parse --short HEAD)"
  git --git-dir="$PGIT" update-ref "$BACKUP" HEAD ""
  ```

确认个人 Git 已切换到目标同名分支后，只重置该个人分支；若切换前备份的是另一个分支，还须为将被重置的目标分支尖端创建独立备份引用。detached 恢复则使用 `switch --detach <personal-commit>`，不执行以下分支重置：

```bash
git --git-dir="$PGIT" --work-tree="$ROOT" reset --hard <personal-commit>
```

不得运行 `clean`。完成后报告：双方分支、目标项目 SHA、所选个人提交、其锚点、是完全匹配还是最近祖先匹配、距离、备份引用和 stash 情况。仅恢复个人文件到另一 SHA 时，说明主仓 HEAD 未改变，不能称双方版本已对齐。

若用户明确要求同时回退项目 Git，应先完成双方状态检查、目标树冲突检查和个人提交定位，再执行项目 Git 的 checkout/reset，最后执行个人 Git reset。未经明确要求，不替用户重置项目 Git。

## 撤销单个个人提交

不跟随项目版本、只撤销某条个人提交时，优先生成新的反向提交，不改写历史：

先执行与正常提交相同的分支、锚点、项目干净状态和文件边界检查，并确认个人工作区干净、待撤销提交属于当前个人分支历史。

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
git --git-dir=.personal-git for-each-ref refs/personal-backup/
git --git-dir=.personal-git --work-tree=. reflog
git --git-dir=.personal-git --work-tree=. stash list
```

每次操作结束说明：执行了哪种个人 Git 操作、双方分支、项目锚点、个人提交、涉及文件、互斥检查结果、是否创建备份或 stash，以及仍存在的风险。不要声称项目与个人版本已对齐，除非分支映射、trailer 和实际目标提交已经核对。
