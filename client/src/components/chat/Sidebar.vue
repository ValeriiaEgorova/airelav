<!-- Sidebar.vue -->
<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps({
  history: { type: Array, default: () => [] },
  currentTaskId: { type: Number, default: null },
  userEmail: { type: String, default: 'User' },
});

const emit = defineEmits(['select', 'delete', 'new', 'logout']);
const route = useRoute();
const router = useRouter();

const userInitial = computed(() =>
  props.userEmail ? props.userEmail[0].toUpperCase() : 'U'
);

// Проверяем, находимся ли мы на странице настроек API
const isApiPage = computed(() => route.path === '/api-settings');
</script>

<template>
  <aside
    class="flex w-72 flex-col border-r border-slate-800 bg-slate-900 text-slate-300"
  >
    <!-- Logo -->
    <div
      class="flex h-16 cursor-pointer items-center border-b border-slate-800 px-6"
      @click="router.push('/')"
    >
      <div
        class="mr-3 flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow"
      >
        <i class="fas fa-cube text-sm text-white"></i>
      </div>
      <span class="font-semibold text-white">AIrelav</span>
    </div>

    <!-- === РЕЖИМ 1: ЧАТ (Показываем историю) === -->
    <div v-if="!isApiPage" class="flex h-full flex-col overflow-hidden">
      <div class="p-4">
        <button
          class="flex w-full items-center justify-between rounded-xl bg-slate-800 px-4 py-3 text-sm font-medium shadow transition hover:bg-slate-700"
          @click="$emit('new')"
        >
          <span class="flex items-center gap-2"
            ><i class="fas fa-plus"></i> Новый чат</span
          >
        </button>
      </div>

      <div class="custom-scrollbar flex-1 space-y-1 overflow-y-auto px-3">
        <div class="px-3 py-2 text-xs uppercase tracking-wider text-slate-500">
          История
        </div>
        <div
          v-for="item in history"
          :key="item.id"
          class="group flex cursor-pointer items-center gap-3 rounded-xl p-3 transition"
          :class="
            item.id === currentTaskId
              ? 'bg-slate-800 text-white shadow'
              : 'text-slate-400 hover:bg-slate-800'
          "
          @click="$emit('select', item)"
        >
          <i
            class="far fa-comment-alt"
            :class="
              item.id === currentTaskId ? 'text-blue-400' : 'text-slate-500'
            "
          ></i>
          <span class="flex-1 truncate text-sm">{{ item.title }}</span>
          <button
            class="text-slate-500 opacity-0 transition hover:text-red-400 group-hover:opacity-100"
            @click.stop="$emit('delete', item.id)"
          >
            <i class="fas fa-trash-alt"></i>
          </button>
        </div>
      </div>

      <!-- Кнопка перехода в API (внизу) -->
      <div class="px-3 pb-2">
        <button
          class="flex w-full items-center gap-3 rounded-xl p-3 text-slate-400 transition hover:bg-slate-800 hover:text-white"
          @click="router.push('/api-settings')"
        >
          <i class="fas fa-code"></i>
          <span class="text-sm">API & Developers</span>
        </button>
      </div>
    </div>

    <!-- === РЕЖИМ 2: МЕНЮ (Показываем навигацию как в твоем дизайне) === -->
    <div v-else class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
      <button
        class="group flex w-full items-center gap-3 rounded-xl p-3 text-slate-400 transition hover:bg-slate-800 hover:text-white"
        @click="router.push('/')"
      >
        <i class="fas fa-wand-magic-sparkles w-5 text-center"></i>
        <span class="text-sm font-medium">Генератор</span>
      </button>

      <div
        class="px-3 pb-2 pt-4 text-xs font-semibold uppercase tracking-wider text-slate-500"
      >
        Разработчикам
      </div>

      <button
        class="group flex w-full items-center gap-3 rounded-xl bg-slate-800 p-3 text-white shadow"
      >
        <i class="fas fa-key w-5 text-center text-blue-500"></i>
        <span class="text-sm font-medium">API Ключи</span>
      </button>

      <!-- Заглушка -->
      <button
        class="group flex w-full items-center gap-3 rounded-xl p-3 text-slate-400 transition hover:bg-slate-800 hover:text-white"
      >
        <i class="fas fa-book w-5 text-center"></i>
        <span class="text-sm font-medium">Документация</span>
      </button>
    </div>

    <!-- Профиль -->
    <div class="border-t border-slate-800 p-4">
      <div
        class="flex items-center gap-3 rounded-xl p-2 transition hover:bg-slate-800"
      >
        <div
          class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-purple-400 to-pink-500 text-xs font-bold text-white"
        >
          {{ userInitial }}
        </div>
        <div class="flex-1 overflow-hidden">
          <p class="truncate text-sm text-white">{{ userEmail }}</p>
          <p class="text-xs text-slate-500">Pro Plan</p>
        </div>
        <button
          class="text-slate-400 hover:text-white"
          @click="$emit('logout')"
        >
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </div>
  </aside>
</template>
