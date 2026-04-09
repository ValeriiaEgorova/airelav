<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Sidebar from './chat/Sidebar.vue';
import Navbar from './chat/Navbar.vue';
import { chatStore } from '../chatStore';

const router = useRouter();

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

onMounted(() => {
  chatStore.fetchHistory(true);
});
</script>

<template>
  <div class="flex min-h-screen bg-background overflow-hidden">
    <Sidebar 
      :history="chatStore.history"
      :current-task-id="chatStore.currentConversationId"
      :has-more="chatStore.hasMore"
      @select="handleSelect"
      @new="handleNew"
      @delete="chatStore.deleteChat"
      @load-more="chatStore.fetchHistory(false)"
      @logout="logout"
    />

    <main class="md:ml-72 flex-1 flex flex-col h-screen relative">
      <Navbar 
        :user-email="chatStore.userEmail" 
        :selected-model="chatStore.selectedModel"
        @update:model="(val) => chatStore.selectedModel = val"
      />
      
      <div class="flex-1 overflow-hidden pt-20">
         <RouterView /> 
      </div>
    </main>
  </div>
</template>