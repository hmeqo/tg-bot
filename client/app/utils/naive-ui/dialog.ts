import { createDiscreteApi, darkTheme, dateZhCN, zhCN, type DialogOptions } from 'naive-ui'

export class DialogText {
  static readonly upload: DialogOptions = {
    title: '上传文件',
    content: '确认上传?',
    type: 'info'
  }
  static readonly delete: DialogOptions = {
    title: '删除数据',
    content: '确认删除?',
    type: 'error'
  }
  static readonly update: DialogOptions = {
    title: '修改数据',
    content: '确认修改?',
    type: 'warning'
  }
  static readonly save: DialogOptions = {
    title: '保存数据',
    content: '确认保存?',
    type: 'info'
  }
  static readonly logout: DialogOptions = {
    title: '退出登录',
    content: '确认退出登录?',
    type: 'warning'
  }

  static readonly resetPwd: DialogOptions = {
    title: '重置密码',
    content: '确定重置密码? 重置后此账号的所有设备将退出登录',
    type: 'warning'
  }
}

// TODO Remove this
export const { message, notification, dialog, loadingBar } = createDiscreteApi(
  ['message', 'dialog', 'notification', 'loadingBar'],
  {
    configProviderProps: {
      theme: darkTheme,
      themeOverrides: naiveConfigProvider.themeOverrides,
      locale: zhCN,
      dateLocale: dateZhCN
    }
  }
)

export function createDialog(options: DialogOptions) {
  const { message } = useNaiveApi()
  const result = dialog.create({
    negativeText: '取消',
    positiveText: '确认',
    maskClosable: false,
    ...options,
    onNegativeClick: (e) => {
      options?.onNegativeClick?.(e)
      message.info('已取消')
    },
    onPositiveClick: (e) => {
      if (!options.onPositiveClick) return
      result.loading = true
      options.onPositiveClick(e)
      result.loading = false
    },
    onEsc: () => {
      options?.onClose?.()
      message.info('已取消')
    },
    onClose: () => {
      options?.onClose?.()
      message.info('已取消')
    }
  })
}
