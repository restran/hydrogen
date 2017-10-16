# hydrogen

[![travis-ci](https://travis-ci.org/restran/magnetos.svg?branch=master)](https://travis-ci.org/restran/magnetos)
[![Coverage Status](https://coveralls.io/repos/github/restran/magnetos/badge.svg?branch=master)](https://coveralls.io/github/restran/magnetos?branch=master)

## 安装依赖

- [pywebview](https://github.com/r0x0r/pywebview)

## Build Windows Binary

    C:/Python35/Scripts/pyinstaller --onefile main.py

打包成一个文件，不显示控制台，设置图标

    pyinstaller.exe --onefile --windowed --icon=app.ico app.py

## Upload to PyPi

安装最新的 setuptools

    pip3 install -U pip setuptools twine

生成 wheel 包

    python3 setup.py register bdist_wheel --universal upload

生成 tar.gz 包，因为 setup.py 用到了 pypandoc，安装的时候会需要依赖

    python3 setup.py register sdist upload

## 通过 setup install 安装后删除

    python3 setup.py install --record files.txt
    cat files.txt | xargs rm -rf

## 常见问题

使用 pyinstaller 打包时出现 jinja2 问题，导致运行后的程序无法创建 flask web server

```
Syntax error in  c:\python35\lib\site-packages\jinja2\asyncsupport.py
("'yield' inside async function", ('c:\\python35\\lib\\site-packages\\jinja2\\asyncsupport.py', 35, 12, '            yield event\n'))
```

https://stackoverflow.com/questions/43163201/pyinstaller-syntax-error-yield-inside-async-function-python-3-5-1

jinja2 2.9.6 版本会有此问题，可以使用 jinja2==2.8.1 或者使用 pyinstaller 3.3 以上版本