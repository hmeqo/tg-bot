<script setup lang="ts">
import { darkTheme, dateZhCN, lightTheme, zhCN } from 'naive-ui'

defineProps<{
  light?: boolean
  dark?: boolean
}>()

function getLocale() {
  return zhCN
}
function getDateLocale() {
  return dateZhCN
}

const prefersTheme = lightTheme
</script>

<template>
  <NConfigProvider
    :theme="light ? lightTheme : dark ? darkTheme : prefersTheme"
    :theme-overrides="naiveConfigProvider.themeOverrides"
    :locale="getLocale()"
    :date-locale="getDateLocale()"
  >
    <NLoadingBarProvider>
      <slot />
    </NLoadingBarProvider>
  </NConfigProvider>
</template>
