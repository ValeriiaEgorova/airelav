<script setup>
const props = defineProps({
  message: { type: Object, required: true },
});

const API_URL = 'http://127.0.0.1:8000';

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
    <div v-if="message.role === 'user'" class="mb-8 flex justify-end">
      <div
        class="max-w-2xl rounded-2xl rounded-tr-sm bg-slate-100 px-6 py-4 text-slate-800 shadow-sm"
      >
        {{ message.content }}
      </div>
    </div>

    <div v-else class="mb-8 flex max-w-4xl gap-4">
      <div
        class="mt-1 flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-blue-100"
      >
        <i class="fas fa-robot text-blue-600"></i>
      </div>

      <div class="w-full space-y-4">
        <div v-if="message.loading" class="space-y-3">
          <div class="flex items-center gap-3 text-sm text-slate-500">
            <div class="flex gap-1">
              <div
                class="h-2 w-2 animate-bounce rounded-full bg-blue-500"
                style="animation-delay: -0.32s"
              ></div>
              <div
                class="h-2 w-2 animate-bounce rounded-full bg-blue-500"
                style="animation-delay: -0.16s"
              ></div>
              <div
                class="h-2 w-2 animate-bounce rounded-full bg-blue-500"
              ></div>
            </div>
            <span>{{ message.status_msg || 'Думаю...' }}</span>
          </div>
          <div class="h-1 w-64 overflow-hidden rounded-full bg-slate-200">
            <div
              class="h-full bg-blue-500 transition-all duration-500"
              :style="{ width: message.progress + '%' }"
            ></div>
          </div>
        </div>

        <div
          v-else-if="message.error"
          class="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700"
        >
          <p class="font-bold">
            <i class="fas fa-exclamation-circle mr-2"></i>Ошибка генерации
          </p>
          <p class="mt-1 text-sm">{{ message.content }}</p>
        </div>

        <div v-else>
          <p class="mb-3 text-slate-700">{{ message.content }}</p>

          <div
            v-if="message.preview"
            class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow"
          >
            <div
              class="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-2"
            >
              <span class="text-xs font-semibold text-slate-500"
                >Предпросмотр (5 строк)</span
              >
              <div class="flex gap-2">
                <a
                  :href="`${API_URL}/download/${message.task_id}?format=csv`"
                  target="_blank"
                  class="rounded px-2 py-1 text-xs text-green-600 transition hover:bg-green-50"
                  ><i class="fas fa-file-csv"></i> CSV</a
                >
                <a
                  :href="`${API_URL}/download/${message.task_id}?format=json`"
                  target="_blank"
                  class="rounded px-2 py-1 text-xs text-blue-600 transition hover:bg-blue-50"
                  ><i class="fas fa-file-code"></i> JSON</a
                >
                <a
                  :href="`${API_URL}/download/${message.task_id}?format=xlsx`"
                  target="_blank"
                  class="rounded px-2 py-1 text-xs text-emerald-600 transition hover:bg-emerald-50"
                  ><i class="fas fa-file-excel"></i> XLSX</a
                >
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th
                      v-for="(key, idx) in Object.keys(message.preview[0])"
                      :key="idx"
                      class="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500"
                    >
                      {{ key }}
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-for="(row, rIdx) in message.preview" :key="rIdx">
                    <td
                      v-for="(val, cIdx) in row"
                      :key="cIdx"
                      class="whitespace-nowrap px-4 py-2 text-slate-700"
                    >
                      {{ val }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- <div class="border-t border-gray-200 bg-gray-50 px-4 py-2 text-center">
              <span class="text-xs text-gray-400">Показана часть данных. Скачайте файл для полного доступа.</span>
            </div> -->

            <div
              class="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-4 py-2"
            >
              <div
                class="flex items-center gap-3 text-xs font-medium text-slate-500"
              >
                <span v-if="message.row_count !== undefined">
                  <i class="fas fa-list-ol mr-1"></i>
                  {{ formatNumber(message.row_count) }} строк
                </span>
                <span v-if="message.file_size !== undefined">
                  <i class="fas fa-weight-hanging mr-1"></i>
                  {{ formatBytes(message.file_size) }}
                </span>
              </div>

              <span class="text-xs text-slate-400">
                Показаны первые 5 строк
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
