<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import { chatStore } from '../chatStore';
import ChatMessage from './chat/ChatMessage.vue';
import BaseModal from './common/BaseModal.vue'; // Убедитесь, что путь верный

const toast = useToast();
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// --- СОСТОЯНИЕ (STATE) ---
const prompt = ref('');
const messages = ref([]);
const isGenerating = ref(false);
const isEnhancing = ref(false);
const chatContainer = ref(null);
const pollingInterval = ref(null);

// --- ЛОГИКА ЛИМИТА СИМВОЛОВ ---
const MAX_CHARS = 1000;
const charCount = computed(() => prompt.value.length);
const isNearLimit = computed(() => charCount.value > MAX_CHARS * 0.9);
const isOverLimit = computed(() => charCount.value >= MAX_CHARS);

// --- МОДАЛКА УДАЛЕНИЯ ---
const showDeleteModal = ref(false);
const chatToDelete = ref(null);

const scrollToBottom = async (force = false) => {
  await nextTick();
  if (chatContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = chatContainer.value;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;

    // Скроллим только если пользователь почти внизу (запас 150px) или если это force-вызов
    if (force || distanceToBottom < 150) {
      chatContainer.value.scrollTo({
        top: scrollHeight,
        behavior: 'smooth',
      });
    }
  }
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
};

// --- ЛОГИКА ЧАТА ---

const loadFullChat = async (id) => {
  if (!id) {
    messages.value = [];
    return;
  }

  if (pollingInterval.value) clearInterval(pollingInterval.value);

  try {
    const response = await axios.get(`${API_URL}/conversations/${id}`);
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
    toast.error('Failed to load chat history');
  }
};

const enhancePrompt = async () => {
  const text = prompt.value.trim();
  if (!text || isEnhancing.value || isGenerating.value) return;

  isEnhancing.value = true;
  try {
    const response = await axios.post(`${API_URL}/enhance-prompt`, {
      prompt: text,
    });
    if (response.data && response.data.enhanced_prompt) {
      prompt.value = response.data.enhanced_prompt;
      toast.info('Prompt enhanced with AI');
    }
  } catch (error) {
    console.error('Ошибка при улучшении промпта:', error);
    toast.error('Failed to enhance prompt');
  } finally {
    isEnhancing.value = false;
  }
};

const sendMessage = async () => {
  const text = prompt.value.trim();
  if (!text || isGenerating.value || isOverLimit.value) return;

  // 1. Очищаем старый интервал, если он был
  if (pollingInterval.value) clearInterval(pollingInterval.value);

  // 2. Добавляем сообщение пользователя
  messages.value.push({ role: 'user', content: text });
  prompt.value = '';
  isGenerating.value = true;
  await scrollToBottom();

  // 3. Создаем объект сообщения ИИ и запоминаем его индекс
  const aiMessageIndex =
    messages.value.push({
      role: 'ai',
      loading: true,
      progress: 0,
      status_msg: 'Инициализация...',
      content: '',
      task_id: null,
      preview: null,
      error: false,
    }) - 1;

  await scrollToBottom();

  try {
    // 4. Запрос на генерацию
    const response = await axios.post(`${API_URL}/generate`, {
      prompt: text,
      conversation_id: chatStore.currentConversationId,
      model: chatStore.selectedModel,
    });

    const { task_id, conversation_id } = response.data;

    // Привязываем ID к сообщению
    messages.value[aiMessageIndex].task_id = task_id;

    // Если это новый чат — обновляем глобальный ID и историю в сайдбаре
    if (!chatStore.currentConversationId) {
      chatStore.currentConversationId = conversation_id;
      await chatStore.fetchHistory(true);
    }

    // 5. ЦИКЛ ОПРОСА (Polling)
    pollingInterval.value = setInterval(async () => {
      try {
        // Опрашиваем статус КОНКРЕТНОЙ задачи (этот эндпоинт мы создавали в main.py)
        const taskRes = await axios.get(`${API_URL}/tasks/${task_id}`);
        const data = taskRes.data;

        // Прямое обновление полей объекта в массиве
        messages.value[aiMessageIndex].progress = data.progress;
        messages.value[aiMessageIndex].status_msg = data.status_message;

        console.log(`Прогресс задачи ${task_id}: ${data.progress}%`); // Для отладки в консоли браузера

        if (data.status === 'completed') {
          clearInterval(pollingInterval.value);
          messages.value[aiMessageIndex].loading = false;
          messages.value[aiMessageIndex].content = 'Готово! Вот результат:';
          messages.value[aiMessageIndex].preview = data.preview_data;
          messages.value[aiMessageIndex].file_size = data.file_size;
          messages.value[aiMessageIndex].row_count = data.row_count;
          isGenerating.value = false;
          await scrollToBottom();
        } else if (data.status === 'failed') {
          clearInterval(pollingInterval.value);
          messages.value[aiMessageIndex].loading = false;
          messages.value[aiMessageIndex].error = true;
          messages.value[aiMessageIndex].content = `Ошибка: ${data.error_log}`;
          isGenerating.value = false;
          await scrollToBottom();
        }
      } catch (e) {
        console.error('Ошибка в цикле опроса:', e);
        // Не очищаем интервал при временной ошибке сети, пробуем дальше
      }
    }, 1500);
  } catch (error) {
    console.error('Ошибка при отправке:', error);
    const errorMsg =
      error.response?.data?.detail || 'Ошибка соединения с сервером.';
    messages.value[aiMessageIndex].loading = false;
    messages.value[aiMessageIndex].error = true;
    messages.value[aiMessageIndex].content = errorMsg;
    isGenerating.value = false;
  }
};

const confirmDelete = async () => {
  if (!chatToDelete.value) return;
  try {
    await chatStore.deleteChat(chatToDelete.value);
    showDeleteModal.value = false;
    messages.value = [];
    toast.success('Conversation deleted');
  } catch (e) {
    toast.error('Failed to delete chat');
  }
};

// --- WATCHERS & LIFECYCLE ---

watch(
  () => chatStore.currentConversationId,
  (newId) => {
    if (newId) {
      loadFullChat(newId);
    } else {
      messages.value = [];
      if (pollingInterval.value) clearInterval(pollingInterval.value);
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (chatStore.currentConversationId) {
    loadFullChat(chatStore.currentConversationId);
  }
});
</script>

<template>
  <!-- МОДАЛКА УДАЛЕНИЯ -->
  <BaseModal
    :show="showDeleteModal"
    title="Delete Chat?"
    description="This action cannot be undone. All generated files for this conversation will be removed."
    confirm-text="Delete"
    :is-destructive="true"
    @close="showDeleteModal = false"
    @confirm="confirmDelete"
  />

  <div
    class="relative flex h-full w-full flex-1 flex-col overflow-hidden bg-background"
  >
    <!-- Область сообщений -->
    <section
      ref="chatContainer"
      class="custom-scrollbar mx-auto flex w-full max-w-6xl flex-1 flex-col gap-12 overflow-y-auto px-6 pb-32 pt-8"
    >
      <!-- Пустое состояние -->
      <div
        v-if="messages.length === 0"
        class="mt-20 flex flex-col items-center text-center opacity-70"
      >
        <div
          class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-container-highest"
        >
          <span class="material-symbols-outlined text-[32px] text-primary"
            >auto_awesome</span
          >
        </div>
        <h2 class="font-headline text-3xl font-bold text-on-surface">
          Describe your dataset
        </h2>
        <p class="mt-2 max-w-md text-on-surface-variant">
          Enter a prompt below to generate synthetic data, schemas, or exports
          in CSV, JSON, and Excel.
        </p>
      </div>

      <!-- Сообщения -->
      <ChatMessage v-for="(msg, idx) in messages" :key="idx" :message="msg" />
    </section>

    <!-- Подвал с полем ввода -->
    <footer
      class="absolute bottom-0 left-0 right-0 z-10 bg-gradient-to-t from-background via-background to-transparent px-4 pb-8 pt-12 md:px-8"
    >
      <div class="relative mx-auto max-w-4xl">
        <!-- Предупреждение о лимите -->
        <transition name="fade">
          <div
            v-if="isOverLimit"
            class="absolute -top-8 left-0 right-0 mx-auto w-max rounded-full border border-red-200 bg-red-100 px-4 py-1 text-center text-xs font-bold text-red-500 shadow-sm"
          >
            Maximum limit reached ({{ MAX_CHARS }} chars)
          </div>
        </transition>

        <div
          class="relative flex items-center rounded-full border border-outline-variant/10 bg-surface-container-lowest p-2 shadow-xl transition-all focus-within:ring-2"
          :class="
            isOverLimit
              ? 'border-red-500/50 focus-within:ring-red-500/50'
              : 'focus-within:ring-primary/20'
          "
        >
          <!-- Кнопка улучшения промпта (Вместо скрепки) -->
          <button
            :disabled="isEnhancing || !prompt.trim() || isGenerating"
            title="Improve prompt with AI"
            class="group flex h-12 w-12 shrink-0 items-center justify-center transition-colors disabled:cursor-not-allowed disabled:opacity-50"
            :class="
              prompt.trim()
                ? 'rounded-full text-primary hover:bg-primary/10'
                : 'text-on-surface-variant'
            "
            @click="enhancePrompt"
          >
            <span
              v-if="!isEnhancing"
              class="material-symbols-outlined transition-transform group-hover:scale-110"
            >
              auto_fix_high
            </span>
            <span
              v-else
              class="material-symbols-outlined animate-spin text-primary"
            >
              sync
            </span>
          </button>

          <textarea
            v-model="prompt"
            :maxlength="MAX_CHARS"
            class="h-[48px] flex-1 resize-none border-none bg-transparent px-2 py-3 font-medium leading-[24px] text-on-surface outline-none placeholder:text-on-surface-variant/40 focus:ring-0"
            placeholder="Describe the dataset you want to generate..."
            rows="1"
            @keydown.enter.prevent="sendMessage"
          ></textarea>

          <div class="flex shrink-0 items-center gap-3 pr-2">
            <!-- Счетчик символов -->
            <span
              v-if="charCount > 0"
              class="text-[10px] font-bold tabular-nums transition-colors"
              :class="
                isNearLimit ? 'text-red-500' : 'text-on-surface-variant/40'
              "
            >
              {{ charCount }} / {{ MAX_CHARS }}
            </span>

            <!-- Кнопка отправки -->
            <button
              :disabled="isGenerating || !prompt.trim() || isOverLimit"
              class="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-white shadow-lg shadow-primary/30 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
              :class="{ 'bg-red-500 shadow-red-500/30': isOverLimit }"
              @click="sendMessage"
            >
              <span
                v-if="!isGenerating"
                class="material-symbols-outlined"
                style="font-variation-settings: 'FILL' 1"
                >send</span
              >
              <span v-else class="material-symbols-outlined animate-spin"
                >sync</span
              >
            </button>
          </div>
        </div>

        <!-- Значки внизу -->
        <div class="mt-3 flex justify-center gap-6">
          <span
            class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/30"
          >
            <span class="material-symbols-outlined text-[14px]">shield</span>
            Isolated Sandbox
          </span>
          <span
            class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/30"
          >
            <span class="material-symbols-outlined text-[14px]">bolt</span>
            Real-time generation
          </span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}
.font-headline {
  font-family: 'Manrope', sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
