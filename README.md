# CMSC461_DMS

# To create and start database:
First open docker desktop app
Run the command in terminal:
docker-compose up --build
Then just run every time you want to run the database:
docker-compose up


# To stop and delete database
First press CTRL + C to stop
Run the command in terminal:
docker-compose down
Then run:
docker volume rm proj-app-template_mysql_data
