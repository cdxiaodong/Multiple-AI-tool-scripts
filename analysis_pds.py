import os
import PyPDF2
import openai
import time
from tqdm import tqdm
import argparse

# 初始系统消息
system_message = """
你是一名信息安全专家 帮我分析我提供的ppt中的内容并分别生成标题和 摘要
"""

# 标记字符串
MARK_STRING = "auto_aied"

# 读取PDF文件并提取文本内容
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        pages_text = []

        for page_num in tqdm(range(len(reader.pages)), desc="Extracting text from PDF"):
            page = reader.pages[page_num]
            page_text = page.extract_text().strip()
            pages_text.append(page_text)

    return pages_text

# 使用OpenAI API生成摘要
def generate_summary_with_openai(text):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": text}
    ]

    start_time = time.time()
    response = openai.ChatCompletion.create(
        model="gpt-4.0-o",
        messages=messages
    )
    end_time = time.time()
    elapsed_time = end_time - start_time

    result = response.choices[0].message.content.strip()
    print(f"Generated summary in {elapsed_time:.2f} seconds")
    return result

# 生成Markdown内容
def generate_markdown(pages_text):
    markdown_content = ""

    # 将多个页面的内容合并成一个请求
    batch_size = 15  # 每15页合并成一个请求
    summaries = []

    for i in tqdm(range(0, len(pages_text), batch_size), desc="Processing pages"):
        batch_text = "\n".join(pages_text[i:i + batch_size])
        summary = generate_summary_with_openai(batch_text)
        summaries.append(summary)

    # 合并所有摘要
    combined_summary = "\n".join(summaries)
    final_summary = generate_summary_with_openai(combined_summary)

    # 生成Markdown内容
    markdown_content += f"{final_summary}\n\n"

    return markdown_content

# 保存Markdown文件
def save_markdown_file(markdown_content, output_path):
    with open(output_path, "a", encoding="utf-8") as md_file:
        md_file.write(markdown_content)

# 重命名文件
def rename_file(pdf_path, mark_string):
    base_name, ext = os.path.splitext(pdf_path)
    new_name = f"{base_name}_{mark_string}{ext}"
    os.rename(pdf_path, new_name)
    return new_name

# 主函数
def main(pdf_folder_path, output_path, api_key):
    # 设置OpenAI API密钥
    openai.api_key = api_key

    # 清空输出文件
    with open(output_path, "w", encoding="utf-8") as md_file:
        md_file.write("")

    # 遍历文件夹中的所有PDF文件
    for pdf_file in tqdm(os.listdir(pdf_folder_path), desc="Processing PDFs"):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.normpath(os.path.join(pdf_folder_path, pdf_file))
            if MARK_STRING in pdf_file:
                print(f"Skipping already processed file: {pdf_file}")
                continue

            print(f"Starting analysis for {pdf_file}...")
            pages_text = extract_text_from_pdf(pdf_path)
            print(f"PDF extraction completed for {pdf_file}.")

            print(f"Starting Markdown generation for {pdf_file}...")
            markdown_content = generate_markdown(pages_text)
            print(f"Markdown generation completed for {pdf_file}.")

            # 添加PDF文件名作为大标题
            markdown_content = f"# {pdf_file}\n\n{markdown_content}"

            print(f"Saving Markdown content for {pdf_file}...")
            save_markdown_file(markdown_content, output_path)
            print(f"Markdown content saved for {pdf_file}.")

            # 重命名文件
            new_name = rename_file(pdf_path, MARK_STRING)
            print(f"Renamed file to: {new_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze PDFs and generate summaries.")
    parser.add_argument("pdf_folder_path", type=str, help="Path to the folder containing PDFs")
    parser.add_argument("output_path", type=str, help="Path to the output Markdown file")
    parser.add_argument("api_key", type=str, help="OpenAI API key")

    args = parser.parse_args()

    main(args.pdf_folder_path, args.output_path, args.api_key)
