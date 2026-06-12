<template>
  <div class="salary-page">
    <!-- 市场薪资调研 -->
    <div class="section-card">
      <div class="section-header">
        <h2>市场薪资调研</h2>
        <p class="section-desc">基于 AI 分析市场数据，估算指定岗位的薪资水平</p>
      </div>

      <div class="research-form">
        <div class="form-row">
          <div class="field">
            <label class="field-label">选择岗位（可选）</label>
            <select v-model="researchForm.job_id" class="field-select" @change="onJobSelect">
              <option value="">手动输入...</option>
              <option v-for="j in jobs" :key="j.id" :value="j.id">{{ j.title }} · {{ j.location }}</option>
            </select>
          </div>
        </div>
        <div class="form-row" v-if="!researchForm.job_id">
          <div class="field"><label class="field-label">岗位名称</label><input v-model="researchForm.title" placeholder="如：Python开发工程师" /></div>
          <div class="field"><label class="field-label">工作城市</label><input v-model="researchForm.location" placeholder="如：上海" /></div>
        </div>
        <button class="btn btn-primary" @click="doResearch" :disabled="researching">
          {{ researching ? '调研中...' : '开始调研' }}
        </button>
      </div>

      <!-- 调研结果 -->
      <div v-if="researchResult" class="salary-result">
        <div class="salary-bars">
          <div class="bar-item">
            <span class="bar-label">25分位</span>
            <div class="bar-track"><div class="bar-fill bar-p25" :style="{ width: p25Pct + '%' }"></div></div>
            <span class="bar-value">¥{{ (researchResult.p25 / 1000).toFixed(1) }}k</span>
          </div>
          <div class="bar-item bar-item--avg">
            <span class="bar-label">平均</span>
            <div class="bar-track"><div class="bar-fill bar-avg" :style="{ width: avgPct + '%' }"></div></div>
            <span class="bar-value bar-value--accent">¥{{ (researchResult.average / 1000).toFixed(1) }}k</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">75分位</span>
            <div class="bar-track"><div class="bar-fill bar-p75" :style="{ width: p75Pct + '%' }"></div></div>
            <span class="bar-value">¥{{ (researchResult.p75 / 1000).toFixed(1) }}k</span>
          </div>
        </div>
        <p class="source-note">{{ researchResult.source_summary }}</p>
        <span class="research-date">调研日期: {{ researchResult.research_date }}</span>
      </div>
    </div>

    <!-- 候选人薪资预估 -->
    <div class="section-card">
      <div class="section-header">
        <h2>候选人薪资预估</h2>
        <p class="section-desc">综合匹配分数和市场数据，为候选人推荐薪资区间</p>
      </div>

      <div class="research-form">
        <div class="form-row">
          <div class="field">
            <label class="field-label">岗位</label>
            <select v-model="estimateForm.job_id" class="field-select">
              <option value="">请选择...</option>
              <option v-for="j in jobs" :key="j.id" :value="j.id">{{ j.title }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">简历</label>
            <select v-model="estimateForm.resume_id" class="field-select">
              <option value="">请选择...</option>
              <option v-for="r in resumes" :key="r.id" :value="r.id">{{ r.structured_data?.name || r.original_filename }}</option>
            </select>
          </div>
        </div>
        <button class="btn btn-primary" @click="doEstimate" :disabled="estimating || !estimateForm.job_id || !estimateForm.resume_id">
          {{ estimating ? '分析中...' : '预估薪资' }}
        </button>
      </div>

      <!-- 预估结果 -->
      <div v-if="estimateResult" class="estimate-result">
        <div class="est-header">
          <span class="est-name">{{ estimateResult.candidate_name }}</span>
          <span class="est-score">匹配度 {{ estimateResult.match_score }}分</span>
        </div>
        <div class="est-range">
          <div class="range-bar">
            <div class="range-market" :style="{ left: marketLeft + '%', width: marketWidth + '%' }"></div>
            <div class="range-recommended" :style="{ left: recLeft + '%', width: recWidth + '%' }"></div>
          </div>
          <div class="range-labels">
            <span class="rl">¥{{ (estimateResult.recommended_min / 1000).toFixed(0) }}k</span>
            <span class="rl rl--accent">建议: ¥{{ (estimateResult.recommended_min / 1000).toFixed(0) }}k – ¥{{ (estimateResult.recommended_max / 1000).toFixed(0) }}k</span>
            <span class="rl">¥{{ (estimateResult.recommended_max / 1000).toFixed(0) }}k</span>
          </div>
          <p class="range-market-avg">市场平均: ¥{{ (estimateResult.market_average / 1000).toFixed(1) }}k / 月</p>
        </div>
        <p class="est-reasoning">{{ estimateResult.reasoning }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../utils/api'

const jobs = ref<any[]>([])
const resumes = ref<any[]>([])
const researching = ref(false)
const estimating = ref(false)

const researchForm = ref({ job_id: '', title: '', location: '' })
const estimateForm = ref({ job_id: '', resume_id: '' })

const researchResult = ref<any>(null)
const estimateResult = ref<any>(null)

// 百分比计算
const maxSalary = computed(() => researchResult.value ? Math.max(researchResult.value.p75 * 1.2, 1) : 1)
const p25Pct = computed(() => researchResult.value ? (researchResult.value.p25 / maxSalary.value) * 100 : 0)
const avgPct = computed(() => researchResult.value ? (researchResult.value.average / maxSalary.value) * 100 : 0)
const p75Pct = computed(() => researchResult.value ? (researchResult.value.p75 / maxSalary.value) * 100 : 0)

// 薪资区间可视化
const rangeMax = computed(() => estimateResult.value ? Math.max(estimateResult.value.recommended_max * 1.3, 1) : 1)
const marketLeft = computed(() => estimateResult.value ? 0 : 0)
const marketWidth = computed(() => estimateResult.value ? (estimateResult.value.market_average / rangeMax.value) * 100 : 0)
const recLeft = computed(() => estimateResult.value ? (estimateResult.value.recommended_min / rangeMax.value) * 100 : 0)
const recWidth = computed(() => estimateResult.value ? ((estimateResult.value.recommended_max - estimateResult.value.recommended_min) / rangeMax.value) * 100 : 0)

const onJobSelect = () => {
  const job = jobs.value.find((j: any) => j.id === researchForm.value.job_id)
  if (job) {
    researchForm.value.title = job.title
    researchForm.value.location = job.location
  }
}

const doResearch = async () => {
  if (!researchForm.value.title || (!researchForm.value.job_id && !researchForm.value.location)) return
  researching.value = true
  researchResult.value = null
  try {
    const payload: any = {}
    if (researchForm.value.job_id) payload.job_id = researchForm.value.job_id
    if (researchForm.value.title) payload.title = researchForm.value.title
    if (researchForm.value.location) payload.location = researchForm.value.location
    const { data } = await api.post('/api/v1/salary/research', payload)
    researchResult.value = data
  } catch (e) {
    console.error('薪资调研失败', e)
    alert('薪资调研失败，请检查AI配置')
  } finally {
    researching.value = false
  }
}

const doEstimate = async () => {
  estimating.value = true
  estimateResult.value = null
  try {
    const { data } = await api.post('/api/v1/salary/estimate', estimateForm.value)
    estimateResult.value = data
  } catch (e) {
    console.error('薪资预估失败', e)
    alert('薪资预估失败，请检查AI配置和匹配结果')
  } finally {
    estimating.value = false
  }
}

onMounted(async () => {
  try {
    const [j, r] = await Promise.all([
      api.get('/api/v1/jobs', { params: { page_size: 100 } }),
      api.get('/api/v1/resumes', { params: { status: 'completed', page_size: 100 } }),
    ])
    jobs.value = j.data.items || []
    resumes.value = r.data.items || []
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.salary-page { display: flex; flex-direction: column; gap: 16px; max-width: 680px; }

.section-card {
  background: var(--white); border-radius: var(--radius-md); padding: 24px;
  box-shadow: var(--shadow-sm); border: 1px solid rgba(0,0,0,0.04);
}
.section-header { margin-bottom: 20px; }
.section-header h2 { font-family: var(--font-display); font-size: 16px; font-weight: 600; color: var(--graphite); margin: 0; }
.section-desc { font-size: 13px; color: var(--stone); margin: 4px 0 0; }

.research-form { display: flex; flex-direction: column; gap: 14px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.field-label { display: block; font-size: 11px; font-weight: 600; color: var(--graphite-light); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.03em; }
.field-select { width: 100%; }

/* 薪资条 */
.salary-result { margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(0,0,0,0.06); }
.salary-bars { display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px; }
.bar-item { display: grid; grid-template-columns: 56px 1fr 72px; gap: 10px; align-items: center; }
.bar-label { font-size: 11px; color: var(--stone); }
.bar-track { height: 10px; background: var(--paper-alt); border-radius: 5px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 5px; transition: width 0.8s ease; }
.bar-p25 { background: var(--stone-light); }
.bar-avg { background: linear-gradient(90deg, var(--amber), var(--amber-light)); }
.bar-p75 { background: var(--stone-light); }
.bar-value { font-family: var(--font-display); font-size: 13px; font-weight: 600; color: var(--graphite); }
.bar-value--accent { color: var(--amber); }
.source-note { font-size: 12px; color: var(--graphite-light); line-height: 1.6; margin: 0 0 4px; }
.research-date { font-size: 11px; color: var(--stone); }

/* 预估结果 */
.estimate-result { margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(0,0,0,0.06); }
.est-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.est-name { font-family: var(--font-display); font-size: 16px; font-weight: 600; color: var(--graphite); }
.est-score { padding: 3px 10px; background: var(--amber-glow); color: #B8862A; border-radius: 4px; font-size: 12px; font-weight: 500; }

.est-range { margin-bottom: 14px; }
.range-bar { position: relative; height: 24px; background: var(--paper-alt); border-radius: 6px; overflow: hidden; margin-bottom: 8px; }
.range-market { position: absolute; top: 0; height: 100%; background: rgba(0,0,0,0.04); }
.range-recommended { position: absolute; top: 0; height: 100%; background: linear-gradient(90deg, var(--amber), var(--amber-light)); border-radius: 6px; }
.range-labels { display: flex; justify-content: space-between; align-items: center; }
.rl { font-size: 12px; color: var(--stone); }
.rl--accent { font-family: var(--font-display); font-weight: 600; color: var(--amber); }
.range-market-avg { font-size: 12px; color: var(--stone); margin: 8px 0 0; }
.est-reasoning { font-size: 13px; color: var(--graphite-light); line-height: 1.6; margin: 0; padding: 12px; background: var(--paper); border-radius: var(--radius-sm); }
</style>
