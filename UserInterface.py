from datetime import date, datetime
from AutoDownloader import Downloader
import logging
import sys

class UI:
    def __init__(self, logger):
        self.ad = Downloader()
        self.logger = logger
    def launch(self):
        self.logger.info("Session initiates.")
        self.call_for_input()
        self.logger.info("Session terminates.")


    def call_for_input(self):
        while (1):
            
            print("Command options: " )
            print("-s yyyy-mm-dd  [download-path(full)] (download a specific day's files. Download path is optional)")
            print("-b yyyy-mm-dd yyyy-mm-dd [download-path(full)]   (download files in date range: both sides inclusive. Download path is optional)")
            print("-e         (exit)")
            

            ip = input(">>:")
            self.logger.debug("Command entered: " + ip)
            input_list = ip.split(sep = " ")
            if (ip == "-e"):
                self.logger.info("User inputs exit command.")
                break;
            try:
                self.parse(input_list)
            except Exception as e:
                print("Invalid command. Please check grammar")
                self.logger.info("User enters invalid command")
                self.logger.debug(e)
                continue
            
            self.logger.info("Command execution successful.")
            print("Command executed successfully")

    def parse(self, input_list):
        if (len(input_list) == 0):
            raise Exception()
        if (input_list[0] == "-s"):
            self.logger.info("Command type is single day downloads")
            dt = input_list[1]
            if (len(input_list) > 2):
                self.ad.download_path = input_list[2]
                self.ad.validate_base_path()
            dt = datetime.strptime(dt, '%Y-%m-%d').date()
            self.ad.download(dt)
            return

        if (input_list[0] == "-b"):
            self.logger.info("Command type is batch downloads")
            start = input_list[1]
            end = input_list[2]
            if (len(input_list) > 3):
                self.ad.download_path = input_list[3]
                self.ad.validate_base_path()
            start = datetime.strptime(start, '%Y-%m-%d').date()
            end = datetime.strptime(end, '%Y-%m-%d').date()
            self.ad.download_batch(start, end)
            return

        self.logger.info("Invalid command type identified.")
        raise Exception("Unrecognized input")

        


if __name__ == "__main__":

    root = logging.getLogger("auto_downloader")
    root.setLevel(logging.DEBUG)
    fh = logging.FileHandler("auto_downloader.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    root.addHandler(fh)
    root.addHandler(ch)
    ui = UI(root)
    ui.launch()