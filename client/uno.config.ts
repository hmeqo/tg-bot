import { presetWind3 } from '@unocss/preset-wind3'
import { defineConfig, presetIcons, transformerDirectives } from 'unocss'

export default defineConfig({
  rules: [],
  presets: [presetWind3(), presetIcons()],
  transformers: [transformerDirectives()]
})
