<template>
  <div class="p-6">
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Správa Domén</h2>
        <p class="mt-2 text-sm text-gray-500">Zoznam a správa vašich registrovaných domén cez Websupport API.</p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="fetchDomains" 
          class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-all shadow-sm"
          :disabled="loading"
        >
          <span :class="{ 'animate-spin': loading }">🔄</span>
          {{ loading ? 'Načítavam...' : 'Obnoviť' }}
        </button>
        <button class="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-xl text-sm font-semibold text-white hover:bg-blue-700 transition-all shadow-lg shadow-blue-200">
          <span>+</span>
          Pridať doménu
        </button>
      </div>
    </header>

    <div v-if="loading && !domains.length" class="flex flex-col items-center justify-center py-20">
      <div class="w-12 h-12 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
      <p class="mt-4 text-gray-500 font-medium">Načítavam vaše domény...</p>
    </div>

    <div v-else-if="!domains.length" class="bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200 py-20 px-6 text-center">
      <div class="bg-white w-16 h-16 rounded-2xl shadow-sm flex items-center justify-center mx-auto mb-4 text-2xl">
        🌐
      </div>
      <h3 class="text-lg font-bold text-gray-900">Žiadne domény</h3>
      <p class="mt-2 text-sm text-gray-500 max-w-xs mx-auto">Zatiaľ ste nepridali žiadne domény alebo neboli nájdené v systéme Websupport.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="d in domains" 
        :key="d.id" 
        class="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:shadow-blue-900/5 hover:-translate-y-1 transition-all duration-300 overflow-hidden"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <div class="bg-blue-50 text-blue-600 p-2.5 rounded-xl group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
              <span class="text-xl">🔗</span>
            </div>
            <div class="flex flex-col items-end">
              <span class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700">Active</span>
            </div>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-1 truncate">{{ d.name }}</h3>
          <p class="text-sm text-gray-500 line-clamp-2 min-h-[40px]">{{ d.description || 'Žiadny popis nie je k dispozícii.' }}</p>
        </div>
        <div class="px-6 py-4 bg-gray-50/50 border-t border-gray-50 flex items-center justify-between">
          <button class="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors uppercase tracking-widest">Detail</button>
          <div class="flex items-center gap-2">
            <button class="p-1.5 text-gray-400 hover:text-red-600 transition-colors" title="Zmazať">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/api";

const domains = ref([]);
const loading = ref(false);

const fetchDomains = async () => {
  loading.value = true;
  try {
    const res = await api.get("/domains");
    // Handle both array and object responses based on Websupport API structure
    domains.value = res.data.domains || (Array.isArray(res.data) ? res.data : []);
  } catch (err) {
    console.error(err);
    // Silent fail if it's just a connection error for demo
  } finally {
    loading.value = false;
  }
};

onMounted(fetchDomains);
</script>
