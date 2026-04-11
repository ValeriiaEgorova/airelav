<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useToast } from "vue-toastification";
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
      params: { name: newKeyName.value } 
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
  return apiKeys.value.filter(k => 
    (k.name || '').toLowerCase().includes(query) ||
    (k.key || '').toLowerCase().includes(query)
  );
});

const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    day: 'numeric', month: 'short', year: 'numeric',
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
    confirmText="Generate Key"
    @close="showKeyModal = false"
    @confirm="generateNewKey"
  >
    <div class="mt-2 mb-6">
      <input 
        v-model="newKeyName" 
        type="text" 
        placeholder="e.g. Production App" 
        class="w-full p-3 bg-surface-container-low border border-outline-variant/20 rounded-xl focus:ring-2 focus:ring-primary outline-none text-on-surface"
        @keyup.enter="generateNewKey"
      />
    </div>
  </BaseModal>

  <!-- МОДАЛКА: УДАЛЕНИЕ КЛЮЧА -->
  <BaseModal 
    :show="showDeleteModal"
    title="Revoke API Key?"
    description="Any applications using this key will immediately lose access to the Airelav API. This action cannot be undone."
    confirmText="Revoke Key"
    :isDestructive="true"
    @close="showDeleteModal = false"
    @confirm="handleRevoke"
  />

  <div class="pt-8 px-8 pb-12 w-full overflow-y-auto h-screen custom-scrollbar bg-background">
    <div class="max-w-6xl mx-auto">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
        <div class="space-y-2">
          <h1 class="text-4xl font-headline font-extrabold text-on-background tracking-tight">API Management</h1>
          <p class="text-on-surface-variant max-w-lg leading-relaxed">
            Securely manage your access keys for the Airelav Data Engine. Use these keys to authenticate your requests via our REST API.
          </p>
        </div>
        <button 
          @click="openCreateModal"
          class="bg-primary text-on-primary px-8 py-4 rounded-full font-bold flex items-center gap-3 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all w-fit"
        >
          <span class="material-symbols-outlined">add</span>
          Create New Key
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <div class="bg-surface-container-low p-6 rounded-2xl flex flex-col justify-between min-h-[140px] border border-outline-variant/5">
          <span class="text-on-surface-variant font-medium text-sm">Active Keys</span>
          <div class="flex items-baseline gap-2">
            <span class="text-4xl font-headline font-bold text-primary">{{ apiKeys.length.toString().padStart(2, '0') }}</span>
            <span class="text-on-surface-variant/60 text-xs">/ 10 Limit</span>
          </div>
        </div>
        
        <div class="bg-surface-container-low p-6 rounded-2xl flex flex-col justify-between min-h-[140px] relative overflow-hidden group border border-outline-variant/5">
          <div class="relative z-10">
            <span class="text-on-surface-variant font-medium text-sm">System Health</span>
            <div class="flex items-center gap-2 mt-4">
              <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
              <span class="font-bold text-on-background">Operational</span>
            </div>
          </div>
          <div class="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-700">
            <span class="material-symbols-outlined text-8xl">verified_user</span>
          </div>
        </div>
      </div>

      <!-- Keys Table Section -->
      <div class="bg-surface-container-low rounded-3xl p-1 border border-outline-variant/5">
        <div class="bg-surface-container-lowest rounded-[calc(1.5rem-4px)] overflow-hidden">
          
          <!-- Table Header / Search -->
          <div class="px-8 py-6 border-b border-surface-container-low flex flex-col sm:flex-row items-center justify-between gap-4">
            <h3 class="font-headline font-bold text-xl">Existing Keys</h3>
            <div class="relative w-full sm:w-64">
              <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/50 text-sm">search</span>
              <input 
                v-model="searchQuery"
                class="pl-10 pr-4 py-2 bg-surface-container-low border-none rounded-full text-sm focus:ring-2 focus:ring-primary/20 w-full outline-none text-on-surface" 
                placeholder="Search keys..." 
                type="text"
              />
            </div>
          </div>

          <!-- List -->
          <div class="divide-y divide-surface-container-low">
            <div v-if="filteredKeys.length === 0" class="px-8 py-12 text-center text-on-surface-variant/40">
              <span class="material-symbols-outlined text-4xl mb-2 opacity-20">key_off</span>
              <p>No API keys found.</p>
            </div>

            <div 
              v-for="key in filteredKeys" 
              :key="key.id"
              class="group px-8 py-6 flex flex-col lg:flex-row lg:items-center justify-between hover:bg-surface-container-low/50 transition-colors duration-300 gap-6"
            >
              <!-- Key Info -->
              <div class="flex items-center gap-6">
                <div class="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary shrink-0">
                  <span class="material-symbols-outlined">key</span>
                </div>
                <div class="space-y-1">
                  <h4 class="font-bold text-on-background">{{ key.name }}</h4>
                  <div class="flex items-center gap-3">
                    <code class="text-[11px] bg-surface-container-high px-3 py-1 rounded-full text-on-surface font-mono tracking-tighter">
                      {{ key.key.substring(0, 10) }}••••••••{{ key.key.substring(key.key.length - 4) }}
                    </code>
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-600">Active</span>
                  </div>
                </div>
              </div>

              <!-- Actions & Metadata -->
              <div class="flex items-center justify-between lg:justify-end gap-12 border-t lg:border-none pt-4 lg:pt-0">
                <div class="text-left lg:text-right">
                  <p class="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/40">Created</p>
                  <p class="text-sm font-medium text-on-surface-variant">{{ formatDate(key.created_at) }}</p>
                </div>
                
                <div class="flex items-center gap-2">
                  <button 
                    @click="copyToClipboard(key.key)"
                    class="p-2 rounded-xl hover:bg-primary/10 text-on-surface-variant transition-all flex items-center gap-2 group-hover:text-primary"
                    title="Copy to clipboard"
                  >
                    <span class="material-symbols-outlined text-[20px]">content_copy</span>
                    <span class="hidden sm:inline text-xs font-semibold">Copy</span>
                  </button>
                  <button 
                    @click="confirmRevoke(key.id)"
                    class="p-2 rounded-xl hover:bg-red-50 text-on-surface-variant hover:text-red-600 transition-all flex items-center gap-2"
                    title="Revoke key"
                  >
                    <span class="material-symbols-outlined text-[20px]">cancel</span>
                    <span class="hidden sm:inline text-xs font-semibold">Revoke</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Bottom Help Text -->
      <p class="mt-8 text-center text-xs text-on-surface-variant/40 max-w-2xl mx-auto leading-relaxed">
        Airelav API keys are secrets. If a key is compromised, revoke it immediately. 
        You can have up to 10 active keys at any given time.
      </p>

    </div>
  </div>
</template>

<style scoped>
.font-headline { font-family: 'Manrope', sans-serif; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e2db; border-radius: 10px; }
</style>