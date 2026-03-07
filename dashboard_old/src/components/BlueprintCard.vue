<template>
  <div class="relative w-full rounded-3xl overflow-hidden flex items-center justify-center bg-gradient-to-b from-slate-900 to-slate-800 shadow-2xl" :style="{ minHeight: height }">
    
    <!-- Animated Accents Background -->
    <div class="accents absolute inset-0 pointer-events-none flex justify-center items-center overflow-hidden">
      <!-- Wobbling backdrop cards -->
      <div v-if="withAccents" class="acc-card acc-card-1"></div>
      <div v-if="withAccents" class="acc-card acc-card-2"></div>
      <div v-if="withAccents" class="acc-card acc-card-3"></div>
      
      <!-- Rotating lights -->
      <div v-if="withLights" class="light"></div>
      <div v-if="withLights" class="light sm"></div>
      <div v-if="withLights" class="top-light"></div>
    </div>

    <!-- Main Glassmorphic Card -->
    <div class="blueprint-card z-10 transition-transform duration-300 ease-out hover:-translate-y-1" :class="cardClass">
      <!-- Slots allow maximum reusability -->
      
      <div v-if="$slots.icon || icon" class="icon-wrapper mb-6 text-5xl opacity-90 drop-shadow-lg" :class="iconColorClass">
        <slot name="icon">{{ icon }}</slot>
      </div>
      
      <h2 v-if="$slots.title || title" class="text-2xl font-extrabold text-white tracking-tight mb-2">
        <slot name="title">{{ title }}</slot>
      </h2>
      
      <p v-if="$slots.description || description" class="text-[0.95em] font-medium text-slate-400 mb-6 leading-relaxed">
        <slot name="description">{{ description }}</slot>
      </p>

      <div v-if="$slots.action" class="mt-auto">
        <slot name="action"></slot>
      </div>
      <div v-else-if="actionText" class="button flex items-center gap-2 mt-auto" @click="$emit('action')">
        <span>{{ actionText }}</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  description: String,
  icon: String,
  actionText: String,
  height: {
    type: String,
    default: '550px'
  },
  iconColorClass: {
    type: String,
    default: 'text-blue-400 animate-pulse'
  },
  cardClass: {
    type: String,
    default: 'w-[360px] h-[440px]'
  },
  withAccents: {
    type: Boolean,
    default: true
  },
  withLights: {
    type: Boolean,
    default: true
  }
});

defineEmits(['action']);
</script>

<style scoped>
/* Leverage design tokens from tailwind.css */
.blueprint-card {
    position: relative;
    border-radius: 24px;
    background: linear-gradient(
        180deg,
        var(--color-glass-base, rgba(30, 58, 138, 0.4)) 0%,
        var(--color-glass-dark, rgba(15, 23, 42, 0.8)) 50%
    );
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: var(--shadow-glass-inner, inset 0 2px 2px 0 rgba(96, 165, 250, 0.3), inset 0 -2px 2px 0 rgba(0, 0, 0, 0.4), 0 15px 35px rgba(0,0,0,0.5));
    color: #f8fafc;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
    padding: 36px;
    display: flex; 
    flex-direction: column; 
}

.blueprint-card .button {
    width: fit-content;
    border-radius: 100px;
    padding: 12px 32px;
    font-weight: 600;
    font-size: 0.95em;
    background: rgba(255, 255, 255, 0.08);
    box-shadow: var(--shadow-glass-button, 0 0 0 1px rgba(255, 255, 255, 0.15), inset 120px 0 100px -100px rgba(0, 0, 0, 0.5), 0 0 0 0 rgba(255, 255, 255, 0.1));
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    color: #ffffff;
}

.blueprint-card .button:hover {
    box-shadow: var(--shadow-glass-button-hover, 0 0 0 1px rgba(96, 165, 250, 0.5), inset 200px 0px 100px -100px rgba(0, 0, 0, 0.3), 0 4px 12px rgba(59, 130, 246, 0.3));
    background: rgba(59, 130, 246, 0.15);
    transform: translateY(-2px);
}

/* Accents Background Elements */
.accents .acc-card {
    width: 370px; height: 460px;
    background: rgba(30, 58, 138, 0.1);
    opacity: 0.7;
    position: absolute;
    border-radius: 26px;
    box-shadow: inset 0 2px 2px 0 rgba(147, 197, 253, 0.15),
                inset 0 -2px 2px 0 rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    transition: all 0.1s linear;
    transform-origin: 50% 80%;
}

.acc-card-1 { animation: var(--animate-wobble-1, wobble 18s ease-in-out infinite); }
.acc-card-2 { animation: var(--animate-wobble-2, wobble 22s ease-in-out -6s infinite reverse); }
.acc-card-3 { animation: var(--animate-wobble-3, wobble 26s ease-in-out -18s infinite); }

.accents .light {
    --bgref: url("data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg id='Layer_1' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 487 487'%3E%3Ccircle cx='243' cy='243.5' r='233' style='fill:none; opacity:.15; stroke:%233b82f6; stroke-linecap:round; stroke-miterlimit:10; stroke-width:18px;'/%3E%3Ccircle cx='243.5' cy='243.5' r='243' style='fill:none; stroke:%231e3a8a; stroke-linecap:round; stroke-miterlimit:10;'/%3E%3Ccircle cx='243' cy='243.5' r='222' style='fill:none; stroke:%231e3a8a; stroke-linecap:round; stroke-miterlimit:10;'/%3E%3Cpath d='m10,243.5C10,114.82,114.32,10.5,243,10.5' style='fill:none; stroke:%2360a5fa; stroke-linecap:round; stroke-miterlimit:10; stroke-width:18px;'/%3E%3C/svg%3E");
    position: absolute;
    left: 50%; top: 50%;
    transform: translate(-50%, -50%);
    margin-left: -140px;
    margin-top: 40px;
    width: 220px; height: 220px;
    z-index: 0;
    background-image: var(--bgref);
    animation: var(--animate-rotate360, rotate360 22s linear infinite);
    background-size: contain;
}

.accents .light::before, .accents .light::after {
    content: ''; display: block;
    width: 100%; height: 100%;
    position: absolute;
    left: 0; right: 0; top: 0; bottom: 0;
    background-image: var(--bgref);
    filter: blur(5px);
    transform: scale(1.02);
    background-size: contain;
}

.accents .light::after {
    filter: blur(14px);
}

.accents .light.sm {
    width: 140px; height: 140px;
    margin-left: 170px;
    margin-top: -80px;
    animation: var(--animate-rotate360-fast, rotate360 18s linear -10s infinite);
}

.accents .top-light {
    position: absolute;
    left: 50%; top: -2px;
    transform: translateX(-50%);
    width: 280px;
    height: 4px;
    border-radius: 10px;
    background: #eff6ff; 
    box-shadow: 
        0 0px 2px 1px #93c5fd,
        0 2px 6px 1px #60a5fa,
        0 6px 14px 2px #3b82f688,
        0 12px 24px 4px #2563eb66,
        0 20px 40px 10px #1d4ed844;
}

@media screen and (max-width: 768px) {
    .blueprint-card {
        width: 90%;
        height: auto;
        min-height: 380px;
    }
    .accents .acc-card { width: 95%; height: 400px; }
    .accents .top-light { width: 200px; }
}
</style>
