import js from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import eslintConfigPrettier from 'eslint-config-prettier';
import globals from 'globals';

export default [
  // 1. Базовые настройки
  js.configs.recommended,

  // 2. Настройки Vue
  ...pluginVue.configs['flat/recommended'],

  // 3. Отключаем конфликты Prettier
  eslintConfigPrettier,

  // 4. Глобальные настройки
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser, // <--- ВОТ ЭТО РЕШАЕТ ВСЕ ПРОБЛЕМЫ (alert, localStorage и т.д.)
        ...globals.node,    // (опционально, если используете process.env)
      },
    },
    rules: {
      // Сделаем правила чуть мягче для диплома
      'vue/multi-word-component-names': 'off', // Чтобы можно было называть файлы Login.vue (одним словом)
      'vue/require-default-prop': 'off',       // Убираем предупреждение в HelloWorld.vue
      'no-unused-vars': 'warn',                // Неиспользуемые переменные — это не ошибка, а предупреждение
      'no-undef': 'error',                     // А вот неизвестные переменные — ошибка
    },
  },
];