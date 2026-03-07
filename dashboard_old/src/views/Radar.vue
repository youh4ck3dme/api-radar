<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-3xl font-bold text-neutral-900">API Radar</h2>
        <p class="text-neutral-500 mt-1">Sledovanie a detekcia shadow API v reálnom čase.</p>
      </div>
      <div class="flex gap-3">
        <button 
          @click="startScanner" 
          class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-blue-200"
        >
          Spustiť Scanner
        </button>
        <button 
          @click="fetchEndpoints" 
          class="bg-white border border-neutral-200 text-neutral-700 px-5 py-2.5 rounded-xl font-bold hover:bg-neutral-50 transition-all"
        >
          Aktualizovať
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-blue-50 border border-blue-100 p-6 rounded-3xl">
        <div class="text-blue-600 text-sm font-bold uppercase tracking-wider mb-2">Celkovo endpointov</div>
        <div class="text-4xl font-black text-blue-900">{{ endpoints.length }}</div>
      </div>
      <div class="bg-red-50 border border-red-100 p-6 rounded-3xl">
        <div class="text-red-600 text-sm font-bold uppercase tracking-wider mb-2">Shadow API</div>
        <div class="text-4xl font-black text-red-900">{{ shadowCount }}</div>
      </div>
      <div class="bg-green-50 border border-green-100 p-6 rounded-3xl">
        <div class="text-green-600 text-sm font-bold uppercase tracking-wider mb-2">Zdokumentované</div>
        <div class="text-4xl font-black text-green-900">{{ endpoints.length - shadowCount }}</div>
      </div>
    </div>

    <!-- Endpoints List -->
    <div class="overflow-hidden border border-neutral-100 rounded-3xl">
      <table class="w-full text-left">
        <thead class="bg-neutral-50 border-b border-neutral-100 text-neutral-500 text-sm uppercase font-bold">
          <tr>
            <th class="px-6 py-4">Metóda</th>
            <th class="px-6 py-4">Endpoint</th>
            <th class="px-6 py-4">Zásahy</th>
            <th class="px-6 py-4">Status</th>
            <th class="px-6 py-4">Posledná aktivita</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100">
          <tr v-for="api in endpoints" :key="api.id" class="hover:bg-neutral-50/50 transition-colors">
            <td class="px-6 py-4">
              <span 
                class="px-2.5 py-1 rounded-lg text-xs font-black uppercase"
                :class="getMethodClass(api.method)"
              >
                {{ api.method }}
              </span>
            </td>
            <td class="px-6 py-4 font-mono text-sm text-neutral-700">{{ api.endpoint }}</td>
            <td class="px-6 py-4 font-bold">{{ api.count }}</td>
            <td class="px-6 py-4">
              <span 
                v-if="api.is_shadow" 
                class="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs font-bold ring-1 ring-red-200"
              >
                SHADOW ALERT
              </span>
              <span 
                v-else 
                class="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold ring-1 ring-green-200"
              >
                DOCUMENTED
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-neutral-400">
              {{ formatDate(api.last_seen) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const endpoints = ref([]);
const loading = ref(false);

const shadowCount = computed(() => endpoints.value.filter(e => e.is_shadow).length);

const fetchEndpoints = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/radar/endpoints');
    endpoints.value = response.data;
  } catch (error) {
    console.error('Radar fetch error:', error);
  } finally {
    loading.value = false;
  }
};

const startScanner = async () => {
  try {
    await axios.post('/api/radar/start');
    alert('Radar scanner bol úspešne spustený na VPS.');
  } catch (error) {
    console.error('Radar start error:', error);
  }
};

const getMethodClass = (method) => {
  const classes = {
    'GET': 'bg-blue-100 text-blue-700',
    'POST': 'bg-green-100 text-green-700',
    'PUT': 'bg-amber-100 text-amber-700',
    'DELETE': 'bg-red-100 text-red-700'
  };
  return classes[method] || 'bg-neutral-100 text-neutral-700';
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleString('sk-SK');
};

onMounted(() => {
  fetchEndpoints();
  setInterval(fetchEndpoints, 10000); // Poll every 10s
});
</script>
