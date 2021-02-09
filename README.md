# Py_SSM_iCrop2
A Python Translation of SSM_iCrop2 (Experimental).

Original Model available here: http://ssm-crop-models.net/ssm-icrop2/  
All rights reserved of original model by the original authors.  

Original Model citation:  
Soltani, A., Alimagham, S.M., Nehbandani, A., Torabi, B., Zeinali, E., Zand, E., Ghassemi, S., …. Vadez, V., van Ittersum, M.K., Sinclair, T.R., 2020. SSM-iCrop2: A simple model   for diverse crop species over large areas. Agric. Syst. 182: 102855.

This code is intended to be used with the Anaconda Distribution of Python available here: https://www.anaconda.com/products/individual  
Scroll to the bottom of the installer page where it says "Anaconda Installers" and select the correct one for your operating system  

Inside an Anaconda Prompt or Terminal you can use the included win_env.yml or mac_env.yml file to execute:  

For Windows (64-bit)  
>conda env create -f win_env.yml

For Mac (including M1 using Rosetta 2)  
>conda env create -f mac_env.yml

which will automatically create the icrop2_model environment with the necessary python packages to run the Py_SSM_iCrop2 code.  

Alternatively, you can create your own python environment manually using:  
>conda create -n <name_of_your_environment> python=3.8.5

>conda install numpy pandas xlrd openpyxl

>conda install -c plotly plotly python-kaleido

An example of running the code is displayed below:

First activate the icrop2_model environment from (base) anaconda environment:
>conda activate icrop2_model 

Then run the model:
>python py_ssm_icrop2.py -if Test_Inputs -w Test_Outputs

Both -if (inputs folder) and -w (write) should be folders.
Depending on your system you may need to include the full absolute file/folder paths to the python file and the Input/Output folders.
