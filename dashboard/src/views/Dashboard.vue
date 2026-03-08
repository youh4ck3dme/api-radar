<template>
  <div class="px-4 py-8 sm:px-8">
    <!-- Hero Section -->
    <div class="mb-12">
      <h2 class="text-4xl font-black text-neutral-900 tracking-tightest mb-2">Systems <span class="text-blue-600">Overview</span></h2>
      <p class="text-neutral-400 font-medium italic">Unified control center for your domains, SSL, and API traffic.</p>
    </div>

    <HeroCard class="mb-12 shadow-2xl shadow-blue-500/10 rounded-[2.5rem] overflow-hidden border border-white/20" />

    <!-- Performance & Scale Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
      <div v-for="stat in stats" :key="stat.label" class="group relative">
        <div class="absolute -inset-1 bg-gradient-to-br from-neutral-200 to-white rounded-[2.5rem] blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
        <div class="relative bg-white p-8 rounded-[2rem] border border-neutral-100 shadow-sm transition-all group-hover:-translate-y-1 group-hover:shadow-xl">
          <div class="flex items-center justify-between mb-4">
            <p class="text-[10px] font-black text-neutral-400 uppercase tracking-[0.3em]">{{ stat.label }}</p>
             <div class="w-8 h-8 rounded-xl bg-neutral-50 flex items-center justify-center text-xs group-hover:bg-blue-600 group-hover:text-white transition-colors duration-500">
               {{ stat.label.includes('Domain') ? '🌐' : stat.label.includes('Status') ? '🛰️' : '🔔' }}
             </div>
          </div>
          <div class="flex items-baseline gap-3">
            <p class="text-5xl font-black text-neutral-900 tabular-nums tracking-tighter">{{ stat.value }}</p>
            <p v-if="stat.subValue" class="text-[10px] font-black text-blue-600 uppercase tracking-widest bg-blue-50 px-2 py-0.5 rounded-full">{{ stat.subValue }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Ledger -->
    <div class="bg-white rounded-[2.5rem] border border-neutral-200/60 shadow-2xl shadow-neutral-200/40 overflow-hidden relative">
      <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-neutral-800 to-neutral-400"></div>
      <div class="px-8 py-6 border-b border-neutral-100 flex items-center justify-between bg-neutral-50/30">
        <h3 class="text-sm font-black text-neutral-900 uppercase tracking-widest">Global Activity Ledger</h3>
        <button class="text-xs font-black text-blue-600 hover:text-blue-800 transition-colors uppercase tracking-widest px-4 py-2 rounded-xl hover:bg-blue-50">View Expanded Meta</button>
      </div>
      <ul class="divide-y divide-neutral-100">
        <li v-for="activity in recentActivity" :key="activity.id" class="group px-8 py-6 hover:bg-neutral-50/50 transition-all cursor-pointer">
          <div class="flex items-center space-x-6">
            <div :class="activity.iconClass" class="w-14 h-14 rounded-2xl flex items-center justify-center shadow-sm transition-transform group-hover:scale-110 duration-500">
              <span class="text-2xl">{{ activity.icon }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                 <p class="text-sm font-black text-neutral-900 uppercase tracking-tight">{{ activity.title }}</p>
                 <span class="w-1 h-1 rounded-full bg-neutral-300"></span>
                 <p class="text-[10px] text-neutral-400 font-bold uppercase tracking-widest">{{ activity.time }}</p>
              </div>
              <p class="text-xs text-neutral-400 font-medium italic">Authorized system operation successfully recorded.</p>
            </div>
            <div class="flex-shrink-0">
              <span :class="activity.statusClass" class="inline-flex items-center px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm ring-1 ring-black/5">
                {{ activity.status }}
              </span>
            </div>
          </div>
        </li>
      </ul>
      <div v-if="recentActivity.length === 0" class="p-20 text-center">
         <div class="text-neutral-200 text-5xl mb-4">📜</div>
         <p class="text-neutral-400 font-black uppercase tracking-widest text-xs">No entries in the ledger yet</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/api";
import HeroCard from "../components/HeroCard.vue";

const stats = ref([
  { label: 'Total Domains', value: '0', subValue: 'Loading...' },
  { label: 'System Status', value: '...', subValue: 'Checking...' },
  { label: 'Recent Events', value: '0', subValue: 'Last 7 days' }
]);

const recentActivity = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchDashboardData = async () => {
  try {
    loading.value = true;
    const [statsRes, activitiesRes] = await Promise.all([
      api.get("/dashboard/stats"),
      api.get("/dashboard/activities")
    ]);

    // Update stats
    stats.value[0].value = statsRes.data.user_stats.total_domains.toString();
    stats.value[1].value = statsRes.data.system_health.database === 'online' ? 'Online' : 'Offline';
    stats.value[1].subValue = `API: ${statsRes.data.system_health.websupport_api}`;
    stats.value[2].value = statsRes.data.user_stats.recent_activities.toString();

    // Update activities
    recentActivity.value = activitiesRes.data.activities.map((a, index) => ({
      id: index,
      title: a.action,
      time: new Date(a.timestamp).toLocaleString(),
      status: 'Info',
      icon: '📝',
      iconClass: 'bg-blue-50 text-blue-600',
      statusClass: 'bg-blue-100 text-blue-800'
    }));
  } catch (err) {
    console.error("Failed to fetch dashboard data:", err);
    error.value = "Failed to load dashboard data. Please try again later.";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchDashboardData);
</script>
