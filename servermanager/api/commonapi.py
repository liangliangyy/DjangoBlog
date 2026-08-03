import logging
import os

import openai

from servermanager.models import commands

logger = logging.getLogger(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')
if os.environ.get('HTTP_PROXY'):
    openai.proxy = os.environ.get('HTTP_PROXY')


class ChatGPT:

    @staticmethod
    def chat(prompt):
        try:
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                      messages=[{"role": "user", "content": prompt}])
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(e)
            return "服务器出错了"


class CommandHandler:
    def __init__(self):
        self.commands = commands.objects.all()

    def run(self, title):
        """
        运行命令
        :param title: 命令
        :return: 返回命令执行结果
        """
        # Security: Only execute pre-defined commands from database
        # Never execute arbitrary user input
        cmd = list(
            filter(
                lambda x: x.title.upper() == title.upper(),
                self.commands))
        if cmd:
            return self.__run_command__(cmd[0].command)
        else:
            return "未找到相关命令，请输入hepme获得帮助。"

    def __run_command__(self, cmd):
        """
        执行预定义的命令
        
        安全注意：
        1. 只执行数据库中预定义的命令
        2. 命令由管理员在后台配置
        3. 不接受任何用户输入作为命令参数
        """
        try:
            # Security: Use subprocess instead of os.popen for better control
            import subprocess
            # Set timeout to prevent long-running commands
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                check=False
            )
            if result.returncode == 0:
                return result.stdout if result.stdout else '命令执行成功'
            else:
                return f'命令执行失败: {result.stderr}'
        except subprocess.TimeoutExpired:
            return '命令执行超时'
        except Exception as e:
            logger.error(f'Command execution error: {e}')
            return '命令执行出错!'

    def get_help(self):
        rsp = ''
        for cmd in self.commands:
            rsp += '{c}:{d}\n'.format(c=cmd.title, d=cmd.describe)
        return rsp


if __name__ == '__main__':
    chatbot = ChatGPT()
    prompt = "写一篇1000字关于AI的论文"
    print(chatbot.chat(prompt))
