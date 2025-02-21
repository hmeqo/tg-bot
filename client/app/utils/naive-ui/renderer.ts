import { NuxtLink } from '#components'
import dayjs from 'dayjs'
import { NIcon } from 'naive-ui'

export function renderAction(text: string, onclick: Function) {
  return () => h('a', { onclick }, text)
}

export function renderIcon(data: { type?: any; content?: string | VNode; attr?: any }) {
  return () =>
    h(data.type || NIcon, data.attr, {
      default: () => data.content
    })
}

export function renderLink(
  text: string,
  url: string | { path: string; query?: Record<string, any> },
  attr?: Record<string, any>
) {
  return () =>
    h(
      NuxtLink,
      {
        ...attr,
        to: url,
        onClick: (e: Event) => {
          ;(e.target as HTMLAnchorElement)?.blur()
        },
        draggable: false
      },
      () => text
    )
}

export type IsSingleDateDisabledDetail =
  | {
      type: 'date'
      year: number
      month: number
      date: number
    }
  | {
      type: 'month'
      year: number
      month: number
    }
  | {
      type: 'year'
      year: number
    }
  | {
      type: 'quarter'
      year: number
      quarter: number
    }
  | {
      type: 'input'
    }

export function disableFutureDates(
  timestamp: number,
  type: IsSingleDateDisabledDetail | IsSingleDateDisabledDetail['type']
) {
  if (typeof type !== 'string') type = type.type

  let startSect: number = Date.now()
  switch (type) {
    case 'year':
      startSect = dayjs(startSect).startOf('year').valueOf()
      break
    case 'quarter':
      startSect = dayjs(startSect).startOf('quarter').valueOf()
      break
    case 'month':
      startSect = dayjs(startSect).startOf('month').valueOf()
      break
  }
  return timestamp >= startSect
}
