# PyNewHope

PyNewHope is a Python implementation of the NewHope quantum secure cryptographic scheme proposed by Alkim, Ducas, Pöppelmann, and Schwabe: https://eprint.iacr.org/2015/1092

This Python implementation is based on, and duplicates much of the functionality of, the reference C implementation available in the `liboqs` repository: https://github.com/open-quantum-safe/liboqs/tree/master/src/kex_rlwe_newhope

This implementation is designed to be used natively in Python applications, without the need for wrappers or other means of incorporating the C implementation into production software. A testing harness is available in `test_newhope.py`, and documentation is provided as code comments. The code should be readable and usable.

This work was submitted as a master's capstone advanced lab to the computer science department at the Courant Institute of Mathematical Sciences at New York University. It should be considered open source, free to use and modify.

Python 3.6 must be installed for this implementation to work, as it relies on `hashlib.shake_128()`, which is only available in version 3.6 and later.

Python 3.6 downloads: https://www.python.org/downloads/release/python-360/

Installing Python 3.6 on Windows: https://docs.python.org/3/using/windows.html

Whether you're using Python on Linux, Mac, or Windows, it's important that Python is added to the PATH during installation.

Installing Git : https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

Instructions for cloning and testing PyNewHope on Mac/Linux:
------------------------------------------------------------

Once you have Python 3.6 and Git installed, open a terminal and enter the following commands:
```
git clone https://github.com/scottwn/PyNewHope

cd PyNewHope

python3.6 test_newhope.py
```

Instructions for cloning and testing PyNewHope on Windows:
----------------------------------------------------------

First make sure you have Python 3.6 installed.

Download PyNewHope as a zip file from https://github.com/scottwn/PyNewHope using the "Clone or download" button.

Unzip PyNewHope into a directory in your Python PATH.

Open a Python shell and enter the following commands:
```
import test_newhope

test_newhope
```

