import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
        meta: { title: '仪表盘', icon: '📊' },
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

export default router
