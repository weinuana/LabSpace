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
          <h1>创建账号</h1>
          <p>注册后即可浏览实验室、提交预约。</p>
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
          <el-form-item prop="confirmPassword" label="确认密码">
            <el-input
              type="password"
              size="large"
              v-model="form.confirmPassword"
              placeholder="请确认密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <div>
            <el-button
              size="large"
              type="primary"
              :loading="loadingValue"
              class="auth-submit"
              @click="register"
              >注册</el-button
            >
            <div class="auth-switch">
              已有账号？请
              <router-link to="/login">登录</router-link>
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
import { registerApi } from '@/api/auth'
import router from '@/router'

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const loadingValue = ref(false)

const formRef = ref()
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else {
    if (value !== form.password) {
      callback(new Error('两次密码输入不一致'))
    } else {
      callback()
    }

    callback()
  }
}
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [{ validator: validatePass, trigger: 'blur' }]
}

const register = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loadingValue.value = true
  try {
    const res = await registerApi(form)
    if (res.code === 200) {
      ElMessage.success('注册成功')
      await router.push('/login')
    }
  } finally {
    loadingValue.value = false
  }
}
</script>
