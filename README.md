# hydrogen

[![travis-ci](https://travis-ci.org/restran/hydrogen.svg?branch=master)](https://travis-ci.org/restran/hydrogen)
[![Coverage Status](https://coveralls.io/repos/github/restran/hydrogen/badge.svg?branch=master)](https://coveralls.io/github/restran/hydrogen?branch=master)


这个工具使用了 Web 技术来实现，界面使用 Vue + Element 写的，使用 [pywebview](https://github.com/r0x0r/pywebview) 实现窗口程序。

---------

![demo.gif](D:/Dropbox/Python/Workspace/hydrogen/doc/demo.gif "")

---------

## Build Windows Binary

    pyinstaller --onefile main.py

打包成一个文件，不显示控制台，设置图标

    pyinstaller --onefile --windowed --icon=app.ico app.py


## 常见问题

使用 pyinstaller 打包时出现 jinja2 问题，导致运行后的程序无法创建 flask web server

```
Syntax error in  c:\python35\lib\site-packages\jinja2\asyncsupport.py
("'yield' inside async function", ('c:\\python35\\lib\\site-packages\\jinja2\\asyncsupport.py', 35, 12, '            yield event\n'))
```

https://stackoverflow.com/questions/43163201/pyinstaller-syntax-error-yield-inside-async-function-python-3-5-1

jinja2 2.9.6 版本会有此问题，可以使用 jinja2==2.8.1 或者使用 pyinstaller 3.3 以上版本


## 相关项目

- [CTFCrackTools](https://github.com/0Chencc/CTFCrackTools)
