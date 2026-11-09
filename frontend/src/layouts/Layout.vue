<template>
  <div class="workspace">
    <aside class="workspace-sidebar">
      <div class="workspace-brand">
        <div class="brand-mark" aria-hidden="true"><el-icon><Connection /></el-icon></div>
        <div>
          <strong>Lab<span>Space</span></strong>
          <small>智能实验室预约系统</small>
        </div>
      </div>

      <div class="workspace-menu-label">工作空间</div>
      <el-menu class="workspace-menu" router :default-active="router.currentRoute.value.path">
        <el-menu-item index="/manager/home">
          <el-icon><icon-menu /></el-icon>
          系统首页
        </el-menu-item>
        <el-menu-item index="/manager/lablist" v-if="userInfo?.role === 'student'">
          <el-icon><OfficeBuilding /></el-icon>
          实验室列表
        </el-menu-item>
        <el-menu-item index="/manager/lab" v-if="userInfo?.role === 'admin'">
          <el-icon><House /></el-icon>
          实验室管理
        </el-menu-item>
        <el-menu-item index="/manager/equipment" v-if="userInfo?.role === 'admin'">
          <el-icon><Setting /></el-icon>
          设备列表管理
        </el-menu-item>
        <el-menu-item index="/manager/user" v-if="userInfo?.role === 'admin'">
          <el-icon><User /></el-icon>
          用户管理
        </el-menu-item>
        <el-menu-item index="/manager/my-reservation" v-if="userInfo?.role === 'student'">
          <el-icon><Tickets /></el-icon>
          <span>我的预约</span>
        </el-menu-item>
        <el-menu-item index="/manager/audit-reservation" v-if="userInfo?.role === 'admin'">
          <el-icon><DocumentChecked /></el-icon>
          <span>预约审核</span>
        </el-menu-item>
        <el-menu-item index="/manager/ai-chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI智能助手</span>
        </el-menu-item>
      </el-menu>

      <div class="workspace-sidebar-note">
          <el-icon><OfficeBuilding /></el-icon>
          <span>实验室预约平台</span>
      </div>
    </aside>

    <div class="workspace-body">
      <header class="workspace-header">
        <div class="workspace-context">
          <span class="workspace-mobile-mark brand-mark" aria-hidden="true">
            <el-icon><Connection /></el-icon>
          </span>
          <div>
            <div class="workspace-context-kicker">LABSPACE / WORKSPACE</div>
            <div class="workspace-context-title">实验室工作台</div>
          </div>
        </div>
        <el-dropdown @command="handleCommand">
          <button type="button" class="workspace-account">
            <el-avatar :size="34" :src="userInfo?.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="workspace-account-copy">
              <strong>{{ userInfo?.name || '我的账户' }}</strong>
              <small v-if="userInfo?.role">{{ userInfo.role === 'admin' ? '管理员' : '学生' }}</small>
            </span>
            <el-icon class="workspace-account-arrow"><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </header>

      <main class="workspace-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import router from '@/router'
import { logout } from '@/utils/auth'
import { useUser } from '@/utils/user'
import {
  Menu as IconMenu,
  House,
  Setting,
  User,
  OfficeBuilding,
  Tickets,
  Document,
  DocumentChecked,
  ChatDotRound
} from '@element-plus/icons-vue'

const { userInfo } = useUser()

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/manager/profile')
  } else if (command === 'password') {
    router.push('/manager/password')
  } else if (command === 'logout') {
    logout()
    router.push('/login')
  }
}
</script>
