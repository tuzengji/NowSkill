# NowSkill

这是我的公开 Skill 同步清单。把这个仓库交给另一台电脑上的 Agent 做同步，它会读取 `AGENTS.md`，安装清单内的全部 Skill、检查并安装上游更新，同时卸载自己用户级目录中清单外的非内置 Skill。

仓库遵循以下规则：

- 自有 Skill 保存完整源码。
- 第三方 Skill 只保存来源链接、目录和锁定提交，不复制第三方源码。
- Codex 自带的 `.system` Skill 和随 Codex 运行时提供的 Skill 不收录。
- 同步时检查 GitHub 默认分支最新提交；如来源设置了 `update_ref`，则检查指定引用。成功后把实际提交写回清单。
- Feishu 等 well-known 来源每次获取当前文件，记录文件树内容哈希；这类来源不提供历史版本下载。
- 替换和卸载前保留可恢复备份，不删除符号链接指向的原始源码。

## 自动同步

需要 Python 3.10 或更新版本、Git 和网络连接：

```bash
git clone https://github.com/tuzengji/NowSkill.git
cd NowSkill
python3 scripts/sync.py
```

默认安装到用户级目录 `~/.agents/skills`，同时检查 `$CODEX_HOME/skills`（未设置时为 `~/.codex/skills`），移除旧目录中的重复副本和清单外的非内置 Skill。同名 Skill 的本地修改会被备份后替换。

```bash
# 检查上游并预览；仅临时下载，不改安装目录和清单
python3 scripts/sync.py --dry-run

# 另一种 Agent：只同步明确指定的用户 Skill 目录
python3 scripts/sync.py --dest /path/to/agent/skills

# 同时清理该 Agent 的另一个用户 Skill 目录
python3 scripts/sync.py --dest /path/to/agent/skills --root /path/to/legacy/skills
```

`--dest` 会关闭对 Codex 两个默认目录的扫描，只处理目标目录和显式传入的 `--root`。不要把主目录、项目根目录、系统目录或插件缓存作为同步目录。

已有仓库再次同步前，先在干净工作区执行 `git pull --ff-only` 获取最新清单；不能为拉取更新而丢弃本地修改。不要并发执行同步，也不要在同步过程中修改 Skill 目录。

所有来源下载和验证成功后才开始替换与卸载；应用过程中出错会尝试回滚文件变更。若权限或磁盘故障导致回滚失败，脚本会报告待恢复路径。旧文件保存在各 Skill 根目录旁的 `skill-backups/nowskill-<时间>-<唯一标识>/` 中，脚本会打印具体位置。恢复时将相应目录移回原路径；符号链接备份应移回原位置后再使用。

`.system` 和 Codex 内置运行时保留。脚本不处理项目级、管理员级目录或插件缓存；Agent 应另行核查第三方插件提供的 Skill，通过其受支持的卸载机制处理，不能直接删除缓存或连带移除无关连接器。遇到无法安全处理的项必须报告，不能宣称已完全同步。目录外的链接目标不会被删除；链接集合、断链或受保护目录冲突会停止同步并报告。

这里的“官方保留”指内置/system/runtime Skill。手动安装的 OpenAI curated Skill 仍属于清单管理范围。用户级目录遵循[官方 Skill 目录说明](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)。

当前用户级清单包含 47 个 Skill，均来自第三方。

同步只迁移 Skill 文件，不迁移 API Token、MCP 登录状态或其他凭据。新 Skill 通常会自动出现，必要时重启 Agent。

### 仅恢复锁定版本

`python3 scripts/install.py` 保留为非破坏性的增量恢复命令：GitHub 来源使用清单中的提交，已有目录默认跳过，`--force` 才备份替换。well-known 来源仍获取当前内容。这个命令不检查 GitHub 更新，也不清理额外 Skill，不用于上面的完整同步流程。

### 持续同步规则

在主电脑上通过 Agent 新增、卸载或更新非内置 Skill 时，同一任务必须更新本仓库并提交、推送。另一台电脑执行同步时，以仓库清单为准，不能先把那台电脑多余的 Skill 加进清单。同步产生的新版本信息在有写权限时提交、推送；没有权限则保留本地清单并报告。

这是一条 Agent 工作规则，不是后台监控服务。仅复制仓库链接或 `git clone` 不会自行执行脚本；接收仓库的 Agent 需要读取指令并执行同步任务。

## 收录内容

### 第三方 Skill

| Skill | 上游 |
| --- | --- |
| `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/codebase-design)；深模块设计、职责与调用规则审查，包含设计及测试参考，锁定版本见清单 |
| `domain-modeling` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/domain-modeling)；澄清领域概念、维护术语表与架构决策记录，包含格式模板，锁定版本见清单 |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| `lark-base`, `lark-shared` | [Feishu well-known skills](https://open.feishu.cn/.well-known/skills/index.json) |
| `playwright` | [openai/skills](https://github.com/openai/skills) |
| `grilling` | [mattpocock/skills](https://github.com/mattpocock/skills) |
| `handoff` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/handoff)；将当前对话整理为下一位 Agent 可继续使用的交接文档，锁定版本见清单 |
| `improve-codebase-architecture` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/improve-codebase-architecture)；架构审查与改进候选可视化报告，按需单项安装，保留完整引用文件 |
| `research` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/research)；基于一手资料开展调研，保存带引用的研究笔记，锁定版本见清单 |
| `diagnosing-bugs` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/diagnosing-bugs)；以可复现反馈循环定位故障与性能回退，包含人工辅助诊断模板，锁定版本见清单 |
| `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/writing-for-agents)；编写和精简 Skill、AGENTS.md 等 Agent 文档，明确触发条件与上下文引用，锁定版本见清单 |
| `code-review` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/code-review)；按指定基线，分别审查代码规范与需求实现，锁定版本见清单 |
| `retro` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/retro)；复盘 Agent 会话，提出工具、自动检查与规则改进，锁定版本见清单 |
| `tdd` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd)；围绕约定的公共接口逐步编写失败测试与实现，包含测试与 mocking 参考，锁定版本见清单 |
| `grill-with-docs` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/grill-with-docs)；组合 grilling 与 domain-modeling，在需求访谈中沉淀术语和架构决策，锁定版本见清单 |
| `setup-matt-pocock-skills` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/setup-matt-pocock-skills)；配置项目工单、分类标签与领域文档位置，包含配置模板，锁定版本见清单 |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) |
| `anti-defensive-writing` | [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing)；精简中英文写作中的防御性表达，保留必要限定，锁定版本见清单 |
| `humanizer-zh` | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable)；界面设计、审查、美化及响应式与可访问性检查，锁定版本见清单 |
| `awesome-design-md` | [wearescientist/awesome-design-md](https://github.com/wearescientist/awesome-design-md)（封装自 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)）；主流产品 DESIGN.md 设计规范索引与按需套用，锁定版本见清单 |
| `ppt-master` | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)；可编辑 PPTX 生成、模板填充与演示稿美化，锁定版本见清单 |
| `logo-design` | [kaankiziltug/logo-design-skill](https://github.com/kaankiziltug/logo-design-skill)；Logo 概念、SVG 绘制、小尺寸检查和交付工具 |
| `nature-figure`, `nature-writing`, `nature-shared` | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)；科学绘图、论文写作及共享参考，锁定版本见清单 |
| `design-taste-frontend` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/f6b76575f949707b4e3c37cd86cb44b0b98643e8/skills/taste-skill)；反模板化前端设计与版式精修规则、文案与一致性门禁检查，锁定版本见清单 |
| `hallmark` | [Nutlope/hallmark](https://github.com/Nutlope/hallmark/tree/04977e15f3dfd6ee4b74c887dac3eb52665d6c92/skills/hallmark)；网页设计架构审查、设计 Token 约束与 `sloplint` 门禁检查，锁定版本见清单 |
| `emil-design-eng` 等 18 个前端动效与界面工程 Skill | [emilkowalski/skills](https://github.com/emilkowalski/skills/tree/0f2e23b32bb1265e84cff8d3e75785fec953fb1b/skills)（含 `emil-design-eng`、`mobile-native`、`animate`、`choreograph`、`gestures`、`review-animations`、`improve-animations`、`animation-performance`、`apple-design` 等 18 项）；微交互、缓动物理曲线、移动端原生手感与界面精修，锁定版本见清单 |

### 项目级 Skill

论文项目单独安装了 [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)，锁定提交 `333fd5eba58e28951ea89f12f03fefd78c877a47`。

| Skill | 项目内入口 |
| --- | --- |
| `academic-paper` | `.agents/skills/academic-paper` |
| `academic-paper-reviewer` | `.agents/skills/academic-paper-reviewer` |
| `deep-research` | `.agents/skills/deep-research` |
| `academic-pipeline` | `.agents/skills/academic-pipeline` |

项目目录为 `~/LovingHeart/ShouYuLove/以手寻语SignTrace/第十一届残疾人数据科学研讨会`。四个入口链接到项目内同一份完整上游快照，保留共享规则和脚本的相对路径。记录见 `skills.lock.json` 的 `project_skills`；本仓库仅保存来源、版本、路径和哈希，不包含第三方源码或论文。

这些项目项不属于用户级 `skills` 同步列表，`scripts/sync.py` 按既有规则保留项目级安装，不把它们迁入全局目录。迁移这个论文项目时应按锁定提交恢复完整上游目录及四个入口，不能只复制单个 `SKILL.md`。当前记录另有 5 个项目级 Skill：上述 4 个论文 Skill 和 1 个自有网站设计 Skill。

完整机器可读清单见 `skills.lock.json`。

## 给 Agent 的一句话

```text
请读取这个仓库的 AGENTS.md，以 skills.lock.json 为唯一目标清单，自动同步安装并检查更新全部 Skill，同时卸载你用户级目录中清单外的非内置 Skill，保留官方内置 Skill。执行 python3 scripts/sync.py，完成后报告更新、卸载、失败项和备份位置。
```
