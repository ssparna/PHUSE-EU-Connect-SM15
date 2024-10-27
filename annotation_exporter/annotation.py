"""
Contains the Annotation class which is used for storing annotations in a more convenient format
"""
import logging as lg
import os
from page import Page
from PyPDF2.generic import DictionaryObject, RectangleObject

lg.basicConfig(
    filename=f"{os.path.dirname(__file__)}/Annotation_Exporter.log",
    encoding="utf-8",
    level=lg.DEBUG,
    filemode="w")

separators: tuple[str] = (",", ";", "|") # expand as needed

class Annotation:
    """
    This is the class that stores a single annotation with convenient access
    """
    def __init__(self, annot_obj: DictionaryObject, page: Page) -> None:
        self.annot_obj = annot_obj
        self.page: Page = page
        self.dataset: bool = False
        self.supp: bool = False
        self.separators: tuple[str] = separators 

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

    @staticmethod
    def get_multiple_variables(annot_obj: DictionaryObject) -> list[dict | DictionaryObject]:
        """
        returns all variables from an annotation
        """
        split_set = set()
        try:
            content = annot_obj["/Contents"]
        except KeyError:
            lg.info("Unsupported Annotation: %s", annot_obj)
            return []

        content = "".join(content.split())
        split_annot = content.split("=", 1)

        for separator in separators:
            for string in split_annot[0].split(separator):
                if any(ext in string for ext in separators): # if any separator is in the string don't add it
                    continue
                elif "("  in string:
                    string = string.split("(", 1)[0]
                elif ")" in string:
                    string = string.split(")", 1)[1]

                if string == "":
                    continue
                split_set.add(string)

        split_content = list(split_set)
        if len(split_content) == 1:
            return [annot_obj]
        else:
            #print(f"""\n\n\nmultiple variables: {[{"/Contents": f"{string} =", "/C": annot_obj["/C"], "/Subtype": annot_obj["/Subtype"], "/Rect": annot_obj["/Rect"]} for string in split_content]}\n\n\n""")
            return [{"/Contents": f"{string} =", "/C": annot_obj["/C"], "/Subtype": annot_obj["/Subtype"], "/Rect": annot_obj["/Rect"]} for string in split_content]

    def is_dataset(self) -> bool:
        """
        returns wehther the annotation is a dataset or not
        """
        if len(self.content_without_spaces.split("(", 1)[0]) == 2: # new standard
            self.page.add_datasets(self.content_without_spaces.split("(", 1)[0], self.color)
            return True
        elif len(self.content_without_spaces.split("=", 1)[0]) == 2: # old standard
            self.page.add_datasets(self.content_without_spaces.split("=", 1)[0], self.color)
            return True
        return False

    def is_supp(self) -> bool:
        """
        returns wehther the annotation is a supplementary variable or not
        """
        if self.content_without_spaces.split("=", 1)[0][:4] == "SUPP":
            return True
        return False

    def __str__(self) -> str:
        return f"Annotation: {self.content} on page {self.page.get_page_nr()}"

    def __repr__(self) -> str:
        return f"Annotation: {self.content} on page {self.page.get_page_nr()}"
