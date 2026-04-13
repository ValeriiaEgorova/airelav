<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { useToast } from "vue-toastification";

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
    toast.error("Invalid or missing reset token");
    router.push('/login');
  }
});

const handleReset = async () => {
  if (newPassword.value !== confirmPassword.value) {
    toast.error("Passwords do not match!");
    return;
  }
  if (newPassword.value.length < 6) {
    toast.warning("Password must be at least 6 characters");
    return;
  }

  isSubmitting.value = true;
  try {
    await axios.post(`${API_URL}/auth/reset-password`, {
      token: token.value,
      new_password: newPassword.value
    });
    
    toast.success("Password successfully updated! Please log in.");
    router.push('/login');
  } catch (error) {
    const msg = error.response?.data?.detail || "Failed to reset password";
    toast.error(msg);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="material-symbols-outlined text-3xl">lock_reset</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Create New Password</h2>
        <p class="text-gray-500 mt-2 text-sm">Please enter your new password below.</p>
      </div>

      <form @submit.prevent="handleReset" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
          <input 
            v-model="newPassword" 
            type="password" 
            required
            class="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="••••••••"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
          <input 
            v-model="confirmPassword" 
            type="password" 
            required
            class="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="••••••••"
          />
        </div>

        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors disabled:opacity-70 mt-6"
        >
          {{ isSubmitting ? 'Updating...' : 'Update Password' }}
        </button>
      </form>
    </div>
  </div>
</template>
