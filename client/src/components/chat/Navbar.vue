<script setup>
defineProps({
  userEmail: {
    type: String,
    default: 'User'
  },
  selectedModel: {
    type: String,
    required: true
  }
});

defineEmits(['update:model']);
</script>

<template>
  <!-- ВАЖНО: Добавил w-full вместо w-screen, чтобы не было горизонтального скролла -->
  <nav class="fixed top-0 left-0 right-0 w-full z-50 bg-[#fcf9f2]/80 backdrop-blur-xl border-b border-outline-variant/20 flex justify-between items-center px-8 h-20 bg-gradient-to-b from-[#f6f3ec] to-transparent">
    <div class="flex items-center gap-8 h-full">
      
      <div class="flex items-center gap-4 py-2 select-none">
        <div class="relative shrink-0 group">
          <div class="w-12 h-12 bg-gradient-to-tr from-[#6b3500] to-[#ff9238] rounded-xl flex items-center justify-center rotate-3 shadow-lg group-hover:rotate-6 transition-all duration-300">
            <span class="material-symbols-outlined text-white text-[28px]">hub</span>
          </div>
          <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center shadow-sm">
            <div class="w-2.5 h-2.5 bg-[#ff9238] rounded-full animate-pulse"></div>
          </div>
        </div>

        <div class="flex flex-col justify-center">
          <!-- ИСПРАВЛЕНО: Уменьшил жирность шрифта с font-extrabold на font-bold -->
          <h1 class="text-[26px] font-bold tracking-tighter text-[#1c1c18] leading-none mb-1">Airelav</h1>
          <!-- ИСПРАВЛЕНО: Уменьшил жирность шрифта с font-black на font-semibold -->
          <span class="text-[10px] font-semibold tracking-[0.15em] text-[#944a00]/70 uppercase">Data Studio</span>
        </div>
      </div>

      <div class="hidden md:flex gap-6 items-center h-full">
        <a href="https://github.com" target="_blank" rel="noopener noreferrer" class="text-[#944a00] font-bold font-headline tracking-tight hover:opacity-80 transition-opacity">
          GitHub
        </a>
      </div>
    </div>

    <div class="flex items-center gap-6">
      
      <!-- Модели -->
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

      <!-- Профиль пользователя -->
      <button class="group flex items-center gap-3 p-1 pr-3 rounded-full hover:bg-surface-container-high/60 transition-all duration-300">
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
            <span class="material-symbols-outlined text-[16px] text-on-surface-variant group-hover:rotate-180 transition-transform duration-300">expand_more</span>
          </div>
          <span class="inline-flex mt-1 px-2 py-0.5 rounded-md text-[9px] font-bold bg-primary/10 text-primary uppercase tracking-[0.05em]">
            Pro Plan
          </span>
        </div>
      </button>

    </div>
  </nav>
</template>