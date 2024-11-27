import os
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

# 定义权限范围
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class GmailHandler:
    def __init__(self, proxy_host=None, proxy_port=None):
        """
        初始化 GmailHandler，用于处理 Gmail 操作。
        :param proxy_host: 代理主机地址（可选）
        :param proxy_port: 代理端口（可选）
        """
        self.creds = None
        self.service = None
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

    def authenticate(self):
        """
        进行 Gmail API 身份认证，并构建服务。
        """
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        # 构建 Gmail 服务
        if self.proxy_host and self.proxy_port:
            import httplib2
            import google_auth_httplib2
            proxy_info = httplib2.ProxyInfo(
                proxy_type=httplib2.socks.PROXY_TYPE_SOCKS5,
                proxy_host=self.proxy_host,
                proxy_port=self.proxy_port,
            )
            http = httplib2.Http(proxy_info=proxy_info, timeout=60)
            authed_http = google_auth_httplib2.AuthorizedHttp(self.creds, http=http)
            self.service = build("gmail", "v1", http=authed_http)
        else:
            self.service = build("gmail", "v1", credentials=self.creds)

    def search_messages(self, query, max_results=10):
        """
        使用查询字符串搜索邮件。
        :param query: 搜索字符串（例如 'from:user@example.com'）
        :param max_results: 最大返回结果数量
        :return: 邮件列表（包含 ID）
        """
        try:
            results = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
            return results.get("messages", [])
        except HttpError as error:
            print(f"Error searching messages: {error}")
            return []

    def get_message_details(self, message_id):
        """
        根据邮件 ID 获取详细信息。
        :param message_id: 邮件 ID
        :return: 邮件详情
        """
        try:
            return self.service.users().messages().get(userId="me", id=message_id, format="full").execute()
        except HttpError as error:
            print(f"Error fetching message details: {error}")
            return None

    def extract_email_content(self, message):
        """
        提取邮件的主题、正文和附件信息。
        :param message: 邮件详情
        :return: 邮件内容（主题、正文、附件）
        """
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        parts = payload.get("parts", [])

        # 提取主题
        subject = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")

        # 提取发件人
        sender = next((header["value"] for header in headers if header["name"] == "From"), "Unknown Sender")

        # 提取正文
        body = ""
        for part in parts:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            elif part["mimeType"] == "text/html":
                html_content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                soup = BeautifulSoup(html_content, "html.parser")
                body = soup.get_text(strip=True)

        # 提取附件
        attachments = []
        for part in parts:
            if part.get("filename"):
                attachment_id = part["body"].get("attachmentId")
                if attachment_id:
                    attachments.append({"filename": part["filename"], "attachment_id": attachment_id})

        return subject, sender, body, attachments

    def save_attachments(self, message_id, attachments, save_dir="attachments"):
        """
        保存邮件的附件到指定目录。
        :param message_id: 邮件 ID
        :param attachments: 附件信息列表
        :param save_dir: 保存目录
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for attachment in attachments:
            attachment_id = attachment["attachment_id"]
            filename = attachment["filename"]

            attachment_data = self.service.users().messages().attachments().get(
                userId="me", messageId=message_id, id=attachment_id
            ).execute()

            file_data = base64.urlsafe_b64decode(attachment_data["data"])

            # 保存附件
            filepath = os.path.join(save_dir, filename)
            with open(filepath, "wb") as f:
                f.write(file_data)
            print(f"Attachment saved: {filepath}")