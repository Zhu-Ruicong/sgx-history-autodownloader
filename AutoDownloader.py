# Tick https://links.sgx.com/1.0.0/derivatives-historical/4724/WEBPXTICK_DT.zip
# Tick structure https://links.sgx.com/1.0.0/derivatives-historical/4724/TickData_structure.dat
# TC https://links.sgx.com/1.0.0/derivatives-historical/4724/TC.txt
# TC structure https://links.sgx.com/1.0.0/derivatives-historical/4724/TC_structure.dat
from datetime import datetime, date, timedelta
import numpy as np
import requests

class Downloader:
    def __init__(self):
        self.benchmark_index = 4724
        self.benchmark_date = date(2020,9,16)
        self.earliest_valid_index = 2755
        self.earliest_valid_date = date(2013,4,5)
        
        self.tick_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/WEBPXTICK_DT.zip"
        self.tick_struct_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/TickData_structure.dat"
        self.tc_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/TC.txt"
        self.tc_struct_url = "https://links.sgx.com/1.0.0/derivatives-historical/DATE_INDEX/TC_structure.dat"

    def download_file(self, url, filename):
        local_filename = filename
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                
                    f.write(chunk)
        return local_filename

    def download(self, dt):
        index = self.get_date_index(dt)
        if (index == None):
            print("Failure")
            return;
        self.download_file(self.tc_url.replace('DATE_INDEX', str(index)), "TC_" + dt.strftime("%Y%m%d"))
        self.download_file(self.tick_url.replace('DATE_INDEX', str(index)), "WEBPXTICK_DT-" + dt.strftime("%Y%m%d"))
        self.download_file(self.tick_struct_url.replace('DATE_INDEX', str(index)), "TC_structure_" + dt.strftime("%Y%m%d"))
        self.download_file(self.tc_struct_url.replace('DATE_INDEX', str(index)), "TickData_structure_" + dt.strftime("%Y%m%d"))


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
        print("initial estimate is " + str(estimated_index))
        consecutive_error_count = 0
        while (1):
            print("current temp is :" + str(temp))
            print("current direction is :" + str(direction))
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

                

a= Downloader()
dt= date(2020, 8, 28)
t = a.download(dt)
print(t)