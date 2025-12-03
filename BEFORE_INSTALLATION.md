# Guide to configure before installing the tool

When you start installing with the following command:

```bash
npm install -g uipro-cli
cd /path/to/your/project
uipro init --ai your_AI_assistant
```

You may face with an error similar to:

```text
✖ Installation failed error Failed to extract zip: Error: Command failed: unzip -o "C:\Users\XUANHO~1\AppData\Local\Temp\uipro-1764730187888\release.zip" -d 

"C:\Users\ADMIN\AppData\Local\Temp\uipro-1764730187888\extracted" 'unzip' is not recognized as an internal or external command, operable program or batch file.
```

This happens because Windows does not provide the unzip command, and UIPro CLI requires it.
To resolve the issue, follow the steps below.

1. Install the 7-Zip and **add to system PATH** the installation directory(normally C:\Program Files\7-Zip\). After that you must to check by entering the command "7z" in the Powershell to ensure that 7-Zip has been installed successfully.
2. **Create unzip.md file** in Windows\System32 with the following body:

```bash
@echo off
setlocal

set ZIPFILE=
set OUTDIR=

:parse
if "%1"=="" goto run
if "%1"=="-o" shift & goto parse
if "%1"=="-d" (
    set OUTDIR=%2
    shift & shift
    goto parse
)
if "%ZIPFILE%"=="" (
    set ZIPFILE=%1
) else (
    rem ignore other args
)
shift
goto parse

:run
if "%ZIPFILE%"=="" (
    echo Missing zip file
    exit /b 1
)

if "%OUTDIR%"=="" (
    echo Missing output directory
    exit /b 1
)

7z x "%ZIPFILE%" -y -o"%OUTDIR%"
```

3. Continue to the uipro-cli command
