"""
This module contains the class Page.
"""
class Page:
    """
    Keeps track of the datasets on each page and the page number.
    """
    def __init__(self, page_nr: int):
        """
        Initialise class.
        
        :param page_nr: Page number.
        :type page: int
        
        """
        self.page_nr: int = page_nr
        self.datasets: list[dict] = []

    def get_page_nr(self):
        """
        Simple getter for page number.
        
        :return: The page number.
        :rtype: int
        
        """
        return self.page_nr

    def get_datasets(self):
        """
        Simple getter for datasets.

        :return: The datasets.
        :rtype: list[list]
        
        """
        return self.datasets

    def add_datasets(self, data: dict):
        """
        Adds the datasets to the list.

        :param data: The dataset to add.
        :type data: dict
        """
        self.datasets.append(data)
