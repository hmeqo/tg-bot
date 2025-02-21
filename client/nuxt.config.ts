// https://nuxt.com/docs/api/configuration/nuxt-config
import AutoImport from 'unplugin-auto-import/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'

export default defineNuxtConfig({
  future: {
    compatibilityVersion: 4
  },
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ['@unocss/nuxt', 'nuxtjs-naive-ui', 'nuxt-csurf'],
  components: [
    { path: '@/components' }
    // { path: '@/components/forms', pathPrefix: false }
  ],
  css: ['assets/css/main.css'],

  ssr: false,
  routeRules: {
    '/api/**': { proxy: 'http://127.0.0.1:8000/api/**' },
    '/media/**': { proxy: 'http://127.0.0.1:8000/media/**' }
  },

  nitro: {
    compressPublicAssets: true
  },

  vite: {
    plugins: [
      AutoImport({
        imports: [
          {
            'naive-ui': ['useDialog', 'useMessage', 'useNotification', 'useLoadingBar']
          }
        ],
        dts: 'types/auto-imports.d.ts'
      }),
      Components({
        resolvers: [NaiveUiResolver()],
        dts: 'types/components.d.ts'
      })
    ]
  },

  csurf: {
    https: false, // default true if in production
    cookieKey: 'csrftoken', // "__Host-csrf" if https is true otherwise just "csrf"
    headerName: 'X-Csrftoken' // the header where the csrf token is stored
  },

  typescript: {
    tsConfig: {
      compilerOptions: {
        paths: {
          '@': ['.'],
          '@/*': ['./*'],
          '@@': ['..'],
          '@@/*': ['../*'],
          '#components': ['./components']
        }
      }
    }
  }
})
