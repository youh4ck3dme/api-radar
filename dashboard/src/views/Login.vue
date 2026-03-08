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

/* ── Animated orbs ────────────────────────────── */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  animation: float 15s ease-in-out infinite;
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(30, 58, 138, 0.3), rgba(30, 58, 138, 0.05));
  top: -10%; left: -10%;
  animation-delay: 0s;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.2), rgba(14, 165, 233, 0.05));
  bottom: -10%; right: -10%;
  animation-delay: 5s;
}
.orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.2), transparent);
  top: 40%; left: 50%;
  animation-delay: -3s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1) rotate(0deg); }
  33%       { transform: translate(30px, -40px) scale(1.1) rotate(5deg); }
  66%       { transform: translate(-20px, 20px) scale(0.9) rotate(-3deg); }
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
