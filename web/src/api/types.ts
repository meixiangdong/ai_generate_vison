export type ScriptSegment = {
  index: number
  text: string
  duration_sec: number
}

export type GenerateScriptReq = {
  product_name: string
  goals: string
  tone: string
  duration_sec: number
}
export type GenerateScriptResp = {
  script_id: number
  segments: ScriptSegment[]
}

export type BuildTimelineReq = {
  script_id: number
}
export type TimelineItem = {
  index: number
  asset_path: string
  caption: string
  start: number
  duration: number
}
export type BuildTimelineResp = {
  timeline_id: number
  items: TimelineItem[]
}

export type PreviewReq = { timeline_id: number }
export type PreviewResp = { timeline_id: number; video_url: string }

export type ExportReq = { timeline_id: number }
export type ExportResp = {
  timeline_id: number
  video_url: string
  srt_url: string
  cover_url: string
}