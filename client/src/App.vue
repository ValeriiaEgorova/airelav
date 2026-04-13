<script setup>
import { RouterView } from 'vue-router';
</script>

<template>
  <!-- Убираем Suspense, оставляем только окно роутера -->
  <RouterView />
</template>
