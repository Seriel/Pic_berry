#!/bin/bash
### BEGIN INIT INFO
# Provides:          PeB.sh
# Required-Start:    $all
# Required-Stop:     $all
# Should-Start:
# Should-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Startup per Pic_Berry
# Description:       Startup per Pic_Berry con jessie
### END INIT INFO#

After=mysql.service
Wants=mysql.service

case "$1" in
start)  sleep 60 
        echo "Lancio Pic_Berry:"
        cd /home/pi/PeB
        sudo python /home/pi/PeB/Pic_Berry.py
        ;;
stop)   echo "Non ancora implementato"
        ;;
restart) echo "Non ancora implementato"
        ;;
reload|force-reload) echo "Non ancora implementato"
        ;;
*)      echo "Usage: /etc/init.d/PeB.sh {start|stop|restart|reload|force-reload}"
        exit 2
        ;;
esac
exit 0
