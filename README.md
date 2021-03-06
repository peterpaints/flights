#### Flights

[![CircleCI](https://circleci.com/gh/peterpaints/flights.svg?style=svg)](https://circleci.com/gh/peterpaints/flights)
[![Coverage Status](https://coveralls.io/repos/github/peterpaints/flights/badge.svg)](https://coveralls.io/github/peterpaints/flights)

Ticket booking and flights reservation micro api.

#### Development

To begin, simply clone this repo, and run:
```
docker-compose up
```
That's it!

If you want to seed yourself as an admin user, to hit some of the endpoints
restricted for admins, then run:
```
docker-compose run flights python api/models/seed.py --email bla@bla.com --password Password1 --admin True
```

#### Info
This is a test micro-app, written in Flask, and wrapped in Docker. Flask is light-weight, and affords one more control over how to design database models, configure security for the API endpoints and serialize responses back to clients.

Everything, from the redis server to the backend database runs on docker. To access the postgres instance running within docker, run `docker ps -a`, and select the container id of the postgres server.

Then, run `docker exec -it <container_id> bash`

Once you've opened the shell session, run `psql -U postgres flights`

This connects you to the `flights` database. From here you can run `SQL` queries such as
`SELECT * FROM flights;` to inspect various tables.


#### The Endpoints

You can play around with the API by:
* Pasting [this url](http://35.234.209.220:8000/api/) in your browser, and working with the beautifully autogenerated Swagger UI
* Using [`Postman`](https://www.getpostman.com/)
* Using [`Curl`](https://curl.haxx.se/)

Here are SOME of the endpoints:

| URL Endpoint | HTTP Methods | Action |
| -------- | ------------- | --------- |
| `api/healthz` | `GET`  | Check if the API is ready to receive requests|
| `api/users/register/` | `POST`  | Register a new user|
| `api/users/login/` | `POST` | Log user in and receive access token|
| `/api/users/photo/upload` | `POST` | Upload a photo |
| `/api/users/photo/download` | `GET` | Download your most recent photo |
| `api/tickets/book` | `POST` | Book a flight ticket |
| `api/tickets/cancel` | `GET` | Cancel a ticket|
| `api/flights` | `GET` |  Retrieve all flights|
| `/api/flights/origin/{origin_id}` | `GET` | Get a flight by origin |

... among MANY others.
Visit [this url](http://35.234.209.220:8000/api/) for more.
