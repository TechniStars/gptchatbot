import multiprocessing

from src.app.app import launch_api
from src.config.config import CONFIG
from src.setup.setup_data import setup_data
from src.telegram_bot.bot import launch_telegram

if __name__ == '__main__':
    setup_data()
    multiprocessing.set_start_method('spawn', force=True)
    if CONFIG['global_config']['features']['enable_api']:
        print("Starting API...")
        api_process = multiprocessing.Process(target=launch_api)
        api_process.start()

    if CONFIG['global_config']['features']['enable_telegram']:
        print("Starting Telegram...")
        telegram_process = multiprocessing.Process(target=launch_telegram)
        telegram_process.start()
