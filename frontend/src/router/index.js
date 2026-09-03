import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import StockOperationsView from '@/views/StockOperationsView.vue'
import InventoryView from '@/views/InventoryView.vue'
import CellsView from '@/views/CellsView.vue'
import PartsView from '@/views/PartsView.vue'
import PartTypesView from '@/views/PartTypesView.vue'
import LocationsView from '@/views/LocationsView.vue'
import LotsView from '@/views/LotsView.vue'
import VendorsView from '@/views/VendorsView.vue'
import TransactionsView from '@/views/TransactionsView.vue'
import ReportsView from '@/views/ReportsView.vue'
import UsersView from '@/views/UsersView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/stock-operations', name: 'stock-operations', component: StockOperationsView },
  { path: '/inventory', name: 'inventory', component: InventoryView },
  { path: '/cells', name: 'cells', component: CellsView },
  { path: '/parts', name: 'parts', component: PartsView },
  { path: '/part-types', name: 'part-types', component: PartTypesView },
  { path: '/locations', name: 'locations', component: LocationsView },
  { path: '/lots', name: 'lots', component: LotsView },
  { path: '/vendors', name: 'vendors', component: VendorsView },
  { path: '/transactions', name: 'transactions', component: TransactionsView },
  { path: '/reports', name: 'reports', component: ReportsView },
  { path: '/users', name: 'users', component: UsersView },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (!to.meta.public && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
