<template>
  <div class="page-view chat-page">
    <header class="page-heading">
      <div class="page-kicker">预约服务</div>
      <h1>AI 智能助手</h1>
      <p>查询开放实验室、了解预约规则，或在对话中提交预约。</p>
    </header>

    <section class="chat-panel" aria-label="AI 智能助手对话">
      <div class="chat-heading">
        <span class="tile-icon" aria-hidden="true"><el-icon><MagicStick /></el-icon></span>
        <div>
          <h2>实验室预约助手</h2>
          <p>预约与规则问答</p>
        </div>
      </div>

      <div ref="listRef" class="chat-list">
        <div
          v-for="(item, index) in messages"
          :key="index"
          class="chat-row"
          :class="{ 'chat-row-user': item.role === 'user' }"
        >
          <span v-if="item.role === 'assistant'" class="chat-avatar" aria-hidden="true">
            <el-icon><MagicStick /></el-icon>
          </span>
          <div class="chat-bubble">
            <p v-if="item.role === 'assistant' && item.status" class="chat-status">
              {{ item.status }}
            </p>
            <ul v-if="item.role === 'assistant' && item.steps?.length" class="chat-steps">
              <li v-for="(step, i) in item.steps" :key="i">{{ step }}</li>
            </ul>
            <div class="chat-markdown" v-html="parseMarkdown(item.content)"></div>
          </div>
        </div>
      </div>

      <div class="chat-compose">
        <div class="chat-compose-row">
          <el-input
            v-model="input"
            type="textarea"
            :rows="2"
            placeholder="问问实验室怎么预约、开放时间..."
            @keydown.enter.exact.prevent="handleSend"
            @keydown.enter.shift.stop
          />
          <el-button type="primary" @click="handleSend" :loading="loading">
            发送
            <el-icon class="el-icon--right"><Promotion /></el-icon>
          </el-button>
        </div>
        <p class="chat-hint">Enter 发送 · Shift + Enter 换行</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { chatStreamApi } from '@/api/ai'
import { ref, reactive, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify' // 过滤危险的 HTML，防止 XSS 攻击
import { ElMessage } from 'element-plus'

const messages = ref([
  {
    role: 'assistant',
    content:
      '你好，我是实验室预约助手。可以问规则和开放实验室，也可以说「帮我预约明天下午的实验室」，确认后我会帮你提交。'
  }
])
const input = ref('')
const loading = ref(false)
const listRef = ref()

const scrollToBottom = () => {
  nextTick(() => {
    const elem = listRef.value
    if (elem) elem.scrollTop = elem.scrollHeight
  })
}

const handleSend = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  scrollToBottom()
  // 必须用 reactive：普通对象 push 后再改字段，视图可能不更新
  const assistant = reactive({
    role: 'assistant',
    content: '', // 正文：靠 token 一点点拼
    status: '正在思考…', // 当前状态文案
    steps: [] // 过程流水，不进下次 history
  })
  messages.value.push(assistant)
  const history = messages.value
    .filter((item) => item.role === 'user' || item.role === 'assistant')
    .slice(0, -1) // 去掉刚插入的空助手，避免把空 content 送回去
    // 只保留 role/content；status、steps 丢掉
    .map(({ role, content }) => ({ role, content }))
  try {
    // 第二个参数是回调：每解析出一条 SSE 事件就进一次
    await chatStreamApi({ messages: history }, (evt) => {
      if (evt.type === 'status') {
        assistant.status = evt.message || '正在思考…'
      } else if (evt.type === 'tool_start') {
        const label = evt.label || evt.name || '工具'
        assistant.status = `正在${label}…`
        assistant.steps.push(`开始：${label}`)
      } else if (evt.type === 'tool_end') {
        const label = evt.label || evt.name || '工具'
        assistant.status = `${label}完成`
        assistant.steps.push(`完成：${label}`)
      } else if (evt.type === 'token') {
        assistant.content += evt.content || '' // 打字机：追加，不是覆盖
        assistant.status = '' // 开始出字后清掉「正在…」，避免叠在一起
      } else if (evt.type === 'done') {
        assistant.status = ''
        // 注意：不要在这里再 append 一整段正文，否则会双份
      } else if (evt.type === 'error') {
        assistant.status = ''
        if (!assistant.content) {
          assistant.content = evt.message || '请求失败'
        }
        ElMessage.error(evt.message || '请求失败')
      }
      scrollToBottom()
    })
  } catch (err) {
    assistant.status = ''
    if (!assistant.content) {
      assistant.content = err.message || '网络异常'
    }
    ElMessage.error(err.message || '网络异常')
  } finally {
    loading.value = false
    assistant.status = ''
    scrollToBottom()
  }
}

// 将 markdown 字符串转换为安全的 HTML 字符串
const parseMarkdown = (text) => {
  if (!text) return ''
  marked.setOptions({ breaks: true }) // 把 \n 转换成 <br>
  // 使用 marked 解析，然后用 DOMPurify 清理
  const rawHtml = marked.parse(text)
  return DOMPurify.sanitize(rawHtml)
}
</script>
