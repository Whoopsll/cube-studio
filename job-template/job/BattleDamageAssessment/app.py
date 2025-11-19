import os
import random
import time

from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__)

# 使用绝对路径，确保容器或不同工作目录下也能正确访问资源文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENE_DIR = os.path.join(BASE_DIR, "scenes")  # 场景图片（毁伤前）
DAMAGE_DIR = os.path.join(BASE_DIR, "unidentified")  # 毁伤图片（上传后）
RESULT_DIR = os.path.join(BASE_DIR, "identified")  # 识别结果（检测后）

# 确保文件夹存在
for folder in (SCENE_DIR, DAMAGE_DIR, RESULT_DIR):
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    前端上传毁伤图片（真正的文件并不保存），
    我们在本地文件夹里找对应的场景图片、毁伤图片和识别结果返回。
    """
    data = request.get_json()
    scene_id = data.get('scene_id')  # 场景ID，例如 "1" 对应 1.png
    filename = data.get('filename')  # 文件名，例如 "1.png"
    
    if not scene_id:
        return jsonify({'error': '缺少场景ID'}), 400
    if not filename:
        return jsonify({'error': '缺少文件名'}), 400

    # 所有图片都使用相同的文件名（基于场景ID）
    scene_path = os.path.join(SCENE_DIR, filename)
    damage_path = os.path.join(DAMAGE_DIR, filename)
    result_path = os.path.join(RESULT_DIR, filename)

    # 检查文件是否存在
    if not os.path.isfile(scene_path):
        return jsonify({'error': f'scenes 中找不到场景图片 {filename}'}), 404
    if not os.path.isfile(damage_path):
        return jsonify({'error': f'unidentified 中找不到毁伤图片 {filename}'}), 404
    if not os.path.isfile(result_path):
        return jsonify({'error': f'identified 中找不到识别结果 {filename}'}), 404

    # 模拟检测耗时 3~15 s
    sleep_time = random.randint(3, 15)
    time.sleep(sleep_time)

    # 返回三张图片的可访问 URL 及文字
    return jsonify({
        'scene_url'  : f'/image/{filename}?folder=scene',   # 场景图片（毁伤前）
        'damage_url' : f'/image/{filename}?folder=damage',  # 毁伤图片（上传后）
        'result_url' : f'/image/{filename}?folder=result',  # 识别结果（检测后）
        'texts'    : [
            f'检测完成，耗时 {sleep_time} 秒',
            '毁伤等级：高',
            '建议：立即修复'
        ]
    })

@app.route('/image/<path:filename>')
def serve_image(filename):
    """统一供图接口，根据folder参数返回对应文件夹的图片"""
    folder = request.args.get('folder')
    if folder == 'scene':
        return send_from_directory(SCENE_DIR, filename)
    if folder == 'damage':
        return send_from_directory(DAMAGE_DIR, filename)
    if folder == 'result':
        return send_from_directory(RESULT_DIR, filename)
    return '参数错误', 400


def run():
    """启动 Flask 应用，支持环境变量配置"""
    host = os.getenv("HOST", os.getenv("SERVER_IP", "0.0.0.0"))
    port = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8080")))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()