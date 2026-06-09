# scheduler.py

import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler

from agent import run_agent

scheduler = BlockingScheduler()

scheduler.add_job(
    lambda: asyncio.run(run_agent()),
    "interval",
    minutes=30
)

print("Scheduler started...")

scheduler.start()