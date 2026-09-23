import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import HarnessGate from './components/HarnessGate.vue'
import NewLiteracy from './components/NewLiteracy.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'home-hero-image': () => h(HarnessGate),
      'home-features-after': () => h(NewLiteracy),
    })
  },
}
