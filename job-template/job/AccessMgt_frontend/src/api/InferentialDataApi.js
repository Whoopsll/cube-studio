import request from '@/utils/request';

export function getList(data) {
  return request({
    url: '/basic/get/collect',
    method: 'post',
    data
  });
}

export function deleteList(id) {
  return request({
    url: '/basic/delete/collect',
    method: 'post',
    data: { id: id }
  });
}

export function addList(data) {
  return request({
    url: '/basic/add/collect',
    method: 'post',
    data
  });
}

export function updateList(data) {
  return request({
    url: '/basic/update/collect',
    method: 'post',
    data
  });
}