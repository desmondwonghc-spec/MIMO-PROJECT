<template>
  <div class="jobs-page">
    <div class="page-toolbar">
      <input v-model="searchQuery" type="text" placeholder="搜索岗位..." class="search-input" />
      <router-link to="/jobs/create" class="btn btn-primary">+ 创建岗位</router-link>
    </div>
    <div class="jobs-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="jobs.length === 0" class="empty-state">
        <p>📋 暂无岗位，点击上方按钮创建第一个岗位</p>
      </div>
      <div v-else class="job-cards">
        <div v-for="job in jobs" :key="job.id" class="job-card" @click="goToDetail(job.id)">
          <div class="job-header">
            <h3 class="job-title">{{ job.title }}</h3>
            <span class="job-status" :class="'status-' + job.status">{{ statusLabels[job.status] }}</span>
          </div>
          <div class="job-meta">
            <span>📍 {{ job.location }}</span>
            <span v-if="job.department">🏢 {{ job.department }}</span>
            <span v-if="job.salary_range">💰 {{ (job.salary_range.min / 1000).toFixed(0) }}k - {{ (job.salary_range.max / 1000).toFixed(0) }}k</span>
          </div>
          <div class="job-tags">
            <span v-for="tag in job.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
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

const goToDetail = (id: string) => {
  router.push(`/jobs/${id}`)
}

onMounted(fetchJobs)
</script>

<style scoped>
.page-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}
.search-input:focus { border-color: #667eea; }

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
  border: none;
  display: inline-block;
}
.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}

.job-cards { display: flex; flex-direction: column; gap: 12px; }

.job-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.job-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12); }

.job-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.job-title { margin: 0; font-size: 16px; color: #333; }

.job-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.status-active { background: #e6f7e6; color: #52c41a; }
.status-draft { background: #f0f0f0; color: #999; }
.status-paused { background: #fff7e6; color: #faad14; }
.status-closed { background: #fff1f0; color: #ff4d4f; }

.job-meta { display: flex; gap: 16px; font-size: 13px; color: #888; margin-bottom: 8px; }
.job-tags { display: flex; gap: 6px; }
.tag {
  padding: 2px 8px;
  background: #f0f0ff;
  color: #667eea;
  border-radius: 4px;
  font-size: 12px;
}

.loading, .empty-state { text-align: center; padding: 40px; color: #999; }
</style>
