import { reactive } from 'vue';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const chatStore = reactive({
  history: [],
  hasMore: true,
  userEmail: 'User',
  currentConversationId: null,
  selectedModel: 'gemini-2.5-flash',

  async fetchHistory(reset = true) {
    try {
      const offset = reset ? 0 : this.history.length;
      const res = await axios.get(`${API_URL}/conversations`, {
        params: { offset, limit: 10 }
      });
      if (reset) this.history = res.data;
      else this.history.push(...res.data);
      this.hasMore = res.data.length === 10;
    } catch (e) { console.error(e); }
  },

  async deleteChat(id) {
    if (!confirm('Вы уверены?')) return;
    try {
      await axios.delete(`${API_URL}/conversations/${id}`); 
      this.history = this.history.filter(item => item.id !== id);
      if (this.currentConversationId === id) {
        this.currentConversationId = null;
      }
    } catch (e) { 
      console.error('Ошибка удаления:', e);
      alert('Не удалось удалить чат. Проверьте консоль.'); 
    }
  }
});