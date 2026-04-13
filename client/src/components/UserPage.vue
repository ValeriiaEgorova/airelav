<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';

const toast = useToast();
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const user = ref(null);
const loading = ref(true);

const fetchProfile = async () => {
  try {
    const res = await axios.get(`${API_URL}/auth/me`);
    user.value = res.data;
  } catch (e) {
    toast.error('Failed to load profile');
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'Oct 12, 2023'; // Заглушка
  return new Date(dateStr).toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
};

onMounted(fetchProfile);
</script>

<template>
  <div
    class="custom-scrollbar h-screen w-full overflow-y-auto bg-background px-8 pb-12 pt-8"
  >
    <div v-if="!loading && user" class="mx-auto max-w-5xl">
      <!-- Приветствие -->
      <div class="mb-10">
        <h1
          class="font-headline text-4xl font-extrabold tracking-tight text-on-background"
        >
          Account Settings
        </h1>
        <p class="mt-2 text-on-surface-variant">
          Manage your profile, subscription, and usage limits.
        </p>
      </div>

      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <!-- Левая колонка: Инфо о пользователе -->
        <div class="space-y-8 lg:col-span-2">
          <!-- Карточка профиля -->
          <div
            class="rounded-3xl border border-outline-variant/5 bg-surface-container-low p-8"
          >
            <div class="mb-8 flex items-center gap-6">
              <div
                class="flex h-20 w-20 items-center justify-center rounded-full bg-blue-600 text-3xl font-bold text-white"
              >
                {{ user.email[0].toUpperCase() }}
              </div>
              <div>
                <h2 class="text-2xl font-bold text-on-surface">
                  {{ user.email }}
                </h2>
                <p class="text-on-surface-variant">User ID: #{{ user.id }}</p>
                <span
                  class="mt-2 inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-blue-700"
                >
                  {{ user.tier }} plan
                </span>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div
                class="rounded-2xl border border-outline-variant/10 bg-surface-container-lowest p-4 text-center"
              >
                <p
                  class="text-xs font-bold uppercase text-on-surface-variant/50"
                >
                  Datasets
                </p>
                <p class="mt-1 text-2xl font-black">
                  {{ user.stats.total_datasets }}
                </p>
              </div>
              <div
                class="rounded-2xl border border-outline-variant/10 bg-surface-container-lowest p-4 text-center"
              >
                <p
                  class="text-xs font-bold uppercase text-on-surface-variant/50"
                >
                  Total Rows
                </p>
                <p class="mt-1 text-2xl font-black">
                  {{ user.stats.total_rows.toLocaleString() }}
                </p>
              </div>
              <div
                class="rounded-2xl border border-outline-variant/10 bg-surface-container-lowest p-4 text-center"
              >
                <p
                  class="text-xs font-bold uppercase text-on-surface-variant/50"
                >
                  API Keys
                </p>
                <p class="mt-1 text-2xl font-black">
                  {{ user.stats.active_keys }}
                </p>
              </div>
            </div>
          </div>

          <!-- Быстрые действия -->
          <!-- Быстрые действия -->
          <div class="space-y-4">
            <router-link
              to="/api-settings"
              class="group flex items-center justify-between rounded-3xl border border-outline-variant/5 bg-surface-container-low p-6 transition-all hover:bg-surface-container-high"
            >
              <div class="flex items-center gap-6">
                <div
                  class="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600/10 text-blue-600"
                >
                  <span class="material-symbols-outlined text-2xl"
                    >vpn_key</span
                  >
                </div>
                <div>
                  <h3 class="text-lg font-bold text-on-surface">
                    API Management
                  </h3>
                  <p class="text-sm text-on-surface-variant">
                    Generate and revoke your developer keys for REST API access.
                  </p>
                </div>
              </div>
              <span
                class="material-symbols-outlined translate-x-[-10px] text-on-surface-variant opacity-0 transition-all group-hover:translate-x-0 group-hover:opacity-100"
              >
                arrow_forward
              </span>
            </router-link>
          </div>
        </div>

        <!-- Правая колонка: Информация о тарифе -->
        <div class="space-y-8">
          <div
            class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-gray-900 to-gray-800 p-8 text-white shadow-xl"
          >
            <div class="relative z-10">
              <h3
                class="mb-2 text-xs font-bold uppercase tracking-widest opacity-60"
              >
                Current Plan
              </h3>
              <h2 class="mb-6 text-4xl font-black uppercase">
                {{ user.tier }}
              </h2>

              <ul class="mb-8 space-y-4 text-sm font-medium opacity-80">
                <li class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-sm text-green-400"
                    >check_circle</span
                  >
                  {{
                    user.tier === 'free'
                      ? '10 generations / day'
                      : 'Unlimited generations'
                  }}
                </li>
                <li class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-sm text-green-400"
                    >check_circle</span
                  >
                  Up to 10 active API keys
                </li>
                <li class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-sm text-green-400"
                    >check_circle</span
                  >
                  {{
                    user.tier === 'free'
                      ? '1 day file storage'
                      : '30 days file storage'
                  }}
                </li>
              </ul>

              <button
                v-if="user.tier === 'free'"
                class="w-full rounded-2xl bg-white py-3 font-bold text-gray-900 transition-all hover:bg-gray-100 active:scale-95"
                @click="toast.info('Billing is not connected')"
              >
                Upgrade to Pro
              </button>
            </div>
            <!-- Декор -->
            <div
              class="absolute -bottom-10 -right-10 h-40 w-40 rounded-full bg-blue-500/20 blur-3xl"
            ></div>
          </div>

          <div class="rounded-3xl border border-amber-100 bg-amber-50 p-6">
            <div class="flex items-start gap-4">
              <span class="material-symbols-outlined text-amber-600">info</span>
              <div>
                <p class="text-sm font-bold text-amber-900">Important Note</p>
                <p class="mt-1 text-xs leading-relaxed text-amber-800">
                  Generated files are automatically deleted after their
                  expiration date to free up server resources.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Skeleton Loader -->
    <div v-else class="mx-auto max-w-5xl animate-pulse">
      <div class="mb-10 h-10 w-64 rounded-lg bg-gray-200"></div>
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div class="h-96 rounded-3xl bg-gray-200 lg:col-span-2"></div>
        <div class="h-96 rounded-3xl bg-gray-200"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-headline {
  font-family: 'Manrope', sans-serif;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}
</style>
