<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import axios from 'axios';
import { useToast } from "vue-toastification";
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

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
        content: task.status === 'completed' ? 'Готово! Вот результат:' : task.error_log ? `Ошибка: ${task.error_log}` : 'Обработка...',
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
    toast.error("Failed to load chat history");
  }
};

const enhancePrompt = async () => {
  const text = prompt.value.trim();
  if (!text || isEnhancing.value || isGenerating.value) return;

  isEnhancing.value = true;
  try {
    const response = await axios.post(`${API_URL}/enhance-prompt`, { prompt: text });
    if (response.data && response.data.enhanced_prompt) {
      prompt.value = response.data.enhanced_prompt;
      toast.info("Prompt enhanced with AI");
    }
  } catch (error) {
    console.error("Ошибка при улучшении промпта:", error);
    toast.error("Failed to enhance prompt");
  } finally {
    isEnhancing.value = false;
  }
};

const sendMessage = async () => {
  const text = prompt.value.trim();
  if (!text || isGenerating.value || isOverLimit.value) return;

  messages.value.push({ role: 'user', content: text });
  prompt.value = '';
  isGenerating.value = true;
  scrollToBottom();

  const aiMessage = ref({
    role: 'ai', loading: true, progress: 0, status_msg: 'Инициализация...', content: '', task_id: null, preview: null,
  });
  messages.value.push(aiMessage.value);
  scrollToBottom();

  try {
    const response = await axios.post(`${API_URL}/generate`, {
      prompt: text, 
      conversation_id: chatStore.currentConversationId, 
      model: chatStore.selectedModel,
    });
    
    const { task_id, conversation_id } = response.data;
    aiMessage.value.task_id = task_id;

    if (!chatStore.currentConversationId) {
      chatStore.currentConversationId = conversation_id;
      chatStore.fetchHistory(true);
    }

    pollingInterval.value = setInterval(async () => {
      try {
        const chatRes = await axios.get(`${API_URL}/conversations/${conversation_id}`);
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
            toast.success("Generation complete");
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
    const msg = error.response?.data?.detail || 'Ошибка соединения с сервером.';
    aiMessage.value.loading = false; 
    aiMessage.value.error = true; 
    aiMessage.value.content = msg;
    isGenerating.value = false;
    toast.error(msg);
  }
};

const confirmDelete = async () => {
  if (!chatToDelete.value) return;
  try {
    await chatStore.deleteChat(chatToDelete.value);
    showDeleteModal.value = false;
    messages.value = [];
    toast.success("Conversation deleted");
  } catch (e) {
    toast.error("Failed to delete chat");
  }
};

// --- WATCHERS & LIFECYCLE ---

watch(() => chatStore.currentConversationId, (newId) => {
  if (newId) {
    loadFullChat(newId);
  } else {
    messages.value = [];
    if (pollingInterval.value) clearInterval(pollingInterval.value);
  }
}, { immediate: true });

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
    confirmText="Delete"
    :isDestructive="true"
    @close="showDeleteModal = false"
    @confirm="confirmDelete"
  />

  <div class="flex-1 flex flex-col relative w-full h-full overflow-hidden bg-background">
    
    <!-- Область сообщений -->
    <section ref="chatContainer" class="flex-1 overflow-y-auto pt-8 pb-32 px-6 max-w-6xl mx-auto w-full flex flex-col gap-12 custom-scrollbar">
      
      <!-- Пустое состояние -->
      <div v-if="messages.length === 0" class="mt-20 flex flex-col items-center text-center opacity-70">
        <div class="w-16 h-16 rounded-2xl bg-surface-container-highest flex items-center justify-center mb-6">
          <span class="material-symbols-outlined text-[32px] text-primary">auto_awesome</span>
        </div>
        <h2 class="font-headline text-3xl font-bold text-on-surface">Describe your dataset</h2>
        <p class="mt-2 text-on-surface-variant max-w-md">
          Enter a prompt below to generate synthetic data, schemas, or exports in CSV, JSON, and Excel.
        </p>
      </div>

      <!-- Сообщения -->
      <ChatMessage 
        v-for="(msg, idx) in messages" 
        :key="idx" 
        :message="msg" 
      />
    </section>

    <!-- Подвал с полем ввода -->
    <footer class="absolute bottom-0 right-0 left-0 bg-gradient-to-t from-background via-background to-transparent pt-12 pb-8 px-4 md:px-8 z-10">
      <div class="max-w-4xl mx-auto relative">
        
        <!-- Предупреждение о лимите -->
        <transition name="fade">
          <div v-if="isOverLimit" class="absolute -top-8 left-0 right-0 text-center text-xs font-bold text-red-500 bg-red-100 py-1 rounded-full w-max mx-auto px-4 shadow-sm border border-red-200">
            Maximum limit reached ({{ MAX_CHARS }} chars)
          </div>
        </transition>

        <div class="relative bg-surface-container-lowest rounded-full shadow-xl border border-outline-variant/10 p-2 flex items-center transition-all focus-within:ring-2"
             :class="isOverLimit ? 'focus-within:ring-red-500/50 border-red-500/50' : 'focus-within:ring-primary/20'">
          
          <!-- Кнопка улучшения промпта (Вместо скрепки) -->
          <button 
            @click="enhancePrompt"
            :disabled="isEnhancing || !prompt.trim() || isGenerating"
            title="Improve prompt with AI"
            class="w-12 h-12 flex items-center justify-center transition-colors group disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            :class="prompt.trim() ? 'text-primary hover:bg-primary/10 rounded-full' : 'text-on-surface-variant'"
          >
            <span v-if="!isEnhancing" class="material-symbols-outlined group-hover:scale-110 transition-transform">
              auto_fix_high
            </span>
            <span v-else class="material-symbols-outlined animate-spin text-primary">
              sync
            </span>
          </button>
          
          <textarea 
            v-model="prompt"
            :maxlength="MAX_CHARS"
            @keydown.enter.prevent="sendMessage"
            class="flex-1 bg-transparent border-none focus:ring-0 py-3 px-2 text-on-surface resize-none font-medium placeholder:text-on-surface-variant/40 outline-none h-[48px] leading-[24px]" 
            placeholder="Describe the dataset you want to generate..." 
            rows="1"
          ></textarea>
          
          <div class="flex items-center gap-3 pr-2 shrink-0">
            <!-- Счетчик символов -->
            <span 
              v-if="charCount > 0"
              class="text-[10px] font-bold transition-colors tabular-nums"
              :class="isNearLimit ? 'text-red-500' : 'text-on-surface-variant/40'"
            >
              {{ charCount }} / {{ MAX_CHARS }}
            </span>

            <!-- Кнопка отправки -->
            <button 
              :disabled="isGenerating || !prompt.trim() || isOverLimit"
              @click="sendMessage"
              class="bg-primary text-white w-12 h-12 rounded-full flex items-center justify-center shadow-lg shadow-primary/30 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
              :class="{'bg-red-500 shadow-red-500/30': isOverLimit}"
            >
              <span v-if="!isGenerating" class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">send</span>
              <span v-else class="material-symbols-outlined animate-spin">sync</span>
            </button>
          </div>
        </div>
        
        <!-- Значки внизу -->
        <div class="mt-3 flex justify-center gap-6">
          <span class="flex items-center gap-1.5 text-[10px] font-bold text-on-surface-variant/30 uppercase tracking-widest">
            <span class="material-symbols-outlined text-[14px]">shield</span> Isolated Sandbox
          </span>
          <span class="flex items-center gap-1.5 text-[10px] font-bold text-on-surface-variant/30 uppercase tracking-widest">
            <span class="material-symbols-outlined text-[14px]">bolt</span> Real-time generation
          </span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.05); border-radius: 10px; }
.font-headline { font-family: 'Manrope', sans-serif; }

.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }
</style>