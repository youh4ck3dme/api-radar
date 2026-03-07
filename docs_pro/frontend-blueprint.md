# Frontend Blueprint

## Prehľad
Tento blueprint definuje kompletné frontend rozhranie pre API Centrum pomocou Vue.js 3 a moderných web technológií.

## Ciele
- Vytvoriť užívateľsky prívetivé webové rozhranie
- Implementovať reaktívny design pre všetky veľkosti obrazoviek
- Pripojiť frontend k backend API
- Implementovať real-time aktualizácie cez WebSocket
- Zabezpečiť bezpečný prístup a autentifikáciu

## 1. Frontend Architecture

### 1.1 Project structure
```
frontend/
├── public/
│   ├── manifest.webmanifest
│   ├── robots.txt
│   └── favicon.ico
├── src/
│   ├── assets/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── variables.css
│   │   ├── images/
│   │   └── icons/
│   ├── components/
│   │   ├── common/
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   ├── ErrorBoundary.vue
│   │   │   └── ToastNotification.vue
│   │   ├── auth/
│   │   │   ├── LoginForm.vue
│   │   │   ├── RegisterForm.vue
│   │   │   ├── PasswordResetForm.vue
│   │   │   └── TwoFactorAuth.vue
│   │   ├── domains/
│   │   │   ├── DomainList.vue
│   │   │   ├── DomainForm.vue
│   │   │   ├── DomainDetails.vue
│   │   │   └── DomainActions.vue
│   │   ├── ssl/
│   │   │   ├── SSLList.vue
│   │   │   ├── SSLForm.vue
│   │   │   ├── SSLDetails.vue
│   │   │   └── SSLActions.vue
│   │   ├── dashboard/
│   │   │   ├── DashboardOverview.vue
│   │   │   ├── SystemHealth.vue
│   │   │   ├── ActivityFeed.vue
│   │   │   └── UsageMetrics.vue
│   │   └── monitoring/
│   │       ├── HealthStatus.vue
│   │       ├── PerformanceMetrics.vue
│   │       └── AlertList.vue
│   ├── composables/
│   │   ├── useAuth.js
│   │   ├── useDomains.js
│   │   ├── useSSL.js
│   │   ├── useDashboard.js
│   │   ├── useWebSocket.js
│   │   └── useNotifications.js
│   ├── composables/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── domains.js
│   │   ├── ssl.js
│   │   └── dashboard.js
│   ├── router/
│   │   └── index.js
│   ├── store/
│   │   ├── index.js
│   │   ├── modules/
│   │   │   ├── auth.js
│   │   │   ├── domains.js
│   │   │   ├── ssl.js
│   │   │   ├── dashboard.js
│   │   │   └── notifications.js
│   ├── utils/
│   │   ├── helpers.js
│   │   ├── validators.js
│   │   ├── formatters.js
│   │   └── constants.js
│   ├── views/
│   │   ├── HomeView.vue
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── DashboardView.vue
│   │   ├── DomainsView.vue
│   │   ├── SSLView.vue
│   │   ├── MonitoringView.vue
│   │   └── SettingsView.vue
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

### 1.2 Technology stack
```json
{
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "vuex": "^4.1.0",
    "axios": "^1.5.0",
    "socket.io-client": "^4.7.2",
    "pinia": "^2.1.6",
    "vue-i18n": "^9.3.1",
    "vue-toastification": "^2.0.0-rc.5",
    "@vueuse/core": "^10.4.1",
    "date-fns": "^2.30.0",
    "lodash": "^4.17.21",
    "chart.js": "^4.3.3",
    "vue-chartjs": "^5.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.4",
    "vite": "^4.4.9",
    "sass": "^1.66.1",
    "eslint": "^8.47.0",
    "prettier": "^3.0.3"
  }
}
```

## 2. Vue.js Components

### 2.1 Main App component
```vue
<!-- src/App.vue -->
<template>
  <div id="app">
    <ToastNotification />
    <div class="app-container">
      <AppHeader v-if="isAuthenticated" />
      <AppSidebar v-if="isAuthenticated" />
      
      <main class="main-content" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <router-view />
      </main>
      
      <AppFooter />
    </div>
    
    <LoadingSpinner v-if="isLoading" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import AppHeader from './components/common/AppHeader.vue'
import AppSidebar from './components/common/AppSidebar.vue'
import AppFooter from './components/common/AppFooter.vue'
import LoadingSpinner from './components/common/LoadingSpinner.vue'
import ToastNotification from './components/common/ToastNotification.vue'

const store = useStore()

const isAuthenticated = computed(() => store.getters.isAuthenticated)
const isSidebarCollapsed = computed(() => store.getters.isSidebarCollapsed)
const isLoading = computed(() => store.getters.isLoading)
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 2rem;
  margin-left: 250px; /* Sidebar width */
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 60px; /* Collapsed sidebar width */
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 1rem;
  }
  
  .main-content.sidebar-collapsed {
    margin-left: 0;
  }
}
</style>
```

### 2.2 Authentication components
```vue
<!-- src/components/auth/LoginForm.vue -->
<template>
  <div class="login-form">
    <div class="form-card">
      <div class="form-header">
        <h2>Prihlásenie</h2>
        <p>Prihláste sa k svojmu účtu</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="form-body">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="vas@email.sk"
            required
            :class="{ error: errors.email }"
          />
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>
        
        <div class="form-group">
          <label for="password">Heslo</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Vaše heslo"
            required
            :class="{ error: errors.password }"
          />
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>
        
        <div class="form-group">
          <label class="checkbox-label">
            <input v-model="form.rememberMe" type="checkbox" />
            Zapamätať si ma
          </label>
        </div>
        
        <button 
          type="submit" 
          class="btn btn-primary btn-full"
          :disabled="isLoading"
        >
          <span v-if="isLoading">
            <i class="spinner"></i> Prihlasovanie...
          </span>
          <span v-else>Prihlásiť sa</span>
        </button>
      </form>
      
      <div class="form-footer">
        <router-link to="/forgot-password" class="link">Zabudli ste heslo?</router-link>
        <span class="separator">•</span>
        <router-link to="/register" class="link">Vytvoriť účet</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuth } from '../../composables/useAuth'
import { useNotifications } from '../../composables/useNotifications'

const { login } = useAuth()
const { showNotification } = useNotifications()

const isLoading = ref(false)
const errors = ref({})

const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

const validateForm = () => {
  errors.value = {}
  
  if (!form.email) {
    errors.value.email = 'Zadajte emailovú adresu'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.value.email = 'Zadajte platnú emailovú adresu'
  }
  
  if (!form.password) {
    errors.value.password = 'Zadajte heslo'
  } else if (form.password.length < 8) {
    errors.value.password = 'Heslo musí mať aspoň 8 znakov'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleLogin = async () => {
  if (!validateForm()) {
    return
  }
  
  isLoading.value = true
  
  try {
    await login(form.email, form.password, form.rememberMe)
    showNotification('Úspešne ste sa prihlásili', 'success')
  } catch (error) {
    showNotification(error.message || 'Prihlásenie zlyhalo', 'error')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-form {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-background-secondary);
}

.form-card {
  background: var(--color-card-background);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: var(--shadow-elevation-medium);
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 2rem;
  text-align: center;
}

.form-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--color-text-primary);
}

.form-header p {
  margin: 0;
  color: var(--color-text-secondary);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
  background: var(--color-input-background);
  color: var(--color-text-primary);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-transparent);
}

.form-group input.error {
  border-color: var(--color-error);
}

.error-message {
  font-size: 0.75rem;
  color: var(--color-error);
  margin-top: 0.25rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: var(--color-disabled);
  cursor: not-allowed;
  transform: none;
}

.btn-full {
  width: 100%;
}

.form-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

.separator {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

### 2.3 Domain management components
```vue
<!-- src/components/domains/DomainList.vue -->
<template>
  <div class="domain-list">
    <div class="list-header">
      <h2>Moje domény</h2>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="refreshDomains">
          <i class="icon-refresh"></i>
          Obnoviť
        </button>
        <button class="btn btn-primary" @click="showCreateModal = true">
          <i class="icon-plus"></i>
          Pridať doménu
        </button>
      </div>
    </div>
    
    <div class="search-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Vyhľadať doménu..."
          class="search-input"
        />
        <i class="icon-search"></i>
      </div>
      
      <div class="filters">
        <select v-model="statusFilter" class="filter-select">
          <option value="">Všetky stavy</option>
          <option value="active">Aktívne</option>
          <option value="pending">Čakajúce</option>
          <option value="suspended">Pozastavené</option>
        </select>
        
        <select v-model="sortField" class="filter-select">
          <option value="name">Zoradiť podľa názvu</option>
          <option value="created_at">Zoradiť podľa dátumu</option>
          <option value="status">Zoradiť podľa stavu</option>
        </select>
      </div>
    </div>
    
    <div class="domain-grid">
      <DomainCard
        v-for="domain in filteredDomains"
        :key="domain.id"
        :domain="domain"
        @refresh="refreshDomains"
      />
      
      <div v-if="filteredDomains.length === 0" class="empty-state">
        <i class="icon-domain"></i>
        <h3>Žiadne domény</h3>
        <p>Zatiaľ nemáte žiadne domény. Pridajte svoju prvú doménu.</p>
        <button class="btn btn-primary" @click="showCreateModal = true">
          Pridať prvú doménu
        </button>
      </div>
    </div>
    
    <DomainFormModal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @created="handleDomainCreated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDomains } from '../../composables/useDomains'
import { useNotifications } from '../../composables/useNotifications'
import DomainCard from './DomainCard.vue'
import DomainFormModal from './DomainFormModal.vue'

const { domains, fetchDomains, isLoading } = useDomains()
const { showNotification } = useNotifications()

const showCreateModal = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const sortField = ref('created_at')

onMounted(() => {
  fetchDomains()
})

const filteredDomains = computed(() => {
  let filtered = domains.value
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(domain => 
      domain.name.toLowerCase().includes(query) ||
      domain.description?.toLowerCase().includes(query)
    )
  }
  
  // Filter by status
  if (statusFilter.value) {
    filtered = filtered.filter(domain => domain.status === statusFilter.value)
  }
  
  // Sort
  filtered.sort((a, b) => {
    switch (sortField.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'created_at':
        return new Date(b.created_at) - new Date(a.created_at)
      case 'status':
        return a.status.localeCompare(b.status)
      default:
        return 0
    }
  })
  
  return filtered
})

const refreshDomains = async () => {
  await fetchDomains()
  showNotification('Zoznam domén bol obnovený', 'success')
}

const handleDomainCreated = (domain) => {
  showCreateModal.value = false
  showNotification(`Doména ${domain.name} bola úspešne vytvorená`, 'success')
  fetchDomains()
}
</script>

<style scoped>
.domain-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.list-header h2 {
  margin: 0;
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.search-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: var(--color-card-background);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 1rem;
  background: var(--color-input-background);
  color: var(--color-text-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.icon-search {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  pointer-events: none;
}

.filters {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-input-background);
  color: var(--color-text-primary);
  font-size: 1rem;
}

.domain-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  background: var(--color-card-background);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.empty-state i {
  font-size: 3rem;
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: var(--color-text-primary);
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    flex-direction: column;
    gap: 1rem;
  }
  
  .domain-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

## 3. Vue Composables

### 3.1 Authentication composable
```javascript
// src/composables/useAuth.js
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { authAPI } from '../services/auth'

export function useAuth() {
  const store = useStore()
  const router = useRouter()
  
  const isLoading = ref(false)
  const error = ref(null)
  
  const isAuthenticated = computed(() => store.getters.isAuthenticated)
  const user = computed(() => store.getters.user)
  const token = computed(() => store.getters.token)
  
  const login = async (email, password, rememberMe = false) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.login(email, password)
      
      // Store tokens
      const { access_token, refresh_token, user: userData } = response
      
      store.commit('SET_AUTH', {
        token: access_token,
        refreshToken: refresh_token,
        user: userData
      })
      
      // Set remember me
      if (rememberMe) {
        localStorage.setItem('remember_me', 'true')
      } else {
        localStorage.removeItem('remember_me')
      }
      
      // Set up token refresh
      setupTokenRefresh(refresh_token)
      
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear auth state
      store.commit('CLEAR_AUTH')
      localStorage.removeItem('remember_me')
      clearInterval(window.tokenRefreshInterval)
      router.push('/login')
    }
  }
  
  const refreshToken = async () => {
    try {
      const refreshToken = store.getters.refreshToken
      if (!refreshToken) return
      
      const response = await authAPI.refreshToken(refreshToken)
      
      store.commit('SET_TOKEN', response.access_token)
      setupTokenRefresh(response.refresh_token)
      
      return response
    } catch (err) {
      console.error('Token refresh error:', err)
      logout()
      throw err
    }
  }
  
  const setupTokenRefresh = (refreshToken) => {
    // Clear existing interval
    if (window.tokenRefreshInterval) {
      clearInterval(window.tokenRefreshInterval)
    }
    
    // Set up token refresh every 15 minutes
    window.tokenRefreshInterval = setInterval(() => {
      refreshToken().catch(err => {
        console.error('Auto refresh failed:', err)
      })
    }, 15 * 60 * 1000) // 15 minutes
  }
  
  const checkAuth = async () => {
    const token = store.getters.token
    if (!token) return false
    
    try {
      const response = await authAPI.checkAuth()
      store.commit('SET_USER', response.user)
      return true
    } catch (err) {
      logout()
      return false
    }
  }
  
  const register = async (userData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.register(userData)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const forgotPassword = async (email) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.forgotPassword(email)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const resetPassword = async (token, password) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.resetPassword(token, password)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    // State
    isLoading,
    error,
    isAuthenticated,
    user,
    token,
    
    // Actions
    login,
    logout,
    refreshToken,
    checkAuth,
    register,
    forgotPassword,
    resetPassword
  }
}
```

### 3.2 Domain management composable
```javascript
// src/composables/useDomains.js
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { domainsAPI } from '../services/domains'

export function useDomains() {
  const store = useStore()
  
  const isLoading = ref(false)
  const error = ref(null)
  
  const domains = computed(() => store.getters.domains)
  const domainCount = computed(() => domains.value.length)
  
  const fetchDomains = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsAPI.getDomains()
      store.commit('SET_DOMAINS', response.domains)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const createDomain = async (domainData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsAPI.createDomain(domainData)
      store.commit('ADD_DOMAIN', response.domain)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const updateDomain = async (domainId, domainData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsAPI.updateDomain(domainId, domainData)
      store.commit('UPDATE_DOMAIN', response.domain)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const deleteDomain = async (domainId) => {
    isLoading.value = true
    error.value = null
    
    try {
      await domainsAPI.deleteDomain(domainId)
      store.commit('REMOVE_DOMAIN', domainId)
      return true
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const getDomainDetails = async (domainId) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsAPI.getDomainDetails(domainId)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const checkDomainAvailability = async (domainName) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsAPI.checkDomain(domainName)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const getDomainSSLStatus = async (domainName) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await domainsAPI.getDomainSSLStatus(domainName)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    // State
    isLoading,
    error,
    domains,
    domainCount,
    
    // Actions
    fetchDomains,
    createDomain,
    updateDomain,
    deleteDomain,
    getDomainDetails,
    checkDomainAvailability,
    getDomainSSLStatus
  }
}
```

### 3.3 WebSocket composable
```javascript
// src/composables/useWebSocket.js
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { useStore } from 'vuex'

export function useWebSocket() {
  const store = useStore()
  const socket = ref(null)
  const isConnected = ref(false)
  
  const connect = () => {
    const token = store.getters.token
    if (!token) return
    
    socket.value = io(import.meta.env.VITE_WS_URL, {
      auth: {
        token: token
      }
    })
    
    socket.value.on('connect', () => {
      isConnected.value = true
      console.log('WebSocket connected')
    })
    
    socket.value.on('disconnect', () => {
      isConnected.value = false
      console.log('WebSocket disconnected')
    })
    
    // Listen for domain updates
    socket.value.on('domain:updated', (data) => {
      store.commit('UPDATE_DOMAIN', data.domain)
    })
    
    // Listen for SSL updates
    socket.value.on('ssl:updated', (data) => {
      store.commit('UPDATE_SSL_CERTIFICATE', data.certificate)
    })
    
    // Listen for system events
    socket.value.on('system:health', (data) => {
      store.commit('SET_SYSTEM_HEALTH', data.health)
    })
    
    // Listen for notifications
    socket.value.on('notification', (data) => {
      store.commit('ADD_NOTIFICATION', data.notification)
    })
  }
  
  const disconnect = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
    }
  }
  
  const emit = (event, data) => {
    if (socket.value && isConnected.value) {
      socket.value.emit(event, data)
    }
  }
  
  onMounted(() => {
    connect()
  })
  
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    socket,
    isConnected,
    connect,
    disconnect,
    emit
  }
}
```

## 4. API Services

### 4.1 API client setup
```javascript
// src/services/api.js
import axios from 'axios'
import { useAuth } from '../composables/useAuth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    
    // Handle token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          })
          
          localStorage.setItem('token', response.data.access_token)
          localStorage.setItem('refresh_token', response.data.refresh_token)
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
```

### 4.2 Domain API service
```javascript
// src/services/domains.js
import apiClient from './api'

export const domainsAPI = {
  // Get all domains
  async getDomains(page = 1, size = 10, search = '', status = '') {
    const params = { page, size }
    if (search) params.search = search
    if (status) params.status = status
    
    return await apiClient.get('/domains', { params })
  },
  
  // Get domain by ID
  async getDomainDetails(domainId) {
    return await apiClient.get(`/domains/${domainId}`)
  },
  
  // Create new domain
  async createDomain(domainData) {
    return await apiClient.post('/domains', domainData)
  },
  
  // Update domain
  async updateDomain(domainId, domainData) {
    return await apiClient.put(`/domains/${domainId}`, domainData)
  },
  
  // Delete domain
  async deleteDomain(domainId) {
    return await apiClient.delete(`/domains/${domainId}`)
  },
  
  // Check domain availability
  async checkDomain(domainName) {
    return await apiClient.post('/domains/check', { domain: domainName })
  },
  
  // Get domain SSL status
  async getDomainSSLStatus(domainName) {
    return await apiClient.get(`/ssl/${domainName}`)
  },
  
  // Get domain DNS records
  async getDomainDNS(domainId) {
    return await apiClient.get(`/domains/${domainId}/dns`)
  },
  
  // Update domain DNS records
  async updateDomainDNS(domainId, dnsRecords) {
    return await apiClient.put(`/domains/${domainId}/dns`, { records: dnsRecords })
  }
}
```

### 4.3 SSL API service
```javascript
// src/services/ssl.js
import apiClient from './api'

export const sslAPI = {
  // Get all SSL certificates
  async getCertificates(page = 1, size = 10) {
    return await apiClient.get('/ssl', { params: { page, size } })
  },
  
  // Generate SSL certificate
  async generateCertificate(domain, email) {
    return await apiClient.post('/ssl/generate', { domain, email })
  },
  
  // Get SSL certificate details
  async getCertificateDetails(domain) {
    return await apiClient.get(`/ssl/${domain}`)
  },
  
  // Renew SSL certificate
  async renewCertificate(domain) {
    return await apiClient.post(`/ssl/renew/${domain}`)
  },
  
  // Revoke SSL certificate
  async revokeCertificate(domain) {
    return await apiClient.delete(`/ssl/revoke/${domain}`)
  },
  
  // Get SSL certificate info
  async getCertificateInfo(domain) {
    return await apiClient.get(`/ssl/info/${domain}`)
  }
}
```

## 5. State Management

### 5.1 Vuex store setup
```javascript
// src/store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'
import domains from './modules/domains'
import ssl from './modules/ssl'
import dashboard from './modules/dashboard'
import notifications from './modules/notifications'

const store = createStore({
  modules: {
    auth,
    domains,
    ssl,
    dashboard,
    notifications
  },
  strict: process.env.NODE_ENV !== 'production'
})

export default store
```

### 5.2 Auth module
```javascript
// src/store/modules/auth.js
import { authAPI } from '../../services/auth'

const state = {
  token: localStorage.getItem('token'),
  refreshToken: localStorage.getItem('refresh_token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null
}

const getters = {
  token: state => state.token,
  refreshToken: state => state.refreshToken,
  user: state => state.user,
  isAuthenticated: state => state.isAuthenticated,
  isLoading: state => state.isLoading,
  error: state => state.error,
  userRole: state => state.user?.role,
  userPermissions: state => state.user?.permissions || []
}

const mutations = {
  SET_LOADING(state, isLoading) {
    state.isLoading = isLoading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  SET_AUTH(state, { token, refreshToken, user }) {
    state.token = token
    state.refreshToken = refreshToken
    state.user = user
    state.isAuthenticated = true
    state.error = null
    
    localStorage.setItem('token', token)
    localStorage.setItem('refresh_token', refreshToken)
  },
  
  SET_TOKEN(state, token) {
    state.token = token
    localStorage.setItem('token', token)
  },
  
  SET_USER(state, user) {
    state.user = user
  },
  
  CLEAR_AUTH(state) {
    state.token = null
    state.refreshToken = null
    state.user = null
    state.isAuthenticated = false
    state.error = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }
}

const actions = {
  async login({ commit }, { email, password, rememberMe }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await authAPI.login(email, password)
      commit('SET_AUTH', {
        token: response.access_token,
        refreshToken: response.refresh_token,
        user: response.user
      })
      
      if (rememberMe) {
        localStorage.setItem('remember_me', 'true')
      }
      
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async logout({ commit }) {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      commit('CLEAR_AUTH')
    }
  },
  
  async refreshToken({ commit, state }) {
    try {
      const response = await authAPI.refreshToken(state.refreshToken)
      commit('SET_TOKEN', response.access_token)
      return response
    } catch (error) {
      commit('CLEAR_AUTH')
      throw error
    }
  },
  
  async checkAuth({ commit }) {
    try {
      const response = await authAPI.checkAuth()
      commit('SET_USER', response.user)
      return true
    } catch (error) {
      commit('CLEAR_AUTH')
      return false
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
```

## 6. Router Configuration

### 6.1 Vue Router setup
```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

// Import views
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import DomainsView from '../views/DomainsView.vue'
import SSLView from '../views/SSLView.vue'
import MonitoringView from '../views/MonitoringView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/domains',
    name: 'domains',
    component: DomainsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/ssl',
    name: 'ssl',
    component: SSLView,
    meta: { requiresAuth: true }
  },
  {
    path: '/monitoring',
    name: 'monitoring',
    component: MonitoringView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, checkAuth } = useAuth()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!isAuthenticated.value) {
      // Try to check auth status
      const isAuth = await checkAuth()
      if (!isAuth) {
        next('/login')
        return
      }
    }
  }
  
  // Check if route is for guests only (login, register)
  if (to.meta.guestOnly && isAuthenticated.value) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
```

## 7. Styling & Design System

### 7.1 CSS Variables
```css
/* src/assets/css/variables.css */
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-primary-transparent: rgba(59, 130, 246, 0.1);
  
  --color-secondary: #64748b;
  --color-secondary-dark: #475569;
  
  --color-success: #10b981;
  --color-success-dark: #059669;
  
  --color-warning: #f59e0b;
  --color-warning-dark: #d97706;
  
  --color-error: #ef4444;
  --color-error-dark: #dc2626;
  
  --color-text-primary: #1f2937;
  --color-text-secondary: #6b7280;
  --color-text-muted: #9ca3af;
  
  --color-background: #f8fafc;
  --color-background-secondary: #f1f5f9;
  --color-background-tertiary: #e2e8f0;
  
  --color-card-background: #ffffff;
  --color-input-background: #ffffff;
  
  --color-border: #e5e7eb;
  --color-border-hover: #d1d5db;
  
  --color-disabled: #9ca3af;
  
  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  --spacing-3xl: 4rem;
  
  /* Shadows */
  --shadow-elevation-low: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-elevation-medium: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-elevation-high: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  
  /* Borders */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-radius-full: 9999px;
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --transition-slow: 500ms ease;
  
  /* Z-index */
  --z-dropdown: 1000;
  --z-modal: 1050;
  --z-toast: 1100;
  --z-tooltip: 1200;
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text-primary: #f8fafc;
    --color-text-secondary: #cbd5e1;
    --color-text-muted: #94a3b8;
    
    --color-background: #0f172a;
    --color-background-secondary: #111827;
    --color-background-tertiary: #1f2937;
    
    --color-card-background: #111827;
    --color-input-background: #1f2937;
    
    --color-border: #374151;
    --color-border-hover: #4b5563;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :root {
    --color-border: #000000;
    --color-text-primary: #000000;
    --color-text-secondary: #000000;
  }
}
```

### 7.2 Component styling
```scss
/* src/assets/css/components.scss */
@import './variables.css';

// Common component styles
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-decoration: none;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-elevation-low);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  &.btn-primary {
    background: var(--color-primary);
    color: white;
    
    &:hover:not(:disabled) {
      background: var(--color-primary-dark);
    }
  }
  
  &.btn-secondary {
    background: var(--color-secondary);
    color: white;
    
    &:hover:not(:disabled) {
      background: var(--color-secondary-dark);
    }
  }
  
  &.btn-success {
    background: var(--color-success);
    color: white;
    
    &:hover:not(:disabled) {
      background: var(--color-success-dark);
    }
  }
  
  &.btn-warning {
    background: var(--color-warning);
    color: white;
    
    &:hover:not(:disabled) {
      background: var(--color-warning-dark);
    }
  }
  
  &.btn-error {
    background: var(--color-error);
    color: white;
    
    &:hover:not(:disabled) {
      background: var(--color-error-dark);
    }
  }
  
  &.btn-outline {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-primary);
    
    &:hover:not(:disabled) {
      border-color: var(--color-primary);
      color: var(--color-primary);
    }
  }
  
  &.btn-ghost {
    background: transparent;
    color: var(--color-text-primary);
    
    &:hover:not(:disabled) {
      background: var(--color-background-tertiary);
    }
  }
  
  &.btn-full {
    width: 100%;
  }
  
  &.btn-icon {
    padding: 0.75rem;
    width: 40px;
    height: 40px;
  }
}

.card {
  background: var(--color-card-background);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-elevation-low);
  transition: box-shadow var(--transition-normal);
  
  &:hover {
    box-shadow: var(--shadow-elevation-medium);
  }
  
  &.card-compact {
    border-radius: var(--border-radius-md);
  }
  
  &.card-full {
    width: 100%;
    height: 100%;
  }
}

.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  background: var(--color-input-background);
  color: var(--color-text-primary);
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
  
  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary-transparent);
  }
  
  &:disabled {
    background: var(--color-background-tertiary);
    color: var(--color-text-secondary);
    cursor: not-allowed;
  }
  
  &::placeholder {
    color: var(--color-text-muted);
  }
  
  &.input-error {
    border-color: var(--color-error);
  }
  
  &.input-success {
    border-color: var(--color-success);
  }
}

.label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
  
  &.badge-primary {
    background: var(--color-primary-transparent);
    color: var(--color-primary);
  }
  
  &.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-success);
  }
  
  &.badge-warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--color-warning);
  }
  
  &.badge-error {
    background: rgba(239, 68, 68, 0.1);
    color: var(--color-error);
  }
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  
  &::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-text-secondary);
  }
  
  &.status-active {
    color: var(--color-success);
    background: rgba(16, 185, 129, 0.1);
    
    &::before {
      background: var(--color-success);
    }
  }
  
  &.status-pending {
    color: var(--color-warning);
    background: rgba(245, 158, 11, 0.1);
    
    &::before {
      background: var(--color-warning);
    }
  }
  
  &.status-inactive {
    color: var(--color-error);
    background: rgba(239, 68, 68, 0.1);
    
    &::before {
      background: var(--color-error);
    }
  }
}

// Layout utilities
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.grid {
  display: grid;
  gap: var(--spacing-md);
}

.flex {
  display: flex;
  gap: var(--spacing-md);
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.text-sm {
  font-size: var(--font-size-sm);
}

.text-base {
  font-size: var(--font-size-base);
}

.text-lg {
  font-size: var(--font-size-lg);
}

.text-xl {
  font-size: var(--font-size-xl);
}

.text-2xl {
  font-size: var(--font-size-2xl);
}

.text-3xl {
  font-size: var(--font-size-3xl);
}

.text-4xl {
  font-size: var(--font-size-4xl);
}

.text-primary {
  color: var(--color-primary);
}

.text-success {
  color: var(--color-success);
}

.text-warning {
  color: var(--color-warning);
}

.text-error {
  color: var(--color-error);
}

.text-muted {
  color: var(--color-text-muted);
}

.mt-1 { margin-top: var(--spacing-xs); }
.mt-2 { margin-top: var(--spacing-sm); }
.mt-3 { margin-top: var(--spacing-md); }
.mt-4 { margin-top: var(--spacing-lg); }
.mt-5 { margin-top: var(--spacing-xl); }
.mt-6 { margin-top: var(--spacing-2xl); }

.mb-1 { margin-bottom: var(--spacing-xs); }
.mb-2 { margin-bottom: var(--spacing-sm); }
.mb-3 { margin-bottom: var(--spacing-md); }
.mb-4 { margin-bottom: var(--spacing-lg); }
.mb-5 { margin-bottom: var(--spacing-xl); }
.mb-6 { margin-bottom: var(--spacing-2xl); }

.p-1 { padding: var(--spacing-xs); }
.p-2 { padding: var(--spacing-sm); }
.p-3 { padding: var(--spacing-md); }
.p-4 { padding: var(--spacing-lg); }
.p-5 { padding: var(--spacing-xl); }
.p-6 { padding: var(--spacing-2xl); }

.px-1 { padding-left: var(--spacing-xs); padding-right: var(--spacing-xs); }
.px-2 { padding-left: var(--spacing-sm); padding-right: var(--spacing-sm); }
.px-3 { padding-left: var(--spacing-md); padding-right: var(--spacing-md); }
.px-4 { padding-left: var(--spacing-lg); padding-right: var(--spacing-lg); }

.py-1 { padding-top: var(--spacing-xs); padding-bottom: var(--spacing-xs); }
.py-2 { padding-top: var(--spacing-sm); padding-bottom: var(--spacing-sm); }
.py-3 { padding-top: var(--spacing-md); padding-bottom: var(--spacing-md); }
.py-4 { padding-top: var(--spacing-lg); padding-bottom: var(--spacing-lg); }

// Responsive utilities
@media (max-width: 768px) {
  .container {
    padding: 0 var(--spacing-sm);
  }
  
  .hidden-mobile {
    display: none !important;
  }
}

@media (min-width: 769px) {
  .hidden-desktop {
    display: none !important;
  }
}
```

## 8. Implementation Steps

### 8.1 Week 1: Basic Setup
- [ ] Nastaviť Vue.js projekt
- [ ] Nastaviť router a základnú štruktúru
- [ ] Vytvoriť základné komponenty (Header, Sidebar, Footer)
- [ ] Nastaviť CSS-in-JS styling

### 8.2 Week 2: Authentication
- [ ] Vytvoriť auth komponenty
- [ ] Implementovať auth composable
- [ ] Nastaviť Vuex store pre auth
- [ ] Pridať navigačné guards

### 8.3 Week 3: Domain Management
- [ ] Vytvoriť domain komponenty
- [ ] Implementovať domain composable
- [ ] Nastaviť API services
- [ ] Pridať CRUD operácie

### 8.4 Week 4: SSL Management
- [ ] Vytvoriť SSL komponenty
- [ ] Implementovať SSL composable
- [ ] Pridať SSL generovanie a správu
- [ ] Integrácia s backend API

### 8.5 Week 5: Dashboard & Monitoring
- [ ] Vytvoriť dashboard komponenty
- [ ] Implementovať WebSocket pripojenie
- [ ] Pridať real-time metriky
- [ ] Vytvoriť monitoring view

### 8.6 Week 6: Polish & Polish
- [ ] Implementovať notifikácie
- [ ] Pridať loading stavy
- [ ] Optimalizovať výkon
- [ ] Testovanie a bug fixing

## 9. Best Practices

### 9.1 Vue.js best practices
- **Composition API**: Používať Composition API pre lepšiu organizáciu kódu
- **Composables**: Vytvárať reusable composable funkcie
- **Props validation**: Validovať props pomocou PropTypes
- **Event handling**: Používať emit pre komunikáciu medzi komponentami
- **Lifecycle hooks**: Používať správne lifecycle hooks

### 9.2 State management best practices
- **Single source of truth**: Jedno miesto pre každý kus dát
- **Immutable updates**: Nepriamo meniť state pomocou mutations
- **Async actions**: Asynchrónne operácie v actions
- **Error handling**: Ošetrovať chyby v každom action
- **Performance**: Používať getters pre výpočty

### 9.3 API integration best practices
- **Error handling**: Ošetrovať všetky možné chyby
- **Loading states**: Zobrazovať loading indikátory
- **Caching**: Implementovať caching pre častejšie volania
- **Retry logic**: Pridať retry pre network chyby
- **Security**: Neprezrádzať citlivé informácie

Tento blueprint poskytuje komplexný návod na vytvorenie moderného a užívateľsky prívetivého frontend rozhrania pre API Centrum.