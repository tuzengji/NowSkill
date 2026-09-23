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

当前清单包含 15 个启用中的第三方 Skill。

同步只迁移 Skill 文件，不迁移 API Token、MCP 登录状态或其他凭据。新 Skill 通常会自动出现，必要时重启 Agent。

### 仅恢复锁定版本

`python3 scripts/install.py` 保留为非破坏性的增量恢复命令：GitHub 来源使用清单中的提交，已有目录默认跳过，`--force` 才备份替换。well-known 来源仍获取当前内容。这个命令不检查 GitHub 更新，也不清理额外 Skill，不用于上面的完整同步流程。

### 持续同步规则

在主电脑上通过 Agent 新增、卸载或更新非内置 Skill 时，同一任务必须更新本仓库并提交、推送。另一台电脑执行同步时，以仓库清单为准，不能先把那台电脑多余的 Skill 加进清单。同步产生的新版本信息在有写权限时提交、推送；没有权限则保留本地清单并报告。

这是一条 Agent 工作规则，不是后台监控服务。仅复制仓库链接或 `git clone` 不会自行执行脚本；接收仓库的 Agent 需要读取指令并执行同步任务。

## 收录内容

### 自有 Skill

当前没有已安装的自有 Skill。

### 第三方 Skill

| Skill | 上游 |
| --- | --- |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| `lark-base`, `lark-shared` | [Feishu well-known skills](https://open.feishu.cn/.well-known/skills/index.json) |
| `design-taste-frontend` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| `figma`, `hatch-pet`, `pdf`, `playwright` | [openai/skills](https://github.com/openai/skills) |
| `flight-booking-ai`, `tourmind-booking` | [tourmind-com/Tourmind-Booking-Skills](https://github.com/tourmind-com/Tourmind-Booking-Skills) |
| `grill-me`, `grilling` | [mattpocock/skills](https://github.com/mattpocock/skills) |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) |
| `i-have-adhd` | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) |
| `shuorenhua` | [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) |

完整机器可读清单见 `skills.lock.json`。

## 给 Agent 的一句话

```text
请读取这个仓库的 AGENTS.md，以 skills.lock.json 为唯一目标清单，自动同步安装并检查更新全部 Skill，同时卸载你用户级目录中清单外的非内置 Skill，保留官方内置 Skill。执行 python3 scripts/sync.py，完成后报告更新、卸载、失败项和备份位置。
```
