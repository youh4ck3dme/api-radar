<template>
  <Login v-if="!isAuthenticated" @logged-in="isAuthenticated = true" />
  <div v-else class="min-h-screen bg-[#f8fafc] text-neutral-900 font-sans selection:bg-blue-100 selection:text-blue-900">
    <!-- Navbar -->
    <nav class="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-neutral-200/60">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-20 items-center">
          <div class="flex items-center gap-4 group cursor-pointer">
            <div class="relative w-12 h-12 flex items-center justify-center">
               <div class="absolute inset-0 bg-blue-600 rounded-2xl rotate-6 transition-transform group-hover:rotate-12 group-hover:scale-110"></div>
               <div class="relative bg-white p-2.5 rounded-2xl shadow-lg border border-blue-50">
                 <img src="/favicon.png" alt="Logo" class="w-6 h-6 object-contain" />
               </div>
            </div>
            <div>
              <h1 class="text-xl font-black bg-gradient-to-br from-neutral-900 to-neutral-600 bg-clip-text text-transparent tracking-tight">
                API Radar <span class="text-blue-600 font-black">Pro</span>
              </h1>
              <p class="text-[10px] uppercase font-black tracking-widest text-neutral-400 mt-0.5">Advanced Discovery</p>
            </div>
          </div>
          
          <!-- Desktop Nav -->
          <div class="hidden lg:flex bg-neutral-100/80 p-1.5 rounded-2xl border border-neutral-200/50 backdrop-blur-sm">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="currentTab = tab.id"
              class="px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center gap-2.5"
              :class="currentTab === tab.id ? 'bg-white text-blue-700 shadow-md shadow-blue-500/10 ring-1 ring-neutral-200/50' : 'text-neutral-500 hover:text-neutral-900 hover:bg-white/40'"
            >
              <span class="text-lg leading-none">{{ tab.icon }}</span>
              {{ tab.name }}
            </button>
          </div>

          <div class="flex items-center gap-5">
            <div class="hidden md:flex flex-col items-end">
              <span class="text-xs font-black text-neutral-900">John Doe</span>
              <span class="text-[10px] font-bold text-neutral-400">Admin Account</span>
            </div>
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-200 border-2 border-white flex items-center justify-center text-white font-black text-xs ring-4 ring-neutral-50">
              JD
            </div>
            <button @click="logout" class="p-2.5 rounded-xl bg-neutral-100/80 text-neutral-400 hover:text-red-600 hover:bg-red-50 transition-all border border-neutral-200/50">
              <span class="text-xl leading-none">🚪</span>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <div class="glass-card rounded-[2.5rem] p-4 min-h-[750px] overflow-hidden">
        <transition name="fade" mode="out-in">
          <Dashboard v-if="currentTab === 'dashboard'" />
          <Domains v-else-if="currentTab === 'domains'" />
          <Radar v-else-if="currentTab === 'radar'" />
          <Backups v-else-if="currentTab === 'backups'" />
          <Performance v-else-if="currentTab === 'performance'" />
        </transition>
      </div>
    </main>

    <!-- Mobile Navigation Bar -->
    <div class="lg:hidden fixed bottom-8 left-1/2 -translate-x-1/2 w-[90%] max-w-sm z-50">
      <div class="bg-white/80 backdrop-blur-2xl border border-white/40 shadow-2xl rounded-[2rem] p-2 flex items-center justify-between ring-1 ring-black/5">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="currentTab = tab.id"
          class="relative p-4 rounded-2xl transition-all duration-500"
          :class="currentTab === tab.id ? 'bg-blue-600 text-white shadow-xl shadow-blue-500/40 scale-110 -translate-y-2' : 'text-neutral-400 hover:text-neutral-600'"
        >
          <span class="text-xl leading-none">{{ tab.icon }}</span>
          <div v-if="currentTab === tab.id" class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-white rounded-full"></div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import Dashboard from "./views/Dashboard.vue";
import Domains from "./views/Domains.vue";
import Radar from "./views/Radar.vue";
import Backups from "./views/Backups.vue";
import Performance from "./views/Performance.vue";
import Login from "./views/Login.vue";

const isAuthenticated = ref(!!localStorage.getItem('access_token'));

const logout = () => {
  localStorage.removeItem('access_token');
  isAuthenticated.value = false;
};

const currentTab = ref('dashboard');
const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: '📊' },
  { id: 'domains', name: 'Domény', icon: '🌐' },
  { id: 'radar', name: 'Radar', icon: '🛰️' },
  { id: 'backups', name: 'Zálohy', icon: '📦' },
  { id: 'performance', name: 'Výkon', icon: '⚡' }
];
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
