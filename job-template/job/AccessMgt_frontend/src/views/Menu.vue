<template>
  <div class="admin-layout">
    <!-- 左侧菜单栏 -->
    <div class="sidebar">
      <div class="logo">
        <h2>评估系统</h2>
      </div>
      <el-menu
        :default-active="$route.path"
        class="sidebar-menu"
        background-color="#001f2a"
        text-color="#ffffff"
        active-text-color="#ffffff"
        router
      >
        <el-menu-item class="active" index="/dashboard">
          <el-icon><House /></el-icon>
          <span>体系管理</span>
        </el-menu-item>
        <el-menu-item class="active" index="/users">
          <el-icon><User /></el-icon>
          <span>指标管理</span>
        </el-menu-item>
        <!-- <el-menu-item class="active" index="/analytics/0">
          <el-icon><Goods /></el-icon>
          <span>评估管理</span>
        </el-menu-item> -->
        <!-- <el-menu-item class="active" index="/inferential-data">
          <el-icon><Document /></el-icon>
          <span>推演数据管理</span>
        </el-menu-item>
        <el-menu-item class="active" index="/results">
          <el-icon><Document /></el-icon>
          <span>数据结果展示</span>
        </el-menu-item> -->
      </el-menu>
    </div>

    <!-- 右侧内容区域 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <div class="header">
        <div class="header-left">
          <h3>当前位置：{{ currentTitle  }}</h3>
        </div>
        <!-- <div class="header-right">
          <el-dropdown @command="handleUserAction">
            <span class="user-info">
              <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="username">管理员</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div> -->
      </div>
      <!-- 页面内容区域 -->
       <div class="content">
            <router-view></router-view>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentTitle = ref('')

const handleUserAction = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心')
      break
    case 'settings':
      ElMessage.info('设置')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        ElMessage.success('已退出登录')
      })
      break
  }
}
watch(
  () => route.meta.title,
  (newTitle) => {
    currentTitle.value = newTitle || '评估系统'
  },
  { immediate: true }
)
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: #f0f2f5;
}

.sidebar {
  width: 250px;
  background-color: #304156;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #001f2a;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  color: #fff;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.active:hover {
  background:#0c6783;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 60px;
  color: #fff;
  background-color: #0c4759;;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left h3 {
  width: 247px;
  height: 20px;
  line-height: normal;
  font-family: MicrosoftYaHeiUI;
  color: #ffffff;
  font-size: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.username {
  color: #fff;
  font-size: 14px;
}

.content {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .header-right {
    gap: 8px;
  }
  
  .username {
    display: none;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
:deep(.el-menu--vertical .el-menu-item.is-active) {
  background: linear-gradient(90deg, #0c6783 0%, #0a4360 100%) !important;
}
</style>
