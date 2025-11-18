<template>
  <div class="workflow-container">
    <!-- Left Sidebar - Tree Structure -->
    <div class="left-sidebar">
      <div class="sidebar-header">
        <h3>指标管理</h3>
        <div class="header-actions">
          <el-button size="small" @click="togoBack">
            返回
          </el-button>
          <el-button size="small" @click="refreshBaseMetrics">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
      
      <div class="metrics-container">
        <!-- 基础指标 -->
        <div class="metric-section">
          <div class="section-header">
            <span class="section-title">基础指标</span>
            <el-input style="width: 200px;" v-model="basicTreeName" placeholder="搜索基础指标"></el-input>
            <el-button size="small" @click="basicTreeDataSearch" :loading="loadingBaseMetrics">
              <el-icon><Search /></el-icon>
            </el-button>
          </div>
          <el-tree
            ref="baseTreeRef"
            :data="baseMetricsData"
            :props="treeProps"
            node-key="id"
            class="tree-container"
            :expand-on-click-node="false"
            v-loading="loadingBaseMetrics"
            default-expand-all
          >
            <template #default="{ node, data }">
              <div 
                class="tree-node"
                draggable="true"
              >
                <span class="node-label">{{ data.label }}</span>
                <div class="node-type-badge">基础</div>
              </div>
            </template>
          </el-tree>
        </div>
        
        <!-- 自定义指标 -->
        <div class="metric-section">
          <div class="section-header">
            <span class="section-title">自定义指标</span>
            <el-button size="small" @click="showAddCustomDialog = true">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
          <el-tree
            ref="customTreeRef"
            :data="customMetricsData"
            :props="treeProps"
            node-key="id"
            class="tree-container"
            :expand-on-click-node="false"
            default-expand-all
          >
            <template #default="{ node, data }">
              <div 
                class="tree-node"
                draggable="true"
              >
                <span class="node-label">{{ data.label }}</span>
                <div class="node-actions">
                  <el-button size="small" text @click.stop="addChildCustomMetricDialog(data)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button size="small" text @click.stop="editCustomMetric(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button 
                    size="small" 
                    text 
                    :disabled="hasChildren(data)"
                    @click.stop="deleteCustomMetric(data)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <div class="node-type-badge custom">自定义</div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>
    </div>

    <!-- Center Area - Flowchart -->
    <div 
      class="center-area"
      :class="{ 'drag-over': isDragOver }"
      @drop="handleDrop" 
      @dragover="handleDragOver"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
    >
      <div class="flowchart-header">
        <div class="zoom-controls">
          <el-button size="small" @click="zoomOut">
            <span>-</span>
          </el-button>
          <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
          <el-button size="small" @click="zoomIn">
            <span>+</span>
          </el-button>
          <el-button size="small" @click="resetZoom">重置</el-button>
        </div>
        <div class="header-actions">

          <el-select v-model="selectedWorkflowType" placeholder="请选择推演数据集合" style="width: 150px; margin-right: 10px;">
            <el-option v-for="item in selectedWorkflowOption" :label="item.label" :value="item.value" :key="item.value"/>
          </el-select>
          <el-button size="small" @click="clearGraph">清空</el-button>
          <el-button size="small" @click="saveWorkflow" :loading="savingWorkflow">保存工作流</el-button>
          <el-button size="small" @click="toggleSnapToGrid" :type="snapToGrid ? 'primary' : 'default'">
            {{ snapToGrid ? '关闭吸附' : '开启吸附' }}
          </el-button>
        </div>
      </div>
      
      <!-- Canvas Area with zoom and pan -->
      <div 
        class="canvas-wrapper"
        ref="canvasWrapper"
        @wheel="handleWheel"
        @mousedown="handleCanvasMouseDown"
      >
        <div 
          class="canvas-container"
          ref="canvasContainer"
          :style="{
            transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
            transformOrigin: '0 0'
          }"
          @click="handleCanvasClick"
        >
          <!-- Snap guides -->
          <div v-if="snapGuides.vertical !== null" class="snap-guide vertical" :style="{ left: snapGuides.vertical + 'px' }"></div>
          <div v-if="snapGuides.horizontal !== null" class="snap-guide horizontal" :style="{ top: snapGuides.horizontal + 'px' }"></div>
          
          <!-- Nodes -->
          <div
            v-for="node in graphData.nodes"
            :key="node.id"
            class="flow-node"
            :class="{
              'selected': selectedNode && selectedNode.id === node.id,
              'connecting': isConnecting && connectionStart && connectionStart.id === node.id,
              'connectable': isConnecting && (!connectionStart || connectionStart.id !== node.id),
              'has-parent': hasParentNode(node.id),
              'connection-invalid': isConnecting && !canConnectTo(node.id),
              'base-metric': node.metricType === 'base',
              'custom-metric': node.metricType === 'custom'
            }"
            :style="{
              left: node.x + 'px',
              top: node.y + 'px'
            }"
            @mousedown="startDrag($event, node)"
            @click="selectNode(node)"
            @contextmenu="showNodeContextMenu($event, node)"
          >
            <div class="node-content">
              <div class="node-title">{{ node.label }}</div>
              <div class="metric-type-indicator" :class="node.metricType">
                {{ node.metricType === 'base' ? '基础' : '自定义' }}
              </div>
            </div>
            <div class="node-handles">
              <div 
                class="handle handle-left"
                :class="{
                  'active': isConnecting && connectionStart && connectionStart.id === node.id,
                  'disabled': isConnecting && !canConnectTo(node.id)
                }"
                @click.stop="startConnection($event, node, 'input')"
                :title="hasParentNode(node.id) ? '该节点已有父节点' : '连接到此节点'"
              ></div>
              <div 
                class="handle handle-right"
                :class="{ 'active': isConnecting && connectionStart && connectionStart.id === node.id }"
                @click.stop="startConnection($event, node, 'output')"
                title="从此节点开始连接"
              ></div>
            </div>
          </div>

          <!-- Edges -->
          <svg class="edges-layer" :style="{ width: '100%', height: '100%' }">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#40a9ff" />
              </marker>
              <marker
                id="arrowhead-selected"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#ff4d4f" />
              </marker>
            </defs>
            
            <!-- Regular edges -->
            <path
              v-for="edge in graphData.edges"
              :key="edge.id"
              :d="getEdgePath(edge)"
              :stroke="selectedEdge && selectedEdge.id === edge.id ? '#ff4d4f' : '#40a9ff'"
              :stroke-width="selectedEdge && selectedEdge.id === edge.id ? 3 : 2"
              fill="none"

              class="edge-path"
              @click="selectEdge(edge, $event)"
              @contextmenu="showEdgeContextMenu($event, edge)"
            />
            
            <!-- Invisible wider paths for easier clicking -->
            <path
              v-for="edge in graphData.edges"
              :key="'click-' + edge.id"
              :d="getEdgePath(edge)"
              stroke="transparent"
              stroke-width="12"
              fill="none"
              class="edge-click-area"
              @click="selectEdge(edge, $event)"
              @contextmenu="showEdgeContextMenu($event, edge)"
            />
            
            <!-- Temporary edge while connecting -->
            <path
              v-if="tempEdge"
              :d="tempEdge.path"
              :stroke="tempEdge.valid ? '#40a9ff' : '#ff4d4f'"
              stroke-width="2"
              :stroke-dasharray="tempEdge.valid ? '5,5' : '10,5'"
              fill="none"

            />
          </svg>
        </div>
      </div>
      
      <!-- Instructions -->
      <div v-if="!graphData.nodes.length && !isDragOver" class="instructions">
        <div class="instruction-content">
          <h4>使用说明：</h4>
          <ul>
            <li>从左侧拖拽指标到画布创建流程图</li>
            <li>基础指标从接口获取，自定义指标可以增删改</li>
            <li>拖拽节点可以移动位置</li>
            <li>点击节点右侧圆点开始连线</li>
            <li><strong>每个子节点只能有一个父节点</strong></li>
            <li><strong>每个父节点可以有多个子节点</strong></li>
            <li>点击连线可以选中并删除</li>
            <li>点击节点查看和编辑属性</li>
            <li>保存属性会存储到本地，保存工作流会发送到后端</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Right Sidebar - Properties -->
    <el-drawer
      v-model="showProperties"
      :title="selectedEdge ? '连线属性' : '节点属性'"
      direction="rtl"
      size="800px"
      class="properties-drawer"
    >
      <!-- Node Properties -->
      <div v-if="selectedNode && !selectedEdge" class="properties-content">
        <el-form 
          :model="nodeForm" 
          label-width="100px" 
          label-position="left"
          :rules="nodeFormRules"
          ref="nodeFormRef" 
          >
          <el-form-item label="节点名称" prop="label">
            <el-input v-model="nodeForm.label" placeholder="请输入节点名称" />
          </el-form-item>
          
          <el-form-item label="描述信息" prop="description">
            <el-input
              v-model="nodeForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入节点描述信息"
            />
          </el-form-item>
          
          <!-- <el-form-item label="自定义权重" v-if="nodeAnalysisMethod !== 'ahp'">
            <el-input-number v-model="customWeight" :min="0" :max="100" :step="1" placeholder="请输入权重占比(%)" />
          </el-form-item> -->
          <el-form-item label="权重分析方法">
            <el-select v-model="nodeAnalysisMethod" placeholder="请选择分析方法" style="width: 180px; margin-right: 10px;">
              <el-option label="AHP层次分析法" value="ahp"></el-option>
              <el-option label="变异系数法" value="CoefficientMethod"></el-option>
              <el-option label="熵权法" value="EntropyWeight"></el-option>
              <el-option label="直接赋权法" value="directEmpowerment"></el-option>
              <el-option label="灰色关联分析法" value="GreyRelationalAnalysis"></el-option>
              <el-option label="环比系数法" value="DareMethod"></el-option>
              <el-option label="因子分析法" value="FactorAnalysis"></el-option>
              <el-option label="主成分分析法" value="PcaWeight"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="权重分析">
            <el-button @click="openWeightAllocation" :disabled="getChildNodes(selectedNode.id).length === 0">
              权重分析
            </el-button>
            <span v-if="getChildNodes(selectedNode.id).length === 0" class="text-gray-400 ml-2">
              (无子节点)
            </span>
          </el-form-item>

          <el-form-item label="指标算法" v-if="getChildNodes(selectedNode.id).length > 0">
            <div class="algorithm-section" style="display: flex; align-items: center;">
              <el-select v-model="selectedAlgorithm" placeholder="请选择指标算法" style="width: 200px; margin-right: 10px;">
                <el-option label="模糊综合评判法" value="fuzzy"></el-option>
                <el-option label="加权平均法" value="weighted"></el-option>
                <!-- <el-option label="TOPSIS法" value="topsis"></el-option> -->
                <!-- <el-option label="SEA法" value="sea"></el-option> -->
                <el-option label="灰色白化权聚类法" value="grey"></el-option>
                <!-- <el-option label="ADC法" value="adc"></el-option> -->
                <el-option label="指数法" value="index"></el-option>
                <el-option label="专家打分法" value="expert"></el-option>
              </el-select>
              <el-button
                v-if="selectedAlgorithm === 'fuzzy'"
                @click="initFuzzyMatrix()"
                class="ml-2"
              >
                参数配置
              </el-button>
              <el-button
                v-if="selectedAlgorithm === 'grey'"
                @click="initGreyClusteringData(); showGreyClusteringDialog = true"
                class="ml-2"
              >
                参数配置
              </el-button>
            </div>
          </el-form-item>

          <!-- Grey Clustering Configuration Dialog -->
          <el-dialog v-model="showGreyClusteringDialog" title="灰色白化权聚类法配置" width="800px">
            <div class="grey-clustering-container">
              <div class="score-segments-section mt-4">
                <p style="color: #fff;">第一行输入0-100递增数值:</p>
                <el-table :data="[greyClusteringSegments]" border style="width: 100%; overflow: auto;">
                  <el-table-column min-width="100px" label="分数分段"></el-table-column>
                  <el-table-column min-width="120px" v-for="index in greyClusteringSegments.length" :key="index" :label="'分段 ' + (index)">
                    <template #default="scope">
                      <el-input
                        v-model="greyClusteringSegments[index-1]"
                        type="number"
                        :min="0"
                        :max="100"
                        @change="handleGreySegmentChange(index-1)"
                      ></el-input>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" min-width="180px">
                    <template #default>
                      <el-button type="primary" size="small" @click="addGreyClusteringColumn">
                        新增列
                      </el-button>
                      <el-button type="danger" size="small" @click="deleteGreyClusteringColumn">
                        删除列
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div class="data-table-container mt-6">
                <p style="color: #fff;">子节点范围配置:</p>
                <el-table :data="greyClusteringData" border style="width: 100%">
                  <el-table-column prop="nodeName" label="子节点名称" min-width="120"></el-table-column>
                  <el-table-column v-for="(segment, index) in greyClusteringSegments.length + 1" :key="index" :label="'范围 ' + (index + 1)">
                    <template #default="scope">
                      <el-input
                        v-model="scope.row.ranges[index]"
                        placeholder="例如: [0, 10, 20]"
                        @change="handleGreyRangeChange(scope.row, index)"
                      ></el-input>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
            <template #footer>
              <el-button @click="showGreyClusteringDialog = false">取消</el-button>
              <el-button type="primary" @click="saveGreyClusteringConfig">保存配置</el-button>
            </template>
          </el-dialog>

          <!-- Fuzzy Comprehensive Evaluation Matrix Dialog -->
          <el-dialog v-model="showFuzzyMatrixDialog" title="模糊综合评判矩阵配置" width="800px">
            <div class="table-container">
              <table class="parameter_table">
                <thead>
                  <tr>
                    <th style="min-width: 100px;">分数分段</th>
                    <th v-for="(segment, index) in scoreSegments" :key="'header-' + index">
                      {{ segment }}分
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in fuzzyMatrixData" :key="'row-' + rowIndex">
                    <td>{{ row.nodeName }}</td>
                    <td v-for="(value, colIndex) in row.values" :key="'cell-' + rowIndex + '-' + colIndex">
                      <el-input
                        v-model="row.values[colIndex]"
                        type="number"
                        style="width: 100px"
                        :min="0"
                        :max="100"
                        @change="handleMatrixValueChange(rowIndex, colIndex)"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="score-segments-section mt-4">
              <p style="color: #fff;">分数分段配置:</p>
              <el-table :data="[scoreSegments]" border style="width: 100%; overflow: auto;">
                <el-table-column min-width="100px" label="分数分段"></el-table-column>
                <el-table-column min-width="120px" v-for="index in scoreSegments.length" :key="index" :label="'分段 ' + (index)">
                  <template #default="scope">
                    <el-input
                      v-model="scoreSegments[index-1]"
                      :min="0"
                      :max="100"
                      @change="handleScoreSegmentChange(index-1)"
                    ></el-input>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="180px">
                  <template #default>
                    <el-button type="primary" size="small" @click="addMatrixColumn">
                      新增列
                    </el-button>
                    <el-button type="danger" size="small" @click="delMatrixColumn">
                      删除列
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <template #footer>
              <el-button @click="showFuzzyMatrixDialog = false">取消</el-button>
              <el-button type="primary" @click="saveFuzzyMatrixConfig">保存配置</el-button>
            </template>
          </el-dialog>

          <el-form-item label="评分方式" v-if="getChildNodes(selectedNode.id).length === 0">
            <el-radio-group v-model="scoringMethod">
              <el-radio style="color: #fff;" label="expert">专家打分</el-radio>
              <el-radio style="color: #fff;" label="formula">公式计算</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <!-- Expert Scoring -->
          <el-form-item v-if="selectedAlgorithm === 'expert' || (getChildNodes(selectedNode.id).length === 0 && scoringMethod === 'expert')" label="专家评分">
            <el-input-number
              v-model="expertScore"
              :min="0"
              :max="100"
              style="width: 100%"
              placeholder="请输入0-100分"
            />
          </el-form-item>
          
          <!-- Formula Calculation -->
          <div v-if="scoringMethod.includes('formula')" class="formula-section">
            <el-form-item label="算法公式">
              <el-input v-model="nodeForm.formula" placeholder="例如：1-(P1-P3)/(P2-P3)"/>
            </el-form-item>
            
            <el-form-item label="参数列表">
              <div class="parameter-table">
                <el-table :data="parameterList" border style="width: 100%">
                  <el-table-column type="index" label="序号" width="60" />
                  <el-table-column prop="name" label="参数名称" />
                  <el-table-column prop="alias" label="参数别名" />
                  <el-table-column label="操作" align="center" min-width="180">
                    <template #default="scope">
                      <el-button size="small" @click="bindDataSource(scope.row)">数据源绑定</el-button>
                      <el-button size="small" type="danger" @click="deleteParameter(scope.row.id)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
                <el-button type="primary" size="small" @click="showAddParameterDialog = true" class="mt-2">
                  新增参数
                </el-button>
              </div>
            </el-form-item>
          </div>
          
          <el-form-item label="归一化算法" v-if="getChildNodes(selectedNode.id).length === 0">
            <div class="normalization-section">
              <el-select v-model="normalizationAlgorithm" placeholder="请选择归一化算法" style="width: 200px" @change="resetNormalizationParams">
                <el-option label="高斯函数映射" value="gaussian_mapping" type="minmax"/>
                <el-option label="柯西分布映射" value="cauchy_mapping" type="minmax"/>
                <el-option label="指数衰减函数" value="exponential_decay" type="minmax"/>
                <el-option label="辑斯蒂函数变体" value="logistic_variant" type="minmax"/>
                <el-option label="对称线性函数" value="linear_segment" type="linear_segment"/>
                <el-option label="单段线性函数" value="linear_mapping" type="linear_mapping"/>
                <el-option label="开关函数" value="zero_one_mapping" type="zero_one_mapping"/>
                <el-option label="线性分段函数" value="segmentation_liner_mapping" type="segmentation_liner_mapping"/>
                <el-option label="台阶分段函数" value="segmentation_mapping" type="segmentation_mapping"/>
              </el-select>
              <el-button @click="showParameterConfigDialog = true" class="ml-2">参数配置</el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="指标类型">
            <el-input :value="nodeForm.metricType === 'base' ? '基础指标' : '自定义指标'" disabled />
          </el-form-item>
          
          <!-- <el-form-item label="节点编码">
            <el-input v-model="nodeForm.code" placeholder="请输入节点编码" />
          </el-form-item>
          
          <el-form-item label="坐标位置">
            <div class="coordinate-inputs">
              <el-input-number
                v-model="nodeForm.x"
                :min="0"
                style="width: 48%"
                placeholder="X坐标"
                @change="updateNodePosition"
              />
              <el-input-number
                v-model="nodeForm.y"
                :min="0"
                style="width: 48%; margin-left: 4%"
                placeholder="Y坐标"
                @change="updateNodePosition"
              />
            </div>
          </el-form-item> -->
          
          <el-form-item label="创建时间">
            <el-input :value="formatDate(nodeForm.createTime)" disabled />
          </el-form-item>
          
          <el-form-item label="更新时间">
            <el-input :value="formatDate(nodeForm.updateTime)" disabled />
          </el-form-item>
        </el-form>
        
        <div class="form-actions">
          <el-button type="primary" @click="saveNodeProperties">保存属性</el-button>
          <el-button @click="showProperties = false">取消</el-button>
        </div>
      </div>

      <!-- Edge Properties -->
      <!-- <div v-if="selectedEdge" class="properties-content">
        <el-form :model="edgeForm" label-width="100px" label-position="left">
          <el-form-item label="连线名称">
            <el-input v-model="edgeForm.label" placeholder="请输入连线名称" />
          </el-form-item>
          <el-form-item label="连线类型">
            <el-select v-model="edgeForm.type" placeholder="请选择连线类型" style="width: 100%">
              <el-option label="数据流" value="dataflow" />
              <el-option label="控制流" value="controlflow" />
              <el-option label="依赖关系" value="dependency" />
            </el-select>
          </el-form-item>
          <el-form-item label="描述信息">
            <el-input
              v-model="edgeForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入连线描述信息"
            />
          </el-form-item>
          <el-form-item label="源节点">
            <el-input :value="getNodeLabel(edgeForm.source)" disabled />
          </el-form-item>
          <el-form-item label="目标节点">
            <el-input :value="getNodeLabel(edgeForm.target)" disabled />
          </el-form-item>
          <el-form-item label="创建时间">
            <el-input :value="formatDate(edgeForm.createTime)" disabled />
          </el-form-item>
          <el-form-item label="更新时间">
            <el-input :value="formatDate(edgeForm.updateTime)" disabled />
          </el-form-item>
        </el-form>
        
        <div class="form-actions">
          <el-button type="primary" @click="saveEdgeProperties">保存属性</el-button>
          <el-button type="danger" @click="deleteSelectedEdge">删除连线</el-button>
          <el-button @click="showProperties = false">取消</el-button>
        </div>
      </div> -->
    </el-drawer>

    <!-- Add Custom Metric Dialog -->
    <el-dialog v-model="showAddCustomDialog" title="添加自定义指标" width="400px">
      <el-form :model="customMetricForm" label-width="80px">
        <el-form-item label="指标名称" required>
          <el-input v-model="customMetricForm.label" placeholder="请输入指标名称" />
        </el-form-item>
        <el-form-item label="描述信息">
          <el-input
            v-model="customMetricForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入指标描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCustomDialog = false">取消</el-button>
        <el-button type="primary" @click="addCustomMetric">确定</el-button>
      </template>
    </el-dialog>

    <!-- Edit Custom Metric Dialog -->
    <el-dialog v-model="showEditCustomDialog" title="编辑自定义指标" width="400px">
      <el-form :model="editCustomMetricForm" label-width="80px">
        <el-form-item label="指标名称" required>
          <el-input v-model="editCustomMetricForm.label" placeholder="请输入指标名称" />
        </el-form-item>
        <el-form-item label="描述信息">
          <el-input
            v-model="editCustomMetricForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入指标描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCustomDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEditCustomMetric">确定</el-button>
      </template>
    </el-dialog>

    <!-- Add Child Custom Metric Dialog -->
    <el-dialog v-model="showAddChildCustomDialog" title="添加子指标" width="400px">
      <el-form :model="childCustomMetricForm" label-width="80px">
        <el-form-item label="父指标">
          <el-input :value="parentCustomMetric?.label" disabled />
        </el-form-item>
        <el-form-item label="指标名称" required>
          <el-input v-model="childCustomMetricForm.label" placeholder="请输入子指标名称" />
        </el-form-item>
        <el-form-item label="描述信息">
          <el-input
            v-model="childCustomMetricForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入指标描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddChildCustomDialog = false">取消</el-button>
        <el-button type="primary" @click="addChildCustomMetricAction">确定</el-button>
      </template>
    </el-dialog>

    <!-- Context Menu -->
    <div
      v-if="contextMenu.show"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <div v-if="contextMenu.type === 'node'" class="menu-item" @click="deleteSelectedNode">删除节点</div>
      <div v-if="contextMenu.type === 'node'" class="menu-item" @click="duplicateNode">复制节点</div>
      <div v-if="contextMenu.type === 'edge'" class="menu-item" @click="deleteContextEdge">删除连线</div>
      <div v-if="contextMenu.type === 'edge'" class="menu-item" @click="editContextEdge">编辑连线</div>
    </div>

    <!-- Connection Warning Dialog -->
    <el-dialog v-model="showConnectionWarning" title="连接冲突" width="400px">
      <div class="warning-content">
        <p>目标节点 <strong>{{ connectionWarning.targetLabel }}</strong> 已经有父节点：</p>
        <p><strong>{{ connectionWarning.existingParentLabel }}</strong></p>
        <p>每个节点只能有一个父节点。您希望如何处理？</p>
      </div>
      <template #footer>
        <el-button @click="showConnectionWarning = false">取消</el-button>
        <el-button type="warning" @click="replaceParentConnection">替换父节点</el-button>
      </template>
    </el-dialog>

    <!-- Weight Allocation Dialog -->
    <el-dialog v-model="showWeightAllocationDialog" title="权重分析" width="800px">
      <div class="weight-allocation-content">
        <template v-if="nodeAnalysisMethod === 'ahp'">
          <div class="scale-meaning-box">
            <div class="scale-title">标度含义说明</div>
            <div class="scale-items">
              <div class="scale-item"><span class="scale-number">1</span><span class="scale-desc">因素A(行)与B(列)相比，具有同等重要性</span></div>
              <div class="scale-item"><span class="scale-number">3</span><span class="scale-desc">因素A(行)与B(列)相比，A比B稍微重要</span></div>
              <div class="scale-item"><span class="scale-number">5</span><span class="scale-desc">因素A(行)与B(列)相比，A比B明显重要</span></div>
              <div class="scale-item"><span class="scale-number">7</span><span class="scale-desc">因素A(行)与B(列)相比，A比B强烈重要</span></div>
              <div class="scale-item"><span class="scale-number">9</span><span class="scale-desc">因素A(行)与B(列)相比，A比B极端重要</span></div>
            </div>
            <div class="scale-note">
              <p><strong>注:</strong> 标度2，4，6，8分别表示A与B相比，其重要性分别在1~3，3~5，5~7，7-9之间</p>
              <p><strong>重要提示:</strong> 禁止出现A比B重要，B比C重要，C比A重要的逻辑矛盾</p>
            </div>
          </div>
          <p class="mb-4" style="color: #fff;">AHP层次分析法判断矩阵</p>
          <el-table :data="ahpMatrix" border style="width: 100%">
            <el-table-column width="120">
              <template #header>
                <span>子节点</span>
              </template>
              <template #default="{ $index }">
                {{ getChildNodes(selectedNode?.id)[$index]?.label || '' }}
              </template>
            </el-table-column>
            <el-table-column v-for="(child, colIndex) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
              <template #default="{ row, $index }">
                <el-input v-model="row[colIndex]" size="small" :disabled="$index === colIndex" @change="handleMatrixInput($index, colIndex, row[colIndex])" type="text" />
              </template>
            </el-table-column>
          </el-table>

          <!-- AHP权重计算结果 -->
          <div class="mt-4">
            <p class="mb-2" style="color: #fff;">权重计算结果</p>
            <el-table :data="ahpWeights" border style="width: 100%">
              <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
              <el-table-column prop="weight" label="权重占比">
                <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
              </el-table-column>
            </el-table>
          </div>

          <div style="margin-top: 10px;" class="mt-4 text-center">
            <el-button type="primary" @click="calculateAhpWeights" :loading="calculatingWeights">
              计算权重
            </el-button>
          </div>
        </template>
        <template v-else-if="nodeAnalysisMethod === 'EntropyWeight' || nodeAnalysisMethod === 'CoefficientMethod'">
          <div class="score-segments-section mt-4">
            <el-button size="small" @click="addMethodMatrixColumn" style="margin-bottom: 10px;">新增列</el-button>
            <el-button size="small" @click="delMethodMatrixColumn" type="danger" style="margin-bottom: 10px;">删除列</el-button>
            <el-table :data="methodMatrixData" border style="width: 100%">
              <el-table-column prop="name" label="子节点名称" min-width="120"></el-table-column>
              <el-table-column min-width="100px" v-for="(segment, index) in methodMatrixData[0]?.row_list || []" :key="index" :label="'第' + (index + 1) + '段'">
                <template #default="scope">
                  <el-input
                    v-model="scope.row.row_list[index]"
                    @change="handleMatrixChange(scope.row, index)"
                  ></el-input>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 权重计算结果 -->
          <div class="mt-4">
            <p class="mb-2" style="color: #fff;">权重计算结果</p>
            <el-table :data="methodWeights" border style="width: 100%">
              <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
              <el-table-column prop="weight" label="权重占比">
                <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
              </el-table-column>
            </el-table>
          </div>

          <div class="mt-4 text-center">
            <el-button type="primary" @click="calculateMethodWeights" :loading="calculatingWeights">
              计算权重
            </el-button>
          </div>
        </template>
        <template v-else-if="nodeAnalysisMethod === 'GreyRelationalAnalysis'">
          <div class="grey-relational-container">
            <h4 style="color: #fff;" class="grey-relational-title">灰色关联分析法配置</h4>
            <!-- 分辨系数配置 -->
            <div class="rho-config mt-4">
              <el-form-item style="color: #fff;" label="分辨系数 rho (0-1)">
                <el-slider
                  v-model="greyRelationalData.rho"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  show-input
                />
              </el-form-item>
            </div>

            <!-- 子节点类型配置 -->
            <div class="index-types-config mt-4">
              <h5 style="color: #fff;">子节点类型配置</h5>
              <div v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" class="index-type-item">
                <span style="color: #fff;" class="child-name">{{ child.label }}</span>
                <el-radio-group v-model="greyRelationalData.index_types[index]">
                  <el-radio style="color: #fff;" :label="'positive'">越大越好</el-radio>
                  <el-radio style="color: #fff;" :label="'negative'">越小越好</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 数据表格 -->
            <div class="data-table-container mt-4">
              <el-button size="small" @click="addGreyDataRow" style="margin-bottom: 10px;">新增行</el-button>
              <el-button size="small" @click="deleteGreyDataRow" type="danger" style="margin-bottom: 10px;">删除行</el-button>
              <el-table :data="greyRelationalData.data_list" border style="width: 100%">
                <el-table-column v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
                  <template #default="scope">
                    <el-input
                      v-model="greyRelationalData.data_list[scope.$index][index]"
                      type="number"
                      :min="0"
                      :max="100"
                      @change="handleGreyDataChange(scope.$index, index, $event)"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="greyRelationalWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>

            <div class="mt-4 text-center">
              <el-button type="primary" @click="calculateGreyRelationalWeights" :loading="calculatingWeights">
                计算权重
              </el-button>
            </div>
          </div>
        </template>
        <template v-else-if="nodeAnalysisMethod === 'DareMethod'">
          <div class="dare-method-container">
            <h4 style="color: #fff;" class="dare-method-title">环比系数法配置</h4>
            
            <!-- 环比系数输入 -->
            <div class="dare-coefficients mt-4">
              <p style="color: #fff;" class="mb-2">请输入环比系数（大于等于0）</p>
              <div v-for="(pair, index) in dareCoefficientPairs" :key="index" class="dare-coefficient-item">
                <span style="color: #fff;" class="pair-description">{{ pair }} 的重要程度：</span>
                <el-input
                  v-model="dareCoefficients[index]"
                  type="number"
                  :min="0"
                  step="0.01"
                  precision="2"
                  style="width: 150px; margin-left: 10px;"
                  @change="handleDareCoefficientInput(index)"
                />
              </div>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="dareWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>

            <div class="mt-4 text-center">
              <el-button type="primary" @click="calculateDareWeights" :loading="calculatingWeights">
                计算权重
              </el-button>
            </div>
          </div>
        </template>
        <template v-else-if="nodeAnalysisMethod === 'FactorAnalysis'">
          <div class="factor-analysis-container">
            <h4 style="color: #fff;" class="factor-analysis-title">因子分析法配置</h4>

            <!-- 数据表格 -->
            <div class="data-table-container mt-4">
              <el-button size="small" @click="addFactorDataRow('FactorAnalysis')" style="margin-bottom: 10px;">新增行</el-button>
              <el-button size="small" @click="deleteFactorDataRow('FactorAnalysis')" type="danger" style="margin-bottom: 10px;">删除行</el-button>
              <el-table :data="factorData.data_list" border style="width: 100%">
                <el-table-column v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
                  <template #default="scope">
                    <el-input
                      v-model="factorData.data_list[scope.$index][index]"
                      type="number"
                      :min="0"
                      @change="handleFactorDataChange('FactorAnalysis', scope.$index, index, $event)"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="factorWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>

            <div class="mt-4 text-center">
              <el-button type="primary" @click="calculateFactorWeights()" :loading="calculatingWeights">
                计算权重
              </el-button>
            </div>
          </div>
        </template>
        <template v-else-if="nodeAnalysisMethod === 'PcaWeight'">
          <div class="factor-analysis-container">
            <h4 style="color: #fff;" class="factor-analysis-title">主成分分析法配置</h4>

            <!-- 数据表格 -->
            <div class="data-table-container mt-4">
              <el-button size="small" @click="addFactorDataRow('PcaWeight')" style="margin-bottom: 10px;">新增行</el-button>
              <el-button size="small" @click="deleteFactorDataRow('PcaWeight')" type="danger" style="margin-bottom: 10px;">删除行</el-button>
              <el-table :data="pcaData.data_list" border style="width: 100%">
                <el-table-column v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
                  <template #default="scope">
                    <el-input
                      v-model="pcaData.data_list[scope.$index][index]"
                      type="number"
                      :min="0"
                      @change="handleFactorDataChange('PcaWeight', scope.$index, index, $event)"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="pcaWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>

            <div class="mt-4 text-center">
              <el-button type="primary" @click="calculatePcaWeights()" :loading="calculatingWeights">
                计算权重
              </el-button>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="direct-weight-container">
            <h4 class="direct-weight-title">为子节点分配权重（总和应为100%）</h4>
            <div class="direct-weight-list">
              <div v-for="child in getChildNodes(selectedNode?.id)" :key="child.id" class="direct-weight-item">
                <span class="child-name">{{ child.label }}</span>
                <div class="weight-input-group">
                  <el-input-number
                    v-model="percentageWeights[child.id]"
                    :min="0"
                    :max="100"
                    :precision="1"
                    style="width: 120px"
                    @change="(value) => { percentageWeights[child.id] = value; childWeights[child.id] = value / 100 }"
                  />
                  <span class="percent-sign">%</span>
                </div>
              </div>
            </div>
            <div class="weight-total mt-4">
              <strong>总计: {{ calculateTotalWeight() }}%</strong>
            </div>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="showWeightAllocationDialog = false">取消</el-button>
        <el-button type="primary" @click="saveWeightAllocation">确定</el-button>
      </template>
    </el-dialog>

    <!-- Add Parameter Dialog -->
    <el-dialog v-model="showAddParameterDialog" title="新增参数" width="400px">
      <el-form :model="newParameter" label-width="80px">
        <el-form-item label="参数名称" required>
          <el-input v-model="newParameter.name" placeholder="请输入参数名称" />
        </el-form-item>
        <el-form-item label="参数别名" required>
          <el-input v-model="newParameter.alias" placeholder="请输入参数别名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddParameterDialog = false">取消</el-button>
        <el-button type="primary" @click="addParameter">确定</el-button>
      </template>
    </el-dialog>

    <!-- Parameter Configuration Dialog -->
    <el-dialog v-model="showParameterConfigDialog" title="参数配置" width="600px">
      <div class="parameter-config-content">
        <el-form label-width="120px">
          <el-form-item v-if="currentAlgorithmType === 'minmax'" label="期望值 (μ)">
            <el-input-number v-model="normalizationParams.mu" :precision="2" :step="0.1" style="width: 100%" @change="checkParam('mu', 0, 1, '期望值应在 0-1 之间')"/>
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'minmax'" label="系数 (k)">
            <el-input-number v-model="normalizationParams.k" :precision="2" :step="0.1" style="width: 100%" @change="checkParam('k', 0, 100, '系数应在 0-100 之间')"/>
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'zscore'" label="均值">
            <el-input-number v-model="normalizationParams.mean" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'zscore'" label="标准差">
            <el-input-number v-model="normalizationParams.std" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'decimal'" label="小数位数">
            <el-input-number v-model="normalizationParams.decimal" :min="1" :max="10" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'linear_segment'" label="满分点 (μ)">
            <el-input-number v-model="normalizationParams.mu" :precision="2" :step="0.1" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'linear_segment'" label="单边有效范围 (d)">
            <el-input-number v-model="normalizationParams.d" :precision="2" :step="0.1" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'linear_mapping'" label="最小值 (x_min)">
            <el-input-number v-model="normalizationParams.x_min" :precision="2" :step="0.1" style="width: 100%" @change="checkParam('x_min', 0, 100, '参数应在 0-100 之间')"/>
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'linear_mapping'" label="最大值 (x_max)">
            <el-input-number v-model="normalizationParams.x_max" :precision="2" :step="0.1" style="width: 100%" @change="checkParam('x_max', 0, 100, '参数应在 0-100 之间')"/>
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'linear_mapping' || currentAlgorithmType === 'zero_one_mapping'" label="增减性">
            <el-select v-model="normalizationParams.upDown" placeholder="请选择增减性" style="width: 100%">
              <el-option label="增" value="1" />
              <el-option label="减" value="-1" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="currentAlgorithmType === 'zero_one_mapping'" label="关键点 (μ)">
            <el-input-number v-model="normalizationParams.mu" :precision="2" :step="0.1" :min="0" style="width: 100%" @change="checkParam('mu', 0, 100, '参数应在 0-100 之间')"/>
          </el-form-item>
          <template v-if="currentAlgorithmType === 'segmentation_liner_mapping' || currentAlgorithmType === 'segmentation_mapping'">
              <div class="table-container">
                <table class="parameter_table">
                  <thead>
                    <tr>
                      <th style="min-width: 100px;">x_list(指标值)
                        y_list(得分值)</th>
                      <th v-for="(x, index) in normalizationParams.x_list" :key="'header-' + index">
                        列 {{ index + 1 }}
                        <el-button
                          type="danger"
                          size="small"
                          @click="removeColumn(index)"
                          style="margin-left: 5px"
                        >
                          删除
                        </el-button>
                      </th>
                      <th style="width: 80px"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>x_list</td>
                      <td v-for="(x, index) in normalizationParams.x_list" :key="'x-' + index">
                        <el-input
                          v-model="normalizationParams.x_list[index]"
                          type="number"
                          style="width: 100px"
                          @change="validateXYList(index)"
                        />
                      </td>
                      <td rowspan="2" style="vertical-align: middle;">
                        <el-button type="primary" size="small" @click="addColumn">
                          新增列
                        </el-button>
                      </td>
                    </tr>
                    <tr>
                      <td>y_list</td>
                      <td v-for="(y, index) in normalizationParams.y_list" :key="'y-' + index">
                        <el-input
                          v-model="normalizationParams.y_list[index]"
                          type="number"
                          style="width: 100px"
                          @change="validateXYList(index)"
                        />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
          </template>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showParameterConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveParameterConfig">确定</el-button>
      </template>
    </el-dialog>

    <!-- Data Source Binding Dialog -->
    <el-dialog v-model="showDataSourceDialog" title="数据源绑定" width="800px">
      <div class="data-source-content">
        <el-form label-width="100px">
          <!-- 参数信息 -->
          <el-form-item label="参数名称">
            <el-input :value="currentParameter?.name" disabled />
          </el-form-item>
          <el-form-item label="参数别名">
            <el-input :value="currentParameter?.alias" disabled />
          </el-form-item>
          <el-form-item label="表名">
            <el-select v-model="dataSourceForm.InferentialListValue" @change="handleInferentialListChange" placeholder="请选择表" style="width: 100%">
              <el-option v-for="item in InferentialList" :label="item.name" :value="item.id" :key="item.id" />
            </el-select>
          </el-form-item>
          <!-- 数据源选择 -->
          <el-form-item label="数据源">
            <el-select v-model="dataSourceForm.dataSource" placeholder="请选择数据源" style="width: 100%">
              <el-option v-for="item in dataSourceList" :label="item.label" :value="item.value" :key="item.value" />
            </el-select>
          </el-form-item>
          
          <!-- 筛选条件 -->
          <el-form-item label="筛选条件">
            <div class="filter-conditions">
              <div v-for="(condition, index) in dataSourceForm.filterConditions" :key="index" class="condition-row">
                <el-select v-model="condition.field" @change="handleFieldChange(condition)" placeholder="选择字段" style="width: 200px">
                  <el-option v-for="item in dataSourceList" :label="item.label" :value="item.value" :key="item.value" />
                </el-select>
                
                <el-select v-model="condition.operator" placeholder="操作符" style="width: 120px; margin: 0 8px" :disabled="!condition.field">
                  <el-option v-for="op in getOperatorsByFieldType(condition.field)" :label="op.label" :value="op.value" :key="op.value" />
                </el-select>
                
                <el-input 
                  v-model="condition.value" 
                  placeholder="输入值" 
                  style="width: 200px"
                  :disabled="condition.operator === 'is_null' || condition.operator === 'is_not_null'"
                />
                
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeFilterCondition(index)"
                  style="margin-left: 8px"
                  :disabled="dataSourceForm.filterConditions.length === 1"
                >
                  删除
                </el-button>
              </div>
              
              <el-button type="primary" size="small" @click="addFilterCondition" class="mt-2">
                <el-icon><Plus /></el-icon>
                新增筛选条件
              </el-button>
            </div>
          </el-form-item>
          
          <!-- 结果取值 -->
          <el-form-item label="结果取值">
            <div class="result-calculation">
              <el-select v-model="dataSourceForm.resultType" placeholder="请选择计算方式" style="width: 200px">
                <el-option label="求和" value="get_sum" />
                <el-option label="平均值" value="get_mean" />
                <el-option label="中位数" value="get_median" />
                <el-option label="最大值" value="get_max" />
                <el-option label="最小值" value="get_min" />
                <el-option label="方差" value="get_variance" />
                <el-option label="标准差" value="get_std" />
                <el-option label="众数" value="get_mode" />
                <el-option label="乘积" value="get_product" />
                <el-option label="绝对值求和" value="get_sum_abs" />
                <el-option label="绝对值平均" value="get_mean_abs" />
                <el-option label="算数平均数" value="get_arithmetic_mean" />
                <el-option label="均方差" value="get_mse" />
                <el-option label="统计个数" value="get_count" />
                <el-option label="统计占比" value="get_percentage" />
              </el-select>
              
              <!-- 统计占比时的额外输入框 -->
              <el-input 
                v-if="dataSourceForm.resultType === 'get_percentage'"
                v-model="dataSourceForm.percentageCondition"
                placeholder="请输入占比条件"
                style="width: 200px; margin-left: 8px"
              />
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showDataSourceDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDataSourceBinding">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
import { ref, reactive, onMounted, nextTick, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getList } from '@/api/UserView'
import { getList as getInferentialDataList } from '@/api/InferentialDataApi'
import { getInferentialList, getDictList } from '@/api/OrderView'
import { computeDare, computeGreyRelational, computeEntropy, computeAph, analyticsSave, analyticsList, computeCoefficient, computeFactor, computePca } from '@/api/AnalyticsApi'

// Reactive data
const baseTreeRef = ref(null)
const customTreeRef = ref(null)
const canvasContainer = ref(null)
const canvasWrapper = ref(null)
const showProperties = ref(false)
const showAddCustomDialog = ref(false)
const showEditCustomDialog = ref(false)
const showAddChildCustomDialog = ref(false)
const showConnectionWarning = ref(false)
const selectedNode = ref(null)
const selectedEdge = ref(null)
const draggedTreeNode = ref(null)
const isDragOver = ref(false)
const parentCustomMetric = ref(null)
const editingCustomMetric = ref(null)
const loadingBaseMetrics = ref(false)
const savingWorkflow = ref(false)
let dragCounter = 0

// Add after existing reactive data declarations
const route = useRoute()
const analyticsId = ref(route.params.id)
// 生成报表并跳转
const generateReport = () => {
  router.push({
    name: 'Report',
    params: {
      id: analyticsId.value
    }
  })
}
const showWeightAllocationDialog = ref(false)
const showParameterConfigDialog = ref(false)
const scoringMethod = ref('expert') // 'expert' or 'formula'
const expertScore = ref(100)
const normalizationAlgorithm = ref('gaussian_mapping')
const parameterList = ref([
  { id: 1, name: '参数一', alias: 'p1' },
  { id: 2, name: '参数二', alias: 'p2' }
])
const newParameter = reactive({
  name: '',
  alias: ''
})
const showAddParameterDialog = ref(false)
const selectedWorkflowType = ref(null)
const selectedWorkflowOption = ref(null)

// Weight allocation data
  const childWeights = ref({})
  const percentageWeights = ref({})
  // 将全局分析方法改为每个节点独立存储
const nodeAnalysisMethod = ref('ahp')
  // 灰色关联分析法相关数据
  const greyRelationalData = ref({
    rho: 0.5,
    index_types: {},
    data_list: []
  })
  // 环比系数法相关数据
  const dareCoefficients = ref([])
  // 灰色白化权聚类法相关数据
  const showGreyClusteringDialog = ref(false)
  const greyClusteringSegments = ref([0, 40, 80, 100])
  const greyClusteringData = ref([])

  // 1. 添加表单引用
const nodeFormRef = ref(null);

// 2. 定义表单验证规则
const nodeFormRules = ref({
  label: [
    { required: true, message: '节点名称不能为空', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim() === '') {
          callback(new Error('节点名称不能为空白字符'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
  description: [
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim() === '') {
          callback(new Error('描述信息不能为空白字符'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
});
  
  // 初始化灰色白化权聚类数据
  const initGreyClusteringData = () => {
    if (!selectedNode.value) return
    const children = getChildNodes(selectedNode.value.id)
    // 从本地存储加载配置
    const nodeDetails = nodeDetailsStorage.value[selectedNode.value.id] || {}
    if (nodeDetails.greyClusteringSegments) {
      greyClusteringSegments.value = nodeDetails.greyClusteringSegments
    }
    if (nodeDetails.greyClusteringData) {
      greyClusteringData.value = nodeDetails.greyClusteringData
    } else {
      // 初始化新数据
      greyClusteringData.value = children.map(child => ({
        nodeId: child.id,
        nodeName: child.label,
        ranges: new Array(greyClusteringSegments.value.length).fill(0)
      }))
    }
  }
  
  // 处理分数段变化
  const handleGreySegmentChange = (index) => {
    // 确保输入值在0-100范围内
    greyClusteringSegments.value[index] = Math.max(0, Math.min(100, Number(greyClusteringSegments.value[index]) || 0))
    // 更新子节点数据的列数
    greyClusteringData.value.forEach(row => {
      while (row.ranges.length < greyClusteringSegments.value.length) {
        row.ranges.push(0)
      }
      while (row.ranges.length > greyClusteringSegments.value.length) {
        row.ranges.pop()
      }
    })
  }
  
  // 新增列
  const addGreyClusteringColumn = () => {
    greyClusteringSegments.value.push(0)
    greyClusteringData.value.forEach(row => {
      row.ranges.push(0)
    })
  }
  
  // 删除列
  const deleteGreyClusteringColumn = () => {
    if (greyClusteringSegments.value.length > 1) {
      greyClusteringSegments.value.pop()
      greyClusteringData.value.forEach(row => {
        row.ranges.pop()
      })
    } else {
      ElMessage.warning('至少保留一列')
    }
  }
  
  // 处理范围输入变化
const handleGreyRangeChange = (row, index) => {
  let val = Number(row.ranges[index]);

  if (isNaN(val) || val < 0) {
    val = 0;
    ElMessage.warning('范围值不能小于0，已自动调整为0');
  } else if (val > 100) {
    val = 100;
    ElMessage.warning('范围值不能大于100，已自动调整为100');
  }

  // 回写合法值
  row.ranges[index] = val;
};
  
  // 保存灰色白化权聚类配置
  // 检查数组是否单调
  const isMonotonic = (arr) => {
    // 确保所有元素都是数字
    const numArr = arr.map(item => Number(item));
    if (numArr.some(isNaN)) return false;
    
    if (numArr.length <= 1) return true;
    
    // 检查是否单调递增
    let isIncreasing = true;
    for (let i = 1; i < numArr.length; i++) {
      if (numArr[i] <= numArr[i-1]) {
        isIncreasing = false;
        break;
      }
    }
    
    // 检查是否单调递减
    let isDecreasing = true;
    for (let i = 1; i < numArr.length; i++) {
      if (numArr[i] >= numArr[i-1]) {
        isDecreasing = false;
        break;
      }
    }
    
    return isIncreasing || isDecreasing;
  }
  
  const saveGreyClusteringConfig = () => {
    console.log('保存灰色白化权聚类配置', greyClusteringSegments.value, greyClusteringData.value)
    // 验证分数分段是否单调
    if (!isMonotonic(greyClusteringSegments.value)) {
      ElMessage.error('分数分段必须是单调递增的数值！');
      return;
    }
    
    // 验证并转换所有ranges值为数字
    let hasInvalidValue = false;
    greyClusteringData.value.forEach(row => {
      row.ranges = row.ranges.map(val => {
        const num = Number(val);
        if (isNaN(num)) {
          hasInvalidValue = true;
          return 0;
        }
        return num;
      });
    });
    
    if (hasInvalidValue) {
      ElMessage.error('所有范围值必须是有效的数字！');
      return;
    }
    
    // 验证每个子节点的ranges数组是否单调递增或递减
    let hasNonMonotonicRanges = false;
    greyClusteringData.value.forEach(row => {
      if (!isMonotonic(row.ranges)) {
        hasNonMonotonicRanges = true;
      }
    });
    
    if (hasNonMonotonicRanges) {
      ElMessage.error('每个子节点的范围值必须是单调递增或递减的！');
      return;
    }
    if (!selectedNode.value) return
    // 保存到节点详情
    const nodeDetails = nodeDetailsStorage.value[selectedNode.value.id] || {}
    nodeDetails.greyClusteringSegments = greyClusteringSegments.value
    nodeDetails.greyClusteringData = greyClusteringData.value
    nodeDetailsStorage.value[selectedNode.value.id] = nodeDetails
    // 保存到本地存储
    saveNodeDetailsToLocal()
    ElMessage.success('配置已保存')
    showGreyClusteringDialog.value = false
  }
  const dareWeights = ref([])
  const dareCoefficientPairs = ref([])
  // 因子分析和主成分分析相关数据
  const factorData = ref({
    data_list: []
  })
  const pcaData = ref({
    data_list: []
  })
  const factorWeights = ref([])
  const pcaWeights = ref([])
  // const customWeight = ref(0)
const ahpMatrix = ref([])
const selectedAlgorithm = ref('weighted')
// AHP计算结果状态
const ahpWeights = ref([])
const greyRelationalWeights = ref([])
const calculatingWeights = ref(false)

// Connection warning data
const connectionWarning = ref({
  sourceId: null,
  targetId: null,
  targetLabel: '',
  existingParentLabel: ''
})

// Snap to grid functionality
const snapToGrid = ref(true)
const snapThreshold = 20
const snapGuides = ref({
  vertical: null,
  horizontal: null
})

// Zoom and pan states
const zoomLevel = ref(1)
const panOffset = ref({ x: 0, y: 0 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

// Drag and connection states
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const isConnecting = ref(false)
const connectionStart = ref(null)
const tempEdge = ref(null)

// Context menu
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  node: null,
  edge: null,
  type: null
})

// Tree configuration
const treeProps = {
  children: 'children',
  label: 'label'
}

// Base metrics data (from API)
const baseMetricsData = ref([
  {
    id: 'base-metrics',
    label: '基础指标',
    children: []
  }
])
const data = {
  page: 1,
  num: 20,
  name: ''
}
const nodes = ref([])

// 获取初始数据
const getInitialData = async() => {
  await analyticsList(analyticsId.value).then(res => {
    console.log(res.data)
    customMetricsData.value = res.data.treeData.customMetrics
    graphData.value = res.data.graphData
    nodeDetailsStorage.value = res.data.nodeDetails ? res.data.nodeDetails : {}
    selectedWorkflowType.value = res.data.workflowType
    // 不再设置全局分析方法，改为从节点详情加载
  })
}
const basicTreeData = {
    page: 1,
    num: 10000,
    name: ''
  }
// 获取基础指标左侧树结构数据
const getBasicData = async() => {
  await getList(basicTreeData).then(res => {
  nodes.value = res.data.info
  baseMetricsData.value[0].children = res.data.info.map(item => ({
    label: item.name,
    id: item.id,
    description: item.description,
  }))
  console.log(baseMetricsData.value)
})
}

// 获取推演数据列表
const getInferentialData = async() => {
  await getInferentialDataList(data).then(res => {
    console.log(res.data)
    selectedWorkflowOption.value = res.data.info.map(item => ({
      label: item.name,
      value: item.id
    }))
  })
  selectedWorkflowType.value = selectedWorkflowOption.value[0].value
}

// Custom metrics data (local management)
const customMetricsData = ref([
  {
    id: 'custom-metrics',
    label: '自定义指标',
    children: []
  }
])

// Form data
const nodeForm = reactive({
  label: '',
  metricType: '',
  description: '',
  code: '',
  category: '',
  weight: 0,
  formula: '',
  dataSource: '',
  businessRule: '',
  x: 0,
  y: 0,
  createTime: null,
  updateTime: null
})

const edgeForm = reactive({
  label: '',
  type: 'dataflow',
  description: '',
  source: '',
  target: '',
  createTime: null,
  updateTime: null
})

const customMetricForm = reactive({
  label: '',
  description: ''
})

const editCustomMetricForm = reactive({
  label: '',
  description: ''
})

const childCustomMetricForm = reactive({
  label: '',
  description: ''
})

// Graph data
const graphData = ref({
  nodes: [],
  edges: []
})

// Node details storage (local storage for node properties)
const nodeDetailsStorage = ref({})

// Add to reactive data
const normalizationParams = reactive({
  mu: 0,
  k: 0,
  mean: 0,
  std: 0,
  decimal: 0,
  d: 0,
  x_min: 0,
  x_max: 0,
  upDown: 0,
  x_list: [0],
  y_list: [0]
})
/** 归一化算法切换 → 重置参数 */
const resetNormalizationParams = (alg) => {
  const base = {
    mu: 0,
    k: 0,
    mean: 0,
    std: 0,
    decimal: 2,
    d: 0,
    x_min: 0,
    x_max: 0,
    upDown: '1',
    x_list: [0],
    y_list: [0],
  };

  switch (alg) {
    case 'gaussian_mapping':
    case 'cauchy_mapping':
    case 'exponential_decay':
    case 'logistic_variant':
      Object.assign(normalizationParams, { ...base, mu: 0.5, k: 1 });
      break;

    case 'linear_segment':
      Object.assign(normalizationParams, { ...base, mu: 50, d: 10 });
      break;

    case 'linear_mapping':
      Object.assign(normalizationParams, { ...base, x_min: 0, x_max: 100, upDown: '1' });
      break;

    case 'zero_one_mapping':
      Object.assign(normalizationParams, { ...base, mu: 50 });
      break;

    case 'segmentation_liner_mapping':
    case 'segmentation_mapping':
      Object.assign(normalizationParams, { ...base, x_list: [0, 50, 100], y_list: [0, 50, 100] });
      break;

    default:
      Object.assign(normalizationParams, base);
  }
};
/**
 * 参数超界自动修正并提示
 * @param {string} key  params 的键
 * @param {number} min  最小值
 * @param {number} max  最大值
 * @param {string} msg  提示语
 */
const checkParam = (key, min, max, msg) => {
  let val = Number(normalizationParams[key]);
  if (isNaN(val)) val = min;
  if (val < min) {
    normalizationParams[key] = min;
    ElMessage.warning(msg);
  } else if (val > max) {
    normalizationParams[key] = max;
    ElMessage.warning(msg);
  } else {
    normalizationParams[key] = Math.round(val * 100) / 100; // 保留两位
  }
};

// Functions for managing parameter columns
const addColumn = () => {
  // Add new x value (last value + 50)
  const lastXValue = normalizationParams.x_list[normalizationParams.x_list.length - 1] || 0
  normalizationParams.x_list.push(lastXValue + 1)

  // Add new y value (same as last y value)
  const lastYValue = normalizationParams.y_list[normalizationParams.y_list.length - 1] || 0
  normalizationParams.y_list.push(lastYValue)
}

const removeColumn = (index) => {
    normalizationParams.x_list.splice(index, 1)
    normalizationParams.y_list.splice(index, 1)
}

// Validate x_list: ensure each value is positive and later values are greater than previous ones
const validateXYList = (index) => {
  ['x_list', 'y_list'].forEach((arrKey) => {
    let val = Number(normalizationParams[arrKey][index]);
    if (isNaN(val)) val = 0;
    if (val < 0) {
      val = 0;
      ElMessage.warning(`${arrKey} 值不能小于 0`);
    } else if (val > 100) {
      val = 100;
      ElMessage.warning(`${arrKey} 值不能大于 100`);
    }
    normalizationParams[arrKey][index] = Math.round(val * 100) / 100;
  });
};
const basicTreeName = ref('')
// API functions
const basicTreeDataSearch = async () => {
  basicTreeData.name = basicTreeName.value
  loadingBaseMetrics.value = true
  try {
    // 模拟API调用
    await getBasicData()
    
    // 更新基础指标数据
    // baseMetricsData.value[0].children = baseMetrics
    
    ElMessage.success('基础指标加载成功')
  } catch (error) {
    ElMessage.error('基础指标加载失败')
    console.error('Load base metrics error:', error)
  } finally {
    loadingBaseMetrics.value = false
  }
}

const togoBack = () => {
  router.push('/dashboard')
}

const refreshBaseMetrics = () => {
  basicTreeDataSearch()
  getBasicData()
}

// Custom metrics management
const addCustomMetric = () => {
  if (!customMetricForm.label) {
    ElMessage.warning('请输入指标名称')
    return
  }

  const newMetric = {
    id: `custom-${Date.now()}`,
    label: customMetricForm.label,
    description: customMetricForm.description
  }

  // 添加到自定义指标的children中
  customMetricsData.value[0].children.push(newMetric)
  showAddCustomDialog.value = false
  
  // Reset form
  customMetricForm.label = ''
  customMetricForm.description = ''
  
  saveCustomMetricsToLocal()
  ElMessage.success('自定义指标添加成功')
}

const editCustomMetric = (metric) => {
  editingCustomMetric.value = metric
  editCustomMetricForm.label = metric.label
  editCustomMetricForm.description = metric.description || ''
  showEditCustomDialog.value = true
}

const saveEditCustomMetric = () => {
  if (!editCustomMetricForm.label) {
    ElMessage.warning('请输入指标名称')
    return
  }

  if (editingCustomMetric.value) {
    editingCustomMetric.value.label = editCustomMetricForm.label
    editingCustomMetric.value.description = editCustomMetricForm.description
    editingCustomMetric.value.updateTime = Date.now()
  }

  showEditCustomDialog.value = false
  editingCustomMetric.value = null
  saveCustomMetricsToLocal()
  ElMessage.success('自定义指标编辑成功')
}

const addChildCustomMetricDialog = (parentMetric) => {
  parentCustomMetric.value = parentMetric
  childCustomMetricForm.label = ''
  childCustomMetricForm.description = ''
  showAddChildCustomDialog.value = true
}

const addChildCustomMetricAction = () => {
  if (!childCustomMetricForm.label) {
    ElMessage.warning('请输入指标名称')
    return
  }

  if (!parentCustomMetric.value) {
    ElMessage.error('未找到父指标')
    return
  }

  const newChild = {
    id: `custom-child-${Date.now()}`,
    label: childCustomMetricForm.label,
    description: childCustomMetricForm.description
  }

  if (!parentCustomMetric.value.children) {
    parentCustomMetric.value.children = []
  }

  parentCustomMetric.value.children.push(newChild)
  showAddChildCustomDialog.value = false
  saveCustomMetricsToLocal()
  ElMessage.success('子指标添加成功')
}

const deleteCustomMetric = (metric) => {
  if (hasChildren(metric)) {
    ElMessage.warning('该指标存在子指标，无法删除')
    return
  }

  ElMessageBox.confirm(`确定要删除 "${metric.label}" 吗？`, '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const removeMetricFromTree = (metrics, targetId) => {
      for (let i = 0; i < metrics.length; i++) {
        if (metrics[i].id === targetId) {
          metrics.splice(i, 1)
          return true
        }
        if (metrics[i].children) {
          if (removeMetricFromTree(metrics[i].children, targetId)) {
            return true
          }
        }
      }
      return false
    }

    removeMetricFromTree(customMetricsData.value, metric.id)
    saveCustomMetricsToLocal()
    ElMessage.success('自定义指标已删除')
  })
}

// Local storage functions
const saveCustomMetricsToLocal = () => {
  localStorage.setItem('custom-metrics', JSON.stringify(customMetricsData.value))
}

const saveNodeDetailsToLocal = (nodeId, details) => {
  nodeDetailsStorage.value[nodeId] = {
    ...details,
    updateTime: Date.now()
  }
  localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value))
}

// 画布数据本地存储函数
const saveGraphDataToLocal = () => {
  try {
    const graphDataToSave = {
      nodes: graphData.value.nodes,
      edges: graphData.value.edges,
    }
    localStorage.setItem('workflow-graph', JSON.stringify(graphDataToSave))
    console.log('Graph data saved to localStorage')
  } catch (error) {
    console.error('Failed to save graph data:', error)
  }
}

// Workflow save function
const saveWorkflow = async () => {
  savingWorkflow.value = true
  try {
    // 准备要发送到后端的完整数据
    // 获取所有已连接的节点ID
    const connectedNodeIds = new Set();
    graphData.value.edges.forEach(edge => {
      connectedNodeIds.add(edge.source);
      connectedNodeIds.add(edge.target);
    });

    // 过滤掉未连接的节点
    const filteredNodes = graphData.value.nodes.filter(node => connectedNodeIds.has(node.id));
    // 更新本地节点数据以反映删除
    graphData.value.nodes = filteredNodes;

    // 确保所有节点在nodeDetailsStorage中都有条目，包括默认值
    filteredNodes.forEach(node => {
      if (!nodeDetailsStorage.value[node.id]) {
        // 创建默认属性
        nodeDetailsStorage.value[node.id] = {
          label: node.label || '',
          description: node.description || '',
          code: node.code || '',
          category: node.category || '',
          weight: node.weight || 0,
          formula: node.formula || '',
          businessRule: '',
          updateTime: Date.now()
        };
      }
    });

    const workflowData = {
      // 左侧树数据
      treeData: {
        baseMetrics: baseMetricsData.value,
        customMetrics: customMetricsData.value
      },
      // 画布数据
      graphData: {
        nodes: filteredNodes,
        edges: graphData.value.edges
      },
      // 所有节点的详细属性数据
      nodeDetails: nodeDetailsStorage.value,
      // 工作流类型
      workflowType: selectedWorkflowType.value,
      // selectedAnalysisMethod: selectedAnalysisMethod.value,
    }

    // 模拟发送到后端API
    console.log('Saving workflow data:', workflowData)
    
    // 这里替换为实际的API调用
    // const response = await fetch('/api/workflow/save', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify(workflowData)
    // })
    
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 1500))
    await analyticsSave({
      id: analyticsId.value,
      detail: workflowData
    }).then(() => {
      ElMessage.success('工作流保存成功')
    })
    // 同时保存到本地存储作为备份
    localStorage.setItem('workflow-backup', JSON.stringify(workflowData))
    saveGraphDataToLocal()
  } catch (error) {
    ElMessage.error('工作流保存失败')
    console.error('Save workflow error:', error)
  } finally {
    savingWorkflow.value = false
  }
}

const updateNodeParentStatus = (nodeId) => {
  // 这里不需要实际更新节点状态，因为我们使用的是计算属性和条件渲染
  // 这个函数的调用主要是为了触发Vue的响应式更新
  nextTick(() => {
    // 强制重新渲染
    if (selectedNode.value && selectedNode.value.id === nodeId) {
      // 如果选中的节点就是被影响的节点，重新加载其属性
      selectNode(selectedNode.value);
    }
  });
}

// Helper functions for parent-child relationships
const hasParentNode = (nodeId) => {
  return graphData.value.edges.some(edge => edge.target === nodeId)
}

const getParentNodes = (nodeId) => {
  return graphData.value.edges
    .filter(edge => edge.target === nodeId)
    .map(edge => graphData.value.nodes.find(node => node.id === edge.source))
    .filter(Boolean)
}

const getChildNodes = (nodeId) => {
  return graphData.value.edges
    .filter(edge => edge.source === nodeId)
    .map(edge => graphData.value.nodes.find(node => node.id === edge.target))
    .filter(Boolean)
}

const canConnectTo = (targetNodeId) => {
  if (!isConnecting.value || !connectionStart.value) return true
  
  // 不能连接到自己
  if (connectionStart.value.id === targetNodeId) return false
  
  // 检查是否会形成循环
  if (wouldCreateCycle(connectionStart.value.id, targetNodeId)) return false
  
  return true
}

const wouldCreateCycle = (sourceId, targetId) => {
  // 检查从targetId开始，是否能通过子节点路径回到sourceId
  const visited = new Set()
  
  const dfs = (currentId) => {
    if (visited.has(currentId)) return false
    if (currentId === sourceId) return true
    
    visited.add(currentId)
    
    const children = graphData.value.edges
      .filter(edge => edge.source === currentId)
      .map(edge => edge.target)
    
    for (const childId of children) {
      if (dfs(childId)) return true
    }
    
    return false
  }
  
  return dfs(targetId)
}

const getNodeLabel = (nodeId) => {
  const node = graphData.value.nodes.find(n => n.id === nodeId)
  return node ? node.label : '未知节点'
}

const formatDate = (timestamp) => {
  if (!timestamp) return '未设置'
  return new Date(timestamp).toLocaleString('zh-CN')
}

const hasChildren = (node) => {
  return node.children && node.children.length > 0
}

const getNodePosition = (nodeId) => {
  const node = graphData.value.nodes.find(n => n.id === nodeId)
  return node ? { x: node.x + 70, y: node.y + 25 } : { x: 0, y: 0 }
}

const getEdgePath = (edge) => {
  const sourcePos = getNodePosition(edge.source)
  const targetPos = getNodePosition(edge.target)
  
  const startX = sourcePos.x + 70
  const startY = sourcePos.y
  const endX = targetPos.x - 70
  const endY = targetPos.y
  
  const midX = startX + (endX - startX) / 2
  
  return `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${endY} L ${endX} ${endY}`
}

// 判断拖拽的节点来源
const getMetricTypeFromDraggedNode = (draggedNode) => {
  // 检查是否来自基础指标树
  const isFromBaseMetrics = (node, baseTree) => {
    if (!baseTree || !baseTree.children) return false
    
    const checkInChildren = (children) => {
      for (let child of children) {
        if (child.id === node.id) return true
        if (child.children && checkInChildren(child.children)) return true
      }
      return false
    }
    
    return checkInChildren(baseTree.children)
  }
  
  // 检查是否来自自定义指标树
  const isFromCustomMetrics = (node, customTree) => {
    if (!customTree || !customTree.children) return false
    
    const checkInChildren = (children) => {
      for (let child of children) {
        if (child.id === node.id) return true
        if (child.children && checkInChildren(child.children)) return true
      }
      return false
    }
    
    return checkInChildren(customTree.children)
  }
  
  if (isFromBaseMetrics(draggedNode, baseMetricsData.value[0])) {
    return 'base'
  } else if (isFromCustomMetrics(draggedNode, customMetricsData.value[0])) {
    return 'custom'
  }
  
  return 'base' // 默认为基础指标
}

// Modified connection functions
const startConnection = (event, node, type) => {
  event.stopPropagation()
  
  if (!isConnecting.value) {
    // 开始连线
    isConnecting.value = true
    connectionStart.value = node
    ElMessage.info(`开始连线，请点击目标节点完成连接`)
    
    // 添加鼠标移动监听来显示临时连线
    const handleConnectionMove = (moveEvent) => {
      if (!canvasWrapper.value || !connectionStart.value) return
      
      const rect = canvasWrapper.value.getBoundingClientRect()
      const startPos = getNodePosition(connectionStart.value.id)
      
      const mouseX = (moveEvent.clientX - rect.left - panOffset.value.x) / zoomLevel.value
      const mouseY = (moveEvent.clientY - rect.top - panOffset.value.y) / zoomLevel.value
      
      const startX = startPos.x + 70
      const startY = startPos.y
      const midX = startX + (mouseX - startX) / 2
      
      // 检查鼠标位置是否在有效的连接目标上
      const targetNode = getNodeAtPosition(mouseX, mouseY)
      const isValidConnection = targetNode && canConnectTo(targetNode.id)
      
      tempEdge.value = {
        path: `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${mouseY} L ${mouseX} ${mouseY}`,
        valid: isValidConnection
      }
    }
    
    const handleConnectionEnd = () => {
      document.removeEventListener('mousemove', handleConnectionMove)
      document.removeEventListener('click', handleConnectionEnd)
    }
    
    document.addEventListener('mousemove', handleConnectionMove)
    document.addEventListener('click', handleConnectionEnd)
  } else {
    // 完成连线
    if (connectionStart.value && connectionStart.value.id !== node.id) {
      attemptCreateEdge(connectionStart.value.id, node.id)
    }
    
    // 重置连线状态
    isConnecting.value = false
    connectionStart.value = null
    tempEdge.value = null
  }
}

const getNodeAtPosition = (x, y) => {
  return graphData.value.nodes.find(node => {
    return x >= node.x && x <= node.x + 140 &&
           y >= node.y && y <= node.y + 50
  })
}

const attemptCreateEdge = (sourceId, targetId) => {
  // 检查是否会形成循环
  if (wouldCreateCycle(sourceId, targetId)) {
    ElMessage.error('无法创建连线：会形成循环依赖')
    return
  }
  
  // 检查目标节点是否已有父节点
  const existingParentEdge = graphData.value.edges.find(edge => edge.target === targetId)
  
  if (existingParentEdge) {
    // 显示警告对话框
    const targetNode = graphData.value.nodes.find(n => n.id === targetId)
    const existingParentNode = graphData.value.nodes.find(n => n.id === existingParentEdge.source)
    
    connectionWarning.value = {
      sourceId: sourceId,
      targetId: targetId,
      targetLabel: targetNode?.label || '未知节点',
      existingParentLabel: existingParentNode?.label || '未知节点'
    }
    
    showConnectionWarning.value = true
  } else {
    // 直接创建连线
    createEdge(sourceId, targetId)
  }
}

const replaceParentConnection = () => {
  const { sourceId, targetId } = connectionWarning.value
  
  // 删除现有的父连线
  const existingParentEdge = graphData.value.edges.find(edge => edge.target === targetId)
  if (existingParentEdge) {
    graphData.value.edges = graphData.value.edges.filter(e => e.id !== existingParentEdge.id)
  // 更新节点状态
  updateNodeParentStatus(existingParentEdge.source)
  updateNodeParentStatus(targetId)
  }
  
  // 创建新连线
  createEdge(sourceId, targetId)
  
  showConnectionWarning.value = false
  ElMessage.success('父节点已替换')
}

const createEdge = (sourceId, targetId) => {
  const edgeId = `edge-${sourceId}-${targetId}`
  const existingEdge = graphData.value.edges.find(e => e.id === edgeId)
  
  if (!existingEdge) {
    const now = Date.now()
    const newEdge = {
      id: edgeId,
      source: sourceId,
      target: targetId,
      label: '',
      type: 'dataflow',
      description: '',
      createTime: now,
      updateTime: now
    }
    
    graphData.value.edges.push(newEdge)
    ElMessage.success('连线创建成功')
  } else {
    ElMessage.warning('连线已存在')
  }
}

// Node selection and operations
const selectNode = (node) => {
  // customWeight.value = nodeDetailsStorage.value[node.id]?.customWeight || 0
  selectedAlgorithm.value = nodeDetailsStorage.value[node.id]?.selectedAlgorithm || 'weighted'

  // 从本地存储加载权重结果和分析方法
  const nodeDetails = nodeDetailsStorage.value[node.id] || {};
  if (nodeDetails.selectedAnalysisMethod) {
    nodeAnalysisMethod.value = nodeDetails.selectedAnalysisMethod;
  }
  if (nodeDetails.ahpWeights) {
    ahpWeights.value = nodeDetails.ahpWeights
  } else {
    ahpWeights.value = [];
  }
  console.log('Selected node:', node)
  if (isConnecting.value) {
    // 完成连线
    if (connectionStart.value && connectionStart.value.id !== node.id) {
      attemptCreateEdge(connectionStart.value.id, node.id)
    }
    
    // 重置连线状态
    isConnecting.value = false
    connectionStart.value = null
    tempEdge.value = null
    return
  }
  
  // 正常选择节点
  selectedNode.value = node
  selectedEdge.value = null
  
  // 从本地存储加载节点详情，如果没有则使用节点基本信息
  const savedDetails = nodeDetailsStorage.value[node.id] || {}
  
  Object.assign(nodeForm, {
    label: savedDetails.label || node.label || '',
    metricType: node.metricType || 'base',
    description: savedDetails.hasOwnProperty('description')
    ? savedDetails.description
    : (node.description || ''),
    code: savedDetails.code || node.code || '',
    category: savedDetails.category || node.category || '',
    weight: savedDetails.weight || node.weight || 0,
    formula: savedDetails.formula || node.formula ||'',
    dataSource: savedDetails.dataSource || '',
    businessRule: savedDetails.businessRule || '',
    x: Math.round(node.x),
    y: Math.round(node.y),
    createTime: node.createTime || null,
    updateTime: savedDetails.updateTime || node.updateTime || null
  })
  
  // 加载扩展属性
  scoringMethod.value = savedDetails.scoringMethod || scoringMethod.value
  expertScore.value = savedDetails.expertScore || 100
  normalizationAlgorithm.value = savedDetails.normalizationAlgorithm || 'gaussian_mapping'
  parameterList.value = (savedDetails.parameterList || node.params || []).map((param, index) => ({
  ...param,
  id: param.id || `param-${Date.now()}-${index}`
}))
  
  // 加载权重分配数据
  childWeights.value = savedDetails.childWeights || {}
  
  // 加载归一化参数
  if (savedDetails.normalizationParams) {
    Object.assign(normalizationParams, savedDetails.normalizationParams)
  } else {
    Object.assign(normalizationParams, {
      mu: 0.5,
      k: 1.0,
      mean: 0,
      std: 1,
      decimal: 2
    })
  }
  
  showProperties.value = true
}

// Edge operations
const selectEdge = (edge, event) => {
  event.stopPropagation()
  selectedEdge.value = edge
  selectedNode.value = null
  
  Object.assign(edgeForm, {
    label: edge.label || '',
    type: edge.type || 'dataflow',
    description: edge.description || '',
    source: edge.source,
    target: edge.target,
    createTime: edge.createTime || null,
    updateTime: edge.updateTime || null
  })
  
  // showProperties.value = true
}

const deleteSelectedEdge = () => {
  if (selectedEdge.value) {
    ElMessageBox.confirm('确定要删除这条连线吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      graphData.value.edges = graphData.value.edges.filter(e => e.id !== selectedEdge.value.id)
      selectedEdge.value = null
      showProperties.value = false
      ElMessage.success('连线已删除')
    })
  }
}

const saveEdgeProperties = () => {
  if (selectedEdge.value) {
    Object.assign(selectedEdge.value, {
      ...edgeForm,
      updateTime: Date.now()
    })
    showProperties.value = false
    ElMessage.success('连线属性已保存')
  }
}

const showEdgeContextMenu = (event, edge) => {
  event.preventDefault()
  event.stopPropagation()
  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    edge: edge,
    type: 'edge'
  }
  
  document.addEventListener('click', hideContextMenu)
}

const deleteContextEdge = () => {
  if (contextMenu.value.edge) {
    graphData.value.edges = graphData.value.edges.filter(e => e.id !== contextMenu.value.edge.id)
    if (selectedEdge.value && selectedEdge.value.id === contextMenu.value.edge.id) {
      selectedEdge.value = null
      showProperties.value = false
    }
    ElMessage.success('连线已删除')
  }
  hideContextMenu()
}

const editContextEdge = () => {
  if (contextMenu.value.edge) {
    selectEdge(contextMenu.value.edge, { stopPropagation: () => {} })
  }
  hideContextMenu()
}

// Snap to grid functions
const toggleSnapToGrid = () => {
  snapToGrid.value = !snapToGrid.value
  ElMessage.info(snapToGrid.value ? '已开启网格吸附' : '已关闭网格吸附')
}

const clearSnapGuides = () => {
  snapGuides.value.vertical = null
  snapGuides.value.horizontal = null
}

// Zoom and pan functions
const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, 3)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, 0.1)
}

const resetZoom = () => {
  zoomLevel.value = 1
  panOffset.value = { x: 0, y: 0 }
}

const handleWheel = (event) => {
  event.preventDefault()
  
  if (!canvasWrapper.value) return
  
  const rect = canvasWrapper.value.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(0.1, Math.min(3, zoomLevel.value * delta))
  
  const zoomRatio = newZoom / zoomLevel.value
  panOffset.value.x = mouseX - (mouseX - panOffset.value.x) * zoomRatio
  panOffset.value.y = mouseY - (mouseY - panOffset.value.y) * zoomRatio
  
  zoomLevel.value = newZoom
}

const handleCanvasMouseDown = (event) => {
  if (event.target === canvasWrapper.value || event.target === canvasContainer.value) {
    isPanning.value = true
    panStart.value = {
      x: event.clientX - panOffset.value.x,
      y: event.clientY - panOffset.value.y
    }
    
    document.addEventListener('mousemove', handlePanMove)
    document.addEventListener('mouseup', handlePanEnd)
  }
}

const handlePanMove = (event) => {
  if (!isPanning.value) return
  
  panOffset.value = {
    x: event.clientX - panStart.value.x,
    y: event.clientY - panStart.value.y
  }
}

const handlePanEnd = () => {
  isPanning.value = false
  document.removeEventListener('mousemove', handlePanMove)
  document.removeEventListener('mouseup', handlePanEnd)
}

// Tree drag handlers
const handleTreeNodeDragStart = (event, data) => {
  draggedTreeNode.value = data
  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('application/json', JSON.stringify(data))
  event.target.style.opacity = '0.5'
}

const handleTreeNodeDragEnd = (event) => {
  event.target.style.opacity = '1'
  draggedTreeNode.value = null
}

// Drop handlers
const handleDragEnter = (event) => {
  event.preventDefault()
  dragCounter++
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  dragCounter--
  if (dragCounter === 0) {
    isDragOver.value = false
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'copy'
}

const handleDrop = (event) => {
  event.preventDefault()
  dragCounter = 0
  isDragOver.value = false
  
  if (!draggedTreeNode.value || !canvasContainer.value) return
  
  const rect = canvasContainer.value.getBoundingClientRect()
  const x = (event.clientX - rect.left - panOffset.value.x) / zoomLevel.value - 70
  const y = (event.clientY - rect.top - panOffset.value.y) / zoomLevel.value - 25
  
  const snappedPos = snapToPosition(Math.max(10, x), Math.max(10, y))
  const now = Date.now()
  
  // 确定指标类型
  const metricType = getMetricTypeFromDraggedNode(draggedTreeNode.value)
  
  const newNode = {
    id: `node-${now}`,
    label: draggedTreeNode.value.label,
    x: snappedPos.x,
    y: snappedPos.y,
    metricType: metricType,
    description: draggedTreeNode.value.description || '',
    code: draggedTreeNode.value.code || draggedTreeNode.value.id,
    category: '',
    weight: 0,
    createTime: now,
    updateTime: now,
    formula: nodes.value.find(node => node.id === draggedTreeNode.value.id)?.formula || '',
    params: nodes.value.find(node => node.id === draggedTreeNode.value.id)?.params || []
  }
  
  graphData.value.nodes.push(newNode)
  draggedTreeNode.value = null
  
  setTimeout(clearSnapGuides, 1000)
  
  ElMessage.success('节点添加成功')
}

const updateNodePosition = () => {
  if (selectedNode.value) {
    const snappedPos = snapToPosition(nodeForm.x, nodeForm.y, selectedNode.value.id)
    
    selectedNode.value.x = snappedPos.x
    selectedNode.value.y = snappedPos.y
    selectedNode.value.updateTime = Date.now()
    
    nodeForm.x = snappedPos.x
    nodeForm.y = snappedPos.y
    
    setTimeout(clearSnapGuides, 1000)
  }
}

const startDrag = (event, node) => {
  if (isConnecting.value || isPanning.value) return
  
  isDragging.value = true
  selectedNode.value = node
  selectedEdge.value = null
  
  const rect = canvasContainer.value.getBoundingClientRect()
  dragOffset.value = {
    x: (event.clientX - rect.left - panOffset.value.x) / zoomLevel.value - node.x,
    y: (event.clientY - rect.top - panOffset.value.y) / zoomLevel.value - node.y
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event) => {
  if (!isDragging.value || !selectedNode.value || !canvasContainer.value) return
  
  const rect = canvasContainer.value.getBoundingClientRect()
  const x = (event.clientX - rect.left - panOffset.value.x) / zoomLevel.value - dragOffset.value.x
  const y = (event.clientY - rect.top - panOffset.value.y) / zoomLevel.value - dragOffset.value.y
  
  const snappedPos = snapToPosition(Math.max(10, x), Math.max(10, y), selectedNode.value.id)
  selectedNode.value.x = snappedPos.x
  selectedNode.value.y = snappedPos.y
  
  if (isConnecting.value && connectionStart.value) {
    const startPos = getNodePosition(connectionStart.value.id)
    const endX = (event.clientX - rect.left - panOffset.value.x) / zoomLevel.value
    const endY = (event.clientY - rect.top - panOffset.value.y) / zoomLevel.value
    
    const startX = startPos.x + 70
    const startY = startPos.y
    const midX = startX + (endX - startX) / 2
    
    tempEdge.value = {
      path: `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${mouseY} L ${mouseX} ${mouseY}`,
      valid: true
    }
  }
}

const handleMouseUp = () => {
  if (isDragging.value && selectedNode.value) {
    selectedNode.value.updateTime = Date.now()
    setTimeout(clearSnapGuides, 1000)
  }
  
  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const showNodeContextMenu = (event, node) => {
  event.preventDefault()
  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    node: node,
    type: 'node'
  }
  
  document.addEventListener('click', hideContextMenu)
}

const hideContextMenu = () => {
  contextMenu.value.show = false
  document.removeEventListener('click', hideContextMenu)
}

const deleteSelectedNode = () => {
  if (contextMenu.value.node) {
    deleteGraphNode(contextMenu.value.node.id)
  }
  hideContextMenu()
}

const duplicateNode = () => {
  if (contextMenu.value.node) {
    const originalNode = contextMenu.value.node
    const now = Date.now()
    const newNode = {
      ...originalNode,
      id: `node-${now}`,
      x: originalNode.x + 50,
      y: originalNode.y + 50,
      createTime: now,
      updateTime: now
    }
    graphData.value.nodes.push(newNode)
    ElMessage.success('节点复制成功')
  }
  hideContextMenu()
}

// Graph operations
const clearGraph = () => {
  ElMessageBox.confirm('确定要清空所有节点吗？', '确认清空', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    graphData.value.nodes = []
    graphData.value.edges = []
    selectedNode.value = null
    selectedEdge.value = null
    showProperties.value = false
    clearSnapGuides()
    // 清空内存中的数据
    nodeDetailsStorage.value = {}
    childWeights.value = {}
    
    // 清理所有本地存储的数据
    localStorage.removeItem('custom-metrics')
    localStorage.removeItem('node-details')
    localStorage.removeItem('workflow-backup')
    localStorage.removeItem('workflow-graph')
    ElMessage.success('图表已清空')
  })
  saveGraphDataToLocal()
}

const deleteGraphNode = (nodeId) => {
  graphData.value.nodes = graphData.value.nodes.filter(n => n.id !== nodeId)
  graphData.value.edges = graphData.value.edges.filter(e => e.source !== nodeId && e.target !== nodeId)
  
  // 删除节点详情数据
  if (nodeDetailsStorage.value[nodeId]) {
    delete nodeDetailsStorage.value[nodeId]
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value))
  }
  
  if (selectedNode.value && selectedNode.value.id === nodeId) {
    selectedNode.value = null
    showProperties.value = false
  }
  
  ElMessage.success('节点已删除')
}

const saveNodeProperties = () => {
   nodeFormRef.value.validate((valid) => {
    if (valid) {
      // 验证通过，执行保存逻辑
      if (selectedNode.value) {
        // 更新节点基本信息
        Object.assign(selectedNode.value, {
          label: nodeForm.label,
          updateTime: Date.now()
        })
        
        // 保存详细属性到本地存储，包括所有扩展属性
        const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
        saveNodeDetailsToLocal(selectedNode.value.id, {
          ...existingDetails,
          label: nodeForm.label,
          description: nodeForm.description,
          code: nodeForm.code,
          category: nodeForm.category,
          weight: nodeForm.weight,
          formula: nodeForm.formula,
          // Removed dataSource to prevent overwriting dataSources
          businessRule: nodeForm.businessRule,
          // 扩展属性
          scoringMethod: scoringMethod.value,
          expertScore: expertScore.value,
          normalizationAlgorithm: normalizationAlgorithm.value,
          parameterList: parameterList.value,
          childWeights: childWeights.value,
          // customWeight: customWeight.value,
          selectedAlgorithm: selectedAlgorithm.value,
          normalizationParams: { ...normalizationParams },
          // 保存节点分析方法
          selectedAnalysisMethod: nodeAnalysisMethod.value
        })
        
        showProperties.value = false
        ElMessage.success('属性已保存到本地')
    }
    } else {
      // 验证失败
      ElMessage.error('请完善节点信息');
      return false;
    }
  });
}

const handleCanvasClick = (event) => {
  if (event.target === canvasContainer.value) {
    if (isConnecting.value) {
      isConnecting.value = false
      connectionStart.value = null
      tempEdge.value = null
      ElMessage.info('连线已取消')
    } else {
      selectedNode.value = null
      selectedEdge.value = null
      showProperties.value = false
    }
    clearSnapGuides()
  }
}

// Add new methods
const openWeightAllocation = () => {
  const children = getChildNodes(selectedNode.value.id)
  // 从本地存储加载权重并转换为百分比
  const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {}
  const savedWeights = savedDetails.childWeights || {}
  children.forEach(child => {
    percentageWeights.value[child.id] = (savedWeights[child.id] || 0) * 100
    childWeights.value[child.id] = savedWeights[child.id] || 0
  })

  // 初始化矩阵数据
  if (nodeAnalysisMethod.value === 'ahp') {
    // 尝试从本地存储加载已保存的矩阵
    const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    if (savedDetails.ahpMatrix && savedDetails.ahpMatrix.length === children.length) {
      ahpMatrix.value = savedDetails.ahpMatrix.map(row => [...row]);
      // 确保对角线为1
      ahpMatrix.value.forEach((row, i) => row[i] = 1);
    } else {
      ahpMatrix.value = children.map((_, i) => 
        children.map((_, j) => i === j ? 1 : 0)
      );
    }
  } else if (nodeAnalysisMethod.value === 'EntropyWeight' || nodeAnalysisMethod.value === 'CoefficientMethod') {
    // 尝试从本地存储加载已保存的数据
    const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    const methodKey = nodeAnalysisMethod.value;
    if (savedDetails[methodKey + 'MatrixData']) {
      methodMatrixData.value = savedDetails[methodKey + 'MatrixData'];
      methodWeights.value = savedDetails[methodKey + 'Weights'] || [];
    } else {
      // 初始化新的矩阵数据
      methodMatrixData.value = children.map(child => ({
        name: child.label,
        row_list: new Array(4).fill(0)
      }));
      methodWeights.value = [];
    }
  } else if (nodeAnalysisMethod.value === 'GreyRelationalAnalysis') {
    // 尝试从本地存储加载已保存的数据
    const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    if (savedDetails.greyRelationalData) {
      greyRelationalData.value = savedDetails.greyRelationalData;
      greyRelationalWeights.value = savedDetails.greyRelationalWeights || [];
    } else {
      // 初始化新的灰色关联分析数据
      greyRelationalData.value = {
        rho: 0.5,
        index_types: children.map(() => 'positive'),
        data_list: []
      };
      greyRelationalWeights.value = [];
    }
  } else if (nodeAnalysisMethod.value === 'DareMethod') {
    // 尝试从本地存储加载已保存的数据
    const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    if (savedDetails.dareCoefficients && savedDetails.dareCoefficientPairs) {
      dareCoefficients.value = savedDetails.dareCoefficients;
      dareCoefficientPairs.value = savedDetails.dareCoefficientPairs;
      dareWeights.value = savedDetails.dareWeights || [];
    } else {
      // 初始化环比系数对和系数数组
      dareCoefficientPairs.value = [];
      dareCoefficients.value = [];
      for (let i = 1; i < children.length; i++) {
        const prevChild = children[i - 1];
        const currChild = children[i];
        dareCoefficientPairs.value.push(`${currChild.label} 比 ${prevChild.label}`);
        dareCoefficients.value.push(0.1); // 默认系数为0.1
      }
      dareWeights.value = [];
    }
  } else if (nodeAnalysisMethod.value === 'FactorAnalysis') {
    // 尝试从本地存储加载已保存的数据
    const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    if (savedDetails.factorData) {
      factorData.value = savedDetails.factorData;
      factorWeights.value = savedDetails.factorWeights || [];
    } else {
      // 初始化因子分析数据
      factorData.value = {
        data_list: children.map(() => [0])
      };
      factorWeights.value = [];
    }
  } else if (nodeAnalysisMethod.value === 'PcaWeight') {
    // 尝试从本地存储加载已保存的数据
    const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    if (savedDetails.pcaData) {
      pcaData.value = savedDetails.pcaData;
      pcaWeights.value = savedDetails.pcaWeights || [];
    } else {
      // 初始化主成分分析数据
      pcaData.value = {
        data_list: children.map(() => [0])
      };
      pcaWeights.value = [];
    }
  }

  showWeightAllocationDialog.value = true
}

const calculateTotalWeight = () => {
  const children = getChildNodes(selectedNode.value?.id)
  return children.reduce((total, child) => {
    return total + (percentageWeights.value[child.id] || 0)
  }, 0)
}

const handleMatrixInput = (rowIndex, colIndex, value) => {
  if (rowIndex === colIndex) return; // 忽略对角线元素
  
  // 解析输入值，可以是分数如"1/3"或小数如"0.333"
  let numValue;
  if (typeof value === 'string' && value.includes('/')) {
    const [numerator, denominator] = value.split('/').map(Number);
    if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
      numValue = numerator / denominator;
    } else {
      ElMessage.error('请输入有效的分数格式，如1/3');
      return;
    }
  } else {
    numValue = Number(value);
    if (isNaN(numValue)) {
      numValue = 1;
    } else if (numValue <= 0) {
      numValue = 1;
      ElMessage.error('请输入有效参数，数值应在0到100之间');
    } else if (numValue >= 100) {
      numValue = 100;
      ElMessage.error('请输入有效参数，数值应在0到100之间');
    }
    // 更新当前值
    ahpMatrix.value[rowIndex][colIndex] = numValue;
  }
  
  // 更新当前位置的值为数值
  ahpMatrix.value[rowIndex][colIndex] = numValue;
  
  // 计算倒数并更新对应位置
 const reciprocal = 1 / numValue;
  ahpMatrix.value[colIndex][rowIndex] = reciprocal;
};

// 灰色关联分析法相关方法
const addGreyDataRow = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择节点');
    return;
  }
  const children = getChildNodes(selectedNode.value.id)
  if (children.length > 0) {
    greyRelationalData.value.data_list.push(new Array(children.length).fill(0))
  } else {
    ElMessage.warning('当前节点没有子节点');
  }
}

// 因子分析和主成分分析相关方法
const addFactorDataRow = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择节点');
    return;
  }
  const children = getChildNodes(selectedNode.value.id)
  if (children.length > 0) {
    if (nodeAnalysisMethod.value === 'FactorAnalysis') {
      factorData.value.data_list.push(new Array(1).fill(0))
    } else if (nodeAnalysisMethod.value === 'PcaWeight') {
      pcaData.value.data_list.push(new Array(1).fill(0))
    }
  } else {
    ElMessage.warning('当前节点没有子节点');
  }
}

const deleteFactorDataRow = () => {
  if (nodeAnalysisMethod.value === 'FactorAnalysis' && factorData.value.data_list.length > 1) {
    factorData.value.data_list.pop()
  } else if (nodeAnalysisMethod.value === 'PcaWeight' && pcaData.value.data_list.length > 1) {
    pcaData.value.data_list.pop()
  } else {
    ElMessage.warning('至少保留一行数据');
  }
}

const handleFactorDataChange = (method, rowIndex, colIndex, value) => {
  let num = Number(value);

  if (isNaN(num)) {
    num = 0;
  } else if (num < 0) {
    num = 0;
    ElMessage.warning('输入值不能小于0，已自动调整为0');
  } else if (num > 100) {
    num = 100;
    ElMessage.warning('输入值不能大于100，已自动调整为100');
  }

  if (method === 'FactorAnalysis') {
    factorData.value.data_list[rowIndex][colIndex] = num;
  } else if (method === 'PcaWeight') {
    pcaData.value.data_list[rowIndex][colIndex] = num;
  }
};

const deleteGreyDataRow = () => {
  if (greyRelationalData.value.data_list.length > 0) {
    greyRelationalData.value.data_list.pop()
  }
}

const handleGreyDataChange = (rowIndex, colIndex, value) => {
  // 确保值是数字
  let numValue = Number(value);
  // 限制在0-100范围内
  if (isNaN(numValue)) {
    numValue = 0;
  } else if (numValue < 0) {
    numValue = 0;
  } else if (numValue > 100) {
    numValue = 100;
  }
  // 更新数据
  greyRelationalData.value.data_list[rowIndex][colIndex] = numValue;
};

const handleDareCoefficientInput = (index) => {
  let val = Number(dareCoefficients.value[index]);

  if (isNaN(val) || val < 0) {
    dareCoefficients.value[index] = 0;
  } else if (val > 100) {
    dareCoefficients.value[index] = 100;
    ElMessage.warning('环比系数不能大于100，已自动调整为100');
  } else {
    dareCoefficients.value[index] = Math.round(val * 100) / 100; // 保留两位小数
  }
};

const calculateGreyRelationalWeights = async () => {
  if (!selectedNode.value) return;

  calculatingWeights.value = true;
  try {
    // 发送灰色关联分析数据到后端API
    // 将index_types对象转换为数组
    const indexTypesArray = greyRelationalData.value.index_types;
    const response = await computeGreyRelational({
      rho: greyRelationalData.value.rho,
      index_types: indexTypesArray,
      data_list: greyRelationalData.value.data_list
    })

    console.log('灰色关联分析权重计算结果:', response)

    if (response.code === 1) {
      // 格式化权重结果
      greyRelationalWeights.value = response.data.map((weight, index) => ({
        nodeId: getChildNodes(selectedNode.value.id)[index].id,
        nodeLabel: getChildNodes(selectedNode.value.id)[index].label,
        weight: weight
      }));

      // 保存到本地存储
      const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
      nodeDetailsStorage.value[selectedNode.value.id] = {
        ...existingDetails,
        greyRelationalWeights: greyRelationalWeights.value,
        greyRelationalData: greyRelationalData.value
      };

      localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
      ElMessage.success('灰色关联分析权重计算成功');
    } else {
      ElMessage.error('权重计算失败: ' + (response.msg || '未知错误'));
    }
  } finally {
    calculatingWeights.value = false;
  }
}

const calculateAhpWeights = async () => {
  if (!selectedNode.value) return;
  
  calculatingWeights.value = true;
  try {
    // 发送矩阵数据到后端API
    const response = await computeAph({
      data_list: ahpMatrix.value,
    })
    console.log(response.code === 1)
    if (response.code === 1) {
      // 格式化权重结果
      console.log(111, response.data)
      ahpWeights.value = response.data.map((weight, index) => ({
        nodeId: getChildNodes(selectedNode.value.id)[index].id,
        nodeLabel: getChildNodes(selectedNode.value.id)[index].label,
        weight: weight
      }));
      
      // 保存到本地存储
      const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
      nodeDetailsStorage.value[selectedNode.value.id] = {
        ...existingDetails,
        ahpWeights: ahpWeights.value,
        ahpMatrix: ahpMatrix.value
      };
      
      localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
      ElMessage.success('权重计算成功');
    } else {
      ElMessage.error('权重计算失败: ' + (response.msg || '未知错误'));
    }
  } finally {
    calculatingWeights.value = false;
  }
};

const calculateDareWeights = async () => {
  if (!selectedNode.value) return;
  
  calculatingWeights.value = true;
  try {
    // 发送环比系数数据到后端API
    const response = await computeDare({
      data_list: dareCoefficients.value
    })
    
    if (response.code === 1) {
      // 格式化权重结果
      dareWeights.value = response.data.map((weight, index) => ({
        nodeId: getChildNodes(selectedNode.value.id)[index].id,
        nodeLabel: getChildNodes(selectedNode.value.id)[index].label,
        weight: weight
      }));
      
      // 保存到本地存储
      const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
      nodeDetailsStorage.value[selectedNode.value.id] = {
        ...existingDetails,
        dareWeights: dareWeights.value,
        dareCoefficients: dareCoefficients.value,
        dareCoefficientPairs: dareCoefficientPairs.value
      };
      
      localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
      ElMessage.success('环比系数法权重计算成功');
    } else {
      ElMessage.error('权重计算失败: ' + (response.msg || '未知错误'));
    }
  } finally {
    calculatingWeights.value = false;
  }
};

const calculateFactorWeights = async () => {
  if (!selectedNode.value) return;
  
  calculatingWeights.value = true;
  try {
    // 发送因子分析数据到后端API
    const response = await computeFactor({
      data_list: factorData.value.data_list
    })
    
    if (response.code === 1) {
      // 格式化权重结果
      factorWeights.value = response.data.map((weight, index) => ({
        nodeId: getChildNodes(selectedNode.value.id)[index].id,
        nodeLabel: getChildNodes(selectedNode.value.id)[index].label,
        weight: weight
      }));
      
      // 保存到本地存储
      const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
      nodeDetailsStorage.value[selectedNode.value.id] = {
        ...existingDetails,
        factorWeights: factorWeights.value,
        factorData: factorData.value
      };
      
      localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
      ElMessage.success('因子分析法权重计算成功');
    } else {
      ElMessage.error('权重计算失败: ' + (response.msg || '未知错误'));
    }
  } finally {
    calculatingWeights.value = false;
  }
};

const calculatePcaWeights = async () => {
  if (!selectedNode.value) return;
  
  calculatingWeights.value = true;
  try {
    // 发送主成分分析数据到后端API
    const response = await computePca({
      data_list: pcaData.value.data_list
    })
    
    if (response.code === 1) {
      // 格式化权重结果
      pcaWeights.value = response.data.map((weight, index) => ({
        nodeId: getChildNodes(selectedNode.value.id)[index].id,
        nodeLabel: getChildNodes(selectedNode.value.id)[index].label,
        weight: weight
      }));
      
      // 保存到本地存储
      const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
      nodeDetailsStorage.value[selectedNode.value.id] = {
        ...existingDetails,
        pcaWeights: pcaWeights.value,
        pcaData: pcaData.value
      };
      
      localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
      ElMessage.success('主成分分析法权重计算成功');
    } else {
      ElMessage.error('权重计算失败: ' + (response.msg || '未知错误'));
    }
  } finally {
    calculatingWeights.value = false;
  }
};

const saveWeightAllocation = () => {
  console.log('saveWeightAllocation', childWeights.value)
  if (nodeAnalysisMethod.value === 'ahp') {
    // 保存AHP矩阵数据到本地
    if (!nodeDetailsStorage.value[selectedNode.value.id]) {
      nodeDetailsStorage.value[selectedNode.value.id] = {}
    }
    nodeDetailsStorage.value[selectedNode.value.id].ahpMatrix = [...ahpMatrix.value]
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value))
    showWeightAllocationDialog.value = false
    ElMessage.success('AHP矩阵数据已保存')
  } else if (nodeAnalysisMethod.value === 'EntropyWeight' || nodeAnalysisMethod.value === 'CoefficientMethod') {
    // 保存矩阵数据到本地
    if (!nodeDetailsStorage.value[selectedNode.value.id]) {
      nodeDetailsStorage.value[selectedNode.value.id] = {}
    }
    const methodKey = nodeAnalysisMethod.value;
    nodeDetailsStorage.value[selectedNode.value.id][methodKey + 'MatrixData'] = [...methodMatrixData.value];
    nodeDetailsStorage.value[selectedNode.value.id][methodKey + 'Weights'] = [...methodWeights.value];
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value))
    showWeightAllocationDialog.value = false
    ElMessage.success('权重分析数据已保存')
  } else if (nodeAnalysisMethod.value === 'GreyRelationalAnalysis') {
    // 保存灰色关联分析数据到本地
    if (!nodeDetailsStorage.value[selectedNode.value.id]) {
      nodeDetailsStorage.value[selectedNode.value.id] = {}
    }
    nodeDetailsStorage.value[selectedNode.value.id].greyRelationalData = {
      ...greyRelationalData.value,
      data_list: [...greyRelationalData.value.data_list],
      index_types: [...greyRelationalData.value.index_types]
    };
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value))
    showWeightAllocationDialog.value = false
    ElMessage.success('灰色关联分析数据已保存')
  } else if (nodeAnalysisMethod.value === 'DareMethod') {
    // 保存环比系数法数据到本地
    if (!nodeDetailsStorage.value[selectedNode.value.id]) {
      nodeDetailsStorage.value[selectedNode.value.id] = {}
    }
    nodeDetailsStorage.value[selectedNode.value.id].dareCoefficients = [...dareCoefficients.value];
    nodeDetailsStorage.value[selectedNode.value.id].dareCoefficientPairs = [...dareCoefficientPairs.value];
    nodeDetailsStorage.value[selectedNode.value.id].dareWeights = [...dareWeights.value];
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
    showWeightAllocationDialog.value = false;
    ElMessage.success('环比系数法数据已保存');
  } else if (nodeAnalysisMethod.value === 'FactorAnalysis') {
    // 保存因子分析法数据到本地
    if (!nodeDetailsStorage.value[selectedNode.value.id]) {
      nodeDetailsStorage.value[selectedNode.value.id] = {}
    }
    nodeDetailsStorage.value[selectedNode.value.id].factorData = {
      ...factorData.value,
      data_list: [...factorData.value.data_list]
    };
    nodeDetailsStorage.value[selectedNode.value.id].factorWeights = [...factorWeights.value];
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
    showWeightAllocationDialog.value = false;
    ElMessage.success('因子分析法数据已保存');
  } else if (nodeAnalysisMethod.value === 'PcaWeight') {
    // 保存主成分分析法数据到本地
    if (!nodeDetailsStorage.value[selectedNode.value.id]) {
      nodeDetailsStorage.value[selectedNode.value.id] = {}
    }
    nodeDetailsStorage.value[selectedNode.value.id].pcaData = {
      ...pcaData.value,
      data_list: [...pcaData.value.data_list]
    };
    nodeDetailsStorage.value[selectedNode.value.id].pcaWeights = [...pcaWeights.value];
    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
    showWeightAllocationDialog.value = false;
    ElMessage.success('主成分分析法数据已保存');
  } else {
    const total = calculateTotalWeight()
    if (Math.abs(total - 100) > 0.1) {
      ElMessage.warning('权重总和应为100%')
      return
    }

    // 保存权重数据
    nodeDetailsStorage.value[selectedNode.value.id] = {
      ...nodeDetailsStorage.value[selectedNode.value.id],
      childWeights: childWeights.value
    }

    showWeightAllocationDialog.value = false
    ElMessage.success('权重分析已保存')
  }
}

const addParameter = () => {
  if (!newParameter.name || !newParameter.alias) {
    ElMessage.warning('请填写完整的参数信息')
    return
  }
  
  const newId = `param-${Date.now()}`
  parameterList.value.push({
    id: newId,
    name: newParameter.name,
    alias: newParameter.alias
  })
  
  newParameter.name = ''
  newParameter.alias = ''
  showAddParameterDialog.value = false
  ElMessage.success('参数添加成功')
}

const deleteParameter = (id) => {
  parameterList.value = parameterList.value.filter(p => p.id !== id)
  ElMessage.success('参数删除成功')
}

// 在现有的响应式数据声明后添加
const showDataSourceDialog = ref(false)
const currentParameter = ref(null)

// 数据源绑定表单数据
const dataSourceForm = reactive({
  InferentialListValue: '',
  dataSource: '',
  filterConditions: [
    {
      field: '',
      operator: '',
      value: ''
    }
  ],
  resultType: '',
  percentageCondition: ''
})
const dataSourceList = ref(null)
const InferentialList = ref(null)
const bindDataSource = async(parameter) => {
  currentParameter.value = parameter
  showDataSourceDialog.value = true
  const data = {
    page: 1,
    num: 10,
    name: '',
    collect_id: selectedWorkflowType.value
  }
  const res = await getInferentialList(data)
  InferentialList.value = res.data.info
  
  // 从本地存储加载已保存的数据源配置
  const savedDetails = nodeDetailsStorage.value[selectedNode.value?.id] || {}
  const savedDataSources = savedDetails.dataSources || {}
  const savedConfig = savedDataSources[parameter.id]
  
  if (savedConfig) {
    // 恢复已保存的配置
    Object.assign(dataSourceForm, savedConfig)
    await getDictList(dataSourceForm.InferentialListValue).then(res => {
    dataSourceList.value = res.data.info.map(item => ({
      label: item.col_name,
      type: item.col_type,
      value: item.id
    }))
  })
  } else {
    // 重置为默认值
    Object.assign(dataSourceForm, {
      InferentialListValue: '',
      dataSource: '',
      filterConditions: [
        {
          field: '',
          operator: '',
          value: ''
        }
      ],
      resultType: '',
      percentageCondition: ''
    })
  }
}

const handleInferentialListChange = async() => {
  await getDictList(dataSourceForm.InferentialListValue).then(res => {
    dataSourceList.value = res.data.info.map(item => ({
      label: item.col_name,
      type: item.col_type,
      value: item.id
    }))
  })
}

// 添加筛选条件
const addFilterCondition = () => {
  dataSourceForm.filterConditions.push({
    field: '',
    operator: '',
    value: ''
  })
}

// 删除筛选条件
const removeFilterCondition = (index) => {
  if (dataSourceForm.filterConditions.length > 1) {
    dataSourceForm.filterConditions.splice(index, 1)
  }
}

// 保存数据源绑定
const saveDataSourceBinding = () => {
  if (!currentParameter.value || !selectedNode.value) {
    ElMessage.warning('参数或节点信息缺失')
    return
  }
  
  if (!dataSourceForm.dataSource) {
    ElMessage.warning('请选择数据源')
    return
  }
  
  if (!dataSourceForm.resultType) {
    ElMessage.warning('请选择结果取值方式')
    return
  }
  
  // 验证筛选条件
  for (let condition of dataSourceForm.filterConditions) {
    if (!condition.field || !condition.operator) {
      ElMessage.warning('请完善筛选条件')
      return
    }
    
    // 检查需要值的操作符
    const needsValue = !['is_null', 'is_not_null'].includes(condition.operator)
    if (needsValue && !condition.value) {
      ElMessage.warning('请填写筛选条件的值')
      return
    }
  }
  
  // 如果选择统计占比，检查占比条件
  if (dataSourceForm.resultType === 'get_percentage' && !dataSourceForm.percentageCondition) {
    ElMessage.warning('请输入统计占比条件')
    return
  }
  
  // 获取当前节点的详细信息
  const savedDetails = nodeDetailsStorage.value[selectedNode.value.id] || {}
  
  // 初始化数据源配置对象
  if (!savedDetails.dataSources) {
    savedDetails.dataSources = {}
  }
  
  // 保存当前参数的数据源配置
  savedDetails.dataSources[currentParameter.value.id] = {
    InferentialListValue: dataSourceForm.InferentialListValue,
    dataSource: dataSourceForm.dataSource,
    filterConditions: [...dataSourceForm.filterConditions],
    resultType: dataSourceForm.resultType,
    percentageCondition: dataSourceForm.percentageCondition,
    updateTime: Date.now()
  }
  
  // 保存到本地存储
  saveNodeDetailsToLocal(selectedNode.value.id, savedDetails)
  
  showDataSourceDialog.value = false
  ElMessage.success('数据源绑定已保存')
}

const getOperatorsByFieldType = (fieldValue) => {
  const field = dataSourceList.value?.find(item => item.value === fieldValue);
  if (!field) return [];
  
  const type = field.type;
  const operators = [
    { label: '等于', value: 'equals' },
    { label: '不等于', value: 'not_equals' },
    { label: '大于', value: 'greater_than' },
    { label: '小于', value: 'less_than' },
    { label: '大于等于', value: 'greater_equal' },
    { label: '小于等于', value: 'less_equal' },
    { label: '包含', value: 'contains' },
    { label: '不包含', value: 'not_contains' },
    { label: '为空', value: 'is_null' },
    { label: '不为空', value: 'is_not_null' }
  ];
  
  switch(type) {
    case 'int':
    case 'float':
      return operators.filter(op => !['contains', 'not_contains'].includes(op.value));
    case 'string':
      return operators.filter(op => 
        ['equals', 'not_equals', 'contains', 'not_contains', 'is_null', 'is_not_null'].includes(op.value)
      );
    case 'boolean':
      return operators.filter(op => ['equals', 'not_equals'].includes(op.value));
    case 'date':
      return operators.filter(op => !['contains', 'not_contains'].includes(op.value));
    default:
      return operators;
  }
};

const handleFieldChange = (condition) => {
  const allowedOperators = getOperatorsByFieldType(condition.field);
  if (!allowedOperators.some(op => op.value === condition.operator)) {
    condition.operator = '';
  }
};

const saveParameterConfig = () => {
  const alg = normalizationAlgorithm.value;
  if (alg === 'linear_mapping') {
      const { x_min, x_max } = normalizationParams;
      if (x_max <= x_min) {
        ElMessage.error('最大值必须大于最小值！');
        return;
      }
    }
  /* 1. 线性/台阶分段函数：必须严格递增 */
  if (
    alg === 'segmentation_liner_mapping' ||
    alg === 'segmentation_mapping'
  ) {
    const { x_list } = normalizationParams;

    for (let i = 1; i < x_list.length; i++) {
      if (x_list[i] <= x_list[i - 1]) {
        ElMessage.error('x 行必须为严格递增序列！');
        return;
      }
    }
  }

  /* 2. 其它原有保存逻辑 … */
  showParameterConfigDialog.value = false;
  ElMessage.success('参数配置已保存');
};

// Lifecycle
onMounted(() => {
  nextTick(async() => {
    // 加载基础指标
    await basicTreeDataSearch()
    await getBasicData()
    await getInferentialData()
    await getInitialData()
  })
})

const currentAlgorithmType = computed(() => {
  const options = [
    { value: 'gaussian_mapping', type: 'minmax' },
    { value: 'cauchy_mapping', type: 'minmax' },
    { value: 'exponential_decay', type: 'minmax' },
    { value: 'logistic_variant', type: 'minmax' },
    { value: 'linear_segment', type: 'minmax' },
    { value: 'zscore', type: 'zscore' },
    { value: 'decimal', type: 'decimal' },
    { value: 'linear_segment', type: 'linear_segment' },
    { value: 'linear_mapping', type: 'linear_mapping' },
    { value: 'zero_one_mapping', type: 'zero_one_mapping' },
    { value: 'segmentation_liner_mapping', type: 'segmentation_liner_mapping' },
    { value: 'segmentation_mapping', type: 'segmentation_mapping' },
  ];
  
  const selectedOption = options.find(option => option.value === normalizationAlgorithm.value);
  return selectedOption ? selectedOption.type : 'minmax';
});
// 模糊矩阵相关数据
const showFuzzyMatrixDialog = ref(false)
const fuzzyMatrixData = ref([])
const scoreSegments = ref([20, 40, 60, 80])

// 通用权重分析数据
const methodMatrixData = ref([])
const methodWeights = ref([])


// 初始化模糊矩阵数据
const initFuzzyMatrix = () => {
  showFuzzyMatrixDialog.value = true
  // 获取当前选中节点的子节点
  if(nodeDetailsStorage.value[selectedNode.value.id].fuzzyMatrixData) {
    fuzzyMatrixData.value = nodeDetailsStorage.value[selectedNode.value.id].fuzzyMatrixData
    scoreSegments.value = nodeDetailsStorage.value[selectedNode.value.id].scoreSegments
  } else {
    const children = getChildNodes(selectedNode.value.id)
    fuzzyMatrixData.value = children.map(child => ({
      nodeId: child.id,
      nodeName: child.label,
      values: new Array(scoreSegments.value.length).fill(0)
    }))
  } 
}

// 处理矩阵值变化
const handleMatrixValueChange = (rowIndex, colIndex) => {
  const currentValue = fuzzyMatrixData.value[rowIndex].values[colIndex]
  // 确保值在0-100之间
  if (currentValue < 0) {
    fuzzyMatrixData.value[rowIndex].values[colIndex] = 0
  } else if (currentValue > 100) {
    fuzzyMatrixData.value[rowIndex].values[colIndex] = 100
  }
}

// 处理分数分段变化
const handleScoreSegmentChange = (index) => {
  const currentValue = scoreSegments.value[index]
  const prevIndex = index - 1
  const nextIndex = index + 1

  // 确保值在0-100之间
  if (currentValue < 0) {
    scoreSegments.value[index] = 0
  } else if (currentValue > 100) {
    scoreSegments.value[index] = 100
  }

  // 确保分数分段递增
  if (prevIndex >= 0) {
    if (scoreSegments.value[index] < scoreSegments.value[prevIndex]) {
      scoreSegments.value[index] = scoreSegments.value[prevIndex]
    }
  }

  if (nextIndex < scoreSegments.value.length) {
    if (scoreSegments.value[index] > scoreSegments.value[nextIndex]) {
      scoreSegments.value[nextIndex] = scoreSegments.value[index]
    }
  }

  // 更新矩阵列数
  fuzzyMatrixData.value.forEach(row => {
    if (row.values.length < scoreSegments.value.length) {
      // 添加新列
      const newLength = scoreSegments.value.length
      const lastValue = row.values[row.values.length - 1] || 0
      while (row.values.length < newLength) {
        row.values.push(lastValue)
      }
    } else if (row.values.length > scoreSegments.value.length) {
      // 移除多余的列
      row.values.splice(scoreSegments.value.length)
    }
  })
}

// 添加矩阵列
const addMethodMatrixColumn = () => {
  // 为每行添加新参数
  methodMatrixData.value.forEach(row => {
    row.row_list.push(row.row_list[row.row_list.length - 1] || 0)
  })
  console.log('添加矩阵列', methodMatrixData.value)
}

// 删除矩阵列
const delMethodMatrixColumn = () => {
  methodMatrixData.value.forEach(row => {
    row.row_list.splice(row.row_list.length - 1, 1)
  })
}

// 矩阵值变化处理
const handleMatrixChange = (row, colIndex) => {
  const currentValue = row.row_list[colIndex]
  // 确保值在0-100之间
  if (currentValue < 0) {
    row.row_list[colIndex] = 0
  } else if (currentValue > 100) {
    row.row_list[colIndex] = 100
  }
}

// 计算权重
const calculateMethodWeights = async () => {
  if (!selectedNode.value) return;
  console.log('计算权重', methodMatrixData.value)
  methodMatrixData.value = methodMatrixData.value.map((item,index) => {
    return {
      code: index + 1,
      name: item.name,
      row_list: item.row_list
    }
  });
  calculatingWeights.value = true;
  try {
    const methodKey = nodeAnalysisMethod.value === 'EntropyWeight' ? 'entropy' : 'coefficient';
    let res;
    if(nodeAnalysisMethod.value === 'EntropyWeight') {
      res = await computeEntropy({data_list: methodMatrixData.value});
    } else {
      res = await computeCoefficient({data_list: methodMatrixData.value});
    }
    methodWeights.value = res.data.map((item, index) => {
      return {
        weight: item.weight,
        nodeId: item.code,
        nodeLabel: methodMatrixData.value[index].name
      }
    }) 

    // 保存到本地存储
    const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
    nodeDetailsStorage.value[selectedNode.value.id] = {
      ...existingDetails,
      [`${methodKey}Weights`]: methodWeights.value
    };

    localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
    ElMessage.success('权重计算成功');
  } finally {
    calculatingWeights.value = false;
  }
};

// 添加矩阵列
const addMatrixColumn = () => {
  const newIndex = scoreSegments.value.length
  // 设置新分段的默认值为前一个分段的值或100
  const defaultValue = newIndex > 0 ? scoreSegments.value[newIndex - 1] : 10
  scoreSegments.value.push(defaultValue)

  // 为每行添加新参数
  fuzzyMatrixData.value.forEach(row => {
    row.values.push(row.values[row.values.length - 1] || 0)
  })
  console.log('添加矩阵列', scoreSegments.value, fuzzyMatrixData.value)
}
// 删除矩阵列
const delMatrixColumn = () => {
  scoreSegments.value.splice(scoreSegments.value.length - 1, 1)
  fuzzyMatrixData.value.forEach(row => {
    row.values.splice(row.values.length - 1, 1)
  })
}

// 保存配置
const saveFuzzyMatrixConfig = () => {
  /* 1. 校验分数分段是否严格单调递增 */
  for (let i = 1; i < scoreSegments.value.length; i++) {
    if (scoreSegments.value[i] <= scoreSegments.value[i - 1]) {
      ElMessage.error('分数分段必须为严格递增序列！');
      return; // 阻断保存
    }
  }

  /* 2. 原有逻辑继续执行 */
  const existingDetails = nodeDetailsStorage.value[selectedNode.value.id] || {};
  nodeDetailsStorage.value[selectedNode.value.id] = {
    ...existingDetails,
    scoreSegments: [...scoreSegments.value],
    fuzzyMatrixData: JSON.parse(JSON.stringify(fuzzyMatrixData.value))
  };

  localStorage.setItem('node-details', JSON.stringify(nodeDetailsStorage.value));
  showFuzzyMatrixDialog.value = false;
  ElMessage.success('配置保存成功');
};

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('click', hideContextMenu)
  document.removeEventListener('mousemove', handlePanMove)
  document.removeEventListener('mouseup', handlePanEnd)
})
</script>

<style scoped>
.scale-meaning-box {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  color: #fff;
}

.scale-title {
  font-size: 16px;
  margin-bottom: 12px;
  color: #409EFF;
  font-weight: bold;
}

.scale-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  margin-bottom: 15px;
}

.scale-item {
  display: flex;
  align-items: center;
  min-width: 280px;
}

.scale-number {
  display: inline-block;
  width: 24px;
  height: 24px;
  background-color: #409EFF;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  margin-right: 8px;
  font-weight: bold;
}

.scale-desc {
  font-size: 14px;
}

.scale-note {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
}

.scale-note p {
  margin: 5px 0;
}

/* 直接赋值法样式 */
.direct-weight-container {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
}

.direct-weight-title {
  color: #409EFF;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: bold;
}

.direct-weight-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.direct-weight-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  color: #fff;
}

.weight-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.percent-sign {
  color: #fff;
}

.workflow-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.left-sidebar {
  display: flex;
  flex-direction: column;
  width: 360px;
  background: white;
  border-right: 1px solid #e8e8e8;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.metrics-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.metric-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #f0f0f0;
  overflow: auto;
}

.metric-section:last-child {
  border-bottom: none;
}

.section-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.tree-container {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;
  border: 2px solid transparent;
  position: relative;
}

.tree-node:hover {
  background: #f0f9ff;
  border-color: #91caff;
}

.tree-node:active {
  cursor: grabbing;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}

.node-actions {
  opacity: 0;
  display: flex;
  gap: 4px;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.node-type-badge {
  font-size: 10px;
  border-radius: 10px;
  background: #e6f7ff;
  color: #1890ff;
  flex-shrink: 0;
}

.node-type-badge.custom {
  background: #f6ffed;
  color: #52c41a;
}

.center-area {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  background: white;
  margin: 0 1px;
  position: relative;
  transition: all 0.3s;
}

.center-area.drag-over {
  background: #f0f9ff;
  border: 2px dashed #40a9ff;
}

.flowchart-header {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zoom-level {
  min-width: 50px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.canvas-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  cursor: grab;
}

.canvas-wrapper:active {
  cursor: grabbing;
}

.canvas-container {
  width: 1000%;
  height: 1000vh;
  position: relative;
  background: radial-gradient(circle, #e0e0e0 1px, transparent 1px);
  background-size: 20px 20px;
  transition: transform 0.1s ease-out;
}

.snap-guide {
  position: absolute;
  pointer-events: none;
  z-index: 10;
}

.snap-guide.vertical {
  width: 1px;
  height: 100%;
  background: #ff4d4f;
  box-shadow: 0 0 2px rgba(255, 77, 79, 0.5);
}

.snap-guide.horizontal {
  width: 100%;
  height: 1px;
  background: #ff4d4f;
  box-shadow: 0 0 2px rgba(255, 77, 79, 0.5);
}

.flow-node {
  position: absolute;
  width: 140px;
  height: 60px;
  background: #91caff;
  border: 2px solid #40a9ff;
  border-radius: 6px;
  cursor: move;
  user-select: none;
  transition: all 0.2s;
}

.flow-node.base-metric {
  background: #e6f7ff;
  border-color: #1890ff;
}

.flow-node.custom-metric {
  background: #f6ffed;
  border-color: #52c41a;
}

.flow-node.connecting {
  border-color: #52c41a;
  box-shadow: 0 0 0 2px rgba(82, 196, 26, 0.2);
}

.flow-node.connectable {
  border-color: #faad14;
  cursor: crosshair;
}

.flow-node.connectable:hover {
  border-color: #fa8c16;
  box-shadow: 0 0 0 2px rgba(250, 173, 20, 0.2);
}

.flow-node.connection-invalid {
  border-color: #ff4d4f;
  cursor: not-allowed;
}

.flow-node.connection-invalid:hover {
  box-shadow: 0 0 0 2px rgba(255, 77, 79, 0.2);
}

.flow-node.has-parent {
  border-left: 4px solid #52c41a;
}

.flow-node:hover {
  box-shadow: 0 4px 12px rgba(64, 169, 255, 0.3);
}

.flow-node.selected {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.node-content {
  padding: 0 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.node-title {
  font-size: 13px;
  font-weight: 500;
  color: #000;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-type {
  font-size: 11px;
  color: #666;
  margin-top: 2px;
}

.metric-type-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.metric-type-indicator.base {
  color: #1890ff;
}

.metric-type-indicator.custom {
  color: #52c41a;
}

.node-handles {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 100%;
  pointer-events: none;
}

.handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #40a9ff;
  border: 2px solid white;
  border-radius: 50%;
  cursor: crosshair;
  pointer-events: all;
  transition: all 0.2s;
}

.handle:hover {
  transform: scale(1.5);
  background: #1890ff;
}

.handle.active {
  background: #52c41a;
  transform: scale(1.5);
}

.handle.disabled {
  background: #ff4d4f;
  cursor: not-allowed;
}

.handle.disabled:hover {
  background: #ff7875;
  transform: scale(1.2);
}

.handle-left {
  left: -6px;
}

.handle-right {
  right: -6px;
}

.edges-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.edge-path {
  cursor: pointer;
  pointer-events: all;
  transition: all 0.2s;
}

.edge-path:hover {
  stroke-width: 3 !important;
  stroke: #1890ff !important;
}

.edge-click-area {
  cursor: pointer;
  pointer-events: all;
}

.instructions {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: left;
  color: #666;
  pointer-events: none;
  z-index: 5;
}

.instruction-content {
  background: rgba(255, 255, 255, 0.9);
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.instruction-content h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.instruction-content ul {
  margin: 0;
  padding-left: 20px;
}

.instruction-content li {
  margin-bottom: 8px;
}

.instruction-content li strong {
  color: #1890ff;
}

.properties-drawer {
  z-index: 1000;
}

.properties-content {
  padding: 20px;
}

.coordinate-inputs {
  display: flex;
  justify-content: space-between;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 120px;
}

.menu-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background: #f5f5f5;
}

.menu-item:first-child {
  border-radius: 4px 4px 0 0;
}

.menu-item:last-child {
  border-radius: 0 0 4px 4px;
}

.warning-content {
  padding: 16px 0;
  color: #fff;
}

.warning-content p {
  margin: 8px 0;
  line-height: 1.5;
}

.warning-content strong {
  color: #1890ff;
}

/* Animation for drag feedback */
@keyframes dragPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.tree-node[draggable="true"]:active {
  animation: dragPulse 0.3s ease-in-out;
}

.formula-section {
  border: 1px solid #133b48;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  background: #195877;
}

.parameter-table {
  width: 100%;
}

.normalization-section {
  display: flex;
  align-items: center;
}

.weight-allocation-content {
  padding: 16px 0;
}

.weight-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.weight-item:last-child {
  border-bottom: none;
}

.child-name {
  flex: 1;
  font-weight: 500;
  margin-right: 10px;
}

.weight-total {
  text-align: right;
  padding-top: 16px;
  color: #fff;
}

.parameter-config-content {
  padding: 16px 0;
}

.data-source-content {
  padding: 16px 0;
}

.filter-conditions {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.condition-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.condition-row:last-child {
  margin-bottom: 0;
}

.result-calculation {
  display: flex;
  align-items: center;
}

.mt-2 {
  margin-top: 8px;
}

/* 列表容器样式 */
.list-container {
  margin-top: 10px;
}

.list-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

/* 表格容器样式 */
.table-container {
  margin-top: 10px;
  overflow-x: auto;
}

/* 参数表格样式 */
.parameter_table {
  width: 100%;
  border-collapse: collapse;
}

.parameter_table th,
.parameter_table td {
  padding: 10px;
  text-align: center;
  border: 1px solid #133b48;
  color: #fff;
}

.parameter_table th {
  background-color: #050b0d;
  font-weight: 500;
  color: #fff;
}

.parameter_table tbody tr:nth-child(odd) {
  background-color: #050b0d;
  color: #fff;
}

.parameter_table tbody tr:nth-child(even) {
  background-color: #050b0d;
  color: #fff;
}
</style>
