# This is an example python script for use in
# Azure Machine Learning Studio

import pandas as pd
import matplotlib.pyplot as plt

def azureml_main(dataframe1 = None, dataframe2 = None):
    """
    Inputs: 2 Pandas dataframes
    Output: A single Pandas dataframe.
            If a .png image is generated, it will also be available for display
    """

    pd.scatter_matrix(dataframe1)
    plt.savefig('scatter_matrix.png', figsize=(12,12))

    return dataframe1,
