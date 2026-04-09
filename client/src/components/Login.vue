<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const isRegistering = ref(false); // Состояние: Вход или Регистрация
const showPassword = ref(false);

const API_URL = 'http://127.0.0.1:8000';

const handleSubmit = async () => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email.value);
    formData.append('password', password.value);

    if (isRegistering.value) {
      await axios.post(`${API_URL}/auth/register`, null, {
        params: { email: email.value, password: password.value },
      });
      alert('Аккаунт создан! Входим...');
    }

    const response = await axios.post(`${API_URL}/token`, formData);

    localStorage.setItem('token', response.data.access_token);

    router.push('/');
  } catch (error) {
    console.error(error);
    const msg = error.response?.data?.detail || 'Ошибка авторизации';
    alert(msg);
  }
};
</script>

<template>
  <div class="bg-background text-on-surface font-['Outfit'] min-h-screen flex flex-col items-center justify-center p-6 mesh-bg relative overflow-x-hidden">
    
    <div class="data-line-grid"></div>
    <div class="noise"></div>
    <div class="fixed inset-0 data-dot-grid pointer-events-none"></div>

    <div class="fixed inset-0 -z-10 pointer-events-none">
        <div class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary-light/30 rounded-full blur-[120px] animate-blob"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[120px] animate-blob" style="animation-delay: 4s;"></div>
    </div>

    <div class="fixed inset-0 pointer-events-none">
        <div class="absolute top-[15%] left-[20%] animate-float-slow opacity-20" style="animation-delay: -6s;">
            <div class="flex flex-col -space-y-4 rotate-12">
                <div class="w-16 h-10 bg-primary/20 border border-primary/30 rounded-lg transform skew-x-12"></div>
                <div class="w-16 h-10 bg-primary/10 border border-primary/30 rounded-lg transform skew-x-12"></div>
                <div class="w-16 h-10 bg-white/40 border border-primary/30 rounded-lg transform skew-x-12 backdrop-blur-sm"></div>
            </div>
        </div>

        <div class="absolute bottom-[40%] left-[5%] animate-float-slow opacity-40" style="animation-delay: -3s;">
            <div class="relative w-20 h-20 border border-primary/30 rounded-full flex items-center justify-center">
                <div class="w-10 h-10 border border-primary-light/40 rounded-lg rotate-45 animate-spin-slow" style="animation-duration: 8s;"></div>
                <div class="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-primary-light rounded-full"></div>
            </div>
        </div>

        <div class="absolute bottom-[0%] left-[25%] animate-float-reverse opacity-100">
            <div class="flex flex-col items-center gap-4">
                <div class="w-3 h-3 rounded-full bg-primary-light shadow-[0_0_15px_rgba(255,146,56,0.6)]"></div>
                <div class="w-px h-20 bg-gradient-to-b from-primary-light to-transparent"></div>
            </div>
        </div>

        <div class="absolute top-[20%] right-[12%] animate-float-fast opacity-60">
            <div class="data-chip p-3 rotate-6">
                <div class="flex gap-1.5">
                    <div class="w-2 h-2 rounded-full bg-primary/20"></div>
                    <div class="w-12 h-2 rounded-full bg-primary/10"></div>
                </div>
                <div class="w-20 h-2 bg-primary/5 rounded-full mt-2"></div>
            </div>
        </div>

        <div class="absolute bottom-[10%] right-[10%] animate-float-slow">
            <div class="w-32 h-32 rounded-3xl border-4 border-dashed border-primary/10 flex items-center justify-center rotate-12">
                <span class="material-symbols-outlined text-primary/10 text-6xl">database</span>
            </div>
        </div>
    </div>

    <main class="relative z-50 w-full max-w-[460px]">
        <div class="glass-card rounded-[3rem] p-10 md:p-12 relative overflow-x-hidden group">
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-[2px] bg-gradient-to-r from-transparent via-primary-light to-transparent shadow-[0_0_15px_rgba(255,146,56,0.5)]"></div>
            
            <div class="flex flex-col items-center mb-10 text-center">
                <div class="relative group cursor-pointer mb-4">
                    <div class="w-16 h-16 bg-gradient-to-tr from-primary-dark to-primary-light rounded-2xl flex items-center justify-center rotate-3 shadow-xl group-hover:rotate-6 transition-transform">
                        <span class="material-symbols-outlined text-white text-4xl">hub</span>
                    </div>

                    <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center shadow-md">
                        <div class="w-2.5 h-2.5 bg-primary-light rounded-full animate-pulse"></div>
                    </div>
                </div>

                <h1 class="text-4xl font-extrabold tracking-tight text-on-surface">Airelav</h1>
                <p class="text-xs font-bold text-primary-light uppercase tracking-[0.3em] mt-2 opacity-80">
                  Dataset Engine
                </p>
            </div>

            <form class="space-y-6" @submit.prevent="handleSubmit">
                <div class="space-y-2">
                    <label class="text-[11px] font-bold uppercase tracking-widest text-primary/70 ml-4 block">Email Address</label>
                    <div class="relative">
                        <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-primary/40">mail</span>
                        <input 
                            v-model="email"
                            required
                            type="email"
                            placeholder="address@mail.ru" 
                            class="w-full h-14 pl-12 pr-6 bg-white/50 border border-primary/10 rounded-2xl text-sm font-medium focus:ring-4 focus:ring-primary-light/10 focus:border-primary-light transition-all outline-none" 
                        />
                    </div>
                </div>
                
                <div class="space-y-2">
                    <div class="flex justify-between items-center px-4">
                        <label class="text-[11px] font-bold uppercase tracking-widest text-primary/70">Password</label>
                        <a v-if="!isRegistering" class="text-[11px] font-extrabold text-primary-light hover:underline" href="#">Forgot password?</a>
                    </div>
                    <div class="relative">
                        <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-primary/40">key</span>
                        <input 
                            v-model="password"
                            required
                            :type="showPassword ? 'text' : 'password'"
                            placeholder="••••••••" 
                            class="w-full h-14 pl-12 pr-12 bg-white/50 border border-primary/10 rounded-2xl text-sm font-medium focus:ring-4 focus:ring-primary-light/10 focus:border-primary-light transition-all outline-none" 
                        />
                        <button 
                            type="button" 
                            @click="showPassword = !showPassword"
                            class="absolute right-4 top-1/2 -translate-y-1/2 text-primary/40 hover:text-primary transition-colors"
                        >
                            <span class="material-symbols-outlined text-xl">
                                {{ showPassword ? 'visibility_off' : 'visibility' }}
                            </span>
                        </button>
                    </div>
                </div>

                <button class="w-full h-14 rounded-2xl bg-gradient-to-r from-primary-dark via-primary to-primary-light text-white font-bold text-sm uppercase tracking-[0.2em] shadow-xl shadow-primary/30 hover:shadow-primary/50 hover:brightness-110 active:scale-[0.98] transition-all duration-300 mt-4 relative overflow-x-hidden group/btn" type="submit">
                    <span class="relative z-10">{{ isRegistering ? 'SIGN UP' : 'SIGN IN' }}</span>
                    <div class="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover/btn:translate-x-[100%] transition-transform duration-700 skew-x-[-20deg]"></div>
                </button>
            </form>

            <div class="mt-10">
                <div class="relative flex items-center gap-4 mb-6">
                    <div class="h-px flex-1 bg-gradient-to-r from-transparent to-primary/10"></div>
                    <span class="text-[10px] font-bold uppercase tracking-[0.2em] text-primary/30">
                        {{ isRegistering ? 'OR REGISTER WITH' : 'OR LOGIN WITH' }}
                    </span>
                    <div class="h-px flex-1 bg-gradient-to-l from-transparent to-primary/10"></div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <button class="flex items-center justify-center gap-2 h-12 rounded-xl bg-white/50 border border-primary/5 hover:bg-white hover:border-primary/20 transition-all shadow-sm group">
                        <img src="https://www.svgrepo.com/show/475656/google-color.svg" class="w-4 h-4 grayscale group-hover:grayscale-0 transition-all" alt="">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-primary/60">Google</span>
                    </button>
                    <button class="flex items-center justify-center gap-2 h-12 rounded-xl bg-white/50 border border-primary/5 hover:bg-white hover:border-primary/20 transition-all shadow-sm group">
                        <img src="https://www.svgrepo.com/show/475654/github-color.svg" class="w-4 h-4 grayscale group-hover:grayscale-0 transition-all" alt="">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-primary/60">GitHub</span>
                    </button>
                </div>
            </div>
        </div>

        <p class="text-center mt-8 text-primary/60 font-medium">
            {{ isRegistering ? 'Already have an account?' : "Don't have an account?" }}
            <a 
                href="#"
                @click.prevent="isRegistering = !isRegistering"
                class="text-primary-light font-extrabold hover:text-primary transition-colors border-b-2 border-primary-light/20 hover:border-primary-light ml-1" 
            >
                {{ isRegistering ? 'Sign In' : 'Sign Up' }}
            </a>
        </p>
    </main>

    <div class="mt-16 w-full max-w-[1000px] grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 mb-10 hidden md:grid">
        <div class="bg-white/30 backdrop-blur-md p-6 rounded-3xl border border-white/50 hover:bg-white/50 transition-all cursor-default">
            <div class="text-primary mb-3"><span class="material-symbols-outlined text-[22px]">auto_awesome</span></div>
            <h4 class="font-bold text-sm text-on-surface">Intelligent Design</h4>
            <p class="text-xs text-primary/60 mt-1">Leverage generative tools to accelerate your workflow.</p>
        </div>
        <div class="bg-white/30 backdrop-blur-md p-6 rounded-3xl border border-white/50 hover:bg-white/50 transition-all cursor-default">
            <div class="text-primary mb-3"><span class="material-symbols-outlined text-[22px]">security</span></div>
            <h4 class="font-bold text-sm text-on-surface">Enterprise Grade</h4>
            <p class="text-xs text-primary/60 mt-1">Built with the highest security standards for data privacy.</p>
        </div>
        <div class="bg-white/30 backdrop-blur-md p-6 rounded-3xl border border-white/50 hover:bg-white/50 transition-all cursor-default">
            <div class="text-primary mb-3"><span class="material-symbols-outlined text-[22px]">cloud_done</span></div>
            <h4 class="font-bold text-sm text-on-surface">Instant Sync</h4>
            <p class="text-xs text-primary/60 mt-1">Your projects are synchronized across all devices.</p>
        </div>
    </div>
  </div>
</template>

<style scoped>
.glass-card { 
    background: rgba(255, 255, 255, 0.75); 
    backdrop-filter: blur(20px) saturate(160%); 
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow: 0 30px 60px -12px rgba(148, 74, 0, 0.2);
}
.mesh-bg {
    background-image: 
        radial-gradient(at 0% 0%, rgba(255, 146, 56, 0.2) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(148, 74, 0, 0.1) 0px, transparent 50%);
}
.data-dot-grid {
    background-image: radial-gradient(rgba(148, 74, 0, 0.1) 1px, transparent 1px);
    background-size: 40px 40px;
}
.noise {
    position: absolute;
    inset: 0; z-index: -1; opacity: 0.04; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
.data-chip {
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(148, 74, 0, 0.1);
    border-radius: 12px;
}
.data-line-grid {
    position: absolute;
    inset: 0;
    z-index: -1;
    background-image: 
        linear-gradient(to right, rgba(148, 74, 0, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(148, 74, 0, 0.05) 1px, transparent 1px);
    background-size: 70px 70px;
}
</style>