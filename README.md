# NowSkill

这是我的 Codex Skill 恢复清单。把这个仓库交给另一台电脑上的 Agent，让它读取 `AGENTS.md` 并执行安装脚本，即可恢复本机当前使用的非内置 Skill。

仓库遵循以下规则：

- 自有 Skill 保存完整源码。
- 第三方 Skill 只保存来源链接、目录和锁定提交，不复制第三方源码。
- Codex 自带的 `.system` Skill 和随 Codex 运行时提供的 Skill 不收录。
- GitHub 来源默认锁定到已核对的提交，保证安装结果可复现。

## 自动安装

需要 Python 3、Git 和网络连接：

```bash
git clone https://github.com/tuzengji/NowSkill.git
cd NowSkill
python3 scripts/install.py
```

默认安装到官方推荐的用户级目录 `~/.agents/skills`。已存在的同名目录会跳过，不会覆盖本地修改。

```bash
# 先查看将执行的操作
python3 scripts/install.py --dry-run

# 安装到指定目录
python3 scripts/install.py --dest ~/.codex/skills

# 更新同名 Skill；旧目录会先备份到 ~/.agents/skill-backups/
python3 scripts/install.py --force
```

`as-snow-falls` 在这台电脑上处于禁用状态，因此仓库保留的是 `SKILL.md.disabled`，安装后也不会被 Codex 自动加载。其余 14 个 Skill 会正常安装。

安装脚本只恢复 Skill 文件，不迁移 API Token、MCP 登录状态或其他凭据。若新 Skill 没有立即出现，请重启 Codex。

## 收录内容

### 自有 Skill

| Skill | 状态 | 仓库内容 |
| --- | --- | --- |
| `as-snow-falls` | 已安装但禁用 | 源码位于 `skills/as-snow-falls/` |

### 第三方 Skill

| Skill | 上游 |
| --- | --- |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills/tree/7407f3893ad4dceab546ac002c3ef806e4000c73/skills/find-skills) |
| `lark-base`, `lark-shared` | [Feishu well-known skills](https://open.feishu.cn/.well-known/skills/index.json) |
| `design-taste-frontend` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/5217fb45be2c0b302f29c9cd31cbd3237501c684/skills/taste-skill) |
| `figma`, `hatch-pet`, `pdf`, `playwright` | [openai/skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated) |
| `flight-booking-ai`, `tourmind-booking` | [tourmind-com/Tourmind-Booking-Skills](https://github.com/tourmind-com/Tourmind-Booking-Skills/tree/47f22676ea7214328a8a1cac0932a40638ca4f49/skills) |
| `grill-me`, `grilling` | [mattpocock/skills](https://github.com/mattpocock/skills/tree/c55ee46073ed923f86ce59a5eb3b6d895095d1b7/skills/productivity) |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer/tree/9862685f575c65a8247f90369951df1b3416e3d6) |
| `shuorenhua` | [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua/tree/5a9eafefe03807404135f4d2ee4f42fe61d58759) |

完整机器可读清单见 `skills.lock.json`。

## 给 Agent 的一句话

```text
请读取这个仓库的 AGENTS.md，并安装 skills.lock.json 中的全部 Skill；不要覆盖已有 Skill，完成后报告安装、跳过和失败项。
```
