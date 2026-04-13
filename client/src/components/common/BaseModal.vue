<script setup>
defineProps(['show', 'title', 'description', 'confirmText', 'isDestructive']);
defineEmits(['close', 'confirm']);
</script>

<template>
  <Transition name="fade">
    <!-- Убраны звездочки и знаки решетки. Добавлен z-[9999] -->
    <div 
      v-if="show" 
      class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full overflow-hidden animate-pop">
        <div class="p-6">
          <h3 class="text-xl font-bold text-gray-900 mb-2">{{ title }}</h3>
          <p class="text-gray-600 mb-6">{{ description }}</p>
          
          <slot></slot>

          <div class="flex space-x-3">
            <button 
              @click="$emit('close')" 
              class="flex-1 px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-bold transition-all active:scale-95"
            >
              Cancel
            </button>

            <button 
              @click="$emit('confirm')" 
              :class="[
                'flex-1 px-4 py-3 text-white rounded-xl font-bold transition-all active:scale-95 shadow-md',
                isDestructive 
                  ? 'bg-red-500 hover:bg-red-600 shadow-red-200' 
                  : 'bg-blue-600 hover:bg-blue-700 shadow-blue-200'
              ]"
            >
              {{ confirmText || 'Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.animate-pop { animation: pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
@keyframes pop { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>