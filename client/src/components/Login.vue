<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const isRegistering = ref(false);
const showPassword = ref(false);

const API_URL = 'http://127.0.0.1:8000';

const handleSubmit = async () => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email.value);
    formData.append('password', password.value);

    if (isRegistering.value) {
      await axios.post(`${API_URL}/auth/register`, null, {
        params: { email: email.value, password: password.value }
      });
      alert("Аккаунт создан! Входим...");
    }

    const response = await axios.post(`${API_URL}/token`, formData);
    
    localStorage.setItem('token', response.data.access_token);
    
    router.push('/');
    
  } catch (error) {
    console.error(error);
    const msg = error.response?.data?.detail || "Ошибка авторизации";
    alert(msg);
  }
};
</script>

<template>
  <div class="flex h-screen w-full overflow-hidden bg-white font-sans">

    <div class="relative hidden flex-col justify-between overflow-hidden bg-slate-900 text-white lg:flex lg:w-1/2">
        
        <div class="absolute inset-0 z-0 bg-gradient-to-br from-blue-900 via-slate-900 to-indigo-900"></div>
        <div class="pattern-grid absolute inset-0 z-0 opacity-20"></div>
        
        <div class="absolute left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-blue-500 opacity-20 blur-3xl mix-blend-multiply filter"></div>
        <div class="absolute bottom-1/4 right-1/4 h-96 w-96 animate-pulse rounded-full bg-purple-500 opacity-20 blur-3xl mix-blend-multiply filter" style="animation-delay: 2s"></div>

        <div class="relative z-10 flex h-full flex-col justify-between p-12">
            <div class="flex items-center space-x-3">
                <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
                    <i class="fas fa-cube text-lg text-white"></i>
                </div>
                <span class="text-3xl font-bold tracking-tight">AIrelav</span>
            </div>

            <div class="max-w-md">
                <h2 class="mb-6 text-4xl font-bold leading-tight">
                  Генерируйте данные<br> силой мысли.
                </h2>
                <p class="text-lg leading-relaxed text-slate-400">
                    Превратите текстовые описания в структурированные датасеты JSON, CSV или Excel за считанные секунды. Идеально для тестирования и ML.
                </p>
            </div>

            <div class="flex items-center space-x-4">
                <div class="flex -space-x-2">
                    <img class="h-8 w-8 rounded-full border-2 border-slate-900" src="https://i.pravatar.cc/100?img=33" alt="User">
                    <img class="h-8 w-8 rounded-full border-2 border-slate-900" src="https://i.pravatar.cc/100?img=47" alt="User">
                    <img class="h-8 w-8 rounded-full border-2 border-slate-900" src="https://i.pravatar.cc/100?img=12" alt="User">
                </div>
                <p class="text-sm font-medium text-slate-500">Присоединяйтесь к разработчикам</p>
            </div>
        </div>
    </div>

    <div class="relative flex w-full items-center justify-center bg-white p-8 lg:w-1/2">
        <div class="absolute left-6 top-6 flex items-center space-x-2 lg:hidden">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
                <i class="fas fa-cube text-xs text-white"></i>
            </div>
            <span class="font-bold text-slate-900">AIrelav</span>
        </div>

        <div class="w-full max-w-md fade-in-up">
            <div class="mb-10">
                <h1 class="mb-2 text-3xl font-bold text-slate-900">
                  {{ isRegistering ? 'Создать аккаунт' : 'С возвращением!' }}
                </h1>
                <p class="text-slate-500">
                  {{ isRegistering ? 'Заполните данные для регистрации.' : 'Введите данные для доступа.' }}
                </p>
            </div>

            <div class="mb-6 grid grid-cols-2 gap-4">
                <button class="flex items-center justify-center space-x-2 rounded-xl border border-slate-200 py-2.5 transition-colors hover:bg-slate-50">
                    <i class="fab fa-google text-red-500"></i>
                    <span class="text-sm font-medium text-slate-700">Google</span>
                </button>
                <button class="flex items-center justify-center space-x-2 rounded-xl border border-slate-200 py-2.5 transition-colors hover:bg-slate-50">
                    <i class="fab fa-github text-slate-900"></i>
                    <span class="text-sm font-medium text-slate-700">GitHub</span>
                </button>
            </div>

            <div class="relative mb-6 flex items-center py-2">
                <div class="flex-grow border-t border-slate-200"></div>
                <span class="mx-4 flex-shrink-0 text-xs font-medium uppercase text-slate-400">Или через email</span>
                <div class="flex-grow border-t border-slate-200"></div>
            </div>

            <form class="space-y-5" @submit.prevent="handleSubmit">
                <div>
                    <label class="mb-1.5 block text-sm font-medium text-slate-700">Email адрес</label>
                    <input 
                        v-model="email"
                        type="email" 
                        required
                        placeholder="name@company.com" 
                        class="w-full rounded-xl border border-slate-300 px-4 py-3 text-slate-900 placeholder-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                    >
                </div>

                <div>
                    <div class="mb-1.5 flex items-center justify-between">
                        <label class="block text-sm font-medium text-slate-700">Пароль</label>
                        <a v-if="!isRegistering" href="#" class="text-sm font-medium text-blue-600 hover:text-blue-500">Забыли пароль?</a>
                    </div>
                    <div class="relative">
                        <input 
                            v-model="password"
                            :type="showPassword ? 'text' : 'password'"
                            required
                            placeholder="••••••••" 
                            class="w-full rounded-xl border border-slate-300 px-4 py-3 text-slate-900 placeholder-slate-400 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                        >
                        <button 
                          type="button" 
                          @click="showPassword = !showPassword"
                          class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                        >
                            <i :class="showPassword ? 'far fa-eye-slash' : 'far fa-eye'"></i>
                        </button>
                    </div>
                </div>

                <button 
                  type="submit"
                  class="w-full transform rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 py-3.5 font-bold text-white shadow-lg shadow-blue-500/30 transition-all hover:from-blue-700 hover:to-indigo-700 active:scale-[0.98]"
                >
                    {{ isRegistering ? 'Зарегистрироваться' : 'Войти в аккаунт' }}
                </button>
            </form>

            <p class="mt-8 text-center text-sm text-slate-600">
                {{ isRegistering ? 'Уже есть аккаунт?' : 'Нет аккаунта?' }}
                <button 
                  @click="isRegistering = !isRegistering" 
                  class="font-semibold text-blue-600 transition-colors hover:text-blue-500 ml-1"
                >
                  {{ isRegistering ? 'Войти' : 'Создать бесплатно' }}
                </button>
            </p>
        </div>
        
        <div class="absolute bottom-6 w-full text-center">
            <div class="space-x-4 text-xs text-slate-400">
                <a href="#" class="hover:text-slate-600">Privacy Policy</a>
                <span>&bull;</span>
                <a href="#" class="hover:text-slate-600">Terms of Service</a>
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
.fade-in-up {
    animation: fadeInUp 0.6s ease-out forwards;
    opacity: 0;
    transform: translateY(20px);
}

@keyframes fadeInUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.pattern-grid {
    background-image: radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px);
    background-size: 24px 24px;
}
</style>
