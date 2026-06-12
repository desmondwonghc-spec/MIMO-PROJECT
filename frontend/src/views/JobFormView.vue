<template>
  <div class="job-form-page">
    <h2>{{ isEdit ? '编辑岗位' : '创建岗位' }}</h2>
    <form @submit.prevent="handleSubmit" class="job-form">
      <div class="form-section">
        <h3>基本信息</h3>
        <div class="form-row">
          <div class="form-group">
            <label>岗位名称 *</label>
            <input v-model="form.title" required placeholder="如：Python高级开发工程师" />
          </div>
          <div class="form-group">
            <label>工作地点 *</label>
            <input v-model="form.location" required placeholder="如：上海" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>所属部门</label>
            <input v-model="form.department" placeholder="如：技术部" />
          </div>
          <div class="form-group">
            <label>工作类型</label>
            <select v-model="form.employment_type">
              <option value="full-time">全职</option>
              <option value="part-time">兼职</option>
              <option value="contract">合同</option>
              <option value="internship">实习</option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3>岗位描述</h3>
        <div class="form-group">
          <label>岗位描述 *</label>
          <textarea v-model="form.description" rows="4" required placeholder="描述岗位的主要工作内容..."></textarea>
        </div>
        <div class="form-group">
          <label>岗位职责（每行一条）</label>
          <textarea v-model="responsibilitiesText" rows="4" placeholder="设计和开发API&#10;代码审查&#10;技术文档编写"></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3>任职要求</h3>
        <div class="form-row">
          <div class="form-group">
            <label>学历要求</label>
            <select v-model="form.requirements.education">
              <option value="">不限</option>
              <option value="high-school">高中</option>
              <option value="associate">大专</option>
              <option value="bachelor">本科</option>
              <option value="master">硕士</option>
              <option value="phd">博士</option>
            </select>
          </div>
          <div class="form-group">
            <label>最低工作年限</label>
            <input v-model.number="form.requirements.min_experience_years" type="number" min="0" />
          </div>
        </div>
        <div class="form-group">
          <label>必备技能（逗号分隔）</label>
          <input v-model="requiredSkillsText" placeholder="Python, FastAPI, MongoDB" />
        </div>
        <div class="form-group">
          <label>加分技能（逗号分隔）</label>
          <input v-model="preferredSkillsText" placeholder="Docker, Kubernetes" />
        </div>
      </div>

      <div class="form-section">
        <h3>薪资范围</h3>
        <div class="form-row">
          <div class="form-group">
            <label>最低月薪（元）</label>
            <input v-model.number="form.salary_range.min" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>最高月薪（元）</label>
            <input v-model.number="form.salary_range.max" type="number" min="0" />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3>标签</h3>
        <div class="form-group">
          <label>标签（逗号分隔）</label>
          <input v-model="tagsText" placeholder="后端, 高级, 远程" />
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="goBack">取消</button>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../utils/api'
import type { Job } from '../types'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => !!route.params.id)
const submitting = ref(false)

const form = ref({
  title: '',
  department: '',
  location: '',
  employment_type: 'full-time',
  description: '',
  requirements: {
    education: '',
    min_experience_years: 0,
    required_skills: [] as string[],
    preferred_skills: [] as string[],
  },
  salary_range: { min: 0, max: 0, currency: 'CNY' },
  tags: [] as string[],
})

const responsibilitiesText = ref('')
const requiredSkillsText = ref('')
const preferredSkillsText = ref('')
const tagsText = ref('')

const goBack = () => router.push('/jobs')

const handleSubmit = async () => {
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      responsibilities: responsibilitiesText.value.split('\n').filter(s => s.trim()),
      tags: tagsText.value.split(',').map(s => s.trim()).filter(Boolean),
      requirements: {
        ...form.value.requirements,
        education: form.value.requirements.education || null,
        required_skills: requiredSkillsText.value.split(',').map(s => s.trim()).filter(Boolean),
        preferred_skills: preferredSkillsText.value.split(',').map(s => s.trim()).filter(Boolean),
      },
    }
    if (isEdit.value) {
      await api.put(`/api/v1/jobs/${route.params.id}`, payload)
    } else {
      await api.post('/api/v1/jobs', payload)
    }
    router.push('/jobs')
  } catch (e) {
    console.error('保存失败', e)
    alert('保存失败，请检查表单')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await api.get<Job>(`/api/v1/jobs/${route.params.id}`)
      form.value.title = data.title
      form.value.department = data.department
      form.value.location = data.location
      form.value.employment_type = data.employment_type
      form.value.description = data.description
      form.value.requirements.education = data.requirements.education || ''
      form.value.requirements.min_experience_years = data.requirements.min_experience_years
      if (data.salary_range) {
        form.value.salary_range = { ...data.salary_range }
      }
      responsibilitiesText.value = (data.responsibilities || []).join('\n')
      requiredSkillsText.value = (data.requirements.required_skills || []).join(', ')
      preferredSkillsText.value = (data.requirements.preferred_skills || []).join(', ')
      tagsText.value = (data.tags || []).join(', ')
    } catch (e) {
      console.error('获取岗位详情失败', e)
    }
  }
})
</script>

<style scoped>
.job-form-page h2 { font-family: var(--font-display); margin: 0 0 20px; color: var(--graphite); font-size: 18px; font-weight: 600; }

.job-form {
  background: var(--white);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04);
}

.form-section { margin-bottom: 24px; }
.form-section h3 {
  margin: 0 0 16px; font-family: var(--font-display); font-size: 13px; font-weight: 600;
  color: var(--graphite-light); text-transform: uppercase; letter-spacing: 0.04em;
  border-bottom: 1px solid rgba(0,0,0,0.06); padding-bottom: 10px;
}

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 12px; color: var(--graphite-light); font-weight: 600; letter-spacing: 0.02em; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--stone-light);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font-body);
  background: var(--white);
  color: var(--graphite);
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  border-color: var(--amber);
  box-shadow: 0 0 0 3px var(--amber-glow);
}
.form-group textarea { resize: vertical; }

.form-actions { display: flex; gap: 12px; justify-content: flex-end; padding-top: 16px; border-top: 1px solid rgba(0,0,0,0.06); }

.btn { padding: 10px 24px; border-radius: var(--radius-sm); font-size: 13px; font-family: var(--font-body); font-weight: 500; cursor: pointer; border: none; transition: all 0.15s; }
.btn-primary { background: var(--amber); color: var(--obsidian); }
.btn-primary:hover { background: #D49A2E; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: var(--paper-alt); color: var(--graphite-light); }
.btn-secondary:hover { background: var(--stone-light); }
</style>
