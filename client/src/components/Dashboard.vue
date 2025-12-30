<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const prompt = ref('');
const selectedFormat = ref('csv');
const history = ref([]);
const isGenerating = ref(false);
const currentTask = ref(null);
const pollingInterval = ref(null);

const API_URL = 'http://127.0.0.1:8000';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

const fetchHistory = async () => {
  try {
    const response = await axios.get(`${API_URL}/history`);
    history.value = response.data;
  } catch (error) {
    console.error('Ошибка загрузки истории:', error);
  }
};

const startGeneration = async () => {
  if (!prompt.value.trim()) return alert('Введите описание данных!');

  isGenerating.value = true;
  currentTask.value = {
    status_message: 'Инициализация...',
    progress: 0,
    preview_data: null,
  };

  try {
    const response = await axios.post(`${API_URL}/generate`, null, {
      params: { prompt: prompt.value }, // file_format убрали
    });

    const taskId = response.data.task_id;

    pollingInterval.value = setInterval(() => checkStatus(taskId), 2000);
  } catch (error) {
    console.error(error); // <--- Добавили эту строчку, теперь переменная используется
    alert('Ошибка соединения с сервером');
    isGenerating.value = false;
  }
};

const checkStatus = async (taskId) => {
  await fetchHistory();

  const task = history.value.find((t) => t.id === taskId);

  if (task) {
    currentTask.value = task;

    if (task.status === 'completed' || task.status === 'failed') {
      clearInterval(pollingInterval.value);
      isGenerating.value = false;

      if (task.status === 'completed') {
        // авто-скачивание
        // window.open(`${API_URL}/download/${taskId}`, '_blank');
      } else {
        alert(`Ошибка генерации: ${task.error_log}`);
      }
    }
  }
};

const selectFromHistory = (item) => {
  prompt.value = item.prompt;
  selectedFormat.value = item.file_format;
  currentTask.value = item;
};

const getFormatIcon = (fmt) => {
  if (fmt === 'csv') return 'fa-file-csv text-green-500';
  if (fmt === 'json') return 'fa-code text-blue-500';
  return 'fa-file-excel text-green-600';
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

onMounted(() => {
  fetchHistory();
});
</script>

<template>
  <div class="flex min-h-screen bg-gray-50 font-sans">
    <div
      class="fixed z-10 flex h-full w-80 flex-col border-r border-gray-200 bg-white"
    >
      <div class="flex h-16 items-center border-b px-6">
        <div
          class="mr-3 flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600"
        >
          <i class="fas fa-cube text-sm text-white"></i>
        </div>
        <span class="text-xl font-bold text-gray-900">SynthGen AI</span>
      </div>

      <div class="p-4">
        <button
          class="flex w-full items-center justify-center space-x-2 rounded-lg bg-blue-500 px-4 py-3 text-white transition-colors hover:bg-blue-600"
          @click="
            prompt = '';
            currentTask = null;
          "
        >
          <i class="fas fa-plus"></i>
          <span>Новый запрос</span>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto px-4 pb-4">
        <h3
          class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500"
        >
          История запросов
        </h3>

        <div class="space-y-2">
          <div
            v-for="item in history"
            :key="item.id"
            class="group cursor-pointer rounded-lg border border-transparent p-3 transition-colors hover:border-gray-200 hover:bg-gray-50"
            :class="{
              'border-blue-200 bg-blue-50':
                currentTask && currentTask.id === item.id,
            }"
            @click="selectFromHistory(item)"
          >
            <div class="flex items-start justify-between">
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-gray-900">
                  {{ item.prompt }}
                </p>
                <div class="mt-1 flex items-center space-x-3">
                  <span
                    class="flex items-center space-x-1 text-xs text-gray-500"
                  >
                    <i :class="['fas', getFormatIcon(item.file_format)]"></i>
                    <span class="uppercase">{{ item.file_format }}</span>
                  </span>
                  <span class="text-xs text-gray-500">{{
                    formatDate(item.created_at)
                  }}</span>
                </div>
              </div>

              <div class="flex items-center">
                <div
                  v-if="item.status === 'completed'"
                  class="h-2 w-2 rounded-full bg-green-500"
                ></div>
                <div
                  v-else-if="item.status === 'processing'"
                  class="h-2 w-2 animate-pulse rounded-full bg-yellow-500"
                ></div>
                <div
                  v-else-if="item.status === 'failed'"
                  class="h-2 w-2 rounded-full bg-red-500"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="border-t border-gray-100 p-4">
        <button
          class="flex w-full items-center justify-center space-x-2 rounded-lg px-4 py-2 text-gray-500 transition-colors hover:bg-red-50 hover:text-red-600"
          @click="logout"
        >
          <i class="fas fa-sign-out-alt"></i>
          <span>Выйти из аккаунта</span>
        </button>
      </div>
    </div>

    <div class="ml-80 flex flex-1 flex-col">
      <header
        class="flex h-16 items-center justify-end border-b bg-white px-8 shadow-sm"
      >
        <nav class="flex space-x-6">
          <a href="#" class="text-gray-600 hover:text-gray-900">Документация</a>
          <a href="#" class="font-medium text-gray-900"
            ><i class="fab fa-github mr-2"></i>GitHub</a
          >
        </nav>
      </header>

      <div class="flex flex-1 items-center justify-center bg-gray-50 p-8">
        <div class="w-full max-w-4xl">
          <div class="mb-8 text-center">
            <h1 class="mb-4 text-4xl font-bold text-gray-900">
              Генерация данных силой мысли
            </h1>
            <p class="text-xl text-gray-600">
              Опишите сценарий на естественном языке, и ИИ создаст датасет.
            </p>
          </div>

          <div
            class="relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-8 shadow-lg"
          >
            <div class="mb-6">
              <textarea
                v-model="prompt"
                class="h-32 w-full resize-none rounded-xl border border-gray-200 p-4 text-lg transition-all focus:border-transparent focus:ring-2 focus:ring-blue-500"
                placeholder="Например: Список из 500 заказов интернет-магазина, где у 10% записей отсутствует номер телефона..."
              ></textarea>
            </div>

            <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label class="mb-2 block text-sm font-medium text-gray-700"
                  >Язык данных</label
                >
                <select
                  class="w-full rounded-lg border border-gray-200 bg-white p-2.5"
                >
                  <option>Russian (RU)</option>
                  <option disabled>English (US)</option>
                </select>
              </div>
            </div>

            <button
              :disabled="isGenerating"
              class="flex w-full transform items-center justify-center space-x-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-[1.01] hover:from-blue-700 hover:to-indigo-700 disabled:cursor-not-allowed disabled:opacity-70"
              @click="startGeneration"
            >
              <i v-if="!isGenerating" class="fas fa-bolt"></i>
              <i v-else class="fas fa-circle-notch fa-spin"></i>
              <span>{{
                isGenerating ? 'Нейросеть работает...' : 'Сгенерировать датасет'
              }}</span>
            </button>

            <div
              v-if="isGenerating && currentTask"
              class="animate-fade-in mt-6 rounded-lg border border-blue-100 bg-blue-50 p-4"
            >
              <div class="mb-2 flex items-center justify-between">
                <span class="text-sm font-medium text-blue-800">{{
                  currentTask.status_message
                }}</span>
                <span class="text-sm font-bold text-blue-600"
                  >{{ currentTask.progress }}%</span
                >
              </div>
              <div class="h-2.5 w-full rounded-full bg-blue-200">
                <div
                  class="h-2.5 rounded-full bg-blue-600 transition-all duration-500"
                  :style="{ width: currentTask.progress + '%' }"
                ></div>
              </div>
            </div>

            <div
              v-if="currentTask && currentTask.preview_data"
              class="animate-fade-in mt-8 border-t pt-6"
            >
              <div class="mb-4 flex items-center justify-between">
                <h3 class="flex items-center text-lg font-bold text-gray-800">
                  <i class="fas fa-table mr-2 text-blue-500"></i>Предпросмотр
                </h3>

                <!-- НОВЫЕ КНОПКИ СКАЧИВАНИЯ -->
                <div class="flex space-x-2">
                  <span class="mr-2 self-center text-sm text-gray-500"
                    >Скачать как:</span
                  >

                  <a
                    :href="`${API_URL}/download/${currentTask.id}?format=csv`"
                    target="_blank"
                    class="flex items-center space-x-1 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm font-medium text-green-700 transition hover:bg-green-100"
                  >
                    <i class="fas fa-file-csv"></i> <span>CSV</span>
                  </a>

                  <a
                    :href="`${API_URL}/download/${currentTask.id}?format=json`"
                    target="_blank"
                    class="flex items-center space-x-1 rounded-lg border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm font-medium text-yellow-700 transition hover:bg-yellow-100"
                  >
                    <i class="fas fa-code"></i> <span>JSON</span>
                  </a>

                  <a
                    :href="`${API_URL}/download/${currentTask.id}?format=xlsx`"
                    target="_blank"
                    class="flex items-center space-x-1 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100"
                  >
                    <i class="fas fa-file-excel"></i> <span>Excel</span>
                  </a>
                </div>
              </div>

              <div
                class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm"
              >
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th
                        v-for="(key, index) in Object.keys(
                          currentTask.preview_data[0]
                        )"
                        :key="index"
                        class="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-gray-500"
                      >
                        {{ key }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 bg-white">
                    <tr
                      v-for="(row, rowIndex) in currentTask.preview_data"
                      :key="rowIndex"
                      class="hover:bg-gray-50"
                    >
                      <td
                        v-for="(value, colIndex) in row"
                        :key="colIndex"
                        class="whitespace-nowrap px-6 py-4 text-sm text-gray-700"
                      >
                        {{ value }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p class="mt-2 text-center text-xs text-gray-400">
                Показаны первые 5 строк. Скачайте файл для полного доступа.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
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
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
</style>
