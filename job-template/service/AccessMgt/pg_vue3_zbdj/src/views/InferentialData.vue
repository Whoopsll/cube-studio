<template>
  <div class="results-container">
    <div class="content">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="请输入集合名称"
            style="width: 300px"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>

      <div class="table-container">
        <!-- 数据表格 -->
        <el-table
          :data="originData"
          style="width: 100%"
          v-loading="loading"
          stripe
          border
        >
          <el-table-column type="index" label="序号" min-width="80" />
          <el-table-column prop="name" label="集合名称" min-width="150" />
          <el-table-column prop="createTime" label="创建时间" min-width="150" />
          <el-table-column label="操作" align="center" min-width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="primary" @click="handleDetail(scope.row)">详情</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        </div>

        <!-- 分页 -->
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

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      :title="dialogType === 'add' ? '新增集合' : '编辑集合'"
      v-model="dialogVisible"
      width="600px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="modelFormRef"
        :model="modelForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="集合名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入集合名称" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getList, deleteList, addList, updateList } from '@/api/InferentialDataApi'
import { useRouter } from 'vue-router'

/* ------------------ 数据 ------------------ */
const searchQuery = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
// 模拟数据
const originData = ref()
const router = useRouter()

const fetchUserList = async () => {
  loading.value = true;
   try {
    const data = {
      page: currentPage.value,
      num: pageSize.value,
      name: searchQuery.value
    }
    const res = await getList(data);
    originData.value = res.data.info;
    total.value = res.data.total_num;
    loading.value = false;
   } catch (error) {
        console.error('Error fetching user list:', error);
  }
};

/* ------------------ 表单 ------------------ */
const dialogVisible = ref(false)
const dialogType = ref('add')
const modelFormRef = ref()

const modelForm = reactive({
  name: '',
})

const rules = {
  name: [
    { required: true, message: '请输入集合名称', trigger: 'blur' },
    { 
      validator: (_, value) => {
        if (!value.trim()) {
          return Promise.reject('集合名称不能为空字符');
        }
        return Promise.resolve();
      }, 
      trigger: 'blur'
    }
  ],
}

const resetForm = () => {
  modelForm.name = ''
}

const handleAdd = () => {
  dialogType.value = 'add'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(modelForm, row)
  dialogVisible.value = true
}

// 防抖函数
const debounce = (fn, delay = 500) => {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 防抖处理的提交函数
const handleSubmit = debounce(() => {
  modelFormRef.value.validate((valid) => {
    if (!valid) return
    
    if (dialogType.value === 'add') {
      const maxId = Math.max(...originData.value.map(i => i.id), 0)
      addList({
        ...modelForm,
        id: maxId + 1,
        createTime: new Date().toLocaleString('sv-SE').replace('T', ' ')
      }).then(() => {
        fetchUserList()
        ElMessage.success('新增集合成功')
      }).catch(() => {
        ElMessage.error('新增集合失败')
      })
    } else {
      updateList(modelForm).then(() => {
        fetchUserList()
        ElMessage.success('修改集合成功')
      }).catch(() => {
        ElMessage.error('修改集合失败')
      })
    }
    dialogVisible.value = false
  })
}, 300)

const submitForm = () => {
  handleSubmit()
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除指标【${row.name}】吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteList(row.id).then(() => {
      fetchUserList()
    })
  })
}

const handleDetail = (row) => {
    console.log(row)
    router.push({ name: 'Orders', params: { id: row.id } })
}
/* ------------------ 搜索 & 分页 ------------------ */
const handleSearch = () => (fetchUserList())
const handleReset = () => {
  searchQuery.value = ''
  currentPage.value = 1
  searchQuery.value = ''
  fetchUserList()
}
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchUserList()
}
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUserList()
}

onMounted(() => {
  fetchUserList()
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