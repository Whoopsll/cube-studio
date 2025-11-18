import request from '@/utils/request';

export function getReportList(id) {
  return request({
    url: '/compute/start',
    method: 'post',
    data: { id }
  });
}

export function exportReportFile(id) {
  return request({
    url: '/compute/make_docx',
    method: 'post',
    data: { id },
    responseType: 'blob'
  });
}