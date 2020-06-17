![alt text](gitlogo.png "Logo ")

# Redcap_to_bids
This python script will convert redcap export into bids format

# Configuration file
Use the **config.json** file to set bids_root, events mapping, subjects, etc..

# Requirements
`$ pip install PyCap`

`$ pip install pandas`

# How to run
`$ python redcaptobids.py https://redcap.example.edu/api/ SomeSuperSecretAPIKeyThatNobodyElseShouldHave`


# Output
The script will create tsv phenotypes and json sidecar templates for each.
Thiese phenotypes outputs are based on the instrument_mapping element in the config.json


```
anxiety_sensitivity_index_asi3 ->

/phenotype/anxiety_sensitivity_index_asi3.tsv
/phenotype/anxiety_sensitivity_index_asi3.json
```