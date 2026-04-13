<script setup>
// Импортируем RouterLink, чтобы использовать его вместо обычных кнопок для навигации
import { RouterLink } from 'vue-router';

defineProps({
  userEmail: {
    type: String,
    default: 'User',
  },
  selectedModel: {
    type: String,
    required: true,
  },
  // Добавим проп для тарифа, чтобы бейдж не был всегда "Pro"
  userTier: {
    type: String,
    default: 'free',
  },
});

defineEmits(['update:model']);
</script>

<template>
  <nav
    class="fixed left-0 right-0 top-0 z-50 flex h-20 w-full items-center justify-between border-b border-outline-variant/20 bg-[#fcf9f2]/80 bg-gradient-to-b from-[#f6f3ec] to-transparent px-8"
  >
    <div class="flex h-full items-center gap-8">
      <!-- Логотип (теперь кликабельный, ведет на главную) -->
      <RouterLink
        to="/"
        class="flex select-none items-center gap-4 py-2 transition-opacity hover:opacity-90"
      >
        <div class="group relative shrink-0">
          <div
            class="flex h-12 w-12 rotate-3 items-center justify-center rounded-xl bg-gradient-to-tr from-[#6b3500] to-[#ff9238] shadow-lg transition-all duration-300 group-hover:rotate-6"
          >
            <span class="material-symbols-outlined text-[28px] text-white"
              >hub</span
            >
          </div>
          <div
            class="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-white shadow-sm"
          >
            <div
              class="h-2.5 w-2.5 animate-pulse rounded-full bg-[#ff9238]"
            ></div>
          </div>
        </div>

        <div class="flex flex-col justify-center text-left">
          <h1
            class="mb-1 text-[26px] font-bold leading-none tracking-tighter text-[#1c1c18]"
          >
            Airelav
          </h1>
          <span
            class="text-[10px] font-semibold uppercase tracking-[0.15em] text-[#944a00]/70"
            >Data Studio</span
          >
        </div>
      </RouterLink>

      <div class="hidden h-full items-center gap-6 md:flex">
        <a
          href="https://github.com/ValeriiaEgorova/airelav"
          target="_blank"
          rel="noopener noreferrer"
          class="font-headline font-bold tracking-tight text-[#944a00] transition-opacity hover:opacity-80"
        >
          GitHub
        </a>
      </div>
    </div>

    <div class="flex items-center gap-6">
      <!-- Переключатель моделей -->
      <div
        class="hidden items-center gap-1 rounded-full border border-outline-variant/10 bg-surface-container-high/50 p-1 lg:flex"
      >
        <button
          class="flex h-9 min-w-[90px] items-center justify-center rounded-full px-4 text-[11px] font-bold uppercase tracking-wider transition-all"
          :class="
            selectedModel === 'gemini-2.5-flash'
              ? 'bg-white text-primary shadow-sm'
              : 'text-on-surface-variant hover:text-on-surface'
          "
          @click="$emit('update:model', 'gemini-2.5-flash')"
        >
          Flash 2.5
        </button>
        <button
          class="flex h-9 min-w-[90px] items-center justify-center rounded-full px-4 text-[11px] font-bold uppercase tracking-wider transition-all"
          :class="
            selectedModel === 'gemini-2.5-flash-lite'
              ? 'bg-white text-primary shadow-sm'
              : 'text-on-surface-variant hover:text-on-surface'
          "
          @click="$emit('update:model', 'gemini-2.5-flash-lite')"
        >
          Flash Lite
        </button>
      </div>

      <div class="hidden h-8 w-px bg-outline-variant/20 lg:block"></div>

      <!-- Профиль пользователя (теперь ведет на /profile) -->
      <RouterLink
        to="/profile"
        class="group flex items-center gap-3 rounded-full border border-transparent p-1 pr-3 transition-all duration-300 hover:border-outline-variant/10 hover:bg-surface-container-high/60"
      >
        <div class="relative">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20 font-headline font-bold text-primary shadow-sm ring-2 ring-white"
          >
            {{ userEmail ? userEmail.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div
            class="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-white bg-green-500"
          ></div>
        </div>

        <div class="hidden text-left sm:block">
          <div class="flex items-center gap-1.5">
            <p
              class="text-sm font-bold leading-none text-[#1c1c18] transition-colors group-hover:text-primary"
            >
              {{ userEmail.split('@')[0] }}
            </p>
            <span
              class="material-symbols-outlined text-[16px] text-on-surface-variant transition-colors group-hover:text-primary"
              >person</span
            >
          </div>
          <!-- Динамический бейдж тарифа -->
          <span
            class="mt-1 inline-flex rounded-md bg-primary/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-[0.05em] text-primary"
          >
            {{ userTier }} Plan
          </span>
        </div>
      </RouterLink>
    </div>
  </nav>
</template>
