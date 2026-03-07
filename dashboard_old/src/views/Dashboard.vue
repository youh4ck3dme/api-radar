<template>
  <div class="p-6">
    <HeroCard />

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div v-for="stat in stats" :key="stat.label" class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <p class="text-sm font-medium text-gray-500 uppercase tracking-wider">{{ stat.label }}</p>
        <div class="mt-2 flex items-baseline">
          <p class="text-4xl font-bold text-gray-900">{{ stat.value }}</p>
          <p v-if="stat.subValue" class="ml-2 text-sm font-medium text-green-600">{{ stat.subValue }}</p>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="px-6 py-5 border-b border-gray-50 flex items-center justify-between bg-gray-50/50">
        <h3 class="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <button class="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors">View all</button>
      </div>
      <ul class="divide-y divide-gray-50">
        <li v-for="activity in recentActivity" :key="activity.id" class="px-6 py-4 hover:bg-gray-50/50 transition-colors cursor-pointer">
          <div class="flex items-center space-x-4">
            <div :class="activity.iconClass" class="p-2 rounded-xl">
              <span class="text-lg">{{ activity.icon }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ activity.title }}</p>
              <p class="text-xs text-gray-500 mt-0.5">{{ activity.time }}</p>
            </div>
            <div class="flex-shrink-0">
              <span :class="activity.statusClass" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ activity.status }}
              </span>
            </div>
          </div>
        </li>
      </ul>
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
