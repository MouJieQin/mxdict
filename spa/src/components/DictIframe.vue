<template>
  <iframe ref="iframeRef" class="dict-iframe" frameborder="0" scrolling="no"
    sandbox="allow-scripts allow-same-origin"></iframe>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'

interface Props {
  html: string
  cssUrl: string
  jsUrl: string
  basePath: string
  dictionaryRoot: string
  currentWord?: string // 如果你有当前单词，传进来做缓存 key
}

const props = defineProps<Props>()
const emits = defineEmits(['entry-click'])

const iframeRef = ref<HTMLIFrameElement | null>(null)
const API_PREFIX = 'http://localhost:5959/api/download?path='
const baseUrl = ref(`${API_PREFIX}${props.basePath}`)
const iframeId = ref(props.dictionaryRoot)

// ================ 业务逻辑 ================
function handleEntryClick(entryPath: string) {
  console.log('✅ 点击词条:', entryPath)
  emits('entry-click', entryPath)
}

// ================ 核心渲染（极速版） ================
async function renderIframe() {
  const iframe = iframeRef.value
  if (!iframe) return

  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return

  // 处理资源路径
  let content = props.html
    .replace(/src=\"/g, `src="${baseUrl.value}/`)
    .replace(/file:\//g, baseUrl.value)


  // 只在第一次加载 CSS/JS
  doc.body.innerHTML = ''

  // CSS
  if (props.cssUrl) {
    const link = doc.createElement('link')
    link.rel = 'stylesheet'
    link.href = `${API_PREFIX}${props.cssUrl}`
    doc.head.appendChild(link)
  }

  // JS
  if (props.jsUrl) {
    const script = doc.createElement('script')
    script.src = `${API_PREFIX}${props.jsUrl}`
    script.charset = 'UTF-8'
    doc.head.appendChild(script)
  }

  console.log("doc.head.innerHTML:", doc.head.innerHTML)

  // 注入一次全局点击监听
  injectClickHandler(doc)

  await nextTick()

  // 只更新内容，不重建整个 iframe
  doc.body.innerHTML = content
  updateIframeHeight()
}

// ================ 点击事件只注入一次 ================
function injectClickHandler(doc: Document) {
  const script = doc.createElement('script')
  script.textContent = `
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href]');
      if (!a) return;
      const href = a.href || a.getAttribute('href');

      if (href.startsWith('entry://')) {
        e.preventDefault();
        window.parent.postMessage({
          type: 'ENTRY_CLICK',
          iframeId: '${iframeId.value}',
          entry: href.replace('entry://', '')
        }, '*');
      }
      else if (href.startsWith('sound://')) {
        e.preventDefault();
        window.parent.postMessage({
          type: 'SOUND_CLICK',
          iframeId: '${iframeId.value}',
          sound: href.replace('sound://', '')
        }, '*');
      }
      else if (href.startsWith('http://localhost:9595/dict#')) {
        // 放行
      }
      else {
        e.preventDefault();
        console.log('拦截链接:', href);
      }
    });
  `
  doc.body.appendChild(script)
}

// ================ 高度自适应 ================
function updateIframeHeight() {
  const iframe = iframeRef.value
  if (!iframe?.contentDocument) return
  const h = iframe.contentDocument.body.scrollHeight
  iframe.style.height = `${h + 30}px`
}

// ================ 监听变化 ================
watch(
  () => [props.html, props.basePath],
  async () => {
    await nextTick()
    renderIframe()
    window.scrollTo(0, 0)
  },
  { deep: true, immediate: true }
)

// ================ 外层消息监听 ================
const messageListener = (e: MessageEvent) => {
  if (e.data?.iframeId !== iframeId.value) return

  if (e.data?.type === 'ENTRY_CLICK') {
    try {
      handleEntryClick(decodeURIComponent(e.data.entry))
    } catch {
      handleEntryClick(e.data.entry)
    }
  }
  else if (e.data?.type === 'SOUND_CLICK') {
    const soundUrl = `${baseUrl.value}/${e.data.sound}`
    const audio = new Audio(soundUrl)
    audio.currentTime = 0
    audio.play().catch(err => console.warn('播放失败', err))
  }
}

window.addEventListener('message', messageListener)

onUnmounted(() => {
  window.removeEventListener('message', messageListener)
  if (iframeRef.value) {
    iframeRef.value.srcdoc = ''
  }
})
</script>

<style scoped>
.dict-iframe {
  width: 100%;
  border: none;
}
</style>