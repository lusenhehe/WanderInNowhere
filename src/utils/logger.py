import logging,os,datetime,sys
from src.paths import assets_path

def setup_logging():
    """
    setup_logging: 初始化日志系统，创建日志文件并配置日志记录格式和级别。
    日志文件保存在 Assets/Debug 目录下，文件名格式为 "日志_YYYYMMDD_HHMMSS.txt"。

    :return: 日志文件路径
    """
    # 确保目录存在
    log_dir = assets_path('Debug')
    os.makedirs(log_dir, exist_ok=True)

    # 生成文件名：日志_YYYYMMDD_HHMMSS.txt
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"日志_{timestamp}.txt")
    # 自定义级别名称
    logging.addLevelName(logging.INFO,    "Correct")
    logging.addLevelName(logging.WARNING, "Warning")
    logging.addLevelName(logging.ERROR,   "Error")
    logging.addLevelName(logging.DEBUG,   "Debug")
    # 配置日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    # 静默嘈杂的第三方 INFO 日志（例如 HTTP 请求跟踪）
    for noisy_name in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy_name).setLevel(logging.WARNING)
    # 一些 SDK 使用模块级日志记录器，具有通用名称
    for noisy_name in ("zai", "openai"):
        logging.getLogger(noisy_name).setLevel(logging.WARNING)
    logging.info("======日志系统初始化完成======")
    return log_file
logger = logging.getLogger("Game")
