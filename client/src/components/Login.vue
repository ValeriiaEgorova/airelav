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
        params: { email: email.value, password: password.value }
      });
      alert("Registration successful! Logging in...");
    }

    const response = await axios.post(`${API_URL}/token`, formData);
    
    localStorage.setItem('token', response.data.access_token);
    
    router.push('/');
    
  } catch (error) {
    alert(error.response?.data?.detail || "Authentication failed");
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 relative overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50"></div>

    <div class="relative w-full max-w-md bg-white border border-gray-200 rounded-2xl shadow-xl p-8 animate-fade-in">
      
      <div class="flex items-center justify-center mb-6 space-x-3">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <i class="fas fa-cube text-white"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">SynthGen AI</span>
      </div>

      <h1 class="text-2xl font-bold text-center text-gray-900 mb-2">
        {{ isRegistering ? 'Create Account' : 'Welcome back' }}
      </h1>
      <p class="text-center text-gray-600 mb-8">
        {{ isRegistering ? 'Join to start generating data' : 'Sign in to generate synthetic datasets' }}
      </p>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <div class="relative">
            <i class="fas fa-envelope absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
            <input v-model="email" type="email" placeholder="you@example.com" class="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all" required />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <div class="relative">
            <i class="fas fa-lock absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
            <input v-model="password" type="password" placeholder="••••••••" class="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all" required />
          </div>
        </div>

        <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 rounded-xl font-semibold hover:from-blue-600 hover:to-blue-700 transition-all transform hover:scale-[1.02] flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/30">
          <i class="fas fa-right-to-bracket"></i>
          <span>{{ isRegistering ? 'Sign Up' : 'Sign In' }}</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        {{ isRegistering ? 'Already have an account?' : 'Don’t have an account?' }}
        <button @click="isRegistering = !isRegistering" class="text-blue-600 hover:text-blue-700 font-medium ml-1">
          {{ isRegistering ? 'Sign in' : 'Sign up' }}
        </button>
      </p>

    </div>
  </div>
</template>

<style>
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>