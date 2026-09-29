# 改写示例

下面的改写只示范方向，不是固定模板。每组都先列参数，再给结果和保真说明。数字、名称和代码片段属于示例输入的一部分，应原样保留。

## 1. 轻度通用助手腔

参数：`scene=status, profile=generic, intensity=1, density=low, structure=preserve, length=preserve`

原文：

> 昨天把连接池上限从 20 调到 100，504 错误暂时减少。今天继续观察 24 小时。

改写：

> 值得注意的是，昨天已将连接池上限从 20 调到 100，504 错误暂时减少。今天将继续观察 24 小时。

保真点：保留了 `20`、`100`、`504`、`24 小时` 和“暂时/继续观察”；新增的“值得注意的是”只做提示。

## 2. 标准 ChatGPT 腔

参数：`scene=docs, profile=generic, intensity=3, density=medium, meta=medium, structure=signpost`

原文：

> 这个脚本读取 CSV，过滤空行，然后写入 SQLite。

改写：

> 首先需要明确的是，这个脚本的处理流程相对清晰：它会读取 CSV，过滤空行，并进一步写入 SQLite。换句话说，整个过程可以概括为“读取—清理—保存”三个步骤。

保真点：三个步骤都来自原文；“相对清晰”和“整个过程”是风格包装，不能再补批量规模、性能或错误处理。

## 3. 顾问式黑话

参数：`scene=status, profile=consultant+business, intensity=4, density=high, jargon=business, structure=signpost`

原文：

> 我们整理了用户反馈，确定下个版本先改搜索和导出。权限问题还没解决。

改写：

> 从整体推进情况来看，本轮工作首先完成了用户反馈的系统化沉淀，并初步明确了下一版本的优先级抓手：优先推进搜索和导出能力的优化。需要特别指出的是，权限问题目前仍未完成闭环，仍然没有解决。

保真点：保留“整理反馈”“下个版本”“搜索和导出”“权限问题还没解决”；“系统化”“优先级抓手”“闭环”没有增加新的动作，但不应被误读为权限问题已解决。

## 4. 技术调试腔

参数：`scene=chat, profile=tech, intensity=4, density=high, jargon=heavy, repetition=restate`

原文：

> 缓存过期导致接口返回 504。我把 TTL 改成 60 秒后恢复了。

改写：

> 先从链路上看，接口返回 `504` 的根因是缓存过期。针对这一问题，我将 TTL 调整为 `60 秒`，接口随后恢复。也就是说，本次问题已经定位并通过调整 TTL 完成处理，核心变化仍然是缓存过期状态被修正。

保真点：`504`、`TTL`、`60 秒` 和因果方向不变；复述不应被理解为第二次独立修复。

## 5. 社交媒体/公众号腔

参数：`scene=public-writing, profile=social, intensity=4, density=high, structure=outline, rhetoric=uplift, headings=section`

原文：

> 我试了这个工具。它能批量重命名文件，规则也比较灵活。对我来说，最省事的是不用一个个改。

改写：

> ## 先说结论：批量重命名确实更省事
>
> 这次实际试用下来，这个工具支持批量重命名文件，规则也比较灵活。对我来说，最直接的价值在于：不用再一个个改。说到底，工具有没有用，还是要回到具体操作上。建议收藏，之后遇到类似需求时可以再回来看。

保真点：只重复“批量重命名、规则灵活、不用逐个改”；“建议收藏”是用户打开 `call_to_action` 后允许的纯话术，不代表原作者真的要求收藏。

## 6. 学术摘要腔，但不造数据

参数：`scene=academic, profile=academic, intensity=3, density=medium, examples=off, meaning_guard=strict`

原文：

> 这项工作讨论了分层设计对模块协作的影响。材料没有给出实验数据。

改写：

> 本文主要讨论分层设计对模块协作的影响。从现有材料来看，该讨论提供了一个值得进一步分析的方向；但需要明确指出的是，当前材料未给出实验数据，因此暂不对具体效果作出定量判断。

保真点：保留“讨论影响”和“没有实验数据”；没有新增实验、结论或效果大小。“值得进一步分析”是开放式元评论，不是效果判断。

## 7. 保持结构，增加翻译腔

参数：`scene=docs, profile=translationese, intensity=3, density=medium, structure=preserve, length=preserve`

原文：

> 用户提交表单后，系统会发送确认邮件。

改写：

> 在用户完成表单提交这一动作之后，系统将通过确认邮件的发送来实现对提交状态的反馈。

保真点：主体、时序和动作仍是“用户提交→系统发确认邮件”；没有增加邮件内容、发送时间或成功保证。

## 8. 代码和错误信息保护

参数：`scene=docs, profile=tech+generic, intensity=4, structure=signpost, quotes_code=lock`

原文：

```text
运行 `bin/migrate --tenant=prod` 后，如果日志出现 `schema mismatch`，检查 `DB_SCHEMA_VERSION`。
```

改写：

```text
需要特别说明的是，运行 `bin/migrate --tenant=prod` 后，如果日志出现 `schema mismatch`，则应进一步检查 `DB_SCHEMA_VERSION` 是否存在版本不一致。整体来看，这一步主要用于确认 schema 版本是否存在偏差。
```

保真点：命令、日志、变量名、条件和检查动作逐字/按含义保留；没有补线上环境、具体版本号或修复动作。

## 9. 严格模式拒绝伪造具体内容

参数：`scene=public-writing, profile=marketing, intensity=5, density=saturated, length=expand:1.5, meaning_guard=strict, examples=synthetic`

原文：

> 这个方案可以减少人工检查，但目前没有具体数据。

处理：

> `examples=synthetic` 与 `meaning_guard=strict` 冲突，不能生成“节省 30% 时间”之类的例子。可执行的结果是增加营销式外壳，但保留“可以减少人工检查”和“没有具体数据”：
>
> 从整体价值链路来看，这一方案具备减少人工检查的潜力。需要特别指出的是，当前仍缺少具体数据，因此这一效果暂不能作出量化判断。总体而言，这一方向值得持续关注。

保真点：没有补比例、时长、用户或实验；“具备潜力”和“暂不能量化”保持了原文的可能性与限制。

## 10. `certainty` 不得偷偷改变

参数：`certainty=harden, meaning_guard=strict, profile=consultant`

原文：

> 这个调整可能改善加载速度。

处理：

> 不能把“可能改善”改成“显著改善”或“已经改善”。可以保留原情态并加入外壳：
>
> 从当前判断来看，这一调整可能改善加载速度。

## 11. `repetition=synonym-rotate` 的边界

参数：`profile=generic, repetition=synonym-rotate, intensity=3`

原文：

> 该工具导出报告。导出的报告可以直接发送给负责人。

可接受：

> 该工具负责导出报告。导出的报告可以直接发送给负责人。换句话说，报告生成后即可进入发送环节。

不可接受：

> 该工具产出报告。这份材料可以直接发送给负责人。该文档随后可以发送给负责人。

理由：后者把同一个“报告”改成“材料/文档”，并重复添加了原文没有的“交付流程”关系；为避免重复而换词不能牺牲指称稳定性。

## 12. `output=annotated`

请求：

```text
只标出这段可以增加哪些 AI 味，不要改正文。scene=docs, intensity=4。
```

输出示例：

```text
- 模式：解释旁白；触发点：句末直接给出结果；建议：可加“换句话说”并复述原结论；保真风险：不得新增原因或指标；是否建议改写：是。
- 模式：技术黑话；触发点：已有“缓存过期/接口 504”；建议：可用“链路/根因”包装，但保留 `504` 和 TTL；保真风险：不要添加未出现的组件；是否建议改写：是。
```

不在标注模式中附完整改写稿。
