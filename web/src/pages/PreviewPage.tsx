import React, { useState } from 'react'
import { Button, message, Empty } from 'antd'
import { api, API_ORIGIN } from '../api/client'
import type { BuildTimelineResp, PreviewResp } from '../api/types'

export default function PreviewPage({ timeline, onPreview, onBack }: { timeline: BuildTimelineResp | null, onPreview: (p: PreviewResp) => void, onBack: () => void }) {
  const [loading, setLoading] = useState(false)
  const [url, setUrl] = useState<string>('')

  const preview = async () => {
    if (!timeline) return
    setLoading(true)
    try {
      const { data } = await api.post<PreviewResp>('/preview', { timeline_id: timeline.timeline_id })
      setUrl(`${API_ORIGIN}${data.video_url}`)
      onPreview(data)
    } catch (e: any) {
      message.error(e?.message || '预览失败')
    } finally {
      setLoading(false)
    }
  }

  if (!timeline) return <Empty description="请先构建时间线" />

  return (
    <>
      <Button type="primary" onClick={preview} loading={loading}>生成预览</Button>
      {url && (
        <div style={{ marginTop: 16 }}>
          <video src={url} controls style={{ width: '100%' }} />
        </div>
      )}
      <div style={{ marginTop: 16 }}>
        <Button onClick={onBack}>上一步</Button>
      </div>
    </>
  )
}