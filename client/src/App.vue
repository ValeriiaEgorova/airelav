<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';


const prompt = ref('');
const selectedFormat = ref('csv');
const history = ref([]);
const isGenerating = ref(false);
const currentTask = ref(null); 
const pollingInterval = ref(null);

const API_URL = 'http://127.0.0.1:8000';

const fetchHistory = async () => {
  try {
    const response = await axios.get(`${API_URL}/history`);
    history.value = response.data;
  } catch (error) {
    console.error("Ошибка загрузки истории:", error);
  }
};

const startGeneration = async () => {
  if (!prompt.value.trim()) return alert("Введите описание данных!");
  
  isGenerating.value = true;
  currentTask.value = { status_message: "Инициализация...", progress: 0, preview_data: null };

  try {
    const response = await axios.post(`${API_URL}/generate`, null, {
      params: {
        prompt: prompt.value,
        file_format: selectedFormat.value
      }
    });

    const taskId = response.data.task_id;
    
    pollingInterval.value = setInterval(() => checkStatus(taskId), 2000);

  } catch (error) {
    alert("Ошибка соединения с сервером");
    isGenerating.value = false;
  }
};

const checkStatus = async (taskId) => {
  await fetchHistory();
  
  const task = history.value.find(t => t.id === taskId);
  
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
    
    <div class="w-80 bg-white border-r border-gray-200 flex flex-col fixed h-full z-10">
      <div class="h-16 flex items-center px-6 border-b">
        <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
          <i class="fas fa-cube text-white text-sm"></i>
        </div>
        <span class="text-xl font-bold text-gray-900">SynthGen AI</span>
      </div>

      <div class="p-4">
        <button @click="prompt = ''; currentTask = null" class="w-full bg-blue-500 text-white px-4 py-3 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center space-x-2">
          <i class="fas fa-plus"></i>
          <span>Новый запрос</span>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto px-4 pb-4">
        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">История запросов</h3>
        
        <div class="space-y-2">
          <div 
            v-for="item in history" 
            :key="item.id"
            @click="selectFromHistory(item)"
            class="group p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors border border-transparent hover:border-gray-200"
            :class="{'bg-blue-50 border-blue-200': currentTask && currentTask.id === item.id}"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ item.prompt }}</p>
                <div class="flex items-center space-x-3 mt-1">
                  <span class="flex items-center space-x-1 text-xs text-gray-500">
                    <i :class="['fas', getFormatIcon(item.file_format)]"></i>
                    <span class="uppercase">{{ item.file_format }}</span>
                  </span>
                  <span class="text-xs text-gray-500">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
              
              <div class="flex items-center">
                <div v-if="item.status === 'completed'" class="w-2 h-2 bg-green-500 rounded-full"></div>
                <div v-else-if="item.status === 'processing'" class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <div v-else-if="item.status === 'failed'" class="w-2 h-2 bg-red-500 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex-1 flex flex-col ml-80">
      
      <header class="bg-white shadow-sm border-b h-16 flex items-center justify-end px-8">
        <nav class="flex space-x-6">
          <a href="#" class="text-gray-600 hover:text-gray-900">Документация</a>
          <a href="#" class="text-gray-900 font-medium"><i class="fab fa-github mr-2"></i>GitHub</a>
        </nav>
      </header>

      <div class="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div class="w-full max-w-4xl">
          
          <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-4">
              Генерация данных силой мысли
            </h1>
            <p class="text-xl text-gray-600">
              Опишите сценарий на естественном языке, и ИИ создаст датасет.
            </p>
          </div>

          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 relative overflow-hidden">
            
            <div class="mb-6">
              <textarea 
                v-model="prompt"
                class="w-full h-32 p-4 border border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-lg" 
                placeholder="Например: Список из 500 заказов интернет-магазина, где у 10% записей отсутствует номер телефона..."
              ></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Формат файла</label>
                <div class="flex bg-gray-100 rounded-lg p-1">
                  <button @click="selectedFormat = 'csv'" :class="{'bg-white shadow-sm text-gray-900': selectedFormat === 'csv', 'text-gray-500': selectedFormat !== 'csv'}" class="flex-1 py-2 rounded-md text-sm font-medium transition-all">CSV</button>
                  <button @click="selectedFormat = 'json'" :class="{'bg-white shadow-sm text-gray-900': selectedFormat === 'json', 'text-gray-500': selectedFormat !== 'json'}" class="flex-1 py-2 rounded-md text-sm font-medium transition-all">JSON</button>
                  <button @click="selectedFormat = 'excel'" :class="{'bg-white shadow-sm text-gray-900': selectedFormat === 'excel', 'text-gray-500': selectedFormat !== 'excel'}" class="flex-1 py-2 rounded-md text-sm font-medium transition-all">Excel</button>
                </div>
              </div>
               <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Язык данных</label>
                <select class="w-full p-2.5 border border-gray-200 rounded-lg bg-white">
                  <option>Russian (RU)</option>
                  <option disabled>English (US)</option>
                </select>
              </div>
            </div>

            <button 
              @click="startGeneration" 
              :disabled="isGenerating"
              class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-8 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all transform hover:scale-[1.01] flex items-center justify-center space-x-3 text-lg font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <i v-if="!isGenerating" class="fas fa-bolt"></i>
              <i v-else class="fas fa-circle-notch fa-spin"></i>
              <span>{{ isGenerating ? 'Нейросеть работает...' : 'Сгенерировать датасет' }}</span>
            </button>

            <div v-if="isGenerating && currentTask" class="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-100 animate-fade-in">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-medium text-blue-800">{{ currentTask.status_message }}</span>
                <span class="text-sm font-bold text-blue-600">{{ currentTask.progress }}%</span>
              </div>
              <div class="w-full bg-blue-200 rounded-full h-2.5">
                <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: currentTask.progress + '%' }"></div>
              </div>
            </div>

            <div v-if="currentTask && currentTask.preview_data && currentTask.preview_data.length > 0" class="mt-8 animate-fade-in border-t pt-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold text-gray-800 flex items-center">
                  <i class="fas fa-table mr-2 text-blue-500"></i>Предпросмотр данных
                </h3>
                <a 
                  :href="`${API_URL}/download/${currentTask.id}`" 
                  target="_blank"
                  class="text-sm bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-lg transition-colors flex items-center"
                >
                  <i class="fas fa-download mr-2"></i> Скачать файл
                </a>
              </div>
              
              <div class="overflow-x-auto border border-gray-200 rounded-lg shadow-sm">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th 
                        v-for="(key, index) in Object.keys(currentTask.preview_data[0])" 
                        :key="index"
                        class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider"
                      >
                        {{ key }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <!-- Строки таблицы -->
                    <tr v-for="(row, rowIndex) in currentTask.preview_data" :key="rowIndex" class="hover:bg-gray-50">
                      <td 
                        v-for="(value, colIndex) in row" 
                        :key="colIndex"
                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-700"
                      >
                        {{ value }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p class="mt-2 text-center text-xs text-gray-400">Показаны первые 5 строк. Скачайте файл для полного доступа.</p>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
</style>