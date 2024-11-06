======
README
======

This is an example project for the accompanying presentation and paper
at PHUSE EU Connect 2024 which can be found `here <www.github.com>`_.

The purpose of this repo is to provide access to the code showcased in
the previously mentioned presentation and paper. Feel free to use this
as a baseline or inspiration to improve your workflow when dealing with
the CDISC standard.

Installation
------------

Requirements:
~~~~~~~~~~~~~

-  Python 3.10 or later
-  openpyxl
-  PyPDF2
-  FreeSimpleGUI

How to use
~~~~~~~~~~

1. Download the project
2. Create a virtual environment

.. code-block:: batch

   path\to\project python -m venv venv  path\to\project venv\Scripts\activate

3. Install all required packages

.. code-block:: batch

   pip install -r requirements.txt

4. Run project/annotation_exporter/main.py
5. Enter paths for PDF and Template inputs
6. Enter output folder
7. Click the Export_Annots button
8. Deactivate venv

.. code-block:: batch

   path\to\project venv\Scripts\deactivate


The outputs should be in the specified folder.

Troubleshooting
---------------

1. Make sure all packages are installed correctly
2. Replace all backslashes in the paths with normal (forward) slashes
   “/”
3. Make sure you using absolute paths (for example
   C:/users/…/project/PDF/example_compressed)

You can also always open an issue and I will try to help you.

Contributing
------------

This project is not intended to be maintained actively but I will try to fix any bugs that come up.

License
-------

This project is licensed under the MIT License

Credits
-------

The project was created by Salomo Sparna.
