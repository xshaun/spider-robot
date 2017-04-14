::--------------------------------------------::
::--------------windows user------------------::

::step1: install python and pip
::::python msi file [https://www.python.org/downloads/release/python-2713/]
start /wait .\packages\windows\win32\python-3.4.3.msi /quiet

::step2: add python into path
set path=%path%;C:\Python34;C:\Python34\Scripts

::step3: install selenium and requests component 
C:\Python34\Scripts\pip3 install selenium
C:\Python34\Scripts\pip3 install requests

::step4: install chrome && webdriver
.\packages\windows\ChromeSetup.exe

copy .\packages\windows\chromedriver.exe C:\Python34

::step5: exec alimama-ie.py
:: C:\Python34\python .\alimama.py

pause