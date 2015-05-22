rem Build Arelle GUI using cx_Freeze

@set PYTHONDIR=c:\python34
@set NSISDIR=C:\Program Files (x86)\NSIS
@set BUILTDIR=build\exe.win-amd64-3.4
@set TCL_LIBRARY=c:\python34\Lib\tcl8.6
@set TK_LIBRARY=c:\python34\Lib\tcl8.6\tk8.6

rem rmdir build /s/q
rmdir dist /s/q
mkdir dist
"%PYTHONDIR%\python" setup.py build_exe

"%NSISDIR%\makensis" installWin64.nsi

rem compact /c /f dist\arelle-win-x64.exe