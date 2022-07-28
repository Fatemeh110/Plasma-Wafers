# Experimental Log/Notes (written) for Experimental Data collected
This file contains commentary and notes on the data collected within the
`ExperimentalData` folder of this repository.

## July 21, 2022
First collection of open loop data for the treatment of TEOS wafers. 31 samples
were treated, with 28 containing valid data. Treatment parameters for the data
collection are listed in [this Excel sheet](https://docs.google.com/spreadsheets/d/11XSvAFbMtYl3doMqZjAGY9qEgc7f4dpo/edit?usp=sharing&ouid=106042046026168166788&rtpof=true&sd=true).

The first folder (`2022_07_21_14h07m28s`) of the data collection for this day was
to test and ensure the data collection code was working with the setup.

The second folder (`2022_07_21_14h17m03s-Sample1-test`) was a trial run of the
parameters listed for the first sample. This sample was doubly-treated to fix a
bug in the data collection code.

The remainder of the folders contain valid experimental results for the samples
listed from 1-28. There are two folders for Sample 15. The first
(`2022_07_21_14h36m40s-Sample15`) may be discarded since the sample was dropped
after treatment.


## July 26, 2022
Additional collection of open loop data for the treatment of TEOS wafers. 72
samples were treated, with 68 containing valid data. Treatment parameters for
the data collection are listed in the same Excel sheet linked under July 21,
2022.

In addition to the valid data collected, several folders with the designation
`Sample999` contain baseline data for when the plasma jet is off.
  * `2022_07_26_11h48m21s-Sample999` - baseline for no sample underneath jet
  * `2022_07_26_11h55m32s-Sample999` - baseline for a sample underneath jet
  * `2022_07_26_12h27m42s-Sample999` - baseline after jet distance was changed
  from 10 to 7
  * `2022_07_26_13h30m07s-Sample999` - baseline after jet distance was changed
  from 7 to 3

Valid data collected starts with `2022_07_26_11h58m37s-Sample29` for Sample 29
through `2022_07_26_13h24m24s-Sample96` for Sample 96.

`2022_07_26_13h28m01s-Sample599` contains data for a test run which reduced the
plasma jet distance to 3 mm (see Excel sheet for more info on the parameters for
   this run).

## July 27, 2022
Additional collection of open loop data for the treatment of TEOS wafers. 48
samples were treated, with 45 containing valid data. Treatment parameters for
the data collection are listed in the same Excel sheet linked under July 21,
2022.

In addition to the valid data collected, several folders with the designation
`Sample999` contain baseline data for when the plasma jet is off.
  * `2022_07_27_16h42m41s-Sample999` - baseline for a sample underneath jet

Valid data collected starts with `2022_07_27_16h43m12s-Sample97` for Sample 97
through `2022_07_27_17h28m13s-Sample140` for Sample 140.

`2022_07_27_17h06m01s-Samplexx122` and `2022_07_27_17h07m43s-Samplexx122`
contain data for repeated runs of Sample 122. The first sample, the data
collection bugged out (no data folder). In the second sample (first data folder),
the plasma acted strangely, producing an orange plasma(?) plume of gas. The
second data folder contains a test run to make sure the plasma doesn't produce
the orange plume again. `2022_07_27_17h08m57s-Sample122` corresponds to valid
data for Sample 122.

`2022_07_27_17h29m32s-Sample888` was an attempted run to see if the orange plume
conditions would work again (for recording purposes). (no orange plume observed)
