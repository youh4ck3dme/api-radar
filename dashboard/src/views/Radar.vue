<template>
  <div class="px-4 py-8 sm:px-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-12">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <span class="flex h-3 w-3 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-blue-600"></span>
          </span>
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">Live Scanning Active</span>
        </div>
        <h2 class="text-4xl font-black text-neutral-900 tracking-tightest">API <span class="text-blue-600">Radar</span></h2>
        <p class="text-neutral-400 font-medium mt-1 max-w-md italic">Advanced shadow API detection and traffic analysis engine.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <button 
          @click="toggleSentinel" 
          :class="sentinelActive ? 'bg-emerald-500 text-white' : 'bg-neutral-800 text-neutral-400'"
          class="flex-1 sm:flex-none px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all shadow-xl flex items-center justify-center gap-3 border border-white/5 active:scale-95"
        >
          <span>{{ sentinelActive ? '🛡️' : '🔔' }}</span> 
          {{ sentinelActive ? 'Sentinel Active' : 'Enable Sentinel' }}
        </button>
        <button 
          @click="startScanner" 
          class="flex-1 sm:flex-none bg-neutral-900 hover:bg-black text-white px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-2xl hover:shadow-blue-500/20 active:scale-95 flex items-center justify-center gap-3 border border-white/10"
        >
          <span>🛰️</span> Start Engine
        </button>
        <button 
          @click="fetchEndpoints" 
          class="p-4 rounded-2xl bg-white border border-neutral-200 text-neutral-400 hover:text-blue-600 hover:bg-blue-50 transition-all shadow-sm group"
        >
          <span class="block transition-transform group-hover:rotate-180 duration-500">🔄</span>
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
      <div class="relative group">
        <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div class="relative bg-white border border-neutral-100 p-8 rounded-[2rem] shadow-sm transition-transform hover:-translate-y-1">
          <div class="text-neutral-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">Discovery Rate</div>
          <div class="flex items-end gap-3">
            <div class="text-5xl font-black text-neutral-900 tabular-nums tracking-tighter">{{ endpoints.length }}</div>
            <div class="text-blue-600 font-black text-xs mb-2">NEW</div>
          </div>
        </div>
      </div>
      
      <div class="relative group">
        <div class="absolute -inset-1 bg-gradient-to-r from-red-600 to-rose-500 rounded-[2.5rem] blur opacity-0 group-hover:opacity-20 transition duration-1000" :class="shadowCount > 0 ? 'opacity-10' : ''"></div>
        <div class="relative bg-white border border-neutral-100 p-8 rounded-[2rem] shadow-sm transition-transform hover:-translate-y-1" :class="shadowCount > 0 ? 'border-red-100' : ''">
          <div class="text-neutral-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">Shadow Alerts</div>
          <div class="flex items-end gap-3">
            <div class="text-5xl font-black tabular-nums tracking-tighter" :class="shadowCount > 0 ? 'text-red-600' : 'text-neutral-900'">{{ shadowCount }}</div>
            <div v-if="shadowCount > 0" class="text-red-500 font-black text-xs mb-2 animate-pulse">CRITICAL</div>
          </div>
        </div>
      </div>

      <div class="relative group">
        <div class="absolute -inset-1 bg-gradient-to-r from-emerald-600 to-teal-500 rounded-[2.5rem] blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div class="relative bg-white border border-neutral-100 p-8 rounded-[2rem] shadow-sm transition-transform hover:-translate-y-1">
          <div class="text-neutral-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4">Verified Safe</div>
          <div class="flex items-end gap-3">
            <div class="text-5xl font-black text-neutral-900 tabular-nums tracking-tighter">{{ endpoints.length - shadowCount }}</div>
            <div class="text-emerald-500 font-black text-xs mb-2">SECURE</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Discovery Board -->
    <div class="bg-white border border-neutral-200/60 rounded-[2.5rem] shadow-2xl shadow-neutral-200/40 overflow-hidden relative">
      <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 via-indigo-500 to-cyan-400"></div>
      <div class="px-8 py-6 border-b border-neutral-100 flex items-center justify-between bg-neutral-50/30">
        <h3 class="text-sm font-black text-neutral-900 uppercase tracking-widest">Discovery Log</h3>
        <div class="flex items-center gap-2">
           <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
           <span class="text-[10px] font-bold text-neutral-400 uppercase">Real-time Feed</span>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-neutral-400 text-[10px] uppercase font-black tracking-widest">
              <th class="px-10 py-6">Identity</th>
              <th class="px-10 py-6">Virtual Path</th>
              <th class="px-10 py-6 text-center">Volume</th>
              <th class="px-10 py-6">Classification</th>
              <th class="px-10 py-6 text-right">Integrity</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="api in endpoints" :key="api.id" class="group hover:bg-blue-50/30 transition-all duration-300">
              <td class="px-10 py-6">
                <span 
                   class="inline-block px-3 py-1.5 rounded-xl font-black text-[10px] uppercase tracking-tighter shadow-sm border border-transparent transition-all group-hover:scale-110"
                   :class="getMethodClass(api.method)"
                >
                  {{ api.method }}
                </span>
              </td>
              <td class="px-10 py-6">
                <div class="flex flex-col">
                  <span class="font-mono text-sm font-bold text-neutral-700 group-hover:text-blue-700 transition-colors">{{ api.endpoint }}</span>
                  <span class="text-[10px] text-neutral-300 mt-1 uppercase font-bold tracking-tight">Active Route</span>
                </div>
              </td>
              <td class="px-10 py-6 text-center">
                <div class="inline-flex flex-col items-center">
                   <span class="text-lg font-black text-neutral-900 tabular-nums">{{ api.count }}</span>
                   <span class="text-[9px] text-neutral-400 uppercase font-bold">Requests</span>
                </div>
              </td>
              <td class="px-10 py-6">
                <div v-if="api.is_shadow" class="flex items-center gap-3">
                  <div class="bg-red-50 text-red-600 px-4 py-2 rounded-2xl flex items-center gap-2 ring-1 ring-red-100 shadow-sm shadow-red-100/50">
                    <span class="relative flex h-2 w-2">
                       <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                       <span class="relative inline-flex rounded-full h-2 w-2 bg-red-600"></span>
                    </span>
                    <span class="text-[10px] font-black uppercase tracking-wider">Shadow Alert</span>
                  </div>
                </div>
                <div v-else class="flex items-center gap-3">
                  <div class="bg-emerald-50 text-emerald-600 px-4 py-2 rounded-2xl flex items-center gap-2 ring-1 ring-emerald-100">
                    <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
                    <span class="text-[10px] font-black uppercase tracking-wider">Documented</span>
                  </div>
                </div>
              </td>
              <td class="px-10 py-6 text-right">
                <div class="flex flex-col items-end">
                   <div class="w-24 h-1.5 bg-neutral-100 rounded-full overflow-hidden mb-1.5">
                      <div 
                        class="h-full rounded-full transition-all duration-1000" 
                        :class="api.is_shadow ? 'bg-red-400 w-1/4' : 'bg-emerald-400 w-full'"
                      ></div>
                   </div>
                   <span class="text-[10px] font-bold text-neutral-400">{{ api.is_shadow ? 'Low Trust' : 'High Integrity' }}</span>
                </div>
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
const shadowCount = ref(0);
const sentinelActive = ref(false);

const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
};

const toggleSentinel = async () => {
    if (sentinelActive.value) {
        sentinelActive.value = false;
        return;
    }

    try {
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            alert('Notification permission denied');
            return;
        }

        const registration = await navigator.serviceWorker.ready;
        const vapidRes = await api.get('/radar/vapid-key');
        const publicKey = vapidRes.data.publicKey;

        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicKey)
        });

        const subObj = subscription.toJSON();
        await api.post('/radar/subscribe', {
            endpoint: subObj.endpoint,
            keys: {
                p256dh: subObj.keys.p256dh,
                auth: subObj.keys.auth
            }
        });

        sentinelActive.value = true;
        console.log('Sentinel Web Push Subscribed');
    } catch (err) {
        console.error('Sentinel activation failed:', err);
        alert('Failed to activate Sentinel alerts. Ensure your browser supports Web Push and PWA features.');
    }
};

const fetchEndpoints = async () => {
  loading.value = true;
  try {
    const response = await api.get('/radar/endpoints');
    endpoints.value = response.data;
    // Update shadow count reactively
    shadowCount.value = endpoints.value.filter(e => e.is_shadow).length;
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
