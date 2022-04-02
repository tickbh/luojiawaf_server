git pull
date > uw/monitor
#docker exec -it django_center_erp-docker uwsgi --reload uwsgi.ini
echo "reload end"
tail -f logs/uwsgi.log