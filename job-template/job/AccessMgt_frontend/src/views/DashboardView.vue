<template>
  <div class="results-container">
    <div class="content">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="请输入体系名称"
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

        <!-- 数据表格 -->
        <div class="table-container">
          <el-table
          :data="originData"
          style="width: 100%"
          v-loading="loading"
          stripe
          border
        >
          <el-table-column type="index" label="序号" width="80" />
          <el-table-column prop="name" label="体系名称" min-width="200" />
          <el-table-column prop="description" label="体系描述" min-width="200" />
          <el-table-column prop="createTime" label="创建时间" min-width="200" />
          <el-table-column label="操作" align="center" min-width="250" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" @click="handleCopy(scope.row)">复制</el-button>
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
      :title="dialogType === 'add' ? '新增体系' : '编辑体系'"
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
        <el-form-item label="体系名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入体系名称" />
        </el-form-item>
        <el-form-item label="体系描述" prop="description">
          <el-input type="textarea" v-model="modelForm.description" placeholder="请输入体系描述" />
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
import { useRouter } from 'vue-router'
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getList, deleteList, addList, updateList, copyList} from '@/api/DashboardApi'

/* ------------------ 数据 ------------------ */
const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
// 模拟数据
const originData = ref([
  {
    id: 1,
    name: '攻击及时性',
    description: '对潜作战',
    createTime: '2024-05-09 20:30:00',
  },
  {
    id: 2,
    name: '对潜攻击指挥决策及时性',
    description: '对潜攻击决策',
    createTime: '2024-05-08 20:30:00',
  }
])

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

/* ------------------ 表格数据 ------------------ */
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

/* ------------------ 表单 ------------------ */
const dialogVisible = ref(false)
const dialogType = ref('add')
const modelFormRef = ref()

const modelForm = reactive({
  id: null,
  name: '',
  description: '',
})

const rules = {
  name: [
    { required: true, message: '请输入体系名称', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim() === '') {
          callback(new Error('体系名称不能为空字符'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
}

const resetForm = () => {
  modelFormRef.value?.resetFields()
  modelForm.id = null
  modelForm.name = ''
  modelForm.description = ''
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

const handleDetail = (row) => {
    console.log(row)
    router.push({ name: 'Analytics', params: { id: row.id } })
}

// 防抖函数
const debounce = (fn, delay = 300) => {
  let timer = null;
  return function (...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
};

// 新增提交的防抖处理
const handleAddSubmit = debounce((formData) => {
  const maxId = Math.max(...originData.value.map(i => i.id), 0)
  addList({
    ...formData,
    id: maxId + 1,
    createTime: new Date().toLocaleString('sv-SE').replace('T', ' ')
  }).then(() => {
    fetchUserList()
    ElMessage.success('新增体系成功')
    dialogVisible.value = false
  })
}, 500);

// 编辑提交的防抖处理
const handleEditSubmit = debounce((formData) => {
  updateList(formData).then(() => {
    fetchUserList()
    ElMessage.success('修改体系成功')
    dialogVisible.value = false
  })
}, 500);

const submitForm = () => {
  modelFormRef.value.validate((valid) => {
    if (!valid) return;
    if (dialogType.value === 'add') {
      handleAddSubmit(modelForm);
    } else {
      handleEditSubmit(modelForm);
    }
  });
};

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除体系【${row.name}】吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteList(row.id).then(() => {
      fetchUserList()
    })
  })
}

const handleCopy = async (row) => {
  // 获取详情数据
  await copyList(row.id).then(res => {
    fetchUserList()
    ElMessage.success('复制体系成功')
  });
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
  margin: 20px auto;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}
</style>