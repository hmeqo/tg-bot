import dayjs from 'dayjs'
import zhCN from 'dayjs/locale/zh-cn'

export default defineNuxtPlugin(async (nuxtApp) => {
  dayjs.extend((await import('dayjs/plugin/relativeTime')).default)
  dayjs.extend((await import('dayjs/plugin/quarterOfYear')).default)
  dayjs.extend((await import('dayjs/plugin/utc')).default)
  dayjs.extend((await import('dayjs/plugin/timezone')).default)

  dayjs.locale(zhCN)
})
