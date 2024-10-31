# Annotation-Exporter
This is an example project for the accompanying presentation and paper at PHUSE EU Connect 2024 which can be found [Here]().

The purpose of this repo is to provide access to the code showcased in the previously mentioned presentation and paper. Feel free to use this as a baseline or inspiration to improve your workflow when dealing with the Cdisk standard.

## Installation

### Requirements:
- Python 3.10 or later
- openpyxl
- PyPDF2
- FreeSimpleGUI

### How to use 
All Paths need to be absolute Paths.
1. Download the Project
2. Create a Virtual environment
    ```{batch}
    path\to\project python -m venv venv
    path\to\project venv\Scripts\activate
    ```
3. Install all required packages 
    ```{python}
    pip install -r requirements.txt
    ```
4. Run project/annotation_exporter/main.py
5. Enter paths for PDF and Template inputs
6. Enter output folder
7. Click the Export_Annots button
8. Deactivate venv
    ```{batch}
    path\to\project venv\Scripts\deactivate
    ```

The outputs should be in the specified folder.

## Troubleshooting

1. Make sure all packages are installed correctly
2. Replace all backslashes in the Paths with normal (forward) slashes "/"
3. Make sure you using absolute Paths (for example C:/users/.../project/PDF/example_compressed)

You can also always open an issue and I will try to help you.

## Contributing
This Project is not intended to be maintained or updated.

## License
This project is licensed under the MIT License

## Credits
The project was created by Salomo Sparna.