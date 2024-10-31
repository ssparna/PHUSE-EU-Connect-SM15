"""
contains multiple classes for various tasks:
-Page class for keeping track of page information and annotations
-PDF class for reading and modifying pdf files
-Annotation class for acessing annotations easily
"""
from __future__ import annotations # Nessecary for typehinting
import os
import logging as lg
import PyPDF2
from PyPDF2.generic import AnnotationBuilder, NameObject, DictionaryObject, RectangleObject
from PyPDF2._page import PageObject


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
    def __init__(self, page: PageObject, page_nr: int) -> None:
        """
        Initialise class. page_nr is passed because of the way PyPDF2 works
        where the page number is not in the page object.
        
        :param page: The page object.
        :type page: PageObject
        :param page_nr: Page number.
        :type page: int
        """
        self.page: PageObject = page
        self.page_nr: int = page_nr
        self.datasets: list[tuple] = []
        self.has_annotations: bool = False
        self.annotations: list[Annotation] = self.generate_annotation_list()

    def generate_annotation_list(self) -> list[Annotation]:
        """
        Generates the list of annotations, resolves 
        IndirectObject references and creates Annotation objects.
        
        :return: list of annotations
        :rtype: list[Annotation]
        """
        if "/Annots" not in self.page:
            return []

        self.has_annotations = True
        annotation_dictionary_objects: list[DictionaryObject] = [annot.get_object() for annot in self.page["/Annots"]]

        return [
            Annotation(annot_dict, self)
            for dict_obj in annotation_dictionary_objects
            for annot_dict in Annotation.get_multiple_variables(dict_obj)
            ]

    def add_annotation(self, annotation: Annotation) -> None:
        """
        Adds an annotation to the page.

        :param annotation: The annotation to add.
        :type annotation: Annotation
        """
        self.annotations.append(annotation)

    def get_annotations(self) -> list[Annotation]:
        """
        getter for page annotations

        :return: list of annotations
        :rtype: list[Annotation]
        """
        return self.annotations

    def get_page_nr(self) -> int:
        """
        Simple getter for the page number.
        
        :return: The page number.
        :rtype: int
        """
        return self.page_nr

    def get_datasets(self) -> list[tuple]:
        """
        Simple getter for all datasets.

        :return: The datasets. each dataset is a tuple with dataset name and color
        :rtype: list[tuple]
        """
        return self.datasets

    def add_datasets(self, data: tuple) -> None:
        """
        Adds the datasets to the list.

        :param data: The dataset to add.
        :type data: tuple
        """
        self.datasets.append(data)

class PDF:
    """
    Modifies the pdf file and generates a data structure to work on
    """
    def __init__(self, pdf_reader: PyPDF2.PdfReader) -> None:
        self.pdf_reader: PyPDF2.PdfReader =  pdf_reader
        self.pages: list[Page] = self.init_pages()

    def init_pages(self) -> list[Page]:
        """
        Initialises the pages that will initialize the Annotations

        :return: list of pages
        :rtype: list[Page]
        """
        page_list: list[Page] = []
        for page in self.pdf_reader.pages:
            page_list.append(Page(page, self.pdf_reader.get_page_number(page)))

        return page_list

    def convert_old_standard(self, output_folder: str) -> None:
        """
        Converts the old standard to the new standard,
        for reference check the gitHub repo.

        :param output_folder: path to the output folder
        :type output_folder: str
        """
        writer = PyPDF2.PdfWriter()
        new_pdf_path: str = f"{output_folder}/output.pdf"

        writer.append_pages_from_reader(self.pdf_reader)

        for page in self.pages:

            for annot in page.get_annotations():
                if not annot.dataset or annot.new_datset:
                    continue

                dataset_long_name: str = annot.content.split("=", 1)[1].lstrip()
                print(dataset_long_name, annot.content)
                new_annot = AnnotationBuilder.free_text(
                    f"{annot.dataset_name} ({dataset_long_name})",
                    rect=annot.rect,
                )
                new_annot[NameObject("/C")] = annot.color
                writer.add_annotation(page.get_page_nr(), new_annot)

        with open(new_pdf_path, "wb") as fp:
            writer.write(fp)

class Annotation:
    """
    This is the class that stores a single annotation with convenient 
    access to frequently used proprties and some useful methods
    """
    def __init__(self, annot_obj: DictionaryObject, page: Page) -> None:
        self.is_valid: bool = True
        self.annot_obj = annot_obj
        self.page: Page = page
        self.dataset: bool = False
        self.new_datset: bool = False
        self.supp: bool = False
        self.separators: tuple[str] = SEPARATORS
        self.dataset_name: str = None
        self.assigned_dataset: str = None
        self.variable_name: str = None

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
            self.is_valid = False
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
    def get_multiple_variables(annot_obj: DictionaryObject) -> list[dict]:
        """
        returns all variables from an annotation. this is used to pick up on multiple variables
        being in the same annotation.  This has the side effect of converting the DictionaryObjects 
        to dictionaries which looses some (hopefully irrelevant) data.

        :param annot_obj: the annotation object
        :type annot_obj: DictionaryObject
        :return: list of annotations as a list of dictionaries
        :rtype: list[dict]
        """
        split_set = set()
        try: # try except as this is an unsafe annotation
            content: str = annot_obj["/Contents"]
            color: list[float] = annot_obj["/C"]
            subtype: str = annot_obj["/Subtype"]
            rect: list[float] = annot_obj["/Rect"]
        except KeyError:
            lg.info("Unsupported Annotation: %s", annot_obj)
            return []

        for separator in SEPARATORS:
            for possible_variable in content.split(separator):
                if any(ext in possible_variable for ext in SEPARATORS): # if any separator is in the string don't add it
                    continue
                elif "("  in possible_variable: #brackets are special cases
                    possible_variable = possible_variable.split("(", 1)[0]
                elif ")" in possible_variable:
                    possible_variable = possible_variable.split(")", 1)[1]

                if possible_variable == "":
                    continue
                split_set.add(possible_variable)

        split_content = list(split_set)
        return [{"/Contents": string,
                    "/C": color,
                    "/Subtype": subtype,
                    "/Rect": rect}
                    for string in split_content]

    def is_dataset(self) -> bool:
        """
        Returns wehther the annotation is a dataset or not
        and implicitly adds the dataset to the page. There is
        a static method that checks if a string is a dataset 
        aswell so if you need to call this on just a string you
        can use Annotation.is_dataset_static(string).

        :return: if the annotation is a dataset
        :rtype: bool
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
        returns wether the annotation is a supplementary variable or not

        :return: if the annotation is a supplementary variable
        :rtype: bool
        """
        if self.content_without_spaces.split("=", 1)[0][:4] == "SUPP":
            self.dataset_name = self.content_without_spaces.split("=", 1)[0][:6]
            return True
        return False

    def sort_into_datasets(self) -> None:
        """
        Sorts self into one of the datasets from the page it is on
        """
        for combination in self.page.get_datasets():
            if combination[1] == self.color: # match color
                lg.debug(
                        """Variable %s was assiged %s because %s is the same as %s""", 
                        self.content, combination, self.color, combination[1])
                self.assigned_dataset = combination[0]
                return

        lg.error("no dataset was matched to variable! %s", self)

    @staticmethod
    def is_dataset_static(string: str) -> bool:
        """
        static method that checks if a string is a dataset
        :param string: the string to check

        :type string: str
        :return: True if the string is a dataset, False otherwise
        :rtype: bool
        """
        if len(string.split("(", 1)[0]) == 2: # new standard
            return True
        elif len(string.split("=", 1)[0]) == 2: # old standard
            return True
        return False

    def __str__(self) -> str:
        return f"Annotation: {self.content} on page {self.page.get_page_nr()}"

    def __repr__(self) -> str:
        return f"Annotation: {self.content} on page {self.page.get_page_nr()}"
