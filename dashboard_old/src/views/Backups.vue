<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Záloha systému (Backupy)</h2>
      <button 
        @click="createBackup" 
        :disabled="creating"
        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors disabled:opacity-50"
      >
        <span v-if="creating">Vytváram...</span>
        <span v-else>Vytvoriť novú zálohu</span>
      </button>
    </div>

    <div v-if="loading" class="text-gray-500">Načítavam zoznam záloh...</div>
    
    <div v-else>
      <div v-if="backups.length === 0" class="bg-gray-50 border border-dashed border-gray-300 p-8 text-center text-gray-500 rounded">
        Zatiaľ neboli vytvorené žiadne zálohy.
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-gray-100 text-left">
              <th class="p-2 border">Súbor</th>
              <th class="p-2 border">Veľkosť</th>
              <th class="p-2 border">Dátum úpravy</th>
              <th class="p-2 border text-right">Akcie</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in backups" :key="b.filename" class="hover:bg-gray-50">
              <td class="p-2 border font-mono text-sm">{{ b.filename }}</td>
              <td class="p-2 border">{{ formatSize(b.size) }}</td>
              <td class="p-2 border text-sm text-gray-600">{{ formatDate(b.modified) }}</td>
              <td class="p-2 border text-right">
                <button 
                  @click="deleteBackup(b.filename)"
                  class="text-red-600 hover:text-red-800 font-medium px-2 py-1"
                >
                  Zmazať
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/api";

const backups = ref([]);
const loading = ref(false);
const creating = ref(false);

const fetchBackups = async () => {
  loading.value = true;
  try {
    const res = await api.get("/backups");
    backups.value = res.data;
  } catch (err) {
    console.error(err);
    alert("Nepodarilo sa načítať zálohy.");
  } finally {
    loading.value = false;
  }
};

const createBackup = async () => {
  creating.value = true;
  try {
    await api.post("/backups/create");
    await fetchBackups();
  } catch (err) {
    console.error(err);
    alert("Vytváranie zálohy zlyhalo.");
  } finally {
    creating.value = false;
  }
};

const deleteBackup = async (filename) => {
  if (!confirm(`Naozaj chcete zmazať zálohu ${filename}?`)) return;
  
  try {
    await api.delete(`/backups/${filename}`);
    await fetchBackups();
  } catch (err) {
    console.error(err);
    alert("Zmazanie zálohy zlyhalo.");
  }
};

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleString('sk-SK');
};

onMounted(fetchBackups);
</script>
