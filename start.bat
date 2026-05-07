@echo off
echo Starting Job Scrapping Application...
echo.
echo Starting Backend on http://localhost:8000 ...
start "Backend" cmd /k "cd backend && ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Application started!
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window (services will keep running)...
pause >nul
