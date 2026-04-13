<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

import { useToast } from 'vue-toastification';
const toast = useToast();

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
      toast.success('Аккаунт создан! Входим...');
    }

    const response = await axios.post(`${API_URL}/token`, formData);

    localStorage.setItem('token', response.data.access_token);

    router.push('/');
  } catch (error) {
    console.error(error);
    const msg = error.response?.data?.detail || 'Ошибка авторизации';
    toast.error(msg);
  }
};

const loginWithGithub = () => {
  // Перенаправляем пользователя на эндпоинт бэкенда
  window.location.href = `${API_URL}/auth/github/login`;
};

const loginWithGoogle = () => {
  // Аналогично для Google, когда настроите его на бэкенде
  window.location.href = `${API_URL}/auth/google/login`;
};

import BaseModal from './common/BaseModal.vue';

const showForgotModal = ref(false);
const forgotEmail = ref('');
const isSendingReset = ref(false);

const handleForgotPassword = async () => {
  if (!forgotEmail.value) {
    toast.warning('Please enter your email');
    return;
  }

  isSendingReset.value = true;
  try {
    const res = await axios.post(`${API_URL}/auth/forgot-password`, {
      email: forgotEmail.value,
    });
    showForgotModal.value = false;

    // ЭМУЛЯЦИЯ ПИСЬМА: Показываем ссылку прямо в тосте (для защиты диплома)
    if (res.data.demo_link) {
      toast.success('Link generated! (Check console for demo link)', {
        timeout: 5000,
      });
      console.log('DEMO RESET LINK:', res.data.demo_link);

      // Для удобства тестирования можно сразу перекинуть юзера
      // window.location.href = res.data.demo_link;
    } else {
      toast.success(res.data.message);
    }
  } catch (error) {
    toast.error('Failed to process request');
  } finally {
    isSendingReset.value = false;
  }
};
</script>

<template>
  <div
    class="mesh-bg relative flex min-h-screen flex-col items-center justify-center overflow-x-hidden bg-background p-6 font-['Outfit'] text-on-surface"
  >
    <BaseModal
      :show="showForgotModal"
      title="Reset Password"
      description="Enter your email address and we'll send you a link to reset your password."
      confirm-text="Send Link"
      @close="showForgotModal = false"
      @confirm="handleForgotPassword"
    >
      <div class="mb-6 mt-2">
        <input
          v-model="forgotEmail"
          type="email"
          placeholder="you@example.com"
          class="w-full rounded-xl border border-primary/20 bg-white/50 p-3 text-sm font-medium outline-none focus:ring-2 focus:ring-primary"
          @keyup.enter="handleForgotPassword"
        />
      </div>
    </BaseModal>
    <div class="data-line-grid"></div>
    <div class="noise"></div>
    <div class="data-dot-grid pointer-events-none fixed inset-0"></div>

    <div class="pointer-events-none fixed inset-0 -z-10">
      <div
        class="absolute left-[-10%] top-[-10%] h-[50%] w-[50%] animate-blob rounded-full bg-primary-light/30 blur-[120px]"
      ></div>
      <div
        class="absolute bottom-[-10%] right-[-10%] h-[50%] w-[50%] animate-blob rounded-full bg-primary/20 blur-[120px]"
        style="animation-delay: 4s"
      ></div>
    </div>

    <div class="pointer-events-none fixed inset-0">
      <div
        class="absolute left-[20%] top-[15%] animate-float-slow opacity-20"
        style="animation-delay: -6s"
      >
        <div class="flex rotate-12 flex-col -space-y-4">
          <div
            class="h-10 w-16 skew-x-12 transform rounded-lg border border-primary/30 bg-primary/20"
          ></div>
          <div
            class="h-10 w-16 skew-x-12 transform rounded-lg border border-primary/30 bg-primary/10"
          ></div>
          <div
            class="h-10 w-16 skew-x-12 transform rounded-lg border border-primary/30 bg-white/40 backdrop-blur-sm"
          ></div>
        </div>
      </div>

      <div
        class="absolute bottom-[40%] left-[5%] animate-float-slow opacity-40"
        style="animation-delay: -3s"
      >
        <div
          class="relative flex h-20 w-20 items-center justify-center rounded-full border border-primary/30"
        >
          <div
            class="h-10 w-10 rotate-45 animate-spin-slow rounded-lg border border-primary-light/40"
            style="animation-duration: 8s"
          ></div>
          <div
            class="absolute left-1/2 top-0 h-2 w-2 -translate-x-1/2 rounded-full bg-primary-light"
          ></div>
        </div>
      </div>

      <div
        class="absolute bottom-[0%] left-[25%] animate-float-reverse opacity-100"
      >
        <div class="flex flex-col items-center gap-4">
          <div
            class="h-3 w-3 rounded-full bg-primary-light shadow-[0_0_15px_rgba(255,146,56,0.6)]"
          ></div>
          <div
            class="h-20 w-px bg-gradient-to-b from-primary-light to-transparent"
          ></div>
        </div>
      </div>

      <div class="absolute right-[12%] top-[20%] animate-float-fast opacity-60">
        <div class="data-chip rotate-6 p-3">
          <div class="flex gap-1.5">
            <div class="h-2 w-2 rounded-full bg-primary/20"></div>
            <div class="h-2 w-12 rounded-full bg-primary/10"></div>
          </div>
          <div class="mt-2 h-2 w-20 rounded-full bg-primary/5"></div>
        </div>
      </div>

      <div class="absolute bottom-[10%] right-[10%] animate-float-slow">
        <div
          class="flex h-32 w-32 rotate-12 items-center justify-center rounded-3xl border-4 border-dashed border-primary/10"
        >
          <span class="material-symbols-outlined text-6xl text-primary/10"
            >database</span
          >
        </div>
      </div>
    </div>

    <main class="relative z-50 w-full max-w-[460px]">
      <div
        class="glass-card group relative overflow-x-hidden rounded-[3rem] p-10 md:p-12"
      >
        <div
          class="absolute left-1/2 top-0 h-[2px] w-3/4 -translate-x-1/2 bg-gradient-to-r from-transparent via-primary-light to-transparent shadow-[0_0_15px_rgba(255,146,56,0.5)]"
        ></div>

        <div class="mb-10 flex flex-col items-center text-center">
          <div class="group relative mb-4 cursor-pointer">
            <div
              class="flex h-16 w-16 rotate-3 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary-dark to-primary-light shadow-xl transition-transform group-hover:rotate-6"
            >
              <span class="material-symbols-outlined text-4xl text-white"
                >hub</span
              >
            </div>

            <div
              class="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-white shadow-md"
            >
              <div
                class="h-2.5 w-2.5 animate-pulse rounded-full bg-primary-light"
              ></div>
            </div>
          </div>

          <h1 class="text-4xl font-extrabold tracking-tight text-on-surface">
            Airelav
          </h1>
          <p
            class="mt-2 text-xs font-bold uppercase tracking-[0.3em] text-primary-light opacity-80"
          >
            Dataset Engine
          </p>
        </div>

        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div class="space-y-2">
            <label
              class="ml-4 block text-[11px] font-bold uppercase tracking-widest text-primary/70"
              >Email Address</label
            >
            <div class="relative">
              <span
                class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-primary/40"
                >mail</span
              >
              <input
                v-model="email"
                required
                type="email"
                placeholder="address@mail.ru"
                class="h-14 w-full rounded-2xl border border-primary/10 bg-white/50 pl-12 pr-6 text-sm font-medium outline-none transition-all focus:border-primary-light focus:ring-4 focus:ring-primary-light/10"
              />
            </div>
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-between px-4">
              <label
                class="text-[11px] font-bold uppercase tracking-widest text-primary/70"
                >Password</label
              >
              <a
                v-if="!isRegistering"
                class="cursor-pointer text-[11px] font-extrabold text-primary-light hover:underline"
                href="#"
                @click.prevent="showForgotModal = true"
              >
                Forgot password?
              </a>
            </div>
            <div class="relative">
              <span
                class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-primary/40"
                >key</span
              >
              <input
                v-model="password"
                required
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="h-14 w-full rounded-2xl border border-primary/10 bg-white/50 pl-12 pr-12 text-sm font-medium outline-none transition-all focus:border-primary-light focus:ring-4 focus:ring-primary-light/10"
              />
              <button
                type="button"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-primary/40 transition-colors hover:text-primary"
                @click="showPassword = !showPassword"
              >
                <span class="material-symbols-outlined text-xl">
                  {{ showPassword ? 'visibility_off' : 'visibility' }}
                </span>
              </button>
            </div>
          </div>

          <button
            class="group/btn relative mt-4 h-14 w-full overflow-x-hidden rounded-2xl bg-gradient-to-r from-primary-dark via-primary to-primary-light text-sm font-bold uppercase tracking-[0.2em] text-white shadow-xl shadow-primary/30 transition-all duration-300 hover:shadow-primary/50 hover:brightness-110 active:scale-[0.98]"
            type="submit"
          >
            <span class="relative z-10">{{
              isRegistering ? 'SIGN UP' : 'SIGN IN'
            }}</span>
            <div
              class="absolute inset-0 translate-x-[-100%] skew-x-[-20deg] bg-white/20 transition-transform duration-700 group-hover/btn:translate-x-[100%]"
            ></div>
          </button>
        </form>

        <div class="mt-10">
          <div class="relative mb-6 flex items-center gap-4">
            <div
              class="h-px flex-1 bg-gradient-to-r from-transparent to-primary/10"
            ></div>
            <span
              class="text-[10px] font-bold uppercase tracking-[0.2em] text-primary/30"
            >
              {{ isRegistering ? 'OR REGISTER WITH' : 'OR LOGIN WITH' }}
            </span>
            <div
              class="h-px flex-1 bg-gradient-to-l from-transparent to-primary/10"
            ></div>
          </div>

          <div class="mt-6 w-full">
            <button
              type="button"
              class="group flex h-12 w-full items-center justify-center gap-3 rounded-xl border border-primary/10 bg-white/50 transition-all duration-300 hover:border-primary/30 hover:bg-white hover:shadow-md"
              @click="loginWithGithub"
            >
              <img
                src="https://www.svgrepo.com/show/475654/github-color.svg"
                class="h-5 w-5 grayscale transition-all duration-300 group-hover:grayscale-0"
                alt="GitHub Logo"
              />
              <span
                class="text-xs font-extrabold uppercase tracking-[0.15em] text-primary/70 transition-colors group-hover:text-primary"
              >
                Continue with GitHub
              </span>
            </button>
          </div>
        </div>
      </div>

      <p class="mt-8 text-center font-medium text-primary/60">
        {{
          isRegistering ? 'Already have an account?' : "Don't have an account?"
        }}
        <a
          href="#"
          class="ml-1 border-b-2 border-primary-light/20 font-extrabold text-primary-light transition-colors hover:border-primary-light hover:text-primary"
          @click.prevent="isRegistering = !isRegistering"
        >
          {{ isRegistering ? 'Sign In' : 'Sign Up' }}
        </a>
      </p>
    </main>

    <div
      class="relative z-10 mb-10 mt-16 grid hidden w-full max-w-[1000px] grid-cols-1 gap-6 md:grid md:grid-cols-3"
    >
      <div
        class="cursor-default rounded-3xl border border-white/50 bg-white/30 p-6 backdrop-blur-md transition-all hover:bg-white/50"
      >
        <div class="mb-3 text-primary">
          <span class="material-symbols-outlined text-[22px]"
            >auto_awesome</span
          >
        </div>
        <h4 class="text-sm font-bold text-on-surface">Intelligent Design</h4>
        <p class="mt-1 text-xs text-primary/60">
          Leverage generative tools to accelerate your workflow.
        </p>
      </div>
      <div
        class="cursor-default rounded-3xl border border-white/50 bg-white/30 p-6 backdrop-blur-md transition-all hover:bg-white/50"
      >
        <div class="mb-3 text-primary">
          <span class="material-symbols-outlined text-[22px]">security</span>
        </div>
        <h4 class="text-sm font-bold text-on-surface">Enterprise Grade</h4>
        <p class="mt-1 text-xs text-primary/60">
          Built with the highest security standards for data privacy.
        </p>
      </div>
      <div
        class="cursor-default rounded-3xl border border-white/50 bg-white/30 p-6 backdrop-blur-md transition-all hover:bg-white/50"
      >
        <div class="mb-3 text-primary">
          <span class="material-symbols-outlined text-[22px]">cloud_done</span>
        </div>
        <h4 class="text-sm font-bold text-on-surface">Instant Sync</h4>
        <p class="mt-1 text-xs text-primary/60">
          Your projects are synchronized across all devices.
        </p>
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
  inset: 0;
  z-index: -1;
  opacity: 0.04;
  pointer-events: none;
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
