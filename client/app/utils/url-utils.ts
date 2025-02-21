export function ensureEndSlash(_url: unknown) {
  const url = `${_url}`
  return url.endsWith('/') ? url : `${url}/`
}

export function ensureStartSlash(_url: unknown) {
  const url = `${_url}`
  return url.startsWith('/') ? url : `/${url}`
}

export function noEndSlash(_url: unknown) {
  const url = `${_url}`
  return url.endsWith('/') ? url.slice(0, -1) : url
}

export function noStartSlash(_url: unknown) {
  const url = `${_url}`
  return url.startsWith('/') ? url.slice(1) : url
}

/**
 * Like python's string.format
 * Example: format('hello {name}', { name: 'John' })
 */
export function format(url: string, kwargs: Record<string, unknown>) {
  return Object.entries(kwargs).reduce((acc, [key, arg]) => acc.replace(`{${key}}`, `${arg}`), url)
}

/**
 * Returns the last part of the url
 */
export function urlBasename(url: string): string {
  return url.split('/').pop() ?? ''
}

export function urlToString(
  url: string | { path: string; query?: string[][] | Record<string, string> | string | URLSearchParams }
): string {
  if (typeof url === 'string') {
    return url
  }

  const { path, query } = url
  const searchParams = new URLSearchParams(query)
  return `${path}?${searchParams}`
}

export function suburlToUrl(url: string) {
  return `${location.origin}${url}`
}

export function toThumbnailUrl(url: string, opts?: { size?: number }) {
  const params = new URLSearchParams({
    size: `${opts?.size || 256}`
  })
  return `${fullPathToPath(url)}?${params}`
}

export function fullPathToPath(fullPath: string) {
  return fullPath.split('?', 1)[0]!
}

export function formatFileSize(size: string | number) {
  size = Number.parseInt(`${size}`)
  if (size < 1024) {
    return `${size}B`
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)}KB`
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / 1024 / 1024).toFixed(2)}MB`
  } else {
    return `${(size / 1024 / 1024 / 1024).toFixed(2)}GB`
  }
}
