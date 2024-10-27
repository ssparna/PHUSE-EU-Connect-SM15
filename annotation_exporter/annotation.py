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
        self.new_datset: bool = False
        self.supp: bool = False
        self.separators: tuple[str] = separators
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
        
        for separator in separators:
            if separator not in self.content:
                continue

            self.content = self.content.split(separator, 1)[0]
        

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
        
        for separator in separators:
            for string in content.split(separator):
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
            #annot_obj[NameObject("/Contents")] = NameObject(string) # truncating variable to exclude exess text
            return [annot_obj]
        else:
            #print(f"""\n\n\nmultiple variables: {[{"/Contents": f"{string} =", "/C": annot_obj["/C"], "/Subtype": annot_obj["/Subtype"], "/Rect": annot_obj["/Rect"]} for string in split_content]}\n\n\n""")
            return [{"/Contents": string, "/C": annot_obj["/C"], "/Subtype": annot_obj["/Subtype"], "/Rect": annot_obj["/Rect"]} for string in split_content]

    def is_dataset(self) -> bool:
        """
        returns wehther the annotation is a dataset or not
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
