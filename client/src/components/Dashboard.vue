<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Sidebar from './chat/Sidebar.vue';
import ChatMessage from './chat/ChatMessage.vue';

const router = useRouter();
const API_URL = 'http://127.0.0.1:8000';

const prompt = ref('');
const history = ref([]);
const messages = ref([]);
const currentConversationId = ref(null);
const isGenerating = ref(false);
const userEmail = ref('');
const chatContainer = ref(null);
const pollingInterval = ref(null);
const selectedModel = ref('gemini-2.5-flash');
const limit = 3;
const hasMoreHistory = ref(true);

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

const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1])).sub;
  } catch (e) {
    return 'User';
  }
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const fetchHistory = async (reset = true) => {
  try {
    // 1. Вычисляем offset автоматически
    // Если это сброс (reset=true), начинаем с 0.
    // Если догрузка (reset=false), пропускаем столько элементов, сколько уже есть в списке.
    const requestOffset = reset ? 0 : history.value.length;

    const response = await axios.get(`${API_URL}/conversations`, {
      params: {
        offset: requestOffset,
        limit: limit,
      },
    });

    const newItems = response.data;

    // 2. Проверяем, есть ли еще данные
    // Если пришло меньше чем лимит (или 0), значит это конец.
    if (newItems.length < limit) {
      hasMoreHistory.value = false;
    } else {
      hasMoreHistory.value = true;
    }

    // 3. Обновляем список
    if (reset) {
      history.value = newItems;
    } else {
      // Добавляем новые элементы в конец массива
      history.value.push(...newItems);
    }
  } catch (error) {
    console.error('Ошибка загрузки истории:', error);
  }
};

const setModel = (model) => {
  selectedModel.value = model;
};

const startNewChat = () => {
  currentConversationId.value = null;
  messages.value = [];
  prompt.value = '';
  if (pollingInterval.value) clearInterval(pollingInterval.value);
};

const selectChat = async (conversation) => {
  if (currentConversationId.value === conversation.id) return;

  currentConversationId.value = conversation.id;
  prompt.value = '';
  if (pollingInterval.value) clearInterval(pollingInterval.value);

  try {
    const response = await axios.get(
      `${API_URL}/conversations/${conversation.id}`
    );
    const tasks = response.data;

    messages.value = [];
    tasks.forEach((task) => {
      messages.value.push({ role: 'user', content: task.prompt });

      messages.value.push({
        role: 'ai',
        task_id: task.id,
        content:
          task.status === 'completed'
            ? 'Готово! Вот результат:'
            : task.error_log
              ? `Ошибка: ${task.error_log}`
              : 'Обработка...',
        preview: task.preview_data,
        file_size: task.file_size,
        row_count: task.row_count,
        loading: task.status === 'pending' || task.status === 'processing',
        error: task.status === 'failed',
        progress: task.progress,
        status_msg: task.status_message,
      });
    });

    scrollToBottom();
  } catch (error) {
    console.error('Ошибка загрузки чата:', error);
  }
};

const deleteChat = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить этот чат?')) return;
  try {
    await axios.delete(`${API_URL}/history/${id}`);
    await fetchHistory();
    if (currentConversationId.value === id) startNewChat();
  } catch (error) {
    alert('Не удалось удалить чат');
  }
};

const sendMessage = async () => {
  const text = prompt.value.trim();
  if (!text) return;

  messages.value.push({ role: 'user', content: text });
  prompt.value = '';
  isGenerating.value = true;
  scrollToBottom();

  const aiMessage = ref({
    role: 'ai',
    loading: true,
    progress: 0,
    status_msg: 'Инициализация...',
    content: '',
    task_id: null,
    preview: null,
  });
  messages.value.push(aiMessage.value);
  scrollToBottom();

  try {
    const response = await axios.post(`${API_URL}/generate`, {
      prompt: text,
      conversation_id: currentConversationId.value,
      model: selectedModel.value, // Убедитесь, что эта переменная есть в setup
    });

    const { task_id, conversation_id } = response.data;
    aiMessage.value.task_id = task_id;

    if (!currentConversationId.value) {
      currentConversationId.value = conversation_id;
      fetchHistory();
    }

    pollingInterval.value = setInterval(async () => {
      try {
        const chatRes = await axios.get(
          `${API_URL}/conversations/${conversation_id}`
        );
        const tasks = chatRes.data;
        const currentTaskData = tasks.find((t) => t.id === task_id);

        if (currentTaskData) {
          aiMessage.value.progress = currentTaskData.progress;
          aiMessage.value.status_msg = currentTaskData.status_message;

          if (currentTaskData.status === 'completed') {
            aiMessage.value.loading = false;
            aiMessage.value.content = 'Готово! Вот результат:';
            aiMessage.value.preview = currentTaskData.preview_data;
            aiMessage.value.file_size = currentTaskData.file_size;
            aiMessage.value.row_count = currentTaskData.row_count;
            clearInterval(pollingInterval.value);
            isGenerating.value = false;
            scrollToBottom();
          } else if (currentTaskData.status === 'failed') {
            aiMessage.value.loading = false;
            aiMessage.value.error = true;
            aiMessage.value.content = `Ошибка: ${currentTaskData.error_log}`;
            clearInterval(pollingInterval.value);
            isGenerating.value = false;
            scrollToBottom();
          }
        }
      } catch (e) {
        console.error('Ошибка поллинга:', e);
      }
    }, 2000);
  } catch (error) {
    console.error(error);
    aiMessage.value.loading = false;
    aiMessage.value.error = true;
    aiMessage.value.content = 'Ошибка соединения с сервером.';
    isGenerating.value = false;
  }
};

onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) {
    userEmail.value = parseJwt(token);
  }
  fetchHistory(true);
});
</script>

<template>
  <div
    class="flex h-screen overflow-hidden bg-slate-50 font-sans text-slate-800"
  >
    <Sidebar
      :history="history"
      :current-task-id="currentConversationId"
      :user-email="userEmail"
      :has-more="hasMoreHistory"
      @select="selectChat"
      @delete="deleteChat"
      @new="startNewChat"
      @logout="logout"
      @load-more="fetchHistory(false)"
    />

    <main class="relative flex flex-1 flex-col">
      <header
        class="flex h-14 items-center justify-between border-b border-slate-200 bg-white/70 px-6 backdrop-blur"
      >
        <div class="flex rounded-xl bg-slate-100 p-1">
          <button
            class="rounded-lg px-4 py-1.5 text-sm font-medium transition-all"
            :class="
              selectedModel === 'gemini-2.5-flash'
                ? 'text-brand-600 bg-white shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            "
            @click="setModel('gemini-2.5-flash')"
          >
            Flash 2.5
          </button>

          <button
            class="rounded-lg px-4 py-1.5 text-sm font-medium transition-all"
            :class="
              selectedModel === 'gemini-2.5-flash-lite'
                ? 'text-brand-600 bg-white shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            "
            @click="setModel('gemini-2.5-flash-lite')"
          >
            Flash Lite
          </button>
        </div>
      </header>

      <div
        ref="chatContainer"
        class="flex-1 space-y-8 overflow-y-auto px-6 py-10 pb-44"
      >
        <div v-if="messages.length === 0" class="mt-20 text-center">
          <div
            class="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-100"
          >
            <i class="fas fa-magic text-2xl text-blue-600"></i>
          </div>
          <h2 class="text-2xl font-bold text-slate-800">
            Какой датасет вам нужен?
          </h2>
          <p class="mt-2 text-slate-500">
            Опишите структуру, и я создам данные, код и файлы.
          </p>
        </div>

        <ChatMessage v-for="(msg, idx) in messages" :key="idx" :message="msg" />
      </div>

      <div
        class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-slate-50 via-slate-50 to-transparent px-6 pb-6 pt-12"
      >
        <div class="relative mx-auto max-w-4xl">
          <textarea
            v-model="prompt"
            class="w-full resize-none rounded-2xl border border-slate-200 px-5 py-4 pr-16 shadow-lg outline-none transition focus:border-transparent focus:ring-2 focus:ring-blue-500"
            placeholder="Опишите данные или внесите правки..."
            rows="3"
            @keydown.enter.prevent="sendMessage"
          ></textarea>

          <button
            :disabled="isGenerating || !prompt.trim()"
            class="absolute bottom-3 right-3 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-50"
            @click="sendMessage"
          >
            <i v-if="!isGenerating" class="fas fa-arrow-up"></i>
            <i v-else class="fas fa-spinner fa-spin"></i>
          </button>
        </div>
        <p class="mt-3 text-center text-xs text-slate-400">
          AIrelav может допускать ошибки. Проверяйте важные данные.
        </p>
      </div>
    </main>
  </div>
</template>

<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
</style>
