<template>
  <div class="settings-page">
    <h2>系统设置</h2>
    <div class="settings-card">
      <h3>🤖 DeepSeek API 配置</h3>
      <div class="form-group">
        <label>API 密钥</label>
        <div class="input-row">
          <input
            v-model="apiKey"
            :type="showKey ? 'text' : 'password'"
            placeholder="sk-..."
          />
          <button class="btn btn-small" @click="showKey = !showKey">
            {{ showKey ? '🙈 隐藏' : '👁️ 显示' }}
          </button>
        </div>
        <p v-if="settings?.deepseek_api_key_set" class="hint success">
          ✅ 已配置: {{ settings.deepseek_api_key_masked }}
        </p>
      </div>
      <div class="form-group">
        <label>API 地址</label>
        <input v-model="baseUrl" placeholder="https://api.deepseek.com" />
      </div>
      <div class="form-actions">
        <button class="btn btn-secondary" @click="testConnection" :disabled="testing">
          {{ testing ? '测试中...' : '🔗 测试连接' }}
        </button>
        <button class="btn btn-primary" @click="saveSettings" :disabled="saving">
          {{ saving ? '保存中...' : '💾 保存' }}
        </button>
      </div>
      <div v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
        {{ testResult.message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import type { SettingsResponse, APITestResponse } from '../types'

const settings = ref<SettingsResponse | null>(null)
const apiKey = ref('')
const baseUrl = ref('https://api.deepseek.com')
const showKey = ref(false)
const testing = ref(false)
const saving = ref(false)
const testResult = ref<APITestResponse | null>(null)

const fetchSettings = async () => {
  try {
    const { data } = await api.get<SettingsResponse>('/api/v1/settings')
    settings.value = data
    baseUrl.value = data.deepseek_base_url
  } catch (e) {
    console.error('获取设置失败', e)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const payload: any = {}
    if (apiKey.value) payload.deepseek_api_key = apiKey.value
    if (baseUrl.value) payload.deepseek_base_url = baseUrl.value
    const { data } = await api.put<SettingsResponse>('/api/v1/settings', payload)
    settings.value = data
    apiKey.value = ''
    alert('设置已保存')
  } catch (e) {
    console.error('保存设置失败', e)
  } finally {
    saving.value = false
  }
}

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  try {
    const { data } = await api.post<APITestResponse>('/api/v1/settings/test-api', {
      api_key: apiKey.value || undefined,
      base_url: baseUrl.value || undefined,
    })
    testResult.value = data
  } catch (e) {
    testResult.value = { success: false, message: '请求失败', model: '' }
  } finally {
    testing.value = false
  }
}

onMounted(fetchSettings)
</script>

<style scoped>
h2 { margin: 0 0 20px; }
.settings-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  max-width: 600px;
}
.settings-card h3 { margin: 0 0 20px; font-size: 16px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px; color: #666; font-weight: 500; }
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}
.input-row { display: flex; gap: 8px; }
.input-row input { flex: 1; }
.form-actions { display: flex; gap: 12px; margin-top: 20px; }
.btn { padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; border: none; }
.btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.btn-secondary { background: #f0f0f0; color: #666; }
.btn-small { padding: 6px 12px; font-size: 12px; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.hint { font-size: 12px; color: #999; margin: 4px 0 0; }
.hint.success { color: #52c41a; }
.test-result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
}
.test-result.success { background: #e6f7e6; color: #52c41a; }
.test-result.error { background: #fff1f0; color: #ff4d4f; }
</style>
