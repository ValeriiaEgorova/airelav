<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const isRegistering = ref(false);

const API_URL = 'http://127.0.0.1:8000';

const handleSubmit = async () => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email.value);
    formData.append('password', password.value);

    if (isRegistering.value) {
      await axios.post(`${API_URL}/auth/register`, null, {
        params: { email: email.value, password: password.value },
      });
      alert('Registration successful! Logging in...');
    }

    const response = await axios.post(`${API_URL}/token`, formData);

    localStorage.setItem('token', response.data.access_token);

    router.push('/');
  } catch (error) {
    alert(error.response?.data?.detail || 'Authentication failed');
  }
};
</script>

<template>
  <div
    class="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-50 px-4"
  >
    <div
      class="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50"
    ></div>

    <div
      class="animate-fade-in relative w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-xl"
    >
      <div class="mb-6 flex items-center justify-center space-x-3">
        <div
          class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600"
        >
          <i class="fas fa-cube text-white"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">SynthGen AI</span>
      </div>

      <h1 class="mb-2 text-center text-2xl font-bold text-gray-900">
        {{ isRegistering ? 'Create Account' : 'Welcome back' }}
      </h1>
      <p class="mb-8 text-center text-gray-600">
        {{
          isRegistering
            ? 'Join to start generating data'
            : 'Sign in to generate synthetic datasets'
        }}
      </p>

      <form class="space-y-5" @submit.prevent="handleSubmit">
        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700"
            >Email</label
          >
          <div class="relative">
            <i
              class="fas fa-envelope absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400"
            ></i>
            <input
              v-model="email"
              type="email"
              placeholder="you@example.com"
              class="w-full rounded-lg border border-gray-200 py-3 pl-10 pr-4 outline-none transition-all focus:border-transparent focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700"
            >Password</label
          >
          <div class="relative">
            <i
              class="fas fa-lock absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400"
            ></i>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="w-full rounded-lg border border-gray-200 py-3 pl-10 pr-4 outline-none transition-all focus:border-transparent focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          class="flex w-full transform items-center justify-center space-x-2 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 py-3 font-semibold text-white shadow-lg shadow-blue-500/30 transition-all hover:scale-[1.02] hover:from-blue-600 hover:to-blue-700"
        >
          <i class="fas fa-right-to-bracket"></i>
          <span>{{ isRegistering ? 'Sign Up' : 'Sign In' }}</span>
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-600">
        {{
          isRegistering ? 'Already have an account?' : 'Don’t have an account?'
        }}
        <button
          class="ml-1 font-medium text-blue-600 hover:text-blue-700"
          @click="isRegistering = !isRegistering"
        >
          {{ isRegistering ? 'Sign in' : 'Sign up' }}
        </button>
      </p>
    </div>
  </div>
</template>

<style>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
