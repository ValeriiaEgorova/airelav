<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const router = useRouter();
const route = useRoute();
const toast = useToast();

const newPassword = ref('');
const confirmPassword = ref('');
const token = ref('');
const isSubmitting = ref(false);

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

onMounted(() => {
  // Получаем токен из URL (например: /reset-password?token=eyJ...)
  token.value = route.query.token;
  if (!token.value) {
    toast.error('Invalid or missing reset token');
    router.push('/login');
  }
});

const handleReset = async () => {
  if (newPassword.value !== confirmPassword.value) {
    toast.error('Passwords do not match!');
    return;
  }
  if (newPassword.value.length < 6) {
    toast.warning('Password must be at least 6 characters');
    return;
  }

  isSubmitting.value = true;
  try {
    await axios.post(`${API_URL}/auth/reset-password`, {
      token: token.value,
      new_password: newPassword.value,
    });

    toast.success('Password successfully updated! Please log in.');
    router.push('/login');
  } catch (error) {
    const msg = error.response?.data?.detail || 'Failed to reset password';
    toast.error(msg);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 px-4">
    <div
      class="w-full max-w-md rounded-2xl border border-gray-100 bg-white p-8 shadow-xl"
    >
      <div class="mb-8 text-center">
        <div
          class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 text-blue-600"
        >
          <span class="material-symbols-outlined text-3xl">lock_reset</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Create New Password</h2>
        <p class="mt-2 text-sm text-gray-500">
          Please enter your new password below.
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleReset">
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700"
            >New Password</label
          >
          <input
            v-model="newPassword"
            type="password"
            required
            class="w-full rounded-xl border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700"
            >Confirm Password</label
          >
          <input
            v-model="confirmPassword"
            type="password"
            required
            class="w-full rounded-xl border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          :disabled="isSubmitting"
          class="mt-6 w-full rounded-xl bg-blue-600 py-3 font-bold text-white transition-colors hover:bg-blue-700 disabled:opacity-70"
        >
          {{ isSubmitting ? 'Updating...' : 'Update Password' }}
        </button>
      </form>
    </div>
  </div>
</template>
