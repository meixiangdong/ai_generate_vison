from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.db import get_db
from app.schemas.pipeline import (
    GenerateScriptRequest, GenerateScriptResponse,
    BuildTimelineRequest, BuildTimelineResponse,
    PreviewRequest, PreviewResponse,
    ExportRequest, ExportResponse
)
from app.models.entities import Script, Timeline, Render
from app.services.providers.volcengine import VolcengineLLM
from app.services.materials import simple_match_assets
from app.services.render import render_timeline

router = APIRouter()

@router.post("/generate_script", response_model=GenerateScriptResponse)
def generate_script(req: GenerateScriptRequest, db: Session = Depends(get_db)):
    prompt = f"产品：{req.product_name}\n目标：{req.goals}\n风格：{req.tone}"
    llm = VolcengineLLM()
    segments = llm.generate_script(prompt, req.duration_sec)

    script = Script(prompt=prompt, content=segments)
    db.add(script)
    db.commit()
    db.refresh(script)
    return {"script_id": script.id, "segments": segments}

@router.post("/build_timeline", response_model=BuildTimelineResponse)
def build_timeline(req: BuildTimelineRequest, db: Session = Depends(get_db)):
    script: Script = db.get(Script, req.script_id)
    if not script:
        raise HTTPException(404, "script not found")

    segs: List[Dict] = script.content
    assets = simple_match_assets(segs)
    items = []
    current = 0.0
    for i, seg in enumerate(segs):
        dur = float(seg.get("duration_sec", 5))
        items.append({
            "index": i,
            "asset_path": assets[i] if i < len(assets) else "",
            "caption": seg.get("text", ""),
            "start": current,
            "duration": dur,
        })
        current += dur

    timeline = Timeline(script_id=req.script_id, items=items)
    db.add(timeline)
    db.commit()
    db.refresh(timeline)
    return {"timeline_id": timeline.id, "items": items}

@router.post("/preview", response_model=PreviewResponse)
def preview(req: PreviewRequest, db: Session = Depends(get_db)):
    timeline: Timeline = db.get(Timeline, req.timeline_id)
    if not timeline:
        raise HTTPException(404, "timeline not found")
    video_path, srt_path, cover_path, _ = render_timeline(timeline.items, kind="preview")
    render = Render(timeline_id=timeline.id, kind="preview", video_path=video_path, srt_path=srt_path, cover_path=cover_path)
    db.add(render)
    db.commit()

    # expose as url
    basename = video_path.replace("\\", "/").split("/")[-1]
    return {"video_url": f"/outputs/{basename}", "timeline_id": timeline.id}

@router.post("/export", response_model=ExportResponse)
def export(req: ExportRequest, db: Session = Depends(get_db)):
    timeline: Timeline = db.get(Timeline, req.timeline_id)
    if not timeline:
        raise HTTPException(404, "timeline not found")
    video_path, srt_path, cover_path, _ = render_timeline(timeline.items, kind="export")
    render = Render(timeline_id=timeline.id, kind="export", video_path=video_path, srt_path=srt_path, cover_path=cover_path)
    db.add(render)
    db.commit()

    return {
        "video_url": f"/outputs/{video_path.replace('\\', '/').split('/')[-1]}",
        "srt_url": f"/srt/{srt_path.replace('\\', '/').split('/')[-1]}",
        "cover_url": f"/covers/{cover_path.replace('\\', '/').split('/')[-1]}",
        "timeline_id": timeline.id,
    }