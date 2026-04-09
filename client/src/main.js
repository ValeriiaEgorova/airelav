import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import router from './router';
import axios from 'axios';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      router.push('/login'); 
    }
    return Promise.reject(error);
  }
);

createApp(App).use(router).mount('#app');
