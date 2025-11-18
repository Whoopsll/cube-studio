import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/DashboardView.vue'
import Users from '@/views/UserView.vue'
import Analytics from '@/views/AnalyticsView.vue'
import Orders from '@/views/OrderView.vue'
import Report from '@/views/ReportView.vue'
import Results from '@/views/ResultsView.vue'
import ResultDetail from '@/views/ResultDetailView.vue'
import Workflow from '@/views/WorkflowView.vue'
import Menu from '@/views/Menu.vue'
import InferentialData from '@/views/InferentialData.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/users' // 添加重定向规则
    },
    {
      path: '/',
      component: Menu,
      children: [
        {
          path: '/dashboard',
          name: 'Dashboard',
          component: Dashboard,
          meta: { title: '体系管理' }
        },
        {
          path: '/users',
          name: 'Users',
          component: Users,
          meta: { title: '指标管理' }
        },
        {
          path: '/analytics/:id',
          name: 'Analytics',
          component: Analytics,
          meta: { title: '评估管理' }
        },
        {
          path: '/orders/:id',
          name: 'Orders',
          component: Orders,
          meta: { title: '推演数据管理' }
        },
        {
          path: '/inferential-data',
          name: 'InferentialData',
          component: InferentialData,
          meta: { title: '数据源集合' }
        },
        {
          path: '/report/:id',
          name: 'Report',
          component: Report,
          meta: { title: '评估结果展示' }
        },
        {
          path: '/results',
          name: 'Results',
          component: Results,
          meta: { title: '数据结果展示' }
        },
        {
          path: '/result-detail',
          name: 'ResultDetail',
          component: ResultDetail,
          meta: { title: '评估报告详情' }
        },
        {
          path: '/work-flow',
          name: 'Workflow',
          component: Workflow,
          meta: { title: '评估结果详情' }
        }
      ]
    }
  ]
})

export default router
