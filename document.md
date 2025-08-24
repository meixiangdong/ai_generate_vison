# 项目结构与各文件职责说明

## 后端 backend/

- app/main.py
  - 创建 FastAPI 实例、注册路由、CORS、挂载静态目录（/outputs、/assets、/srt、/covers）；可在启动时确保本地目录存在。

- app/core/config.py
  - 统一读取环境变量（Pydantic Settings），含服务、数据库、存储路径、CORS、Volcengine 配置。

- app/core/db.py
  - 初始化 SQLAlchemy 引擎与 Session，建表；提供 get_db 依赖。

- app/models/
  - 定义 ORM 实体和 Base（如 Script、Timeline、Render 等表结构）。

- app/schemas/
  - 定义 FastAPI 请求/响应的 Pydantic 模型（DTO）。

- app/routers/pipeline.py
  - 核心流程 API：
    - POST /generate_script：调用 LLM 生成分段脚本，写入 Script 表
    - POST /build_timeline：根据脚本生成时间线（素材匹配/时轴计算），写入 Timeline 表
    - POST /preview：调用渲染服务生成预览视频，写入 Render 表
    - POST /export：调用渲染服务导出成片，写入 Render 表

- app/services/
  - materials.py：简易素材匹配（按分段数从 storage/assets 中取素材）
  - render.py：使用 MoviePy/FFmpeg 生成预览/导出的视频与封面、SRT 等
  - providers/volcengine.py：火山引擎（Doubao）LLM 与 TTS 适配层（当前为占位实现，支持无密钥 mock 返回）

- app/utils/
  - 工具函数（如果有的话，比如路径、时间等工具）

---

## 环境与存储

- backend/.env.example：环境变量示例。复制为项目根 .env 后填写。
- storage/
  - assets/ 存放素材
  - outputs/ 产出视频（首次运行会自动创建，或手动创建）
  - srt/ 字幕文件
  - covers/ 封面图

---

## 前端 web/

- Vite + React + TypeScript 项目
- src/pages：页面入口
- src/api：封装调用后端的 API
- 通过 npm run dev 启动本地开发服务器，联调后端接口