@echo off
chcp 65001
cls

:setEnv
setlocal EnableDelayedExpansion

:start
echo Generate GUID Template to Copyboard
echo.
call :runScript
pause
goto :EOF

:runScript
for /f "delims=" %%i in ('python %~dp0\gen_guid.py') do (
    set a=%%i
    echo GUID=!a!
    set "guid=!a!"
    echo.
)
set "jsonTab=    "
set "rn=&echo."

echo [!rn!%jsonTab%{!rn!%jsonTab%%jsonTab%"guid": "!guid!",!rn!%jsonTab%%jsonTab%//[POPULARS, GAMES, PROGRAMMING, SYSTEM, GENERIC, OTHERS]!rn!%jsonTab%%jsonTab%"category": "GAMES",!rn!%jsonTab%%jsonTab%"name": "TemplateName",!rn!%jsonTab%%jsonTab%"description": "None",!rn!%jsonTab%%jsonTab%"icon": "game.ico",!rn!%jsonTab%%jsonTab%"rules": [!rn!%jsonTab%%jsonTab%%jsonTab%"game.exe"!rn!%jsonTab%%jsonTab%]!rn!%jsonTab%}!rn!]|clip
goto :EOF

:EOF