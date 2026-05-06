# CMSC461_DMS

# To create and start database:
First open docker desktop app
Run the command in terminal:
docker-compose up --build
Then just run:
docker-compose up
If you don't decide to delete the database

# To stop and delete database
First press CTRL + C to stop
Run the command in terminal:
docker-compose down
Then run:
docker volume rm proj-app-template_mysql_data
