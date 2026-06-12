<template>
  <div class="jobs-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="search-field">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索岗位名称、部门..."
            class="search-input"
            @input="debouncedFetch"
          />
        </div>
      </div>
      <router-link to="/jobs/create" class="btn btn-primary">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 1v12M1 7h12"/></svg>
        创建岗位
      </router-link>
    </div>

    <!-- 岗位列表 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="jobs.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="var(--stone-light)" stroke-width="1.5">
          <rect x="8" y="12" width="32" height="28" rx="3"/>
          <path d="M14 12V8a3 3 0 013-3h14a3 3 0 013 3v4"/>
          <path d="M16 22h16M16 28h10"/>
        </svg>
      </div>
      <p class="empty-title">还没有岗位</p>
      <p class="empty-desc">创建第一个岗位开始招聘</p>
    </div>

    <div v-else class="job-list">
      <div
        v-for="job in jobs"
        :key="job.id"
        class="job-row"
        @click="goToDetail(job.id)"
      >
        <div class="job-main">
          <div class="job-title-row">
            <h3 class="job-title">{{ job.title }}</h3>
            <span class="status-dot" :class="'dot-' + job.status"></span>
            <span class="status-text">{{ statusLabels[job.status] }}</span>
          </div>
          <div class="job-meta">
            <span class="meta-item">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M7 1.5C4.5 1.5 2.5 3.5 2.5 6S7 12.5 7 12.5s4.5-4 4.5-6.5S9.5 1.5 7 1.5z"/><circle cx="7" cy="6" r="1.5"/></svg>
              {{ job.location }}
            </span>
            <span v-if="job.department" class="meta-item">{{ job.department }}</span>
            <span v-if="job.salary_range" class="meta-item salary">
              ¥{{ (job.salary_range.min / 1000).toFixed(0) }}k – {{ (job.salary_range.max / 1000).toFixed(0) }}k
            </span>
          </div>
        </div>
        <div class="job-right">
          <div class="job-tags">
            <span v-for="tag in job.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <svg class="row-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4l4 4-4 4"/></svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import type { Job, PaginatedResponse } from '../types'

const router = useRouter()
const jobs = ref<Job[]>([])
const loading = ref(true)
const searchQuery = ref('')

let debounceTimer: ReturnType<typeof setTimeout>
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchJobs, 300)
}

const statusLabels: Record<string, string> = {
  draft: '草稿',
  active: '招聘中',
  paused: '已暂停',
  closed: '已关闭',
}

const fetchJobs = async () => {
  loading.value = true
  try {
    const { data } = await api.get<PaginatedResponse<Job>>('/api/v1/jobs', {
      params: { search: searchQuery.value || undefined },
    })
    jobs.value = data.items
  } catch (e) {
    console.error('获取岗位列表失败', e)
  } finally {
    loading.value = false
  }
}

const goToDetail = (id: string) => router.push(`/jobs/${id}`)

onMounted(fetchJobs)
</script>

<style scoped>
.jobs-page { display: flex; flex-direction: column; gap: 16px; }

/* === 工具栏 === */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.search-field {
  position: relative;
  width: 320px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--stone);
}

.search-input {
  padding-left: 36px;
  border-color: var(--stone-light);
}

/* === 岗位列表 === */
.job-list {
  background: var(--white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04);
  overflow: hidden;
}

.job-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.1s ease;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}

.job-row:last-child { border-bottom: none; }
.job-row:hover { background: var(--paper); }

.job-main { flex: 1; min-width: 0; }

.job-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.job-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--graphite);
  margin: 0;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-active { background: var(--sage); }
.dot-draft { background: var(--stone); }
.dot-paused { background: var(--amber); }
.dot-closed { background: var(--coral); }

.status-text {
  font-size: 12px;
  color: var(--stone);
}

.job-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--stone);
}

.meta-item.salary {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--amber);
}

.job-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.job-tags { display: flex; gap: 6px; }

.tag {
  padding: 3px 10px;
  background: var(--amber-glow);
  color: #B8862A;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.01em;
}

.row-arrow {
  color: var(--stone-light);
  transition: transform 0.15s ease;
}

.job-row:hover .row-arrow { transform: translateX(2px); }

/* === 空状态 === */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.empty-icon { margin-bottom: 16px; }
.empty-title { font-family: var(--font-display); font-weight: 600; color: var(--graphite); margin-bottom: 4px; }
.empty-desc { font-size: 13px; color: var(--stone); }

/* === 加载状态 === */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: var(--stone);
  font-size: 13px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--stone-light);
  border-top-color: var(--amber);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
