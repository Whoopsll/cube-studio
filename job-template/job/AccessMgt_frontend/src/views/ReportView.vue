<template>
  <div class="report-container">
    <!-- 颜色选择器弹窗 -->
    <el-dialog v-model="colorPickerVisible" title="选择颜色" width="30%">
      <div class="color-picker-container">
        <el-color-picker v-model="selectedColor" show-alpha></el-color-picker>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="colorPickerVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmColorChange">确定</el-button>
        </span>
      </template>
    </el-dialog>
    <div class="report-header">
      <h3>评估名称：{{ reportTitle }}</h3>
      <div>
        <!-- <el-button @click="saveReport">评估结果保存</el-button> -->
        <el-button @click="exportReport">评估结果导出并保存</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>

    <!-- 滚动内容容器 -->
    <div class="scroll-container">
      <!-- 层级指标表格 -->
      <div class="report-section">
        <div class="hierarchy-table">
          <table>
            <thead>
              <tr>
                <th v-for="(level, index) in levels" :key="index">{{ level }}级指标</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.id">
                <td v-for="(cell, index) in row.cells.filter(c => !c.hidden)" :key="index" :class="{ 'has-score': cell.score }" :rowspan="cell.rowspan || 1">
                  <div class="cell-content">
                    <div v-if="cell.label">{{ cell.label }}</div>
                    <div v-if="cell.score >= 0" class="score">得分: {{ cell.score.toFixed(2) }}</div>
                    <div v-if="cell.details" class="method-info">
                    <!-- 有子节点的指标：仅展示权重分析方法和指标算法 -->
                    <template v-if="cell.children && cell.children.length > 0">
                      <div v-if="cell.details.selectedAnalysisMethod">权重方法: {{ getLabelByValue(cell.details.selectedAnalysisMethod, analysisMethodMap) }}</div>
                      <div v-if="cell.details.selectedAlgorithm">指标算法: {{ getLabelByValue(cell.details.selectedAlgorithm, algorithmMap) }}</div>
                    </template>
                    <!-- 无子节点的指标：展示归一化算法和评分方式 -->
                    <template v-else>
                      <div v-if="cell.details.normalizationAlgorithm">归一化算法: {{ getLabelByValue(cell.details.normalizationAlgorithm, normalizationMap) }}</div>
                      <div v-if="cell.details.scoringMethod">评分方式: {{ getLabelByValue(cell.details.scoringMethod, scoringMethodMap) }}</div>
                      <!-- 仅当评分方式为公式计算时才显示公式 -->
                      <div v-if="cell.details.scoringMethod === 'formula' && cell.details.formula">公式: {{ cell.details.formula }}</div>
                    </template>
                  </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ECharts图表区域 -->
      <div class="report-section">
        <div class="charts-container">
          <div class="chart-item">
            <div class="chart-controls">
              <div style="display: flex; justify-content: space-between;">
                <el-select v-model="currentLevel" @change="handleLevelChange" class="custom-select">
                  <el-option v-for="level in levels" :key="level" :label="level + '级指标'" :value="level"></el-option>
                </el-select>
                <el-button @click="toggleChartType" class="chart-type-btn">
                  {{ chartType === 'bar' ? '切换为折线图' : '切换为条形图' }}
                </el-button>
              </div>
            </div>
            <h3>{{ chartTitles[chartType] }}</h3>
            <div ref="barChart" class="chart"></div>
          </div>
          <div class="chart-item">
            <div class="chart-controls">
              <el-select v-model="currentLevel" @change="handleLevelChange" class="custom-select">
                <el-option v-for="level in levels" :key="level" :label="level + '级指标'" :value="level"></el-option>
              </el-select>
            </div>
            <h3>{{ chartTitles.pie }}</h3>
            <div ref="pieChart" class="chart"></div>
          </div>
          <div class="chart-item">
            <div class="chart-controls">
              <el-select v-model="currentLevel" @change="handleLevelChange" class="custom-select">
                <el-option v-for="level in levels" :key="level" :label="level + '级指标'" :value="level"></el-option>
              </el-select>
            </div>
            <h3>{{ chartTitles.line }}</h3>
            <div ref="lineChart" class="chart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 权重分析方法映射
const analysisMethodMap = {
  'ahp': 'AHP层次分析法',
  'Coefficient': '变异系数法',
  'EntropyWeight': '熵权法',
  'directEmpowerment': '直接赋权法',
  'GreyRelationalAnalysis': '灰色关联分析法',
  'DareMethod': '环比系数法',
  'FactorAnalysis': '因子分析法',
  'PcaWeight': '主成分分析法'
};

// 指标算法映射
const algorithmMap = {
  'fuzzy': '模糊综合评判法',
  'weighted': '加权平均法',
  'topsis': 'TOPSIS法',
  'sea': '灰色SEA法',
  'grey': '灰色聚类法',
  'adc': 'ADC法',
  'index': '指数法',
  'expert': '专家打分法'
};

// 归一化算法映射
const normalizationMap = {
  'gaussian_mapping': '高斯映射',
  'cauchy_mapping': '柯西分布映射',
  'exponential_decay': '指数衰减映射',
  'logistic_variant': '逻辑斯函数变体',
  'linear_mapping': '对线性映射',
  'segment_linear': '单段线性函数',
  'zero_one_mapping': '开关函数',
  'segmentation_liner_mapping': '线性分段函数',
  'segmentation_mapping': '台阶分段函数',
  'zscore': 'Z-Score标准化',
  'decimal': '小数定标标准化'
};

// 评分方式映射
const scoringMethodMap = {
  'expert': '专家打分',
  'formula': '公式计算',
  'data': '数据采集'
};

// 根据value获取label的函数
const getLabelByValue = (value, map) => {
  return map[value] || value;
};


import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { getReportList, exportReportFile } from '@/api/ReportApi'
// 路由相关
const router = useRouter()
const goBack = () => {
  router.go(-1)
}
// 报表数据
const reportTitle = ref('空天攻防与联合火力打击')
const route = useRoute()
const systemId = ref(route.params.id || '') // 从路由参数获取analyticsId赋值给systemId
const levels = ref([])
const currentLevel = ref('一')
const tableData = ref([])
const chartTitles = {
  bar: '指标得分条形图',
  pie: '指标权重占比图',
  line: '指标趋势折线图'
}

// 计算树结构的最大层级深度
const calculateMaxDepth = (treeData) => {
  let maxDepth = 0;

  const traverse = (node, depth) => {
    maxDepth = Math.max(maxDepth, depth);
    if (node.children && node.children.length > 0) {
      node.children.forEach(child => traverse(child, depth + 1));
    }
  };

  if (Array.isArray(treeData)) {
    treeData.forEach(rootNode => traverse(rootNode, 1));
  } else {
    traverse(treeData, 1);
  }

  return maxDepth;
};

// 生成层级标签数组
const generateLevels = (maxDepth) => {
  const levelLabels = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
  return levelLabels.slice(0, maxDepth);
}

// ECharts实例
const barChart = ref(null)
const pieChart = ref(null)
const lineChart = ref(null)
// 图表类型和颜色相关变量
const chartType = ref('bar') // 'bar' 或 'line'
const customColors = ref({}) // 存储自定义颜色 {name: color}
const colorPickerVisible = ref(false)
const selectedColor = ref('#409EFF')
const selectedDataName = ref('')
const barInstance = ref(null)
const pieInstance = ref(null)
const lineInstance = ref(null)

// 处理级别变化
const handleLevelChange = () => {
  // 根据选择的级别更新图表数据
  updateChartsByLevel(currentLevel.value)
}

// 根据级别更新图表
const updateChartsByLevel = (level) => {
  // 获取当前级别的索引
  const levelIndex = levels.value.indexOf(level);
  if (levelIndex === -1) return;

  // 从表格数据中提取当前级别的数据
  const levelData = [];
  tableData.value.forEach(row => {
    row.cells.forEach((cell, index) => {
      if (index === levelIndex && !cell.hidden && cell.score !== '') {
        levelData.push({
          name: cell.label,
          value: cell.score
        });
      }
    });
  });

  // 提取名称和值
  const names = levelData.map(item => item.name);
  const values = levelData.map(item => item.value);

  // 更新图表
  updateBarChart(names, values);
  updatePieChart(levelData);
  updateLineChart(['当前阶段'], values); // 简化处理，实际应用可能需要多个阶段数据
}

// 切换图表类型
const toggleChartType = () => {
  chartType.value = chartType.value === 'bar' ? 'line' : 'bar'
  updateChartsByLevel(currentLevel.value)
}

// 更新条形图或折线图
const updateBarChart = (xAxisData, data) => {
  if (barInstance.value) {
    // 准备数据，应用自定义颜色
    const seriesData = data.map((value, index) => {
      const name = xAxisData[index]
      return {
        value,
        itemStyle: customColors.value[name] ? { color: customColors.value[name] } : null
      }
    })

    barInstance.value.setOption({
      xAxis: { data: xAxisData },
      series: [{
        data: seriesData,
        type: chartType.value,
        symbol: chartType.value === 'line' ? 'circle' : undefined,
        itemStyle: chartType.value === 'bar' ? { color: '#409EFF' } : undefined
      }]
    })

    // 绑定点击事件
    barInstance.value.off('click')
    barInstance.value.on('click', (params) => {
      selectedDataName.value = params.name
      selectedColor.value = customColors.value[params.name] || '#409EFF'
      colorPickerVisible.value = true
    })
  }
}

// 确认颜色更改
const confirmColorChange = () => {
  if (selectedDataName.value) {
    customColors.value[selectedDataName.value] = selectedColor.value
    updateChartsByLevel(currentLevel.value)
  }
  colorPickerVisible.value = false
}

// 更新饼图
const updatePieChart = (data) => {
  if (pieInstance.value) {
    // 准备数据，应用自定义颜色
    const seriesData = data.map(item => ({
      ...item,
      itemStyle: customColors.value[item.name] ? { color: customColors.value[item.name] } : null
    }))

    pieInstance.value.setOption({
      series: [{
        data: seriesData,
        itemStyle: {
          color: function(params) {
            if (customColors.value[params.data.name]) {
              return customColors.value[params.data.name]
            }
            const colorList = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
            return colorList[params.dataIndex % colorList.length]
          }
        }
      }]
    })

    // 绑定点击事件
    pieInstance.value.off('click')
    pieInstance.value.on('click', (params) => {
      selectedDataName.value = params.data.name
      selectedColor.value = customColors.value[params.data.name] || '#409EFF'
      colorPickerVisible.value = true
    })
  }
}

// 更新折线图
const updateLineChart = (xAxisData, data) => {
  if (lineInstance.value) {
    lineInstance.value.setOption({
      xAxis: { data: xAxisData },
      series: [{ data: data }]
    })
  }
}

// 初始化图表
const initCharts = () => {
  // 初始化条形图
  if (barChart.value) {
    barInstance.value = echarts.init(barChart.value)
    barInstance.value.setOption({
      title: { text: chartTitles.bar },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['侦查预警', '信息传输', '指挥控制', '行动处置', '综合打击'] },
      yAxis: { type: 'value', max: 100 },
      series: [{ data: [90, 92, 88, 95, 94], type: 'bar', itemStyle: { color: '#409EFF' } }]
    })
  }

  // 初始化饼图
  if (pieChart.value) {
    pieInstance.value = echarts.init(pieChart.value)
    pieInstance.value.setOption({
      title: { text: chartTitles.pie },
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', right: 10, top: 'center' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 30, name: '侦查预警' },
          { value: 20, name: '指挥控制' },
          { value: 15, name: '信息传输' },
          { value: 15, name: '行动效果评估' },
          { value: 20, name: '临机处置' }
        ],
        itemStyle: {
          color: function(params) {
            const colorList = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
            return colorList[params.dataIndex]
          }
        }
      }]
    })
  }

  // 初始化折线图
  if (lineChart.value) {
    lineInstance.value = echarts.init(lineChart.value)
    lineInstance.value.setOption({
      title: { text: chartTitles.line },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['阶段1', '阶段2', '阶段3', '阶段4', '阶段5', '阶段6', '阶段7'] },
      yAxis: { type: 'value', max: 100 },
      series: [{ data: [92, 93, 91, 89, 94, 95, 94], type: 'line', symbol: 'circle', itemStyle: { color: '#409EFF' } }]
    })
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (barInstance.value) barInstance.value.resize()
  if (pieInstance.value) pieInstance.value.resize()
  if (lineInstance.value) lineInstance.value.resize()
}

// 转换树形数据为表格数据
const transformTreeToTable = (treeData, results, nodeDetails) => {
  const tableData = [];
  const maxLevel = levels.value.length;
  let rowId = 1;

  // 确保maxLevel至少为1，避免数组越界
  if (maxLevel === 0) {
    return tableData;
  }

  // 递归计算子节点总数
  const getChildrenCount = (node) => {
    if (!node.children || node.children.length === 0) {
      return 1;
    }
    let count = 1; // 包括当前节点
    node.children.forEach(child => {
      count += getChildrenCount(child);
    });
    return count;
  };

  // 递归处理树形结构
  const processNode = (node, level, parentCells) => {
    const nodeId = node.id;
    const nodeResult = results[nodeId]; // 直接从对象中获取
    const nodeDetail = nodeDetails[nodeId]; // 直接从对象中获取

    // 创建当前行的单元格
    const cells = [...parentCells.map(cell => ({ ...cell, hidden: true }))];
    const currentCell = {
        label: nodeDetail ? nodeDetail.label : '',
        score: nodeResult !== undefined ? nodeResult : '',
        rowspan: 1,
        details: nodeDetail || {},
        children: node.children || [], // 添加children属性用于判断是否有子节点
        hidden: false
      };
    cells[level] = currentCell;

    // 填充剩余级别为空单元格
    for (let i = level + 1; i < maxLevel; i++) {
        cells[i] = { label: '', score: '', rowspan: 1, hidden: true };
      }

    // 计算子节点总数
    const childrenCount = node.children && node.children.length > 0 ? getChildrenCount(node) - 1 : 0;
    currentCell.rowspan = childrenCount + 1;

    // 添加当前行
    tableData.push({
      id: rowId++,
      cells
    });

    // 处理子节点
    if (node.children && node.children.length > 0) {
      node.children.forEach(child => {
        // 创建新的单元格数组副本，避免引用问题
        const newParentCells = [...cells];
        processNode(child, level + 1, newParentCells);
      });
    }
  };

  // 从根节点开始处理
  if (treeData) {
    // 检查treeData是否为数组，如果是则遍历每个元素作为根节点处理
    if (Array.isArray(treeData)) {
      treeData.forEach(rootNode => {
        processNode(rootNode, 0, []);
      });
    } else {
      // 否则直接处理单一根节点
      processNode(treeData, 0, []);
    }
  }

  return tableData;
};

// 获取报表数据
const fetchReportData = async () => {
  try {
    const response = await getReportList(systemId.value);
    reportTitle.value = response.data.system_name;

    // 假设API返回的数据结构包含tree_data, results和node_details
    const { tree_data, results, node_details } = response.data || {};

    // 转换数据并更新表格数据
    if (tree_data && results && node_details) {
      // 计算最大层级深度并更新levels
      const maxDepth = calculateMaxDepth(tree_data);
      levels.value = generateLevels(maxDepth);
      // 设置默认当前层级为第一级
      if (levels.value.length > 0) {
        currentLevel.value = levels.value[0];
      }
      
      tableData.value = transformTreeToTable(tree_data, results, node_details);
      // 初始化图表数据
      setTimeout(() => {
        initCharts()
        updateChartsByLevel(currentLevel.value);
      }, 0);
    } else {
      console.warn('API返回的数据结构不完整');
      tableData.value = [];
      levels.value = ['一', '二', '三', '四', '五']; // 默认为5级
    }
  } catch (error) {
    console.error('获取报表数据失败:', error);
    tableData.value = [];
  }
}

const exportReport = async () => {
  try {
    const response = await exportReportFile(systemId.value);
    const blob = response.data;
    
    // 从Content-Disposition头中提取文件名
    const contentDisposition = response.headers['content-disposition'];
    let filename = `评估报告_${systemId.value}.docx`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = decodeURIComponent(filenameMatch[1]);
      }
    }
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    
    // 添加导出成功提示
    ElMessage.success('报表导出成功');
  } catch (error) {
    console.error('导出报表失败:', error);
    ElMessage.error('报表导出失败');
  }
}

// 组件生命周期
onMounted(() => {
  fetchReportData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (barInstance.value) barInstance.value.dispose()
  if (pieInstance.value) pieInstance.value.dispose()
  if (lineInstance.value) lineInstance.value.dispose()
})
</script>

<style scoped>
.report-container {
  padding: 20px;
  color: #333;
  height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scroll-container::-webkit-scrollbar {
  display: none;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.report-section {
  margin-bottom: 40px;
}

.hierarchy-table {
  margin-bottom: 20px;
}

.hierarchy-table table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.hierarchy-table td, .hierarchy-table th {
  word-break: break-word;
  vertical-align: middle;
}

.cell-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  height: 100%;
}

.hierarchy-table th,
.hierarchy-table td {
  padding: 12px 15px;
  border: 1px solid #eee;
  text-align: left;
}

.hierarchy-table th {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #1f2d3d;
}

.hierarchy-table .has-score {
  background-color: #f0f7ff;
}

.score {
  color: #409eff;
  margin-top: 5px;
  font-size: 14px;
}

.method-info {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid #e4e7ed;
}

.method-info div {
  margin-bottom: 3px;
}

.custom-select {
  width: 160px;
  margin-bottom: 15px;
}

.details-content div {
  margin-bottom: 5px;
}

.charts-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.chart-item {
  flex: 1 1 calc(33.333% - 20px);
  min-width: 300px;
  background-color: #fff;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.chart {
  width: 100%;
  height: 300px;
  margin-top: 15px;
}
</style>