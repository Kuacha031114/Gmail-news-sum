from openai import OpenAI, APIError, APIConnectionError, RateLimitError

class EmailSummarizer:
    """
    使用 OpenAI API 对邮件内容进行总结。
    """
    def __init__(self, api_key):
        """
        初始化 EmailSummarizer。
        :param api_key: OpenAI API 密钥
        """
        
        self.client = OpenAI(
            base_url="https://api2.aigcbest.top/v1",
            api_key=api_key
            )  # 实例化 OpenAI 客户端

    def summarize_email(self, subjects, bodies, senders):
        """
        对邮件内容进行总结。
        :param subject: 邮件主题
        :param body: 邮件正文
        :param sender: 邮件发送者
        :return: GPT 生成的总结
        """
        # 创建 Prompt
        prompt = f"""
The news email details are as follows:

Sender: {senders[0]}
Subject: {subjects[0]}
Body:
{bodies[0]}

Sender: {senders[1]}
Subject: {subjects[1]}
Body:
{bodies[1]}

Sender: {senders[2]}
Subject: {subjects[2]}
Body:
{bodies[2]}

Please write a 600-800 word summary based on the above news content. And tell me the relevant news time at the beginning.
"""

        try:
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an news email summarization assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # 提取 GPT 的回复
            summary = response.choices[0].message.content.strip()
            return summary

        except APIConnectionError as e:
            print(f"网络连接错误: {e}")
            return "Error: Unable to summarize email due to network issues."

        except RateLimitError as e:
            print(f"请求超出限制: {e}")
            return "Error: API rate limit exceeded. Please try again later."

        except APIError as e:
            print(f"API 错误: {e}")
            return "Error: An error occurred while summarizing the email."

        except Exception as e:
            print(f"未知错误: {e}")
            return "Error: An unexpected error occurred."

