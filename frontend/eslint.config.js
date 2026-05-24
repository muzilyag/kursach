import pluginVue from 'eslint-plugin-vue'
import vueTsConfigs from '@vue/eslint-config-typescript'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue,js,jsx}']
  },  
  {
    name: 'app/ignores',
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**', 'node_modules/**']
  },
  ...pluginVue.configs['flat/essential'],  
  ...vueTsConfigs(),  
  skipFormatting,  
  {
    rules: {
      'vue/multi-word-component-names': 'off', 
      '@typescript-eslint/no-explicit-any': 'warn' 
    }
  }
]