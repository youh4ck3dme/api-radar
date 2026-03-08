<template>
  <div class="px-4 py-8 sm:px-8">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-12">
      <div>
        <h2 class="text-4xl font-black text-neutral-900 tracking-tightest mb-2">Domain <span class="text-blue-600">Assets</span></h2>
        <p class="text-neutral-400 font-medium italic">Secure management of your global domain portfolio via Websupport.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <button 
          @click="fetchDomains" 
          class="p-4 rounded-2xl bg-white border border-neutral-200 text-neutral-400 hover:text-blue-600 hover:bg-blue-50 transition-all shadow-sm group"
          :disabled="loading"
        >
          <span class="block transition-transform group-hover:rotate-180 duration-500" :class="{ 'animate-spin': loading }">🔄</span>
        </button>
        <button class="flex-1 sm:flex-none bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-2xl shadow-blue-500/20 active:scale-95 flex items-center justify-center gap-3 border border-white/10">
          <span>+</span>
          Register Asset
        </button>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading && !domains.length" class="flex flex-col items-center justify-center py-32">
      <div class="relative w-20 h-20">
         <div class="absolute inset-0 border-4 border-blue-50 rounded-full"></div>
         <div class="absolute inset-0 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p class="mt-8 text-neutral-400 font-black uppercase tracking-[0.3em] text-[10px]">Syncing with Registry...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!domains.length" class="bg-white rounded-[2.5rem] border-2 border-dashed border-neutral-100 py-32 px-6 text-center">
      <div class="bg-neutral-50 w-24 h-24 rounded-3xl shadow-sm flex items-center justify-center mx-auto mb-8 text-4xl grayscale opacity-50">
        🌐
      </div>
      <h3 class="text-xl font-black text-neutral-900 tracking-tight uppercase">Registry Empty</h3>
      <p class="mt-2 text-sm text-neutral-400 font-medium max-w-xs mx-auto italic">No domain assets were discovered in the connected account.</p>
    </div>

    <!-- Domain Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div 
        v-for="d in domains" 
        :key="d.id" 
        class="group relative"
      >
        <div class="absolute -inset-1 bg-gradient-to-br from-blue-600 to-indigo-500 rounded-[2.5rem] blur opacity-0 group-hover:opacity-10 transition duration-500"></div>
        <div class="relative bg-white rounded-[2rem] border border-neutral-100 shadow-sm hover:shadow-2xl transition-all duration-500 overflow-hidden hover:-translate-y-2">
          <div class="p-8">
            <div class="flex items-start justify-between mb-8">
              <div class="bg-neutral-50 text-neutral-400 p-3 rounded-2xl group-hover:bg-blue-600 group-hover:text-white transition-all duration-500 shadow-inner">
                <span class="text-2xl">🔗</span>
              </div>
              <div class="flex flex-col items-end">
                <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-emerald-50 text-emerald-600 ring-1 ring-emerald-100 shadow-sm shadow-emerald-50">Live</span>
              </div>
            </div>
            <h3 class="text-xl font-black text-neutral-900 mb-2 truncate group-hover:text-blue-600 transition-colors">{{ d.name }}</h3>
            <p class="text-xs text-neutral-400 font-medium line-clamp-2 min-h-[32px] italic leading-relaxed">{{ d.description || 'Verified domain asset with active SSL monitoring.' }}</p>
          </div>
          <div class="px-8 py-5 bg-neutral-50/50 border-t border-neutral-50 flex items-center justify-between">
            <button class="text-[10px] font-black text-blue-600 hover:text-blue-800 transition-colors uppercase tracking-widest px-4 py-2 rounded-xl hover:bg-white shadow-sm ring-1 ring-black/5 opacity-0 group-hover:opacity-100 -translate-x-4 group-hover:translate-x-0 transition-all duration-500">Configure</button>
            <div class="flex items-center gap-4">
              <button class="w-8 h-8 rounded-full flex items-center justify-center text-neutral-300 hover:text-red-600 hover:bg-red-50 transition-all" title="Archive Asset">
                🗑️
              </button>
            </div>
          </div>
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
