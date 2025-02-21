export const responsive = reactive({
  small: false,
  medium: false,
  large: false,
  tick(target: any) {
    this.small = target.innerWidth >= 640
    this.medium = target.innerWidth >= 768
    this.large = target.innerWidth >= 1024
  }
})

if (import.meta.client) {
  responsive.tick(window)
  window.addEventListener('resize', (e) => responsive.tick(e.target))
}
