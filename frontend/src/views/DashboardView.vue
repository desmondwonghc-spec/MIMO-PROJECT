<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stat-row">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-number">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-icon" v-html="s.icon"></div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="action-section">
      <div class="section-header">
        <h2>快速操作</h2>
      </div>
      <div class="action-grid">
        <router-link to="/jobs" class="action-card">
          <div class="action-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="4" y="6" width="16" height="14" rx="2"/>
              <path d="M8 6V4.5A1.5 1.5 0 019.5 3h5A1.5 1.5 0 0116 4.5V6"/>
            </svg>
          </div>
          <div class="action-text">
            <span class="action-title">管理岗位</span>
            <span class="action-desc">创建、编辑招聘岗位</span>
          </div>
          <svg class="action-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
        </router-link>

        <router-link to="/resumes" class="action-card">
          <div class="action-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M5 3h9l7 7v11a1 1 0 01-1 1H5a1 1 0 01-1-1V4a1 1 0 011-1z"/>
              <path d="M14 3v7h7"/>
            </svg>
          </div>
          <div class="action-text">
            <span class="action-title">上传简历</span>
            <span class="action-desc">解析 PDF / Word 简历</span>
          </div>
          <svg class="action-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
        </router-link>

        <router-link to="/matching" class="action-card">
          <div class="action-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>
            </svg>
          </div>
          <div class="action-text">
            <span class="action-title">开始匹配</span>
            <span class="action-desc">AI 五维度智能评分</span>
          </div>
          <svg class="action-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
        </router-link>

        <router-link to="/settings" class="action-card">
          <div class="action-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1l2.1-2.1M17 7l2.1-2.1"/>
            </svg>
          </div>
          <div class="action-text">
            <span class="action-title">配置 API</span>
            <span class="action-desc">设置 DeepSeek 密钥</span>
          </div>
          <svg class="action-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
        </router-link>
      </div>
    </div>

    <!-- 签名元素：匹配评分预览 -->
    <div class="ring-showcase">
      <div class="section-header">
        <h2>匹配评分预览</h2>
        <span class="section-hint">上传简历后可在此查看评分</span>
      </div>
      <div class="ring-preview">
        <div class="score-ring" :style="{ '--score': latestScore }">
          <svg viewBox="0 0 120 120">
            <circle class="ring-bg" cx="60" cy="60" r="52" />
            <circle class="ring-fill" cx="60" cy="60" r="52" />
          </svg>
          <div class="ring-center">
            <span class="ring-value">{{ latestScore || '—' }}</span>
            <span class="ring-label">综合匹配</span>
          </div>
        </div>
        <div class="ring-dimensions">
          <div class="dim-item" v-for="d in dimensions" :key="d.name">
            <div class="dim-bar-bg">
              <div class="dim-bar-fill" :style="{ width: d.score + '%' }"></div>
            </div>
            <span class="dim-name">{{ d.name }}</span>
            <span class="dim-score">{{ d.score }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const stats = ref([
  { label: '在招岗位', value: '0', icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#E8A838" stroke-width="1.5"><rect x="3" y="5" width="14" height="12" rx="1.5"/><path d="M6 5V3.5A1.5 1.5 0 017.5 2h5A1.5 1.5 0 0114 3.5V5"/></svg>' },
  { label: '收到简历', value: '0', icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#7BAE7F" stroke-width="1.5"><path d="M5 3h7l5 5v9a1 1 0 01-1 1H5a1 1 0 01-1-1V4a1 1 0 011-1z"/><path d="M12 3v5h5"/></svg>' },
  { label: '匹配结果', value: '0', icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#6B8DD6" stroke-width="1.5"><circle cx="7.5" cy="10" r="5"/><circle cx="12.5" cy="10" r="5"/></svg>' },
  { label: '预面试', value: '0', icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#B07BAC" stroke-width="1.5"><path d="M4 4h12a1 1 0 011 1v8a1 1 0 01-1 1H7l-3 3V5a1 1 0 011-1z"/></svg>' },
])

const latestScore = ref(0)
const dimensions = ref([
  { name: '技能匹配', score: 0 },
  { name: '经验匹配', score: 0 },
  { name: '学历匹配', score: 0 },
  { name: '地点匹配', score: 0 },
  { name: '薪资匹配', score: 0 },
])

onMounted(async () => {
  try {
    const [jobsRes, resumesRes] = await Promise.all([
      api.get('/api/v1/jobs', { params: { page_size: 1 } }),
      api.get('/api/v1/resumes', { params: { page_size: 1 } }),
    ])
    stats.value[0].value = String(jobsRes.data.total || 0)
    stats.value[1].value = String(resumesRes.data.total || 0)

    // 尝试获取最新的匹配结果
    const jobs = jobsRes.data.items || []
    if (jobs.length > 0) {
      try {
        const matchRes = await api.get(`/api/v1/matching/results/${jobs[0].id}`, { params: { page_size: 1 } })
        const matches = matchRes.data.items || []
        stats.value[2].value = String(matchRes.data.total || 0)
        if (matches.length > 0) {
          const m = matches[0]
          latestScore.value = m.overall_score || 0
          const dims = m.dimension_scores || {}
          const dimKeys = ['skills_match', 'experience_match', 'education_match', 'location_match', 'salary_match']
          const dimNames = ['技能匹配', '经验匹配', '学历匹配', '地点匹配', '薪资匹配']
          dimensions.value = dimKeys.map((k, i) => ({
            name: dimNames[i],
            score: dims[k]?.score || 0,
          }))
        }
      } catch { /* no matches yet */ }
    }
  } catch (e) { console.error('加载仪表盘数据失败', e) }
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 28px; }

/* === 统计卡片 === */
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--white);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
}

.stat-number {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--graphite);
  letter-spacing: -0.02em;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--stone);
  margin-top: 6px;
}

.stat-icon {
  position: absolute;
  top: 18px;
  right: 18px;
  opacity: 0.6;
}

/* === 区块标题 === */
.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.section-header h2 {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--graphite);
  letter-spacing: -0.01em;
}

.section-hint {
  font-size: 12px;
  color: var(--stone);
}

/* === 快速操作 === */
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04);
  text-decoration: none;
  transition: all 0.15s ease;
}

.action-card:hover {
  box-shadow: var(--shadow-md);
  border-color: rgba(232, 168, 56, 0.2);
}

.action-card:hover .action-arrow { transform: translateX(2px); }

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--amber-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--amber);
  flex-shrink: 0;
}

.action-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--graphite);
}

.action-desc {
  font-size: 12px;
  color: var(--stone);
  margin-top: 2px;
}

.action-arrow {
  color: var(--stone-light);
  flex-shrink: 0;
  transition: transform 0.15s ease;
}

/* === 签名元素：环形评分 === */
.ring-showcase {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04);
}

.ring-preview {
  display: flex;
  align-items: center;
  gap: 48px;
}

.score-ring {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.score-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: var(--paper-alt);
  stroke-width: 8;
}

.ring-fill {
  fill: none;
  stroke: var(--amber);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 326.7;
  stroke-dashoffset: calc(326.7 - (326.7 * var(--score, 0) / 100));
  transition: stroke-dashoffset 1s ease;
  filter: drop-shadow(0 0 6px rgba(232, 168, 56, 0.3));
}

.ring-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.ring-value {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  color: var(--graphite);
  line-height: 1;
  letter-spacing: -0.02em;
}

.ring-label {
  display: block;
  font-size: 11px;
  color: var(--stone);
  margin-top: 4px;
  letter-spacing: 0.02em;
}

/* === 维度条 === */
.ring-dimensions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dim-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 12px;
  align-items: center;
}

.dim-bar-bg {
  height: 6px;
  background: var(--paper-alt);
  border-radius: 3px;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--amber), var(--amber-light));
  border-radius: 3px;
  transition: width 0.8s ease;
}

.dim-name {
  font-size: 12px;
  color: var(--graphite-light);
  min-width: 56px;
}

.dim-score {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--graphite);
  min-width: 28px;
  text-align: right;
}
</style>
