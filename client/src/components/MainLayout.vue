<script setup>
import { ref, onMounted } from 'vue'; // Добавили ref
import { useRouter } from 'vue-router';
import Sidebar from './chat/Sidebar.vue';
import Navbar from './chat/Navbar.vue';
import BaseModal from './common/BaseModal.vue'; // 1. Импортируем нашу модалку
import { chatStore } from '../chatStore';
import { useToast } from 'vue-toastification'; // Для красивого уведомления

const router = useRouter();
const toast = useToast();

// --- СОСТОЯНИЕ МОДАЛКИ ---
const showDeleteModal = ref(false);
const chatIdToDelete = ref(null);

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

const handleSelect = (chat) => {
  chatStore.currentConversationId = chat.id;
  if (router.currentRoute.value.path !== '/') {
    router.push('/');
  }
};

const handleNew = () => {
  chatStore.currentConversationId = null;
  router.push('/');
};

// --- ЛОГИКА КРАСИВОГО УДАЛЕНИЯ ---

// 2. Эта функция вызывается при клике на корзину в сайдбаре
const prepareDelete = (id) => {
  chatIdToDelete.value = id;
  showDeleteModal.value = true; // Показываем нашу модалку вместо alert
};

// 3. Эта функция вызывается, когда пользователь нажал "Delete" в нашей модалке
const confirmDelete = async () => {
  if (!chatIdToDelete.value) return;

  try {
    await chatStore.deleteChat(chatIdToDelete.value);
    toast.success('Chat deleted successfully');

    // Если удалили тот чат, в котором сейчас находимся — сбрасываем состояние
    if (chatStore.currentConversationId === chatIdToDelete.value) {
      chatStore.currentConversationId = null;
      router.push('/');
    }
  } catch (error) {
    toast.error('Failed to delete chat');
  } finally {
    showDeleteModal.value = false;
    chatIdToDelete.value = null;
  }
};

onMounted(async () => {
  await chatStore.fetchUser();
  await chatStore.fetchHistory();
});
</script>

<template>
  <div class="flex min-h-screen overflow-hidden bg-background">
    <!-- 4. НАША КРАСИВАЯ МОДАЛКА -->
    <BaseModal
      :show="showDeleteModal"
      title="Delete Conversation?"
      description="All generated data and files in this chat will be permanently removed. This action cannot be undone."
      confirm-text="Delete Chat"
      :is-destructive="true"
      @close="showDeleteModal = false"
      @confirm="confirmDelete"
    />

    <Sidebar
      :history="chatStore.history"
      :current-task-id="chatStore.currentConversationId"
      :has-more="chatStore.hasMore"
      @select="handleSelect"
      @new="handleNew"
      @delete="prepareDelete"
      @load-more="chatStore.fetchHistory(false)"
      @logout="logout"
    />
    <!-- Заменили @delete="chatStore.deleteChat" на @delete="prepareDelete" -->

    <main class="relative flex h-screen flex-1 flex-col md:ml-72">
      <Navbar
        :user-email="chatStore.userEmail"
        :user-tier="chatStore.userTier"
        :selected-model="chatStore.selectedModel"
        @update:model="(val) => (chatStore.selectedModel = val)"
      />

      <div class="flex-1 overflow-hidden pt-20">
        <RouterView />
      </div>
    </main>
  </div>
</template>
