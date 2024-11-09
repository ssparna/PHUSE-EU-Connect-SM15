"""
This is the main file for the annotation export project. It allows the user to export annotations
from a pdf to an excel file. For further information on how to use this please consult the 
README.md
"""
import FreeSimpleGUI as sg
from .annot_export import AnnotationExporter


def ending_present(string: str, ending: str) -> bool:
    """
    checks the presence of the correct ending

    :param string: the string to check
    :type string: str
    :param ending: the ending to check for
    :type ending: str
    :return: True if the ending is present, False otherwise
    :rtype: bool
    """
    split_str = string.split(".")
    return split_str[-1] == ending

def run() -> None:
    """
    runs the gui from the presentation
    """
    annotation_exporter: AnnotationExporter = AnnotationExporter()
    sg.theme("DarkGrey5")
    layout: list[list[sg.Element]] = [
        [sg.Text("Annotation Exporter V 0.2")],
        [sg.Push(), sg.Text("PDF Path"), sg.InputText(key="pdf",default_text=r"PDF/example_compressed"), sg.FileBrowse(file_types=(("PDF", "*.pdf"),))],
        [sg.Push(), sg.Text("Spreadsheet Path"), sg.InputText(key="xlsx", default_text=r"Templates/temp"), sg.FileBrowse(file_types=(("Excel", "*.xlsx"),))],
        [sg.Push(), sg.Text("Output Folder"), sg.InputText(key="output", default_text=r"outputs"), sg.FolderBrowse()],
        [sg.Checkbox("Convert Old Standard", key="conv_old"), sg.Checkbox("Create SQLite database", key="sqlite"), sg.Push(), sg.Button("Export Annotations", key="export")]
        ]

    window: sg.Window = sg.Window(title="Annotation Export", layout=layout, margins=(150, 125))



    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        try:
            pdf_p = values["pdf"]
            xlsx_p = values["xlsx"]
            output_p = values["output"]
            convert_old = values["conv_old"]
            sqlite = values["sqlite"]
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
        else:
            continue

        annotation_exporter.export_annotations(
            xlsx_path,
            pdf_path,
            output_folder)

        if convert_old:
            annotation_exporter.pdf.convert_old_standard(output_folder)

        if sqlite:
            annotation_exporter.generate_sqlite(output_folder)


    window.close()

def conv_paths(path: str) -> None:
    """
    replaces all backslashes to prevent accidental escape sequences

    :param path: the path to replace
    :type path: str
    """
    backslash = r"\ "
    backslash = backslash.split(" ", maxsplit=1)[0] # remove the space after the backslash
    path.replace(backslash, "/")

if __name__ == "__main__":
    run()
