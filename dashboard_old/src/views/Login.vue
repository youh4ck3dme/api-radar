<template>
  <div class="login-root">
    <!-- Animated background orbs -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <!-- Glass card -->
    <div class="glass-card">
      <!-- Logo -->
      <div class="logo-wrap">
        <div class="logo-icon">🌐</div>
      </div>

      <h1 class="title">API Centrum</h1>
      <p class="subtitle">Prihlás sa do svojho účtu</p>

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
  background: linear-gradient(135deg, #0f0c29 0%, #1a1a4e 40%, #0d1b3e 100%);
  overflow: hidden;
  position: relative;
  font-family: 'Inter', system-ui, sans-serif;
}

/* ── Animated orbs ────────────────────────────── */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
  animation: float 8s ease-in-out infinite;
}
.orb-1 {
  width: 420px; height: 420px;
  background: radial-gradient(circle, #6366f1, #8b5cf6);
  top: -100px; left: -100px;
  animation-delay: 0s;
}
.orb-2 {
  width: 320px; height: 320px;
  background: radial-gradient(circle, #06b6d4, #3b82f6);
  bottom: -80px; right: -60px;
  animation-delay: 2.5s;
}
.orb-3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, #f472b6, #ec4899);
  top: 55%; left: 60%;
  animation-delay: 5s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(20px, -30px) scale(1.05); }
  66%       { transform: translate(-15px, 20px) scale(0.96); }
}

/* ── Glass card ───────────────────────────────── */
.glass-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  margin: 1rem;
  padding: 2.5rem 2rem;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(32px) saturate(180%);
  -webkit-backdrop-filter: blur(32px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow:
    0 32px 80px rgba(0, 0, 0, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    inset 0 -1px 0 rgba(255, 255, 255, 0.05);
  animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(30px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}

/* ── Logo ─────────────────────────────────────── */
.logo-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 1.25rem;
}
.logo-icon {
  width: 60px; height: 60px;
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.75rem;
  background: linear-gradient(135deg, rgba(99,102,241,0.8), rgba(139,92,246,0.8));
  box-shadow: 0 8px 32px rgba(99,102,241,0.45), inset 0 1px 0 rgba(255,255,255,0.25);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
}

/* ── Typography ───────────────────────────────── */
.title {
  text-align: center;
  font-size: 1.6rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  margin: 0 0 0.25rem;
}
.subtitle {
  text-align: center;
  font-size: 0.875rem;
  color: rgba(255,255,255,0.5);
  margin: 0 0 2rem;
}

/* ── Form ─────────────────────────────────────── */
.form { display: flex; flex-direction: column; gap: 1rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field label {
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(255,255,255,0.65);
  letter-spacing: 0.02em;
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
  opacity: 0.55;
  pointer-events: none;
  user-select: none;
}
.input-wrap input {
  width: 100%;
  padding: 0.75rem 2.8rem 0.75rem 2.8rem;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  color: #fff;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  backdrop-filter: blur(8px);
}
.input-wrap input::placeholder { color: rgba(255,255,255,0.25); }
.input-wrap input:focus {
  border-color: rgba(99,102,241,0.7);
  background: rgba(99,102,241,0.1);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.2);
}
.eye-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  opacity: 0.55;
  transition: opacity 0.2s;
  padding: 0;
  line-height: 1;
}
.eye-btn:hover { opacity: 1; }

/* ── Error ────────────────────────────────────── */
.error-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  background: rgba(239,68,68,0.15);
  border: 1px solid rgba(239,68,68,0.35);
  border-radius: 12px;
  color: #fca5a5;
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
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: 0 8px 24px rgba(99,102,241,0.4), inset 0 1px 0 rgba(255,255,255,0.2);
  letter-spacing: 0.01em;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 32px rgba(99,102,241,0.55), inset 0 1px 0 rgba(255,255,255,0.2);
}
.submit-btn:active:not(:disabled) { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* ── Loader spinner ───────────────────────────── */
.loader {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer ───────────────────────────────────── */
.footer-text {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.dot {
  width: 6px; height: 6px;
  background: #22c55e;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 6px #22c55e;
}
</style>
