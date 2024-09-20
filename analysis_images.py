import pytesseract
from PIL import Image
import openai
import argparse

# 设置Tesseract可执行文件路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

# 初始系统消息
system_message = """
你现在是一网络安全专家。

要求: 用中文回复
"""

# 使用OCR解析图片中的文本
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# 使用OpenAI API生成回复
def generate_response_with_openai(text, api_key):
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4.0-o",
        messages=messages
    )
    return response.choices[0].message.content.strip()

# 主函数
def main(image_path, api_key):
    # 提取图片中的文本
    text = extract_text_from_image(image_path)
    print("OCR解析的文本：")
    print(text)

    # 使用OpenAI API生成回复
    response = generate_response_with_openai(text, api_key)
    print("OpenAI生成的回复：")
    print(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from image using OCR and generate response using OpenAI API.")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    parser.add_argument("api_key", type=str, help="OpenAI API key")

    args = parser.parse_args()

    main(args.image_path, args.api_key)
