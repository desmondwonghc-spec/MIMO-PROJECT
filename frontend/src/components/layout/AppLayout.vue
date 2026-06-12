<template>
  <div class="app-layout">
    <aside class="sidebar">
      <!-- Logo 区域 -->
      <div class="sidebar-brand">
        <div class="brand-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="12" stroke="#E8A838" stroke-width="2" />
            <circle cx="14" cy="14" r="5" fill="#E8A838" />
            <line x1="14" y1="2" x2="14" y2="7" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="14" y1="21" x2="14" y2="26" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="2" y1="14" x2="7" y2="14" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="21" y1="14" x2="26" y2="14" stroke="#E8A838" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">人才洞察</span>
          <span class="brand-sub">TalentLens</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <!-- 底部光晕 + 状态 -->
      <div class="sidebar-footer">
        <div class="sidebar-glow"></div>
        <router-link to="/settings" class="nav-item nav-item--settings">
          <span class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="9" cy="9" r="2.5"/><path d="M9 1.5v2M9 14.5v2M1.5 9h2M14.5 9h2M3.4 3.4l1.4 1.4M13.2 13.2l1.4 1.4M3.4 14.6l1.4-1.4M13.2 4.8l1.4-1.4"/>
            </svg>
          </span>
          <span class="nav-label">设置</span>
        </router-link>
      </div>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div class="top-bar-left">
          <h1 class="page-heading">{{ currentTitle }}</h1>
        </div>
        <div class="top-bar-right">
          <span class="time-display">{{ currentTime }}</span>
        </div>
      </header>
      <div class="page-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentTime = ref('')

let timer: ReturnType<typeof setInterval>

onMounted(() => {
  const update = () => {
    const now = new Date()
    currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  update()
  timer = setInterval(update, 60000)
})

onUnmounted(() => clearInterval(timer))

const menuItems = [
  {
    path: '/dashboard',
    label: '工作台',
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="5" height="5" rx="1"/><rect x="11" y="2" width="5" height="5" rx="1"/><rect x="2" y="11" width="5" height="5" rx="1"/><rect x="11" y="11" width="5" height="5" rx="1"/></svg>',
  },
  {
    path: '/jobs',
    label: '岗位管理',
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="5" width="12" height="11" rx="1.5"/><path d="M6 5V3.5A1.5 1.5 0 017.5 2h3A1.5 1.5 0 0112 3.5V5"/></svg>',
  },
  {
    path: '/resumes',
    label: '简历库',
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 2h7l5 5v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M11 2v5h5"/></svg>',
  },
  {
    path: '/matching',
    label: '匹配评分',
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="7" cy="9" r="4.5"/><circle cx="11" cy="9" r="4.5"/></svg>',
  },
  {
    path: '/salary',
    label: '薪资分析',
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 2v14M5 5.5C5 4.1 6.8 3 9 3s4 1.1 4 2.5S11.2 8 9 8 5 9.1 5 10.5 6.8 13 9 13s4-1.1 4-2.5"/></svg>',
  },
]

const currentTitle = computed(() => (route.meta?.title as string) || '工作台')
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* === 侧边栏 === */
.sidebar {
  width: 224px;
  background: var(--obsidian);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px 20px;
}

.brand-mark {
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.02em;
  line-height: 1.2;
}

.brand-sub {
  font-size: 10px;
  color: var(--stone);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 1px;
}

/* === 导航 === */
.sidebar-nav {
  flex: 1;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s ease;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.85);
}

.nav-item--active {
  background: rgba(232, 168, 56, 0.12);
  color: var(--amber);
}

.nav-item--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--amber);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  flex-shrink: 0;
}

.nav-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

/* === 底部光晕 === */
.sidebar-footer {
  position: relative;
  padding: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar-glow {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 180px;
  height: 100px;
  background: radial-gradient(ellipse at center, rgba(232, 168, 56, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.nav-item--settings {
  position: relative;
  z-index: 1;
}

/* === 主内容区 === */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--paper);
  overflow: hidden;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  background: var(--white);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}

.page-heading {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  color: var(--graphite);
  letter-spacing: -0.01em;
}

.time-display {
  font-size: 12px;
  color: var(--stone);
  font-variant-numeric: tabular-nums;
}

.page-body {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
}
</style>
