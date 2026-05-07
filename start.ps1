# Start the Job Scrapping Application
# Run this from the project root: .\start.ps1

Write-Host "Starting Job Scrapping Application..." -ForegroundColor Green

# Start Backend
Write-Host "Starting Backend on http://localhost:8000 ..." -ForegroundColor Cyan
$backend = Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WorkingDirectory "backend" -PassThru -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
$frontend = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend" -PassThru -WindowStyle Normal

Write-Host "`nApplication started!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop both services" -ForegroundColor Magenta

# Keep script running
while ($true) {
    Start-Sleep -Seconds 1
}
