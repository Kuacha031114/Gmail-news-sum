from modules.gmail_handler import GmailHandler
from modules.summarizer import EmailSummarizer
import os

# 设置 OpenAI API 密钥
OPENAI_API_KEY = os.environ['QIANDUODUOAPI']

def main():
    # 初始化 GmailHandler
    gmail = GmailHandler(proxy_host="127.0.0.1", proxy_port=7890)
    gmail.authenticate()

    # 初始化 EmailSummarizer
    summarizer = EmailSummarizer(api_key=OPENAI_API_KEY)

    # 搜索指定发件人的邮件
    sender_email = "Chen Guankun"
    messages = gmail.search_messages(query=f'from:"{sender_email}"', max_results=3)

    if not messages:
        print("No messages found.")
        return

    subjects = []
    bodies = []
    senders = []
    # 获取并处理邮件内容
    for message in messages:
        message_id = message["id"]
        message_details = gmail.get_message_details(message_id)

        if message_details:
            subject, sender, body, attachments = gmail.extract_email_content(message_details)
            
            subjects.append(subject)
            senders.append(sender)
            bodies.append(body)

            # 保存附件（如果有）
            if attachments:
                gmail.save_attachments(message_id, attachments)

    summary = summarizer.summarize_email(subjects, bodies, senders)

    print(summary)

if __name__ == "__main__":
    main()