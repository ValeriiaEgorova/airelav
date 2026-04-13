import { reactive } from 'vue';
import axios from 'axios';

// Используем переменную окружения или дефолтный адрес
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Настраиваем перехватчик, чтобы каждый запрос из стора автоматически содержал токен
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const chatStore = reactive({
  // --- СОСТОЯНИЕ ---
  history: [],
  hasMore: true,
  userEmail: 'User',
  userTier: 'free', // Добавили для Navbar
  currentConversationId: null,
  selectedModel: 'gemini-2.5-flash',
  isLoading: false,

  // --- МЕТОДЫ ---

  // 1. Загрузка данных пользователя (для Navbar и Profile)
  async fetchUser() {
    try {
      const res = await axios.get(`${API_URL}/auth/me`);
      this.userEmail = res.data.email;
      this.userTier = res.data.tier;
    } catch (e) {
      console.error('Ошибка загрузки профиля:', e);
      // Если 401 (токен протух), можно очистить стор
      if (e.response?.status === 401) {
        localStorage.removeItem('token');
      }
    }
  },

  // 2. Загрузка истории чатов (с пагинацией)
  async fetchHistory(reset = true) {
    this.isLoading = true;
    try {
      const offset = reset ? 0 : this.history.length;
      const res = await axios.get(`${API_URL}/conversations`, {
        params: { offset, limit: 10 }
      });
      
      if (reset) {
        this.history = res.data;
      } else {
        this.history.push(...res.data);
      }
      
      // Если пришло меньше 10 записей, значит больше данных в БД нет
      this.hasMore = res.data.length === 10;
    } catch (e) {
      console.error('Ошибка загрузки истории:', e);
    } finally {
      this.isLoading = false;
    }
  },

  // 3. Удаление чата
  async deleteChat(id) {
    try {
      await axios.delete(`${API_URL}/conversations/${id}`); 
      
      // Удаляем локально
      this.history = this.history.filter(item => item.id !== id);
      
      // Если удалили текущий активный чат — сбрасываем ID
      if (this.currentConversationId === id) {
        this.currentConversationId = null;
      }
    } catch (e) { 
      console.error('Ошибка удаления:', e);
      throw e; // Пробрасываем ошибку для уведомления в компоненте
    }
  },

  // 4. Очистка стора при выходе (Logout)
  clear() {
    this.history = [];
    this.currentConversationId = null;
    this.userEmail = 'User';
    this.userTier = 'free';
  }
});