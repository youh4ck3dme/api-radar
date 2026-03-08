<template>
  <div class="login-root">
    <!-- Animated Radar Background -->
    <div class="radar-container">
      <div class="radar-scan"></div>
      <div class="radar-grid"></div>
      <div class="radar-ping p1"></div>
      <div class="radar-ping p2"></div>
      <div class="radar-ping p3"></div>
    </div>

    <!-- Scrolling Terminal Simulation -->
    <div class="terminal-overlay">
      <div class="terminal-feed">
        <div v-for="(log, i) in logs" :key="i" class="log-line">
          <span class="log-time">[{{ log.time }}]</span>
          <span class="log-status" :class="log.type">{{ log.status }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
        <div class="log-line active">
          <span class="log-time">[{{ currentTime }}]</span>
          <span class="log-status info">EXEC</span>
          <span class="log-msg">shadow_scanner --mode=stealth --target=auto</span>
          <span class="terminal-cursor"></span>
        </div>
      </div>
    </div>

    <!-- Glass card -->
    <div class="glass-card">
      <!-- Logo -->
      <div class="logo-wrap">
        <div class="logo-outer">
            <div class="logo-icon-glass">
                <img src="/favicon.png" alt="Logo" class="logo-img" />
            </div>
        </div>
      </div>

      <h1 class="title">API Radar <span class="text-pro">Pro</span></h1>
      <p class="subtitle">Unified Discovery & Shadow Defense</p>

      <form @submit.prevent="login" class="form">
        <!-- Email -->
        <div class="field">
          <label>Email</label>
          <div class="input-wrap">
            <span class="input-icon">✉</span>
            <input
              v-model="email"
              type="email"
              required
              autocomplete="email"
              placeholder="vas@email.com"
            />
          </div>
        </div>

        <!-- Password -->
        <div class="field">
          <label>Heslo</label>
          <div class="input-wrap">
            <span class="input-icon">🔑</span>
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="••••••••"
            />
            <button type="button" class="eye-btn" @click="showPassword = !showPassword">
              {{ showPassword ? '🙈' : '👁' }}
            </button>
          </div>
        </div>

        <!-- Error -->
        <transition name="shake">
          <div v-if="error" class="error-box">
            <span>⚠</span> {{ error }}
          </div>
        </transition>

        <!-- Submit -->
        <button type="submit" :disabled="loading" class="submit-btn">
          <span v-if="loading" class="loader"></span>
          <span v-else>Prihlásiť sa →</span>
        </button>
      </form>

      <!-- Footer -->
      <p class="footer-text">
        <span class="dot"></span> Zabezpečené šifrovaním
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/api';

const emit = defineEmits(['logged-in']);

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const showPassword = ref(false);

const currentTime = ref(new Date().toLocaleTimeString('en-US', { hour12: false }));

onMounted(() => {
    setInterval(() => {
        currentTime.value = new Date().toLocaleTimeString('en-US', { hour12: false });
    }, 1000);
});

const logs = ref([
  { time: '02:43:01', status: 'INIT', msg: 'Kernel boot sequence started...', type: 'sys' },
  { time: '02:43:02', status: 'WAIT', msg: 'Establishing encrypted uplink...', type: 'sys' },
  { time: '02:43:03', status: 'AUTH', msg: 'Shadow API detection engine: ONLINE', type: 'warn' },
]);

const possibleLogs = [
  { status: 'SCAN', msg: 'Probing endpoint: /api/v1/auth', type: 'info' },
  { status: 'SCAN', msg: 'Probing endpoint: /internal/config', type: 'info' },
  { status: 'SHDW', msg: 'Shadow API detected at 88.212.19.47', type: 'crit' },
  { status: 'SYNC', msg: 'Synchronizing with VPS registry...', type: 'sys' },
  { status: 'PASS', msg: 'Heartbeat signal: SECTOR 7 OK', type: 'sys' },
  { status: 'TRAF', msg: 'Incoming traffic: NGINX_LOG_PIPE', type: 'info' },
];

const addRandomLog = () => {
    const log = possibleLogs[Math.floor(Math.random() * possibleLogs.length)];
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    logs.value.push({ ...log, time });
    if (logs.value.length > 8) logs.value.shift();
};

onMounted(() => {
    setInterval(addRandomLog, 2000);
});

const login = async () => {
  error.value = '';
  loading.value = true;
  try {
    const res = await api.post('/auth/login', { email: email.value, password: password.value });
    localStorage.setItem('access_token', res.data.access_token);
    emit('logged-in');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Prihlásenie zlyhalo. Skontroluj údaje.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* ── Root ─────────────────────────────────────── */
.login-root {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
  overflow: hidden;
  position: relative;
  font-family: 'Outfit', sans-serif;
}

/* ── Radar Background ─────────────────────────── */
.radar-container {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: #020202;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 0; /* Below everything */
}
.radar-grid {
  position: absolute;
  width: 200vw;
  height: 200vw;
  background-image: 
    linear-gradient(rgba(0, 255, 120, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 120, 0.08) 1px, transparent 1px);
  background-size: 80px 80px;
  transform: rotateX(60deg) translateZ(-100px);
  opacity: 0.8;
}
.radar-scan {
  position: absolute;
  width: 1200px;
  height: 1200px;
  background: conic-gradient(from 0deg, rgba(0, 255, 100, 0.6) 0%, transparent 50%);
  border-radius: 50%;
  animation: scan 6s linear infinite;
  mask-image: radial-gradient(circle, black 30%, transparent 80%);
  -webkit-mask-image: radial-gradient(circle, black 30%, transparent 80%);
}
@keyframes scan {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.radar-ping {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #00ff78;
  border-radius: 50%;
  filter: blur(1px);
  box-shadow: 0 0 12px #00ff78;
  opacity: 0;
  z-index: 1;
}
.p1 { top: 20%; left: 30%; animation: ping 4s linear infinite; }
.p2 { top: 60%; left: 70%; animation: ping 4s 1s linear infinite; }
.p3 { top: 45%; left: 55%; animation: ping 4s 2.5s linear infinite; }

@keyframes ping {
  0% { opacity: 0; transform: scale(0.5); }
  10% { opacity: 1; transform: scale(1); }
  30% { opacity: 0; transform: scale(1.2); }
  100% { opacity: 0; }
}

/* ── Terminal Simulation ──────────────────────── */
.terminal-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 2rem;
  z-index: 5;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
}
.terminal-feed {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: -0.02em;
    display: flex;
    flex-direction: column;
    gap: 4px;
    opacity: 0.6;
}
.log-line {
    display: flex;
    gap: 12px;
    align-items: center;
}
.log-time { color: rgba(0, 255, 100, 0.4); }
.log-status {
    padding: 1px 6px;
    border-radius: 4px;
    font-weight: 900;
    font-size: 10px;
}
.log-status.sys { background: rgba(0, 255, 100, 0.1); color: #00ff64; }
.log-status.warn { background: rgba(255, 200, 0, 0.1); color: #ffc800; }
.log-status.crit { background: rgba(255, 0, 0, 0.1); color: #ff0000; animation: blink 0.5s infinite; }
.log-status.info { background: rgba(0, 150, 255, 0.1); color: #0096ff; }
.log-msg { color: rgba(255,255,255,0.7); }

.terminal-cursor {
    display: inline-block;
    width: 8px;
    height: 14px;
    background: #00ff64;
    margin-left: 4px;
    animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {
    from, to { opacity: 1; }
    50% { opacity: 0; }
}

@keyframes blink {
    50% { opacity: 0.3; }
}

/* ── Glass card ───────────────────────────────── */
.glass-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 440px;
  margin: 1.5rem;
  padding: 3.5rem 2.5rem;
  border-radius: 40px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(60px) saturate(180%);
  -webkit-backdrop-filter: blur(60px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 50px 120px -20px rgba(0, 0, 0, 0.8),
    inset 0 1px 1px rgba(255, 255, 255, 0.1);
  animation: cardIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Logo ─────────────────────────────────────── */
.logo-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}
.logo-outer {
    position: relative;
    padding: 8px;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
    border-radius: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.logo-icon-glass {
    width: 64px; height: 64px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid rgba(255,255,255,0.1);
}
.logo-img {
    width: 32px; height: 32px;
    filter: drop-shadow(0 0 10px rgba(14, 165, 233, 0.5));
}

/* ── Typography ───────────────────────────────── */
.title {
  text-align: center;
  font-size: 2rem;
  font-weight: 900;
  color: #fff;
  letter-spacing: -0.04em;
  margin: 0 0 0.5rem;
}
.text-pro {
    color: #3b82f6;
    background: linear-gradient(to right, #60a5fa, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
  text-align: center;
  font-size: 0.95rem;
  font-weight: 500;
  color: rgba(255,255,255,0.4);
  margin: 0 0 2.5rem;
  letter-spacing: 0.01em;
}

/* ── Form ─────────────────────────────────────── */
.form { display: flex; flex-direction: column; gap: 1rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255,255,250,0.45);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* ── Inputs ───────────────────────────────────── */
.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 14px;
  font-size: 0.9rem;
  opacity: 0.4;
  pointer-events: none;
  user-select: none;
}
.input-wrap input {
  width: 100%;
  padding: 0.75rem 2.8rem 0.75rem 2.8rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  color: rgba(255,255,250,0.9);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.input-wrap input::placeholder { color: rgba(255,255,255,0.18); }
.input-wrap input:focus {
  border-color: rgba(255,255,250,0.25);
  background: rgba(255,255,255,0.07);
  box-shadow: 0 0 0 3px rgba(255,255,250,0.06);
}
.eye-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  opacity: 0.4;
  transition: opacity 0.2s;
  padding: 0;
  line-height: 1;
}
.eye-btn:hover { opacity: 0.8; }

/* ── Error ────────────────────────────────────── */
.error-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  border-radius: 12px;
  color: rgba(252,165,165,0.9);
  font-size: 0.82rem;
}
.shake-enter-active { animation: shake 0.4s; }
@keyframes shake {
  0%,100% { transform: translateX(0); }
  25%      { transform: translateX(-6px); }
  75%      { transform: translateX(6px); }
}

/* ── Submit button ────────────────────────────── */
.submit-btn {
  margin-top: 0.5rem;
  width: 100%;
  padding: 0.85rem;
  border: 1px solid rgba(255,255,250,0.14);
  border-radius: 14px;
  background: rgba(255,255,250,0.09);
  color: rgba(255,255,250,0.92);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s, border-color 0.2s;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
  letter-spacing: 0.01em;
  backdrop-filter: blur(8px);
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: rgba(255,255,250,0.14);
  border-color: rgba(255,255,250,0.22);
  box-shadow: 0 12px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.12);
}
.submit-btn:active:not(:disabled) { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Loader spinner ───────────────────────────── */
.loader {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.15);
  border-top-color: rgba(255,255,250,0.8);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer ───────────────────────────────────── */
.footer-text {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.dot {
  width: 6px; height: 6px;
  background: #4ade80;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 8px rgba(74,222,128,0.6);
}
</style>
