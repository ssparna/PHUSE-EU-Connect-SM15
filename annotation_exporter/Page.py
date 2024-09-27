class Page:
    """keeps track of the datasets on each page and the page number"""
    def __init__(self, page_nr: int):
        self.page_nr: int = page_nr
        self.datasets: list[dict] = []

    def get_page_nr(self):
        """simple getter for page number"""
        return self.page_nr
    
    def get_datasets(self):
        """simple getter for datasets"""
        return self.datasets

    def add_datasets(self, data: dict):
        """adds the datasets to the list"""
        self.datasets.append(data)
