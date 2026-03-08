<template>
  <div class="px-4 py-8 sm:px-8">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-12">
      <div>
        <h2 class="text-4xl font-black text-neutral-900 tracking-tightest mb-2">Network <span class="text-blue-600">Health</span></h2>
        <p class="text-neutral-400 font-medium italic">High-precision latency tracking and system-wide throughput analysis.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <button 
          @click="fetchPerformance" 
          :disabled="loading"
          class="flex-1 sm:flex-none flex items-center justify-center gap-3 px-8 py-4 bg-neutral-900 border border-white/10 rounded-2xl font-black text-xs text-white uppercase tracking-widest hover:bg-black transition-all shadow-2xl active:scale-95 disabled:opacity-50"
        >
          <span v-if="loading" class="animate-spin text-lg">⚡</span>
          <span v-else>Recalibrate Engine</span>
        </button>
      </div>
    </header>

    <!-- Performance Stats -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
      <div class="relative group">
        <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div class="relative bg-white border border-neutral-100 p-8 rounded-[2rem] shadow-sm transition-transform hover:-translate-y-1">
          <div class="text-neutral-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">Total Interactions</div>
          <div class="flex items-end gap-3">
            <div class="text-5xl font-black text-neutral-900 tabular-nums tracking-tighter">{{ stats.count }}</div>
            <div class="text-blue-600 font-black text-xs mb-2">HITS</div>
          </div>
        </div>
      </div>

      <div class="relative group">
        <div class="absolute -inset-1 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div class="relative bg-white border border-neutral-100 p-8 rounded-[2rem] shadow-sm transition-transform hover:-translate-y-1">
          <div class="text-neutral-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">System Latency</div>
          <div class="flex items-end gap-3">
            <div class="text-5xl font-black text-blue-600 tabular-nums tracking-tighter">{{ stats.average_latency_ms }}</div>
            <div class="text-blue-400 font-black text-xs mb-2">MS</div>
          </div>
        </div>
      </div>

      <div class="relative group">
        <div class="absolute -inset-1 bg-gradient-to-r from-emerald-600 to-teal-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div class="relative bg-white border border-neutral-100 p-8 rounded-[2rem] shadow-sm transition-transform hover:-translate-y-1">
          <div class="text-neutral-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">Status Map</div>
          <div class="flex flex-wrap gap-2 mt-2">
            <span 
              v-for="(count, code) in stats.status_distribution" 
              :key="code"
              class="px-3 py-1.5 rounded-xl text-[10px] font-black tracking-widest shadow-sm border border-transparent"
              :class="code.startsWith('2') ? 'bg-emerald-50 text-emerald-600 ring-1 ring-emerald-100' : 'bg-red-50 text-red-600 ring-1 ring-red-100'"
            >
              {{ code }} • {{ count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Metrics Feed -->
    <div v-if="stats && stats.recent_metrics && stats.recent_metrics.length" class="bg-white border border-neutral-200/60 rounded-[2.5rem] shadow-2xl shadow-neutral-200/40 overflow-hidden relative">
      <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-blue-900"></div>
      <div class="px-8 py-6 border-b border-neutral-100 flex items-center justify-between bg-neutral-50/30">
        <h3 class="text-sm font-black text-neutral-900 uppercase tracking-widest">Network Telemetry</h3>
        <div class="flex items-center gap-2">
           <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
           <span class="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Active Link</span>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-neutral-400 text-[10px] uppercase font-black tracking-widest">
              <th class="px-10 py-6">Link Endpoint</th>
              <th class="px-10 py-6">Protocol</th>
              <th class="px-10 py-6 text-center">Delay</th>
              <th class="px-10 py-6">Response</th>
              <th class="px-10 py-6 text-right">Synchronization</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="(m, idx) in stats.recent_metrics.slice().reverse()" :key="idx" class="group hover:bg-neutral-50/50 transition-all duration-300">
              <td class="px-10 py-6">
                <div class="flex flex-col">
                  <span class="font-mono text-sm font-bold text-neutral-700 group-hover:text-blue-600 transition-colors">{{ m.path }}</span>
                  <span class="text-[10px] text-neutral-300 mt-1 uppercase font-bold tracking-tight">Virtual Socket</span>
                </div>
              </td>
              <td class="px-10 py-6">
                 <span class="px-3 py-1.5 rounded-xl font-black text-[10px] uppercase tracking-tighter" :class="getMethodClass(m.method)">
                  {{ m.method }}
                </span>
              </td>
              <td class="px-10 py-6 text-center">
                <span class="text-sm font-bold text-neutral-900 tabular-nums">{{ (m.latency * 1000).toFixed(2) }} <span class="text-[10px] text-neutral-400">ms</span></span>
              </td>
              <td class="px-10 py-6">
                 <span 
                    class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ring-1"
                    :class="m.status < 400 ? 'bg-emerald-50 text-emerald-600 ring-emerald-100' : 'bg-red-50 text-red-600 ring-red-100'"
                 >
                    HTTP {{ m.status }}
                 </span>
              </td>
              <td class="px-10 py-6 text-right text-[10px] text-neutral-400 font-bold uppercase tracking-widest">
                {{ formatTime(m.timestamp) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else-if="!loading" class="py-32 bg-white rounded-[2.5rem] border-2 border-dashed border-neutral-100 px-6 text-center shadow-sm">
      <div class="text-neutral-200 text-6xl mb-6 grayscale opacity-30">📊</div>
      <h3 class="text-xl font-black text-neutral-900 tracking-tight uppercase">Telemetry Vacant</h3>
      <p class="mt-2 text-sm text-neutral-400 font-medium max-w-xs mx-auto italic">Activate endpoints to stream real-time performance data to the engine.</p>
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
