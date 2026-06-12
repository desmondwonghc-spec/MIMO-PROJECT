<template>
  <div class="job-detail-page">
    <div v-if="loading" class="loading">加载中...</div>
    <template v-else-if="job">
      <div class="detail-header">
        <div>
          <h2>{{ job.title }}</h2>
          <div class="meta">
            <span>📍 {{ job.location }}</span>
            <span v-if="job.department">🏢 {{ job.department }}</span>
            <span v-if="job.salary_range">💰 {{ (job.salary_range.min / 1000).toFixed(0) }}k - {{ (job.salary_range.max / 1000).toFixed(0) }}k / 月</span>
          </div>
        </div>
        <div class="actions">
          <router-link :to="`/jobs/${job.id}/edit`" class="btn btn-secondary">✏️ 编辑</router-link>
          <button class="btn btn-danger" @click="handleDelete">🗑️ 删除</button>
        </div>
      </div>
      <div class="detail-body">
        <div class="section">
          <h3>岗位描述</h3>
          <p>{{ job.description }}</p>
        </div>
        <div class="section" v-if="job.responsibilities?.length">
          <h3>岗位职责</h3>
          <ul><li v-for="r in job.responsibilities" :key="r">{{ r }}</li></ul>
        </div>
        <div class="section">
          <h3>任职要求</h3>
          <ul>
            <li v-if="job.requirements.education">学历: {{ job.requirements.education }}</li>
            <li v-if="job.requirements.min_experience_years">经验: {{ job.requirements.min_experience_years }}年以上</li>
            <li v-if="job.requirements.required_skills?.length">技能: {{ job.requirements.required_skills.join('、') }}</li>
            <li v-if="job.requirements.preferred_skills?.length">加分: {{ job.requirements.preferred_skills.join('、') }}</li>
          </ul>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../utils/api'
import type { Job } from '../types'

const router = useRouter()
const route = useRoute()
const job = ref<Job | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get<Job>(`/api/v1/jobs/${route.params.id}`)
    job.value = data
  } catch (e) {
    console.error('获取岗位详情失败', e)
  } finally {
    loading.value = false
  }
})

const handleDelete = async () => {
  if (!confirm('确定要删除此岗位吗？')) return
  try {
    await api.delete(`/api/v1/jobs/${route.params.id}`)
    router.push('/jobs')
  } catch (e) {
    console.error('删除失败', e)
  }
}
</script>

<style scoped>
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.detail-header h2 { margin: 0 0 8px; }
.meta { display: flex; gap: 16px; color: #888; font-size: 14px; }
.actions { display: flex; gap: 8px; }
.detail-body { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.section { margin-bottom: 20px; }
.section h3 { margin: 0 0 12px; font-size: 15px; color: #555; }
.section p { color: #666; line-height: 1.6; }
.section ul { color: #666; line-height: 1.8; }
.btn { padding: 8px 16px; border-radius: 6px; font-size: 13px; text-decoration: none; cursor: pointer; border: none; }
.btn-secondary { background: #f0f0f0; color: #666; }
.btn-danger { background: #fff1f0; color: #ff4d4f; }
.loading { text-align: center; padding: 40px; color: #999; }
</style>
