<template>
  <div class="workflow-container">
    <!-- 左侧指标库 -->
    <div class="left-sidebar">
      <div class="sidebar-header">
        <h3>指标库</h3>
        <div class="header-actions">
          <el-button size="small" @click="refreshBaseMetrics">刷新</el-button>
        </div>
      </div>
      
      <div class="metrics-container">
        <!-- 基础指标 -->
        <div class="metric-section">
          <div class="section-header">
            <span class="section-title">基础指标</span>
          </div>
          <div class="tree-container">
            <el-tree
              ref="baseMetricTree"
              :data="baseMetrics"
              node-key="id"
              default-expand-all
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <span class="node-label">{{ data.label }}</span>
                  <el-tag class="node-type-badge" size="small">基础</el-tag>
                </div>
              </template>
            </el-tree>
          </div>
        </div>
        
        <!-- 自定义指标 -->
        <div class="metric-section">
          <div class="section-header">
            <span class="section-title">自定义指标</span>
          </div>
          <div class="tree-container">
            <el-tree
              ref="customMetricTree"
              :data="customMetrics"
              node-key="id"
              default-expand-all
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <span class="node-label">{{ data.label }}</span>
                  <el-tag class="node-type-badge custom" size="small">自定义</el-tag>
                </div>
              </template>
            </el-tree>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 中间画布区域 -->
    <div 
      class="center-area"
      @dragover="handleDragOver"
      @drop="handleDrop"
      @mousedown="handleCanvasMouseDown"
      @mousemove="handleCanvasMouseMove"
      @mouseup="handleCanvasMouseUp"
      @wheel="handleWheel"
    >
      <div class="flowchart-header">
        <div></div>
        <div class="zoom-controls">
          <el-button-group>
            <el-button size="small" @click="zoomIn">+</el-button>
            <el-button size="small" @click="resetZoom">{{ Math.round(scale * 100) }}%</el-button>
            <el-button size="small" @click="zoomOut">-</el-button>
          </el-button-group>
          <el-button size="small" @click="goBack">返回</el-button>
          <el-button size="small" @click="resetView">重置视图</el-button>
        </div>
      </div>
      
      <div class="canvas-wrapper" ref="canvasWrapper">
        <div 
          class="canvas-container" 
          :style="{ transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)` }"
        >
          
          <!-- 吸附线 -->
          <div v-if="snapGuides.vertical !== null" class="snap-guide vertical" :style="{ left: snapGuides.vertical + 'px' }"></div>
          <div v-if="snapGuides.horizontal !== null" class="snap-guide horizontal" :style="{ top: snapGuides.horizontal + 'px' }"></div>
          
          <!-- 连线层 -->
          <svg class="edges-layer" :width="2000" :height="2000">
            <path
              v-for="edge in edges"
              :key="edge.id"
              :d="getEdgePath(edge)"
              class="edge-path"
              :class="{ 'selected': selectedEdge === edge.id }"
              stroke="#999"
              stroke-width="2"
              fill="none"
              @click="selectEdge(edge)"
            />
          </svg>
          
          <!-- 节点 -->
          <div
            v-for="node in nodes"
            :key="node.id"
            class="flow-node"
            :class="{
              'base-metric': node.type === 'base',
              'custom-metric': node.type === 'custom',
              'selected': selectedNode?.id === node.id,
              'connecting': connecting && connectingNode?.id === node.id,
              'connectable': connecting && (!connectingNode || connectingNode.id !== node.id),
              'connection-invalid': connecting && !canConnectTo(node),
              'has-parent': hasParentNode(node.id)
            }"
            :style="{ left: node.x + 'px', top: node.y + 'px' }"
            @mousedown="(e) => handleNodeMouseDown(e, node)"
            @click="selectNode(node)"
            @contextmenu.prevent="(e) => showNodeContextMenu(e, node)"
          >
            <div class="node-content">
              <div class="node-title">{{ node.label }}</div>
              <div class="node-type">{{ node.type === 'base' ? '基础指标' : '自定义指标' }}</div>
              <div 
                class="metric-type-indicator" 
                :class="node.type"
              >
                {{ node.type === 'base' ? '基' : '自' }}
              </div>
            </div>
            
            <!-- 连接点 -->
            <!-- <div class="node-handles">
              <div 
                class="handle handle-left" 
                :class="{ 
                  'disabled': node.type === 'base',
                  'active': connecting && connectingNode?.id === node.id && connectingHandle === 'left',
                  'connectable': connecting && connectingNode?.id !== node.id && canConnectTo(node),
                  'connection-invalid': connecting && connectingNode?.id !== node.id && !canConnectTo(node)
                }"
                :title="node.type === 'base' ? '基础指标不能作为连接目标' : '连接到此节点'"
              ></div>
              <div 
                class="handle handle-right" 
                :class="{ 
                  'active': connecting && connectingNode?.id === node.id && connectingHandle === 'right',
                  'has-parent': hasParentNode(node.id)
                }"
                :title="hasParentNode(node.id) ? '该节点已有父节点' : '从此节点开始连接'"
              ></div>
            </div> -->
          </div>
          
          <!-- 操作说明 -->
          <div v-if="nodes.length === 0" class="instructions">
            <div class="instruction-content">
              <h4>操作说明</h4>
              <ul>
                <li>从左侧<strong>指标库</strong>中拖拽指标到画布</li>
                <li>点击节点查看<strong>属性</strong></li>
                <li>右键节点可进行<strong>删除</strong>等操作</li>
                <li>拖拽节点<strong>连接点</strong>创建连接关系</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧属性面板 -->
    <el-drawer
      v-model="showPropertiesDrawer"
      title="节点属性"
      direction="rtl"
      size="800px"
      class="properties-drawer"
    >
      <div class="properties-content" v-if="selectedNode">
        <el-form :model="nodeForm" label-width="100px" label-position="left">
          <el-form-item label="节点名称">
            <el-input disabled v-model="nodeForm.label" placeholder="请输入节点名称" />
          </el-form-item>
          
          <el-form-item label="描述信息">
            <el-input
              disabled
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
            <el-select v-model="nodeForm.selectedAnalysisMethod" placeholder="请选择分析方法" style="width: 180px; margin-right: 10px;" disabled>
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
              权重查看
            </el-button>
            <span v-if="getChildNodes(selectedNode.id).length === 0" class="text-gray-400 ml-2">
              (无子节点)
            </span>
          </el-form-item>

          <el-form-item label="指标算法" v-if="getChildNodes(selectedNode.id).length > 0">
            <div class="algorithm-section" style="display: flex; align-items: center;">
              <el-select v-model="nodeForm.selectedAlgorithm" placeholder="请选择指标算法" style="width: 200px; margin-right: 10px;" disabled>
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
                v-if="nodeForm.selectedAlgorithm === 'fuzzy'"
                @click="initFuzzyMatrix()"
                class="ml-2"
              >
                参数配置
              </el-button>
              <el-button
                v-if="nodeForm.selectedAlgorithm === 'grey'"
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
                <el-table :data="[nodeForm.greyClusteringSegments]" border style="width: 100%; overflow: auto;">
                  <el-table-column min-width="100px" label="分数分段"></el-table-column>
                  <el-table-column min-width="120px" v-for="index in nodeForm.greyClusteringSegments.length" :key="index" :label="'分段 ' + (index)">
                    <template #default="scope">
                      <el-input
                        v-model="nodeForm.greyClusteringSegments[index-1]"
                        type="number"
                        :min="0"
                        :max="100"
                        @change="handleGreySegmentChange(index-1)"
                      ></el-input>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <div class="data-table-container mt-6">
                <p style="color: #fff;">子节点范围配置:</p>
                <el-table :data="nodeForm.greyClusteringData" border style="width: 100%">
                  <el-table-column prop="nodeName" label="子节点名称" min-width="120"></el-table-column>
                  <el-table-column v-for="(segment, index) in nodeForm.greyClusteringSegments.length + 1" :key="index" :label="'范围 ' + (index + 1)">
                    <template #default="scope">
                      <el-input
                        v-model="scope.row.ranges[index]"
                        placeholder="例如: 0||100"
                        @change="handleGreyRangeChange(scope.row, index)"
                      ></el-input>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
            <template #footer>
              <el-button @click="showGreyClusteringDialog = false">取消</el-button>
            </template>
          </el-dialog>

          <!-- Fuzzy Comprehensive Evaluation Matrix Dialog -->
          <el-dialog v-model="nodeForm.showFuzzyMatrixDialog" title="模糊综合评判矩阵配置" width="800px">
            <div class="table-container">
              <table class="parameter_table">
                <thead>
                  <tr>
                    <th style="min-width: 100px;">分数分段</th>
                    <th v-for="(segment, index) in nodeForm.scoreSegments" :key="'header-' + index">
                      {{ segment }}分
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in nodeForm.fuzzyMatrixData" :key="'row-' + rowIndex">
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
              <el-table :data="[nodeForm.scoreSegments]" border style="width: 100%; overflow: auto;">
                <el-table-column min-width="100px" label="分数分段"></el-table-column>
                <el-table-column min-width="120px" v-for="index in nodeForm.scoreSegments.length" :key="index" :label="'分段 ' + (index)">
                  <template #default="scope">
                    <el-input
                      v-model="nodeForm.scoreSegments[index-1]"
                      :min="0"
                      :max="100"
                      @change="handleScoreSegmentChange(index-1)"
                    ></el-input>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <template #footer>
              <el-button @click="showFuzzyMatrixDialog = false">取消</el-button>
            </template>
          </el-dialog>

          <el-form-item label="评分方式" v-if="getChildNodes(selectedNode.id).length === 0">
            <el-radio-group v-model="nodeForm.scoringMethod" disabled>
              <el-radio style="color: #fff;" value="expert">专家打分</el-radio>
              <el-radio style="color: #fff;" value="formula">公式计算</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <!-- Expert Scoring -->
          <el-form-item v-if="nodeForm.selectedAlgorithm === 'expert' || (getChildNodes(selectedNode.id).length === 0 && nodeForm.scoringMethod === 'expert')" label="专家评分">
            <el-input-number
              v-model="nodeForm.expertScore"
              :min="0"
              :max="100"
              style="width: 100%"
              placeholder="请输入0-100分"
              disabled
            />
          </el-form-item>
          
          <!-- Formula Calculation -->
          <div v-if="nodeForm.scoringMethod.includes('formula')" class="formula-section">
            <el-form-item label="算法公式">
              <el-input v-model="nodeForm.formula" placeholder="例如：1-(P1-P3)/(P2-P3)" disabled/>
            </el-form-item>
            
            <el-form-item label="参数列表">
              <div class="parameter-table">
                <el-table :data="nodeForm.parameterList" border style="width: 100%">
                  <el-table-column type="index" label="序号" width="60" />
                  <el-table-column prop="name" label="参数名称" />
                  <el-table-column prop="alias" label="参数别名" />
                  <el-table-column label="操作" align="center" min-width="180">
                    <template #default="scope">
                      <el-button size="small" @click="bindDataSource(scope.row)">数据源绑定</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-form-item>
          </div>
          
          <el-form-item label="归一化算法" v-if="getChildNodes(selectedNode.id).length === 0">
            <div class="normalization-section">
              <el-select v-model="nodeForm.normalizationAlgorithm" placeholder="请选择归一化算法" style="width: 200px" disabled>
                <el-option label="高斯函数映射" value="gaussian_mapping" type="gaussian_mapping"/>
                <el-option label="柯西分布映射" value="cauchy_mapping" type="cauchy_mapping"/>
                <el-option label="指数衰减函数" value="exponential_decay" type="exponential_decay"/>
                <el-option label="辑斯蒂函数变体" value="logistic_variant" type="logistic_variant"/>
                <el-option label="对称线性函数" value="linear_segment" type="linear_segment"/>
                <el-option label="单段线性函数" value="linear_mapping" type="linear_mapping"/>
                <el-option label="开关函数" value="zero_one_mapping" type="zero_one_mapping"/>
                <el-option label="线性分段函数" value="segmentation_liner_mapping" type="segmentation_liner_mapping"/>
                <el-option label="台阶分段函数" value="segmentation_mapping" type="segmentation_mapping"/>
              </el-select>
              <el-button @click="showParameterConfigDialog = true" class="ml-2">参数配置</el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="更新时间">
            <el-input :value="formatDate(nodeForm.updateTime)" disabled />
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
    <el-dialog v-model="showWeightAllocationDialog" title="权重分析" width="800px">
      <div class="weight-allocation-content">
        <template v-if="nodeForm.selectedAnalysisMethod === 'ahp'">
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
          <el-table :data="nodeForm.ahpMatrix" border style="width: 100%">
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
                <el-input v-model="row[colIndex]" size="small" :disabled="$index === colIndex || true" @change="handleMatrixInput($index, colIndex, row[colIndex])" type="text" />
              </template>
            </el-table-column>
          </el-table>

          <!-- AHP权重计算结果 -->
          <div class="mt-4">
            <p class="mb-2" style="color: #fff;">权重计算结果</p>
            <el-table :data="nodeForm.ahpWeights" border style="width: 100%">
              <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
              <el-table-column prop="weight" label="权重占比">
                <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
              </el-table-column>
            </el-table>
          </div>
        </template>
        <template v-else-if="nodeForm.selectedAnalysisMethod === 'EntropyWeight' || nodeForm.selectedAnalysisMethod === 'CoefficientMethod'">
          <div class="score-segments-section mt-4">
            <el-table :data="nodeForm.methodMatrixData" border style="width: 100%">
              <el-table-column prop="name" label="子节点名称" min-width="120"></el-table-column>
              <el-table-column min-width="100px" v-for="(segment, index) in nodeForm.methodMatrixData[0]?.row_list || []" :key="index" :label="'第' + (index + 1) + '段'">
                <template #default="scope">
                  <el-input
                    v-model="scope.row.row_list[index]"
                    @change="handleMatrixChange(scope.row, index)"
                    disabled
                  ></el-input>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 权重计算结果 -->
          <div class="mt-4">
            <p class="mb-2" style="color: #fff;">权重计算结果</p>
            <el-table :data="nodeForm.methodWeights" border style="width: 100%">
              <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
              <el-table-column prop="weight" label="权重占比">
                <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
              </el-table-column>
            </el-table>
          </div>
        </template>
        <template v-else-if="nodeForm.selectedAnalysisMethod === 'GreyRelationalAnalysis'">
          <div class="grey-relational-container">
            <h4 style="color: #fff;" class="grey-relational-title">灰色关联分析法配置</h4>
            <!-- 分辨系数配置 -->
            <div class="rho-config mt-4">
              <el-form-item style="color: #fff;" label="分辨系数 rho (0-1)">
                <el-slider
                  v-model="nodeForm.greyRelationalData.rho"
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
                  <el-radio style="color: #fff;" :value="'positive'">越大越好</el-radio>
                  <el-radio style="color: #fff;" :value="'negative'">越小越好</el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 数据表格 -->
            <div class="data-table-container mt-4">
              <el-table :data="nodeForm.greyRelationalData.data_list" border style="width: 100%">
                <el-table-column v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
                  <template #default="scope">
                    <el-input
                    v-model="nodeForm.greyRelationalData.data_list[scope.$index][index]"
                    type="number"
                    :min="0"
                    :max="100"
                    @change="handleGreyDataChange(scope.$index, index, $event)"
                    disabled
                  />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="nodeForm.greyRelationalWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </template>
        <template v-else-if="nodeForm.selectedAnalysisMethod === 'DareMethod'">
          <div class="dare-method-container">
            <h4 style="color: #fff;" class="dare-method-title">环比系数法配置</h4>
            
            <!-- 环比系数输入 -->
            <div class="dare-coefficients mt-4">
              <p style="color: #fff;" class="mb-2">请输入环比系数（大于等于0）</p>
              <div v-for="(pair, index) in nodeForm.dareCoefficientPairs" :key="index" class="dare-coefficient-item">
                <span style="color: #fff;" class="pair-description">{{ pair }} 的重要程度：</span>
                <el-input
                  v-model="nodeForm.dareCoefficients[index]"
                  type="number"
                  :min="0"
                  step="0.01"
                  precision="2"
                  style="width: 150px; margin-left: 10px;"
                  @change="dareCoefficients[index] = Math.max(0, Number(dareCoefficients[index]) || 0)"
                  disabled
                />
              </div>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="nodeForm.dareWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </template>
        <template v-else-if="nodeForm.selectedAnalysisMethod === 'FactorAnalysis'">
          <div class="factor-analysis-container">
            <h4 style="color: #fff;" class="factor-analysis-title">因子分析法配置</h4>

            <!-- 数据表格 -->
            <div class="data-table-container mt-4">
              <el-table :data="nodeForm.factorData.data_list" border style="width: 100%">
                <el-table-column v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
                  <template #default="scope">
                    <el-input
                    v-model="nodeForm.factorData.data_list[scope.$index][index]"
                    type="number"
                    :min="0"
                    @change="handleFactorDataChange('FactorAnalysis', scope.$index, index, $event)"
                    disabled
                  />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="nodeForm.factorWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </template>
        <template v-else-if="nodeForm.selectedAnalysisMethod === 'PcaWeight'">
          <div class="factor-analysis-container">
            <h4 style="color: #fff;" class="factor-analysis-title">主成分分析法配置</h4>

            <!-- 数据表格 -->
            <div class="data-table-container mt-4">
              <el-table :data="nodeForm.pcaData.data_list" border style="width: 100%">
                <el-table-column v-for="(child, index) in getChildNodes(selectedNode?.id)" :key="child.id" :label="child.label">
                  <template #default="scope">
                    <el-input
                    v-model="nodeForm.pcaData.data_list[scope.$index][index]"
                    type="number"
                    :min="0"
                    @change="handleFactorDataChange('PcaWeight', scope.$index, index, $event)"
                    disabled
                  />
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 权重计算结果 -->
            <div class="mt-4">
              <p class="mb-2" style="color: #fff;">权重计算结果</p>
              <el-table :data="nodeForm.pcaWeights" border style="width: 100%">
                <el-table-column prop="nodeLabel" label="子节点" width="180"></el-table-column>
                <el-table-column prop="weight" label="权重占比">
                  <template #default="scope">{{ (scope.row.weight * 100).toFixed(2) }}%</template>
                </el-table-column>
              </el-table>
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
                  v-model="nodeForm.percentageWeights[child.id]"
                  :min="0"
                  :max="100"
                  :precision="1"
                  style="width: 120px"
                  @change="(value) => { percentageWeights[child.id] = value; childWeights[child.id] = value / 100 }"
                  disabled
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
      </template>
    </el-dialog>
    <el-dialog v-model="showParameterConfigDialog" title="参数配置" width="600px">
      <div class="parameter-config-content">
        <el-form label-width="120px">
          <template v-if="['gaussian_mapping', 'cauchy_mapping', 'exponential_decay', 'logistic_variant'].includes(nodeForm.normalizationAlgorithm)">
            <el-form-item label="期望值 (μ)">
              <el-input-number disabled v-model="nodeForm.normalizationParams.mu" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="系数 (k)">
              <el-input-number disabled v-model="nodeForm.normalizationParams.k" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
          </template>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'zscore'" label="均值">
            <el-input-number disabled v-model="nodeForm.normalizationParams.mean" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'zscore'" label="标准差">
            <el-input-number disabled v-model="nodeForm.normalizationParams.std" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'decimal'" label="小数位数">
            <el-input-number disabled v-model="nodeForm.normalizationParams.decimal" :min="1" :max="10" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'linear_segment'" label="满分点 (μ)">
            <el-input-number disabled v-model="nodeForm.normalizationParams.mu" :precision="2" :step="0.1" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'linear_segment'" label="单边有效范围 (d)">
            <el-input-number disabled v-model="nodeForm.normalizationParams.d" :precision="2" :step="0.1" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'linear_mapping'" label="最小值 (x_min)">
            <el-input-number disabled v-model="nodeForm.normalizationParams.x_min" :precision="2" :step="0.1" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'linear_mapping'" label="最大值 (x_max)">
            <el-input-number disabled v-model="nodeForm.normalizationParams.x_max" :precision="2" :step="0.1" style="width: 100%" />
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'linear_mapping' || nodeForm.normalizationAlgorithm === 'zero_one_mapping'" label="增减性">
            <el-select disabled v-model="nodeForm.normalizationParams.upDown" placeholder="请选择增减性" style="width: 100%">
              <el-option label="增" value="1" />
              <el-option label="减" value="-1" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="nodeForm.normalizationAlgorithm === 'zero_one_mapping'" label="关键点 (μ)">
            <el-input-number disabled v-model="nodeForm.normalizationParams.mu" :precision="2" :step="0.1" :min="0" style="width: 100%" />
          </el-form-item>
          <template v-if="nodeForm.normalizationAlgorithm === 'segmentation_liner_mapping' || nodeForm.normalizationAlgorithm === 'segmentation_mapping'">
              <div class="table-container">
                <table class="parameter_table">
                  <thead>
                    <tr>
                      <th style="min-width: 100px;">x_list(指标值)
                        y_list(得分值)</th>
                      <th v-for="(x, index) in nodeForm.normalizationParams.x_list" :key="'header-' + index">
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
                      <td v-for="(x, index) in nodeForm.normalizationParams.x_list" :key="'x-' + index">
                        <el-input
                          disabled
                          v-model="nodeForm.normalizationParams.x_list[index]"
                          type="number"
                          style="width: 100px"
                          @change="validateXList(index)"
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
                      <td v-for="(y, index) in nodeForm.normalizationParams.y_list" :key="'y-' + index">
                        <el-input
                          disabled
                          v-model="nodeForm.normalizationParams.y_list[index]"
                          type="number"
                          style="width: 100px"
                          @change="validateXList(index)"
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
      </template>
    </el-dialog>
    <el-dialog v-model="showDataSourceDialog" title="数据源绑定" width="800px">
      <div class="data-source-content">
        <el-form label-width="100px">
          <!-- 参数信息 -->
          <el-form-item label="参数名称">
            <el-input :value="parameter?.name" disabled />
          </el-form-item>
          <el-form-item label="参数别名">
            <el-input :value="parameter?.alias" disabled />
          </el-form-item>
          
          <!-- 数据源选择 -->
          <el-form-item label="数据源">
            <el-select disabled v-model="nodeForm.dataSourceForm[parameter.id].dataSource" placeholder="请选择数据源" style="width: 100%">
              <el-option v-for="item in dataSourceList" :label="item.label" :value="item.value" :key="item.value" />
            </el-select>
          </el-form-item>
          
          <!-- 筛选条件 -->
          <el-form-item label="筛选条件">
            <div class="filter-conditions">
              <div v-for="(condition, index) in nodeForm.dataSourceForm[parameter.id].filterConditions" :key="index" class="condition-row">
                <el-select disabled v-model="condition.field" @change="handleFieldChange(condition)" placeholder="选择字段" style="width: 200px">
                  <el-option v-for="item in dataSourceList" :label="item.label" :value="item.value" :key="item.value" />
                </el-select>
                
                <el-select disabled v-model="condition.operator" placeholder="操作符" style="width: 120px; margin: 0 8px">
                  <el-option v-for="op in getOperatorsByFieldType(condition.field)" :label="op.label" :value="op.value" :key="op.value" />
                </el-select>
                
                <el-input 
                  disabled
                  v-model="condition.value" 
                  placeholder="输入值" 
                  style="width: 200px"
                />
                
              </div>
            </div>
          </el-form-item>
          
          <!-- 结果取值 -->
          <el-form-item label="结果取值">
            <div class="result-calculation">
              <el-select disabled v-model="nodeForm.dataSourceForm[parameter.id].resultType" placeholder="请选择计算方式" style="width: 200px">
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
                v-if="nodeForm.dataSourceForm[parameter.id].resultType === 'get_percentage'"
                disabled
                v-model="nodeForm.dataSourceForm[parameter.id].percentageCondition"
                placeholder="请输入占比条件"
                style="width: 200px; margin-left: 8px"
              />
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showDataSourceDialog = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useResultDataStore } from '@/stores/resultDataStore'
import { useRouter } from 'vue-router'
import { getDictList } from '@/api/OrderView'
// 路由参数

// Pinia store
const resultDataStore = useResultDataStore()

// 节点和连线数据
const graphData = ref(null)
const nodes = ref([])
const edges = ref([])

// 选中的节点和连线
const selectedNode = ref(null)
const selectedEdge = ref(null)

// 连接状态
const connecting = ref(false)
const connectingNode = ref(null)
const connectingHandle = ref(null)

// 缩放和平移
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isPanning = ref(false)
const panStartX = ref(0)
const panStartY = ref(0)

// 吸附线
const snapGuides = reactive({
  vertical: null,
  horizontal: null
})

// 属性面板
const showPropertiesDrawer = ref(false)
const showWeightAllocationDialog = ref(false)
const showParameterConfigDialog = ref(false)
const showDataSourceDialog = ref(false)
// 参数配置
const showGreyClusteringDialog = ref(false)
const showFuzzyMatrixDialog = ref(false) // 模糊综合评判法
const selectedAlgorithm = ref('weighted') // 加权平均法
const scoringMethod = ref('expert')
// 右键菜单
const contextMenuX = ref(0)
const contextMenuY = ref(0)

// 指标数据
const baseMetrics = ref([
  { id: '1', label: '侦查预警能力', type: 'base' },
  { id: '2', label: '信息传输能力', type: 'base' },
  { id: '3', label: '指挥控制能力', type: 'base' },
  { id: '4', label: '行动处置能力', type: 'base' },
  { id: '5', label: '综合打击能力', type: 'base' }
])

const customMetrics = ref([
  { id: '6', label: '空天攻防能力', type: 'custom' },
  { id: '7', label: '联合火力打击能力', type: 'custom' }
])

const expertScore = ref(null)

const router = useRouter()
// 返回上一页
const goBack = () => {
  // 清除store中的数据
  resultDataStore.clearResultData()
  // 返回结果列表页面
  router.go(-1)
}

// 节点表单数据
const nodeForm = reactive({
  label: '',
  code: '',
  type: '',
  typeLabel: '',
  description: '',
  category: '',
  weight: 0,
  formula: '',
  businessRule: '',
  selectedAnalysisMethod: '',
  selectedAlgorithm: '',
  x: 0,
  y: 0,
  updateTime: '',
  dataSourceForm: {},
  // 新增属性
  customWeight: 0,
  expertScore: 0,
  ahpMatrix: [],
  ahpWeights: [],
  normalizationAlgorithm: '',
  normalizationParams: {},
  parameterList: [],
  scoreSegments: [],
  scoringMethod: [],
  childWeights: {},
  fuzzyMatrixData: [],
  greyRelationalData: {},
  greyRelationalWeights: [],
  dareCoefficients: [],
  dareCoefficientPairs: [],
  dareWeights: [],
  factorData: {},
  factorWeights: [],
  pcaData: {},
  pcaWeights: [],
  methodMatrixData: [],
  methodWeights: []
})
const workflowType = ref(1)
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
// 权重分析方法选项
const analysisMethods = [
  { value: 'ahp', label: 'AHP层次分析法' },
  { value: 'Coefficient', label: '变异系数法' },
  { value: 'EntropyWeight', label: '熵权法' },
  { value: 'directEmpowerment', label: '直接赋权法' },
  { value: 'GreyRelationalAnalysis', label: '灰色关联分析法' },
  { value: 'DareMethod', label: '环比系数法' },
  { value: 'FactorAnalysis', label: '因子分析法' },
  { value: 'PcaWeight', label: '主成分分析法' }
]

// 指标算法选项
const algorithms = [
  { value: 'fuzzy', label: '模糊综合评判法' },
  { value: 'weighted', label: '加权平均法' },
  { value: 'topsis', label: 'TOPSIS法' },
  { value: 'sea', label: '灰色SEA法' },
  { value: 'grey', label: '灰色聚类法' },
  { value: 'adc', label: 'ADC法' },
  { value: 'index', label: '指数法' },
  { value: 'expert', label: '专家打分法' }
]

// 刷新基础指标
const refreshBaseMetrics = () => {
  // 实际项目中这里会调用API获取最新的基础指标数据
  console.log('刷新基础指标')
}

// 处理拖拽
const handleDragOver = (event) => {
  event.preventDefault()
}

// 处理放置
// const handleDrop = (event) => {
//   event.preventDefault()
//   const data = JSON.parse(event.dataTransfer.getData('text/plain'))
  
//   // 计算画布上的坐标
//   const rect = event.currentTarget.getBoundingClientRect()
//   const x = (event.clientX - rect.left - translateX.value) / scale.value
//   const y = (event.clientY - rect.top - translateY.value) / scale.value
  
//   // 添加节点
//   const newNode = {
//     id: `node-${Date.now()}`,
//     label: data.label,
//     type: data.type,
//     x: Math.round(x / 20) * 20, // 对齐到网格
//     y: Math.round(y / 20) * 20  // 对齐到网格
//   }
  
//   nodes.value.push(newNode)
// }
const getChildNodes = (nodeId) => {
  return graphData.value.edges
    .filter(edge => edge.source === nodeId)
    .map(edge => graphData.value.nodes.find(node => node.id === edge.target))
    .filter(Boolean)
}
// 选择节点
const selectNode = (node) => {
  selectedNode.value = node
  selectedEdge.value = null
  
  // 从resultDataStore.resultData.nodeDetails中获取节点详细信息
  if (resultDataStore.resultData && resultDataStore.resultData.nodeDetails) {
    const savedDetails = resultDataStore.resultData.nodeDetails[node.id] || {}
    
    Object.assign(nodeForm, {
      label: savedDetails.label || node.label || '',
      code: savedDetails.code || node.code || '',
      type: savedDetails.type || node.type || '',
      typeLabel: savedDetails.typeLabel || node.typeLabel || '',
      description: savedDetails.description || node.description || '',
      category: savedDetails.category || node.category || '',
      weight: savedDetails.weight || node.weight || 0,
      formula: savedDetails.formula || node.formula || '',
      businessRule: savedDetails.businessRule || '',
      selectedAnalysisMethod: savedDetails.selectedAnalysisMethod || '',
      selectedAlgorithm: savedDetails.selectedAlgorithm || 'weighted',
      x: savedDetails.x || node.x || 0,
      y: savedDetails.y || node.y || 0,
      updateTime: savedDetails.updateTime || '',
      dataSourceForm: savedDetails.dataSources || {},
      // 新增属性
      customWeight: savedDetails.customWeight || 0,
      expertScore: savedDetails.expertScore || 0,
      ahpMatrix: savedDetails.ahpMatrix || [],
      ahpWeights: savedDetails.ahpWeights || [],
      normalizationAlgorithm: savedDetails.normalizationAlgorithm || '',
      normalizationParams: savedDetails.normalizationParams || {},
      parameterList: savedDetails.parameterList || [],
      scoreSegments: savedDetails.scoreSegments || [],
      scoringMethod: savedDetails.scoringMethod || [],
      childWeights: savedDetails.childWeights || {},
      fuzzyMatrixData: savedDetails.fuzzyMatrixData || [],
      greyRelationalData: savedDetails.greyRelationalData || {},
      greyRelationalWeights: savedDetails.greyRelationalWeights || [],
      dareCoefficients: savedDetails.dareCoefficients || [],
      dareCoefficientPairs: savedDetails.dareCoefficientPairs || [],
      dareWeights: savedDetails.dareWeights || [],
      factorData: savedDetails.factorData || {},
      factorWeights: savedDetails.factorWeights || {},
      pcaData: savedDetails.pcaData || {},
      pcaWeights: savedDetails.pcaWeights || [],
      methodMatrixData: savedDetails.methodMatrixData || [],
      methodWeights: savedDetails.methodWeights || []
    })
    console.log('nodeForm', nodeForm, 'savedDetails', savedDetails)
  }
  
  // 显示属性面板
  showPropertiesDrawer.value = true
}

// 显示节点右键菜单
const showNodeContextMenu = (event, node) => {
  event.preventDefault()
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  selectedNode.value = node
}

// 检查节点是否可以连接
const canConnectTo = (targetNode) => {
  // 基础指标不能作为连接目标
  if (targetNode.type === 'base') return false
  
  // 不能连接到自己
  if (connectingNode.value && connectingNode.value.id === targetNode.id) return false
  
  // 不能重复连接
  const alreadyConnected = edges.value.some(edge => 
    edge.source === connectingNode.value?.id && edge.target === targetNode.id
  )
  if (alreadyConnected) return false
  
  // 检查是否会造成循环连接
  const wouldCreateCycle = checkConnectionCycle(connectingNode.value?.id, targetNode.id)
  if (wouldCreateCycle) return false
  
  return true
}

// 检查连接是否会形成循环
const checkConnectionCycle = (sourceId, targetId) => {
  // 简单的循环检查实现
  if (!sourceId) return false
  
  const visited = new Set()
  const queue = [targetId]
  
  while (queue.length > 0) {
    const currentId = queue.shift()
    if (currentId === sourceId) return true
    
    if (!visited.has(currentId)) {
      visited.add(currentId)
      const outgoingEdges = edges.value.filter(edge => edge.source === currentId)
      queue.push(...outgoingEdges.map(edge => edge.target))
    }
  }
  
  return false
}

// 检查节点是否有父节点
const hasParentNode = (nodeId) => {
  return edges.value.some(edge => edge.target === nodeId)
}

const openWeightAllocation = () => {
  showWeightAllocationDialog.value = true
}

const getNodePosition = (nodeId) => {
  const node = graphData.value.nodes.find(n => n.id === nodeId)
  return node ? { x: node.x + 70, y: node.y + 25 } : { x: 0, y: 0 }
}
// 生成连线路径
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

// 选择连线
const selectEdge = (edge) => {
  selectedEdge.value = edge.id
  selectedNode.value = null
  showPropertiesDrawer.value = false
}

// 处理画布鼠标按下
const handleCanvasMouseDown = (event) => {
  // 只有在点击画布空白处时才允许拖拽
  if (event.target === event.currentTarget || event.target.classList.contains('canvas-container')) {
    isPanning.value = true
    panStartX.value = event.clientX - translateX.value
    panStartY.value = event.clientY - translateY.value
  }
}

// 处理画布鼠标移动
const handleCanvasMouseMove = (event) => {
  if (isPanning.value) {
    translateX.value = event.clientX - panStartX.value
    translateY.value = event.clientY - panStartY.value
  }
}

// 处理画布鼠标抬起
const handleCanvasMouseUp = () => {
  isPanning.value = false
}

// 处理鼠标滚轮缩放
const handleWheel = (event) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.min(Math.max(0.5, scale.value + delta), 2)
}

// 放大
const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.1, 2)
}

// 缩小
const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.1, 0.5)
}

// 重置缩放
const resetZoom = () => {
  scale.value = 1
}

// 重置视图
const resetView = () => {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

// 处理节点鼠标按下
const handleNodeMouseDown = (event, node) => {
  event.stopPropagation()
  
  // 如果正在连接，不处理节点拖拽
  if (connecting.value) return
  
  // 禁用节点拖拽功能
  // 开始拖拽节点
  // const rect = event.currentTarget.getBoundingClientRect()
  // const x = (event.clientX - rect.left - translateX.value) / scale.value
  // const y = (event.clientY - rect.top - translateY.value) / scale.value
  
  // 计算节点的偏移量
  // const offsetX = x - node.x
  // const offsetY = y - node.y
  
  // 保存拖拽状态
  // const isDragging = ref(true)
  
  // 处理鼠标移动
  // const handleMouseMove = (moveEvent) => {
  //   if (!isDragging.value) return
  //   
  //   // 计算新位置
  //   const newX = (moveEvent.clientX - rect.left - translateX.value) / scale.value - offsetX
  //   const newY = (moveEvent.clientY - rect.top - translateY.value) / scale.value - offsetY
  //   
  //   // 应用吸附
  //   const snappedPos = snapToGrid(newX, newY)
  //   
  //   // 更新节点位置
  //   node.x = snappedPos.x
  //   node.y = snappedPos.y
  //   
  //   // 更新吸附线显示
  //   snapGuides.vertical = snappedPos.snapX !== null ? snappedPos.snapX : null
  //   snapGuides.horizontal = snappedPos.snapY !== null ? snappedPos.snapY : null
  // }
  
  // 处理鼠标抬起
  // const handleMouseUp = () => {
  //   isDragging.value = false
  //   document.removeEventListener('mousemove', handleMouseMove)
  //   document.removeEventListener('mouseup', handleMouseUp)
  //   
  //   // 清除吸附线
  //   setTimeout(() => {
  //     snapGuides.vertical = null
  //     snapGuides.horizontal = null
  //   }, 1000)
  // }
  
  // 添加事件监听器
  // document.addEventListener('mousemove', handleMouseMove)
  // document.addEventListener('mouseup', handleMouseUp)
}
const dataSourceList = ref(null)
const parameter = ref({})
const bindDataSource = async (param) => {
  console.log('parameter', param)
  parameter.value = param
  console.log('parameter.value', parameter.value)
  // 将parameter数据赋值给nodeForm.parameterList
  console.log('nodeForm.dataSourceForm[param.id]', nodeForm.dataSourceForm[param.id])
  // 根据id从nodeForm.dataSources中获取该参数详情
  if (!nodeForm.dataSourceForm[param.id]) {
    nodeForm.dataSourceForm[param.id] = {
      dataSource: '',
      filterConditions: [],
      resultType: '',
      percentageCondition: '',
    }
  }
  await getDictList(nodeForm.dataSourceForm[param.id].InferentialListValue).then(res => {
    dataSourceList.value = res.data.info.map(item => ({
      label: item.col_name,
      type: item.col_type,
      value: item.id
    }))
  })
  showDataSourceDialog.value = true
}

const formatDate = (timestamp) => {
  if (!timestamp) return '未设置'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 组件挂载时的处理
onMounted(() => {
  // 添加全局事件监听器
  document.addEventListener('mousemove', handleCanvasMouseMove)
  document.addEventListener('mouseup', handleCanvasMouseUp)
  
  // 优先从localStorage获取数据
  const savedData = localStorage.getItem('workflow-data');
  if (savedData) {
    try {
      const parsedData = JSON.parse(savedData);
      console.log('从localStorage获取的数据:', parsedData);
      workflowType.value = parsedData.workflowType;
      nodes.value = parsedData.graphData.nodes;
      edges.value = parsedData.graphData.edges;
      graphData.value = parsedData.graphData;
      baseMetrics.value = parsedData.treeData.baseMetrics;
      customMetrics.value = parsedData.treeData.customMetrics;
      // 如果localStorage中有数据，则也更新store
      resultDataStore.setResultData(parsedData);
      return;
    } catch (error) {
      console.error('解析localStorage数据失败:', error);
    }
  }
  
  // 从Pinia store获取数据并初始化
  if (resultDataStore.resultData) {
    // 这里可以根据resultDataStore.resultData初始化节点和连线
    console.log('从store获取的数据:', resultDataStore.resultData)
    workflowType.value = resultDataStore.resultData.workflowType
    nodes.value = resultDataStore.resultData.graphData.nodes
    edges.value = resultDataStore.resultData.graphData.edges
    graphData.value = resultDataStore.resultData.graphData
    baseMetrics.value = resultDataStore.resultData.treeData.baseMetrics
    customMetrics.value = resultDataStore.resultData.treeData.customMetrics
    // 保存数据到localStorage
    saveDataToLocalStorage(resultDataStore.resultData);
    // TODO: 实现具体的初始化逻辑
  }
})

// 组件卸载时的处理
onUnmounted(() => {
  // 移除全局事件监听器
  document.removeEventListener('mousemove', handleCanvasMouseMove)
  document.removeEventListener('mouseup', handleCanvasMouseUp)
  localStorage.removeItem('workflow-data')
})

// 保存数据到localStorage
const saveDataToLocalStorage = (data) => {
  try {
    localStorage.setItem('workflow-data', JSON.stringify(data));
    console.log('数据已保存到localStorage');
  } catch (error) {
    console.error('保存数据到localStorage失败:', error);
  }
}
</script>

<style scoped>
.workflow-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.left-sidebar {
  display: flex;
  flex-direction: column;
  width: 320px;
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

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
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
  flex: 1;
  display: flex;
  flex-direction: column;
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
  width: 100%;
  height: 100%;
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

.edge-path.selected {
  stroke: #1890ff !important;
  stroke-width: 3 !important;
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
</style>