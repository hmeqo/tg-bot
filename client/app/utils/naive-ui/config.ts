import type { GlobalThemeOverrides } from 'naive-ui'
import { type PaginationProps, type UploadSettledFileInfo } from 'naive-ui'

export const naiveConfigProvider = {
  themeOverrides: <GlobalThemeOverrides>{
    // common: {
    //   primaryColor: '#2080f0',
    //   primaryColorHover: '#4098fc',
    //   primaryColorPressed: '#1060c9',
    //   primaryColorSuppl: '#4098fc'
    // },
    // Checkbox: {
    //   textColorDisabled: 'black',
    //   checkMarkColorDisabled: 'black',
    //   checkMarkColorDisabledChecked: 'black'
    // },
    // Image: {
    //   toolbarColor: 'rgba(0, 0, 0, 0.6)'
    // }
  }
}

export class TableConfig {
  static readonly w1200 = 1200
  static readonly w1000 = 1000
  static readonly w800 = 800
  static get pagination(): PaginationProps {
    return this.getPagination()
  }

  static getPagination(opt?: { page?: number; pageSize?: number }): PaginationProps {
    return reactive({
      page: opt?.page ?? undefined,
      showSizePicker: true,
      defaultPageSize: opt?.pageSize ?? 200,
      pageSizes: [5, 10, 15, 30, 50, 75, 100, 200],
      prefix: ({ itemCount }) => h('div', { style: { 'flex-shrink': '0' } }, `总数 ${itemCount}`),
      simple: !responsive.medium
    })
  }
}

export function modelToFileInfo(data: { id: number; url: string; name?: string }): UploadSettledFileInfo {
  return {
    ...data,
    name: data.name || data.url,
    id: `${data.id}`,
    thumbnailUrl: toThumbnailUrl(data.url, { size: 128 }),
    status: 'finished',
    percentage: null,
    batchId: null,
    fullPath: null,
    type: null,
    file: null
  }
}
