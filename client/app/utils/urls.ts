type UrlsRecord = Record<string, string | Record<string, unknown>>

function createUrls<T extends UrlsRecord>(prefix: string, urls: T): Readonly<{ ['index']: string } & T> {
  prefix = noStartSlash(noEndSlash(prefix))

  const deepConvert = (obj: string | UrlsRecord) => {
    if (typeof obj === 'string') {
      return ensureStartSlash(`${prefix}${ensureStartSlash(obj)}`)
    }
    const newObj: UrlsRecord = {}
    for (const [k, v] of Object.entries(obj)) {
      if (typeof v === 'string') {
        newObj[k] = ensureStartSlash(`${prefix}${v}`)
      } else {
        newObj[k] = deepConvert(v as UrlsRecord)
      }
    }
    return newObj
  }
  return Object.entries(urls).reduce((acc, [k, v]) => Object.assign(acc, { [k]: deepConvert(v as UrlsRecord) }), <
    { ['index']: string } & T
  >{ index: ensureStartSlash(prefix) })
}

export const Urls = createUrls('', {
  bill: 'bill'
})
