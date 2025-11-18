<template>
  <div style="overflow-y: auto; scrollbar-width: none; /* Firefox */">
    <router-view></router-view>
  </div>
</template>

<script setup>
// 菜单已移至Menu.vue组件中
</script>
<style>
*{
  margin: 0;
  padding: 0;
}
.el-input__wrapper {
  background-color: #133b48 !important;
}
/* 输入框文字颜色 */
.el-input__inner {
  color: #ffffff !important;
}

/* textarea 输入框背景色 */
.el-textarea__inner {
  background-color: #133b48 !important;
  border-color: #359fbb !important;   /* 可选：边框同色 */
  color: #ffffff !important;          /* 字体白色 */
}

/* 表格背景色 */
.el-table {
  --el-table-border-color: #133b48 !important;
  --el-table-border: 1px solid var(--el-table-border-color) !important;
}

/* 表头背景色 + 字体颜色 */
.el-table th.el-table__cell {
  background-color: #050b0d !important;
  color: #56d4f4 !important;
  font-weight: 600;
}

/* 表格内容背景色 + 字体颜色 */
.el-table td.el-table__cell {
  background-color: #050b0d !important;
  color: #ffffff !important;
}

/* 表格网格线（边框）颜色 */
.el-table--border,
.el-table--border--color,
.el-table--border th.el-table__cell,
.el-table--border td.el-table__cell {
  border-color: #133b48 !important;
}

/* 暂无数据背景色 */
.el-table__empty-block {
  background-color: #050b0d !important;
}

/* 暂无数据文字颜色（可选） */
.el-table__empty-text {
  color: #ffffff !important;
}

/* 普通按钮（编辑、详情等） */
.el-button--primary,
.el-button:not(.el-button--danger):not(.el-button--primary) {
  background-color: #359fbb !important;
  border-color: #359fbb !important;
  color: #ffffff !important;
}

.el-button--primary:hover,
.el-button:not(.el-button--danger):not(.el-button--primary):hover {
  background-color: #2e8aa3 !important;
  border-color: #2e8aa3 !important;
}

/* 删除按钮（danger） */
.el-button--danger {
  background-color: #f46c6c !important;
  border-color: #f46c6c !important;
  color: #ffffff !important;
}

.el-button--danger:hover {
  background-color: #d85c5c !important;
  border-color: #d85c5c !important;
}

/* 弹窗背景色 */
.el-dialog {
  background-color: #195877 !important;
}

/* 弹窗内所有文字颜色 */
.el-dialog,
.el-dialog__title,
.el-form-item__label,
.el-input__inner,
.el-textarea__inner {
  color: #ffffff !important;
}

/* 抽屉内所有输入框/选择器/文本域背景色 */
.properties-drawer {
  /* 统一背景色 */
  background-color: #195877 !important;
  color: #ffffff !important;
}

/* 抽屉标题颜色 */
.properties-drawer .el-drawer__title {
  color: #ffffff !important;
}

/* 所有输入框内文字颜色 */
.properties-drawer .el-input__inner,
.properties-drawer .el-textarea__inner,
.properties-drawer .el-input-number__input,
.properties-drawer .el-select__selected-item {
  color: #ffffff !important;
}

/* 输入框、数字框、文本域、选择器 */
.properties-drawer .el-input__inner,
.properties-drawer .el-textarea__inner,
.properties-drawer .el-input-number__inner,
.properties-drawer .el-select__wrapper {
  /* background-color: #133b48 !important; */
  border-color: #359fbb !important;
  color: #ffffff !important;
}

/* 选择器下拉面板 */
.properties-drawer .el-select-dropdown {
  background-color: #133b48 !important;
  border-color: #359fbb !important;
}
.properties-drawer .el-select-dropdown__item {
  color: #ffffff !important;
}
.properties-drawer .el-select-dropdown__item:hover {
  background-color: #359fbb !important;
}

/* 全局一次性覆盖 */
.el-select .el-select__wrapper {
  background-color: #133b48 !important;
}
/* 占位文字白色 */
.el-select .el-select__placeholder {
  color: #fff !important;
}
.filter-conditions {
  background-color: #133b48 !important;
}

/* 左右翻页按钮背景 */
.el-pagination .btn-prev,
.el-pagination .btn-next {
  background-color: #050b0d !important;
}

/* <> 图标颜色 */
.el-pagination .btn-prev .el-icon,
.el-pagination .btn-next .el-icon {
  color: #359fbb !important;
}

/* 数字方块统一背景 */
.el-pagination .el-pager li {
  background-color: #050b0d !important;
  color: #fff !important;
}

/* 当前页高亮（可保持同色或再加深） */
.el-pagination .el-pager li.is-active {
  background-color: #359fbb !important;
  color: #fff !important;
  font-weight: bold;
}

.el-pagination .el-pagination__total,
.el-pagination .el-pagination__sizes,
.el-pagination .el-pagination__jump {
  color: #fff !important;
}

.pagination-info {
  color: #fff !important;
}

/* 关闭按钮 X 图标颜色改为白色 */
.el-dialog__headerbtn .el-dialog__close {
  color: #fff !important;
}

.el-drawer__close-btn .el-icon.el-drawer__close {
  color: #fff !important;
}
</style>