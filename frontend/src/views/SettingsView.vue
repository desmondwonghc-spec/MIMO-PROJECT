<template>
  <div class="settings-page">
    <!-- API 配置卡片 -->
    <div class="config-card">
      <div class="card-header">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="var(--amber)" stroke-width="1.5">
            <circle cx="10" cy="10" r="3"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4"/>
          </svg>
        </div>
        <div>
          <h3 class="card-title">DeepSeek API</h3>
          <p class="card-desc">配置AI服务连接，驱动简历解析、匹配评分等功能</p>
        </div>
      </div>

      <div class="form-grid">
        <div class="field">
          <label class="field-label">API 密钥</label>
          <div class="input-group">
            <input
              v-model="apiKey"
              :type="showKey ? 'text' : 'password'"
              placeholder="sk-..."
              class="field-input"
            />
            <button class="btn btn-ghost btn-sm" @click="showKey = !showKey">
              {{ showKey ? '隐藏' : '显示' }}
            </button>
          </div>
          <p v-if="settings?.deepseek_api_key_set" class="field-hint field-hint--ok">
            已配置 {{ settings.deepseek_api_key_masked }}
          </p>
        </div>

        <div class="field">
          <label class="field-label">API 地址</label>
          <input v-model="baseUrl" placeholder="https://api.deepseek.com" class="field-input" />
        </div>
      </div>

      <div class="card-actions">
        <button class="btn btn-secondary" @click="testConnection" :disabled="testing">
          <svg v-if="!testing" width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 7h4l2-4 2 8 2-4h4"/></svg>
          <div v-else class="spinner-sm"></div>
          {{ testing ? '测试中...' : '测试连接' }}
        </button>
        <button class="btn btn-primary" @click="saveSettings" :disabled="saving">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>

      <!-- 测试结果 -->
      <div v-if="testResult" class="test-banner" :class="testResult.success ? 'banner-ok' : 'banner-err'">
        <svg v-if="testResult.success" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 8.5l4 4 8-8"/></svg>
        <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8" cy="8" r="6"/><path d="M8 5v3M8 10.5v.5"/></svg>
        <span>{{ testResult.message }}</span>
      </div>
    </div>

    <!-- 其他设置占位 -->
    <div class="config-card config-card--muted">
      <div class="card-header">
        <div class="card-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="var(--stone)" stroke-width="1.5">
            <rect x="3" y="5" width="14" height="10" rx="1.5"/><path d="M3 7l7 4 7-4"/>
          </svg>
        </div>
        <div>
          <h3 class="card-title">邮件配置</h3>
          <p class="card-desc">SMTP 设置，用于自动发送面试邀请（Phase 2）</p>
        </div>
      </div>
      <p class="coming-soon">即将推出</p>
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
  } catch (e) {
    console.error('保存失败', e)
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
  } catch {
    testResult.value = { success: false, message: '请求失败，请检查网络', model: '' }
  } finally {
    testing.value = false
  }
}

onMounted(fetchSettings)
</script>

<style scoped>
.settings-page {
  max-width: 560px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-card {
  background: var(--white);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04);
}

.config-card--muted { opacity: 0.7; }

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 24px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--amber-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.config-card--muted .card-icon { background: rgba(0,0,0,0.04); }

.card-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--graphite);
  margin: 0;
}

.card-desc {
  font-size: 12px;
  color: var(--stone);
  margin: 3px 0 0;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--graphite-light);
  margin-bottom: 6px;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.input-group {
  display: flex;
  gap: 8px;
}

.input-group .field-input { flex: 1; }

.btn-sm { padding: 7px 12px; font-size: 12px; }

.field-hint {
  font-size: 11px;
  color: var(--stone);
  margin: 5px 0 0;
}

.field-hint--ok { color: var(--sage); }

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(0,0,0,0.06);
}

/* 测试结果 */
.test-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.banner-ok { background: var(--sage-bg); color: #4A8A4E; }
.banner-err { background: var(--coral-bg); color: var(--coral); }

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--stone-light);
  border-top-color: var(--amber);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.coming-soon {
  font-size: 13px;
  color: var(--stone);
  text-align: center;
  padding: 12px;
  background: var(--paper);
  border-radius: var(--radius-sm);
}
</style>
