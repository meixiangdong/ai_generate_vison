import os
from typing import List, Dict, Tuple
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ColorClip, ImageClip, concatenate_videoclips, CompositeVideoClip
from app.core.config import settings

def _text_image(text: str, size=(1280, 720), bg=(10, 10, 10), fg=(240, 240, 240)) -> Image.Image:
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    # Try a common font; on Windows, "arial.ttf" often exists
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    lines = text.split("\n")
    y = 100
    for line in lines:
        w, h = draw.textsize(line, font=font)
        draw.text(((size[0]-w)//2, y), line, font=font, fill=fg)
        y += h + 10
    return img

def _clip_from_asset_or_text(asset_path: str, caption: str, duration: float, size=(1280, 720)):
    if asset_path and os.path.exists(asset_path) and asset_path.lower().endswith((".jpg", ".jpeg", ".png")):
        base = ImageClip(asset_path).set_duration(duration).resize(newsize=size)
    else:
        # Fallback to color background
        base = ColorClip(size=size, color=(20, 20, 20), duration=duration)

    # Overlay caption as image
    img = _text_image(caption, size=size, bg=(0,0,0,0))
    # Save temp caption image in memory
    caption_clip = ImageClip(img).set_duration(duration)
    composite = CompositeVideoClip([base, caption_clip.set_pos("center")])
    return composite

def render_timeline(items: List[Dict], kind: str = "preview") -> Tuple[str, str, str, float]:
    # Returns (video_path, srt_path, cover_path, total_duration)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(settings.OUTPUTS_DIR, f"{kind}_{ts}.mp4")
    srtfile = os.path.join(settings.SRT_DIR, f"{kind}_{ts}.srt")
    coverfile = os.path.join(settings.COVERS_DIR, f"{kind}_{ts}.jpg")

    clips = []
    srt_lines = []
    current_start = 0.0
    for item in items:
        duration = float(item.get("duration", 5.0))
        caption = item.get("caption", "")
        asset_path = item.get("asset_path", "")
        clip = _clip_from_asset_or_text(asset_path, caption, duration)
        clips.append(clip)
        # Build SRT
        start = current_start
        end = start + duration
        idx = len(srt_lines) + 1
        srt_lines.append(_srt_block(idx, start, end, caption))
        current_start = end

    if not clips:
        clips = [ColorClip(size=(1280, 720), color=(20, 20, 20), duration=3)]

    final = concatenate_videoclips(clips, method="compose")
    # Write cover as first frame
    frame = final.get_frame(0)
    Image.fromarray(frame).save(coverfile)

    # Write video (low bitrate for preview; higher for export)
    bitrate = "800k" if kind == "preview" else "4000k"
    final.write_videofile(
        outfile,
        fps=25,
        codec="libx264",
        audio=False,
        bitrate=bitrate,
        temp_audiofile=None,
        remove_temp=True,
        verbose=False,
        logger=None
    )
    # Write SRT
    with open(srtfile, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    total_duration = final.duration if hasattr(final, "duration") else current_start
    final.close()
    return outfile, srtfile, coverfile, total_duration

def _srt_block(index: int, start: float, end: float, text: str) -> str:
    return f"{index}\n{_to_srt_time(start)} --> {_to_srt_time(end)}\n{text}\n"

def _to_srt_time(t: float) -> str:
    hours = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int(t % 60)
    millis = int((t - int(t)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"