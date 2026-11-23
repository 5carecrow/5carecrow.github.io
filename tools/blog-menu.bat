@echo off
setlocal
set "BLOG=E:\devprojects\5carecrow.github.io"
set "HUGO=%BLOG%\tools\hugo\hugo.exe"
set "SASS=%BLOG%\tools\dart-sass\dart-sass"
set "PATH=%SASS%;%PATH%"
cd /d "%BLOG%"

:MENU
cls
echo ============================================
echo  5carecrow blog toolbox
echo ============================================
echo  1  New post
echo  2  Preview (hugo server -D)
echo  3  Build check
echo  4  Commit and push
echo  5  Pull latest
echo  6  Open live site
echo  7  Open repo folder
echo  8  Edit hugo.toml
echo  9  Open GitHub Actions
echo  0  Exit
echo.
set "op="
set /p "op=Select [0-9]: "
if "%op%"=="1" goto NEW
if "%op%"=="2" goto PREVIEW
if "%op%"=="3" goto BUILD
if "%op%"=="4" goto COMMIT
if "%op%"=="5" goto PULL
if "%op%"=="6" goto SITE
if "%op%"=="7" goto FOLDER
if "%op%"=="8" goto CONFIG
if "%op%"=="9" goto ACTIONS
if "%op%"=="0" goto END
echo Invalid choice.
pause
goto END

:NEW
set "slug="
set /p "slug=Post file name (e.g. 2026-11-24-my-post): "
if not defined slug goto END
"%HUGO%" new "posts\%slug%.md"
if errorlevel 1 goto FAIL
start "" notepad "content\posts\%slug%.md"
echo Post created: content\posts\%slug%.md
echo Remember to set draft = false when ready to publish.
pause
goto END

:PREVIEW
start "Hugo preview" cmd /k "%HUGO% server -D"
echo Preview started in a new window: http://localhost:1313
pause
goto END

:BUILD
"%HUGO%" --minify --gc
if errorlevel 1 goto FAIL
echo Build OK.
pause
goto END

:COMMIT
set "msg="
set /p "msg=Commit message: "
if not defined msg goto END
git add -A
git commit -m "%msg%"
if errorlevel 1 goto FAIL
set "HTTPS_PROXY="
set "HTTP_PROXY="
set "https_proxy="
set "http_proxy="
git push
if errorlevel 1 goto FAIL
echo Pushed. GitHub Actions will publish in about 1 minute.
pause
goto END

:PULL
git pull --recurse-submodules
if errorlevel 1 goto FAIL
echo Pulled latest changes.
pause
goto END

:SITE
start "" https://5carecrow.github.io/
goto END

:FOLDER
explorer "%BLOG%"
goto END

:CONFIG
start "" notepad "%BLOG%\hugo.toml"
goto END

:ACTIONS
start "" https://github.com/5carecrow/5carecrow.github.io/actions
goto END

:FAIL
echo.
echo Command failed. Check the output above.
pause

:END
endlocal
