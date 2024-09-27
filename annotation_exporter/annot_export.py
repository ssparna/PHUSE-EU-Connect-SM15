"""Contains the AnnotationExporter class which contains the logic for exporting annotations"""
import os
import logging as lg
import PyPDF2
import openpyxl as pyxl
from openpyxl.worksheet.worksheet import Worksheet
from Page import Page


class AnnotationExporter:
    """Responsible for exporting annotations from a pdf to an excel file"""
    def __init__(self) -> None:
        self.green_cell_fill = pyxl.styles.PatternFill(
            start_color = "FF00FF00",
            end_color = "FF00FF00",
            fill_type = "solid")
        self.wb: pyxl.Workbook
        self.pages: list[Page]
        self.reader: PyPDF2.PdfReader
        self.output_folder: str
        self.exporter_col_ds: str | None
        self.exporter_col_var: str | None
        self.ws_datasets: Worksheet
        self.ws_variables: Worksheet
        self.current_page: Page

    def verify_exporter_cols(self) -> None:
        """checks that exporter cols are indeed found and exits if not"""
        if self.exporter_col_ds is None:
            lg.critical("no free column for sheet Datasets found, exiting...")
            exit()
        elif self.exporter_col_var is None:
            lg.critical("no free column for sheet Variables found, exiting...")
            exit()

        lg.debug("(%s) determined as exporter_col_ds", self.exporter_col_ds)
        lg.debug("(%s) determined as exporter_col_var", self.exporter_col_var)

    def determine_exporter_col(self, sheet: str) -> str | None:
        """determines the exporter cols. Returns the exel column index of the free column or None"""
        for cell in self.wb[sheet]["1"]:
            if cell.value is None:
                cell.value = "Present in aCRF"
                return "".join([i for i in cell.coordinate if not i.isdigit()]) # remove all digits

        lg.error("no free column for sheet %s found!", sheet)

    def export_annotations(self, template_path: str, pdf_path: str, output_folder: str):
        """Exports annots, this is the main function that should be called"""
        lg.basicConfig(
            filename=f"{os.path.dirname(__file__)}/Annotation_Exporter.log",
            encoding="utf-8",
            level=lg.DEBUG,
            filemode="w")
        print("exporting annotations...")
        lg.debug("export annots")
        self.wb = pyxl.load_workbook(template_path)
        self.pages = []
        self.output_folder = output_folder

        self.exporter_col_ds = self.determine_exporter_col("Datasets")
        self.exporter_col_var = self.determine_exporter_col("Variables")

        self.verify_exporter_cols()

        self.ws_datasets = self.wb["Datasets"]
        self.ws_variables = self.wb["Variables"]

        reader = PyPDF2.PdfReader(pdf_path)

        for page in reader.pages:
            self.current_page = Page(reader.get_page_number(page))
            self.pages.append(self.current_page)
            lg.info("starting on page: %s", self.current_page.get_page_nr())

            if "/Annots" in page:
                annot_data: list[dict] = []
                for annot in page["/Annots"]:
                    dataset = False
                    annot_obj = annot.get_object()
                    lg.debug(annot_obj)

                    if annot_obj["/Subtype"] != "/FreeText" or "/Contents" not in annot_obj or "/C" not in annot_obj:
                        lg.info("unsupported annotation: %s", annot_obj)
                        continue

                    content = annot_obj["/Contents"]
                    content = "".join(content.split()) # remove spaces
                    split_annot = content.split("=", 1)
                    if len(split_annot[0]) == 2:
                        dataset = True
                        self.current_page.add_datasets([split_annot[0],annot_obj["/C"]])

                    annot_data.append(
                        {"dataset_name": split_annot[0], 
                         "dataset": dataset, 
                         "annot_obj": annot_obj})

                self.add_to_workbook(annot_data)

                lg.debug(self.current_page.get_datasets())
                lg.info("Page %s done!", self.current_page.get_page_nr())
            else:
                lg.info("Page %s has no Annotations, continuing with next page...", self.current_page.get_page_nr())

        self.wb.save(f"{output_folder}/output.xlsx")
        print("generating csv...")
        lg.debug("generating csv of export")
        self.generate_variable_csv()
        self.generate_dataset_csv()
        print("complete!")
        lg.debug("exported annots")

    def enter_dataset(self, dataset_name: str, annot_obj: dict) -> None:
        """adds a dataset to the workbook"""
        for cell in self.ws_datasets["A"]:
            if cell.value == dataset_name:
                y_coordinate = cell.coordinate.split("A", 1)[1]
                self.ws_datasets[f"{self.exporter_col_ds}{y_coordinate}"] = "Present"
                self.ws_datasets[f"{self.exporter_col_ds}{y_coordinate}"].fill = self.green_cell_fill
                lg.debug("%s was assigned as a dataset with the color %s", dataset_name, annot_obj["/C"])
                break

            if cell.value is None: # dataset not in template
                cell.value = dataset_name
                cell.fill = self.green_cell_fill
                y_coordinate = cell.coordinate.split("A", 1)[1]
                dataset_long_name: str = annot_obj["/Contents"].split("=")[1].strip()
                self.ws_datasets[f"B{y_coordinate}"] = dataset_long_name
                self.ws_datasets[f"{self.exporter_col_ds}{y_coordinate}"] = "Present"
                self.ws_datasets[f"{self.exporter_col_ds}{y_coordinate}"].fill = self.green_cell_fill
                break

    def match_dataset_to_variable(self, annot_obj: dict) -> str:
        """matches a dataset to a variable based on color"""
        for combination in self.current_page.get_datasets():
            if combination[1] == annot_obj["/C"]: # match color
                lg.debug(
                        """Variable %s was assiged %s because %s is the same as %s""", 
                        annot_obj["/Contents"], combination, annot_obj["/C"], combination[1])
                return combination[0]

        lg.error("no dataset was matched to variable! %s", annot_obj)

    def add_to_workbook(self, data: list[dict]):
        """adds both datasets and variables to the workbook"""
        for annot in data:
            if annot["dataset"]:
                self.enter_dataset(annot["dataset_name"], annot["annot_obj"])
            else:
                variable_dataset = self.match_dataset_to_variable(annot["annot_obj"])
                variable_name = annot["annot_obj"]["/Contents"].split("=")[0].strip()

                for cell in self.ws_variables["B"]:
                    y_coordinate = cell.coordinate.split("B", 1)[1]

                    if cell.value == variable_dataset and self.ws_variables["C" + y_coordinate].value == variable_name:
                        if self.ws_variables[f"{self.exporter_col_var}{y_coordinate}"].value == "Present":
                            print("yay", y_coordinate)
                            self.add_page_cell(self.ws_variables[f"M{y_coordinate}"])
                            break

                        self.ws_variables[f"{self.exporter_col_var}{y_coordinate}"].value = "Present"
                        self.ws_variables[f"{self.exporter_col_var}{y_coordinate}"].fill = self.green_cell_fill
                        self.ws_variables[f"L{y_coordinate}"].value = "CRF"
                        self.add_page_cell(self.ws_variables[f"M{y_coordinate}"])
                        break

                    if cell.value is None:
                        cell.value = variable_dataset
                        self.ws_variables[f"C{y_coordinate}"].value = annot["dataset_name"]
                        self.ws_variables[f"{self.exporter_col_var}{y_coordinate}"].value = "Present"
                        self.add_page_cell(self.ws_variables[f"M{y_coordinate}"])
                        self.ws_variables[f"{self.exporter_col_var}{y_coordinate}"].fill = self.green_cell_fill
                        self.ws_variables[f"L{y_coordinate}"].value = "CRF"
                        self.ws_variables[f"F{y_coordinate}"].value = "200"
                        break


    def generate_variable_csv(self) -> None:
        """generates the csv for the variables"""
        csv_list = ["Variable Name#Variable Label#Dataset Name#Page(s)\n"] # start with first line
        for cell in self.ws_variables[self.exporter_col_var]:
            if cell.value == "Present":
                cell_str: str = ""
                cell_str += str(self.ws_variables["C" + str(cell.row)].value) + "#"
                cell_str += str(self.ws_variables["D" + str(cell.row)].value) + "#"
                cell_str += str(self.ws_variables["B" + str(cell.row)].value) + "#"
                cell_str += str(self.ws_variables["M" + str(cell.row)].value) + "\n"
                csv_list.append(cell_str)


        csv_str = "".join(csv_list)
        with open(f"{self.output_folder}/Variables.csv", "w", encoding="utf-8") as f:
            f.write(csv_str)

    def generate_dataset_csv(self):
        """generates the csv for the datasets"""
        csv_list: list[str] = ["Dataset Name#Color\n"] # start with first line
        for page in self.pages:
            for dataset in page.get_datasets():
                csv_entry: str = f"{dataset[0]}#{dataset[1]}\n"
                if csv_entry in csv_list:
                    continue
                csv_list.append(csv_entry)

        csv_str = "".join(csv_list)

        with open(f"{self.output_folder}/Datasets.csv", "w", encoding="utf-8") as f:
            f.write(csv_str)

    def add_page_cell(self, cell):
        """adds the current page number to the cell"""
        if not cell.value:
            new_value = f"{self.current_page.get_page_nr() + 1}"
        elif str(self.current_page.get_page_nr() + 1) in cell.value:
            return
        else:
            new_value = f"{cell.value} {self.current_page.get_page_nr() + 1}"
        cell.value = new_value
