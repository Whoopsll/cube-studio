<template>
  <div class="results-container">
    <div class="content">
        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="请输入指标名称"
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
          style="width: 100%;"
          v-loading="loading"
          stripe
          border
        >
          <el-table-column type="index" label="序号" min-width="80" />
          <el-table-column prop="name" label="指标名称" min-width="150" />
          <el-table-column prop="formula" label="算法公式" min-width="200" />
          <el-table-column prop="constraint" label="约束条件" min-width="100" />
          <el-table-column prop="description" label="指标描述" min-width="150" />
          <el-table-column prop="creator" label="创建人" min-width="100" />
          <el-table-column prop="createTime" label="创建时间" min-width="200" />
          <el-table-column label="操作" align="center" min-width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
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
      :title="dialogType === 'add' ? '新增指标' : '编辑指标'"
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
        <el-form-item label="指标名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入指标名称" />
        </el-form-item>

        <el-form-item label="算法公式" prop="formula">
          <el-input v-model="modelForm.formula" placeholder="例如：1-(P1-P3)/(P2-P3)" />
        </el-form-item>

        <el-form-item label="约束条件" prop="constraint">
          <el-input v-model="modelForm.constraint" placeholder="例如：P2>P3" />
        </el-form-item>

        <el-form-item label="指标描述" prop="description">
          <el-input type="textarea" v-model="modelForm.description" placeholder="请输入指标描述" />
        </el-form-item>

        <!-- 参数列表 -->
        <el-form-item label="参数列表">
          <el-table :data="modelForm.params" border size="small" style="width: 100%">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column label="参数名称">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="参数名称" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="变量">
              <template #default="{ row }">
                <el-input v-model="row.alias" placeholder="变量" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeParam($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" size="small" style="margin-top: 8px" @click="addParam">
            新增参数
          </el-button>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { parse } from 'mathjs'
import { ElMessage } from 'element-plus'
import { getList, deleteList, addList, updateList } from '@/api/UserView'

/* ------------------ 数据 ------------------ */
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
    formula: '1-(P1-P3)/(P2-P3)',
    constraint: 'P2>P3',
    description: '对潜作战',
    creator: 'admin',
    createTime: '2024-05-09 20:30:00',
    params: [
    { name: "攻击决策响应时间", alias: "P1" },
    { name: "对潜攻击指挥决策响应时间", alias: "P2" },
    { name: "对潜攻击指挥决策响应可能", alias: "P3" }
  ]
  },
  {
    id: 2,
    name: '对潜攻击指挥决策及时性',
    formula: '1-(T1-T3)/(T2-T3)',
    constraint: 'T2>T3',
    description: '对潜攻击决策',
    creator: 'admin',
    createTime: '2024-05-08 20:30:00',
    params: [
    { name: "攻击决策响应时间", alias: "P1" },
    { name: "对潜攻击指挥决策响应时间", alias: "P2" },
    { name: "对潜攻击指挥决策响应可能", alias: "P3" }
  ]
  }
])

// 算法公式
const ALLOWED_FUNCS = [
  'sin', 'cos', 'tan',
  'arcsin', 'arccos', 'arctan',
  'log', 'log10', 'log1p',
  'exp', 'expm1',
  'sqrt', 'abs', 'ceil', 'floor', 'rint'
]

// 移除 // 和 **，因为 mathjs 支持这些运算符
const ALLOWED_OPS = ['+', '-', '*', '/', '//', '**', '%', '^']

// 括号匹配函数
const isBalancedBrackets = (str) => {
  let stack = 0
  for (const ch of str) {
    if (ch === '(') stack++
    if (ch === ')') {
      if (stack === 0) return false
      stack--
    }
  }
  return stack === 0
}

const normalize = (expr) =>
  expr
    .replace(/(\w+)\s*\/\/\s*(\w+)/g, 'floor($1/$2)') // p1//p2 → floor(p1/p2)
    .replace(/(\w+)\s*\*\*\s*(\w+)/g, '$1^$2');    // p1**p2 → p1^p2

const validateFormula = (expr) => {
  if (!expr.trim()) return '请输入公式'

  // 1. 括号匹配
  if (!isBalancedBrackets(expr)) return '括号不匹配'

  // 只保留允许的字符：数字、字母、空格、括号、函数、运算符
  const normalized = normalize(expr);
  const validRegex = /^[\d+\-*/().,%^a-zA-Z\s]*$/
  if (!validRegex.test(normalized)) return '含有非法字符'

  // 3. 使用 mathjs 解析
  try {
    const node = parse(normalized, { implicit: 'hide' })
    // 可选：检查函数是否在白名单
    node.traverse(n => {
      if (n.isFunctionNode && !ALLOWED_FUNCS.includes(n.name)) {
        throw new Error(`函数 ${n.name} 不被允许`)
      }
      // 检查运算符是否在白名单
      if (n.isOperatorNode && !ALLOWED_OPS.includes(n.op)) {
        throw new Error(`运算符 ${n.op} 不被允许`)
      }
    })
    return ''
  } catch (e) {
    return e.message
  }
}
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
  formula: '',
  constraint: '',
  description: '',
  params: []
})

const rules = {
  name: [
    { required: true, message: '请输入指标名称', trigger: 'blur' },
    { 
      validator: (_, value) => {
        if (!value.trim()) {
          return Promise.reject('指标名称不能为空字符');
        }
        return Promise.resolve();
      }, 
      trigger: 'blur'
    }
  ],
  formula: [
    { required: true, message: '请输入算法公式', trigger: 'blur' },
    {
      validator: (_, value) => {
        const err = validateFormula(value)
        return err ? Promise.reject(err) : Promise.resolve()
      },
      trigger: 'blur'
    }
  ]
}

const resetForm = () => {
  modelFormRef.value?.resetFields()
  modelForm.id = null
  modelForm.name = ''
  modelForm.formula = ''
  modelForm.constraint = ''
  modelForm.description = ''
  modelForm.params = []
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

const addParam = () => {
  modelForm.params.push({ name: '', alias: '' })
}

const removeParam = (index) => {
  modelForm.params.splice(index, 1)
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
  if (dialogType.value === 'add') {
    const maxId = Math.max(...originData.value.map(i => i.id), 0)
    addList({
      ...modelForm,
      id: maxId + 1,
      creator: 'admin',
      createTime: new Date().toLocaleString('sv-SE').replace('T', ' ')
    }).then(() => {
      fetchUserList()
      ElMessage.success('新增指标成功')
    }).catch(() => {
      ElMessage.error('新增指标失败')
    })
  } else {
    updateList(modelForm).then(() => {
      fetchUserList()
      ElMessage.success('修改指标成功')
    })
  }
  dialogVisible.value = false
}, 300)

const submitForm = () => {
  modelFormRef.value.validate((valid) => {
    if (!valid) return
    handleSubmit()
  })
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