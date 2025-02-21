import { createDiscreteApi, darkTheme, dateZhCN, zhCN } from 'naive-ui'

export const useNaiveApi = () => {
  return createDiscreteApi(['message', 'dialog', 'notification', 'loadingBar'], {
    configProviderProps: {
      theme: darkTheme,
      themeOverrides: naiveConfigProvider.themeOverrides,
      locale: zhCN,
      dateLocale: dateZhCN
    }
  })
}
