import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
        meta: { title: '工作台', icon: '📊' },
      },
      {
        path: 'jobs',
        name: 'Jobs',
        component: () => import('../views/JobsView.vue'),
        meta: { title: '岗位管理', icon: '💼' },
      },
      {
        path: 'jobs/create',
        name: 'JobCreate',
        component: () => import('../views/JobFormView.vue'),
        meta: { title: '创建岗位' },
      },
      {
        path: 'jobs/:id',
        name: 'JobDetail',
        component: () => import('../views/JobDetailView.vue'),
        meta: { title: '岗位详情' },
      },
      {
        path: 'jobs/:id/edit',
        name: 'JobEdit',
        component: () => import('../views/JobFormView.vue'),
        meta: { title: '编辑岗位' },
      },
      {
        path: 'resumes',
        name: 'Resumes',
        component: () => import('../views/ResumesView.vue'),
        meta: { title: '简历库', icon: '📄' },
      },
      {
        path: 'resumes/:id',
        name: 'ResumeDetail',
        component: () => import('../views/ResumeDetailView.vue'),
        meta: { title: '简历详情' },
      },
      {
        path: 'matching',
        name: 'Matching',
        component: () => import('../views/MatchingView.vue'),
        meta: { title: '匹配评分', icon: '🎯' },
      },
      {
        path: 'salary',
        name: 'SalaryResearch',
        component: () => import('../views/SalaryView.vue'),
        meta: { title: '薪资分析', icon: '💰' },
      },
      {
        path: 'interview',
        name: 'Interview',
        component: () => import('../views/PreInterviewView.vue'),
        meta: { title: 'AI 预面试', icon: '💬' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { title: '系统设置', icon: '⚙️' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：检查登录状态
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !token) {
    // 需要认证但没有 token，跳转登录页
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && token) {
    // 已登录用户访问登录页，跳转首页
    next({ path: '/dashboard' })
  } else {
    next()
  }
})

export default router
