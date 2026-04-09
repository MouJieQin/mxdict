<template>
  <!-- <dev>
    {{ props.html }}
  </dev> -->
  <iframe ref="iframeRef" class="dict-iframe" frameborder="0" scrolling="no"
    sandbox="allow-scripts allow-same-origin"></iframe>
</template>
<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'

interface Props {
  html: string          // 词典返回的原始 HTML
  cssUrl: string        // 词典 CSS URL
  jsUrl: string         // 词典 JS URL
  basePath: string      // 资源基础路径（音频/图片）
  dictionaryRoot: string // 词典所在目录，如 /dictionaries/dic1/
}

const props = defineProps<Props>()
const iframeRef = ref<HTMLIFrameElement | null>(null)
const baseUrl = ref("http://localhost:5959/api/download?path=" + props.basePath)

// 监听变化 → 刷新 iframe
watch(
  () => [props.html, props.cssUrl, props.jsUrl, props.basePath],
  async () => {
    await nextTick()
    renderIframe()
  },
  { deep: true, immediate: true }
)

// 销毁时清理
onUnmounted(() => {
  if (iframeRef.value) {
    iframeRef.value.srcdoc = ''
  }
})

// 核心：渲染 iframe
function renderIframe() {
  const iframe = iframeRef.value
  if (!iframe) return

  // 获取 iframe document
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return

  // 1. 替换资源路径
  let html = props.html
    .replace(/sound:\//g, baseUrl.value)
    .replace(/file:\//g, baseUrl.value)
    // .replace(/entry:\/\//g, 'javascript:void(0)')

  // 2. 拼接最终 HTML（修复转义 + 拼接错误）
  const finalHtml = `
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">`.concat(
    props.cssUrl !== '' ? `<link rel="stylesheet" href="http://localhost:5959/api/download?path=${props.cssUrl}">` : '').concat(
      `</head>
<body>
  ${html}`).concat(
        props.jsUrl !== '' ? `<script src="http://localhost:5959/api/download?path=${props.jsUrl}" charset="UTF-8"><\/script>` : ''
      ).concat(
        `<script>
    // 全局拦截点击：只允许播放音频
    document.addEventListener('click', (e) => {
      const aTag = e.target.closest('a[href]');
      if (!aTag) return;
      const href = aTag.href || aTag.getAttribute('href');

      // 发音链接：播放音频
      if (href.startsWith('http://localhost:5959/api/download?path=')) {
        e.preventDefault();
        new Audio(href).play().catch(err => console.log('播放失败', err));
      }
      else if (href.startsWith('entry://')) {
        e.preventDefault();
      }
      // 其他所有链接：禁止跳转
      else {
        e.preventDefault();
      }
    });
  <\/script>
</body>
</html>
  `)

  // 3. 写入 iframe
  doc.open()
  doc.write(finalHtml)
  doc.close()

  // 4. 自动高度（修复：立即执行 + 延时兜底）
  const autoHeight = () => {
    if (!iframe.contentDocument) return
    iframe.style.height = iframe.contentDocument.body.scrollHeight + 50 + 'px'
  }
  iframe.onload = autoHeight
  setTimeout(autoHeight, 100) // 延时兜底，解决 CSS 加载后高度变化
}
</script>

<style scoped>
.dict-iframe {
  width: 100%;
  border: none;
  background: #fff;
}
</style>