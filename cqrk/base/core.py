import cqrk.config.config as config

from datetime import datetime
import logging

import os
import colorlog

class core:
    def __init__(self,DEBUG=None):
        self.ROOT    = os.getcwd()

        # 环境检测
        os.makedirs(self.ROOT+'/user/',           exist_ok=True)
        os.makedirs(self.ROOT+'/cache/log/',      exist_ok=True)
        os.makedirs(self.ROOT+'/libs/data/',      exist_ok=True)
        os.makedirs(self.ROOT+'/libs/templates/', exist_ok=True)
        os.makedirs(self.ROOT+'/libs/static/',    exist_ok=True)
        os.makedirs(self.ROOT+'/cookies/',    exist_ok=True)


        self.logger   = logging.getLogger(__name__)
        self.config   = config

        if not isinstance(DEBUG,bool):
            DEBUG = self.config.DEBUG
        
        if DEBUG:
            Level = logging.DEBUG
        else:
            Level = logging.INFO

        log_colors_config = {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        # 输出到控制台
        console_handler = logging.StreamHandler()
        # 输出到文件
        now = datetime.now()
        file_handler = logging.FileHandler(filename=f'{self.ROOT}/cache/{now.strftime("%Y-%m-%d")}.log', mode='a', encoding='utf8')
    
        # 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        self.logger.setLevel(Level)
        console_handler.setLevel(Level)
        file_handler.setLevel(logging.INFO)
    
        # 日志输出格式
        file_format = "[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d][%(funcName)s] %(message)s"
        

        log_format = '%(log_color)s [%(filename)s:%(lineno)d][%(funcName)s] %(asctime)s -> %(message)s'

        file_formatter = logging.Formatter(
            fmt='{}'.format(file_format),
            datefmt='%Y-%m-%d  %H:%M:%S'
        )
        console_formatter = colorlog.ColoredFormatter(
            fmt='{}'.format(log_format),
            log_colors=log_colors_config
        )

        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
    
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
        console_handler.close()
        file_handler.close()