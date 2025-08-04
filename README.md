# 💪 Sculptor - Roman Gladiator Workout Tracker

> *"Discipline is the soul of an army. Train like a gladiator, fight like a champion."*

A comprehensive workout tracking application with Roman gladiator theming, featuring exercise completion tracking, drag-and-drop exercise reordering, and detailed workout history.

## 🏛️ Features

- **⚔️ Training Regimens**: Create custom workout splits (3-day, 4-day, 5-day, 6-day)
- **💪 Exercise Tracking**: Complete exercises with set-based weight tracking
- **🏆 Conquest System**: Track exercise completions and auto-archive completed exercises
- **📜 Gladiator's Codex**: Browse exercise archive with drag-and-drop reordering
- **📊 Battle History**: View detailed workout history and statistics
- **🎯 Rep Range System**: Choose from 6-10, 8-12, or 10-14 rep ranges per exercise
- **📱 Mobile Responsive**: Train anywhere in the empire

## 🛠️ Tech Stack

- **Frontend**: React + Advanced CSS (Roman Gladiator Theme)
- **Backend**: FastAPI + Python
- **Database**: MongoDB
- **Additional**: Drag & Drop (react-beautiful-dnd), Axios

## 🚀 Quick Start

### Prerequisites

- Node.js (v14+) - [Download](https://nodejs.org/)
- Python (v3.8+) - [Download](https://python.org/)
- Yarn - Will be auto-installed if missing

**No database installation needed! Uses JSON file storage.**

### Windows Setup (Recommended)

#### Option 1: Batch Script (Easy)
```cmd
# Double-click start.bat or run in Command Prompt
start.bat
```

#### Option 2: PowerShell Script (Advanced)
```powershell
# Right-click > "Run with PowerShell" or run in PowerShell
powershell -ExecutionPolicy Bypass -File start.ps1
```

#### Option 3: Manual Windows Setup
```cmd
# Create MongoDB data directory
mkdir data\db

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
yarn install
cd ..

# Install development tools
npm install

# Start all services
npm run dev
```

### Linux/Mac Setup

#### Option 1: Automated Setup (Recommended)
```bash
# Make the start script executable
chmod +x start.sh

# Run the setup and start script
./start.sh
```

#### Option 2: Manual Setup
```bash
# Install all dependencies
npm run setup:unix

# Start all services
npm run dev
```

### Stopping the Application

**Windows:**
```cmd
# Double-click stop.bat or run:
stop.bat
# Or PowerShell:
stop.ps1
# Or press Ctrl+C if running npm run dev
```

**Linux/Mac:**
```bash
# Run the stop script
./stop.sh
# Or press Ctrl+C if running npm run dev
```

## 📁 Project Structure

```
sculptor-workout-tracker/
├── backend/
│   ├── server.py           # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Roman gladiator styles
│   │   └── index.js       # Entry point
│   ├── package.json       # Frontend dependencies
│   └── public/            # Static assets
├── data/
│   └── db/                # MongoDB data directory
├── package.json           # Root package.json with scripts
├── start.sh              # Automated setup script
├── stop.sh               # Stop all services script
└── README.md             # This file
```

## 🗄️ Database Schema

### Exercise Collection
```javascript
{
  "id": "uuid",
  "name": "Bench Press",
  "muscle_group": "Chest",
  "equipment": "Barbell"
}
```

### Workout Split Collection
```javascript
{
  "id": "uuid",
  "name": "Push/Pull/Legs",
  "days_per_week": 3,
  "days": [
    {
      "day_number": 1,
      "day_name": "Push Day",
      "muscle_groups": ["Chest", "Shoulders", "Arms"]
    }
  ]
}
```

### Workout Session Collection
```javascript
{
  "id": "uuid",
  "split_id": "split-uuid",
  "day_number": 1,
  "exercises": [
    {
      "exercise_id": "exercise-uuid",
      "exercise_name": "Bench Press",
      "sets": [
        {"set_number": 1, "weight": 135, "reps": 10},
        {"set_number": 2, "weight": 135, "reps": 10}
      ],
      "completed_count": 3,
      "is_archived": true
    }
  ],
  "completed_at": "2024-01-15T10:30:00Z"
}
```

## 🎨 Color Scheme (Roman Gladiator)

- **Backgrounds**: Dark stone (#0d0a08, #1a1612)
- **Primary**: Roman gold (#d4af37)
- **Text**: Antique white (#f5f1eb)
- **Accents**: Battle bronze and arena shadows

## 📱 Mobile Support

The application is fully responsive with:
- Touch-optimized interfaces
- Mobile-specific layouts
- Swipe gestures for navigation
- Optimized for gladiator training on-the-go

## 🔧 Development Scripts

**Cross-Platform:**
```bash
npm run dev              # Start all services
npm run start            # Alias for dev
npm run install:all      # Install all dependencies
npm run backend:dev      # Start only backend
npm run frontend:dev     # Start only frontend
npm run db:start         # Start only MongoDB
npm run build           # Build for production
npm run test:backend    # Run backend tests
npm run test:frontend   # Run frontend tests
```

**Windows-Specific:**
```cmd
npm run setup            # Windows setup
npm run win:start        # Run start.bat
npm run win:stop         # Run stop.bat
npm run win:setup        # Run PowerShell setup
```

**Linux/Mac-Specific:**
```bash
npm run setup:unix       # Unix setup
chmod +x start.sh && ./start.sh    # Automated start
```

## 🛑 Stopping the Application

**Windows:**
- Double-click `stop.bat`
- Or run `stop.ps1` in PowerShell
- Or use `Ctrl+C` if running `npm run dev`

**Linux/Mac:**
```bash
# Stop all services
./stop.sh
# Or use Ctrl+C if running npm run dev
```

## 🏛️ Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=sculptor_workout_db
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🎯 API Endpoints

- `GET /api/exercises` - Get all exercises
- `GET /api/muscle-groups` - Get muscle groups
- `POST /api/splits` - Create workout split
- `GET /api/splits` - Get all splits
- `POST /api/sessions` - Save workout session
- `GET /api/sessions` - Get workout history
- `PATCH /api/sessions/{id}/exercises/{exercise_id}/complete` - Complete exercise

## 🏆 Features in Detail

### Exercise Completion System
- Each exercise requires 3 completions to be archived
- Automatic progression tracking
- Visual completion indicators

### Weight Selection
- Dropdown with predefined weights (1lb to 400lbs)
- Includes fractional weights (2.5lb, 7.5lb, etc.)
- Easy selection for quick workout entry

### Drag & Drop Exercise Reordering
- Intuitive drag handles
- Visual feedback during drag
- Persistent order storage

### Workout History
- Complete session tracking
- Exercise-specific history
- Last workout statistics display

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📜 License

MIT License - Train like a gladiator, code like a champion!

---

*Ave Caesar! Those who are about to lift, salute you!* ⚔️🏛️💪