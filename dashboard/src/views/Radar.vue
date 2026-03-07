<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-3xl font-bold text-neutral-900 tracking-tight">API Radar Pro</h2>
        <p class="text-neutral-500 mt-1">Real-time monitoring and shadow API detection engine.</p>
      </div>
      <div class="flex gap-3">
        <button 
          @click="startScanner" 
          class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-2xl font-bold transition-all shadow-lg shadow-blue-200 active:scale-95 flex items-center gap-2"
        >
          <span>🛰️</span> Spustiť Scanner
        </button>
        <button 
          @click="fetchEndpoints" 
          class="bg-white border border-neutral-200 text-neutral-700 px-5 py-2.5 rounded-2xl font-bold hover:bg-neutral-50 transition-all flex items-center gap-2"
        >
          <span>🔄</span> Refresh
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white border border-neutral-200 p-6 rounded-3xl shadow-sm">
        <div class="text-neutral-400 text-xs font-black uppercase tracking-widest mb-2">Total Endpoints</div>
        <div class="text-4xl font-black text-neutral-900 tabular-nums">{{ endpoints.length }}</div>
      </div>
      <div class="bg-red-50 border border-red-100 p-6 rounded-3xl shadow-sm">
        <div class="text-red-500 text-xs font-black uppercase tracking-widest mb-2">Shadow APIs</div>
        <div class="text-4xl font-black text-red-600 tabular-nums">{{ shadowCount }}</div>
      </div>
      <div class="bg-green-50 border border-green-100 p-6 rounded-3xl shadow-sm">
        <div class="text-green-500 text-xs font-black uppercase tracking-widest mb-2">Documented</div>
        <div class="text-4xl font-black text-green-600 tabular-nums">{{ endpoints.length - shadowCount }}</div>
      </div>
    </div>

    <!-- Endpoints List -->
    <div class="bg-white border border-neutral-200 rounded-3xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-neutral-50 border-b border-neutral-100 text-neutral-400 text-[10px] uppercase font-black tracking-widest">
            <tr>
              <th class="px-8 py-5">Method</th>
              <th class="px-8 py-5">Endpoint Path</th>
              <th class="px-8 py-5 text-center">Hits</th>
              <th class="px-8 py-5">Security Status</th>
              <th class="px-8 py-5">Last Observed</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="api in endpoints" :key="api.id" class="group hover:bg-neutral-50/50 transition-colors">
              <td class="px-8 py-5">
                <span 
                  class="px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider shadow-sm"
                  :class="getMethodClass(api.method)"
                >
                  {{ api.method }}
                </span>
              </td>
              <td class="px-8 py-5 font-mono text-sm text-neutral-600 group-hover:text-blue-600 transition-colors">{{ api.endpoint }}</td>
              <td class="px-8 py-5 text-center">
                <span class="bg-neutral-100 text-neutral-700 font-bold px-3 py-1 rounded-full text-xs tabular-nums">
                  {{ api.count }}
                </span>
              </td>
              <td class="px-8 py-5">
                <div v-if="api.is_shadow" class="flex items-center gap-2">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                  </span>
                  <span class="text-red-600 text-xs font-bold uppercase tracking-tight">Shadow Alert</span>
                </div>
                <div v-else class="flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-green-500"></span>
                  <span class="text-green-600 text-xs font-bold uppercase tracking-tight">Verified</span>
                </div>
              </td>
              <td class="px-8 py-5 text-xs text-neutral-400 font-medium">
                {{ formatDate(api.last_seen) }}
              </td>
            </tr>
            <tr v-if="endpoints.length === 0">
              <td colspan="5" class="px-8 py-20 text-center">
                <div class="text-neutral-300 text-4xl mb-4">🛸</div>
                <div class="text-neutral-400 font-medium">No API activity detected yet.</div>
                <div class="text-neutral-300 text-xs mt-1">Start the scanner to begin discovery.</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
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
    alert('Radar scanner bol úspešne spustený v pozadí.');
  } catch (error) {
    console.error('Radar start error:', error);
  }
};

const getMethodClass = (method) => {
  const classes = {
    'GET': 'bg-blue-500 text-white',
    'POST': 'bg-emerald-500 text-white',
    'PUT': 'bg-violet-500 text-white',
    'DELETE': 'bg-rose-500 text-white',
    'PATCH': 'bg-amber-500 text-white'
  };
  return classes[method] || 'bg-neutral-500 text-white';
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'Never';
  const date = new Date(dateStr);
  return new Intl.RelativeTimeFormat('sk', { numeric: 'auto' }).format(
    Math.round((date - new Date()) / (1000 * 60)), 'minute'
  );
  // Simpler for now:
  // return date.toLocaleTimeString('sk-SK');
};

onMounted(() => {
  fetchEndpoints();
  // Auto-refresh every 5 seconds
  const interval = setInterval(fetchEndpoints, 5000);
  return () => clearInterval(interval);
});
</script>
