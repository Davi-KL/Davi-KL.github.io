// O jsdom não implementa rolagem, e o scrollBehavior do vue-router chama window.scrollTo.
window.scrollTo = (() => {}) as typeof window.scrollTo
