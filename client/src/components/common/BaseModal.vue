<script setup>
defineProps(['show', 'title', 'description', 'confirmText', 'isDestructive']);
defineEmits(['close', 'confirm']);
</script>

<template>
  <Transition name="fade">
    <!-- Убраны звездочки и знаки решетки. Добавлен z-[9999] -->
    <div
      v-if="show"
      class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div
        class="animate-pop w-full max-w-sm overflow-hidden rounded-2xl bg-white shadow-2xl"
      >
        <div class="p-6">
          <h3 class="mb-2 text-xl font-bold text-gray-900">{{ title }}</h3>
          <p class="mb-6 text-gray-600">{{ description }}</p>

          <slot></slot>

          <div class="flex space-x-3">
            <button
              class="flex-1 rounded-xl bg-gray-100 px-4 py-3 font-bold text-gray-700 transition-all hover:bg-gray-200 active:scale-95"
              @click="$emit('close')"
            >
              Cancel
            </button>

            <button
              :class="[
                'flex-1 rounded-xl px-4 py-3 font-bold text-white shadow-md transition-all active:scale-95',
                isDestructive
                  ? 'bg-red-500 shadow-red-200 hover:bg-red-600'
                  : 'bg-blue-600 shadow-blue-200 hover:bg-blue-700',
              ]"
              @click="$emit('confirm')"
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.animate-pop {
  animation: pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes pop {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
