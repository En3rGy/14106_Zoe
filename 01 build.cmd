@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib
@echo on

cd ..\..
C:\Python27\python generator.pyc "14106_Zoe" UTF-8

xcopy .\projects\14106_Zoe\src .\projects\14106_Zoe\release

@echo Fertig.

@pause
