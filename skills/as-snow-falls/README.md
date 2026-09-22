# As Snow Falls · 落雪为念

A Claude Code skill that writes Chinese prose in a distinctive literary voice — physics-tinged, classical, restrained.

> 落雪为念,岁月成诗。

## 这是什么

一个面向 Claude Code 的 skill。调用之后,Claude 会以一种特定的中文文学风格,为你代拟、仿写、改写:

- **硬词软用** —— 把物理术语(熵、量子、原子、波函数、光子、基本粒子、140 亿年)嫁接到抒情场景
- **四字对仗** —— 古典短句与对仗节律,重画面、重留白
- **辩证留白** —— INFJ 式内省、克制、不说满
- **签名意象** —— 雪、长安、猫、星河、烟火、麦、故乡

适合:金句、随笔、生日信、告别信、致辞、悼词、朋友圈长文、文末收束句。
不适合:商业文案、技术文档、纯新闻报道、幽默/梗图/emoji 密集文本。

---

## 安装

**用户级(所有项目共用):**

```bash
mkdir -p ~/.claude/skills
git clone git@github.com:WishingCat/As-Snow-Falls.git ~/.claude/skills/as-snow-falls
```

**项目级(只在当前仓库生效):**

```bash
mkdir -p .claude/skills
git clone git@github.com:WishingCat/As-Snow-Falls.git .claude/skills/as-snow-falls
```

克隆完后在 Claude Code 里重启会话,skill 即可在 available-skills 列表中被识别。

---

## 使用

在 Claude Code 中直接以斜杠命令调用:

```
/as-snow-falls 帮我写一封生日信,给一个走了三年的朋友
/as-snow-falls 给这段话写一个收束句
/as-snow-falls 把这段说明改写得克制一点,去掉流量腔
```

或用自然语言描述任务,Claude 在识别到风格匹配时会自动调用:

```
用落雪为念的风格,帮我写一段中秋给家人的话
模仿 as-snow-falls 这个 skill 写一个毕业致辞的开篇
```

---

## 更新

```bash
cd ~/.claude/skills/as-snow-falls     # 或 .claude/skills/as-snow-falls
git pull
```

---

## 关于

由 [@WishingCat](https://github.com/WishingCat) 维护。本仓库只发布 skill 本身(`SKILL.md`),原始写作档案与详细风格分析未公开。

一把声音的完整形成需要时间,欢迎 issue / PR 反馈在使用中遇到的"听起来不像"的地方。
