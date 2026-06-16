<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo -->
      <div class="login-brand">
        <svg width="40" height="40" viewBox="0 0 28 28" fill="none">
          <circle cx="14" cy="14" r="12" stroke="#E8A838" stroke-width="2" />
          <circle cx="14" cy="14" r="5" fill="#E8A838" />
          <line x1="14" y1="2" x2="14" y2="7" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="14" y1="21" x2="14" y2="26" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="2" y1="14" x2="7" y2="14" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="21" y1="14" x2="26" y2="14" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <h1>人才洞察</h1>
        <span class="brand-sub">TalentLens</span>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-banner">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="7" cy="7" r="6"/><path d="M7 4v3M7 9.5v.5"/></svg>
        {{ error }}
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label class="field-label">用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            autocomplete="username"
            required
          />
        </div>
        <div class="field">
          <label class="field-label">密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            required
          />
        </div>
        <button type="submit" class="btn-login" :disabled="loading || !username || !password">
          <div v-if="loading" class="spinner"></div>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="login-hint">默认账号: admin / admin123</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) return
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.post('/api/v1/auth/login', {
      username: username.value,
      password: password.value,
    })

    // 存储 token 和用户信息
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    // 跳转到首页
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--paper);
  padding: 20px;
}

.login-card {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 40px;
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 380px;
}

.login-brand {
  text-align: center;
  margin-bottom: 32px;
}

.login-brand h1 {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--graphite);
  margin: 12px 0 2px;
}

.brand-sub {
  font-size: 11px;
  color: var(--stone);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--coral-bg);
  color: var(--coral);
  border-radius: var(--radius-sm);
  font-size: 13px;
  margin-bottom: 16px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--graphite-light);
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}

.login-form input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--stone-light);
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-family: var(--font-body);
  background: var(--white);
  color: var(--graphite);
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.login-form input:focus {
  border-color: var(--amber);
  box-shadow: 0 0 0 3px var(--amber-glow);
  outline: none;
}

.btn-login {
  width: 100%;
  padding: 12px;
  background: var(--amber);
  color: var(--obsidian);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-family: var(--font-body);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s, box-shadow 0.15s;
  margin-top: 4px;
}

.btn-login:hover:not(:disabled) {
  background: #D49A2E;
  box-shadow: 0 2px 8px rgba(232, 168, 56, 0.3);
}

.btn-login:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(28, 31, 38, 0.2);
  border-top-color: var(--obsidian);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.login-hint {
  text-align: center;
  font-size: 12px;
  color: var(--stone);
  margin: 16px 0 0;
}
</style>
