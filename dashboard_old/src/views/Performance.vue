<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Metriky výkonu (Performance)</h2>
      <button 
        @click="fetchPerformance" 
        :disabled="loading"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors disabled:opacity-50"
      >
        <span v-if="loading">Aktualizujem...</span>
        <span v-else>Obnoviť dáta</span>
      </button>
    </div>

    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white border p-4 rounded shadow-sm">
        <div class="text-sm text-gray-500 uppercase font-bold mb-1">Celkový počet volaní</div>
        <div class="text-3xl font-bold">{{ stats.count }}</div>
      </div>
      <div class="bg-white border p-4 rounded shadow-sm">
        <div class="text-sm text-gray-500 uppercase font-bold mb-1">Priemerná latencia</div>
        <div class="text-3xl font-bold text-blue-600">{{ stats.average_latency_ms }} ms</div>
      </div>
      <div class="bg-white border p-4 rounded shadow-sm">
        <div class="text-sm text-gray-500 uppercase font-bold mb-1">Stavové kódy</div>
        <div class="flex flex-wrap gap-2 mt-1">
          <span 
            v-for="(count, code) in stats.status_distribution" 
            :key="code"
            class="px-2 py-1 rounded text-xs font-bold"
            :class="code.startsWith('2') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
          >
            {{ code }}: {{ count }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="stats && stats.recent_metrics && stats.recent_metrics.length" class="mt-4">
      <h3 class="text-lg font-medium mb-3">Posledné záznamy</h3>
      <div class="overflow-x-auto border rounded">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="p-2 border-b text-left">Endpoint</th>
              <th class="p-2 border-b text-left">Metóda</th>
              <th class="p-2 border-b text-left">Čas (ms)</th>
              <th class="p-2 border-b text-left">Status</th>
              <th class="p-2 border-b text-left">Kedy</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, idx) in stats.recent_metrics.slice().reverse()" :key="idx" class="hover:bg-gray-50">
              <td class="p-2 border-b font-mono text-xs">{{ m.path }}</td>
              <td class="p-2 border-b">
                <span class="px-1 py-0.5 rounded font-bold text-[10px]" :class="getMethodClass(m.method)">
                  {{ m.method }}
                </span>
              </td>
              <td class="p-2 border-b">{{ (m.latency * 1000).toFixed(2) }}</td>
              <td class="p-2 border-b">
                <span :class="m.status < 400 ? 'text-green-600' : 'text-red-600'">{{ m.status }}</span>
              </td>
              <td class="p-2 border-b text-gray-500">{{ formatTime(m.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else-if="!loading" class="text-gray-500 text-center py-10 bg-gray-50 border rounded border-dashed">
      Dáta výkonu ešte nie sú k dispozícii. Použite aplikáciu a potom refreshnite.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/api";

const stats = ref(null);
const loading = ref(false);

const fetchPerformance = async () => {
  loading.value = true;
  try {
    const res = await api.get("/performance/stats");
    stats.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const getMethodClass = (method) => {
  const map = {
    'GET': 'bg-blue-100 text-blue-700',
    'POST': 'bg-green-100 text-green-700',
    'DELETE': 'bg-red-100 text-red-700',
    'PUT': 'bg-yellow-100 text-yellow-700',
    'PATCH': 'bg-purple-100 text-purple-700'
  };
  return map[method] || 'bg-gray-100 text-gray-700';
};

const formatTime = (ts) => {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString('sk-SK');
};

onMounted(fetchPerformance);
</script>
