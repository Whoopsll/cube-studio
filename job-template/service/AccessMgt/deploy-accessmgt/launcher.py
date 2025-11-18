import os
import sys
import argparse
import datetime
import json
import time
import requests
import pysnooper
from kubernetes import client, config
from kubernetes.client.rest import ApiException

KFJ_CREATOR = os.getenv('KFJ_CREATOR', 'admin')
host = os.getenv('HOST', os.getenv('KFJ_MODEL_REPO_API_URL', 'http://kubeflow-dashboard.infra')).strip('/')

def create_accessmgt_virtualservice(namespace='service', service_name='accessmgt-backend', service_port=10086):
    """创建 VirtualService，将 /api/accessmgt 路径路由到后端服务"""
    try:
        # 加载 Kubernetes 配置
        try:
            config.load_incluster_config()  # 在 Pod 内运行
        except:
            config.load_kube_config()  # 本地运行
        
        # 创建 CustomObjectsApi 客户端
        api = client.CustomObjectsApi()
        
        # VirtualService 配置
        vs_body = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {
                "name": "accessmgt-api-route",
                "namespace": namespace
            },
            "spec": {
                "gateways": [
                    "kubeflow/kubeflow-gateway"
                ],
                "hosts": [
                    "*"
                ],
                "http": [
                    {
                        "match": [
                            {
                                "uri": {
                                    "prefix": "/api/accessmgt"
                                }
                            }
                        ],
                        "rewrite": {
                            "uri": "/"
                        },
                        "route": [
                            {
                                "destination": {
                                    "host": f"{service_name}.{namespace}.svc.cluster.local",
                                    "port": {
                                        "number": service_port
                                    }
                                }
                            }
                        ],
                        "timeout": "300s"
                    }
                ]
            }
        }
        
        # 尝试创建或更新 VirtualService
        try:
            # 先尝试获取现有的 VirtualService
            api.get_namespaced_custom_object(
                group="networking.istio.io",
                version="v1alpha3",
                namespace=namespace,
                plural="virtualservices",
                name="accessmgt-api-route"
            )
            # 如果存在，则更新
            print(f'更新 VirtualService: accessmgt-api-route')
            api.replace_namespaced_custom_object(
                group="networking.istio.io",
                version="v1alpha3",
                namespace=namespace,
                plural="virtualservices",
                name="accessmgt-api-route",
                body=vs_body
            )
            print('VirtualService 更新成功：/api/accessmgt -> 后端服务')
        except ApiException as e:
            if e.status == 404:
                # 不存在，创建新的
                print(f'创建 VirtualService: accessmgt-api-route')
                api.create_namespaced_custom_object(
                    group="networking.istio.io",
                    version="v1alpha3",
                    namespace=namespace,
                    plural="virtualservices",
                    body=vs_body
                )
                print('VirtualService 创建成功：/api/accessmgt -> 后端服务')
            else:
                print(f'创建 VirtualService 失败: {e}')
    except Exception as e:
        print(f'创建 VirtualService 时出错: {e}')
        print('提示：可以手动创建 VirtualService，见 README.md')

@pysnooper.snoop()
def deploy(**kwargs):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': KFJ_CREATOR
    }

    # 获取项目组
    url = host + "/project_modelview/api/?form_data=" + json.dumps({
        "filters": [
            {
                "col": "name",
                "opr": "eq",
                "value": kwargs['project_name']
            }
        ]
    })
    res = requests.get(url, headers=headers)
    exist_project = res.json().get('result', {}).get('data', [])
    if not exist_project:
        print('不存在项目组')
        return
    exist_project = exist_project[0]

    # 部署后端服务
    backend_service_name = kwargs.get('backend_service_name', 'accessmgt-backend')
    backend_model_version = kwargs.get('backend_model_version', datetime.datetime.now().strftime('v%Y.%m.%d.1'))
    
    # 查询后端服务是否存在
    url = host + "/inferenceservice_modelview/api/?form_data=" + json.dumps({
        "filters": [
            {
                "col": "model_name",
                "opr": "eq",
                "value": backend_service_name
            },
            {
                "col": "model_version",
                "opr": "eq",
                "value": backend_model_version
            }
        ]
    })
    res = requests.get(url, headers=headers, allow_redirects=False)
    
    if res.status_code == 200:
        backend_payload = {
            'model_name': backend_service_name,
            'model_version': backend_model_version,
            'model_path': '',
            'label': kwargs.get('backend_label', 'AccessMgt 后端服务'),
            'project': exist_project['id'],
            'images': kwargs['backend_images'],
            'working_dir': kwargs.get('backend_working_dir', ''),
            'command': kwargs.get('backend_command', ''),
            'args': kwargs.get('backend_args', ''),
            'env': kwargs.get('backend_env', 'MYSQL_HOST=mysql-service.infra\nMYSQL_PORT=3306\nMYSQL_USER=root\nMYSQL_PASSWORD=admin\nMYSQL_DB=AccessDB'),
            'resource_memory': kwargs.get('backend_resource_memory', '2G'),
            'resource_cpu': kwargs.get('backend_resource_cpu', '2'),
            'resource_gpu': kwargs.get('backend_resource_gpu', '0'),
            'min_replicas': kwargs.get('backend_replicas', '1'),
            'max_replicas': kwargs.get('backend_replicas', '1'),
            'ports': kwargs.get('backend_ports', '10086'),
            'volume_mount': kwargs.get('backend_volume_mount', ''),
            'inference_config': kwargs.get('backend_inference_config', ''),
            'host': kwargs.get('backend_host', ''),  # 后端服务域名，留空使用默认域名
            'hpa': kwargs.get('backend_hpa', ''),
            'service_type': kwargs.get('backend_service_type', 'serving'),
            'metrics': kwargs.get('backend_metrics', ''),
            'health': kwargs.get('backend_health', '10086:/docs')
        }

        exist_services = res.json().get('result', {}).get('data', [])
        backend_service = None
        
        if not exist_services:
            # 创建后端服务
            url = host + "/inferenceservice_modelview/api/"
            res = requests.post(url, headers=headers, json=backend_payload, allow_redirects=False)
            if res.status_code == 200:
                backend_service = res.json().get('result', {})
            else:
                print(f'后端服务创建失败: {res.content}')
                exit(1)
        else:
            # 更新后端服务
            exist_service = exist_services[0]
            url = host + "/inferenceservice_modelview/api/%s" % exist_service['id']
            res = requests.put(url, headers=headers, json=backend_payload, allow_redirects=False)
            if res.status_code == 200:
                backend_service = res.json().get('result', {})
            else:
                print(f'后端服务更新失败: {res.content}')
                exit(1)

        if backend_service:
            time.sleep(5)
            print(f'后端服务信息: {backend_service}')
            url = host + "/inferenceservice_modelview/api/deploy/prod/%s" % backend_service['id']
            res = requests.get(url, headers=headers, allow_redirects=False)
            if res.status_code in [302, 200]:
                print('后端服务部署成功')
                
                # 创建 VirtualService，将 /api/accessmgt 路由到后端服务
                # InferenceService 默认部署在 service 命名空间
                backend_namespace = backend_service.get('namespace') or 'service'
                create_accessmgt_virtualservice(
                    namespace=backend_namespace,
                    service_name=backend_service_name,
                    service_port=int(kwargs.get('backend_ports', '10086'))
                )
            else:
                print(f'后端服务部署失败: {res.content}')
                exit(1)

    # 部署前端1 (pg_vue3_pgjg)
    frontend1_service_name = kwargs.get('frontend1_service_name', 'accessmgt-fe-pgjg')
    frontend1_model_version = kwargs.get('frontend1_model_version', datetime.datetime.now().strftime('v%Y.%m.%d.1'))
    
    url = host + "/inferenceservice_modelview/api/?form_data=" + json.dumps({
        "filters": [
            {
                "col": "model_name",
                "opr": "eq",
                "value": frontend1_service_name
            },
            {
                "col": "model_version",
                "opr": "eq",
                "value": frontend1_model_version
            }
        ]
    })
    res = requests.get(url, headers=headers, allow_redirects=False)
    
    if res.status_code == 200:
        frontend1_payload = {
            'model_name': frontend1_service_name,
            'model_version': frontend1_model_version,
            'model_path': '',
            'label': kwargs.get('frontend1_label', 'AccessMgt 前端-PGJG'),
            'project': exist_project['id'],
            'images': kwargs['frontend1_images'],
            'working_dir': '',
            'command': '',
            'args': '',
            'env': kwargs.get('frontend1_env', ''),
            'resource_memory': kwargs.get('frontend1_resource_memory', '512Mi'),
            'resource_cpu': kwargs.get('frontend1_resource_cpu', '0.5'),
            'resource_gpu': '0',
            'min_replicas': kwargs.get('frontend1_replicas', '1'),
            'max_replicas': kwargs.get('frontend1_replicas', '1'),
            'ports': '80',
            'volume_mount': '',
            'inference_config': '',
            'host': kwargs.get('frontend1_host', ''),
            'hpa': '',
            'service_type': 'serving',
            'metrics': '',
            'health': '80:/'
        }

        exist_services = res.json().get('result', {}).get('data', [])
        frontend1_service = None
        
        if not exist_services:
            url = host + "/inferenceservice_modelview/api/"
            res = requests.post(url, headers=headers, json=frontend1_payload, allow_redirects=False)
            if res.status_code == 200:
                frontend1_service = res.json().get('result', {})
            else:
                print(f'前端1服务创建失败: {res.content}')
                exit(1)
        else:
            exist_service = exist_services[0]
            url = host + "/inferenceservice_modelview/api/%s" % exist_service['id']
            res = requests.put(url, headers=headers, json=frontend1_payload, allow_redirects=False)
            if res.status_code == 200:
                frontend1_service = res.json().get('result', {})
            else:
                print(f'前端1服务更新失败: {res.content}')
                exit(1)

        if frontend1_service:
            time.sleep(5)
            print(f'前端1服务信息: {frontend1_service}')
            url = host + "/inferenceservice_modelview/api/deploy/prod/%s" % frontend1_service['id']
            res = requests.get(url, headers=headers, allow_redirects=False)
            if res.status_code in [302, 200]:
                print('前端1服务部署成功')
            else:
                print(f'前端1服务部署失败: {res.content}')

    # 部署前端2 (pg_vue3_zbdj)
    frontend2_service_name = kwargs.get('frontend2_service_name', 'accessmgt-fe-zbdj')
    frontend2_model_version = kwargs.get('frontend2_model_version', datetime.datetime.now().strftime('v%Y.%m.%d.1'))
    
    url = host + "/inferenceservice_modelview/api/?form_data=" + json.dumps({
        "filters": [
            {
                "col": "model_name",
                "opr": "eq",
                "value": frontend2_service_name
            },
            {
                "col": "model_version",
                "opr": "eq",
                "value": frontend2_model_version
            }
        ]
    })
    res = requests.get(url, headers=headers, allow_redirects=False)
    
    if res.status_code == 200:
        frontend2_payload = {
            'model_name': frontend2_service_name,
            'model_version': frontend2_model_version,
            'model_path': '',
            'label': kwargs.get('frontend2_label', 'AccessMgt 前端-ZBDJ'),
            'project': exist_project['id'],
            'images': kwargs['frontend2_images'],
            'working_dir': '',
            'command': '',
            'args': '',
            'env': kwargs.get('frontend2_env', ''),
            'resource_memory': kwargs.get('frontend2_resource_memory', '512Mi'),
            'resource_cpu': kwargs.get('frontend2_resource_cpu', '0.5'),
            'resource_gpu': '0',
            'min_replicas': kwargs.get('frontend2_replicas', '1'),
            'max_replicas': kwargs.get('frontend2_replicas', '1'),
            'ports': '80',
            'volume_mount': '',
            'inference_config': '',
            'host': kwargs.get('frontend2_host', ''),
            'hpa': '',
            'service_type': 'serving',
            'metrics': '',
            'health': '80:/'
        }

        exist_services = res.json().get('result', {}).get('data', [])
        frontend2_service = None
        
        if not exist_services:
            url = host + "/inferenceservice_modelview/api/"
            res = requests.post(url, headers=headers, json=frontend2_payload, allow_redirects=False)
            if res.status_code == 200:
                frontend2_service = res.json().get('result', {})
            else:
                print(f'前端2服务创建失败: {res.content}')
                exit(1)
        else:
            exist_service = exist_services[0]
            url = host + "/inferenceservice_modelview/api/%s" % exist_service['id']
            res = requests.put(url, headers=headers, json=frontend2_payload, allow_redirects=False)
            if res.status_code == 200:
                frontend2_service = res.json().get('result', {})
            else:
                print(f'前端2服务更新失败: {res.content}')
                exit(1)

        if frontend2_service:
            time.sleep(5)
            print(f'前端2服务信息: {frontend2_service}')
            url = host + "/inferenceservice_modelview/api/deploy/prod/%s" % frontend2_service['id']
            res = requests.get(url, headers=headers, allow_redirects=False)
            if res.status_code in [302, 200]:
                print('前端2服务部署成功')
            else:
                print(f'前端2服务部署失败: {res.content}')

    print('所有服务部署完成！')


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("deploy accessmgt launcher")
    arg_parser.add_argument('--project_name', type=str, help="所属项目组", default='public')
    
    # 后端参数
    arg_parser.add_argument('--backend_service_name', type=str, help="后端服务名", default='accessmgt-backend')
    arg_parser.add_argument('--backend_model_version', type=str, help="后端版本号", default=datetime.datetime.now().strftime('v%Y.%m.%d.1'))
    arg_parser.add_argument('--backend_label', type=str, help="后端服务描述", default='AccessMgt 后端服务')
    arg_parser.add_argument('--backend_images', type=str, help="后端镜像", required=True)
    arg_parser.add_argument('--backend_command', type=str, help="后端启动命令", default='')
    arg_parser.add_argument('--backend_env', type=str, help="后端环境变量", default='MYSQL_HOST=mysql-service.infra\nMYSQL_PORT=3306\nMYSQL_USER=root\nMYSQL_PASSWORD=admin\nMYSQL_DB=AccessDB')
    arg_parser.add_argument('--backend_resource_memory', type=str, help="后端内存", default='2G')
    arg_parser.add_argument('--backend_resource_cpu', type=str, help="后端CPU", default='2')
    arg_parser.add_argument('--backend_resource_gpu', type=str, help="后端GPU", default='0')
    arg_parser.add_argument('--backend_replicas', type=str, help="后端副本数", default='1')
    arg_parser.add_argument('--backend_ports', type=str, help="后端端口", default='10086')
    arg_parser.add_argument('--backend_host', type=str, help="后端域名", default='')
    arg_parser.add_argument('--backend_health', type=str, help="后端健康检查", default='10086:/docs')
    
    # 前端1参数
    arg_parser.add_argument('--frontend1_service_name', type=str, help="前端1服务名", default='accessmgt-fe-pgjg')
    arg_parser.add_argument('--frontend1_model_version', type=str, help="前端1版本号", default=datetime.datetime.now().strftime('v%Y.%m.%d.1'))
    arg_parser.add_argument('--frontend1_label', type=str, help="前端1服务描述", default='AccessMgt 前端-PGJG')
    arg_parser.add_argument('--frontend1_images', type=str, help="前端1镜像", required=True)
    arg_parser.add_argument('--frontend1_resource_memory', type=str, help="前端1内存", default='512Mi')
    arg_parser.add_argument('--frontend1_resource_cpu', type=str, help="前端1CPU", default='0.5')
    arg_parser.add_argument('--frontend1_replicas', type=str, help="前端1副本数", default='1')
    arg_parser.add_argument('--frontend1_host', type=str, help="前端1域名", default='')
    
    # 前端2参数
    arg_parser.add_argument('--frontend2_service_name', type=str, help="前端2服务名", default='accessmgt-fe-zbdj')
    arg_parser.add_argument('--frontend2_model_version', type=str, help="前端2版本号", default=datetime.datetime.now().strftime('v%Y.%m.%d.1'))
    arg_parser.add_argument('--frontend2_label', type=str, help="前端2服务描述", default='AccessMgt 前端-ZBDJ')
    arg_parser.add_argument('--frontend2_images', type=str, help="前端2镜像", required=True)
    arg_parser.add_argument('--frontend2_resource_memory', type=str, help="前端2内存", default='512Mi')
    arg_parser.add_argument('--frontend2_resource_cpu', type=str, help="前端2CPU", default='0.5')
    arg_parser.add_argument('--frontend2_replicas', type=str, help="前端2副本数", default='1')
    arg_parser.add_argument('--frontend2_host', type=str, help="前端2域名", default='')

    args = arg_parser.parse_args()
    deploy(**args.__dict__)

