<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import BaseModal from '../components/common/BaseModal.vue'; // Проверьте путь к компоненту

const toast = useToast();
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// --- СОСТОЯНИЕ (STATE) ---
const apiKeys = ref([]);
const searchQuery = ref('');

// Состояние для модалки создания
const showKeyModal = ref(false);
const newKeyName = ref('');
const isCreating = ref(false);

// Состояние для модалки удаления (Revoke)
const showDeleteModal = ref(false);
const keyToDeleteId = ref(null);
const isDeleting = ref(false);

// --- ЛОГИКА API ---

const fetchKeys = async () => {
  try {
    const res = await axios.get(`${API_URL}/api-keys`);
    apiKeys.value = res.data;
  } catch (e) {
    console.error('Error fetching keys:', e);
    toast.error('Failed to load API keys');
  }
};

// Открытие модалки создания
const openCreateModal = () => {
  newKeyName.value = '';
  showKeyModal.value = true;
};

// Создание нового ключа
const generateNewKey = async () => {
  if (!newKeyName.value.trim()) {
    toast.warning('Please enter a key name');
    return;
  }

  isCreating.value = true;
  try {
    await axios.post(`${API_URL}/api-keys`, null, {
      params: { name: newKeyName.value },
    });
    showKeyModal.value = false;
    await fetchKeys();
    toast.success('API Key created successfully');
  } catch (e) {
    const errorMsg = e.response?.data?.detail || 'Failed to create key';
    toast.error(errorMsg);
  } finally {
    isCreating.value = false;
  }
};

// Открытие модалки подтверждения удаления
const confirmRevoke = (id) => {
  keyToDeleteId.value = id;
  showDeleteModal.value = true;
};

// Удаление (аннулирование) ключа
const handleRevoke = async () => {
  if (!keyToDeleteId.value) return;

  isDeleting.value = true;
  try {
    await axios.delete(`${API_URL}/api-keys/${keyToDeleteId.value}`);
    showDeleteModal.value = false;
    await fetchKeys();
    toast.success('Key revoked and deleted');
  } catch (e) {
    toast.error('Failed to delete key');
  } finally {
    isDeleting.value = false;
    keyToDeleteId.value = null;
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  toast.success('Copied to clipboard!', { timeout: 2000 });
};

// --- ВЫЧИСЛЯЕМЫЕ СВОЙСТВА ---

const filteredKeys = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return apiKeys.value.filter(
    (k) =>
      (k.name || '').toLowerCase().includes(query) ||
      (k.key || '').toLowerCase().includes(query)
  );
});

const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
};

onMounted(() => {
  fetchKeys();
});
</script>

<template>
  <!-- МОДАЛКА: СОЗДАНИЕ КЛЮЧА -->
  <BaseModal
    :show="showKeyModal"
    title="Create New API Key"
    description="Give your key a name to remember where you use it."
    confirm-text="Generate Key"
    @close="showKeyModal = false"
    @confirm="generateNewKey"
  >
    <div class="mb-6 mt-2">
      <input
        v-model="newKeyName"
        type="text"
        placeholder="e.g. Production App"
        class="w-full rounded-xl border border-outline-variant/20 bg-surface-container-low p-3 text-on-surface outline-none focus:ring-2 focus:ring-primary"
        @keyup.enter="generateNewKey"
      />
    </div>
  </BaseModal>

  <!-- МОДАЛКА: УДАЛЕНИЕ КЛЮЧА -->
  <BaseModal
    :show="showDeleteModal"
    title="Revoke API Key?"
    description="Any applications using this key will immediately lose access to the Airelav API. This action cannot be undone."
    confirm-text="Revoke Key"
    :is-destructive="true"
    @close="showDeleteModal = false"
    @confirm="handleRevoke"
  />

  <div
    class="custom-scrollbar h-screen w-full overflow-y-auto bg-background px-8 pb-12 pt-8"
  >
    <div class="mx-auto max-w-6xl">
      <!-- Header -->
      <div
        class="mb-12 flex flex-col justify-between gap-6 md:flex-row md:items-end"
      >
        <div class="space-y-2">
          <h1
            class="font-headline text-4xl font-extrabold tracking-tight text-on-background"
          >
            API Management
          </h1>
          <p class="max-w-lg leading-relaxed text-on-surface-variant">
            Securely manage your access keys for the Airelav Data Engine. Use
            these keys to authenticate your requests via our REST API.
          </p>
        </div>
        <button
          class="flex w-fit items-center gap-3 rounded-full bg-primary px-8 py-4 font-bold text-on-primary shadow-lg shadow-primary/20 transition-all hover:scale-[1.02] active:scale-95"
          @click="openCreateModal"
        >
          <span class="material-symbols-outlined">add</span>
          Create New Key
        </button>
      </div>

      <!-- Stats -->
      <div class="mb-12 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div
          class="flex min-h-[140px] flex-col justify-between rounded-2xl border border-outline-variant/5 bg-surface-container-low p-6"
        >
          <span class="text-sm font-medium text-on-surface-variant"
            >Active Keys</span
          >
          <div class="flex items-baseline gap-2">
            <span class="font-headline text-4xl font-bold text-primary">{{
              apiKeys.length.toString().padStart(2, '0')
            }}</span>
            <span class="text-xs text-on-surface-variant/60">/ 10 Limit</span>
          </div>
        </div>

        <div
          class="group relative flex min-h-[140px] flex-col justify-between overflow-hidden rounded-2xl border border-outline-variant/5 bg-surface-container-low p-6"
        >
          <div class="relative z-10">
            <span class="text-sm font-medium text-on-surface-variant"
              >System Health</span
            >
            <div class="mt-4 flex items-center gap-2">
              <div
                class="h-3 w-3 animate-pulse rounded-full bg-emerald-500"
              ></div>
              <span class="font-bold text-on-background">Operational</span>
            </div>
          </div>
          <div
            class="absolute -bottom-4 -right-4 opacity-10 transition-transform duration-700 group-hover:scale-110"
          >
            <span class="material-symbols-outlined text-8xl"
              >verified_user</span
            >
          </div>
        </div>
      </div>

      <!-- Keys Table Section -->
      <div
        class="rounded-3xl border border-outline-variant/5 bg-surface-container-low p-1"
      >
        <div
          class="overflow-hidden rounded-[calc(1.5rem-4px)] bg-surface-container-lowest"
        >
          <!-- Table Header / Search -->
          <div
            class="flex flex-col items-center justify-between gap-4 border-b border-surface-container-low px-8 py-6 sm:flex-row"
          >
            <h3 class="font-headline text-xl font-bold">Existing Keys</h3>
            <div class="relative w-full sm:w-64">
              <span
                class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-sm text-on-surface-variant/50"
                >search</span
              >
              <input
                v-model="searchQuery"
                class="w-full rounded-full border-none bg-surface-container-low py-2 pl-10 pr-4 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="Search keys..."
                type="text"
              />
            </div>
          </div>

          <!-- List -->
          <div class="divide-y divide-surface-container-low">
            <div
              v-if="filteredKeys.length === 0"
              class="px-8 py-12 text-center text-on-surface-variant/40"
            >
              <span class="material-symbols-outlined mb-2 text-4xl opacity-20"
                >key_off</span
              >
              <p>No API keys found.</p>
            </div>

            <div
              v-for="key in filteredKeys"
              :key="key.id"
              class="group flex flex-col justify-between gap-6 px-8 py-6 transition-colors duration-300 hover:bg-surface-container-low/50 lg:flex-row lg:items-center"
            >
              <!-- Key Info -->
              <div class="flex items-center gap-6">
                <div
                  class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary"
                >
                  <span class="material-symbols-outlined">key</span>
                </div>
                <div class="space-y-1">
                  <h4 class="font-bold text-on-background">{{ key.name }}</h4>
                  <div class="flex items-center gap-3">
                    <code
                      class="rounded-full bg-surface-container-high px-3 py-1 font-mono text-[11px] tracking-tighter text-on-surface"
                    >
                      {{ key.key.substring(0, 10) }}••••••••{{
                        key.key.substring(key.key.length - 4)
                      }}
                    </code>
                    <span
                      class="h-1.5 w-1.5 rounded-full bg-emerald-500"
                    ></span>
                    <span
                      class="text-[10px] font-bold uppercase tracking-wider text-emerald-600"
                      >Active</span
                    >
                  </div>
                </div>
              </div>

              <!-- Actions & Metadata -->
              <div
                class="flex items-center justify-between gap-12 border-t pt-4 lg:justify-end lg:border-none lg:pt-0"
              >
                <div class="text-left lg:text-right">
                  <p
                    class="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/40"
                  >
                    Created
                  </p>
                  <p class="text-sm font-medium text-on-surface-variant">
                    {{ formatDate(key.created_at) }}
                  </p>
                </div>

                <div class="flex items-center gap-2">
                  <button
                    class="flex items-center gap-2 rounded-xl p-2 text-on-surface-variant transition-all hover:bg-primary/10 group-hover:text-primary"
                    title="Copy to clipboard"
                    @click="copyToClipboard(key.key)"
                  >
                    <span class="material-symbols-outlined text-[20px]"
                      >content_copy</span
                    >
                    <span class="hidden text-xs font-semibold sm:inline"
                      >Copy</span
                    >
                  </button>
                  <button
                    class="flex items-center gap-2 rounded-xl p-2 text-on-surface-variant transition-all hover:bg-red-50 hover:text-red-600"
                    title="Revoke key"
                    @click="confirmRevoke(key.id)"
                  >
                    <span class="material-symbols-outlined text-[20px]"
                      >cancel</span
                    >
                    <span class="hidden text-xs font-semibold sm:inline"
                      >Revoke</span
                    >
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Help Text -->
      <p
        class="mx-auto mt-8 max-w-2xl text-center text-xs leading-relaxed text-on-surface-variant/40"
      >
        Airelav API keys are secrets. If a key is compromised, revoke it
        immediately. You can have up to 10 active keys at any given time.
      </p>
    </div>
  </div>
</template>

<style scoped>
.font-headline {
  font-family: 'Manrope', sans-serif;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e2db;
  border-radius: 10px;
}
</style>
