<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Sidebar from './chat/Sidebar.vue';
import ChatMessage from './chat/ChatMessage.vue';

const router = useRouter();
const API_URL = 'http://127.0.0.1:8000';

// Состояние
const prompt = ref('');
const history = ref([]);
const messages = ref([]); // Текущий чат
const currentTaskId = ref(null); // ID активной задачи (для подсветки в меню)
const currentParentId = ref(null); // ID для цепочки (context)
const isGenerating = ref(false);
const userEmail = ref('');
const chatContainer = ref(null); // Для автоскролла

// --- Настройка Axios ---
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

axios.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response && error.response.status === 401) {
      logout();
    }
    return Promise.reject(error);
  }
);

// --- Вспомогательные функции ---
const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1])).sub;
  } catch (e) {
    return 'User';
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// --- Основная логика ---

const fetchHistory = async () => {
  try {
    const response = await axios.get(`${API_URL}/history`);
    history.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

const startNewChat = () => {
  currentTaskId.value = null;
  currentParentId.value = null;
  messages.value = [];
  prompt.value = '';
};

const selectChat = (item) => {
  currentTaskId.value = item.id;
  currentParentId.value = item.id; // Устанавливаем контекст на эту задачу
  prompt.value = '';
  
  // Восстанавливаем "чат" из одной задачи
  // (В будущем можно сделать полноценную историю сообщений, если хранить их в БД)
  messages.value = [
    { role: 'user', content: item.prompt },
    { 
      role: 'ai', 
      content: 'Вот результат генерации по этому запросу:',
      task_id: item.id,
      preview: item.preview_data,
      loading: false,
      error: item.status === 'failed'
    }
  ];
  scrollToBottom();
};

const deleteChat = async (id) => {
  if (!confirm('Удалить этот запрос?')) return;
  try {
    await axios.delete(`${API_URL}/history/${id}`);
    await fetchHistory();
    if (currentTaskId.value === id) startNewChat();
  } catch (error) {
    alert('Ошибка удаления');
  }
};

const sendMessage = async () => {
  const text = prompt.value.trim();
  if (!text) return;

  // 1. Добавляем сообщение пользователя
  messages.value.push({ role: 'user', content: text });
  prompt.value = '';
  isGenerating.value = true;
  scrollToBottom();

  // 2. Добавляем заглушку ИИ
  const aiMsg = ref({
    role: 'ai',
    loading: true,
    progress: 0,
    status_msg: 'Инициализация...',
    content: ''
  });
  messages.value.push(aiMsg.value);
  scrollToBottom();

  try {
    // 3. Отправляем запрос (с контекстом, если есть)
    const response = await axios.post(`${API_URL}/generate`, null, {
      params: { 
        prompt: text,
        parent_task_id: currentParentId.value 
      }
    });

    const newTaskId = response.data.task_id;
    
    // 4. Поллинг статуса
    const interval = setInterval(async () => {
      try {
        // Получаем свежую историю, чтобы узнать статус
        // (В идеале сделать отдельный роут GET /tasks/{id})
        await fetchHistory();
        const task = history.value.find(t => t.id === newTaskId);

        if (task) {
          aiMsg.value.progress = task.progress;
          aiMsg.value.status_msg = task.status_message;

          if (task.status === 'completed' || task.status === 'failed') {
            clearInterval(interval);
            isGenerating.value = false;

            if (task.status === 'completed') {
              aiMsg.value.loading = false;
              aiMsg.value.content = 'Готово! Данные сгенерированы.';
              aiMsg.value.preview = task.preview_data;
              aiMsg.value.task_id = task.id;
              
              // Обновляем контекст на новую задачу
              currentTaskId.value = task.id;
              currentParentId.value = task.id;
            } else {
              aiMsg.value.loading = false;
              aiMsg.value.error = true;
              aiMsg.value.content = task.error_log || 'Неизвестная ошибка';
            }
            scrollToBottom();
          }
        }
      } catch (e) {
        console.error(e);
      }
    }, 2000);

  } catch (error) {
    aiMsg.value.loading = false;
    aiMsg.value.error = true;
    aiMsg.value.content = 'Ошибка соединения с сервером';
    isGenerating.value = false;
  }
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) userEmail.value = parseJwt(token);
  fetchHistory();
});
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-slate-50 font-sans text-slate-800">
    
    <!-- ЛЕВАЯ ПАНЕЛЬ -->
    <Sidebar 
      :history="history" 
      :current-task-id="currentTaskId" 
      :user-email="userEmail"
      @select="selectChat"
      @delete="deleteChat"
      @new="startNewChat"
      @logout="logout"
    />

    <!-- ПРАВАЯ ЧАСТЬ -->
    <main class="relative flex flex-1 flex-col">
      
      <!-- Шапка -->
      <header class="flex h-14 items-center justify-between border-b border-slate-200 bg-white/70 px-6 backdrop-blur">
        <div class="flex rounded-xl bg-slate-100 p-1">
          <button class="rounded-lg bg-white px-4 py-1.5 text-sm font-medium shadow">GPT-4o</button>
          <button class="px-4 py-1.5 text-sm text-slate-500">Synthetic v2</button>
        </div>
      </header>

      <!-- Область чата -->
      <div class="flex-1 overflow-y-auto px-6 py-10 pb-44 space-y-8" ref="chatContainer">
        
        <!-- Приветствие (если пусто) -->
        <div v-if="messages.length === 0" class="mt-20 text-center">
          <div class="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-100">
            <i class="fas fa-magic text-2xl text-blue-600"></i>
          </div>
          <h2 class="text-2xl font-bold text-slate-800">Какой датасет вам нужен?</h2>
          <p class="mt-2 text-slate-500">Опишите структуру, и я создам данные, код и файлы.</p>
        </div>

        <!-- Сообщения -->
        <ChatMessage 
          v-for="(msg, idx) in messages" 
          :key="idx" 
          :message="msg" 
        />
      </div>

      <!-- Поле ввода (фиксировано внизу) -->
      <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-slate-50 via-slate-50 to-transparent px-6 pb-6 pt-12">
        <div class="relative mx-auto max-w-4xl">
          <textarea 
            v-model="prompt"
            @keydown.enter.prevent="sendMessage"
            class="w-full resize-none rounded-2xl border border-slate-200 px-5 py-4 pr-16 shadow-lg outline-none transition focus:border-transparent focus:ring-2 focus:ring-blue-500"
            placeholder="Опишите данные или внесите правки..."
            rows="3"
          ></textarea>
          
          <button 
            @click="sendMessage"
            :disabled="isGenerating || !prompt.trim()"
            class="absolute bottom-3 right-3 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <i v-if="!isGenerating" class="fas fa-arrow-up"></i>
            <i v-else class="fas fa-spinner fa-spin"></i>
          </button>
        </div>
        <p class="mt-3 text-center text-xs text-slate-400">
          SynthGen может допускать ошибки. Проверяйте важные данные.
        </p>
      </div>

    </main>
  </div>
</template>

<style>
/* Кастомный скроллбар */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
</style>