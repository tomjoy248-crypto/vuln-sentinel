@echo off
chcp 65001 >nul
echo ==========================================
echo  Vuln Sentinel - 一键提交到 GitHub
echo ==========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查是否是 git 仓库
if not exist ".git\config" (
    echo [错误] 当前目录不是 Git 仓库！
    echo 请把这个文件放到你的 GitHub 项目文件夹里再运行。
    echo 项目文件夹通常在：C:\Users\lenovo\Documents\GitHub\vuln-sentinel
    pause
    exit /b 1
)

REM 配置 git 用户信息（如果没有）
git config user.email "dev@vuln-sentinel.local" >nul 2>&1
git config user.name "VulnSentinel Dev" >nul 2>&1

REM 添加所有文件
echo [1/4] 正在添加文件...
git add -A

REM 检查是否有变更
set GIT_STATUS=0
git diff --cached --quiet || set GIT_STATUS=1

if %GIT_STATUS%==0 (
    echo [提示] 没有需要提交的变更，可能已经是最新版了。
    pause
    exit /b 0
)

REM 提交
echo [2/4] 正在提交...
git commit -m "Update Vuln Sentinel 11-S clean final version"
if errorlevel 1 (
    echo [错误] 提交失败！
    pause
    exit /b 1
)

REM 推送到 GitHub
echo [3/4] 正在推送到 GitHub...
git push origin main
if errorlevel 1 (
    echo.
    echo [错误] Push 失败！可能原因：
    echo 1. 网络问题，请检查网络连接
    echo 2. GitHub 未登录，请打开 GitHub Desktop 确认已登录
    echo 3. 权限问题，请确认你有该仓库的写入权限
    echo.
    echo 解决方法：
    echo - 打开 GitHub Desktop，确保显示 "Fetch origin" 或 "Push origin" 按钮
    echo - 如果显示 "Publish repository"，请先点击发布仓库
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  [4/4] 提交成功！
echo ==========================================
echo.
echo 下一步：
echo 1. 打开 https://dashboard.render.com/
echo 2. 找到 vuln-sentinel-v11-s 服务
echo 3. 点击 Manual Deploy → Deploy latest commit
echo 4. 等待 3-5 分钟，状态变 Live
echo.
pause

