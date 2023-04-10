# Code for running APPJ experiments with silicon wafers

This code was used for the open-loop collection of data from the atmospheric pressure plasma jet (APPJ) when using TEOS oxide silicon wafers as the substrate/surface material.

`ExperimentalData` contains all of the collected data and details of the settings for each sample are found in `OL_Settings.xlsx`.

`utils` provides some general utilities for running experiments. Additional details regarding the files are detailed as follows:

  * `APPJPythonFunctions.py` contains most of the functions that allow for data retrieval from the APPJ
  * `experiments.py` contains an `Experiments` class that can be used to run open-loop (no controller) or closed-loop (with controller) experiments. This repository only required the use of the open-loop data collection functionality. Open loop data may be provided by sending a sequence of power and/or flow rate inputs.
  * `uvcRadiometry.py` and `uvtypes.py` are additional files that are used to obtain measurements from the thermal camera
  * `uvcRadiometry_test.py` is used to test operation of the thermal camera. This file should be run in the `utils` directory
  
`appj_requirements.txt` contains the necessary Python dependencies/libraries that are needed to operate the data acquisition from the APPJ. More information regarding the Python dependencies and connection from the APPJ setup to your computer may be found in this repository.

`appj_warmup.py` is used to warm up the APPJ. Generally, it is recommended to run the APPJ at some nominal settings for 10-15 minutes to allow for consistent data acquisitions afterwards. This script will do this as long as your device is set up properly.

`run_exp.py` is the script used to run an experiment and perform the data acquisition

`spectroscopyLive.py` is a script to test the spectroscopy (optical emission spectra) measurement. It requires an additional argument when you run the `python3 spectroscopyLive.py [time\s]` command. The additional argument is how long you would like to run the test in terms of seconds, i.e., 100 would run the test for roughly 100 seconds.
