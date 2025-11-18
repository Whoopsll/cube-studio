import request from '@/utils/request';

// 获取主表单数据
export function getInferentialList(data) {
  return request({
    url: '/basic/get',
    method: 'post',
    data
  });
}

export function deleteList(id) {
  return request({
    url: '/basic/delete',
    method: 'post',
    data: { id }
  });
}

export function addList(data) {
  return request({
    url: '/basic/add',
    method: 'post',
    data
  });
}

export function updateList(data) {
  return request({
    url: '/basic/update',
    method: 'post',
    data
  });
}

// 获取字典管理数据
export function getDictList(id) {
  return request({
    url: '/basic_dict/get',
    method: 'post',
    data: { id }
  });
}

export function deleteDictList(id) {
  return request({
    url: '/basic_dict/delete',
    method: 'post',
    data: { id }
  });
}

export function addDictList(data) {
  return request({
    url: '/basic_dict/add',
    method: 'post',
    data
  });
}

export function updateDictList(data) {
  return request({
    url: '/basic_dict/update',
    method: 'post',
    data
  });
}

// 原始数据部分
export function getRawList(data) {
  return request({
    url: '/basic_row_data/get',
    method: 'post',
    data
  });
}

export function deleteRawList(data) {
  return request({
    url: '/basic_row_data/delete',
    method: 'post',
    data
  });
}

export function addRawList(data) {
  return request({
    url: '/basic_row_data/add',
    method: 'post',
    data
  });
}

export function updateRawList(data) {
  return request({
    url: '/basic_row_data/update',
    method: 'post',
    data
  });
}

export function importRawFile(data) {
  return request({
    url: '/basic_row_data/import',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data
  });
}

export function exportRawFile(data) {
  return request({
    url: '/basic_row_data/export',
    method: 'post',
    data
  });
}