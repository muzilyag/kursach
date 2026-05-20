import pluginVue from 'eslint-plugin-vue'
import vueTsConfigs from '@vue/eslint-config-typescript'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default [
  {
    files: ['**/*.{ts,mts,tsx,vue,js,jsx}']
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