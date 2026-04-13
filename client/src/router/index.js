import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../components/MainLayout.vue';
import Login from '../components/Login.vue';
import Dashboard from '../components/Dashboard.vue';
import ApiSettings from '../components/ApiSettings.vue';
import UserPage from '../components/UserPage.vue';
import AuthSuccess from '../components/AuthSuccess.vue';
import ResetPassword from '../components/ResetPassword.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/auth-success', component: AuthSuccess },
    { path: '/reset-password', component: ResetPassword },

    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'dashboard', component: Dashboard },
        { path: 'api-settings', name: 'api-settings', component: ApiSettings },
        { path: 'profile', name: 'profile', component: UserPage },
      ],
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
