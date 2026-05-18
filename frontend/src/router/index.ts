import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/Login.vue'
import DashboardView from '../views/Dashboard.vue'
import ShoppingView from '../views/Shopping.vue'
import AdminView from '../views/Admin.vue'
import AdminGroupsView from '../views/AdminGroups.vue'
import AdminUsersView from '../views/AdminUsers.vue'
import AdminListsView from '../views/AdminLists.vue'
import AdminAuditView from '../views/AdminAudit.vue'
import ChangePasswordView from '../views/ChangePassword.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    { path: '/change-password', component: ChangePasswordView },
    { 
      path: '/dashboard', 
      component: DashboardView, 
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard/items' },
        { path: 'items', component: { template: '<div></div>' } }, 
        { path: 'settlements', component: { template: '<div></div>' } },
        { path: 'history', component: { template: '<div></div>' } },
        { path: 'analytics', component: { template: '<div></div>' } },
      ]
    },
    { path: '/shopping', component: ShoppingView, meta: { requiresAuth: true } },
    { 
      path: '/admin', 
      component: AdminView, 
      meta: { requiresAdmin: true },
      children: [
        { path: '', component: { template: '<div></div>' } },
        { path: 'users', component: AdminUsersView },
        { path: 'groups', component: AdminGroupsView },
        { path: 'lists', component: AdminListsView },
        { path: 'audit', component: AdminAuditView },
      ]
    },
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  
  if (to.meta.requiresAdmin && !auth.user?.is_admin) {
    return '/login'
  } else if (to.path.startsWith('/admin') && !auth.user?.is_admin) {
    return '/dashboard'
  } else if (to.path === '/dashboard' && auth.user?.is_admin) {
    return '/admin'
  }
})

export default router


