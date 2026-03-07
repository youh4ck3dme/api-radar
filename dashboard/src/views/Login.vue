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
  background: #080808;
  overflow: hidden;
  position: relative;
  font-family: 'Inter', system-ui, sans-serif;
}

/* ── Animated orbs ────────────────────────────── */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  animation: float 9s ease-in-out infinite;
}
.orb-1 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(240,240,230,0.12), rgba(200,200,190,0.04));
  top: -120px; left: -80px;
  animation-delay: 0s;
}
.orb-2 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(220,220,210,0.09), rgba(180,180,170,0.03));
  bottom: -60px; right: -40px;
  animation-delay: 3s;
}
.orb-3 {
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(255,255,245,0.07), transparent);
  top: 50%; left: 58%;
  animation-delay: 6s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(18px, -25px) scale(1.04); }
  66%       { transform: translate(-12px, 18px) scale(0.97); }
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
  background: rgba(255, 255, 253, 0.04);
  backdrop-filter: blur(40px) saturate(160%);
  -webkit-backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 250, 0.1);
  box-shadow:
    0 40px 100px rgba(0, 0, 0, 0.7),
    0 0 0 1px rgba(255,255,255,0.04),
    inset 0 1px 0 rgba(255, 255, 250, 0.12),
    inset 0 -1px 0 rgba(255, 255, 255, 0.03);
  animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(28px) scale(0.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
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
  background: rgba(255,255,250,0.08);
  box-shadow:
    0 8px 32px rgba(0,0,0,0.5),
    inset 0 1px 0 rgba(255,255,255,0.15),
    inset 0 -1px 0 rgba(0,0,0,0.2);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.1);
}

/* ── Typography ───────────────────────────────── */
.title {
  text-align: center;
  font-size: 1.6rem;
  font-weight: 700;
  color: rgba(255,255,250,0.92);
  letter-spacing: -0.02em;
  margin: 0 0 0.25rem;
}
.subtitle {
  text-align: center;
  font-size: 0.875rem;
  color: rgba(255,255,250,0.38);
  margin: 0 0 2rem;
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
