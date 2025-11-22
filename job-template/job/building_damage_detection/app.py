import gradio as gr
from ultralytics import YOLO
import cv2
import os

# --- 模型路径配置 ---
# 在 Docker 镜像内部，工作目录是 /app
# 所以模型路径是相对于 /app 的
MODEL_PATH = "models/best.pt"
CONF_THRESHOLD = 0.3

# 检查模型文件是否存在（这在容器内运行时也会执行）
if not os.path.exists(MODEL_PATH):
    print(f"[警告] 模型文件 '{MODEL_PATH}' 未找到。请确保 Dockerfile 正确复制了模型。")
    # 在实际部署中，如果模型不存在，应用应该优雅地处理或退出

# 加载模型
print("正在加载模型...")
try:
    model = YOLO(MODEL_PATH)
    print("模型加载完毕！")
except Exception as e:
    print(f"模型加载失败: {e}")
    raise

# --- 核心检测函数 ---
def detect_damage(input_image):
    """
    处理上传的图片并返回检测结果。
    input_image: Gradio 传入的 RGB 格式的 numpy 数组。
    """
    try:
        # 将 RGB 转换为 BGR 以适应 OpenCV
        img_bgr = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)
        
        # 执行预测
        results = model(img_bgr, conf=CONF_THRESHOLD, show=False)
        
        # 生成带标注的图像
        annotated_img_bgr = results[0].plot()
        
        # 将 BGR 转换回 RGB 以适应 Gradio 显示
        annotated_img_rgb = cv2.cvtColor(annotated_img_bgr, cv2.COLOR_BGR2RGB)
        
        # 统计检测到的目标数量
        detected_objects = results[0].boxes.shape[0]
        
        # 构建结果文本
        result_text = f"检测完成！\n在图像中找到了 {detected_objects} 个损伤区域。"
        
        # 返回原始图片、标注后的图片和结果文本
        return input_image, annotated_img_rgb, result_text

    except Exception as e:
        return None, None, f"处理图片时发生错误: {str(e)}"

# --- Gradio 界面 ---
with gr.Blocks(title="建筑损伤检测系统") as demo:
    gr.Markdown(
        """
        <h1 style="text-align: center; margin-bottom: 2rem;">建筑损伤检测系统</h1>
        <p style="text-align: center; color: #666;">上传一张建筑图片，系统将自动检测并识别其中的损伤区域。</p>
        """
    )
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            input_image = gr.Image(
                type="numpy",
                label="上传建筑图像",
                height=300
            )
            detect_btn = gr.Button("开始检测", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("<p style='text-align: center;'>原始图片</p>")
            output_original = gr.Image(label="", height=250)
            
            gr.Markdown("<p style='text-align: center;'>检测结果</p>")
            output_result = gr.Image(label="", height=250)
            
            output_text = gr.Textbox(label="检测信息", interactive=False)
    
    detect_btn.click(
        fn=detect_damage,
        inputs=input_image,
        outputs=[output_original, output_result, output_text]
    )

# --- 启动服务 ---
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,       # 监听在 7860 端口
        inbrowser=False         # 在容器环境中，通常不需要自动打开浏览器
    )