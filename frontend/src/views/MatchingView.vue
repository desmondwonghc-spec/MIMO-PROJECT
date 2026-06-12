<template>
  <div class="matching-page">
    <!-- 选择区 -->
    <div class="selector-card">
      <div class="selector-row">
        <div class="field">
          <label class="field-label">选择岗位</label>
          <select v-model="selectedJobId" class="field-select" @change="onJobChange">
            <option value="">请选择岗位...</option>
            <option v-for="j in jobs" :key="j.id" :value="j.id">{{ j.title }} · {{ j.location }}</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="runBatchMatch" :disabled="!selectedJobId || selectedResumeIds.length === 0 || matching">
          <div v-if="matching" class="spinner-sm"></div>
          {{ matching ? '评分中...' : `匹配评分 (${selectedResumeIds.length})` }}
        </button>
      </div>
    </div>

    <div class="content-grid">
      <!-- 左侧：简历选择 -->
      <div class="panel">
        <div class="panel-header">
          <h3>选择简历</h3>
          <button class="btn btn-ghost btn-sm" @click="toggleSelectAll">
            {{ allSelected ? '取消全选' : '全选' }}
          </button>
        </div>
        <div v-if="resumes.length === 0" class="panel-empty">暂无已解析的简历</div>
        <label v-for="r in resumes" :key="r.id" class="resume-check" :class="{ 'check--selected': selectedResumeIds.includes(r.id) }">
          <input type="checkbox" :value="r.id" v-model="selectedResumeIds" class="check-input" />
          <span class="check-avatar">{{ (r.structured_data?.name || '?').charAt(0) }}</span>
          <span class="check-name">{{ r.structured_data?.name || r.original_filename }}</span>
          <span class="check-meta">{{ r.structured_data?.total_experience_years || 0 }}年</span>
        </label>
      </div>

      <!-- 右侧：匹配结果 -->
      <div class="panel">
        <div class="panel-header">
          <h3>匹配结果</h3>
          <span v-if="results.length" class="result-count">{{ results.length }} 位候选人</span>
        </div>

        <div v-if="results.length === 0" class="panel-empty">
          {{ matching ? 'AI 正在评分，请稍候...' : '选择岗位和简历后点击匹配评分' }}
        </div>

        <div v-else class="result-list">
          <div v-for="r in results" :key="r.resume_id" class="result-card">
            <div class="result-top">
              <div class="result-score-ring" :style="{ '--score': r.overall_score }">
                <svg viewBox="0 0 60 60">
                  <circle class="ring-bg" cx="30" cy="30" r="26" />
                  <circle class="ring-fill" cx="30" cy="30" r="26" />
                </svg>
                <span class="ring-num">{{ r.overall_score }}</span>
              </div>
              <div class="result-info">
                <div class="result-name">
                  {{ r.resume_name }}
                  <span class="rec-badge" :class="'rec-' + r.recommendation">{{ recLabels[r.recommendation] }}</span>
                </div>
                <p class="result-summary">{{ r.summary }}</p>
              </div>
            </div>

            <!-- 5维度条 -->
            <div v-if="r.dimension_scores" class="dims">
              <div v-for="(dim, key) in r.dimension_scores" :key="key" class="dim-row">
                <span class="dim-label">{{ dimLabels[key] || key }}</span>
                <div class="dim-bar"><div class="dim-fill" :style="{ width: dim.score + '%' }"></div></div>
                <span class="dim-val">{{ dim.score }}</span>
              </div>
            </div>

            <!-- 优劣势 -->
            <div class="sw-section" v-if="r.strengths?.length || r.weaknesses?.length">
              <div v-if="r.strengths?.length" class="sw-list">
                <span class="sw-tag sw-s" v-for="s in r.strengths" :key="s">+ {{ s }}</span>
              </div>
              <div v-if="r.weaknesses?.length" class="sw-list">
                <span class="sw-tag sw-w" v-for="w in r.weaknesses" :key="w">− {{ w }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../utils/api'

const jobs = ref<any[]>([])
const resumes = ref<any[]>([])
const selectedJobId = ref('')
const selectedResumeIds = ref<string[]>([])
const results = ref<any[]>([])
const matching = ref(false)

const dimLabels: Record<string, string> = {
  skills_match: '技能',
  experience_match: '经验',
  education_match: '学历',
  location_match: '地点',
  salary_match: '薪资',
}

const recLabels: Record<string, string> = {
  strong_match: '强烈推荐',
  good_match: '推荐',
  partial_match: '一般',
  weak_match: '不推荐',
  no_match: '不匹配',
}

const allSelected = computed(() =>
  resumes.value.length > 0 && selectedResumeIds.value.length === resumes.value.length
)

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedResumeIds.value = []
  } else {
    selectedResumeIds.value = resumes.value.map((r: any) => r.id)
  }
}

const onJobChange = async () => {
  if (selectedJobId.value) {
    await loadMatchResults()
  } else {
    results.value = []
  }
}

const loadMatchResults = async () => {
  if (!selectedJobId.value) return
  try {
    const { data } = await api.get(`/api/v1/matching/results/${selectedJobId.value}`)
    results.value = data.items || []
  } catch (e) {
    console.error('获取匹配结果失败', e)
  }
}

const runBatchMatch = async () => {
  if (!selectedJobId.value || selectedResumeIds.value.length === 0) return
  matching.value = true
  try {
    await api.post('/api/v1/matching/batch', {
      job_id: selectedJobId.value,
      resume_ids: selectedResumeIds.value,
    })
    // 重新加载结果
    await loadMatchResults()
  } catch (e) {
    console.error('匹配评分失败', e)
    alert('匹配评分失败，请检查AI配置')
  } finally {
    matching.value = false
  }
}

onMounted(async () => {
  try {
    const [jobsRes, resumesRes] = await Promise.all([
      api.get('/api/v1/jobs', { params: { page_size: 100 } }),
      api.get('/api/v1/resumes', { params: { status: 'completed', page_size: 100 } }),
    ])
    jobs.value = jobsRes.data.items || []
    resumes.value = resumesRes.data.items || []
  } catch (e) {
    console.error('加载数据失败', e)
  }
})
</script>

<style scoped>
.matching-page { display: flex; flex-direction: column; gap: 16px; }

/* 选择区 */
.selector-card {
  background: var(--white); border-radius: var(--radius-md); padding: 16px 20px;
  box-shadow: var(--shadow-sm); border: 1px solid rgba(0,0,0,0.04);
}
.selector-row { display: flex; align-items: flex-end; gap: 16px; }
.field { flex: 1; }
.field-label { display: block; font-size: 12px; font-weight: 600; color: var(--graphite-light); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.03em; }
.field-select { width: 100%; padding: 9px 12px; border: 1px solid var(--stone-light); border-radius: var(--radius-sm); font-family: var(--font-body); font-size: 13px; background: var(--white); color: var(--graphite); }

/* 内容网格 */
.content-grid { display: grid; grid-template-columns: 260px 1fr; gap: 16px; align-items: start; }

/* 面板 */
.panel {
  background: var(--white); border-radius: var(--radius-md); box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0,0,0,0.04); overflow: hidden;
}
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-bottom: 1px solid rgba(0,0,0,0.06); }
.panel-header h3 { font-family: var(--font-display); font-size: 13px; font-weight: 600; color: var(--graphite); margin: 0; }
.panel-empty { padding: 32px; text-align: center; font-size: 13px; color: var(--stone); }
.result-count { font-size: 12px; color: var(--stone); }

/* 简历选择 */
.resume-check {
  display: flex; align-items: center; gap: 8px; padding: 10px 16px;
  cursor: pointer; transition: background 0.1s; border-bottom: 1px solid rgba(0,0,0,0.03);
}
.resume-check:last-child { border-bottom: none; }
.resume-check:hover { background: var(--paper); }
.check--selected { background: var(--amber-glow); }
.check-input { accent-color: var(--amber); }
.check-avatar {
  width: 26px; height: 26px; border-radius: 50%; background: var(--paper-alt);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 700; font-size: 11px; color: var(--graphite-light);
  flex-shrink: 0;
}
.check-name { flex: 1; font-size: 13px; font-weight: 500; color: var(--graphite); }
.check-meta { font-size: 11px; color: var(--stone); }

/* 结果卡片 */
.result-list { display: flex; flex-direction: column; }
.result-card {
  padding: 16px; border-bottom: 1px solid rgba(0,0,0,0.04);
}
.result-card:last-child { border-bottom: none; }

.result-top { display: flex; gap: 14px; margin-bottom: 12px; }

/* 环形分数 */
.result-score-ring {
  position: relative; width: 56px; height: 56px; flex-shrink: 0;
}
.result-score-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: var(--paper-alt); stroke-width: 5; }
.ring-fill {
  fill: none; stroke: var(--amber); stroke-width: 5; stroke-linecap: round;
  stroke-dasharray: 163.4; stroke-dashoffset: calc(163.4 - (163.4 * var(--score, 0) / 100));
  transition: stroke-dashoffset 0.8s ease;
}
.ring-num {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-family: var(--font-display); font-size: 16px; font-weight: 700; color: var(--graphite);
}

.result-info { flex: 1; min-width: 0; }
.result-name { font-family: var(--font-display); font-size: 14px; font-weight: 600; color: var(--graphite); margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }

.rec-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; }
.rec-strong_match { background: var(--sage-bg); color: #4A8A4E; }
.rec-good_match { background: var(--amber-glow); color: #B8862A; }
.rec-partial_match { background: rgba(0,0,0,0.04); color: var(--stone); }
.rec-weak_match { background: var(--coral-bg); color: var(--coral); }
.rec-no_match { background: var(--coral-bg); color: var(--coral); }

.result-summary { font-size: 12px; color: var(--graphite-light); line-height: 1.5; margin: 0; }

/* 维度条 */
.dims { display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; }
.dim-row { display: grid; grid-template-columns: 48px 1fr 32px; gap: 8px; align-items: center; }
.dim-label { font-size: 11px; color: var(--stone); }
.dim-bar { height: 5px; background: var(--paper-alt); border-radius: 3px; overflow: hidden; }
.dim-fill { height: 100%; background: linear-gradient(90deg, var(--amber), var(--amber-light)); border-radius: 3px; }
.dim-val { font-family: var(--font-display); font-size: 11px; font-weight: 600; color: var(--graphite); text-align: right; }

/* 优劣势 */
.sw-section { display: flex; flex-direction: column; gap: 4px; }
.sw-list { display: flex; gap: 4px; flex-wrap: wrap; }
.sw-tag { padding: 2px 8px; border-radius: 3px; font-size: 11px; }
.sw-s { background: var(--sage-bg); color: #4A8A4E; }
.sw-w { background: var(--coral-bg); color: var(--coral); }

/* 小spinner */
.spinner-sm { width: 14px; height: 14px; border: 2px solid rgba(28,31,38,0.2); border-top-color: var(--obsidian); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
