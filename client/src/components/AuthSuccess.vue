<script setup>
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { chatStore } from '../chatStore';

const router = useRouter();
const route = useRoute();

onMounted(async () => {
  const token = route.query.token;
  if (token) {
    localStorage.setItem('token', token);
    await chatStore.fetchUser(); // Загружаем данные профиля
    router.push('/'); // Идем в чат
  } else {
    router.push('/login');
  }
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
      <p class="mt-4 text-gray-600 font-medium">Authenticating with GitHub...</p>
    </div>
  </div>
</template>