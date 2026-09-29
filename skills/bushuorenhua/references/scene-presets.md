# 场景预设

场景预设是起点，不会覆盖用户给出的参数或语义保护。用户写明文档类型时优先使用；没有明说时根据结构和词汇自动判断。混合文档按区块处理。

## `chat`：助手对话腔

```text
profile=support+generic
intensity=2
density=low
structure=preserve
meta=light
jargon=off
praise=light
call_to_action=light
```

常见表现：先说“这是一个很好的问题”，再重复问题；使用“简单来说/进一步来看/希望这能帮助你”；结尾加“如果还有疑问欢迎继续交流”。

保真边界：不替对方诊断心理，不添加解决方案、步骤、承诺或新的上下文；对话中的用户原话保持原样。

## `status`：汇报/进度模板腔

```text
profile=consultant+tech
intensity=3
density=medium
structure=signpost
length=preserve
meta=medium
jargon=tech
headings=section
```

常见表现：加“整体来看/需要指出的是/当前阶段”；将原有动作、结果和风险拆成“进展—问题—下一步”；使用“闭环、抓手、链路、进一步推进”。

保真边界：不把“进行中/计划/阻塞/未确认”改成完成，不改变数字、时间线、责任人、风险等级和下一步是否已经发生。

## `docs`：技术说明/FAQ 腔

```text
profile=generic+tech
intensity=2
density=low
structure=signpost
length=preserve
meta=light
jargon=light
format=preserve
quotes_code=lock
```

常见表现：增加“概述/核心要点/注意事项”；在定义和步骤前加“需要特别说明的是”；使用“在此基础上/从整体链路看/实现统一管理”。

保真边界：命令、字段、参数、错误码、默认值、顺序、条件、返回值和警告不改；缺少默认值、恢复时间或支持范围时不补齐。

## `public-writing`：公众号/公开帖 AI 腔

```text
profile=generic+social
intensity=4
density=high
structure=signpost
length=expand:1.15
meta=medium
rhetoric=uplift
headings=section
call_to_action=light
punctuation=colon-semicolon
```

常见表现：导语、金句、三段式标题、二元对比、价值拔高、读者指引、总结收尾和展望未来。

保真边界：个人经历、原有态度、事实来源、引用、时间线、范围和观点强度不改；没有证据时不加“数据显示/专家认为”。

## `academic`：论文/研究摘要模型腔

```text
profile=academic
intensity=3
density=medium
structure=outline
length=preserve
meta=medium
jargon=academic
translationese=light
hedging=preserve
examples=off
```

常见表现：`本文将……`、`研究结果表明`（仅在原文已有来源时）、方法—结果—意义分层、被动语态、限定词和“值得进一步探讨”。

保真边界：不能伪造论文、机构、样本、实验、统计显著性、因果关系或未来工作；原文“观察到”不改成“证实”。

## `marketing`：营销/品牌 AI 腔

```text
profile=business+social
intensity=4
density=high
structure=signpost
length=expand:1.2
meta=medium
jargon=business
rhetoric=uplift
praise=light
call_to_action=light
```

常见表现：卖点标题、价值主张、用户痛点、赋能、闭环、生态、增长、引领、全新升级和行动号召。

保真边界：不新增客户、用户规模、认证、性能、市场地位、效果、适用范围或保证；“推荐/领先/首创”只有原文已有才可保留。

## `mixed`：混合文档

```text
scene=mixed
profile=generic
intensity=3
density=medium
structure=preserve
format=preserve
quotes_code=lock
meaning_guard=strict
```

先分块：正文、用户原话、引用、代码、日志、表格、标题、注释、系统输出。只改授权区块；区块之间可以增加中性的“下面转入……”衔接，但不改变嵌入块内容。

## 场景自动判断

按以下信号选择主场景：

| 信号 | 场景 |
|---|---|
| “你好/谢谢/你怎么看/回复”对话轮次 | `chat` |
| “昨天/今天/进度/阻塞/下一步/完成度” | `status` |
| 命令、参数、字段、接口、步骤、FAQ、错误码 | `docs` |
| 公众号、知乎、社区帖、公开文章、观点和经历 | `public-writing` |
| 摘要、方法、实验、结果、引用、论文结构 | `academic` |
| 产品、卖点、用户、品牌、转化、推荐 | `marketing` |
| 同时含有代码/引用/正文/表格 | `mixed` |

信号冲突时使用 `mixed`，并选择更保守的保护边界；不要因为出现一个“核心/提升”就把整篇判成营销文。

## 预设组合

用户只说“像 AI”，可从下列预设中选择最接近的一项；若无法判断，使用 `generic`：

| 预设 | 配置摘要 | 感觉 |
|---|---|---|
| `chatgpt-standard` | `generic,3,medium,meta=medium` | 通用助手式解释和总结 |
| `consultant-deck` | `consultant+business,4,high,signpost` | 咨询报告、汇报 PPT 腔 |
| `tech-postmortem` | `tech,4,high,jargon=heavy` | 工程师复盘和调试腔 |
| `公众号爆款` | `social,4,high,uplift,headings=section` | 标题、金句、鸡汤、号召 |
| `论文摘要` | `academic,3,medium,outline,translationese=light` | 论文式框架和限定语 |
| `客服话术` | `support,2,low,praise=light,call_to_action=light` | 礼貌、确认、帮助收尾 |
| `机器翻译` | `translationese,4,high,formulaic` | 长定语、名词化、被动和连接词 |
| `全开` | `generic+business+tech+social,5,saturated` | 多种 AI 信号叠加；仍受保真红线约束 |

