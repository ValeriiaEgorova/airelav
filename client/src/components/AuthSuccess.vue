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
  <div class="flex min-h-screen items-center justify-center">
    <div class="text-center">
      <div
        class="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-primary"
      ></div>
      <p class="mt-4 font-medium text-gray-600">
        Authenticating with GitHub...
      </p>
    </div>
  </div>
</template>
