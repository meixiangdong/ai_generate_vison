import { useState } from 'react'
import './App.css'
import { Steps, Card } from 'antd'
import FormPage from './pages/FormPage'
import ScriptPage from './pages/ScriptPage'
import TimelinePage from './pages/TimelinePage'
import PreviewPage from './pages/PreviewPage'
import ExportPage from './pages/ExportPage'
import type { GenerateScriptResp, BuildTimelineResp, PreviewResp, ExportResp } from './api/types'

function App() {
  const [current, setCurrent] = useState(0)
  const [script, setScript] = useState<GenerateScriptResp | null>(null)
  const [timeline, setTimeline] = useState<BuildTimelineResp | null>(null)
  const [previewed, setPreviewed] = useState<PreviewResp | null>(null)
  const [exported, setExported] = useState<ExportResp | null>(null)

  const steps = [
    { title: '填写表单', content: <FormPage onDone={(r) => { setScript(r); setCurrent(1) }} /> },
    { title: '查看脚本', content: <ScriptPage script={script} onBack={() => setCurrent(0)} onNext={() => setCurrent(2)} /> },
    { title: '构建时间线', content: <TimelinePage script={script} onBack={() => setCurrent(1)} onBuilt={(t) => { setTimeline(t); setCurrent(3) }} /> },
    { title: '生成预览', content: <PreviewPage timeline={timeline} onBack={() => setCurrent(2)} onPreview={(p) => { setPreviewed(p); setCurrent(4) }} /> },
    { title: '导出成片', content: <ExportPage timeline={timeline} exported={exported} onBack={() => setCurrent(3)} onExported={(e) => setExported(e)} /> },
  ]

  return (
    <div style={{ maxWidth: 920, margin: '24px auto', padding: 16 }}>
      <Steps current={current} items={steps.map(s => ({ title: s.title }))} />
      <Card style={{ marginTop: 16 }}>{steps[current].content}</Card>
    </div>
  )
}

export default App
