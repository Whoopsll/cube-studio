import request from '@/utils/request';

export function computeFactor(data) {
    return request({
        url: '/compute/factor_analysis',
        method: 'post',
        data
    })
}

export function computePca(data) {
    return request({
        url: '/compute/pca_weight',
        method: 'post',
        data
    })
}

export function computeDare(data) {
    return request({
        url: '/compute/dare_method',
        method: 'post',
        data
    })
}

export function computeEntropy(data) {
    return request({
        url: '/compute/entropy_weight',
        method: 'post',
        data
    })
}

export function computeCoefficient(data) {
    return request({
        url: '/compute/coefficient_method',
        method: 'post',
        data
    })
}

export function computeAph(data) {
    return request({
        url: '/compute/ahp',
        method: 'post',
        data
    })
}

export function computeGreyRelational(data) {
    return request({
        url: '/compute/grey_relational_analysis',
        method: 'post',
        data
    })
}

export function analyticsSave(data) {
    return request({
        url: '/system/save',
        method: 'post',
        data
    })
}

export function analyticsList(id) {
    return request({
        url: '/system/detail',
        method: 'post',
        data: { id }
    })
}