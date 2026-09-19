@echo off
chcp 65001 > NUL
echo ローカルサーバーを起動しています...
echo ブラウザで http://localhost:8000 を開きます。
echo (終了するにはこのウィンドウで Ctrl + C を押してください)
echo.

:: ブラウザで自動的にページを開く
start http://localhost:8000

:: Pythonのローカルサーバーをポート8000で起動
python -m http.server 8000

pause