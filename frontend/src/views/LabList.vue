<template>
  <div class="page-view">
    <header class="page-heading">
      <div class="page-kicker">预约服务</div>
      <h1>实验室列表</h1>
      <p>查看实验室的位置、容量和开放时间，选择适合的实验室或设备。</p>
    </header>

    <el-card class="page-panel" shadow="never">
      <div class="page-toolbar">
        <el-input
          placeholder="请输入名称查询"
          v-model="params.keywords"
          style="width: 240px"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      </div>

      <div class="lab-grid" v-loading="loading">
        <article v-for="item in tableData" :key="item.id" class="lab-tile">
          <img v-if="item.img" :src="item.img" alt="" class="lab-cover" />
          <div v-else class="lab-cover lab-cover-placeholder" aria-hidden="true">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="lab-tile-body">
            <h2>{{ item.name }}</h2>
            <dl class="lab-facts">
              <div>
                <dt><el-icon aria-hidden="true"><Location /></el-icon>位置</dt>
                <dd>{{ item.location || '-' }}</dd>
              </div>
              <div>
                <dt><el-icon aria-hidden="true"><User /></el-icon>容量</dt>
                <dd>{{ item.capacity }} 人</dd>
              </div>
              <div>
                <dt><el-icon aria-hidden="true"><Clock /></el-icon>开放</dt>
                <dd>
                  {{ item.open_time && item.close_time ? item.open_time + ' - ' + item.close_time : '-' }}
                </dd>
              </div>
            </dl>
            <div class="lab-actions">
              <el-button @click="handleViewEquipment(item)">查看设备</el-button>
              <el-button type="primary" @click="handleReserve(item)">预约</el-button>
            </div>
          </div>
        </article>
        <el-empty v-if="!loading && !tableData?.length" description="暂无实验室" />
      </div>

      <div class="page-pagination">
        <el-pagination
          v-model:current-page="params.page"
          v-model:page-size="params.page_size"
          :total="total"
          background
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </el-card>

    <reserve-dialog
      v-model:visible="reserveVisible"
      :lab-id="currentLab?.id"
      :lab-name="currentLab?.name"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLabPageList } from '@/api/lab'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import router from '@/router'
import ReserveDialog from '@/components/ReserveDialog.vue'

const reserveVisible = ref(false)
const currentLab = ref(null)
const params = reactive({
  page: 1,
  page_size: 10,
  keywords: ''
})
const loading = ref(false)
const tableData = ref([])
const total = ref(0)

const handleViewEquipment = (lab) => {
  router.push({ path: '/manager/lab-equipment', query: { lab_id: lab.id } })
}

const handleReserve = (lab) => {
  currentLab.value = lab
  reserveVisible.value = true
}

// 加载分页数据
const load = async () => {
  loading.value = true
  try {
    const res = await getLabPageList(params)
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  params.page = 1
  load()
}

onMounted(() => {
  load()
})
</script>
