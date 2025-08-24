from pydantic import BaseModel
from typing import List, Optional

class ScriptSegment(BaseModel):
    index: int
    text: str
    duration_sec: int

class GenerateScriptRequest(BaseModel):
    product_name: str
    goals: str
    tone: str
    duration_sec: int = 30

class GenerateScriptResponse(BaseModel):
    script_id: int
    segments: List[ScriptSegment]

class TimelineItem(BaseModel):
    index: int
    asset_path: str
    caption: str
    start: float
    duration: float

class BuildTimelineRequest(BaseModel):
    script_id: int

class BuildTimelineResponse(BaseModel):
    timeline_id: int
    items: List[TimelineItem]

class PreviewRequest(BaseModel):
    timeline_id: int

class PreviewResponse(BaseModel):
    video_url: str
    timeline_id: int

class ExportRequest(BaseModel):
    timeline_id: int

class ExportResponse(BaseModel):
    video_url: str
    srt_url: str
    cover_url: str
    timeline_id: int