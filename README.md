# Gmail-news-sum

简单的调用gmail api和openai api进行最近的邮件总结的小项目

暂且用的钱多多的api

clone下来之后需要自行登录Google cloud创建项目启用Gmail API然后下载credentials.josn放在根目录里

中国大陆用户需要把 backend\main.py 里面设置代理的端口改为自己代理的端口，目前使用的是clash的默认端口7890

然后在根目录运行

```
python backend\main.py
```

就可以访问网页前端了
