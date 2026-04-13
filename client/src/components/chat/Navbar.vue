<script setup>
// Импортируем RouterLink, чтобы использовать его вместо обычных кнопок для навигации
import { RouterLink } from 'vue-router';

defineProps({
  userEmail: {
    type: String,
    default: 'User'
  },
  selectedModel: {
    type: String,
    required: true
  },
  // Добавим проп для тарифа, чтобы бейдж не был всегда "Pro"
  userTier: {
    type: String,
    default: 'free'
  }
});

defineEmits(['update:model']);
</script>

<template>
  <nav class="fixed top-0 left-0 right-0 w-full z-50 bg-[#fcf9f2]/80 border-b border-outline-variant/20 flex justify-between items-center px-8 h-20 bg-gradient-to-b from-[#f6f3ec] to-transparent">
    <div class="flex items-center gap-8 h-full">
      
      <!-- Логотип (теперь кликабельный, ведет на главную) -->
      <RouterLink to="/" class="flex items-center gap-4 py-2 select-none hover:opacity-90 transition-opacity">
        <div class="relative shrink-0 group">
          <div class="w-12 h-12 bg-gradient-to-tr from-[#6b3500] to-[#ff9238] rounded-xl flex items-center justify-center rotate-3 shadow-lg group-hover:rotate-6 transition-all duration-300">
            <span class="material-symbols-outlined text-white text-[28px]">hub</span>
          </div>
          <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center shadow-sm">
            <div class="w-2.5 h-2.5 bg-[#ff9238] rounded-full animate-pulse"></div>
          </div>
        </div>

        <div class="flex flex-col justify-center text-left">
          <h1 class="text-[26px] font-bold tracking-tighter text-[#1c1c18] leading-none mb-1">Airelav</h1>
          <span class="text-[10px] font-semibold tracking-[0.15em] text-[#944a00]/70 uppercase">Data Studio</span>
        </div>
      </RouterLink>

      <div class="hidden md:flex gap-6 items-center h-full">
        <a href="https://github.com/ValeriiaEgorova/airelav" target="_blank" rel="noopener noreferrer" class="text-[#944a00] font-bold font-headline tracking-tight hover:opacity-80 transition-opacity">
          GitHub
        </a>
      </div>
    </div>

    <div class="flex items-center gap-6">
      
      <!-- Переключатель моделей -->
      <div class="hidden lg:flex items-center gap-1 bg-surface-container-high/50 rounded-full p-1 border border-outline-variant/10">
        <button 
          @click="$emit('update:model', 'gemini-2.5-flash')"
          class="h-9 min-w-[90px] px-4 flex items-center justify-center rounded-full text-[11px] font-bold uppercase tracking-wider transition-all"
          :class="selectedModel === 'gemini-2.5-flash' 
            ? 'bg-white text-primary shadow-sm' 
            : 'text-on-surface-variant hover:text-on-surface'"
        >
          Flash 2.5
        </button>
        <button 
          @click="$emit('update:model', 'gemini-2.5-flash-lite')"
          class="h-9 min-w-[90px] px-4 flex items-center justify-center rounded-full text-[11px] font-bold uppercase tracking-wider transition-all"
          :class="selectedModel === 'gemini-2.5-flash-lite' 
            ? 'bg-white text-primary shadow-sm' 
            : 'text-on-surface-variant hover:text-on-surface'"
        >
          Flash Lite
        </button>
      </div>

      <div class="hidden lg:block w-px h-8 bg-outline-variant/20"></div>

      <!-- Профиль пользователя (теперь ведет на /profile) -->
      <RouterLink 
        to="/profile" 
        class="group flex items-center gap-3 p-1 pr-3 rounded-full hover:bg-surface-container-high/60 transition-all duration-300 border border-transparent hover:border-outline-variant/10"
      >
        <div class="relative">
          <div class="w-10 h-10 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold font-headline ring-2 ring-white shadow-sm">
            {{ userEmail ? userEmail.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white rounded-full"></div>
        </div>

        <div class="text-left hidden sm:block">
          <div class="flex items-center gap-1.5">
            <p class="text-sm font-bold text-[#1c1c18] leading-none group-hover:text-primary transition-colors">
              {{ userEmail.split('@')[0] }}
            </p>
            <span class="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:text-primary transition-colors">person</span>
          </div>
          <!-- Динамический бейдж тарифа -->
          <span class="inline-flex mt-1 px-2 py-0.5 rounded-md text-[9px] font-bold bg-primary/10 text-primary uppercase tracking-[0.05em]">
            {{ userTier }} Plan
          </span>
        </div>
      </RouterLink>

    </div>
  </nav>
</template>