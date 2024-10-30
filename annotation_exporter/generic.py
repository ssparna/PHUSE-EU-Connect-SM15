"""
contains multiple classes for various tasks
"""
import os
import logging as lg
import PyPDF2
from PyPDF2.generic import AnnotationBuilder, NameObject, DictionaryObject, RectangleObject


SEPARATORS: tuple[str] = (",", ";", "|") # expand as needed

lg.basicConfig(
    filename=f"{os.path.dirname(__file__)}/Annotation_Exporter.log",
    encoding="utf-8",
    level=lg.DEBUG,
    filemode="w")


class Page:
    """
    Keeps track of the datasets on each page and the page number.
    """
    def __init__(self, page_nr: int) -> None:
        """
        Initialise class.
        
        :param page_nr: Page number.
        :type page: int
        
        """
        self.page_nr: int = page_nr
        self.datasets: set[tuple] = {}
        self.annotations: list[Annotation] = []

    def get_annotations(self) -> list[Annotation]:
        """
        getter for page annotations

        :return: list of annotations
        :rtype: list[Annotation]
        """
        return self.annotations

    def get_page_nr(self) -> int:
        """
        Simple getter for page number.
        
        :return: The page number.
        :rtype: int
        
        """
        return self.page_nr

    def get_datasets(self) -> set[tuple]:
        """
        Simple getter for datasets.

        :return: The datasets. each dataset is a tuple with dataset name and color
        :rtype: set[tuple]
        
        """
        return self.datasets

    def add_datasets(self, data: tuple):
        """
        Adds the datasets to the list.

        :param data: The dataset to add.
        :type data: tuple
        """
        self.datasets.update([data]) # using add(data) doesn't work for some reason

class PDFAugmentor:
    """
    holds static methods for changing the PDF file.
    """
    def __init__(self, pdf_path: str, pages: list[Page]) -> None:
        self.pages: list[Page] = pages
        self.pdf: PyPDF2.PdfReader =  PyPDF2.PdfReader(pdf_path)

    def convert_old_standard(self, pdf_path: str, output_folder: str) -> None:
        """
        converts the old standard to the new standard

        :param pdf_path: path to the pdf file
        :type pdf_path: str
        :param output_folder: path to the output folder
        :type output_folder: str
        """
        writer = PyPDF2.PdfWriter()
        reader = PyPDF2.PdfReader(pdf_path)
        new_pdf_path: str = f"{output_folder}/output.pdf"

        writer.append_pages_from_reader(reader)

        for page in self.pages:
            annots: list[Annotation] = self.get_page_annotations(page)

            for annot in annots:
                if not annot.dataset or annot.new_datset:
                    continue

                dataset_long_name: str = annot.content.split("=", 1)[1].lstrip()
                new_annot = AnnotationBuilder.free_text(
                    f"{annot.dataset_name} ({dataset_long_name})",
                    rect=annot.rect,
                )
                new_annot[NameObject("/C")] = annot.color
                writer.add_annotation(reader.get_page_number(page), new_annot)

        with open(new_pdf_path, "wb") as fp:
            writer.write(fp)

    def get_page_annotations(self, page: Page) -> list:
        """
        returns all annotations on the page
        """
        if page.get:
            return []
        annotation_dictionary_objects: list[DictionaryObject] = [annot.get_object() for annot in page["/Annots"]]
        return [
            Annotation(annot_dict, page)
            for dict_obj in annotation_dictionary_objects
            for annot_dict in Annotation.get_multiple_variables(dict_obj)
            ]

class Annotation:
    """
    This is the class that stores a single annotation with convenient 
    access to frequently used proprties and some useful methods
    """
    def __init__(self, annot_obj: DictionaryObject, page: Page) -> None:
        self.annot_obj = annot_obj
        self.page: Page = page
        self.dataset: bool = False
        self.new_datset: bool = False
        self.supp: bool = False
        self.separators: tuple[str] = SEPARATORS
        self.dataset_name: str
        self.assigned_dataset: str = None
        self.variable_name: str

        try:
            self.color: list[float] = annot_obj["/C"]
            self.content: str = annot_obj["/Contents"]
            self.content_without_spaces: str = "".join(self.content.split())
            self.rect: RectangleObject = annot_obj["/Rect"]
            self.subtype: str = annot_obj["/Subtype"]
            if self.subtype != "/FreeText":
                raise KeyError # not a KeyError but requires the same action
        except KeyError:
            lg.info("Unsupported Annotation: %s", annot_obj)
            return

        self.dataset = self.is_dataset()
        self.supp = self.is_supp()

        self.truncate_exess_text()

    def truncate_exess_text(self) -> None:
        """
        truncates the annotation if it contains invalid text
        """
        if self.dataset or self.supp:
            return

        for separator in SEPARATORS:
            if separator not in self.content:
                continue

            self.content = self.content.split(separator, 1)[0]

    @staticmethod
    def get_multiple_variables(annot_obj: DictionaryObject) -> list[dict | DictionaryObject]:
        """
        returns all variables from an annotation

        :param annot_obj: the annotation object
        :type annot_obj: PyPDF2.generic.DictionaryObject
        :return: list of annotations as either a dictionary or a dictionary object
        :rtype: list[PyPDF2.generic.DictionaryObject | PyPDF2.generic.DictionaryObject]
        """
        split_set = set()
        try:
            content = annot_obj["/Contents"]
        except KeyError:
            lg.info("Unsupported Annotation: %s", annot_obj)
            return []
        content = "".join(content.split())

        for separator in SEPARATORS:
            for possible_variable in content.split(separator):
                if any(ext in possible_variable for ext in SEPARATORS): # if any separator is in the string don't add it
                    continue
                elif "("  in possible_variable:
                    possible_variable = possible_variable.split("(", 1)[0]
                elif ")" in possible_variable:
                    possible_variable = possible_variable.split(")", 1)[1]

                if possible_variable == "":
                    continue
                split_set.add(possible_variable)

        split_content = list(split_set)
        if len(split_content) == 1:
            return [annot_obj]
        else:
            return [{"/Contents": string,
                        "/C": annot_obj["/C"],
                        "/Subtype": annot_obj["/Subtype"],
                        "/Rect": annot_obj["/Rect"]}
                        for string in split_content]

    def is_dataset(self) -> bool:
        """
        returns wehther the annotation is a dataset or not
        and implicitly adds the dataset to the page
        """
        if len(self.content_without_spaces.split("(", 1)[0]) == 2: # new standard
            self.new_datset = True
            self.dataset_name = self.content_without_spaces.split("(", 1)[0]
            self.page.add_datasets((self.dataset_name, self.color))
            return True
        elif len(self.content_without_spaces.split("=", 1)[0]) == 2: # old standard
            self.dataset_name = self.content_without_spaces.split("=", 1)[0]
            self.page.add_datasets((self.dataset_name, self.color))
            return True
        self.variable_name = self.content_without_spaces.split("=", 1)[0]
        return False

    def is_supp(self) -> bool:
        """
        returns wehther the annotation is a supplementary variable or not
        """
        if self.content_without_spaces.split("=", 1)[0][:4] == "SUPP":
            self.dataset_name = self.content_without_spaces.split("=", 1)[0][:6]
            return True
        return False

    def sort_into_datasets(self) -> None:
        """
        sorts an annotation into a dataset
        """
        for combination in self.page.get_datasets():
            if combination[1] == self.color: # match color
                lg.debug(
                        """Variable %s was assiged %s because %s is the same as %s""", 
                        self.content, combination, self.color, combination[1])
                self.assigned_dataset = combination[0]
                return

        lg.error("no dataset was matched to variable! %s", self)

    def __str__(self) -> str:
        return f"Annotation: {self.content} on page {self.page.get_page_nr()}"

    def __repr__(self) -> str:
        return f"Annotation: {self.content} on page {self.page.get_page_nr()}"
