=====
Usage
=====

To use Annotation Exporter in a project you can use the following workflow.

-----
Setup
-----

For now the only thing you need is to install and import the package.

You can install the package locally from the folder structure which you obtain after downloading and unzipping the source file from the github repo or after pulling and checking out the current branch.

The path\\to\\project is the path which contains the folder *annotation_exporter*.

.. code-block:: batch

   path\to\project pip install -e .

The package will be installed from the local file system, and you can edit it directly at the source until it fulfills your requirements.

It is also available on PyPi. You can install it with

.. code-block:: batch

   path\to\project python -m venv venv  path\to\project venv\Scripts\activate
   path\to\project pip install annotation-exporter


You can use it in the following way in the virtual environment.

You import this package in your Python program

.. code-block:: batch

   from annotation_exporter import AnnotationExporter

You'll need the following files:

-  an Excel sheet as a template which contains the SDTM meta data
-  a PDF which contains the CRF with the annotations
-  a folder for the outputs

You can use the Excel file SDTM_Specification_Template.xlsx for the first steps until you have customised your own version.
As for the PDF you can use any PDF that is annotated to the CDISC SDTM standard.

--------------------
Your first operation
--------------------

Firstly create an AnnotationExporter object and define the paths for
template, PDF and output folder. You can use relative paths if you want.


.. code-block:: python

   template_path = "Templates/SDTM_Specification_Template"
   pdf_path = "PDF/example_compressed"
   output_folder = "outputs"
   annot_exporter = AnnotationExporter()

This doesn't do anything by itself, to use the main functionality you need
to call:


.. code-block:: python

   annot_exporter.export_annotations(template_path, pdf_path, output_folder)

After running the file you should see an Excel file and two txt files in
the output folder.

-------------------------
Understanding the package
-------------------------

Calling *export_annotations()*  creates a *PDF* object which
itself creates a *Page* object for every page in the PDF file. That
*Page* object then creates an *Annotation* object for each
annotation on that page. With that the creation of the data structure is
complete and operations on it can begin.

The *AnnotationExporter* class uses this data structure to sort the
annotations into the template. After that is complete, other operations
like converting an old SDTM standard to a new one or outputting the
annotation data in a different format can be done.
