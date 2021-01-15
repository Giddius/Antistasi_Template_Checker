@ECHO off
SETLOCAL EnableDelayedExpansion
SET _THIS_FILE_DIR=%~dp0
SET _INPATH=%~dp1
SET _INFILE=%~nx1
SET _INFILEBASE=%~n1

REM ---------------------------------------------------
SET _date=%DATE:/=-%
SET _time=%TIME::=%
SET _time=%_time: =0%
REM ---------------------------------------------------
REM ---------------------------------------------------
SET _decades=%_date:~-2%
SET _years=%_date:~-4%
SET _months=%_date:~3,2%
SET _days=%_date:~0,2%
REM ---------------------------------------------------
SET _hours=%_time:~0,2%
SET _minutes=%_time:~2,2%
SET _seconds=%_time:~4,2%
REM ---------------------------------------------------
SET _TIMEBLOCK=%_years%-%_months%-%_days%_%_hours%-%_minutes%-%_seconds%
SET _TIMEBLOCK_TIME=%_hours%-%_minutes%-%_seconds%
SET _TIMEBLOCK_DATE=%_years%-%_months%-%_days%

call pskill64 Dropbox
call pyclean -v ..\
rem --upx-dir "D:\Dropbox\hobby\Modding\Ressources\python\upx\upx-3.96-win64" ^
rem --upx-exclude "vcruntime140.dll" ^

set INPATH=%~dp1
set INFILE=%~nx1
set INFILEBASE=%~n1
cd %_THIS_FILE_DIR%\..
call .venv\Scripts\activate.bat
set _CONFIG_FILE=tools\_project_devmeta.env
for /f %%i in (%CONFIG_FILE%) do set %%i
set _OUT_DIR=%WORKSPACEDIR%\pyinstaller_output\%_TIMEBLOCK_DATE%
RD /S /Q %WORKSPACEDIR%\pyinstaller_output\%_TIMEBLOCK_DATE%
mkdir %_OUT_DIR%
cd %INPATH%






set PYTHONOPTIMIZE=1
call pyinstaller --clean ^
--noconfirm ^
--log-level=INFO ^
--onefile -c ^
-i D:\Dropbox\hobby\Modding\Ressources\Icons\To_Sort_Icons\ico_icons\Antistasi_flag_experiment.ico ^
-n antistasi_template_checker ^
--upx-dir D:\Dropbox\hobby\Modding\Ressources\python\upx\upx-3.96-win64 ^
--upx-exclude vcruntime140.dll ^
--upx-exclude ucrtbase.dll ^
--distpath %_OUT_DIR%\dist ^
--workpath %_OUT_DIR%\work ^
--specpath %_OUT_DIR%\spec ^
"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_Template_Checker\antistasi_template_checker\__main__.py"