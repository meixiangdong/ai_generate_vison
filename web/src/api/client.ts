import axios from 'axios'

const BASE =
  (import.meta as any).env?.VITE_API_BASE ||
  'http://localhost:8000/api'

export const api = axios.create({
  baseURL: BASE,
  timeout: 30000
})

// 由 baseURL 推导后端的 Origin（去掉 /api 前缀），用于拼接静态资源完整 URL
export const API_ORIGIN = (() => {
  const base = api.defaults.baseURL || ''
  try {
    const u = new URL(base, window.location.origin)
    return `${u.protocol}//${u.host}`
  } catch {
    return window.location.origin
  }
})()