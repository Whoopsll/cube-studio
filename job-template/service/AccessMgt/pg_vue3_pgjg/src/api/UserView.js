import request from '@/utils/request';

export function getList(data) {
  return request({
    url: '/metric/get',
    method: 'post',
    data
  });
}

export function deleteList(id) {
  return request({
    url: '/metric/delete',
    method: 'post',
    data: { id: id }
  });
}

export function addList(data) {
  return request({
    url: '/metric/add',
    method: 'post',
    data
  });
}

export function updateList(data) {
  return request({
    url: '/metric/update',
    method: 'post',
    data
  });
}