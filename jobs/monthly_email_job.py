#!/home/ray/project/venv/bin/python3.5

import sys, os, datetime as dt

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from admin_alert import send_admin_email
from annual_fee_alert import send_annual_fee_email


send_annual_fee_email()
