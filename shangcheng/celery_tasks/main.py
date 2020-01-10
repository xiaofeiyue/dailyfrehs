"""
celery: 符合生产者　消费者　　设计模式


生产者:----就是任务---也就是函数
这个函数要被celery实例对象的task装饰
这个函数还需要celery的自动检测,只检测task.py的文件

队列
选择redis作为队列

消费者
通过指令就可以


celery　：　将这３者串联起来
"""
import os
from celery import Celery
# 1.我们要为celery的运行去创建Django环境,
# 这行代码可以去manage.py中去复制
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shangcheng.settings')
# 2.创建celery实例
app = Celery('celery_tasks')
# main 参数一般都是celery包名,因为包名是唯一的

# 3.让celery加载队列配置
app.config_from_object('celery_tasks.config')

# 自动检测
# 队列元素是任务的包路径
app.autodiscover_tasks(['celery_tasks.sms'])

# 5.通过指令创建消费者
# celery -A celery_tasks.main worker -l info