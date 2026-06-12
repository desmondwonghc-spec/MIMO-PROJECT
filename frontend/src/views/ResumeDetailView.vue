<template>
  <div class="resume-detail" v-if="resume">
    <!-- 头部 -->
    <div class="detail-header">
      <button class="btn btn-ghost" @click="router.push('/resumes')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 12L6 8l4-4"/></svg>
        返回
      </button>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="handleReparse" :disabled="reparsing">
          {{ reparsing ? '重新解析中...' : '重新解析' }}
        </button>
        <button class="btn btn-danger" @click="handleDelete">删除</button>
      </div>
    </div>

    <!-- 解析状态横幅 -->
    <div v-if="resume.parsing_status !== 'completed'" class="status-banner" :class="'banner-' + resume.parsing_status">
      <div v-if="resume.parsing_status === 'pending' || resume.parsing_status === 'processing'" class="spinner-sm"></div>
      <span v-if="resume.parsing_status === 'pending'">等待解析...</span>
      <span v-else-if="resume.parsing_status === 'processing'">AI 正在解析简历...</span>
      <span v-else-if="resume.parsing_status === 'failed'">解析失败: {{ resume.parsing_error }}</span>
    </div>

    <!-- 候选人概览卡片 -->
    <div class="profile-card" v-if="resume.structured_data">
      <div class="profile-avatar">{{ (resume.structured_data.name || '?').charAt(0) }}</div>
      <div class="profile-info">
        <h2 class="profile-name">{{ resume.structured_data.name || '未知姓名' }}</h2>
        <div class="profile-contacts">
          <span v-if="resume.structured_data.phone">📱 {{ resume.structured_data.phone }}</span>
          <span v-if="resume.structured_data.email">✉️ {{ resume.structured_data.email }}</span>
          <span v-if="resume.structured_data.current_location">📍 {{ resume.structured_data.current_location }}</span>
          <span v-if="resume.structured_data.total_experience_years">
            💼 {{ resume.structured_data.total_experience_years }}年经验
          </span>
        </div>
        <p v-if="resume.structured_data.summary" class="profile-summary">
          {{ resume.structured_data.summary }}
        </p>
      </div>
      <div v-if="resume.structured_data.expected_salary" class="profile-salary">
        <span class="salary-label">期望薪资</span>
        <span class="salary-value">¥{{ (resume.structured_data.expected_salary.amount / 1000).toFixed(0) }}k</span>
      </div>
    </div>

    <!-- 详细信息 -->
    <div class="detail-grid" v-if="resume.structured_data">
      <!-- 技能 -->
      <div class="detail-card" v-if="resume.structured_data.skills?.length">
        <h3 class="card-heading">技能标签</h3>
        <div class="skill-list">
          <span v-for="s in resume.structured_data.skills" :key="s" class="skill-chip">{{ s }}</span>
        </div>
      </div>

      <!-- 工作经历 -->
      <div class="detail-card" v-if="resume.structured_data.work_experience?.length">
        <h3 class="card-heading">工作经历</h3>
        <div class="timeline">
          <div v-for="(exp, i) in resume.structured_data.work_experience" :key="i" class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="exp-header">
                <span class="exp-company">{{ exp.company }}</span>
                <span class="exp-title">{{ exp.title }}</span>
              </div>
              <span class="exp-date">{{ exp.start_date }} — {{ exp.end_date }}</span>
              <ul v-if="exp.highlights?.length" class="exp-highlights">
                <li v-for="h in exp.highlights" :key="h">{{ h }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 教育经历 -->
      <div class="detail-card" v-if="resume.structured_data.education?.length">
        <h3 class="card-heading">教育经历</h3>
        <div v-for="(edu, i) in resume.structured_data.education" :key="i" class="edu-item">
          <span class="edu-school">{{ edu.institution }}</span>
          <span class="edu-detail">{{ edu.major }} · {{ edu.degree }}</span>
          <span class="edu-date">{{ edu.start_year }} — {{ edu.end_year }}</span>
        </div>
      </div>

      <!-- 证书 -->
      <div class="detail-card" v-if="resume.structured_data.certifications?.length">
        <h3 class="card-heading">证书</h3>
        <div class="cert-list">
          <span v-for="c in resume.structured_data.certifications" :key="c" class="cert-item">{{ c }}</span>
        </div>
      </div>
    </div>

    <!-- 原始文件信息 -->
    <div class="file-info">
      <span>📄 {{ resume.original_filename }}</span>
      <span>{{ formatFileSize(resume.file_size) }}</span>
      <span>{{ resume.file_type?.toUpperCase() }}</span>
    </div>
  </div>

  <div v-else class="loading-state"><div class="spinner"></div><span>加载中...</span></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../utils/api'

const router = useRouter()
const route = useRoute()
const resume = ref<any>(null)
const reparsing = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

const fetchResume = async () => {
  try {
    const { data } = await api.get(`/api/v1/resumes/${route.params.id}`)
    resume.value = data
    // 如果还在解析中，启动轮询
    if (data.parsing_status === 'pending' || data.parsing_status === 'processing') {
      if (!pollTimer) {
        pollTimer = setInterval(fetchResume, 2000)
      }
    } else {
      if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
    }
  } catch (e) {
    console.error('获取简历失败', e)
  }
}

const handleReparse = async () => {
  reparsing.value = true
  try {
    const { data } = await api.post(`/api/v1/resumes/${route.params.id}/reparse`)
    resume.value = data
    pollTimer = setInterval(fetchResume, 2000)
  } catch (e) {
    console.error('重新解析失败', e)
  } finally {
    reparsing.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('确定要删除此简历吗？')) return
  try {
    await api.delete(`/api/v1/resumes/${route.params.id}`)
    router.push('/resumes')
  } catch (e) {
    console.error('删除失败', e)
  }
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

onMounted(fetchResume)
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.resume-detail { display: flex; flex-direction: column; gap: 16px; }

/* 头部 */
.detail-header {
  display: flex; align-items: center; justify-content: space-between;
}
.header-actions { display: flex; gap: 8px; }

/* 状态横幅 */
.status-banner {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: var(--radius-sm); font-size: 13px;
}
.banner-pending { background: rgba(0,0,0,0.04); color: var(--stone); }
.banner-processing { background: var(--amber-glow); color: #B8862A; }
.banner-failed { background: var(--coral-bg); color: var(--coral); }

/* 个人信息卡 */
.profile-card {
  display: flex; align-items: flex-start; gap: 20px;
  background: var(--white); border-radius: var(--radius-lg); padding: 24px;
  box-shadow: var(--shadow-sm); border: 1px solid rgba(0,0,0,0.04);
}

.profile-avatar {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, var(--amber), var(--amber-light));
  color: var(--white); display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 700; font-size: 22px; flex-shrink: 0;
}

.profile-info { flex: 1; }
.profile-name {
  font-family: var(--font-display); font-size: 20px; font-weight: 700;
  color: var(--graphite); margin: 0 0 8px;
}
.profile-contacts {
  display: flex; gap: 16px; font-size: 13px; color: var(--stone); margin-bottom: 10px;
}
.profile-summary { font-size: 13px; color: var(--graphite-light); line-height: 1.6; margin: 0; }

.profile-salary {
  text-align: right; flex-shrink: 0;
}
.salary-label { display: block; font-size: 11px; color: var(--stone); text-transform: uppercase; letter-spacing: 0.05em; }
.salary-value {
  font-family: var(--font-display); font-size: 24px; font-weight: 700; color: var(--amber);
}

/* 详情网格 */
.detail-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
.detail-card {
  background: var(--white); border-radius: var(--radius-md); padding: 20px;
  box-shadow: var(--shadow-sm); border: 1px solid rgba(0,0,0,0.04);
}
.card-heading {
  font-family: var(--font-display); font-size: 13px; font-weight: 600;
  color: var(--graphite-light); text-transform: uppercase; letter-spacing: 0.04em;
  margin: 0 0 14px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,0,0,0.06);
}

/* 技能 */
.skill-list { display: flex; gap: 6px; flex-wrap: wrap; }
.skill-chip {
  padding: 4px 12px; background: var(--amber-glow); color: #B8862A;
  border-radius: 4px; font-size: 12px; font-weight: 500;
}

/* 时间线 */
.timeline { position: relative; padding-left: 20px; }
.timeline::before {
  content: ''; position: absolute; left: 5px; top: 4px; bottom: 4px;
  width: 1px; background: var(--stone-light);
}
.timeline-item { position: relative; margin-bottom: 16px; }
.timeline-item:last-child { margin-bottom: 0; }
.timeline-dot {
  position: absolute; left: -19px; top: 5px; width: 9px; height: 9px;
  border-radius: 50%; background: var(--amber); border: 2px solid var(--white);
}
.exp-header { display: flex; gap: 8px; align-items: baseline; margin-bottom: 2px; }
.exp-company { font-weight: 600; color: var(--graphite); font-size: 14px; }
.exp-title { font-size: 13px; color: var(--stone); }
.exp-date { font-size: 12px; color: var(--stone); }
.exp-highlights { margin: 6px 0 0; padding-left: 16px; font-size: 13px; color: var(--graphite-light); line-height: 1.7; }

/* 教育 */
.edu-item { margin-bottom: 10px; }
.edu-item:last-child { margin-bottom: 0; }
.edu-school { font-weight: 600; color: var(--graphite); font-size: 14px; display: block; }
.edu-detail { font-size: 13px; color: var(--graphite-light); }
.edu-date { font-size: 12px; color: var(--stone); margin-left: 8px; }

/* 证书 */
.cert-list { display: flex; flex-direction: column; gap: 6px; }
.cert-item { font-size: 13px; color: var(--graphite-light); padding: 6px 10px; background: var(--paper); border-radius: 4px; }

/* 文件信息 */
.file-info {
  display: flex; gap: 16px; font-size: 12px; color: var(--stone);
  padding: 12px 16px; background: var(--white); border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

/* 通用 */
.spinner {
  width: 18px; height: 18px; border: 2px solid var(--stone-light);
  border-top-color: var(--amber); border-radius: 50%; animation: spin 0.8s linear infinite;
}
.spinner-sm {
  width: 14px; height: 14px; border: 2px solid rgba(184,134,42,0.3);
  border-top-color: #B8862A; border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-state { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 60px; color: var(--stone); }
</style>
