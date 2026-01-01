<script setup>
import { computed } from 'vue';

const props = defineProps({
  history: { type: Array, default: () => [] },
  currentTaskId: { type: Number, default: null },
  userEmail: { type: String, default: 'User' }
});

const emit = defineEmits(['select', 'delete', 'new', 'logout']);

const todayHistory = computed(() => props.history);

const userInitial = computed(() => {
  return props.userEmail ? props.userEmail[0].toUpperCase() : 'U';
});
</script>

<template>
  <aside class="flex w-72 flex-col border-r border-slate-800 bg-slate-900 text-slate-300">
    
    <div class="flex h-16 items-center border-b border-slate-800 px-6">
      <div class="mr-3 flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow">
        <i class="fas fa-cube text-sm text-white"></i>
      </div>
      <span class="font-semibold text-white">SynthGen AI</span>
    </div>

    <div class="p-4">
      <button 
        @click="$emit('new')"
        class="flex w-full items-center justify-between rounded-xl bg-slate-800 px-4 py-3 text-sm font-medium transition hover:bg-slate-700 shadow"
      >
        <span class="flex items-center gap-2">
          <i class="fas fa-plus"></i> Новый чат
        </span>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-3 space-y-1 custom-scrollbar">
      <div class="px-3 py-2 text-xs uppercase tracking-wider text-slate-500">История</div>

      <div 
        v-for="item in todayHistory" 
        :key="item.id"
        @click="$emit('select', item)"
        class="group flex cursor-pointer items-center gap-3 rounded-xl p-3 transition"
        :class="item.id === currentTaskId ? 'bg-slate-800 text-white shadow' : 'hover:bg-slate-800 text-slate-400'"
      >
        <i class="far fa-comment-alt" :class="item.id === currentTaskId ? 'text-blue-400' : 'text-slate-500'"></i>
        <span class="flex-1 truncate text-sm">{{ item.title }}</span>
        
        <button 
          @click.stop="$emit('delete', item.id)"
          class="text-slate-500 opacity-0 transition hover:text-red-400 group-hover:opacity-100"
          title="Удалить"
        >
          <i class="fas fa-trash-alt"></i>
        </button>
      </div>
    </div>

    <div class="border-t border-slate-800 p-4">
      <div class="flex items-center gap-3 rounded-xl p-2 transition hover:bg-slate-800">
        <div class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-purple-400 to-pink-500 text-xs font-bold text-white">
          {{ userInitial }}
        </div>
        <div class="flex-1 overflow-hidden">
          <p class="truncate text-sm text-white">{{ userEmail }}</p>
          <p class="text-xs text-slate-500">Free Plan</p>
        </div>
        <button @click="$emit('logout')" class="text-slate-400 hover:text-white" title="Выйти">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </div>
  </aside>
</template>