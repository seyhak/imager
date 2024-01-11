# To Run the project

1) Run `docker-compose up`

### If project it's running first time:
1) Go to django container and run `python manage.py migrate`
2) Run `python manage.py createsuperuser`


## Project flow

1) go to `localhost:8000/admin`
2) login
3) try to upload any SatelitteImage
4) you should get email notification (in media folder)
5) you can also go to `localhost:8000/api/satellite_images/` to see every uploaded satellite images info
