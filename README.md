# FastAPI Authentication and Data Retrieval API

## Endpoints

### User Authentication
- **Register**: `/register` (POST)
- **Login**: `/login` (POST)
- **Get Profile**: `/profile` (GET, Auth Required)
- **Update Profile**: `/profile` (PUT, Auth Required)
- **Upload Photo**: `/upload-photo` (POST, Auth Required)

### Data APIs
- **Get Coin Details**: `/coins` (GET)
- **Get Specific Coin**: `/coin/{symbol}` (GET)
- **Get Weather Data**: `/weather` (GET)

## Usage
- Start FastAPI: `uvicorn main:app --reload`
- Use the provided cURL commands to test endpoints.
"""
