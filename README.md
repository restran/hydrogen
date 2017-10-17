# hydrogen

在做 CTF 的过程中，有一些编码转换等功能经常要使用，但是网上的各种工具都没有较满意的，而且也能很好自定义一些功能，因此就有了这样一个项目，类似的项目还有[CTFCrackTools](https://github.com/0Chencc/CTFCrackTools)。

这个工具使用了 Web 技术来实现，界面使用 Vue + Element 写的，后端使用 Flask，在 Python 3.5 环境下，使用 [pywebview](https://github.com/r0x0r/pywebview) 实现窗口程序。

![demo.gif](doc/demo.gif "")


## Build Windows Binary

Windows 环境下可以使用 pyinstaller 打包成一个文件

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
