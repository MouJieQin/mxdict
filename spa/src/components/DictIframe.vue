<template>
  <iframe
    ref="iframeRef"
    class="dict-iframe"
    frameborder="0"
    scrolling="no"
    sandbox="allow-scripts allow-same-origin"
  ></iframe>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted, shallowRef } from 'vue'

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
const baseUrl = ref(`http://localhost:5959/api/download?path=${props.basePath}`)
const iframeId = ref(props.dictionaryRoot)

// ================ 缓存 ================
// 缓存已渲染过的词条 HTML
const htmlCache = ref<Record<string, string>>({})
// 音频缓存
const audioCache = shallowRef<Record<string, HTMLAudioElement>>({})

// ================ 只加载一次标记 ================
const hasLoadedCssJs = ref(false)

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

  // 缓存 key：用 currentWord 最好，没有就用 html 本身
  const cacheKey = props.currentWord ?? props.html

  // 命中缓存 → 直接秒渲染
  if (htmlCache.value[cacheKey]) {
    doc.body.innerHTML = htmlCache.value[cacheKey]
    updateIframeHeight()
    return
  }

  // 处理资源路径
  let content = props.html
    .replace(/src=\"/g, `src="${baseUrl.value}/`)
    .replace(/file:\//g, baseUrl.value)

  // 写入缓存
  htmlCache.value[cacheKey] = content

  // 只在第一次加载 CSS/JS
  if (!hasLoadedCssJs.value) {
    doc.body.innerHTML = ''

    // CSS
    if (props.cssUrl) {
      const link = doc.createElement('link')
      link.rel = 'stylesheet'
      link.href = `http://localhost:5959/api/download?path=${props.cssUrl}`
      doc.head.appendChild(link)
    }

    // JS
    if (props.jsUrl) {
      const script = doc.createElement('script')
      script.src = `http://localhost:5959/api/download?path=${props.jsUrl}`
      script.charset = 'UTF-8'
      doc.body.appendChild(script)
    }

    // 注入一次全局点击监听
    injectClickHandler(doc)

    hasLoadedCssJs.value = true
    await nextTick()
  }

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

    // 音频缓存
    let audio = audioCache.value[soundUrl]
    if (!audio) {
      audio = new Audio(soundUrl)
      audioCache.value[soundUrl] = audio
    }

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