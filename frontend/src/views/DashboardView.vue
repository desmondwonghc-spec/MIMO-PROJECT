<template>
  <div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">💼</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.jobs }}</div>
          <div class="stat-label">在招岗位</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📄</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.resumes }}</div>
          <div class="stat-label">收到简历</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.matches }}</div>
          <div class="stat-label">匹配结果</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.interviews }}</div>
          <div class="stat-label">预面试</div>
        </div>
      </div>
    </div>
    <div class="welcome-section">
      <h3>👋 欢迎使用 HR智能简历筛选系统</h3>
      <p>从左侧菜单开始操作，或查看以下快捷入口：</p>
      <div class="quick-actions">
        <router-link to="/jobs" class="action-btn">📋 管理岗位</router-link>
        <router-link to="/resumes" class="action-btn">📤 上传简历</router-link>
        <router-link to="/matching" class="action-btn">🎯 开始匹配</router-link>
        <router-link to="/settings" class="action-btn">⚙️ 配置API</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const stats = ref({ jobs: 0, resumes: 0, matches: 0, interviews: 0 })
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-icon { font-size: 32px; }
.stat-value { font-size: 28px; font-weight: 700; color: #333; }
.stat-label { font-size: 14px; color: #888; margin-top: 4px; }

.welcome-section {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.welcome-section h3 { margin: 0 0 8px; color: #333; }
.welcome-section p { color: #666; margin: 0 0 20px; }

.quick-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.action-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  transition: transform 0.2s;
}
.action-btn:hover { transform: translateY(-2px); }
</style>
