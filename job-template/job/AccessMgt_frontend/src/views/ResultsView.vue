<template>
  <div class="results-container">
    <div class="content">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="请输入搜索关键词"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      
      <div class="table-container">
        <el-table
          :data="originData"
          style="width: 100%"
          v-loading="loading"
          stripe
          border
        >
          <el-table-column type="index" align="center" label="序号" width="80" />
          <el-table-column prop="system_name" label="体系名称" min-width="120" />
          <el-table-column prop="system_description" label="体系描述" min-width="200" />
          <el-table-column prop="basic_name" label="数据源名称" min-width="120" />
          <el-table-column prop="basic_description" label="数据源描述" min-width="200" />
          <el-table-column prop="createTime" label="报告生成时间" min-width="180" />
          <el-table-column label="操作" min-width="400" align="center" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleDownload(scope.row)">下载</el-button>
              <el-button size="small" type="primary" @click="handleWorlflow(scope.row)">详情</el-button>
              <el-button size="small" type="primary" @click="handleDetail(scope.row)">查看评估报告</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getResultsList, exportResultsFile, deleteResultsFile } from '@/api/ResultsApi.js'
import { useRouter } from 'vue-router'
import { useResultDataStore } from '@/stores/resultDataStore'

const router = useRouter()
const resultDataStore = useResultDataStore()
// 搜索相关
const searchQuery = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 加载状态
const loading = ref(false)

// 表格数据
const originData = ref([])

// 评估报告数据
const resultData = ref(null)

// 获取数据
const fetchResultsList = async () => {
  loading.value = true
  try {
    const data = {
      page: currentPage.value,
      num: pageSize.value,
      name: searchQuery.value
    }
    const res = await getResultsList(data)
    originData.value = res.data.info
    total.value = res.data.total_num
    console.log(originData.value)
    loading.value = false
  } catch (error) {
    console.error('Error fetching results list:', error)
    loading.value = false
  }
}

// 计算表格数据
// const tableData = computed(() => {
//   const list = originData.value.filter(item =>
//     item.name.toLowerCase().includes(searchQuery.value.trim().toLowerCase())
//   )
//   total.value = list.length
//   return list.slice(
//     (currentPage.value - 1) * pageSize.value,
//     currentPage.value * pageSize.value
//   )
// })

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchResultsList()
}

// 重置
const handleReset = () => {
  searchQuery.value = ''
  currentPage.value = 1
  fetchResultsList()
}

// 删除
const handleDelete = async (row) => {
  try {
    await deleteResultsFile(row.id)
    ElMessage.success('删除成功')
    fetchResultsList()
  } catch (error) {
    console.error('Error deleting result:', error)
    ElMessage.error('删除失败')
  }
}

// 下载
const handleDownload = async (row) => {
  try {
    const response = await exportResultsFile(row.word_uid)
    const blob = response.data
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${row.system_name}评估报告.docx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Error downloading result:', error)
    ElMessage.error('下载失败')
  }
}

const handleWorlflow = (row) => {
    console.log('row.system_detail', row.system_detail)
    // 使用Pinia store传递数据
    resultDataStore.setResultData(row.system_detail)
    router.push({ name: 'Workflow' })
}

// 详情
const handleDetail = (row) => {
    console.log('row.system_result', row)
    // 使用Pinia store传递数据
    resultDataStore.setResultData(row.system_result)
    router.push({ name: 'ResultDetail' })
}

// 分页相关方法
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchResultsList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchResultsList()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchResultsList()
})
</script>

<style scoped>
.content {
  height: 100%;
  overflow: auto;
}
.results-container {
  padding: 20px;
  background-color: #050b0d;
  height: 100%;
}

.header {
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.table-container {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}
</style>