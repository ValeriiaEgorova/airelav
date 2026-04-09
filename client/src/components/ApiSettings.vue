<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const apiKeys = ref([]);
const searchQuery = ref('');

const fetchKeys = async () => {
  try {
    const res = await axios.get(`${API_URL}/api-keys`);
    apiKeys.value = res.data;
  } catch (e) {
    console.error('Error fetching keys:', e);
  }
};

const createKey = async () => {
  const name = prompt("Enter key name (e.g., 'Production App'):");
  if (!name) return;
  try {
    await axios.post(`${API_URL}/api-keys`, null, { params: { name } });
    fetchKeys();
  } catch (e) {
    alert('Failed to create key');
  }
};

const deleteKey = async (id) => {
  if (!confirm('Are you sure you want to revoke this key?')) return;
  try {
    await axios.delete(`${API_URL}/api-keys/${id}`);
    fetchKeys();
  } catch (e) {
    alert('Failed to delete key');
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  alert('Copied to clipboard!');
};

const filteredKeys = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return apiKeys.value.filter(k => 
    (k.name || '').toLowerCase().includes(query) ||
    (k.key || '').toLowerCase().includes(query)
  );
});

const formatDate = (dateStr) => {
  if (!dateStr) return 'Oct 12, 2023';
  return new Date(dateStr).toLocaleDateString('en-US', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
};

onMounted(() => {
  fetchKeys();
});
</script>

<template>
  <div class="pt-8 px-8 pb-12 w-full overflow-y-auto h-screen custom-scrollbar">
    <div class="max-w-6xl mx-auto">
      
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
        <div class="space-y-2">
          <h1 class="text-4xl font-headline font-extrabold text-on-background tracking-tight">API Management</h1>
          <p class="text-on-surface-variant max-w-lg leading-relaxed">
            Securely manage your access keys for the Airelav Data Engine. Use these keys to authenticate your requests via our REST API.
          </p>
        </div>
        <button 
          @click="createKey"
          class="bg-gradient-to-br from-primary to-primary-container text-on-primary px-8 py-4 rounded-full font-bold flex items-center gap-3 shadow-sm hover:opacity-90 active:scale-95 transition-all w-fit"
        >
          <span class="material-symbols-outlined">add</span>
          Create New Key
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <div class="bg-surface-container-low p-6 rounded-2xl flex flex-col justify-between min-h-[140px]">
          <span class="text-on-surface-variant font-medium text-sm">Active Keys</span>
          <div class="flex items-baseline gap-2">
            <span class="text-4xl font-headline font-bold text-primary">{{ apiKeys.length.toString().padStart(2, '0') }}</span>
            <span class="text-on-surface-variant/60 text-xs">/ 10 Limit</span>
          </div>
        </div>
        
        <div class="bg-surface-container-low p-6 rounded-2xl flex flex-col justify-between min-h-[140px] relative overflow-hidden group">
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

      <div class="bg-surface-container-low rounded-lg p-1">
        <div class="bg-surface-container-lowest rounded-[calc(1rem-4px)] overflow-hidden">
          
          <div class="px-8 py-6 border-b border-surface-container-low flex items-center justify-between">
            <h3 class="font-headline font-bold text-xl">Existing Keys</h3>
            <div class="flex gap-4">
              <div class="relative">
                <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/50 text-sm">search</span>
                <input 
                  v-model="searchQuery"
                  class="pl-10 pr-4 py-2 bg-surface-container-low border-none rounded-full text-sm focus:ring-2 focus:ring-primary/20 w-64 outline-none" 
                  placeholder="Search keys..." 
                  type="text"
                />
              </div>
            </div>
          </div>

          <div class="divide-y divide-surface-container-low">
            <div v-if="filteredKeys.length === 0" class="px-8 py-12 text-center text-on-surface-variant/40">
              <p>No API keys found.</p>
            </div>

            <div 
              v-for="key in filteredKeys" 
              :key="key.id"
              class="group px-8 py-6 flex flex-col lg:flex-row lg:items-center justify-between hover:bg-surface-container-low transition-colors duration-300 gap-6"
            >
              <div class="flex items-center gap-6">
                <div class="w-12 h-12 rounded-2xl bg-primary-fixed flex items-center justify-center text-primary shrink-0">
                  <span class="material-symbols-outlined">key</span>
                </div>
                <div class="space-y-1">
                  <h4 class="font-bold text-on-background">{{ key.name }}</h4>
                  <div class="flex items-center gap-3">
                    <code class="text-xs bg-surface-container-low px-2 py-0.5 rounded-full text-on-surface-variant">
                      {{ key.key.substring(0, 8) }}••••••••{{ key.key.substring(key.key.length - 4) }}
                    </code>
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-600">Active</span>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between lg:justify-end gap-12">
                <div class="text-right">
                  <p class="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/40">Created</p>
                  <p class="text-sm font-medium text-on-surface-variant">{{ formatDate(key.created_at) }}</p>
                </div>
                
                <div class="flex items-center gap-2">
                  <button 
                    @click="copyToClipboard(key.key)"
                    class="p-2 rounded-full hover:bg-surface-container-highest text-on-surface-variant transition-colors flex items-center gap-2 group-hover:text-primary"
                  >
                    <span class="material-symbols-outlined text-[20px]">content_copy</span>
                    <span class="text-xs font-semibold">Copy</span>
                  </button>
                  <button 
                    @click="deleteKey(key.id)"
                    class="p-2 rounded-full hover:bg-error-container/20 text-error transition-colors flex items-center gap-2"
                  >
                    <span class="material-symbols-outlined text-[20px]">cancel</span>
                    <span class="text-xs font-semibold">Revoke</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-headline { font-family: 'Manrope', sans-serif; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e2db; border-radius: 10px; }
</style>