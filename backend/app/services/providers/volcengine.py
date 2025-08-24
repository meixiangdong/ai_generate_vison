import os
from typing import List, Dict
from app.core.config import settings

class VolcengineLLM:
    def __init__(self):
        self.api_base = settings.VOLCENGINE_API_BASE
        self.api_key = settings.VOLCENGINE_API_KEY
        self.model = settings.VOLCENGINE_LLM_MODEL

    def generate_script(self, prompt: str, duration_sec: int) -> List[Dict]:
        # If not configured, return a mocked 5-segment script
        if not self.api_key or not self.api_base:
            segs = []
            per = max(5, duration_sec // 6)
            for i in range(5):
                segs.append({"index": i, "text": f"第{i+1}段：{prompt} - 要点{i+1}", "duration_sec": per})
            return segs

        # TODO: integrate with real Volcengine (Doubao) chat completion API here
        segs = []
        per = max(5, duration_sec // 6)
        for i in range(5):
            segs.append({"index": i, "text": f"【Volcengine/Doubao】{prompt} - 要点{i+1}", "duration_sec": per})
        return segs

class VolcengineTTS:
    def __init__(self):
        self.api_key = settings.VOLCENGINE_API_KEY
        self.voice = settings.VOLCENGINE_TTS_VOICE
        self.speed = settings.VOLCENGINE_TTS_SPEED

    def synthesize(self, text: str) -> str:
        # Without real credentials, skip TTS and return empty string (caller can fall back to silent audio)
        if not self.api_key:
            return ""
        # TODO: integrate with real Volcengine TTS, save wav/mp3 to outputs and return path
        return ""  # placeholder