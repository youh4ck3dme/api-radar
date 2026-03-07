<template>
  <div class="relative w-full h-[550px] rounded-3xl overflow-hidden flex items-center justify-center mb-8 bg-gradient-to-b from-slate-900 to-slate-800 shadow-2xl">
    
    <!-- Animated Accents Background -->
    <div class="accents absolute inset-0 pointer-events-none flex justify-center items-center">
      <div class="acc-card"></div>
      <div class="acc-card"></div>
      <div class="acc-card"></div>
      <div class="light"></div>
      <div class="light sm"></div>
      <div class="top-light"></div>
    </div>

    <!-- Main Glassmorphic Card -->
    <div class="hero-card z-10">
      <div class="icon-placeholder mb-6 text-5xl text-blue-400 opacity-90 animate-pulse drop-shadow-lg">
        🌐
      </div>
      <h2>API Centrum</h2>
      <p>Inteligentná správa domén a SSL certifikátov na jednom mieste. Zjednodušte si prácu s naším centrálnym systémom.</p>
      <div class="button flex items-center gap-2">
        <span>Začať správu</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
// HeroCard component to display a stylish 3D animated hero section
</script>

<style scoped>
.hero-card {
    position: relative;
    width: 360px; 
    height: 440px;
    border-radius: 24px;
    background: linear-gradient(
        180deg,
        rgba(30, 58, 138, 0.4) 0%, /* tailwind blue-900 */
        rgba(15, 23, 42, 0.8) 50% /* tailwind slate-900 */
    );
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: inset 0 2px 2px 0 rgba(96, 165, 250, 0.3), /* text-blue-400 */
                inset 0 -2px 2px 0 rgba(0, 0, 0, 0.4),
                0 15px 35px rgba(0,0,0,0.5);
    
    color: #f8fafc;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
    padding: 36px;
    display: flex; 
    flex-direction: column; 
    justify-content: flex-end;
    transition: transform 0.3s ease;
}

.hero-card:hover {
    transform: translateY(-4px);
}

.hero-card h2 {
    font-size: 1.8em;
    font-weight: 800;
    margin: 8px 0;
    color: #ffffff;
    letter-spacing: -0.02em;
}

.hero-card p {
    font-size: 0.95em;
    font-weight: 500;
    color: #94a3b8; /* slate-400 */
    margin: 12px 0 24px 0;
    line-height: 1.6;
}

.hero-card .button {
    width: fit-content;
    border-radius: 100px;
    padding: 12px 32px;
    font-weight: 600;
    font-size: 0.95em;
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 
        0 0 0 1px rgba(255, 255, 255, 0.15), 
        inset 120px 0 100px -100px rgba(0, 0, 0, 0.5), 
        0 0 0 0 rgba(255, 255, 255, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    color: #ffffff;
}

.hero-card .button:hover {
    box-shadow: 
        0 0 0 1px rgba(96, 165, 250, 0.5), /* blue-400 ring */
        inset 200px 0px 100px -100px rgba(0, 0, 0, 0.3), 
        0 4px 12px rgba(59, 130, 246, 0.3); /* blue glow */
    background: rgba(59, 130, 246, 0.15);
    transform: translateY(-2px);
}

/* Accents Background Elements */
.accents .acc-card {
    width: 370px; height: 460px;
    background: rgba(30, 58, 138, 0.1); /* light hint of blue */
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

.accents .acc-card:nth-child(1) { animation: wobble 18s ease-in-out infinite; }
.accents .acc-card:nth-child(2) { animation: wobble 22s ease-in-out -6s infinite reverse; }
.accents .acc-card:nth-child(3) { animation: wobble 26s ease-in-out -18s infinite; }

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
    animation: rotate360 22s linear infinite;
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
    animation: rotate360 18s linear -10s infinite;
}

.accents .top-light {
    position: absolute;
    left: 50%; top: -2px;
    transform: translateX(-50%);
    width: 280px;
    height: 4px;
    border-radius: 10px;
    background: #eff6ff; /* blue-50 */
    box-shadow: 
        0 0px 2px 1px #93c5fd,
        0 2px 6px 1px #60a5fa,
        0 6px 14px 2px #3b82f688,
        0 12px 24px 4px #2563eb66,
        0 20px 40px 10px #1d4ed844;
}

@keyframes rotate360 { 
    to { transform: translate(-50%, -50%) rotate(360deg); } 
}

@keyframes wobble {
    0% { transform: translateX(8px) translateY(15px) rotate(-2deg) scale(1); }
    20% { transform: translateX(-35px) translateY(-8px) rotate(4deg) scale(1.01); }
    60% { transform: translateX(25px) translateY(12px) rotate(-5deg) scale(1); }
    80% { transform: translateX(-30px) translateY(-18px) rotate(8deg) scale(0.97); }
    100% { transform: translateX(8px) translateY(15px) rotate(-2deg) scale(1); }
}

@media screen and (max-width: 768px) {
    .hero-card {
        width: 90%;
        height: auto;
        min-height: 380px;
    }
    .accents .acc-card {
        width: 95%;
        height: 400px;
    }
    .accents .top-light {
        width: 200px;
    }
}
</style>
