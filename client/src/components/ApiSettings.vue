<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Sidebar from './chat/Sidebar.vue';

// --- Данные ---
const apiKeys = ref([]);
const userEmail = ref('User');
const router = useRouter();
const API_URL = 'http://127.0.0.1:8000';

// --- Логика ---
const fetchKeys = async () => {
  try {
    const res = await axios.get(`${API_URL}/api-keys`);
    apiKeys.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

const createKey = async () => {
  const name = prompt("Название ключа (например, 'Prod App'):");
  if (!name) return;
  try {
    await axios.post(`${API_URL}/api-keys`, null, { params: { name } });
    fetchKeys();
  } catch (e) {
    alert('Ошибка создания ключа');
  }
};

const deleteKey = async (id) => {
  if (!confirm('Отозвать этот ключ? Приложения с ним перестанут работать.'))
    return;
  try {
    await axios.delete(`${API_URL}/api-keys/${id}`);
    fetchKeys();
  } catch (e) {
    alert('Ошибка удаления');
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  alert('Скопировано!');
};

const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1])).sub;
  } catch (e) {
    return 'User';
  }
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) userEmail.value = parseJwt(token);
  fetchKeys();
});

// Форматирование даты
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
};
</script>

<template>
  <div
    class="flex h-screen overflow-hidden bg-slate-50 font-sans text-slate-800"
  >
    <!-- Используем тот же Sidebar, но он сам поймет, что мы на странице API -->
    <Sidebar :user-email="userEmail" @logout="logout" />

    <!-- MAIN CONTENT -->
    <main class="relative flex flex-1 flex-col overflow-hidden">
      <!-- HEADER -->
      <header
        class="z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/70 px-8 backdrop-blur"
      >
        <h1 class="text-lg font-semibold text-slate-800">
          Управление доступом API
        </h1>
        <div class="flex items-center gap-3">
          <span class="text-xs text-slate-500">Статус системы:</span>
          <span
            class="flex items-center gap-1.5 rounded-full border border-green-100 bg-green-50 px-2 py-1 text-xs font-medium text-green-600"
          >
            <span class="h-1.5 w-1.5 rounded-full bg-green-500"></span> Online
          </span>
        </div>
      </header>

      <!-- CONTENT SCROLL AREA -->
      <div class="flex-1 overflow-y-auto p-8">
        <div class="mx-auto max-w-5xl space-y-8">
          <!-- Intro -->
          <div>
            <h2 class="mb-2 text-2xl font-bold text-slate-900">
              Ваши API Ключи
            </h2>
            <p class="text-slate-500">
              Управляйте ключами доступа для интеграции AIrelav в ваши
              приложения.
            </p>
          </div>

          <!-- Keys Card -->
          <div
            class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
          >
            <div
              class="flex items-center justify-between border-b border-slate-100 bg-slate-50/50 px-6 py-4"
            >
              <div>
                <h3
                  class="text-sm font-bold uppercase tracking-wide text-slate-800"
                >
                  Активные ключи
                </h3>
              </div>
              <button
                class="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:opacity-90 hover:shadow"
                @click="createKey"
              >
                <i class="fas fa-plus"></i> Создать ключ
              </button>
            </div>

            <div class="divide-y divide-slate-100">
              <!-- Empty State -->
              <div
                v-if="apiKeys.length === 0"
                class="p-8 text-center text-slate-400"
              >
                У вас пока нет активных API ключей.
              </div>

              <!-- Key Item -->
              <div
                v-for="key in apiKeys"
                :key="key.id"
                class="flex flex-col justify-between p-6 transition hover:bg-slate-50 sm:flex-row sm:items-center"
              >
                <div class="space-y-1">
                  <div class="flex items-center gap-3">
                    <span class="font-semibold text-slate-900">{{
                      key.name
                    }}</span>
                    <span
                      class="rounded bg-green-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-green-700"
                      >Active</span
                    >
                  </div>
                  <div class="flex items-center gap-2">
                    <code
                      class="rounded border border-slate-200 bg-slate-100 px-2 py-1 font-mono text-xs text-slate-500"
                      >{{ key.key }}</code
                    >
                    <button
                      class="text-slate-400 transition hover:text-blue-500"
                      title="Скопировать"
                      @click="copyToClipboard(key.key)"
                    >
                      <i class="far fa-copy"></i>
                    </button>
                  </div>
                  <p class="pt-1 text-xs text-slate-400">
                    Создан {{ formatDate(key.created_at) }}
                  </p>
                </div>
                <div class="mt-4 flex items-center gap-3 sm:mt-0">
                  <button
                    class="rounded-lg p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-500"
                    @click="deleteKey(key.id)"
                  >
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Example Usage -->
          <div
            class="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-sm"
          >
            <div
              class="flex items-center justify-between border-b border-slate-800 bg-slate-950/50 px-4 py-3"
            >
              <div class="flex gap-2">
                <div class="h-2.5 w-2.5 rounded-full bg-red-500/20"></div>
                <div class="h-2.5 w-2.5 rounded-full bg-green-500/20"></div>
              </div>
              <span class="font-mono text-xs text-slate-500">example.sh</span>
            </div>
            <div class="overflow-x-auto p-6">
              <code class="font-mono text-sm leading-relaxed text-slate-300">
                <span class="text-purple-400">curl</span> -X POST
                {{ API_URL }}/generate \<br />
                &nbsp;&nbsp;-H
                <span class="text-yellow-200"
                  >"Authorization: Bearer sk-relav..."</span
                >
                \<br />
                &nbsp;&nbsp;-H
                <span class="text-yellow-200"
                  >"Content-Type: application/json"</span
                >
                \<br />
                &nbsp;&nbsp;-d
                <span class="text-green-300"
                  >'{ "prompt": "List of 50 users" }'</span
                >
              </code>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
