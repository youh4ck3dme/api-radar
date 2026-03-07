<template>
  <Login v-if="!isAuthenticated" @logged-in="isAuthenticated = true" />
  <div v-else class="min-h-screen bg-neutral-50 text-neutral-900 font-sans">
    <!-- Navbar -->
    <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-neutral-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center gap-3">
            <div class="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-200">
              <span class="text-white text-xl">🌐</span>
            </div>
            <h1 class="text-xl font-bold bg-gradient-to-r from-blue-700 to-indigo-600 bg-clip-text text-transparent">
              API Centrum
            </h1>
          </div>
          <div class="hidden md:flex bg-neutral-100 p-1 rounded-xl">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="currentTab = tab.id"
              class="px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-200"
              :class="currentTab === tab.id ? 'bg-white text-blue-700 shadow-sm ring-1 ring-neutral-200' : 'text-neutral-500 hover:text-neutral-700 hover:bg-white/50'"
            >
              {{ tab.name }}
            </button>
          </div>
          <div class="flex items-center gap-4">
            <button class="p-2 text-neutral-400 hover:text-neutral-600 transition-colors">
              <span>🔔</span>
            </button>
            <div class="w-8 h-8 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-700 font-bold text-xs">
              JD
            </div>
            <button @click="logout" class="text-xs text-neutral-400 hover:text-neutral-600 transition-colors px-2 py-1 rounded-lg hover:bg-neutral-100">
              Odhlásiť
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-3xl border border-neutral-200 shadow-xl shadow-neutral-200/50 min-h-[700px] overflow-hidden">
        <transition name="fade" mode="out-in">
          <Dashboard v-if="currentTab === 'dashboard'" />
          <Domains v-else-if="currentTab === 'domains'" />
          <Radar v-else-if="currentTab === 'radar'" />
          <Backups v-else-if="currentTab === 'backups'" />
          <Performance v-else-if="currentTab === 'performance'" />
        </transition>
      </div>
    </main>

    <!-- Mobile Nav -->
    <div class="md:hidden fixed bottom-6 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur-lg border border-neutral-200 shadow-2xl rounded-2xl p-1 flex items-center gap-1 z-50">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        class="p-3 rounded-xl transition-all"
        :class="currentTab === tab.id ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'text-neutral-400'"
      >
        <span class="text-lg">{{ tab.icon }}</span>
      </button>
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
