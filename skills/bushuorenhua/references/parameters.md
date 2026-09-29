# 参数手册

这份手册只负责参数解析。规则冲突时，以 `SKILL.md` 的保真合同和用户直接指定的禁改项为准。

## 配置语法

参数可以写在用户指令中，也可以放进请求级配置块：

```text
[bushuorenhua]
scene=public-writing
profile=generic+marketing
intensity=4
density=0.65
structure=signpost
length=expand:1.20
meta=medium
jargon=business
hedging=preserve
repetition=moderate
format=preserve
punctuation=colon-semicolon
meaning_guard=strict
audit=brief
[/bushuorenhua]
```

值不区分大小写；中文别名按下表归一化。未知参数不猜含义：`audit=brief` 时列在“未执行参数”里，其他情况忽略并继续用默认值。

## 参数总表

| 参数 | 可选值 | 默认值 | 控制什么 |
|---|---|---|---|
| `scene` | `auto / chat / status / docs / public-writing / academic / marketing / mixed` | `auto` | 主场景与保守边界 |
| `profile` | `generic / consultant / business / marketing / tech / academic / social / support / therapeutic / narrator / translationese / custom`，可用 `+` 叠加 | `generic` | 选哪些 AI 姿态族 |
| `intensity` | `0–5` 或 `none / hint / light / standard / strong / saturated` | `5` | 改动范围和结构侵入程度 |
| `density` | `none / sparse / low / medium / high / saturated` 或 `0–1` | `saturated` | 每段 AI 信号的频率 |
| `structure` | `preserve / signpost / outline / recompose` | `signpost` | 是否增加标题、分点和模板骨架 |
| `length` | `preserve / compress:比例 / expand:比例` | `preserve` | 目标长度；只允许风格性增减 |
| `meta` | `off / light / medium / heavy` | `heavy` | “下面将……/这意味着……”等元话术 |
| `jargon` | `off / light / business / tech / academic / mixed / heavy` | `heavy` | 黑话与名词化密度 |
| `hedging` | `preserve / light / medium / heavy` | `preserve` | 模型式缓和语；严格保真时不改原情态 |
| `certainty` | `preserve / soften / harden` | `preserve` | 断言强弱；严格保真只接受 `preserve` |
| `repetition` | `preserve / moderate / restate / synonym-rotate` | `restate` | 同一判断的复述和同义轮换 |
| `rhetoric` | `off / light / contrast / uplift / slogan / mixed` | `mixed` | 二元对比、拔高、口号和展望 |
| `praise` | `off / light / medium / heavy` | `light` | 对读者、作者或问题的认证式夸奖 |
| `format` | `preserve / markdown / outline / table` | `preserve` | 标题、列表、加粗、表格排版 |
| `punctuation` | `preserve / colon-semicolon / em-dash / parenthetical / mixed` | `mixed` | 破折号、冒号、分号、括号的 AI 痕迹 |
| `rhythm` | `natural / even / formulaic` | `even` | 句长与句式均匀度 |
| `headings` | `off / section / every-paragraph` | `section` | 是否生成标题或小标题 |
| `call_to_action` | `off / light / heavy` | `light` | “欢迎交流/建议收藏/如果需要我可以……” |
| `examples` | `off / reuse-only / synthetic` | `off` | 是否补例子；严格保真只允许 `reuse-only` |
| `translationese` | `off / light / heavy` | `light` | 长定语、被动、`基于/通过/对于`等翻译腔 |
| `language_mix` | `preserve / zh-dominant / en-dominant / bilingual` | `preserve` | 中英混排比例；不翻译标识符和引用 |
| `quotes_code` | `lock / comments-only / user-authorized` | `lock` | 引用、代码及代码旁说明的编辑边界 |
| `meaning_guard` | `strict / rhetorical` | `strict` | 语义保护强度 |
| `audit` | `off / brief / full` | `off` | 是否输出参数和保真审计 |
| `output` | `text / text+audit / annotated` | `text` | 交付形式；`annotated` 只诊断不改写 |

## 数值和档位

### `intensity`

| 值 | 行为 |
|---|---|
| `0 / none` | 原文基本不动，只执行用户点名的表面改动。 |
| `1 / hint` | 每段最多一个 AI 信号，句内加少量元话术。 |
| `2 / light` | 清晰可见的模板词和一两类结构，但保留原句节奏。 |
| `3 / standard` | 默认档。混合 2–4 类 AI 模式，必要时加轻量重复和收束。 |
| `4 / strong` | 允许结构化、黑话、拔高、统一句式同时出现；仍不新增命题。 |
| `5 / saturated` | 高密度模型腔，几乎每个段落都有提示、复述或总结；不代表可以编事实。 |

### `density`

密度按“可识别 AI 信号”估算，不按词数机械计数；代码、命令和引用中的命中不计入。短文至少看完整段，长文按段落和 300 字窗口校准。

| 值 | 目标感觉 |
|---|---|
| `none / 0` | 不主动增加 AI 信号。 |
| `sparse / 0.1–0.2` | 偶尔有一句套话或一个黑话。 |
| `low / 0.2–0.35` | 每 2–3 句有一个轻微信号。 |
| `medium / 0.35–0.55` | 大多数段落可识别模型腔，仍能阅读。 |
| `high / 0.55–0.75` | 结构和词汇都明显模板化。 |
| `saturated / 0.75–1` | 信号密集，重复、拔高和元话术几乎持续出现。 |

`intensity` 决定能不能改变句子/段落结构，`density` 决定选中的模式出现多少次。`intensity=1,density=high` 仍尽量句内加词；`intensity=5,density=low` 可以重排结构，但只留下少量 AI 标记。

### `length`

- `preserve`：输出长度大致保持在原文 `0.9–1.1x`；必须删除的重复可变短，不强行补齐。
- `expand:1.20`：目标约为原文 1.2 倍，新增内容只能来自原文复述、过渡、标题、元评论或不承载命题的姿态层。
- `compress:0.85`：压缩冗余外壳，保留原意；不能用摘要替代正文。
- 未给比例时，`expand` 取 `1.15`，`compress` 取 `0.85`。

如果达到目标长度需要加入事实性例子、来源、数据或承诺，停止扩写并把长度目标视为未满足；`audit=brief/full` 时说明原因。

## `profile` 组合

`profile` 可以用 `+` 叠加，左侧为主风格，右侧为辅风格。例如 `consultant+tech` 先用顾问式结构，再用技术黑话点缀；`social+academic` 只在用户明确要求反差时使用。

| profile | 默认启用的模式族 | 默认不主动加入 |
|---|---|---|
| `generic` | 开场套话、解释旁白、总结、重复、结构化 | 具体行业黑话、心理诊断 |
| `consultant` | 结论先行、框架化、价值拔高、行动项 | 网络热词、过度亲密 |
| `business` | 赋能、抓手、闭环、协同、落地、增长叙事 | 学术引用伪装 |
| `marketing` | `business+social` 的别名：卖点、价值主张、号召和品牌式重复 | 伪造客户、规模、认证和效果 |
| `tech` | 链路、端到端、可观测性、收敛、兜底、根因 | 商业卖点过密 |
| `academic` | 本文/研究/方法—结果—意义、被动、限定语 | 口语热词、客服夸奖 |
| `social` | 标题党、分点、金句、热词、行动号召 | 正式 API 术语改写 |
| `support` | 礼貌确认、元解释、重复用户问题、帮助收尾 | 真实心理诊断 |
| `therapeutic` | 温柔确认、情绪复述、低承诺陪伴话术 | 对用户下确定性诊断；除非用户明确要求戏剧化 |
| `narrator` | 旁白、意义解释、转场、读者引导 | 伪造现场细节 |
| `translationese` | 长定语、被动、`基于/通过/对于`、名词化 | 改动代码和术语 |

## 参数冲突处理

下列请求在 `meaning_guard=strict` 时只做表面近似，不直接执行：

- `certainty=harden`：不能把“可能”改成“必然”；可以加“需要特别指出的是”这类不改命题的包装。
- `certainty=soften` 或 `hedging=heavy`：不能把明确事实改成“或许”；可以增加“从现有信息看”但不得改变事实状态。
- `examples=synthetic`：不能编例子；可重复输入已有例子，或在审计里报告无法满足。
- `language_mix` 要求翻译标识符、引用、产品名：保持原样，除非用户逐项授权。
- `structure=recompose` 与 `format=preserve`：保留原排版；只在段落内部调整句序。
- `length=expand` 与 `density=none`：只允许增加中性标题/连接和原文复述，不强行加入词库。

用户明确要求改变语气强度时，可以把 `meaning_guard` 设为 `rhetorical`。即使如此，也不能新增事实、来源、主体、数字和能力；只允许改变强调方式、评价包装和信息排序。

## 自然语言别名

| 用户说法 | 解析为 |
|---|---|
| “轻微 AI 味” | `intensity=1,density=low,structure=preserve` |
| “标准 ChatGPT 腔” | `profile=generic,intensity=3,density=medium,meta=medium` |
| “很重的咨询顾问腔” | `profile=consultant,intensity=4,density=high,structure=signpost,jargon=business` |
| “技术 AI 黑话拉满” | `profile=tech,intensity=5,density=saturated,jargon=heavy` |
| “扩写但别编东西” | `length=expand:1.2,meaning_guard=strict,examples=reuse-only` |
| “保留句子和段落” | `structure=preserve,format=preserve,length=preserve` |
| “允许重组” | `structure=recompose,format=preserve` |
| “像公众号爆款 AI 文” | `profile=social,rhetoric=uplift,headings=section,call_to_action=light` |
| “像论文摘要但不能造数据” | `profile=academic,scene=academic,examples=off,meaning_guard=strict` |
| “只给结果，别解释” | `audit=off,output=text` |
| “告诉我你改了什么” | `audit=brief` |
| “只标问题不改” | `output=annotated` |
