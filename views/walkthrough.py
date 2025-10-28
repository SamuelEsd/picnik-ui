import streamlit as st
import base64

# --- TODO: Create walkthrou for picnik use ---
st.set_page_config(
        layout="wide",
        initial_sidebar_state="expanded",
    )

# Set page title
st.title("Tutorial")

st.header("1.- Single step process.")

st.markdown("""
    <style>
    strong {
        color: #FF5733; /* Change bold text color */
        font-weight: 1000; /* Adjust boldness */
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
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
""")

file_ = open("./resources/download_example_files.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    unsafe_allow_html=True,
)

st.header("2.- Prepare files.")

st.markdown("""
pICNIK works with files with extension **.csv** or **.dat**. The files must be made of three columns:
**“time”** in **minutes [min]**, **“temperature”** in **Kelvin [K]**. The third column was originally thought
as the **mass** in **milligrams [mg]**, but it can be any other temperature-controlled physical property
of the sample or even the conversion values computed by other means. Once you’ve prepared all
your data files, create a list containing the paths to the files:

```
one_step = ['HOME/pICNIK/examples/Constant_E/E_cnt_2.5.csv',
            'HOME/pICNIK/examples/Constant_E/E_cnt_5.csv',
            'HOME/pICNIK/examples/Constant_E/E_cnt_10.csv',
            'HOME/pICNIK/examples/Constant_E/E_cnt_20.csv']
```

""")

st.header("3.- Load files")

st.markdown("""
The DataExtraction object is equipped with functions to read and manipulate data from thermally 
controlled experiments. An exahustive list of all available functions, along with a description,
can be found in the documentation [here](https://erickerock.github.io/pICNIK/modules/DataExtraction.html).


To load files you have to create an instance of the DataExtraction object. Then, simply use
the read_files function.
import picnik as pnk
xtr = pnk.DataExtraction
B, T0 = xtr.read_files(data)
The read_files function takes as obligatory parameter the list of paths to the data files and
returns a numpy[ref] array of computed heating rates (B), another array containing the initial
experimental temperature in K (T0) and a graphical summary of the expirmental data (Fig. 1.1).
""")