@echo off
REM Load environment variables from .env file
setlocal enabledelayedexpansion

if not exist .env (
    echo Warning: .env file not found
    echo Please create a .env file with your environment variables
    echo Example:
    echo PROJECT_ID=your-gcp-project-id
    echo BACKEND_URL=https://your-backend-service-url.run.app
    exit /b 1
)

echo Loading environment variables from .env file...

REM Read .env file and set environment variables
for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
    REM Skip empty lines and comments
    if not "%%a"=="" (
        if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
            echo Set %%a=%%b
        )
    )
)

REM Export variables to calling environment
endlocal & (
    for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
            )
        )
    )
)

echo Environment variables loaded successfully! 