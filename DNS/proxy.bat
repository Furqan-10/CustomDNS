@echo off
echo [*] Starting Custom DNS Proxy Server...
cd C:\dnsproxy
start dnsproxy.exe --listen=0.0.0.0 --port=53 --upstream=0.0.0.0:5354 --verbose
echo [*] DNS Proxy Server started.
pause

