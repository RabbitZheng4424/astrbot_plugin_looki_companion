# Looki 陪伴记忆

这个插件不是“相册检索器”，而是为了让助手能了解我们的现实世界：它会把 Looki 的实时事件和最近 12 小时 `moments` 整合成“我们”视角的共同经历摘要，让 AstrBot 更像一起同行的伙伴，而不是冷冰冰地翻记录。

## 设计目标

- 回答“我们刚才去了哪里”“我们刚刚在干嘛”时，输出一段自然语言叙述
- 优先营造共同经历感，而不是暴露底层 `moment`、文件 URL、JSON 结构
- 只处理最近 12 小时内仍可安全使用的 Looki 数据
- 群聊和私聊使用统一工具，但自动应用不同的权限和隐私边界

## 现在的核心能力

- 把最近一段时间的多个时刻整合成连续时间线摘要
- 读取当前或最近几分钟的场景，优先使用实时事件，失败时回退最近 moments
- 在最近 12 小时内做语义回忆搜索
- 汇总今天仍在 12 小时有效期内的经历概览
- 可选先做图片转文字，再把视觉描述并入时间线摘要
- 自动向 Agent 注入路由提示，明确 Looki 与记忆插件、日记插件的分工

## 原本缺失、现已补上

和最初版本相比，当前实现重点补齐了这些部分：

- 工具从“返回结构化 JSON”改为“直接返回一段自然语言摘要”
- 工具边界从底层查询接口改成了 4 个陪伴语义工具
- 增加 12 小时窗口过滤，不再把过期 moments 当作可用画面
- 增加 `enable_in_group_chat` 与 `admin_only` 两个独立权限开关
- 增加可选图片转文字配置与内部调用链路
- 更新了 Agent 路由提示，明确超过 12 小时的问题应交给记忆插件

## Agent 工具

插件会注册以下 4 个工具：

- `looki_get_recent_experience`
  - 用途：获取最近一段时间的共同经历摘要
  - 参数：
    - `minutes`：回看窗口，默认 `120`
    - `focus`：可选关注点，例如“书店”“晚饭”
  - 返回：一段自然语言时间线摘要

- `looki_get_current_scene`
  - 用途：获取当前或最近几分钟的场景
  - 参数：无
  - 返回：一段自然语言场景描述

- `looki_remember_experience`
  - 用途：在最近 12 小时内做语义回忆
  - 参数：
    - `query`：要回忆的对象或经历
  - 返回：一段自然语言回忆

- `looki_get_day_summary`
  - 用途：获取今天仍处于 12 小时有效期内的概览
  - 参数：无
  - 返回：一段自然语言摘要

## 配置项

- `looki_api_key`
  - 必填
  - Looki API Key

- `looki_base_url`
  - 默认值：`https://open.looki.tech/api/v1`
  - 正常无需修改

- `enable_realtime`
  - 默认值：`true`
  - 是否启用 `/realtime/latest-event`

- `enable_in_group_chat`
  - 默认值：`false`
  - 群聊中是否允许使用 Looki

- `admin_only`
  - 默认值：`true`
  - 是否仅管理员/主人可触发 Looki 查询

- `request_timeout`
  - 默认值：`30`
  - 单次请求超时秒数

- `recent_experience_window_minutes`
  - 默认值：`120`
  - 最近经历工具默认回看窗口

- `realtime_cache_seconds`
  - 默认值：`15`
  - 实时事件短缓存

- `moment_summary_max_chars`
  - 默认值：`220`
  - 文本裁剪长度

- `enable_image_captioning`
  - 默认值：`false`
  - 是否开启图片转文字

- `caption_model`
  - 视觉模型名称

- `caption_api_base`
  - 默认值：`https://api.siliconflow.cn/v1`

- `caption_api_key`
  - 自定义视觉模型 API Key

- `enable_debug_logging`
  - 默认值：`false`
  - 是否开启调试日志

- `inject_routing_hint`
  - 默认值：`true`
  - 是否向 Agent 注入 Looki 路由提示

## 群聊权限逻辑

- `enable_in_group_chat = false`
  - 所有群聊都不会触发 Looki 查询

- `enable_in_group_chat = true` 且 `admin_only = true`
  - 仅管理员身份可触发 Looki

- `enable_in_group_chat = true` 且 `admin_only = false`
  - 群聊允许触发 Looki，但回答会自动避免暴露精确位置

## 数据边界

- 插件只处理最近 12 小时内的数据
- 超过 12 小时的 moments 会被内部直接过滤
- 本插件不做过期补偿，不负责长期记忆
- 超过 12 小时的问题应交给记忆插件
- `journals` 仍不在本插件职责范围内

## 调试命令

- `/looki status`
- `/looki me`
- `/looki scene`
- `/looki recent 90`
- `/looki remember the sushi place from earlier`
- `/looki today`

## 推荐问法

- “我们刚才去了哪些地方？”
- “我们刚刚是不是在书店里？”
- “刚才那家店叫什么来着？”
- “今天这半天我们都做了什么？”
- “我们刚刚看到的那杯咖啡还挺好看。”

## 注意事项

- Looki API 速率限制是每分钟 60 次
- `/realtime/latest-event` 是 Beta 能力，可能为空
- 图片 URL 是临时地址，插件只在当前回合内尝试利用，不做长期保存
- 如果 Looki 不可用，插件会优雅降级，不应硬猜现场细节
