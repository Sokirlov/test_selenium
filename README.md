# Multitask Selenium Parser

This microservice is designed for data parsing using Selenium. It is containerized and requires Docker for operation.

## Starting the Project

Before starting the project, you need to download the required Docker images. Run the following command:

```shell
docker pull selenium/standalone-chrome & docker pull mongo & docker pull redis & wait
```

Once the images are downloaded, you can start the project using:

```shell
docker compose up --build
```

## Using the Project

This is a REST API service built with FastAPI, and it includes Swagger documentation for ease of use.

- Swagger documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Sending a Request

To start a task, send a `POST` request to the base URL:  
`http://127.0.0.1:8000`

The response will include a `task_id`.

### Checking Task Status and Results

To check the status and get the results of your task, send a `GET` request to:  
`http://127.0.0.1:8000/{task_id}`  

Replace `{task_id}` with the actual ID provided in the initial response.