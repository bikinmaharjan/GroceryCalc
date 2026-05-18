# GrocerySplit

GrocerySplit is a tool for managing grocery lists and splitting costs among group members.

## Quick Start

### Using Docker (Recommended)
The fastest way to run the entire stack is using Docker Compose:

```bash
docker-compose up --build
```

- **Backend:** http://localhost:8080
- **Frontend:** http://localhost:3000

### Manual Installation

#### Backend
1. Navigate to the root directory:
   ```bash
   cd /projects/grocery-calculator
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend:
   ```bash
   uvicorn app.main:app --port 8080 --reload
   ```

#### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Administration

The system bootstraps an admin user on the first startup.
- **Username:** `admin`
- **Password:** `admin123`
- **Display Name:** `Administrator`

You can customize these using environment variables:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_DISPLAY_NAME`

## Project Structure
- `/app`: FastAPI backend logic, routers, and database models.
- `/frontend`: Vue.js frontend.
- `grocery.db`: SQLite database file.
- `start.sh`: Helper script to start both backend and frontend simultaneously.
