#!/home/ray/project/venv/bin/python3.5

import sys, os, datetime as dt

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from app import db, models, mail, app

from admin_alert import send_admin_email
from min_spend_update import send_min_spend_email




send_min_spend_email()
