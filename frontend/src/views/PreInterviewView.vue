<template>
  <div class="interview-page">
    <!-- 启动面板（未开始时显示） -->
    <div v-if="!session" class="start-panel">
      <div class="start-card">
        <div class="start-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="var(--amber)" stroke-width="1.5">
            <path d="M8 8h32a2 2 0 012 2v22a2 2 0 01-2 2H16l-8 6v-6H8a2 2 0 01-2-2V10a2 2 0 012-2z"/>
            <path d="M16 18h16M16 24h10"/>
          </svg>
        </div>
        <h2>AI 预面试</h2>
        <p>选择岗位和简历，AI 将根据岗位要求和候选人背景生成针对性面试问题</p>

        <div class="start-form">
          <div class="field">
            <label class="field-label">岗位</label>
            <select v-model="startForm.job_id" class="field-select">
              <option value="">请选择...</option>
              <option v-for="j in jobs" :key="j.id" :value="j.id">{{ j.title }} · {{ j.location }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">简历</label>
            <select v-model="startForm.resume_id" class="field-select">
              <option value="">请选择...</option>
              <option v-for="r in resumes" :key="r.id" :value="r.id">{{ r.structured_data?.name || r.original_filename }}</option>
            </select>
          </div>
          <button class="btn btn-primary btn-lg" @click="startInterview" :disabled="!startForm.job_id || !startForm.resume_id || starting">
            {{ starting ? 'AI 正在准备问题...' : '开始面试' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 面试界面 -->
    <div v-else class="chat-layout">
      <!-- 左侧：问题列表 + 进度 -->
      <div class="sidebar-panel">
        <div class="progress-header">
          <span class="progress-text">进度 {{ currentIndex + 1 }}/{{ totalQuestions }}</span>
          <div class="progress-bar"><div class="progress-fill" :style="{ width: progressPct + '%' }"></div></div>
        </div>
        <div class="question-list">
          <div
            v-for="(q, i) in session.questions"
            :key="q.question_id"
            class="q-item"
            :class="{ 'q-item--active': i === currentIndex, 'q-item--done': i < currentIndex }"
          >
            <span class="q-num">{{ i + 1 }}</span>
            <div class="q-info">
              <span class="q-cat">{{ catLabels[q.category] || q.category }}</span>
              <span class="q-diff" :class="'diff-' + q.difficulty">{{ diffLabels[q.difficulty] }}</span>
            </div>
            <span v-if="getEval(q.question_id)" class="q-score">{{ getEval(q.question_id).score }}/10</span>
          </div>
        </div>

        <!-- 总评按钮 + 导出 -->
        <div class="sidebar-bottom">
          <button
            v-if="session.status === 'in_progress' && currentIndex >= totalQuestions - 1 && lastAnswered"
            class="btn btn-primary btn-full"
            @click="completeInterview"
            :disabled="completing"
          >
            {{ completing ? '生成总评...' : '结束面试，查看总评' }}
          </button>
          <button
            v-if="session.questions?.length"
            class="btn btn-secondary btn-full"
            @click="exportPDF"
            :disabled="exporting"
            style="margin-top: 8px;"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 1v8M3.5 5.5L7 9l3.5-3.5"/><path d="M1 10v2a1 1 0 001 1h10a1 1 0 001-1v-2"/></svg>
            {{ exporting ? '导出中...' : '导出问题 PDF' }}
          </button>
        </div>
      </div>

      <!-- 右侧：对话区域 -->
      <div class="chat-panel">
        <div class="chat-messages" ref="chatRef">
          <div v-for="(turn, i) in session.conversation" :key="i" class="msg" :class="turn.role === 'ai' ? 'msg--ai' : 'msg--candidate'">
            <div class="msg-avatar">{{ turn.role === 'ai' ? '🤖' : '👤' }}</div>
            <div class="msg-body">
              <div class="msg-role">{{ turn.role === 'ai' ? '面试官' : '候选人' }}</div>
              <div class="msg-text">{{ turn.content }}</div>
              <!-- 评分反馈 -->
              <div v-if="turn.role === 'candidate' && getEval(turn.question_id)" class="msg-eval">
                <span class="eval-score">评分: {{ getEval(turn.question_id).score }}/10</span>
                <p class="eval-feedback">{{ getEval(turn.question_id).feedback }}</p>
              </div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="answering" class="msg msg--ai">
            <div class="msg-avatar">🤖</div>
            <div class="msg-body"><div class="typing-dots"><span></span><span></span><span></span></div></div>
          </div>
        </div>

        <!-- 输入区 -->
        <div v-if="session.status === 'in_progress'" class="chat-input">
          <textarea
            v-model="answerText"
            placeholder="输入候选人的回答..."
            rows="3"
            @keydown.ctrl.enter="submitAnswer"
          ></textarea>
          <div class="input-actions">
            <span class="input-hint">Ctrl + Enter 发送</span>
            <button class="btn btn-primary" @click="submitAnswer" :disabled="!answerText.trim() || answering">
              {{ answering ? '评估中...' : '提交回答' }}
            </button>
          </div>
        </div>

        <!-- 总评展示 -->
        <div v-if="session.overall_evaluation" class="overall-card">
          <h3>面试总评</h3>
          <div class="overall-scores">
            <div class="os-item">
              <span class="os-val">{{ session.overall_evaluation.total_score }}</span>
              <span class="os-label">总分</span>
            </div>
            <div class="os-item">
              <span class="os-val">{{ session.overall_evaluation.technical_score }}</span>
              <span class="os-label">技术</span>
            </div>
            <div class="os-item">
              <span class="os-val">{{ session.overall_evaluation.communication_score }}</span>
              <span class="os-label">沟通</span>
            </div>
            <div class="os-item">
              <span class="os-val">{{ session.overall_evaluation.cultural_fit_score }}</span>
              <span class="os-label">文化</span>
            </div>
          </div>
          <div class="overall-rec">
            <span class="rec-badge" :class="'rec-' + session.overall_evaluation.recommendation">
              {{ recLabels[session.overall_evaluation.recommendation] }}
            </span>
          </div>
          <p class="overall-summary">{{ session.overall_evaluation.summary }}</p>
          <div v-if="session.overall_evaluation.highlights?.length" class="overall-tags">
            <span class="tag tag--s" v-for="h in session.overall_evaluation.highlights" :key="h">+ {{ h }}</span>
          </div>
          <div v-if="session.overall_evaluation.key_concerns?.length" class="overall-tags">
            <span class="tag tag--w" v-for="c in session.overall_evaluation.key_concerns" :key="c">! {{ c }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import api from '../utils/api'

const jobs = ref<any[]>([])
const resumes = ref<any[]>([])
const session = ref<any>(null)
const startForm = ref({ job_id: '', resume_id: '' })
const starting = ref(false)
const answering = ref(false)
const completing = ref(false)
const exporting = ref(false)
const answerText = ref('')
const lastAnswered = ref(false)
const chatRef = ref<HTMLElement | null>(null)

const catLabels: Record<string, string> = { technical: '技术', behavioral: '行为', situational: '情景', gap_followup: '追问' }
const diffLabels: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
const recLabels: Record<string, string> = {
  strongly_recommend: '强烈推荐', recommend_interview: '推荐面试',
  needs_further_evaluation: '需进一步评估', not_recommended: '不推荐',
}

const totalQuestions = computed(() => session.value?.questions?.length || 0)
const currentIndex = computed(() => {
  if (!session.value) return 0
  // 从对话中计算当前问题索引
  const aiMsgs = session.value.conversation?.filter((t: any) => t.role === 'ai') || []
  return Math.max(0, aiMsgs.length - 1)
})
const progressPct = computed(() => totalQuestions.value ? ((currentIndex.value + 1) / totalQuestions.value) * 100 : 0)

const getEval = (qid: string) => {
  return session.value?.evaluations?.find((e: any) => e.question_id === qid)
}

const scrollToBottom = () => {
  nextTick(() => { if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight })
}

const startInterview = async () => {
  starting.value = true
  try {
    const { data } = await api.post('/api/v1/interview/start', startForm.value)
    session.value = data
    scrollToBottom()
  } catch (e: any) {
    alert(e.response?.data?.detail || '启动面试失败')
  } finally { starting.value = false }
}

const submitAnswer = async () => {
  if (!answerText.value.trim() || answering.value) return
  answering.value = true
  try {
    const { data } = await api.post(`/api/v1/interview/${session.value.id}/answer`, {
      answer_text: answerText.value.trim(),
    })
    // 刷新会话
    const { data: updated } = await api.get(`/api/v1/interview/${session.value.id}`)
    session.value = updated
    answerText.value = ''
    lastAnswered.value = data.is_last
    scrollToBottom()
  } catch (e: any) {
    alert(e.response?.data?.detail || '提交失败')
  } finally { answering.value = false }
}

const completeInterview = async () => {
  completing.value = true
  try {
    const { data } = await api.post(`/api/v1/interview/${session.value.id}/complete`)
    session.value = data
    scrollToBottom()
  } catch (e: any) {
    alert(e.response?.data?.detail || '生成总评失败')
  } finally { completing.value = false }
}

const exportPDF = async () => {
  if (!session.value?.id) return
  exporting.value = true
  try {
    const response = await api.get(`/api/v1/interview/${session.value.id}/export`, {
      responseType: 'blob',
    })
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `interview_${session.value.id.slice(0, 8)}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e: any) {
    console.error('导出失败', e)
    alert('导出PDF失败')
  } finally { exporting.value = false }
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
.interview-page { height: calc(100vh - 120px); display: flex; }

/* 启动面板 */
.start-panel { display: flex; align-items: center; justify-content: center; width: 100%; }
.start-card {
  background: var(--white); border-radius: var(--radius-lg); padding: 40px;
  box-shadow: var(--shadow-md); text-align: center; max-width: 440px; width: 100%;
}
.start-icon { margin-bottom: 16px; }
.start-card h2 { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--graphite); margin: 0 0 8px; }
.start-card p { font-size: 13px; color: var(--stone); margin: 0 0 24px; }
.start-form { display: flex; flex-direction: column; gap: 12px; text-align: left; }
.field-label { display: block; font-size: 11px; font-weight: 600; color: var(--graphite-light); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.03em; }
.field-select { width: 100%; }
.btn-lg { padding: 12px 24px; font-size: 14px; margin-top: 4px; }

/* 聊天布局 */
.chat-layout { display: flex; width: 100%; gap: 16px; }

/* 侧边栏 */
.sidebar-panel {
  width: 240px; background: var(--white); border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm); display: flex; flex-direction: column; flex-shrink: 0;
}
.progress-header { padding: 14px 16px; border-bottom: 1px solid rgba(0,0,0,0.06); }
.progress-text { font-size: 12px; font-weight: 600; color: var(--graphite-light); display: block; margin-bottom: 8px; }
.progress-bar { height: 4px; background: var(--paper-alt); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--amber); border-radius: 2px; transition: width 0.3s; }

.question-list { flex: 1; overflow-y: auto; padding: 8px 0; }
.q-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 16px;
  font-size: 12px; transition: background 0.1s;
}
.q-item--active { background: var(--amber-glow); }
.q-item--done { opacity: 0.6; }
.q-num {
  width: 20px; height: 20px; border-radius: 50%; background: var(--paper-alt);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 700; font-size: 10px; color: var(--graphite-light); flex-shrink: 0;
}
.q-item--active .q-num { background: var(--amber); color: var(--white); }
.q-item--done .q-num { background: var(--sage); color: var(--white); }
.q-info { flex: 1; display: flex; gap: 4px; }
.q-cat { color: var(--graphite-light); }
.q-diff { font-size: 10px; padding: 1px 5px; border-radius: 3px; }
.diff-easy { background: var(--sage-bg); color: #4A8A4E; }
.diff-medium { background: var(--amber-glow); color: #B8862A; }
.diff-hard { background: var(--coral-bg); color: var(--coral); }
.q-score { font-family: var(--font-display); font-weight: 600; color: var(--amber); }
.sidebar-bottom { padding: 12px; border-top: 1px solid rgba(0,0,0,0.06); }
.btn-full { width: 100%; }

/* 聊天面板 */
.chat-panel { flex: 1; display: flex; flex-direction: column; background: var(--white); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); overflow: hidden; }

.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }

.msg { display: flex; gap: 10px; }
.msg--candidate { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px; border-radius: 50%; background: var(--paper-alt);
  display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;
}
.msg-body { max-width: 70%; }
.msg--candidate .msg-body { text-align: right; }
.msg-role { font-size: 11px; font-weight: 600; color: var(--stone); margin-bottom: 3px; }
.msg-text {
  font-size: 14px; color: var(--graphite); line-height: 1.6;
  padding: 10px 14px; border-radius: 12px;
}
.msg--ai .msg-text { background: var(--paper); border-bottom-left-radius: 4px; }
.msg--candidate .msg-text { background: var(--amber-glow); border-bottom-right-radius: 4px; }

.msg-eval {
  margin-top: 6px; padding: 8px 12px; background: var(--paper); border-radius: 8px;
  font-size: 12px; text-align: left;
}
.eval-score { font-family: var(--font-display); font-weight: 600; color: var(--amber); }
.eval-feedback { color: var(--graphite-light); margin: 4px 0 0; line-height: 1.5; }

/* 输入区 */
.chat-input { padding: 16px; border-top: 1px solid rgba(0,0,0,0.06); }
.chat-input textarea {
  width: 100%; border: 1px solid var(--stone-light); border-radius: var(--radius-sm);
  padding: 10px 12px; font-size: 13px; resize: none; font-family: var(--font-body);
  box-sizing: border-box;
}
.chat-input textarea:focus { border-color: var(--amber); box-shadow: 0 0 0 3px var(--amber-glow); outline: none; }
.input-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.input-hint { font-size: 11px; color: var(--stone); }

/* 打字动画 */
.typing-dots { display: flex; gap: 4px; padding: 12px 14px; }
.typing-dots span { width: 6px; height: 6px; background: var(--stone-light); border-radius: 50%; animation: blink 1.4s infinite both; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%,80%,100% { opacity: 0.3; } 40% { opacity: 1; } }

/* 总评 */
.overall-card {
  margin: 16px; padding: 20px; background: var(--paper); border-radius: var(--radius-md);
  border: 1px solid rgba(232,168,56,0.2);
}
.overall-card h3 { font-family: var(--font-display); font-size: 15px; font-weight: 600; margin: 0 0 14px; color: var(--graphite); }
.overall-scores { display: flex; gap: 20px; margin-bottom: 12px; }
.os-item { text-align: center; }
.os-val { display: block; font-family: var(--font-display); font-size: 24px; font-weight: 700; color: var(--amber); }
.os-label { font-size: 11px; color: var(--stone); }
.overall-rec { margin-bottom: 10px; }
.rec-badge { padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.rec-strongly_recommend { background: var(--sage-bg); color: #4A8A4E; }
.rec-recommend_interview { background: var(--amber-glow); color: #B8862A; }
.rec-needs_further_evaluation { background: rgba(0,0,0,0.04); color: var(--stone); }
.rec-not_recommended { background: var(--coral-bg); color: var(--coral); }
.overall-summary { font-size: 13px; color: var(--graphite-light); line-height: 1.6; margin: 0 0 10px; }
.overall-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 6px; }
.tag { padding: 2px 8px; border-radius: 3px; font-size: 11px; }
.tag--s { background: var(--sage-bg); color: #4A8A4E; }
.tag--w { background: var(--coral-bg); color: var(--coral); }
</style>
