# -*- coding: utf-8 -*-
import logging
import base64


def image_to_base64(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        logging.warning(f"无法读取图片 {image_path}: {e}")
        return None


def image_html_content(image_path):
    html_content = f'<div style="margin: 10px 0;">' \
                   f'<h4>{image_path}</h4>' \
                   f'<img src="{image_to_base64(image_path)}" style="max-width: 400px; border: 1px solid #ccc;"/>' \
                   f'</div>'

    return html_content
