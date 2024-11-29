from flask import Flask, request, jsonify, send_from_directory
from modules.gmail_handler import GmailHandler
from modules.summarizer import EmailSummarizer
import os

# 初始化 Flask 应用
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# 跨域支持（前端和后端分离时需要）
from flask_cors import CORS
CORS(app)

# 设置 OpenAI API 密钥
OPENAI_API_KEY = os.environ['QIANDUODUOAPI']

# 初始化 GmailHandler 和 Summarizer
gmail = GmailHandler(proxy_host="127.0.0.1", proxy_port=7890)
gmail.authenticate()
summarizer = EmailSummarizer(api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    """
    根路径，返回 index.html 页面
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/search_emails', methods=['POST'])
def search_emails():
    """
    查询邮件接口
    """
    data = request.json
    sender_email = data.get('sender_email')
    max_results = data.get('max_results', 3)

    messages = gmail.search_messages(query=f'from:"{sender_email}"', max_results=max_results)

    if not messages:
        return jsonify({"error": "No messages found."}), 404

    email_details = []
    for message in messages:
        message_id = message["id"]
        message_details = gmail.get_message_details(message_id)

        if message_details:
            subject, sender, body, attachments = gmail.extract_email_content(message_details)
            email_details.append({
                "subject": subject,
                "sender": sender,
                "body": body,
                "attachments": attachments
            })

    return jsonify(email_details)

@app.route('/api/summarize_emails', methods=['POST'])
def summarize_emails():
    """
    总结邮件内容接口
    """
    data = request.json
    subjects = data.get('subjects', [])
    bodies = data.get('bodies', [])
    senders = data.get('senders', [])

    summary = summarizer.summarize_email(subjects, bodies, senders)
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)