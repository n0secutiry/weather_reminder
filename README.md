# WeatherReminder

WeatherReminder is a web application and API service that allows users to check the weather, subscribe to specific locations, and receive automated weather updates via email. 

The project includes a responsive web interface for regular users and a JWT-secured REST API for developers, complete with comprehensive API documentation.

## Features
* **Weather Forecasts:** Users can search and view current weather data for specific cities.
* **Email Subscriptions:** Authenticated users can subscribe to locations and opt-in to receive weather updates directly to their email.
* **REST API:** Developers can authenticate to receive a JWT token and make programmatic network requests to fetch weather data.
* **API Documentation:** Built-in documentation detailing endpoints, request parameters, and response formats.
* **Containerized Environment:** Fully dockerized for easy setup and deployment.

## Tech Stack
* **Backend:** Django REST Framework (DRF)
* **Database:** PostgreSQL
* **Frontend:** HTML, CSS, Bootstrap
* **Authentication:** JSON Web Tokens (JWT)
* **Infrastructure:** Docker, Docker Compose

## Prerequisites
* Docker and Docker Compose installed on your machine.

## Installation & Setup

1. Clone the repository:

    git clone https://github.com/your-username/weather-reminder.git
    cd weather-reminder

2. Create a .env file in the root directory and configure your environment variables:

    SECRET_KEY=your_secret_key
    DEBUG=True
    
    POSTGRES_DB=weather_db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=yourpassword
    DB_HOST=db
    DB_PORT=5432
    
    EMAIL_HOST=smtp.example.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your_email@example.com
    EMAIL_HOST_PASSWORD=your_email_password

3. Build and run the Docker containers:

    docker-compose up --build

4. Apply database migrations:

    docker-compose exec web python manage.py migrate

5. Create a superuser to access the admin panel:

    docker-compose exec web python manage.py createsuperuser

The web application should now be accessible at http://127.0.0.1:8000/.



