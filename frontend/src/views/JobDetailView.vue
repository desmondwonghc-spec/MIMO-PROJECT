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
.detail-header h2 { font-family: var(--font-display); margin: 0 0 8px; font-size: 20px; font-weight: 700; color: var(--graphite); }
.meta { display: flex; gap: 16px; color: var(--stone); font-size: 13px; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.meta-item.salary { font-family: var(--font-display); font-weight: 600; color: var(--amber); }
.actions { display: flex; gap: 8px; }
.detail-body {
  background: var(--white); border-radius: var(--radius-md); padding: 24px;
  box-shadow: var(--shadow-sm); border: 1px solid rgba(0,0,0,0.04);
}
.section { margin-bottom: 20px; }
.section h3 {
  margin: 0 0 12px; font-family: var(--font-display); font-size: 13px; font-weight: 600;
  color: var(--graphite-light); text-transform: uppercase; letter-spacing: 0.04em;
  padding-bottom: 8px; border-bottom: 1px solid rgba(0,0,0,0.06);
}
.section p { color: var(--graphite-light); line-height: 1.6; font-size: 14px; }
.section ul { color: var(--graphite-light); line-height: 1.8; font-size: 14px; padding-left: 18px; }
.btn { padding: 8px 16px; border-radius: var(--radius-sm); font-size: 13px; font-family: var(--font-body); font-weight: 500; text-decoration: none; cursor: pointer; border: none; transition: all 0.15s; }
.btn-secondary { background: var(--white); color: var(--graphite); border: 1px solid var(--stone-light); }
.btn-secondary:hover { border-color: var(--stone); }
.btn-danger { background: var(--coral-bg); color: var(--coral); }
.btn-danger:hover { background: var(--coral); color: var(--white); }
.loading { text-align: center; padding: 60px; color: var(--stone); font-size: 13px; }
.btn { padding: 8px 16px; border-radius: 6px; font-size: 13px; text-decoration: none; cursor: pointer; border: none; }
.btn-secondary { background: #f0f0f0; color: #666; }
.btn-danger { background: #fff1f0; color: #ff4d4f; }
.loading { text-align: center; padding: 40px; color: #999; }
</style>
