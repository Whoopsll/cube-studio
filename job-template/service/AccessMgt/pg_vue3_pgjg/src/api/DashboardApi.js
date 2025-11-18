import request from '@/utils/request';

export function getList(data) {
  return request({
    url: '/system/get',
    method: 'post',
    data
  });
}

export function deleteList(id) {
  return request({
    url: '/system/delete',
    method: 'post',
    data: { id: id }
  });
}

export function addList(data) {
  return request({
    url: '/system/add',
    method: 'post',
    data
  });
}

export function updateList(data) {
  return request({
    url: '/system/update',
    method: 'post',
    data
  });
}

export function copyList(id) {
  return request({
    url: '/system/copy',
    method: 'post',
    data: { id: id }
  })
}