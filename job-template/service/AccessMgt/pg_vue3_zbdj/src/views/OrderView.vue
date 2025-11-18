<template>
  <div class="dictionary-system">
    <!-- 主表格页面 -->
    <div class="main-table">
      <div class="search-section">
        <div class="search-bar">
          <div>
          <el-button type="primary" @click="gotoBack">
            返回
          </el-button>
          </div>
          <div>
            <el-input
            v-model="searchText"
            placeholder="请输入名称"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button style="margin-left: 10px;" type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="mainTableData" border style="width: 100%">
          <el-table-column type="index" label="序号" width="80" align="center" />
          <el-table-column prop="name" label="名称" min-width="120" show-overflow-tooltip>
            <template #default="scope">
              <el-input 
                v-if="scope.row.editing" 
                v-model="scope.row.name" 
                size="small"
                placeholder="请输入名称"
              />
              <span v-else>{{ scope.row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <el-input 
                v-if="scope.row.editing" 
                v-model="scope.row.description" 
                size="small"
                placeholder="请输入描述"
              />
              <span v-else>{{ scope.row.description }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" min-width="180" align="center">
            <template #default="scope">
              <span>{{ scope.row.createTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="320" align="center">
            <template #default="scope">
              <!-- 编辑状态下的按钮 -->
              <template v-if="scope.row.editing">
                <el-button 
                  size="small" 
                  type="success"
                  @click="saveMainTableRow(scope.row)"
                >
                  保存
                </el-button>
                <el-button 
                  size="small" 
                  @click="cancelMainTableEdit(scope.row, scope.$index)"
                >
                  取消
                </el-button>
              </template>
              
              <!-- 非编辑状态下的按钮 -->
              <template v-else>
                <el-button 
                  size="small" 
                  type="primary"
                  @click="editMainTableRow(scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger"
                  @click="deleteMainTableRow(scope.row)"
                >
                  删除
                </el-button>
                
                <el-dropdown @command="handleOperation" trigger="click" style="margin-left: 8px;">
                  <el-button type="info" size="small" class="operation-btn">
                    更多
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{action: 'dictionary', row: scope.row}">
                        <el-icon><Setting /></el-icon>
                        字典管理
                      </el-dropdown-item>
                      <el-dropdown-item :command="{action: 'rawData', row: scope.row}">
                        <el-icon><Document /></el-icon>
                        查看原始数据
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </template>
          </el-table-column>
        </el-table>
        
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

    <!-- 字典管理弹框 -->
    <el-dialog 
      v-model="dictionaryDialogVisible" 
      title="字典管理" 
      width="900px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <!-- 字典管理搜索区域 -->
        <div class="dictionary-search">
          <el-input
            v-model="dictionarySearchText"
            placeholder="请输入参数名称或别名进行搜索"
            class="search-input"
            clearable
            @input="handleDictionarySearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleDictionarySearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetDictionarySearch">重置</el-button>
        </div>

        <div class="dialog-toolbar">
          <el-button type="primary" @click="addDictionary">
            <el-icon><Plus /></el-icon>
            新增参数
          </el-button>
        </div>
        
        <el-table :data="filteredDictionaryData" border>
          <el-table-column type="index" label="序号" width="80" align="center" />
          <el-table-column label="参数名称" min-width="180">
            <template #default="scope">
              <el-input 
                v-if="scope.row.editing" 
                v-model="scope.row.col_name" 
                size="small"
                placeholder="请输入参数名称"
              />
              <span v-else>{{ scope.row.col_name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="参数别名" min-width="150">
            <template #default="scope">
              <el-input 
                v-if="scope.row.editing" 
                v-model="scope.row.col_field_name" 
                size="small"
                placeholder="请输入参数别名"
              />
              <span v-else>{{ scope.row.col_field_name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="参数类型" min-width="150">
            <template #default="scope">
              <el-select 
                v-if="scope.row.editing" 
                v-model="scope.row.col_type" 
                size="small"
                placeholder="请选择参数类型"
                style="width: 100%"
              >
                <el-option
                  v-for="item in parameterTypes"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <div class="type-option">
                    <el-icon class="type-icon">
                      <component :is="item.icon" />
                    </el-icon>
                    <span>{{ item.label }}</span>
                  </div>
                </el-option>
              </el-select>
              <span v-else class="type-display">
                <el-icon class="type-icon">
                  <component :is="getTypeIcon(scope.row.col_type)" />
                </el-icon>
                {{ getTypeLabel(scope.row.col_type) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="180" align="center">
            <template #default="scope">
              <el-button 
                v-if="!scope.row.editing" 
                size="small" 
                type="primary"
                @click="editDictionary(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                v-else 
                size="small" 
                type="success"
                @click="saveDictionary(scope.row)"
              >
                保存
              </el-button>
              <el-button 
                v-if="scope.row.editing" 
                size="small" 
                @click="cancelDictionaryEdit(scope.row, scope.$index)"
              >
                取消
              </el-button>
              <el-button 
                v-if="!scope.row.editing"
                size="small" 
                type="danger" 
                @click="deleteDictionary(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 字典搜索结果统计 -->
        <div class="search-result-info" v-if="dictionarySearchText">
          <span>搜索结果：共找到 {{ filteredDictionaryData.length }} 个参数</span>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dictionaryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmDictionary">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 原始数据弹框 -->
    <el-dialog 
      v-model="rawDataDialogVisible" 
      title="原始数据管理" 
      width="1200px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <!-- 搜索区域 -->
        <div class="raw-data-search">
          <el-input
            v-model="rawDataSearchText"
            placeholder="请输入参数名称搜索对应列数据"
            class="search-input"
            clearable
            @input="handleRawDataSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleRawDataSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetRawDataSearch">重置</el-button>
        </div>

        <div class="dialog-toolbar">
          <el-button type="primary" @click="addRawData">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          
          <!-- 导出按钮组 -->
          <el-dropdown @command="handleExport" trigger="click">
            <el-button type="success">
              <el-icon><Download /></el-icon>
              导出
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="excel">
                  <el-icon><Document /></el-icon>
                  导出Excel
                </el-dropdown-item>
                <el-dropdown-item command="csv">
                  <el-icon><Document /></el-icon>
                  导出CSV
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 导入按钮组 -->
          <el-dropdown trigger="click">
            <el-button type="warning">
              <el-icon><Upload /></el-icon>
              导入
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <el-upload
                    :show-file-list="false"
                    :before-upload="(file) => importFile(file, 'excel')"
                    accept=".xlsx,.xls"
                    class="upload-item"
                  >
                    <div class="upload-content">
                      <el-icon><Document /></el-icon>
                      <span>导入Excel</span>
                    </div>
                  </el-upload>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-upload
                    :show-file-list="false"
                    :before-upload="(file) => importFile(file, 'csv')"
                    accept=".csv"
                    class="upload-item"
                  >
                    <div class="upload-content">
                      <el-icon><Document /></el-icon>
                      <span>导入CSV</span>
                    </div>
                  </el-upload>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- 动态生成的表格 -->
        <el-table :data="paginatedRawData" border style="width: 100%; max-height: 400px; overflow: auto;">
          <el-table-column type="index" label="序号" min-width="80" align="center" />
          
          <!-- 动态生成字典参数列 - 根据搜索结果过滤 -->
          <el-table-column 
            v-for="param in filteredParameterColumns" 
            :key="param.col_field_name"
            :label="param.col_name"
            :width="150"
            show-overflow-tooltip
          >
            <template #header>
              <div class="param-header">
                <div class="param-name">{{ param.col_name }}</div>
                <div class="param-info">
                  <span class="param-col_field_name">{{ param.col_field_name }}</span>
                  <el-icon class="type-icon">
                    <component :is="getTypeIcon(param.col_type)" />
                  </el-icon>
                </div>
              </div>
            </template>
            <template #default="scope">
              <el-input 
                v-if="scope.row.editing" 
                v-model="scope.row.row_data[param.col_field_name]" 
                size="small"
                :placeholder="`请输入${param.col_name}`"
              />
              <span v-else>{{ scope.row.row_data[param.col_field_name] || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" min-width="220" align="center" fixed="right">
            <template #default="scope">
              <el-button 
                v-if="!scope.row.editing" 
                size="small" 
                type="primary"
                @click="editRawData(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                v-else 
                size="small" 
                type="success"
                @click="saveRawData(scope.row)"
              >
                保存
              </el-button>
              <el-button 
                v-if="scope.row.editing" 
                size="small" 
                @click="cancelRawDataEdit(scope.row, scope.$index)"
              >
                取消
              </el-button>
              <el-button 
                v-if="!scope.row.editing"
                size="small" 
                type="danger" 
                @click="deleteRawData(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 搜索结果统计 -->
        <div class="search-result-info" v-if="rawDataSearchText">
          <span>显示参数：{{ filteredParameterColumns.map(p => p.col_name).join('、') }} ({{ filteredParameterColumns.length }} 列)</span>
        </div>

        <!-- 原始数据分页 -->
        <div class="pagination-container">
          <div class="pagination-info">
            <span>共 {{ totalRaw }} 条，{{ rawDataPageSize }}/页</span>
          </div>
          <el-pagination
            v-model:current-page="rawDataCurrentPage"
            v-model:page-size="rawDataPageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="totalRaw"
            layout="prev, pager, next, sizes"
            @size-change="handleRawDataSizeChange"
            @current-change="handleRawDataCurrentChange"
          />
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="rawDataDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入确认弹框 -->
    <el-dialog 
      v-model="importConfirmVisible" 
      title="导入确认" 
      width="500px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <div class="import-confirm-content">
        <div class="confirm-icon">
          <el-icon size="48" color="#E6A23C"><Warning /></el-icon>
        </div>
        <div class="confirm-text">
          <h3>确认导入文件</h3>
          <p>文件名：{{ pendingImportFile?.name }}</p>
          <p>文件大小：{{ pendingImportFile ? (pendingImportFile.size / 1024).toFixed(2) + ' KB' : '' }}</p>
          <div class="cover-options">
            <p class="cover-question">是否覆盖现有数据？</p>
            <div class="cover-buttons">
              <el-button type="danger" @click="confirmImport(true)">
                <el-icon><Delete /></el-icon>
                覆盖导入
              </el-button>
              <el-button type="primary" @click="confirmImport(false)">
                <el-icon><Plus /></el-icon>
                追加导入
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelImport">取消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="600px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="100px" class="form-style">
        <el-form-item label="名称" required>
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveForm">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { getInferentialList, deleteList, addList, updateList } from '@/api/OrderView'
import { getDictList, addDictList, deleteDictList, updateDictList } from '@/api/OrderView'
import { getRawList, addRawList, deleteRawList, updateRawList, importRawFile, exportRawFile } from '@/api/OrderView'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const collectId = ref(route.params.id)
const parameterTypes = ref([
  { value: 'int', label: '整数 (int)', icon: 'Histogram' },
  { value: 'float', label: '浮点数 (float)', icon: 'TrendCharts' },
  { value: 'string', label: '字符串 (string)', icon: 'Document' },
  { value: 'boolean', label: '布尔值 (boolean)', icon: 'Select' },
  { value: 'date', label: '日期 (date)', icon: 'Calendar' },
])

// 获取类型图标
const getTypeIcon = (type) => {
  const typeConfig = parameterTypes.value.find(item => item.value === type)
  return typeConfig ? typeConfig.icon : 'Document'
}

// 获取类型标签
const getTypeLabel = (type) => {
  const typeConfig = parameterTypes.value.find(item => item.value === type)
  return typeConfig ? typeConfig.label : type
}

// 搜索相关
const searchText = ref('')
const dictionarySearchText = ref('')
const rawDataSearchText = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(2)

// 原始数据分页相关
const rawDataCurrentPage = ref(1)
const rawDataPageSize = ref(10)
const totalRaw = ref(0)

// 弹框控制
const dictionaryDialogVisible = ref(false)
const rawDataDialogVisible = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')

// 添加导入确认弹框状态
const importConfirmVisible = ref(false)
const pendingImportFile = ref(null)
const pendingImportFormat = ref('')

// 主表格数据
const mainTableData = ref([
  {
    id: 1,
    name: '测试',
    description: '测试修改',
    createTime: '2025-07-22 16:45:51',
    editing: false
  },
  {
    id: 2,
    name: '测试序号',
    description: '测试',
    createTime: '2025-07-22 16:50:40',
    editing: false
  }
])

// 字典数据
const dictionaryId = ref(0)
const dictionary_uuId = ref(0)
const dictionaryData = ref([
  { id: 1, col_name: '测试参数一', col_field_name: 'p1', col_type: 'int', editing: false },
  { id: 2, col_name: '测试参数二', col_field_name: 'p2', col_type: 'float', editing: false },
  { id: 3, col_name: '测试参数三', col_field_name: 'p3', col_type: 'string', editing: false },
  { id: 4, col_name: '额外参数', col_field_name: 'p4', col_type: 'boolean', editing: false },
  { id: 5, col_name: '特殊参数', col_field_name: 'special', col_type: 'date', editing: false }
])

// 字典数据搜索过滤
const filteredDictionaryData = computed(() => {
  if (!dictionarySearchText.value.trim()) {
    return dictionaryData.value
  }
  
  const searchTerm = dictionarySearchText.value.toLowerCase().trim()
  return dictionaryData.value.filter(item => {
    return item.col_name.toLowerCase().includes(searchTerm) ||
           item.col_field_name.toLowerCase().includes(searchTerm)
  })
})

// 原始数据参数列过滤 - 根据参数名称搜索
const filteredParameterColumns = computed(() => {
  if (!rawDataSearchText.value.trim()) {
    return dictionaryData.value
  }
  
  const searchTerm = rawDataSearchText.value.toLowerCase().trim()
  return dictionaryData.value.filter(param => {
    return param.col_name.toLowerCase().includes(searchTerm) ||
           param.col_field_name.toLowerCase().includes(searchTerm)
  })
})

// 原始数据
const rawData = ref([
  { 
    id: 12, 
    row_data: { p1: '650', p2: '1300.2', p3: 'test12', p4: 'false', special: '2025-01-12' }, 
    description: '第十二组测试数据',
    editing: false 
  }
])

// 分页后的原始数据 - 直接使用从服务器获取的数据
const paginatedRawData = computed(() => {
  return rawData.value
})

// 表单数据
const formData = reactive({
  name: '',
  description: '',
})

// 解析CSV字符串为对象数组
const parseCSVString = (csvString) => {
  try {
    const lines = csvString.trim().split('\n')
    if (lines.length === 0) return []
    
    // 获取表头
    const headers = lines[0].split(',').map(header => header.trim())
    
    // 解析数据行
    const data = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(value => value.trim())
      const row = {}
      headers.forEach((header, index) => {
        row[header] = values[index] || ''
      })
      data.push(row)
    }
    
    return data
  } catch (error) {
    console.error('CSV解析失败:', error)
    return []
  }
}

// 导出功能 - 修复版本
const handleExport = async (format) => {
  try {
    // 显示加载状态
    const loading = ElLoading.service({
      lock: true,
      text: '正在导出数据...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    // 准备请求数据
    const exportData = {
      basic_id: dictionaryId.value,
      basic_uuid: dictionary_uuId.value
    }
    
    // 调用导出API
    const response = await exportRawFile(exportData)
    
    // 关闭加载状态
    loading.close()
    
    // 处理返回的数据
    let processedData = []
    
    // 检查响应数据的格式
    if (typeof response === 'string') {
      // 如果返回的是字符串格式（CSV格式），需要解析
      processedData = parseCSVString(response)
    } else if (Array.isArray(response)) {
      // 如果返回的是数组格式，直接使用
      processedData = response
    } else if (response && typeof response === 'object') {
      // 如果返回的是对象，可能需要进一步处理
      if (response && Array.isArray(response)) {
        processedData = response
      } else {
        // 尝试将对象转换为数组
        processedData = [response]
      }
    }
    
    if (!processedData || processedData.length === 0) {
      ElMessage.warning('没有数据可导出')
      return
    }
    
    // 根据格式生成文件
    if (format === 'excel') {
      generateExcelFile(processedData)
    } else if (format === 'csv') {
      generateCSVFile(processedData)
    }
    
    ElMessage.success(`${format.toUpperCase()}导出成功`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  }
}

// 生成Excel文件 - 修复版本
const generateExcelFile = (data) => {
  try {
    // 处理数据，添加序号列
    const processedData = data.map((row, index) => {
      return {
        '序号': index + 1,
        ...row
      }
    })
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(processedData)
    
    // 设置列宽
    const colWidths = []
    if (processedData.length > 0) {
      Object.keys(processedData[0]).forEach(() => {
        colWidths.push({ wch: 15 })
      })
    }
    ws['!cols'] = colWidths
    
    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(wb, ws, '原始数据')
    
    // 生成文件名
    const fileName = `原始数据_${new Date().toISOString().slice(0, 10)}.xlsx`
    
    // 导出文件
    XLSX.writeFile(wb, fileName)
  } catch (error) {
    console.error('Excel文件生成失败:', error)
    ElMessage.error('Excel文件生成失败')
  }
}

// 生成CSV文件 - 修复版本
const generateCSVFile = (data) => {
  try {
    // 处理数据，添加序号列
    const processedData = data.map((row, index) => {
      return {
        '序号': index + 1,
        ...row
      }
    })
    
    if (processedData.length === 0) {
      ElMessage.warning('没有数据可导出')
      return
    }
    
    // 获取表头
    const headers = Object.keys(processedData[0])
    
    // 构建CSV内容
    let csvContent = '\uFEFF' // 添加BOM以支持中文
    csvContent += headers.join(',') + '\n'
    
    // 添加数据行
    processedData.forEach(row => {
      const values = headers.map(header => {
        const value = row[header] || ''
        // 如果值包含逗号、引号或换行符，需要用引号包围并转义引号
        if (value.toString().includes(',') || value.toString().includes('"') || value.toString().includes('\n')) {
          return `"${value.toString().replace(/"/g, '""')}"`
        }
        return value
      })
      csvContent += values.join(',') + '\n'
    })
    
    // 创建Blob并下载
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const fileName = `原始数据_${new Date().toISOString().slice(0, 10)}.csv`
    saveAs(blob, fileName)
  } catch (error) {
    console.error('CSV文件生成失败:', error)
    ElMessage.error('CSV文件生成失败')
  }
}

// 导入文件处理
const importFile = (file, format) => {
  // 存储待导入的文件信息
  pendingImportFile.value = file
  pendingImportFormat.value = format
  
  // 显示确认弹框
  importConfirmVisible.value = true
  
  return false // 阻止默认上传行为
}

// 确认导入
const confirmImport = async (isCover) => {
  if (!pendingImportFile.value) {
    ElMessage.error('没有选择文件')
    return
  }

  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', pendingImportFile.value)
    formData.append('basic_uuid', dictionary_uuId.value.toString())
    formData.append('is_cover', isCover.toString())
    formData.append('basic_id', dictionaryId.value.toString())

    // 调用导入API
    const res = await importRawFile(formData)
    
    // 导入成功
    ElMessage.success(`文件导入成功`)
    
    // 刷新数据
    await getRawDataList()
    
    // 关闭确认弹框
    importConfirmVisible.value = false
    
    // 清理临时数据
    pendingImportFile.value = null
    pendingImportFormat.value = ''
    
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败，请检查文件格式')
  }
}

// 取消导入
const cancelImport = () => {
  importConfirmVisible.value = false
  pendingImportFile.value = null
  pendingImportFormat.value = ''
}

const gotoBack = () => {
  router.push('/inferential-data')
}

// 搜索功能
const handleSearch = () => {
  getMainTableData()
  ElMessage.success('搜索成功')
}

// 重置功能
const handleReset = () => {
  searchText.value = ''
  getMainTableData()
  ElMessage.success('重置成功')
}

// 新增功能
const handleAdd = () => {
  dialogTitle.value = '新增推演数据'
  Object.keys(formData).forEach(key => formData[key] = '')
  dialogVisible.value = true
}

// 主表格编辑功能
const editMainTableRow = (row) => {
  // 保存原始数据用于取消操作
  row.originalData = {
    name: row.name,
    description: row.description
  }
  row.editing = true
}

// 获取主表格数据
const getMainTableData = async () => {
  const data = {
    page: currentPage.value,
    num: pageSize.value,
    name: searchText.value,
    collect_id: collectId.value
  }
  const res = await getInferentialList(data)
  mainTableData.value = res.data.info
  total.value = res.data.total_num
}

// 获取字典管理列表
const getDictionaryList = async (id) => {
  const res = await getDictList(id)
  dictionaryData.value = res.data.info
  filteredDictionaryData.value = res.data.info
}

// 获取原始数据列表
const getRawDataList = async () => {
  try {
    const data = {
      page: rawDataCurrentPage.value,
      num: rawDataPageSize.value,
      basic_uuid: dictionary_uuId.value
    }
    const res = await getRawList(data)
    rawData.value = res.data.info || []
    totalRaw.value = res.data.total || 0
    console.log('原始数据获取结果:', res)
  } catch (error) {
    console.error('获取原始数据失败:', error)
    ElMessage.error('获取原始数据失败')
    rawData.value = []
    totalRaw.value = 0
  }
}

// 保存主表格数据
const saveMainTableRow = (row) => {
  if (!row.name.trim()) {
    ElMessage.warning('指标名称不能为空')
    return
  }
  delete row.originalData
  updateList(row).then(res => {
    getMainTableData()
    row.editing = false
    ElMessage.success('保存成功')
  })
}

const cancelMainTableEdit = (row, index) => {
  if (row.originalData) {
    row.name = row.originalData.name
    row.description = row.originalData.description
    delete row.originalData
  }
  row.editing = false
}

const deleteMainTableRow = (row) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteList(row.id).then(res => {
      getMainTableData()
      ElMessage.success('删除成功')
    })
  })
}

// 操作下拉菜单
const handleOperation = async(command) => {
  dictionaryId.value = command.row.id
  dictionary_uuId.value = command.row.row_data_uuid
  if (command.action === 'dictionary') {
    getDictionaryList(command.row.id)
    dictionaryDialogVisible.value = true
  } else if (command.action === 'rawData') {
    // 打开原始数据弹框时重置分页
    rawDataCurrentPage.value = 1
    rawDataDialogVisible.value = true
    getDictionaryList(command.row.id)
    getRawDataList()
  }
}

// 字典管理搜索功能
const handleDictionarySearch = () => {
  getDictionaryList(dictionaryId.value)
  ElMessage.success(`搜索完成，找到 ${filteredDictionaryData.value.length} 个参数`)
}

// 重置字典管理搜索
const resetDictionarySearch = () => {
  dictionarySearchText.value = ''
  ElMessage.success('搜索重置成功')
}

// 原始数据搜索功能
const handleRawDataSearch = () => {
  // 搜索时重置分页到第一页
  rawDataCurrentPage.value = 1
  
  if (rawDataSearchText.value.trim()) {
    ElMessage.success(`搜索完成，显示 ${filteredParameterColumns.value.length} 个匹配的参数列`)
  } else {
    ElMessage.success('显示所有参数列')
  }
}

// 重置原始数据搜索
const resetRawDataSearch = () => {
  rawDataSearchText.value = ''
  rawDataCurrentPage.value = 1
  ElMessage.success('搜索重置成功，显示所有参数列')
}

// 原始数据分页处理
const handleRawDataSizeChange = (val) => {
  rawDataPageSize.value = val
  rawDataCurrentPage.value = 1 // 重置到第一页
  getRawDataList() // 重新获取数据
}

const handleRawDataCurrentChange = (val) => {
  rawDataCurrentPage.value = val
  getRawDataList() // 重新获取数据
}

// 字典管理相关
const editDictionary = (row) => {
  row.editing = true
  row.first = false
}

const saveDictionary = (row) => {
  if (!row.col_name.trim() || !row.col_field_name.trim() || !row.col_type) {
    ElMessage.warning('参数名称、别名和类型不能为空')
    return
  }
  console.log('row', row)
  if(row.first === true) {
    const data = {
    id: dictionaryId.value,
    basic_id: dictionaryId.value,
    col_name: row.col_name,
    col_field_name: row.col_field_name,
    col_type: row.col_type,
  }
  console.log('data', data)
  addDictList(data).then(res => {
    row.editing = false
    getDictionaryList(dictionaryId.value)
    ElMessage.success('保存成功')
  })
  } else {
    updateDictList(row).then(res => {
      row.editing = false
      getDictionaryList(dictionaryId.value)
      ElMessage.success('保存成功')
    })
  }
}

const deleteDictionary = (row) => {
  // 需要从原始数据中找到对应的参数
  // const actualIndex = dictionaryData.value.findIndex(item => item.id === filteredDictionaryData.value[index].id)
  
  ElMessageBox.confirm('确定要删除这个参数吗？删除后原始数据中对应的列也会被删除。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteDictList(row.id).then(res => {
      getDictionaryList(dictionaryId.value)
    })
    ElMessage.success('删除成功')
  })
}

const addDictionary = () => {
  const newId = Math.max(...dictionaryData.value.map(item => item.id)) + 1
  dictionaryData.value.push({
    id: newId,
    col_name: '',
    col_field_name: '',
    col_type: 'string',
    editing: true,
    isNew: true,
    first: true
  })
}

// 字典管理取消编辑
const cancelDictionaryEdit = (row, index) => {
  if (row.isNew) {
    // 需要从原始数据中找到对应的参数
    const actualIndex = dictionaryData.value.findIndex(item => item.id === row.id)
    dictionaryData.value.splice(actualIndex, 1)
  } else {
    if (row.originalData) {
      Object.keys(row.originalData).forEach(key => {
        if (key !== 'originalData' && key !== 'isNew') {
          row[key] = row.originalData[key]
        }
      })
      delete row.originalData
    }
    row.editing = false
  }
}

const confirmDictionary = () => {
  const hasEditing = dictionaryData.value.some(item => item.editing)
  if (hasEditing) {
    ElMessage.warning('请先保存正在编辑的参数')
    return
  }
  
  // 为新增的字典参数在原始数据中添加对应的值字段
  dictionaryData.value.forEach(param => {
    if (param.isNew) {
      rawData.value.forEach(item => {
        if (!item.row_data[param.col_field_name]) {
          item.row_data[param.col_field_name] = ''
        }
      })
      delete param.isNew
    }
  })
  
  ElMessage.success('字典管理保存成功')
  dictionaryDialogVisible.value = false
}

// 原始数据相关
const addRawData = () => {
  const newValues = {}
  
  // 为每个字典参数创建空值
  dictionaryData.value.forEach(param => {
    newValues[param.col_field_name] = ''
  })
  
  // 在当前页面数据中添加新行用于编辑
  rawData.value.unshift({
    id: Date.now(), // 临时ID
    basic_id: dictionary_uuId.value,
    row_data: { ...newValues},
    description: '',
    editing: true,
    isNew: true,
    first: true
  })
}

const editRawData = (row) => {
  row.editing = true
  row.originalData = { 
    row_data: { ...row.row_data },
    description: row.description,
    first: false
  }
}

const saveRawData = (row) => {
  // 检查是否至少填写了一个参数值
  console.log('row', row)
  const hasValue = Object.values(row.row_data).some(value => value && value.trim())
  if (!hasValue) {
    ElMessage.warning('请至少填写一个参数值')
    return
  }
  delete row.originalData
  delete row.isNew
  const data = {
    id: row.id,
    basic_uuid: dictionary_uuId.value,
    row_data: row.row_data,
    description: row.description
  }
  console.log('data', row)
  if(row.first === true) {
    addRawList(data).then(res => {
      row.editing = false
      getRawDataList()
      ElMessage.success('保存成功')
    })
  } else {
    updateRawList(data).then(res => {
      row.editing = false
      getRawDataList()
      ElMessage.success('保存成功')
    })
  }
}

// 原始数据取消编辑
const cancelRawDataEdit = (row, index) => {
  if (row.isNew) {
    const originalIndex = rawData.value.findIndex(item => item.id === row.id)
    if (originalIndex !== -1) {
      rawData.value.splice(originalIndex, 1)
    }
  } else {
    if (row.originalData) {
      row.row_data = { ...row.originalData.row_data }
      row.description = row.originalData.description
      delete row.originalData
    }
    row.editing = false
  }
}

const deleteRawData = (row) => {
  ElMessageBox.confirm('确定要删除这条数据吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const data = {
      id: row.id,
      basic_uuid: dictionary_uuId.value
    }
    
    deleteRawList(data).then(res => {
      // 删除成功后重新获取数据
      getRawDataList()
      ElMessage.success('删除成功')
      
      // 如果当前页没有数据了，且不是第一页，则跳转到前一页
      setTimeout(() => {
        if (rawData.value.length === 0 && rawDataCurrentPage.value > 1) {
          rawDataCurrentPage.value--
          getRawDataList()
        }
      }, 100)
    }).catch(error => {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    })
  })
}

// 分页相关
const handleSizeChange = (val) => {
  pageSize.value = val
  getMainTableData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  getMainTableData()
}

// 防抖函数
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 表单验证函数
const validateForm = () => {
  // 检查名称是否为空或仅包含空格
  if (!formData.name || !formData.name.trim()) {
    ElMessage.warning('名称不能为空，请输入有效的名称')
    return false
  }
  return true
}

// 使用防抖包装的API提交函数
const submitFormWithDebounce = debounce(async () => {
  try {
    // 构建提交数据
    const submitData = {
      ...formData,
      collect_id: collectId.value,
      id: 0,
      createTime: new Date().toLocaleString('sv-SE').replace('T', ' ')
    }
    
    // 调用API
    await addList(submitData)
    
    // 刷新数据
    getMainTableData()
    
    // 显示成功消息
    ElMessage.success('保存成功')
    
    // 关闭弹窗
    dialogVisible.value = false
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  }
}, 500); // 500毫秒防抖

// 保存表单
const saveForm = () => {
  // 执行表单验证
  if (!validateForm()) {
    return
  }
  
  // 调用带防抖的提交函数
  submitFormWithDebounce();
}

onMounted(() => {
  getMainTableData()
})
</script>

<style scoped>
.main-table {
  background-color: #050b0d;
  padding: 24px;
}
.dictionary-system {
  background-color: #050b0d;;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
}

.search-input {
  width: 280px;
}

.table-container {
  background: #050b0d;
  overflow: hidden;
}

.operation-btn {
  border: none;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.operation-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #195877;
}

.pagination-info {
  color: #606266;
  font-size: 14px;
}

.custom-dialog {
  border-radius: 12px;
}

:deep(.custom-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-radius: 12px 12px 0 0;
}

:deep(.custom-dialog .el-dialog__title) {
  font-weight: 600;
  font-size: 18px;
}

:deep(.custom-dialog .el-dialog__headerbtn .el-dialog__close) {
  font-size: 20px;
}

.dialog-content {
  padding: 20px 0;
}

.dictionary-search,
.raw-data-search {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #195877;
  border-radius: 6px;
}

.dialog-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.upload-btn {
  display: inline-block;
}

.upload-item {
  width: 100%;
}

.upload-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  width: 100%;
}

.search-result-info {
  margin-top: 16px;
  padding: 8px 12px;
  background-color: #e8f4fd;
  border-left: 4px solid #409eff;
  color: #409eff;
  font-size: 14px;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
}

.form-style {
  padding: 0 20px;
}

/* 参数表头样式 */
.param-header {
  text-align: center;
}

.param-name {
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.param-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: #fff;
}

.param-alias {
  background-color: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

/* 参数类型相关样式 */
.type-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-display {
  display: flex;
  align-items: center;
  gap: 6px;
}

.type-icon {
  font-size: 14px;
  color: #409eff;
}

:deep(.form-style .el-form-item__label) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-button--primary) {
  border: none;
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--success) {
  border: none;
}

:deep(.el-button--warning) {
  border: none;
}

:deep(.el-button--danger) {
  border: none;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f5f7fa;
  color: #409eff;
}

:deep(.el-select-dropdown__item) {
  padding: 8px 12px;
}

/* 表格滚动样式 */
:deep(.el-table__body-wrapper) {
  overflow-x: auto;
}

.import-confirm-content {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px 0;
}

.confirm-icon {
  flex-shrink: 0;
}

.confirm-text {
  flex: 1;
}

.confirm-text h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.confirm-text p {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

.cover-options {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.cover-question {
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.cover-buttons {
  display: flex;
  gap: 12px;
}

.cover-buttons .el-button {
  flex: 1;
  height: 40px;
}
</style>