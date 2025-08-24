import React, { useState } from 'react'
import { Button, message, Empty, Descriptions } from 'antd'
import { api, API_ORIGIN } from '../api/client'
import type { BuildTimelineResp, ExportResp } from '../api/types'

export default function ExportPage({ timeline, onExported, onBack, exported }: { timeline: BuildTimelineResp | null, onExported: (e: ExportResp) => void, onBack: () => void, exported: ExportResp | null }) {
  const [loading, setLoading] = useState(false)

  const doExport = async () => {
    if (!timeline) return
    setLoading(true)
    try {
      const { data } = await api.post<ExportResp>('/export', { timeline_id: timeline.timeline_id })
      onExported(data)
    } catch (e: any) {
      message.error(e?.message || '导出失败')
    } finally {
      setLoading(false)
    }
  }

  if (!timeline) return <Empty description="请先构建时间线" />

  return (
    <>
      <Button type="primary" onClick={doExport} loading={loading}>导出</Button>
      {exported && (
        <Descriptions title="导出结果" column={1} style={{ marginTop: 16 }}>
          <Descriptions.Item label="视频"><a href={`${API_ORIGIN}${exported.video_url}`} target="_blank">下载视频</a></Descriptions.Item>
          <Descriptions.Item label="字幕"><a href={`${API_ORIGIN}${exported.srt_url}`} target="_blank">下载SRT</a></Descriptions.Item>
          <Descriptions.Item label="封面"><a href={`${API_ORIGIN}${exported.cover_url}`} target="_blank">下载封面</a></Descriptions.Item>
        </Descriptions>
      )}
      <div style={{ marginTop: 16 }}>
        <Button onClick={onBack}>上一步</Button>
      </div>
    </>
  )
}