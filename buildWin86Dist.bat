rem Build Arelle GUI using cx_Freeze

@set PYTHONDIR=c:\python34x86
@set NSISDIR=C:\Program Files (x86)\NSIS
@set BUILTDIR=build\exe.win32-3.4
@set TCL_LIBRARY=c:\Python34x86\Lib\tcl8.6
@set TK_LIBRARY=c:\Python34x86\Lib\tcl8.6\tk8.6

rem rmdir build /s/q
rmdir dist /s/q
mkdir dist
"%PYTHONDIR%\python" setup.py build_exe

"%NSISDIR%\makensis" installWin86.nsi

rem compact /c /f dist\exe.win32-3.2.exe