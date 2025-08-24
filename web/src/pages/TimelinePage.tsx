import React, { useState } from 'react'
import { Button, List, message, Empty } from 'antd'
import { api } from '../api/client'
import type { GenerateScriptResp, BuildTimelineResp } from '../api/types'

export default function TimelinePage({ script, onBuilt, onBack }: { script: GenerateScriptResp | null, onBuilt: (t: BuildTimelineResp) => void, onBack: () => void }) {
  const [timeline, setTimeline] = useState<BuildTimelineResp | null>(null)
  const [loading, setLoading] = useState(false)

  const build = async () => {
    if (!script) return
    setLoading(true)
    try {
      const { data } = await api.post<BuildTimelineResp>('/build_timeline', { script_id: script.script_id })
      setTimeline(data)
      onBuilt(data)
    } catch (e: any) {
      message.error(e?.message || '构建时间线失败')
    } finally {
      setLoading(false)
    }
  }

  if (!script) return <Empty description="请先生成脚本" />

  return (
    <>
      <Button type="primary" onClick={build} loading={loading}>构建时间线</Button>
      {timeline && (
        <List
          style={{ marginTop: 16 }}
          header="时间线片段"
          bordered
          dataSource={timeline.items}
          renderItem={it => <List.Item>{it.index + 1}. {it.caption}（{it.duration}s） - {it.asset_path || '占位'}</List.Item>}
        />
      )}
      <div style={{ marginTop: 16 }}>
        <Button onClick={onBack}>上一步</Button>
      </div>
    </>
  )
}