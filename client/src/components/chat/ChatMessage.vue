<script setup>
import axios from 'axios';
const props = defineProps({
  message: { type: Object, required: true },
});

import { useToast } from 'vue-toastification';
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
    <div v-if="message.role === 'user'" class="group mb-8 flex justify-end">
      <div class="flex max-w-[80%] flex-col items-end gap-2">
        <div
          class="rounded-2xl rounded-tr-sm bg-surface-container-highest p-5 font-medium leading-relaxed text-on-surface-variant shadow-sm"
        >
          {{ message.content }}
        </div>
      </div>
    </div>

    <div v-else class="mb-8 flex justify-start">
      <div class="flex w-full max-w-[95%] flex-col items-start gap-4">
        <div class="mb-2 flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10"
          >
            <span
              class="material-symbols-outlined text-lg text-primary"
              style="font-variation-settings: 'FILL' 1"
              >auto_awesome</span
            >
          </div>
          <span class="font-headline font-bold text-on-surface"
            >Airelav AI</span
          >
        </div>

        <div
          class="flex w-full flex-col gap-6 rounded-xl border border-outline-variant/10 bg-surface-container-low/50 p-6 shadow-sm"
        >
          <div v-if="message.loading" class="space-y-4">
            <div
              class="flex items-center gap-3 text-sm font-medium text-on-surface-variant"
            >
              <span class="material-symbols-outlined animate-spin text-primary"
                >sync</span
              >
              <span>{{
                message.status_msg || 'Processing your request...'
              }}</span>
            </div>
            <div
              class="h-1.5 w-full max-w-sm overflow-hidden rounded-full bg-surface-container-highest"
            >
              <div
                class="h-full rounded-full bg-primary transition-all duration-500"
                :style="{ width: message.progress + '%' }"
              ></div>
            </div>
          </div>

          <div
            v-else-if="message.error"
            class="rounded-xl border border-error/20 bg-error-container/30 p-4 text-error"
          >
            <p class="flex items-center font-bold">
              <span class="material-symbols-outlined mr-2 text-lg">error</span>
              Generation Error
            </p>
            <p class="mt-1 text-sm font-medium">{{ message.content }}</p>
          </div>

          <div v-else>
            <div
              class="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between"
            >
              <div>
                <h3
                  class="font-headline text-2xl font-bold tracking-tight text-on-surface"
                >
                  Dataset Generated
                </h3>
                <p class="mt-1 text-sm text-on-surface-variant">
                  {{ message.content }}
                </p>
              </div>

              <div v-if="message.preview" class="flex flex-wrap gap-2">
                <button
                  class="flex items-center gap-2 rounded-full border border-outline-variant/10 bg-surface-container-lowest px-4 py-2 text-xs font-bold text-primary shadow-sm transition-all hover:bg-white"
                  @click="downloadFile(message.task_id, 'csv')"
                >
                  <span class="material-symbols-outlined text-sm"
                    >download</span
                  >
                  CSV
                </button>
                <button
                  class="flex items-center gap-2 rounded-full border border-outline-variant/10 bg-surface-container-lowest px-4 py-2 text-xs font-bold text-primary shadow-sm transition-all hover:bg-white"
                  @click="downloadFile(message.task_id, 'json')"
                >
                  <span class="material-symbols-outlined text-sm"
                    >download</span
                  >
                  JSON
                </button>
                <button
                  class="flex items-center gap-2 rounded-full bg-gradient-to-r from-primary to-primary-container px-6 py-2 text-xs font-bold text-white shadow-lg shadow-primary/20 transition-all hover:scale-105 active:scale-95"
                  @click="downloadFile(message.task_id, 'xlsx')"
                >
                  Export Excel
                </button>
              </div>
            </div>

            <div
              v-if="message.preview && message.preview.length"
              class="overflow-hidden rounded-2xl border border-outline-variant/10 bg-surface-container-lowest"
            >
              <div class="overflow-x-auto">
                <table class="w-full border-collapse text-left text-sm">
                  <thead>
                    <tr
                      class="bg-surface-container-low text-on-surface-variant"
                    >
                      <th
                        v-for="(key, idx) in Object.keys(
                          message.preview[0] || {}
                        )"
                        :key="idx"
                        class="px-6 py-4 text-[11px] font-bold uppercase tracking-widest"
                      >
                        {{ key }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="font-medium text-on-surface">
                    <tr
                      v-for="(row, rIdx) in message.preview"
                      :key="rIdx"
                      class="border-t border-outline-variant/5 transition-colors hover:bg-surface-container/30"
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

              <div
                class="flex items-center justify-between border-t border-outline-variant/10 bg-surface-container-low p-4"
              >
                <div
                  class="flex gap-4 text-[11px] font-bold uppercase tracking-widest text-on-surface-variant/60"
                >
                  <span v-if="message.row_count !== undefined">
                    TOTAL: {{ formatNumber(message.row_count) }} ROWS
                  </span>
                  <span v-if="message.file_size !== undefined">
                    SIZE: {{ formatBytes(message.file_size) }}
                  </span>
                </div>
                <span
                  class="text-[10px] font-bold uppercase tracking-widest text-primary/50"
                  >Preview Mode</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
