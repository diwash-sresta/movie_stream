# Movie Stream Project

## Overview
Movie Stream is a Django-based movie streaming platform that allows users to browse movies, view details, and maintain a watchlist. The platform supports Google login authentication and features a user profile section.

## Features
- **User Authentication**: Google login integration
- **Movie Listings**: Browse available movies
- **Movie Detail Pages**: View in-depth information about each movie
- **Watchlist**: Add and manage favorite movies
- **Profile Section**: User-specific settings and information
- **Theming**: Styled home page and movie detail pages
- **Docker Support**: Deploy the project using Docker and Docker Compose

## Installation
### Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- Docker & Docker Compose (optional for containerized deployment)
- Virtual environment (recommended)

### Setup Instructions
1. **Clone the repository**
   ```sh
   git clone https://github.com/your-repo/movie_stream.git
   cd movie_stream
   ```

2. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```sh
   python manage.py migrate
   ```

5. **Run the development server**
   ```sh
   python manage.py runserver
   ```

6. **Access the application**
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Docker Setup
To run the project using Docker:
```sh
docker-compose up --build
```
This will build and start the containers for the application.

## Static Files
Ensure static files are collected for production:
```sh
python manage.py collectstatic
```

## Environment Variables
- `.env` file (if required) should be set up for storing sensitive information like Google API credentials.

## Contributing
1. Fork the repository
2. Create a new branch (`feature-branch`)
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License.

## Contact
For any inquiries, reach out at [your-email@example.com](mailto:your-email@example.com).

