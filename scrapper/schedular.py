import schedule
import time
import __main__

def job():
    print("Job started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    __main__.retrieve_data()
    print("Job completed at:", time.strftime("%Y-%m-%d %H:%M:%S"))

# Run the job every week on a specific day and time (adjust as needed)
schedule.every().week.at("12:00").do(job)

# Add more scheduled jobs if needed
# schedule.every().hour.do(another_job)

while True:
    schedule.run_pending()
    time.sleep(1)
