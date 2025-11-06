# Page Titles and Headers
PAGE_TITLE = "Tutorial"
HEADER_STEP_1 = "1.- Single step process."
HEADER_STEP_2 = "2.- Prepare files."
HEADER_STEP_3 = "3.- Load files."

# CSS for Styling
STYLE_BOLD_TEXT = """
    <style>
    strong {
        color: #FF5733; /* Change bold text color */
        font-weight: 1000; /* Adjust boldness */
    }
    </style>
"""

# Step Descriptions
STEP_1_DESCRIPTION = """
To illustrate the use of pICNIK lets work with an example. To follow this tutorial, data files can
be downloaded from:

[Picnik Examples Repository](https://github.com/ErickErock/pICNIK/tree/main/examples/Constant_E)

The data used in this example is a simulated process that follows an $F1$ reaction model: $f(α) = 1 −α$, 
with the Arrhenius parameters: $E = 75 kJ/mol$ and $ln (A/min) = 12$

The data represents four thermogravitric experiments of linear temperature programs with
heating rates of $(2.5,5,10 and 20) K/min$.

To download the example files, click on the link above, then click on the file you want to download,
and finally click on the "Download" button.

Next image shows how to download the example files:
"""

STEP_2_DESCRIPTION = """
pICNIK works with files with extension **.csv** or **.dat**. The files must be made of three columns:
**“time”** in **minutes [min]**, **“temperature”** in **Kelvin [K]**. The third column was originally thought
as the **mass** in **milligrams [mg]**, but it can be any other temperature-controlled physical property
of the sample or even the conversion values computed by other means. Once you’ve prepared all
your data files, upload them with the file uploader located below:
"""

STEP_3_DESCRIPTION = """
The DataExtraction object in picnik library is equipped with functions to read and manipulate 
data from thermally 
controlled experiments. An exahustive list of all available functions, along with a description,
can be found in the documentation [here](https://erickerock.github.io/pICNIK/modules/DataExtraction.html).


To load files you have to create an instance of the DataExtraction object. Then, simply use
the read_files function.
```
import picnik as pnk
xtr = pnk.DataExtraction
B, T0 = xtr.read_files(data)
```
The next button use read_files function taking the list of paths to the data files
you selected in step 2 and
returns a numpy[ref] array of computed heating rates (B), another array containing the initial
experimental temperature in K (T0) and a graphical summary of the expirmental data (Fig. 1.1).
"""