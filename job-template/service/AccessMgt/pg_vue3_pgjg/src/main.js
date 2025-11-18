import { createApp } from 'vue'
import { createPinia } from 'pinia'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)){
    app.component(key, component)
}
app.use(ElementPlus, {
  locale: zhCn,
})
app.config.globalProperties.$appConfig = window.appConfig; // 全局配置
app.use(createPinia())
app.use(router)

app.mount('#app')
