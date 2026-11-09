<template>
  <div class="auth-page">
    <div class="auth-shell">
      <AuthShowcase />
      <main class="auth-main">
        <div class="auth-mobile-brand">
          <span class="brand-mark" aria-hidden="true"><el-icon><Connection /></el-icon></span>
          <strong>LabSpace</strong>
        </div>
        <div class="auth-heading">
          <p class="auth-kicker">LABSPACE ACCOUNT</p>
          <h1>登录工作台</h1>
          <p>输入账号和密码，进入实验室预约系统。</p>
        </div>

        <el-form ref="formRef" :rules="rules" :model="form" label-position="top">
          <el-form-item prop="username" label="账号">
            <el-input
              size="large"
              v-model="form.username"
              placeholder="请输入账号"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password" label="密码">
            <el-input
              type="password"
              size="large"
              v-model="form.password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <div>
            <el-button
              size="large"
              type="primary"
              class="auth-submit"
              @click="login"
              :loading="loadingValue"
              >登录</el-button
            >
            <div class="auth-switch">
              还没有账号？请
              <router-link to="/register">注册</router-link>
            </div>
          </div>
        </el-form>
      </main>
    </div>
  </div>
</template>

<script setup>
import AuthShowcase from '@/components/AuthShowcase.vue'
import { reactive, ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { loginApi } from '@/api/auth'
import { useUser } from '@/utils/user'

const { saveLoginData } = useUser()

const formRef = ref()
const form = reactive({
  username: '',
  password: ''
})

const loadingValue = ref(false)

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}
const login = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loadingValue.value = true
  try {
    const res = await loginApi(form)
    if (res.code === 200) {
      saveLoginData(res.data)
      ElMessage.success('登陆成功')
      await router.push('/manager/home')
    }
  } finally {
    loadingValue.value = false
  }
}
</script>
