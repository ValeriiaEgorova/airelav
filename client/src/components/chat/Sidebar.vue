<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps({
  history: { type: Array, default: () => [] },
  currentTaskId: { type: [Number, String], default: null }, 
  userEmail: { type: String, default: 'User' },
  hasMore: { type: Boolean, default: false },
});

const emit = defineEmits(['select', 'delete', 'new', 'logout', 'load-more']);
const route = useRoute();

const isApiPage = computed(() => route.path === '/api-settings');

const handleNewRequest = () => {
  emit('new');
};
</script>

<template>
  <aside class="fixed left-0 top-20 h-[calc(100vh-5rem)] w-72 flex flex-col rounded-r-lg py-8 px-4 gap-2 bg-surface-container-low z-40 hidden md:flex border-r border-outline-variant/10">
    
    <nav class="space-y-2">
      <button 
        @click="handleNewRequest" 
        class="w-full flex items-center gap-4 px-4 py-3 bg-surface-container-lowest text-primary rounded-2xl shadow-sm transition-all duration-300 hover:translate-x-1 border border-outline-variant/10"
      >
        <span class="material-symbols-outlined">add_circle</span>
        <span class="font-medium">New Request</span>
      </button>
    </nav>

    <div class="flex-1 overflow-y-auto custom-scrollbar space-y-1 mt-4 pr-1">
      <div class="px-4 py-2 text-on-surface-variant text-sm font-bold sticky top-0 bg-surface-container-low/90 backdrop-blur z-10">
        Recent Requests
      </div>
      
      <div class="space-y-1">
        <div 
          v-for="item in history" 
          :key="item.id"
          @click="$emit('select', item)"
          class="px-4 py-2 text-sm rounded-full cursor-pointer transition-colors group flex justify-between items-center"
          :class="item.id === currentTaskId ? 'bg-surface-container-highest text-primary font-bold' : 'text-on-surface-variant/80 hover:bg-surface-container-highest'"
        >
          <span class="truncate pr-2">{{ item.title || item.id.split('-')[0] }}</span>
          
          <button 
            @click.stop="$emit('delete', item.id)" 
            class="opacity-0 group-hover:opacity-100 text-error/60 hover:text-error transition-opacity flex items-center justify-center"
            title="Delete"
          >
            <span class="material-symbols-outlined text-[16px]">delete</span>
          </button>
        </div>

        <button 
          v-if="hasMore" 
          @click="$emit('load-more')"
          class="w-full text-center py-2 text-xs font-bold text-primary/60 hover:text-primary transition-colors"
        >
          Load more...
        </button>
      </div>
    </div>
    
    <div class="mt-auto pt-6 space-y-1">
      <router-link 
        to="/api-settings" 
        class="w-full flex items-center gap-4 px-4 py-3 rounded-2xl font-medium transition-all duration-300"
        :class="isApiPage 
          ? 'bg-primary text-on-primary shadow-sm' 
          : 'text-on-surface-variant hover:bg-surface-container-highest'"
      >
        <span class="material-symbols-outlined">vpn_key</span>
        <span>API Keys</span>
      </router-link>
      
      <button 
        @click="$emit('logout')" 
        class="w-full flex items-center gap-4 px-4 py-3 text-error/70 hover:text-error hover:bg-error-container/20 rounded-2xl transition-all duration-300"
      >
        <span class="material-symbols-outlined">logout</span>
        <span>Logout</span>
      </button>
    </div>
  </aside>
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
</style>