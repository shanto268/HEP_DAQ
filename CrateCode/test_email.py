from Emailer import Emailer
from Notify import Notify
import time

Notify("run8_100.bin").sendEmail()
Notify().sendPdfEmail("events_data_frame_800.pdf")
