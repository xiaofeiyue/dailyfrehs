


from django.core.mail import send_mail

from celery_tasks.main import app


@app.task
def celery_send_email_action(email):
    # 使用ｄｊａｎｇｏ里面send_mail 发送邮件

    # subject,:主题
    #  message, :内容
    # from_email,发件人
    #  recipient_list:收件人
    subject = '你好啊!欢迎'

    message = ""
    from_email = '<wangyfmy@126.com>'
    recipient_list = [email]

    html_message = "<a href='#'>欢迎<a/>"

    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              fail_silently=False,
              auth_user=None,
              auth_password=None,
              connection=None,
              html_message=html_message)
    # html_message 可以设置html


pass