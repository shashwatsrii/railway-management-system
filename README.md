# Train Booking System API
#### This is a RESTful API for a Train Booking System that allows users to register, login, manage train information, and make bookings. The API provides endpoints for user authentication, train management, and booking functionality.

## Table of Contents
### Authentication
- POST /auth/register
- POST /auth/login
- Trains
- POST /trains/
- GET /trains/search
- PUT /trains/{train_id}
- Bookings
- GET /bookings/
- POST /bookings/

### Authentication
#### POST /auth/register
#### Register a new user.

- Request Body:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

#### POST /auth/login
#### Login for an existing user.

- Request Body:
```json
{
  "username": "string",
  "password": "string"
}
```

### Trains
#### POST /trains/
#### Create a new train.

- Request Body:
```json
{
  "train_number": "string",
  "train_name": "string",
  "source": "string",
  "destination": "string",
  "total_seats": 0
}
```

#### GET /trains/search
#### Search for trains between a specified source and destination.

#### Query Parameters:
- source (required): The source station.
- destination (required): The destination station.

#### PUT /trains/{train_id}
#### Update the details of a specific train (Admin only).

#### Path Parameters:
- train_id (required): The ID of the train.

### Bookings
#### GET /bookings/
#### Get all bookings for the current user. 
- Responses: 200 OK
```json
[
  {
    "id": 0,
    "train_id": 0,
    "user_id": 0,
    "seat_number": "string",
    "created_at": "2024-12-07T09:13:45.295Z"
  }
]
```
#### POST /bookings/
#### Book a seat for the logged-in user.

- Request Body:
```json
{
  "train_id": 0
}
```


## Setup
- Clone this repository.
- Install dependencies using:
```bash
pip install -r requirements.txt
```
- Run the application:
```bash
uvicorn main:app --reload
```