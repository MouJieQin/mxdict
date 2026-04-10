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
}

const props = defineProps<Props>()
const iframeRef = ref<HTMLIFrameElement | null>(null)
const baseUrl = ref("http://localhost:5959/api/download?path=" + props.basePath)
const emits = defineEmits(['entry-click'])
const iframeId = ref(props.dictionaryRoot)
// ==============================================
// 你要触发的 VUE 方法（在这里写业务逻辑）
// ==============================================
function handleEntryClick(entryPath: string) {
  console.log("✅ 收到 entry 点击：", entryPath)
  // 在这里写你的逻辑：查询、跳转、渲染……
  emits('entry-click', entryPath)
}

// 监听变化 → 刷新 iframe
watch(
  () => [props.html, props.cssUrl, props.jsUrl, props.basePath],
  async () => {
    await nextTick()
    renderIframe()
  },
  { deep: true, immediate: true }
)

onUnmounted(() => {
  if (iframeRef.value) {
    iframeRef.value.srcdoc = ''
  }
})

// 核心：渲染 iframe
function renderIframe() {
  const iframe = iframeRef.value
  if (!iframe) return

  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return

  // 1. 替换资源路径
  let html = props.html
    // .replace(/sound:\//g, baseUrl.value)
    .replace(/file:\//g, baseUrl.value)

  // 2. 最终 HTML（关键：注入通信方法）
  const finalHtml = `
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ${props.cssUrl !== '' ? `<link rel="stylesheet" href="http://localhost:5959/api/download?path=${props.cssUrl}">` : ''}
</head>
<body>
  ${html}

  ${props.jsUrl !== '' ? `<script src="http://localhost:5959/api/download?path=${props.jsUrl}" charset="UTF-8"><\/script>` : ''}

  <script>
    // 全局点击拦截 + 通信
    document.addEventListener('click', (e) => {
      const aTag = e.target.closest('a[href]');
      if (!aTag) return;
      const href = aTag.href || aTag.getAttribute('href');

      // entry:// 链接 → 发送消息给外层 Vue
      if (href.startsWith('entry://')) {
        e.preventDefault();
        // ======================================
        // 核心：发送消息给父页面（Vue 组件）
        // ======================================
        window.parent.postMessage({
          type: 'ENTRY_CLICK',
          iframeId: '${iframeId.value}',
          entry: href.replace('entry://', '')
        }, '*');
      }else if (href.startsWith('sound://')) {
          e.preventDefault();
          window.parent.postMessage({
          type: 'SOUND_CLICK',
          iframeId: '${iframeId.value}',
          sound: href.replace('sound://', '')
        }, '*');
      }
      else {
        e.preventDefault();
      }
    });
  <\/script>
</body>
</html>
  `

  doc.open()
  doc.write(finalHtml)
  doc.close()

  // 自动高度
  const autoHeight = () => {
    if (!iframe.contentDocument) return
    iframe.style.height = iframe.contentDocument.body.scrollHeight + 50 + 'px'
  }
  iframe.onload = autoHeight
  setTimeout(autoHeight, 50)
}

// ==============================================
// 监听 iframe 发来的消息
// ==============================================
const messageListener = (e: MessageEvent) => {
  // 只处理当前 iframe 发来的消息 ✅
  if (e.data?.iframeId !== iframeId.value) return
  if (e.data?.type === 'ENTRY_CLICK') {
    try {
      // 解码 URL 编码 → 正常文字
      const realWord = decodeURIComponent(e.data.entry)
      // 触发你的函数
      handleEntryClick(realWord)
    } catch (err) {
      // 防止解码报错
      handleEntryClick(e.data.entry)
    }
  } else if (e.data?.type === 'SOUND_CLICK') {
    const soundPath = baseUrl.value + "/" + e.data.sound;
    try {
      const audio = new Audio(soundPath);
      audio.play().catch(err => {
        // 大部分情况是路径问题，不是浏览器不支持
        console.warn("音频播放提示（可忽略）：", err);
        console.log("🔊 播放音频：", soundPath); // 打开控制台看路径是否正确
      });
    } catch (e) {
      console.log("🔊 播放音频：", soundPath); // 打开控制台看路径是否正确
     }
  }
}
window.addEventListener('message', messageListener)
onUnmounted(() => {
  window.removeEventListener('message', messageListener) // 关键！
})
</script>

<style scoped>
.dict-iframe {
  width: 100%;
  border: none;
  background: #fff;
}
</style>