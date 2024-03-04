#!/bin/bash

sudo service main stop

/home/david/d2by/venv/bin/python /home/david/d2by/database/crons/delete_rows.py

/home/david/d2by/venv/bin/python /home/david/d2by/sport/crons/d2by_matches.py
/home/david/d2by/venv/bin/python /home/david/d2by/sport/crons/fan_sport.py

/home/david/d2by/venv/bin/python /home/david/d2by/esport/crons/d2by_matches.py
/home/david/d2by/venv/bin/python /home/david/d2by/esport/crons/fan_sport.py

sudo service main start
