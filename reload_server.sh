git pull
date > uw/monitor
#docker exec -it django_center_erp-docker uwsgi --reload uwsgi.ini
echo "reload end"
tailf logs/uwsgi.log