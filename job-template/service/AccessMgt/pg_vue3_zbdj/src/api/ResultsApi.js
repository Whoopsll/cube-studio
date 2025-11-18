import request from '@/utils/request'

export function getResultsList(data) {
  return request({
    url: '/access/get',
    method: 'post',
    data
  })
}

export function exportResultsFile(uid) {
  return request({
    url: '/access/upload',
    method: 'post',
    data: { uid },
    responseType: 'blob'
  })
}

export function deleteResultsFile(id) {
  return request({
    url: '/access/delete',
    method: 'post',
    data: { id },
  })
}