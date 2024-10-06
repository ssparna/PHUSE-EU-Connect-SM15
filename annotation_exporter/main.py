"""This is the main file for the annotation export project. It allows the user to export annotations
from a pdf to an excel file. For further information on how to use this please consult the README.md"""
import FreeSimpleGUI as sg 
from annot_export import AnnotationExporter


annotation_exporter: AnnotationExporter = AnnotationExporter()
sg.theme("DarkGrey5")
layout = [
    [sg.Text("Annotation Exporter V 0.2")],
    [sg.Push(), sg.Text("PDF path"), sg.InputText(key="pdf",default_text=r"PDF/aCRF 2.0_example_new"), sg.FileBrowse(file_types=(("PDF", "*.pdf")))],
    [sg.Push(), sg.Text("spreadsheet path"), sg.InputText(key="xlsx", default_text=r"Templates/temp"), sg.FileBrowse(file_types=(("Excel", "*.xlsx")))],
    [sg.Push(), sg.Text("output folder"), sg.InputText(key="output", default_text=r"outputs"), sg.FolderBrowse()],
    [sg.Push(), sg.Button("Export Annotations", key="export")]
    ]

window = sg.Window(title="Annotation Export", layout=layout, margins=(150, 125))

def ending_present(string: str, ending: str):
    """checks the presence of the correct ending"""
    split_str = string.split(".")
    if split_str[-1] == ending:
        return True
    else:
        return False

def conv_paths(path):
    """replaces all backslashes to prevent accidental escape sequences"""
    backslash = r"\ "
    backslash = backslash.split(" ", maxsplit=1)[0] # remove the space after the backslash
    path.replace(backslash, "/")


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    try:
        pdf_p = values["pdf"]
        xlsx_p = values["xlsx"]
        output_p = values["output"]
    except KeyError:
        continue

    conv_paths(pdf_p)
    conv_paths(xlsx_p)
    conv_paths(output_p)

    if event == "export":
        if ending_present(xlsx_p, "xlsx"):
            xlsx_path = xlsx_p
        else:
            xlsx_path = f"{xlsx_p}.xlsx"
        if ending_present(pdf_p, "pdf"):
            pdf_path = pdf_p
        else:
            pdf_path = f"{pdf_p}.pdf"

        output_folder = output_p

    annotation_exporter.export_annotations(xlsx_path, pdf_path, output_folder)

window.close()
