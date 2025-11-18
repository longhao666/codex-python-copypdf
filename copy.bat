echo off
set startPath=.
set pyPath=.
set imagePath=.\empty


for /f "tokens=2 delims==" %%I in ('wmic OS Get localdatetime /value') do set datetime=%%I
set year=%datetime:~0,4%
set month=%datetime:~4,2%
set day=%datetime:~6,2%
echo %year%-%month%-%day%

set mydate=%year%-%month%-%day%

python  %pyPath%\merge_pdfs.py --input-dir %imagePath% --output %mydate%.pdf --overwrite

pause