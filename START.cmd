@echo off
setlocal
cd /d "%~dp0"
echo Face Swap iOS gateway
echo Engine must already be healthy at http://127.0.0.1:8855/api/health
echo Gateway does not start GPU work and does not touch the 3060.
python -c "import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:8855/api/health', timeout=5); sys.exit(0 if r.status==200 else 1)" 2>nul
if errorlevel 1 (
  echo RED: MultoModa is not reachable on 127.0.0.1:8855
  echo Start it first: G:\AI-Home\projects\multomoda-face-studio\START-RUNTIME.vbs
  exit /b 1
)
echo MultoModa health: OK
python "%~dp0gateway.py"
endlocal
