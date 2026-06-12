<template>
  <div class="resumes-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="search-field">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/>
          </svg>
          <input v-model="searchQuery" placeholder="搜索姓名、文件名..." class="search-input" @input="debouncedFetch" />
        </div>
        <div class="filter-pills">
          <button
            v-for="f in filters"
            :key="f.value"
            class="pill"
            :class="{ 'pill--active': activeFilter === f.value }"
            @click="activeFilter = f.value; fetchResumes()"
          >{{ f.label }}</button>
        </div>
      </div>
      <label class="btn btn-primary upload-btn">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 10V2M3.5 5.5L7 2l3.5 3.5"/><path d="M1 9v3a1 1 0 001 1h10a1 1 0 001-1v-3"/></svg>
        上传简历
        <input type="file" accept=".pdf,.docx" multiple @change="handleUpload" class="file-input" />
      </label>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-banner">
      <div class="spinner-sm"></div>
      <span>正在上传 {{ uploadingCount }} 个文件...</span>
    </div>

    <!-- 简历列表 -->
    <div v-if="loading" class="loading-state"><div class="spinner"></div><span>加载中...</span></div>

    <div v-else-if="resumes.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="var(--stone-light)" stroke-width="1.5">
          <path d="M10 6h18l10 10v26a2 2 0 01-2 2H10a2 2 0 01-2-2V8a2 2 0 012-2z"/>
          <path d="M28 6v10h10"/><path d="M16 26h16M16 32h10"/>
        </svg>
      </div>
      <p class="empty-title">简历库为空</p>
      <p class="empty-desc">上传 PDF 或 Word 文件，AI 将自动解析候选人信息</p>
    </div>

    <div v-else class="resume-list">
      <div
        v-for="resume in resumes"
        :key="resume.id"
        class="resume-row"
        @click="goToDetail(resume.id)"
      >
        <div class="resume-avatar">
          {{ getInitial(resume) }}
        </div>
        <div class="resume-main">
          <div class="resume-name-row">
            <span class="resume-name">{{ getDisplayName(resume) }}</span>
            <span class="parse-badge" :class="'badge-' + resume.parsing_status">
              {{ statusLabels[resume.parsing_status] }}
            </span>
          </div>
          <div class="resume-meta">
            <span>{{ resume.original_filename }}</span>
            <span>{{ formatFileSize(resume.file_size) }}</span>
            <span v-if="resume.structured_data?.total_experience_years">
              {{ resume.structured_data.total_experience_years }}年经验
            </span>
            <span v-if="resume.structured_data?.current_location">
              {{ resume.structured_data.current_location }}
            </span>
          </div>
          <div v-if="resume.structured_data?.skills?.length" class="resume-skills">
            <span v-for="s in resume.structured_data.skills.slice(0, 5)" :key="s" class="skill-tag">{{ s }}</span>
          </div>
        </div>
        <div class="resume-right">
          <span class="resume-time">{{ formatTime(resume.created_at) }}</span>
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

const router = useRouter()
const resumes = ref<any[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeFilter = ref('')
const uploading = ref(false)
const uploadingCount = ref(0)

const filters = [
  { label: '全部', value: '' },
  { label: '已解析', value: 'completed' },
  { label: '解析中', value: 'processing' },
  { label: '待解析', value: 'pending' },
  { label: '失败', value: 'failed' },
]

const statusLabels: Record<string, string> = {
  pending: '待解析',
  processing: '解析中',
  completed: '已解析',
  failed: '解析失败',
}

let debounceTimer: ReturnType<typeof setTimeout>
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchResumes, 300)
}

const fetchResumes = async () => {
  loading.value = true
  try {
    const params: any = { page: 1, page_size: 50 }
    if (activeFilter.value) params.status = activeFilter.value
    if (searchQuery.value) params.search = searchQuery.value
    const { data } = await api.get('/api/v1/resumes', { params })
    resumes.value = data.items
  } catch (e) {
    console.error('获取简历列表失败', e)
  } finally {
    loading.value = false
  }
}

const handleUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return

  uploading.value = true
  uploadingCount.value = files.length

  for (const file of Array.from(files)) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source', 'upload')
      await api.post('/api/v1/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } catch (e) {
      console.error(`上传失败: ${file.name}`, e)
    }
  }

  uploading.value = false
  input.value = ''
  await fetchResumes()

  // 3秒后自动刷新一次（等待异步解析）
  setTimeout(fetchResumes, 3000)
  setTimeout(fetchResumes, 8000)
}

const getInitial = (r: any) => {
  const name = r.structured_data?.name || r.original_filename || '?'
  return name.charAt(0).toUpperCase()
}

const getDisplayName = (r: any) => {
  return r.structured_data?.name || r.original_filename || '未知'
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

const formatTime = (iso: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const goToDetail = (id: string) => router.push(`/resumes/${id}`)

onMounted(fetchResumes)
</script>

<style scoped>
.resumes-page { display: flex; flex-direction: column; gap: 16px; }

/* 工具栏 */
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.toolbar-left { display: flex; align-items: center; gap: 12px; flex: 1; }

.search-field { position: relative; width: 260px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--stone); }
.search-input { padding-left: 36px; }

.filter-pills { display: flex; gap: 4px; }
.pill {
  padding: 6px 14px;
  border-radius: 20px;
  border: none;
  background: transparent;
  color: var(--stone);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: var(--font-body);
}
.pill:hover { background: rgba(0,0,0,0.04); }
.pill--active { background: var(--amber-glow); color: #B8862A; }

.upload-btn { position: relative; cursor: pointer; }
.file-input { position: absolute; opacity: 0; width: 100%; height: 100%; cursor: pointer; left: 0; top: 0; }

/* 上传进度 */
.upload-banner {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; background: var(--amber-glow); border-radius: var(--radius-sm);
  font-size: 13px; color: #B8862A;
}

/* 列表 */
.resume-list {
  background: var(--white); border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm); border: 1px solid rgba(0,0,0,0.04); overflow: hidden;
}

.resume-row {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 20px; cursor: pointer;
  transition: background 0.1s ease; border-bottom: 1px solid rgba(0,0,0,0.04);
}
.resume-row:last-child { border-bottom: none; }
.resume-row:hover { background: var(--paper); }

.resume-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--amber-glow); color: #B8862A;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 700; font-size: 15px; flex-shrink: 0;
}

.resume-main { flex: 1; min-width: 0; }

.resume-name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.resume-name { font-family: var(--font-display); font-weight: 600; font-size: 14px; color: var(--graphite); }

.parse-badge {
  padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500;
}
.badge-completed { background: var(--sage-bg); color: #4A8A4E; }
.badge-processing { background: var(--amber-glow); color: #B8862A; }
.badge-pending { background: rgba(0,0,0,0.04); color: var(--stone); }
.badge-failed { background: var(--coral-bg); color: var(--coral); }

.resume-meta {
  display: flex; gap: 12px; font-size: 12px; color: var(--stone);
  margin-bottom: 6px;
}

.resume-skills { display: flex; gap: 4px; flex-wrap: wrap; }
.skill-tag {
  padding: 2px 8px; background: var(--paper-alt); color: var(--graphite-light);
  border-radius: 3px; font-size: 11px;
}

.resume-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.resume-time { font-size: 12px; color: var(--stone); }
.row-arrow { color: var(--stone-light); transition: transform 0.15s ease; }
.resume-row:hover .row-arrow { transform: translateX(2px); }

/* 空/加载状态 */
.empty-state {
  text-align: center; padding: 60px 20px; background: var(--white);
  border-radius: var(--radius-md); box-shadow: var(--shadow-sm);
}
.empty-icon { margin-bottom: 16px; }
.empty-title { font-family: var(--font-display); font-weight: 600; color: var(--graphite); margin-bottom: 4px; }
.empty-desc { font-size: 13px; color: var(--stone); }

.loading-state {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 40px; color: var(--stone); font-size: 13px;
}

.spinner {
  width: 18px; height: 18px; border: 2px solid var(--stone-light);
  border-top-color: var(--amber); border-radius: 50%; animation: spin 0.8s linear infinite;
}
.spinner-sm {
  width: 14px; height: 14px; border: 2px solid rgba(184,134,42,0.3);
  border-top-color: #B8862A; border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
