"""
免费AI生图工具，对接Pollinations公开API，不需要API密钥
支持多种开源模型：SDXL、Flux、Realistic Vision等
"""
import os
import requests
from urllib.parse import quote
from tools.registry import registry

def download_image(url, save_dir=os.path.expanduser("~/.hermes/generated_images")):
    """下载图片到本地"""
    os.makedirs(save_dir, exist_ok=True)
    filename = f"gen_{int(os.times()[4])}.png"
    save_path = os.path.join(save_dir, filename)
    
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return save_path

def generate_image(prompt: str, model: str = "flux", width: int = 1024, height: int = 1024):
    # 模型映射
    model_map = {
        "flux": "flux",
        "sdxl": "sdxl",
        "realistic-vision": "realistic-vision-v5-1",
        "anime": "anything-v5",
        "cartoon": "toon-animediff-v2"
    }
    model_name = model_map.get(model.lower(), "flux")
    
    # 构造请求URL
    encoded_prompt = quote(prompt)
    api_url = f"https://image.pollinations.ai/{encoded_prompt}?model={model_name}&width={width}&height={height}&nologo=true"
    
    try:
        # 下载图片到本地
        local_path = download_image(api_url)
        return {
            "success": True,
            "prompt": prompt,
            "model": model_name,
            "image_url": api_url,
            "local_path": local_path,
            "message": f"✅ 图片生成成功，本地路径：{local_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "❌ 图片生成失败，请稍后重试"
        }

# 工具schema定义
IMAGE_GEN_SCHEMA = {
    "name": "generate_image",
    "description": "根据文字描述生成AI图片，不需要API密钥，完全免费，支持flux/sdxl/写实/动漫/卡通等多种风格",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "图片描述，尽量详细，可以包含风格、画质要求等，建议用英文效果更好"
            },
            "model": {
                "type": "string",
                "description": "可选，生成模型，默认用flux（效果最好），可选值：flux, sdxl, realistic-vision, anime, cartoon",
                "default": "flux"
            },
            "width": {
                "type": "integer",
                "description": "可选，图片宽度，默认1024",
                "default": 1024
            },
            "height": {
                "type": "integer",
                "description": "可选，图片高度，默认1024",
                "default": 1024
            }
        },
        "required": ["prompt"]
    }
}

def _handle_generate_image(args, **kw):
    return generate_image(
        prompt=args.get("prompt"),
        model=args.get("model", "flux"),
        width=args.get("width", 1024),
        height=args.get("height", 1024)
    )

def _check_image_gen_requirements():
    return True, ""

# 注册工具
registry.register(
    name="generate_image",
    toolset="media",
    schema=IMAGE_GEN_SCHEMA,
    handler=_handle_generate_image,
    check_fn=_check_image_gen_requirements,
    emoji="🖼️",
    max_result_size_chars=1000,
)
