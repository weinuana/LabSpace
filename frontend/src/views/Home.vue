<template>
  <div class="home">
    <section class="home-hero">
      <div class="home-hero-copy">
        <div class="hero-eyebrow"><i aria-hidden="true"></i> {{ roleLabel }}工作台</div>
        <h1>你好，{{ userInfo?.name || '同学' }}</h1>
        <p>浏览实验室、管理预约，或向 AI 助手提问。</p>
        <el-button class="hero-button" @click="$router.push('/manager/ai-chat')">
          <el-icon><ChatDotRound /></el-icon>
          打开 AI 助手
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="lab-orbit home-orbit" aria-hidden="true">
        <div class="orbit-ring"></div>
        <div class="orbit-ring"></div>
        <div class="orbit-ring"></div>
        <div class="orbit-core"><el-icon><Connection /></el-icon></div>
      </div>
    </section>

    <section class="home-overview" aria-label="工作台概览">
      <article v-for="(item, index) in statCards" :key="item.label" class="home-stat">
        <span class="tile-icon" aria-hidden="true">
          <el-icon v-if="index === 0"><OfficeBuilding /></el-icon>
          <el-icon v-else-if="index === 1"><Tickets /></el-icon>
          <el-icon v-else><ChatDotRound /></el-icon>
        </span>
        <div>
          <div class="home-stat-label">{{ item.label }}</div>
          <div class="home-stat-value">{{ item.value }}</div>
        </div>
      </article>
    </section>

    <div class="home-panels">
      <section class="home-panel">
        <div class="home-panel-heading">
          <h2>快捷入口</h2>
          <p>前往常用页面</p>
        </div>
        <div class="home-shortcuts">
          <button
            v-for="item in shortcuts"
            :key="item.path"
            type="button"
            class="shortcut-button"
            @click="$router.push(item.path)"
          >
            <span>{{ item.label }}</span>
            <el-icon aria-hidden="true"><ArrowRight /></el-icon>
          </button>
        </div>
      </section>

      <section class="home-panel">
        <div class="home-panel-heading">
          <h2>系统能做什么</h2>
          <p>了解实验室预约和智能助手</p>
        </div>
        <div class="home-features">
          <article v-for="(item, index) in features" :key="item.title" class="home-feature">
            <span class="tile-icon" aria-hidden="true">
              <el-icon v-if="index === 0"><Calendar /></el-icon>
              <el-icon v-else-if="index === 1"><Reading /></el-icon>
              <el-icon v-else><MagicStick /></el-icon>
            </span>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useUser } from '@/utils/user'
import { getLabPageList } from '@/api/lab'
import { getReservationPageList } from '@/api/reservation'

const { userInfo } = useUser()

const labTotal = ref('-')
const reservationTotal = ref('-')

const roleLabel = computed(() => (userInfo.value?.role === 'admin' ? '管理员' : '学生'))

const statCards = computed(() => [
  { label: '开放实验室（约）', value: labTotal.value },
  { label: '与我相关的预约', value: reservationTotal.value },
  { label: 'AI 助手', value: '已接入' }
])

const features = [
  {
    title: '业务预约',
    desc: '实验室 / 设备浏览、提交预约、我的预约与管理员审核。'
  },
  {
    title: '知识库问答',
    desc: 'RAG 检索规则与开放时间等文档，回答有据可依。'
  },
  {
    title: '智能 Agent',
    desc: 'Tool Calling + LangGraph：查库、流式过程可见，对话确认后提交预约。'
  }
]

const shortcuts = computed(() => {
  const list = [
    { label: 'AI 智能助手', path: '/manager/ai-chat' },
    { label: '实验室列表', path: '/manager/lablist' },
    { label: '我的预约', path: '/manager/my-reservation' }
  ]
  if (userInfo.value?.role === 'admin') {
    list.push(
      { label: '预约审核', path: '/manager/audit-reservation' },
      { label: '实验室管理', path: '/manager/lab' },
      { label: '设备管理', path: '/manager/equipment' },
      { label: '用户管理', path: '/manager/user' }
    )
  }
  return list
})

onMounted(async () => {
  try {
    const labRes = await getLabPageList({ page: 1, page_size: 1, status: 1 })
    if (labRes.code === 200) labTotal.value = labRes.data?.total ?? 0
  } catch {
    labTotal.value = '-'
  }
  try {
    const resRes = await getReservationPageList({ page: 1, page_size: 1 })
    if (resRes.code === 200) reservationTotal.value = resRes.data?.total ?? 0
  } catch {
    reservationTotal.value = '-'
  }
})
</script>
