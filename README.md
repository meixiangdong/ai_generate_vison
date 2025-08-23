# AI 营销视频自动生成平台 - README

本项目让用户通过「表单输入 -> 脚本生成 -> 素材匹配 -> 时间线合成 -> 渲染导出」的最小闭环，快速生成高质量营销视频。遵循：
- 最小闭环：默认配置可直接跑通，输出 1080p 成片（含 TTS、字幕、封面）。
- 可扩展：模型、TTS、检索、渲染均为可插拔适配层。
- 模块化：脚本、素材、时间线、TTS、渲染、任务编排相互解耦。
- 前后端分离：API 契约稳定，前端独立开发与部署。
- 人工审核：脚本、素材、时间线、预览等关键步骤可人工查看并调整。

本 README 以“先框架搭好 -> 打通前后端 API -> 页面可展示 -> 功能逐步落地”的节奏组织。

---

## 1. 模型与 TTS 选型（默认字节豆包，API 调用）
- 默认供应商：字节豆包（Doubao，火山引擎）
  - LLM（文本/多模态）：用于分镜脚本生成、镜头描述增强、标签建议
  - TTS：Volcengine 语音合成
- 可选备用：阿里千问（DashScope）与阿里云智能语音（NLS）
- 统一适配接口（后端 services 层）：
  - LLMProvider: generate_script(input) -> Script; refine_script(input) -> Script
  - MMProvider: caption_image(path)->tags[]（按需）；summarize_video(keyframes)->tags[]
  - TTSProvider: synthesize(text, voice, speed, volume, lang)-> wav_path, timestamps
- 稳定性策略：超时 30s；重试 2 次（退避）；429/5xx 自动降级到备用供应商（可配置）

必需配置（环境变量或 config/app.yaml）：
- VOLCENGINE_ACCESS_KEY_ID
- VOLCENGINE_SECRET_ACCESS_KEY
- VOLCENGINE_REGION（例：cn-north-1）
- DOU_BAO_TEXT_MODEL（例：doubao-text-model）
- DOU_BAO_MULTIMODAL_MODEL（可选）
- VOLC_TTS_VOICE（例：zh_female_1）
- VOLC_TTS_FORMAT（wav）

---

## 2. 存储策略（本地素材与产物 + PostgreSQL）
- 本地目录
  - assets/：第三方或自有素材库（videos/ images/ bgm/ sfx/ fonts/ templates/）
  - outputs/{taskId}/：result.mp4、subtitles.srt、timeline.json、cover.jpg、voice.wav
  - data/：索引与日志（如 data/logs）
- 数据库：PostgreSQL（本地或内网安装）
  - 用途：脚本、素材元数据、任务状态、时间线、审核记录等
  - 连接串：DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
- 第三方素材拉取（可选）
  - 支持 Pexels / Pixabay / Unsplash 等渠道的拉取器（需 API Key）
  - 拉取后进行版权标注与标签化，落库并入本地 assets/（统一路径与命名）

---

## 3. 技术栈（详单）
- 前端
  - React 18 + Vite + TypeScript
  - Ant Design（UI）、React Router（路由）
  - React Query（请求/缓存）、Axios（HTTP）
  - Zustand（轻量状态管理）
- 后端
  - Python 3.10+，FastAPI + Uvicorn
  - SQLAlchemy/SQLModel（推荐 SQLModel）对接 PostgreSQL
  - 渲染：MoviePy（时间线拼接）+ FFmpeg（高质量编码，H.264/CRF=18/30fps）
  - 音频：响度归一（目标 -14 LUFS）、旁白区间 BGM ducking（-10~-12dB）
  - 任务：ThreadPoolExecutor（MVP），后续可替换 Redis/Celery
  - 配置：pydantic-settings 或 YAML（config/app.yaml）
  - 日志/健康检查：logging + /health
- 数据库
  - PostgreSQL 14+（建议），psycopg2-binary 驱动

---

## 4. 目录结构（建议）
- api/
  - main.py（FastAPI 入口）
  - routers/（scripts.py、materials.py、timeline.py、render.py、tasks.py、health.py）
  - services/
    - llm.py（Doubao 默认，Qwen 备选）
    - tts.py（Volcengine 默认，Ali NLS 备选）
    - material_index.py（本地素材索引/检索）
    - material_importers/（pexels.py、pixabay.py、unsplash.py）
    - timeline.py（Shot -> timeline.json）
    - render.py（MoviePy 组装、FFmpeg 导出）
    - audio.py（BGM ducking、响度归一）
  - models/
    - schemas.py（Pydantic/SQLModel：Script、Shot、Material、Timeline、Task 等）
    - db.py（数据库会话与建表）
  - storage/
    - files.py（本地文件系统读写）
    - paths.py（统一路径与命名规范）
  - utils/（config、id、logger）
- web/（前端工程）
  - src/pages、src/components、src/api、src/store、src/routes
- assets/、outputs/、data/、config/

---

## 5. API 契约（首批，用于“先打通联调”）
- POST /api/v1/scripts/generate
  - body: { objective, audience, sellingPoints[], tone, channel, durationSec }
  - resp: { scriptId, shots[] }
- PUT /api/v1/scripts/{scriptId}
  - body: { shots[] }（用户编辑后的脚本）
  - resp: { scriptId, shots[] }
- POST /api/v1/materials/search
  - body: { text?, tags[], limit }
  - resp: { items[] }
- POST /api/v1/timeline/build
  - body: { scriptId, materialLocks? }
  - resp: { timelineJson }
- POST /api/v1/render/preview
  - body: { timelineJson, size:"854x480", fps:30 }
  - resp: { taskId }
- POST /api/v1/render/start
  - body: { scriptId | timelineJson, options:{ size:"1920x1080", fps:30, codec:"H264" } }
  - resp: { taskId }
- GET /api/v1/tasks/{taskId}
  - resp: { status: pending|running|done|failed, progress, urls:{ mp4, srt, timeline, cover } }
- GET /health
  - resp: { ok: true, dependencies:{ db, ffmpeg, provider } }

---

## 6. 端到端流程与人工审核
1) 表单提交（objective/audience/sellingPoints/duration/tone/channel）
2) 脚本生成（Doubao LLM）
   - 审核点 A：前端可编辑 shots（台词/时长/顺序），保存 PUT /scripts/{id}
3) 素材匹配（本地索引；可联动第三方素材拉取器）
   - 审核点 B：Top-N 候选可替换并锁定，生成 materialLocks
4) 时间线组装（timeline.json）
   - 审核点 C：预览字幕样式、片头/片尾模板、BGM 选择
5) 预览渲染（480p）
   - 审核点 D：确认预览后发起正式渲染（1080p）
6) 正式渲染与导出（x264、CRF=18、30fps、yuv420p）
   - 产出：MP4、SRT（外挂+可选烧录）、cover.jpg、timeline.json

---

## 7. 渲染质量基线（MVP）
- 视频：1920x1080、30fps、H.264（libx264）、yuv420p、CRF=18、preset=medium
- 音频：旁白清晰、BGM 响度 -14 LUFS；旁白区间 ducking -10~-12 dB
- 字幕：SRT 外挂 + 可选烧录；字体≥36px，安全区内，中文字体建议商用授权
- 兜底：缺视频时以图片（Ken Burns 缩放）+ 字幕卡保证信息表达

---

## 8. 配置样例（默认 Doubao + 本地存储 + PostgreSQL）
- config/app.yaml（建议）
  - app.env: dev
  - storage.assets_dir: "assets"
  - storage.outputs_dir: "outputs"
  - db.database_url: "postgresql+psycopg2://user:pass@localhost:5432/ai_video"
  - llm.provider: "doubao"; llm.model: "doubao-text-model"
  - tts.provider: "volc"; tts.voice: "zh_female_1"; tts.format: "wav"
  - render.ffmpeg_path: "ffmpeg"; render.size: "1920x1080"; render.fps: 30; render.crf: 18

- Windows 环境变量示例
```bash
set VOLCENGINE_ACCESS_KEY_ID=your_access_key_id
```
```bash
set VOLCENGINE_SECRET_ACCESS_KEY=your_secret_access_key
```
```bash
set VOLCENGINE_REGION=cn-north-1
```
```bash
set DOU_BAO_TEXT_MODEL=doubao-text-model
```
```bash
set DOU_BAO_MULTIMODAL_MODEL=doubao-mm-model
```
```bash
set VOLC_TTS_VOICE=zh_female_1
```
```bash
set DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/ai_video
```

- 第三方素材（可选）
```bash
set PEXELS_API_KEY=your_pexels_key
```
```bash
set PIXABAY_API_KEY=your_pixabay_key
```
```bash
set UNSPLASH_ACCESS_KEY=your_unsplash_key
```

---

## 9. 快速启动（先框架与联调）
- 安装后端依赖（示例）
```bash
pip install fastapi uvicorn[standard] pydantic-settings sqlmodel sqlalchemy psycopg2-binary moviepy
```
```bash
pip install opencv-python pillow pyyaml python-multipart
```

- 初始化数据库（确保本机 PostgreSQL 已创建数据库与用户）
```bash
psql -U postgres -c "CREATE DATABASE ai_video;"
```
```bash
psql -U postgres -c "CREATE USER ai_user WITH PASSWORD 'ai_pass';"
```
```bash
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_video TO ai_user;"
```

- 启动后端（默认 8000）
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

- 健康检查
```bash
curl http://localhost:8000/health
```

- 初始化前端（web/）
```bash
npm create vite@latest web -- --template react-ts
```
```bash
cd web
```
```bash
npm i antd axios @tanstack/react-query react-router-dom zustand
```
```bash
npm run dev
```

- 前后端联调必经路径
  - 表单 -> POST /scripts/generate -> 展示/编辑 -> PUT /scripts/{id}
  - 素材页 -> POST /materials/search -> 锁定 materialLocks
  - 时间线页 -> POST /timeline/build -> 摘要预览
  - 渲染页 -> POST /render/preview -> 480p 预览 -> POST /render/start -> 轮询 /tasks/{id} -> 下载链接

---

## 10. 第三方素材拉取（可选）
- Importers（services/material_importers/）
  - pexels.py / pixabay.py / unsplash.py：按关键词/标签拉取
- 流程
  1) 拉取 -> 本地落盘 assets/ 对应子目录
  2) 识别基本元数据（分辨率、时长、帧率、主色等），打标签
  3) 入库（materials 表）并入本地索引
- 合规
  - 仅拉取允许商用的素材；保留来源与授权字段；到期提醒；黑名单过滤

---

## 11. 任务与容错
- 任务状态：pending -> running -> done/failed，progress 0-100%
- 超时：单任务 10 分钟（可配置）
- 重试：渲染失败自动重试 1 次；TTS/LLM 超时自动切换备用供应商
- 观测：记录 LLM/TTS/渲染耗时与错误，/health 检查 DB/FFmpeg/Provider

---

## 12. 路线图（分步落地）
- 阶段 0：骨架搭建与联调（2-3 天）
  - 完成 API 框架与 Mock 返回，前端页面打通展示
- 阶段 1：最小闭环（3-5 天）
  - 接入 Doubao LLM 与 Volc TTS；本地素材检索；480p 预览与 1080p 导出
- 阶段 2：质量增强（3-5 天）
  - BGM ducking、模板（片头/片尾/字幕样式）、审计日志与审核开关
- 阶段 3：扩展能力
  - 第三方素材稳定接入、向量检索、多尺寸导出、快编与增量渲染

---

## 13. FAQ
- 无法连接数据库？
  - 检查 DATABASE_URL，确认 Postgres 用户/库已创建且有权限
- TTS 合成失败？
  - 检查 VOLCENGINE* 环境变量与区域；降低并发；尝试备用供应商
- 渲染失败或耗时长？
  - 检查 FFmpeg 是否可执行；调低分辨率/CRF；检查素材分辨率与编码
- 字幕乱码或字体不生效？
  - 确认字体文件存在且为商用授权；优先使用外挂 SRT，必要时再烧录

---
 README 初始化后端与前端骨架，并将 Doubao/Volcengine 作为默认模型与 TTS 接入，数据库直连 PostgreSQL，素材/产出/SRT/封面使用本地目录管理，优先完成“表单 -> 脚本 -> 时间线 -> 预览 -> 导出”的联调闭环。
 