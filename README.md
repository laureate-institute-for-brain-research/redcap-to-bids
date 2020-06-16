# Redcap_to_bids
This python script will convert redcap export into bids format

# Configuration file
Use the **config.json** file to set events mapping, subjects, etc..


# How to run
`python recaptobids.py https://redcap.example.edu/api/ SomeSuperSecretAPIKeyThatNobodyElseShouldHave`


# Output
The script will create tsv phenotypes and json sidecar templates for each.

Example, if there i