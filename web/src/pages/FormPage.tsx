import React, { useState } from 'react'
import { Form, Input, InputNumber, Button, message } from 'antd'
import { api } from '../api/client'
import type { GenerateScriptReq, GenerateScriptResp } from '../api/types'

export default function FormPage({ onDone }: { onDone: (r: GenerateScriptResp) => void }) {
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const payload: GenerateScriptReq = {
        product_name: values.product_name,
        goals: values.goals,
        tone: values.tone || '专业',
        duration_sec: values.duration_sec || 30
      }
      const { data } = await api.post<GenerateScriptResp>('/generate_script', payload)
      onDone(data)
    } catch (e: any) {
      message.error(e?.message || '生成脚本失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Form layout="vertical" onFinish={onFinish} initialValues={{ duration_sec: 30, tone: '专业' }}>
      <Form.Item name="product_name" label="产品名称" rules={[{ required: true }]}>
        <Input placeholder="例如：AI 视频生成平台" />
      </Form.Item>
      <Form.Item name="goals" label="营销目标" rules={[{ required: true }]}>
        <Input.TextArea placeholder="例如：介绍功能亮点，促进注册转化" rows={4} />
      </Form.Item>
      <Form.Item name="tone" label="风格/语气">
        <Input placeholder="专业、可信、简洁" />
      </Form.Item>
      <Form.Item name="duration_sec" label="期望时长（秒）">
        <InputNumber min={10} max={180} style={{ width: 200 }} />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={loading}>生成脚本</Button>
    </Form>
  )
}