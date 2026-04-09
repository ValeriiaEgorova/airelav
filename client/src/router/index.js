import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../components/MainLayout.vue'; // Импорт оболочки
import Login from '../components/Login.vue';
import Dashboard from '../components/Dashboard.vue';
import ApiSettings from '../components/ApiSettings.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    {
      path: '/',
      component: MainLayout, // Главная оболочка
      children: [
        { path: '', name: 'dashboard', component: Dashboard },
        { path: 'api-settings', name: 'api-settings', component: ApiSettings },
      ],
      meta: { requiresAuth: true }
    }
  ]
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
