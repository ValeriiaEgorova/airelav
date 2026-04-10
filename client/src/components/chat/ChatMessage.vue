<script setup>
import axios from 'axios';
const props = defineProps({
  message: { type: Object, required: true },
});

import { useToast } from "vue-toastification";
const toast = useToast();

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const downloadFile = async (taskId, format) => {
  try {
    const response = await axios.get(`${API_URL}/download/${taskId}`, {
      params: { format },
      responseType: 'blob',
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    link.setAttribute('download', `dataset_${taskId}.${format}`);

    document.body.appendChild(link);
    link.click();

    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Ошибка скачивания:', error);
    toast.error('Не удалось скачать файл. Возможно, сессия истекла.');
  }
};

const formatBytes = (bytes, decimals = 2) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const formatNumber = (num) => {
  return num ? num.toLocaleString('ru-RU') : '0';
};
</script>

<template>
  <div class="w-full">
    <div v-if="message.role === 'user'" class="flex justify-end group mb-8">
      <div class="max-w-[80%] flex flex-col items-end gap-2">
        <div class="bg-surface-container-highest p-5 rounded-2xl rounded-tr-sm text-on-surface-variant font-medium leading-relaxed shadow-sm">
          {{ message.content }}
        </div>
      </div>
    </div>

    <div v-else class="flex justify-start mb-8">
      <div class="max-w-[95%] w-full flex flex-col items-start gap-4">
        
        <div class="flex items-center gap-3 mb-2">
          <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <span class="material-symbols-outlined text-primary text-lg" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
          </div>
          <span class="font-headline font-bold text-on-surface">Airelav AI</span>
        </div>

        <div class="w-full bg-surface-container-low/50 rounded-xl p-6 flex flex-col gap-6 shadow-sm border border-outline-variant/10">
          
          <div v-if="message.loading" class="space-y-4">
            <div class="flex items-center gap-3 text-sm text-on-surface-variant font-medium">
              <span class="material-symbols-outlined animate-spin text-primary">sync</span>
              <span>{{ message.status_msg || 'Processing your request...' }}</span>
            </div>
            <div class="h-1.5 w-full max-w-sm overflow-hidden rounded-full bg-surface-container-highest">
              <div
                class="h-full bg-primary transition-all duration-500 rounded-full"
                :style="{ width: message.progress + '%' }"
              ></div>
            </div>
          </div>

          <div v-else-if="message.error" class="rounded-xl border border-error/20 bg-error-container/30 p-4 text-error">
            <p class="font-bold flex items-center">
              <span class="material-symbols-outlined mr-2 text-lg">error</span>
              Generation Error
            </p>
            <p class="mt-1 text-sm font-medium">{{ message.content }}</p>
          </div>

          <div v-else>
            <div class="flex flex-col md:flex-row md:justify-between md:items-end gap-4 mb-6">
              <div>
                <h3 class="font-headline text-2xl font-bold text-on-surface tracking-tight">Dataset Generated</h3>
                <p class="text-on-surface-variant text-sm mt-1">{{ message.content }}</p>
              </div>
              
              <div v-if="message.preview" class="flex flex-wrap gap-2">
                <button @click="downloadFile(message.task_id, 'csv')" class="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-full hover:bg-white border border-outline-variant/10 shadow-sm transition-all">
                  <span class="material-symbols-outlined text-sm">download</span> CSV
                </button>
                <button @click="downloadFile(message.task_id, 'json')" class="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest text-primary font-bold text-xs rounded-full hover:bg-white border border-outline-variant/10 shadow-sm transition-all">
                  <span class="material-symbols-outlined text-sm">download</span> JSON
                </button>
                <button @click="downloadFile(message.task_id, 'xlsx')" class="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-primary to-primary-container text-white font-bold text-xs rounded-full shadow-lg shadow-primary/20 hover:scale-105 active:scale-95 transition-all">
                  Export Excel
                </button>
              </div>
            </div>

            <div v-if="message.preview && message.preview.length" class="bg-surface-container-lowest rounded-2xl overflow-hidden border border-outline-variant/10">
              <div class="overflow-x-auto">
                <table class="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr class="bg-surface-container-low text-on-surface-variant">
                      <th 
                        v-for="(key, idx) in Object.keys(message.preview[0] || {})" 
                        :key="idx"
                        class="px-6 py-4 font-bold text-[11px] uppercase tracking-widest"
                      >
                        {{ key }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="text-on-surface font-medium">
                    <tr 
                      v-for="(row, rIdx) in message.preview" 
                      :key="rIdx"
                      class="hover:bg-surface-container/30 transition-colors border-t border-outline-variant/5"
                    >
                      <td 
                        v-for="(val, cIdx) in row" 
                        :key="cIdx"
                        class="px-6 py-4"
                      >
                        {{ val }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="p-4 bg-surface-container-low flex justify-between items-center border-t border-outline-variant/10">
                <div class="flex gap-4 text-[11px] font-bold text-on-surface-variant/60 uppercase tracking-widest">
                  <span v-if="message.row_count !== undefined">
                    TOTAL: {{ formatNumber(message.row_count) }} ROWS
                  </span>
                  <span v-if="message.file_size !== undefined">
                    SIZE: {{ formatBytes(message.file_size) }}
                  </span>
                </div>
                <span class="text-[10px] font-bold text-primary/50 uppercase tracking-widest">Preview Mode</span>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>