@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib

echo ^<head^> > .\release\log14106.html
echo ^<link rel="stylesheet" href="style.css"^> >> .\release\log14106.html
echo ^<title^>Logik - Zoe (14106)^</title^> >> .\release\log14106.html
echo ^<style^> >> .\release\log14106.html
echo body { background: none; } >> .\release\log14106.html
echo ^</style^> >> .\release\log14106.html
echo ^<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"^> >> .\release\log14106.html
echo ^</head^> >> .\release\log14106.html

@echo on

type .\README.md | C:\Python27\python -m markdown -x tables >> .\release\log14106.html

cd ..\..
C:\Python27\python generator.pyc "14106_Zoe" UTF-8

xcopy .\projects\14106_Zoe\src .\projects\14106_Zoe\release /exclude:.\projects\14106_Zoe\src\exclude.txt

@echo Fertig.

@pause
