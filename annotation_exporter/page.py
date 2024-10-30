"""
This module contains the class Page.
"""
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
