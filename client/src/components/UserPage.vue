<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useToast } from "vue-toastification";

const toast = useToast();
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const user = ref(null);
const loading = ref(true);

const fetchProfile = async () => {
  try {
    const res = await axios.get(`${API_URL}/auth/me`);
    user.value = res.data;
  } catch (e) {
    toast.error("Failed to load profile");
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'Oct 12, 2023'; // Заглушка
  return new Date(dateStr).toLocaleDateString('en-US', {
    day: 'numeric', month: 'long', year: 'numeric'
  });
};

onMounted(fetchProfile);
</script>

<template>
  <div class="pt-8 px-8 pb-12 w-full overflow-y-auto h-screen custom-scrollbar bg-background">
    <div v-if="!loading && user" class="max-w-5xl mx-auto">
      
      <!-- Приветствие -->
      <div class="mb-10">
        <h1 class="text-4xl font-headline font-extrabold text-on-background tracking-tight">Account Settings</h1>
        <p class="text-on-surface-variant mt-2">Manage your profile, subscription, and usage limits.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Левая колонка: Инфо о пользователе -->
        <div class="lg:col-span-2 space-y-8">
          
          <!-- Карточка профиля -->
          <div class="bg-surface-container-low rounded-3xl p-8 border border-outline-variant/5">
            <div class="flex items-center gap-6 mb-8">
                <div class="w-20 h-20 rounded-full bg-blue-600 flex items-center justify-center text-white text-3xl font-bold">
                    {{ user.email[0].toUpperCase() }}
                </div>
                <div>
                    <h2 class="text-2xl font-bold text-on-surface">{{ user.email }}</h2>
                     <p class="text-on-surface-variant">User ID: #{{ user.id }}</p>
                    <span class="inline-block mt-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-700">
                    {{ user.tier }} plan
                    </span>
                </div>
                </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/10 text-center">
                <p class="text-xs font-bold text-on-surface-variant/50 uppercase">Datasets</p>
                <p class="text-2xl font-black mt-1">{{ user.stats.total_datasets }}</p>
              </div>
              <div class="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/10 text-center">
                <p class="text-xs font-bold text-on-surface-variant/50 uppercase">Total Rows</p>
                <p class="text-2xl font-black mt-1">{{ user.stats.total_rows.toLocaleString() }}</p>
              </div>
              <div class="p-4 rounded-2xl bg-surface-container-lowest border border-outline-variant/10 text-center">
                <p class="text-xs font-bold text-on-surface-variant/50 uppercase">API Keys</p>
                <p class="text-2xl font-black mt-1">{{ user.stats.active_keys }}</p>
              </div>
            </div>
          </div>

          <!-- Быстрые действия -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <router-link to="/api-settings" class="p-6 rounded-3xl bg-surface-container-low border border-outline-variant/5 hover:bg-surface-container-high transition-colors group">
              <span class="material-symbols-outlined text-blue-600 mb-4 text-3xl">vpn_key</span>
              <h3 class="font-bold text-lg flex items-center justify-between">
                API Management
                <span class="material-symbols-outlined opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0">arrow_forward</span>
              </h3>
              <p class="text-sm text-on-surface-variant mt-1">Generate and revoke your developer keys.</p>
            </router-link>

            <button @click="toast.info('Coming soon!')" class="p-6 rounded-3xl bg-surface-container-low border border-outline-variant/5 hover:bg-surface-container-high transition-colors text-left group">
              <span class="material-symbols-outlined text-purple-600 mb-4 text-3xl">lock_reset</span>
              <h3 class="font-bold text-lg flex items-center justify-between">
                Security
                <span class="material-symbols-outlined opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0">arrow_forward</span>
              </h3>
              <p class="text-sm text-on-surface-variant mt-1">Update your password and 2FA settings.</p>
            </button>
          </div>
        </div>

        <!-- Правая колонка: Информация о тарифе -->
        <div class="space-y-8">
          <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-8 text-white relative overflow-hidden shadow-xl">
            <div class="relative z-10">
              <h3 class="text-xs font-bold uppercase tracking-widest opacity-60 mb-2">Current Plan</h3>
              <h2 class="text-4xl font-black mb-6 uppercase">{{ user.tier }}</h2>
              
              <ul class="space-y-4 mb-8 text-sm opacity-80 font-medium">
                <li class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-green-400 text-sm">check_circle</span>
                  {{ user.tier === 'free' ? '10 generations / day' : 'Unlimited generations' }}
                </li>
                <li class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-green-400 text-sm">check_circle</span>
                  Up to 10 active API keys
                </li>
                <li class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-green-400 text-sm">check_circle</span>
                  {{ user.tier === 'free' ? '1 day file storage' : '30 days file storage' }}
                </li>
              </ul>

              <button v-if="user.tier === 'free'" @click="toast.info('Billing is not connected')" class="w-full py-3 rounded-2xl bg-white text-gray-900 font-bold hover:bg-gray-100 transition-all active:scale-95">
                Upgrade to Pro
              </button>
            </div>
            <!-- Декор -->
            <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl"></div>
          </div>

          <div class="p-6 rounded-3xl bg-amber-50 border border-amber-100">
            <div class="flex items-start gap-4">
              <span class="material-symbols-outlined text-amber-600">info</span>
              <div>
                <p class="text-sm font-bold text-amber-900">Important Note</p>
                <p class="text-xs text-amber-800 mt-1 leading-relaxed">
                  Generated files are automatically deleted after their expiration date to free up server resources.
                </p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Skeleton Loader -->
    <div v-else class="max-w-5xl mx-auto animate-pulse">
      <div class="h-10 w-64 bg-gray-200 rounded-lg mb-10"></div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 h-96 bg-gray-200 rounded-3xl"></div>
        <div class="h-96 bg-gray-200 rounded-3xl"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-headline { font-family: 'Manrope', sans-serif; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.05); border-radius: 10px; }
</style>