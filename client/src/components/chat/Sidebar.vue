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
  <aside
    class="fixed left-0 top-20 z-40 flex hidden h-[calc(100vh-5rem)] w-72 flex-col gap-2 rounded-r-lg border-r border-outline-variant/10 bg-surface-container-low px-4 py-8 md:flex"
  >
    <nav class="space-y-2">
      <button
        class="flex w-full items-center gap-4 rounded-2xl border border-outline-variant/10 bg-surface-container-lowest px-4 py-3 text-primary shadow-sm transition-all duration-300 hover:translate-x-1"
        @click="handleNewRequest"
      >
        <span class="material-symbols-outlined">add_circle</span>
        <span class="font-medium">New Request</span>
      </button>
    </nav>

    <div class="custom-scrollbar mt-4 flex-1 space-y-1 overflow-y-auto pr-1">
      <div
        class="sticky top-0 z-10 bg-surface-container-low/90 px-4 py-2 text-sm font-bold text-on-surface-variant backdrop-blur"
      >
        Recent Requests
      </div>

      <div class="space-y-1">
        <div
          v-for="item in history"
          :key="item.id"
          class="group flex cursor-pointer items-center justify-between rounded-full px-4 py-2 text-sm transition-colors"
          :class="
            item.id === currentTaskId
              ? 'bg-surface-container-highest font-bold text-primary'
              : 'text-on-surface-variant/80 hover:bg-surface-container-highest'
          "
          @click="$emit('select', item)"
        >
          <span class="truncate pr-2">{{
            item.title || item.id.split('-')[0]
          }}</span>

          <button
            class="flex items-center justify-center text-error/60 opacity-0 transition-opacity hover:text-error group-hover:opacity-100"
            title="Delete"
            @click.stop="$emit('delete', item.id)"
          >
            <span class="material-symbols-outlined text-[16px]">delete</span>
          </button>
        </div>

        <button
          v-if="hasMore"
          class="w-full py-2 text-center text-xs font-bold text-primary/60 transition-colors hover:text-primary"
          @click="$emit('load-more')"
        >
          Load more...
        </button>
      </div>
    </div>

    <div class="mt-auto space-y-1 pt-6">
      <router-link
        to="/api-settings"
        class="flex w-full items-center gap-4 rounded-2xl px-4 py-3 font-medium transition-all duration-300"
        :class="
          isApiPage
            ? 'bg-primary text-on-primary shadow-sm'
            : 'text-on-surface-variant hover:bg-surface-container-highest'
        "
      >
        <span class="material-symbols-outlined">vpn_key</span>
        <span>API Keys</span>
      </router-link>

      <button
        class="flex w-full items-center gap-4 rounded-2xl px-4 py-3 text-error/70 transition-all duration-300 hover:bg-error-container/20 hover:text-error"
        @click="$emit('logout')"
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
