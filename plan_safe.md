// ... existing code ...
}
// ... existing code ...

# MVP 最小闭环系统平台设计（能输出视频，质量达标）

## 1. MVP 目标与范围
- 目标：用户通过表单输入营销需求 -> AI 生成分镜脚本 -> 自动匹配基础素材 -> 合成时间线 -> 生成成片（1080p，带配音与字幕，可下载）。
- 范围（必须具备）：
  - 表单收集：目标、受众、卖点、渠道、时长、语气
  - 脚本生成：分镜列表（镜头时长/画面描述/旁白/字幕）
  - 素材匹配：基于标签/关键词的本地素材库检索（内置模板素材）
  - 配音（TTS）：中文男女声至少各一款，可调语速音量
  - 字幕：根据脚本生成 SRT，并烧录到视频
  - 渲染导出：1080p，H.264，30fps，MP4
  - 下载与结果页：可获取视频地址、SRT 文件与时间线 JSON

## 2. 高层架构（单机可部署，后续易扩展）
- 前端（Web）：
  - 需求表单页、脚本预览页、进度与结果页（含下载）
- 后端（API 网关 + 服务）：
  - 脚本服务（LLM 调用与提示模板）
  - 素材服务（素材索引、检索、版权校验基本项）
  - TTS 服务（统一接口，支持切换供应商）
  - 渲染服务（时间线组装与 FFmpeg 合成）
  - 任务编排（异步队列 + 状态查询）
- 存储：
  - 对象存储（素材、成片、SRT）
  - 数据库（脚本、任务、素材元数据）
- 中间件：
  - 队列（如 Redis）与日志监控（最小为文件日志 + 健康检查）

## 3. 技术选型（MVP 推荐）
- 后端：Python + FastAPI
  - 原因：生态成熟、视频与音频处理库丰富、快速落地
- 渲染：FFmpeg + MoviePy（时间线拼接更直观，FFmpeg 负责最终高质量编码）
- TTS：
  - 优先：Azure TTS 或科大讯飞（商用品质佳）
  - 备选：Coqui TTS（本地），或 Edge-TTS（简易接入，但稳定性依赖网络）
- 数据库：PostgreSQL（或 SQLite 作为 MVP）
- 缓存与队列：Redis（任务状态与队列）
- 前端：React + Ant Design（表单和进度更快实现）

## 4. 目录结构（建议）
- api/
  - main.py（FastAPI 启动）
  - routers/（scripts.py、materials.py、render.py、tasks.py）
  - services/（llm.py、tts.py、timeline.py、render.py、material_index.py）
  - models/（pydantic schema：Script、Shot、Timeline、Task）
  - storage/（db.py、s3.py 或本地 fs）
- assets/
  - videos/ images/ bgm/ sfx/ fonts/ templates/
- outputs/
  - {taskId}/ result.mp4, subtitles.srt, timeline.json, cover.jpg
- config/
  - app.yaml（TTS 提供商、FFmpeg 路径、存储配置）

## 5. 数据模型（MVP 收敛版）
- Script（脚本）
  - id, objective, audience, tone, durationSec, shots[]
- Shot（分镜）
  - order, durationMs, narration, subtitle, visualDesc, tags[], bgmHint
- Material（素材）
  - id, type(video|image|bgm|sfx), url, meta{fps,duration,colors[],scene}, tags[], license
- Timeline（时间线）
  - tracks: video[], text[], audio[]
  - 每个 clip: {src, in, out, x, y, scale, opacity, transition, z}
- RenderTask（渲染任务）
  - id, scriptId, status(pending|running|done|failed), progress, resultUrls

## 6. API（MVP 版）
- POST /api/v1/scripts/generate
  - body: { objective, audience, sellingPoints[], tone, channel, durationSec }
  - resp: { scriptId, shots[] }
- POST /api/v1/materials/search
  - body: { text?, tags[], limit }
  - resp: { items[] }
- POST /api/v1/render/start
  - body: { scriptId, options:{ size:"1920x1080", fps:30, codec:"H264" } }
  - resp: { taskId }
- GET /api/v1/tasks/{taskId}
  - resp: { status, progress, urls:{ mp4, srt, timeline, cover } }

## 7. 渲染流程（高质量最小闭环）
1) 脚本 -> 时间线组装（timeline.json）
   - 将每个 shot 转为一个或多个 video clip，若无匹配视频则降级为图片（加 Ken Burns 缩放）或模板背景
   - 按 narration 生成 TTS，得到 WAV + 时间戳（SSML 或对齐策略）
   - 根据时间戳生成字幕 SRT（兼容多语言）
2) 音频处理
   - 语音主轨 + BGM：先将 BGM 正常化（-14 LUFS），对旁白区间做 ducking -12 dB
3) 画面与动效
   - 保底：字幕位置与安全区（16:9），1-2 种转场（硬切/交叉溶解）
   - 片头/片尾模板（LOGO + 标语），提供 1 个默认模板
4) 合成与导出
   - 先用 MoviePy 拼接时间线与基本动效
   - 最终用 FFmpeg x264 CRF=18、preset=medium、yuv420p、30fps 输出
   - 将 SRT 烧录版本与外挂版本各导出 1 份
5) 验证与产物落盘
   - 校验分辨率/帧率/码率，生成封面图（截取 0.5s 或关键镜头）

FFmpeg 关键参数示例（参考）：
- 文本字幕烧录（ass/srt 转换后）：
  - -vf "subtitles=subtitles.srt:force_style='FontName=AlibabaPuHuiTi,Outline=1,Shadow=0'"
- 编码质量：
  - -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k

## 8. LLM 脚本生成（可控高质量）
- Prompt 模板（核心约束）：
  - 时长总和≈目标时长；前3秒强钩子；10秒内出现 1-2 个核心卖点
  - 每个镜头给出：durationMs, narration, subtitle, visualDesc, tags[], bgmHint
- 输出后处理：
  - 时长归一（±5%）；空台词过滤；危险词与违规词过滤
- 用户可编辑：提供脚本预览与二次修改后再渲染

## 9. 素材匹配（MVP）
- 素材库初始化：内置 50-200 个免版权视频/图片、10-20 首 BGM、2-5 个音效、2 套字体
- 索引方式：标签 + 关键词（csv/json 索引）；MVP 暂不做向量检索
- 匹配规则（排序）：
  1) 主题/场景标签重合度
  2) 情绪与 bgmHint
  3) 分辨率与清晰度评分
  4) 版权有效性（仅允许白名单来源）
- 兜底：若无视频，使用图片 + 缓慢缩放（Ken Burns）+ 简洁字幕卡

## 10. 质量基线（验收标准）
- 画质与编码：1080p，CRF 18，显著无明显马赛克；字幕清晰可读（≥36px）
- 声音：
  - 人声清晰，无爆音；BGM 在人声时段 ducking 降 10-12 dB
  - 总体响度 ≈ -14 LUFS，避免过响或过小
- 时长：误差 ≤ 5%
- 品牌一致性：片头 LOGO + 统一字体；默认主色一致
- 兼容性：可在主流平台正常上传并通过基础审核（码率与封装正确）

## 11. 任务与重试
- 状态：pending -> running -> done/failed，progress 0-100%
- 失败重试：渲染失败自动重试 1 次；TTS 超时回退至备选 TTS
- 超时：单任务最长 10 分钟，超时判定并失败回收

## 12. 可观测性与日志
- 基础日志：脚本生成耗时、渲染耗时、TTS 调用次数与错误
- 健康检查：/health 返回存活与依赖可用性（DB/Redis/FFmpeg）
- 任务审计：关键信息入库，便于问题追溯

## 13. 安全与合规（MVP）
- 只允许内置白名单素材与商用授权字体
- 脚本输出敏感词过滤（自定义词库）
- 用户数据最小化与隔离（项目维度目录）

## 14. 交互流程（前端 3 页）
1) 需求表单（目标/受众/卖点/时长/语气/渠道）
2) 预览与确认（脚本可编辑；显示素材建议与时长校验）
3) 渲染与下载（进度条；完成后提供 MP4/SRT/JSON 与封面）

## 15. 里程碑与验收
- 里程碑 A（3-5 天）：
  - 表单 -> 脚本 -> 渲染 -> 下载，能产出 30s 成片（含 TTS、字幕、BGM）
- 里程碑 B（+3-5 天）：
  - 片头/片尾模板、字幕样式模板、BGM ducking、质量基线通过
- 验收指标：
  - 5 个不同行业用例均能顺利产出视频；人工主观评分≥7/10
  - 码率、分辨率、帧率与字幕显示符合基线

## 16. 示例时间线 JSON（MVP）
{
  "tracks": {
    "video": [
      {"src":"assets/videos/city_morning.mp4","in":0,"out":2.5,"transition":"cut"},
      {"src":"assets/videos/product_spin.mp4","in":0,"out":3.0,"transition":"crossfade"}
    ],
    "audio": [
      {"src":"outputs/task123/voice.wav","in":0,"out":28.0,"gain":0},
      {"src":"assets/bgm/energetic.mp3","in":0,"out":30.0,"gain":-6,"ducking":[{"start":0,"end":28.0,"gain":-12}]}
    ],
    "text": [
      {"text":"每天轻负担，从一瓶开始","start":0.3,"end":2.3,"x":0.5,"y":0.85,"style":"subtitle_default"}
    ]
  },
  "meta":{"size":"1920x1080","fps":30}
}

## 17. 后续可扩展点（不影响 MVP）
- 向量检索替代标签检索；节拍对齐转场；多尺寸自动适配（9:16/1:1）
- 在线快编：替换镜头、改字后“增量渲染”
- A/B 版本生成与自动化评估