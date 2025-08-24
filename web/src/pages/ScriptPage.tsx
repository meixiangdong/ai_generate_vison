import React from 'react'
import { List, Button, Empty } from 'antd'
import type { GenerateScriptResp } from '../api/types'

export default function ScriptPage({ script, onNext, onBack }: { script: GenerateScriptResp | null, onNext: () => void, onBack: () => void }) {
  if (!script) return <Empty description="请先生成脚本" />
  return (
    <>
      <List
        header="脚本分段"
        bordered
        dataSource={script.segments}
        renderItem={seg => <List.Item>{seg.index + 1}. {seg.text}（{seg.duration_sec}s）</List.Item>}
      />
      <div style={{ marginTop: 16 }}>
        <Button onClick={onBack} style={{ marginRight: 8 }}>返回修改</Button>
        <Button type="primary" onClick={onNext}>确认并构建时间线</Button>
      </div>
    </>
  )
}