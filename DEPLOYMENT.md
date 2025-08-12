# Deployment Guide

## Prerequisites

- Python 3.8 or higher
- Google Sheets API credentials
- Virtual environment (recommended)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/procop07/moodtracker-sheets.git
   cd moodtracker-sheets
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Sheets API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API
   - Create credentials (Service Account)
   - Download the JSON key file
   - Place it in the project root as `credentials.json`

5. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```
   SECRET_KEY=your-secret-key-here
   GOOGLE_SHEETS_ID=your-spreadsheet-id
   ```

6. **Run the application**
   ```bash
   python src/app.py
   ```

## Production Deployment

### Option 1: Heroku

1. **Install Heroku CLI**
2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GOOGLE_SHEETS_ID=your-spreadsheet-id
   ```

5. **Add Google credentials**
   ```bash
   heroku config:set GOOGLE_APPLICATION_CREDENTIALS=credentials.json
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 2: Docker

1. **Build Docker image**
   ```bash
   docker build -t moodtracker .
   ```

2. **Run container**
   ```bash
   docker run -p 5000:5000 \
     -e SECRET_KEY=your-secret-key \
     -e GOOGLE_SHEETS_ID=your-spreadsheet-id \
     moodtracker
   ```

### Option 3: VPS/Cloud Server

1. **SSH into your server**
2. **Clone repository and setup as in local development**
3. **Install a WSGI server like Gunicorn**
   ```bash
   pip install gunicorn
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 src.app:app
   ```

5. **Set up reverse proxy with Nginx** (optional but recommended)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `GOOGLE_SHEETS_ID` | ID of your Google Spreadsheet | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google credentials JSON | Yes |
| `DEBUG` | Enable debug mode (development only) | No |

## Troubleshooting

- **403 Forbidden from Google Sheets**: Check that the service account has access to your spreadsheet
- **Module not found**: Ensure virtual environment is activated and dependencies are installed
- **Port already in use**: Change the port in app.py or kill the process using the port

## Security Notes

- Never commit credentials.json to version control
- Use environment variables for sensitive configuration
- Enable HTTPS in production
- Regularly rotate your secret keys
- Restrict Google Sheets API access to specific IPs if possible
