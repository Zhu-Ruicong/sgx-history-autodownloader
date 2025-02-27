# Tick https://links.sgx.com/1.0.0/derivatives-historical/4724/WEBPXTICK_DT.zip
# Tick structure https://links.sgx.com/1.0.0/derivatives-historical/4724/TickData_structure.dat
# TC https://links.sgx.com/1.0.0/derivatives-historical/4724/TC.txt
# TC structure https://links.sgx.com/1.0.0/derivatives-historical/4724/TC_structure.dat
from datetime import datetime, date, timedelta
import numpy as np
import requests
import os
import logging

class Downloader:
    def __init__(self):
        self.download_path = ""
        self.benchmark_index = 4724
        self.benchmark_date = date(2020,9,16)
        self.earliest_valid_index = 2755
        self.earliest_valid_date = date(2013,4,5)
        self.logger = logging.getLogger("auto_downloader.Downloader")
        
        self.tick_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/WEBPXTICK_DT.zip"
        self.tick_struct_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/TickData_structure.dat"
        self.tc_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/TC.txt"
        self.tc_struct_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/TC_structure.dat"

    def validate_base_path(self):
        if self.download_path == "":
            return
        
        if self.download_path[-1] != "/":
            self.download_path += "/"

        try:
            self.logger.debug("path tested is: " + self.download_path)
            if not os.path.exists(self.download_path):
                os.mkdir(self.download_path)
            open(self.download_path + "test.txt", "w")
            os.remove(self.download_path + "test.txt")
        except Exception as e:
            self.logger.debug(e)
            des = input("path provided is invalid. Would you like to respecify path? (Example: D:/downloads/   If not, default path is used. (y/n)")
            if (des == 'y'):
                self.download_path = input("please enter path: ")
                self.validate_base_path()
            else:
                self.download_path = ""
                print("Using Default path.")

    

    def download_file(self, url, filename):
        self.logger.info("Downloading: " + filename)
        local_filename = filename
        if self.download_path != "":
            local_filename = self.download_path + local_filename
        retries = 0
        while 1:
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192): 
                
                            f.write(chunk)

                self.logger.info("Download Completed: " + filename)
                return local_filename
            except:
                retries += 1
                if (retries > 5):
                    self.logger.error("Download for " + filename + " from " + url + " fails. Retrying." + " Retried 5 times, aborting")
                    break
                else:
                    self.logger.warning("Download for " + filename + " from " + url + " fails. Retrying.")
                    continue

    def download(self, dt):
        index = self.get_date_index(dt)
        if (index == None):
            self.logger.info("Item not found for " + dt.strftime("%Y-%m-%d"))
            return;
        self.download_file(self.tc_url.replace('DATE_INDEX', str(index)), "TC_" + dt.strftime("%Y%m%d") + ".txt")
        self.download_file(self.tick_url.replace('DATE_INDEX', str(index)), "WEBPXTICK_DT-" + dt.strftime("%Y%m%d") + ".zip")
        self.download_file(self.tick_struct_url.replace('DATE_INDEX', str(index)), "TC_structure_" + dt.strftime("%Y%m%d") + ".dat")
        self.download_file(self.tc_struct_url.replace('DATE_INDEX', str(index)), "TickData_structure_" + dt.strftime("%Y%m%d") + ".dat")

    def download_using_index(self, index):
        dt = self.get_date_from_index(index)
        self.download_file(self.tc_url.replace('DATE_INDEX', str(index)), "TC_" + dt.strftime("%Y%m%d") + ".txt")
        self.download_file(self.tick_url.replace('DATE_INDEX', str(index)), "WEBPXTICK_DT-" + dt.strftime("%Y%m%d") + ".zip")
        self.download_file(self.tick_struct_url.replace('DATE_INDEX', str(index)), "TC_structure_" + dt.strftime("%Y%m%d") + ".dat")
        self.download_file(self.tc_struct_url.replace('DATE_INDEX', str(index)), "TickData_structure_" + dt.strftime("%Y%m%d") + ".dat")


    def download_batch(self, start, end):
        start_index = self.get_first_valid_index_since_date(start)
        self.logger.debug("starting index is " + str(start_index))
        end_index = self.get_last_valid_index_before_date(end)
        self.logger.debug("ending index is " + str(end_index))
        for i in range(start_index, end_index + 1):
            dt = self.get_date_from_index(i)
            if dt == None:
                continue
            self.download_using_index(i)
               
    def get_first_valid_index_since_date(self, date):
        if (date < self.earliest_valid_date):
            return self.earliest_valid_index
        temp = self.get_date_index(date)
        conseq_count = 0
        while (temp == None):
            conseq_count += 1
            date = date + timedelta(days = 1)
            temp = self.get_date_index(date)
            if (conseq_count == 10):
                return None
        return temp


    def get_last_valid_index_before_date(self, date):
        temp = self.get_date_index(date)
        conseq_count = 0
        while (temp == None):
            conseq_count += 1
            date = date - timedelta(days = 1)
            temp = self.get_date_index(date)
            if (conseq_count == 10):
                return None
        return temp
            
    def get_date_from_index(self, index):
        url = self.tc_url.replace('DATE_INDEX', str(index))
        h = requests.head(url, allow_redirects=True)
        header = h.headers
        try:
            fetched_date = datetime.strptime(header.get("Content-Disposition")[24:-4], '%Y%m%d').date()
            return fetched_date
        except (Exception):
            return None
        

    def get_date_index(self, dt):
        if dt < self.earliest_valid_date:
            return None

        if (dt.year >= 2017):
            if dt > self.benchmark_date:
                index_estimate = 4724 + np.busday_count(self.benchmark_date, dt)
            else:
                index_estimate = 4724 - np.busday_count(dt, self.benchmark_date)

        else:
            index_estimate = 2755 + np.busday_count(self.earliest_valid_date, dt)
        return self.find_exact_index(index_estimate, dt)


    def find_exact_index(self, estimated_index, dt):
        temp = estimated_index
        direction = 0
        self.logger.debug("initial estimate is " + str(estimated_index))
        consecutive_error_count = 0
        while (1):
            url = self.tc_url.replace('DATE_INDEX', str(temp))
            h = requests.head(url, allow_redirects=True)
            header = h.headers
            try:
                fetched_date = datetime.strptime(header.get("Content-Disposition")[24:-4], '%Y%m%d').date()
            except (Exception):
                consecutive_error_count += 1
                if consecutive_error_count > 5:
                    return None
                if (direction == 0):
                    temp -= 1
                elif direction > 0:
                    temp += 1
                else:
                    temp -= 1
                continue

            consecutive_error_count = 0
            if (fetched_date == dt):
                break;
            if (direction == -2) or (direction == 2):
                    return None
            if (fetched_date < dt):
                if direction == -1:
                    direction = -2
                    temp -= 1
                if (direction == 0) or (direction == 1):
                    direction = 1
                    temp += 1
            elif (fetched_date > dt):
                if direction == 1:
                    direction = 2
                    temp += 1
                if (direction == 0) or (direction == -1):
                    direction = -1
                    temp -= 1
        return temp

                
if __name__ ==" __main__":
    logging.basicConfig(filename='autoDownloader.log', level=logging.DEBUG)
    a= Downloader()
    dt= date(2020, 9, 17)
    t = a.download(dt)
    print("Successfully downloaded")