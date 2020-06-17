#!/usr/bin/env python

# Convert RedCap Exports to BIDS format
import sys
import redcap
import json
import pandas
import os


def read_config_file():
    """
    Return json dict
    """
    # Opening JSON file 
    f = open('config.json',) 
    
    # returns JSON object as  
    # a dictionary 
    data = json.load(f)     
    # Closing file 
    f.close()
    
    return data



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Enter redcap uri and redcap token"
        print "e.g. $ python redcaptobids.py https://redcap.example.edu/api/ SomeSuperSecretAPIKeyThatNobodyElseShouldHave"
        sys.exit()

    
    print "Reading Config File"
    config = read_config_file()
    for key in config:
        print key,': ',config[key]
    print "==========="

    events = config['events'].keys()
    print config['forms'].keys()

    project = redcap.Project(sys.argv[1], sys.argv[2], verify_ssl=False)

    
    for form in config['forms'].keys():
        print 'Exporting %s...' % form
        # print project.export_metadata(forms = form)

        forms = project.forms[:2]
        subset = project.export_records(forms=forms)
        redcapData = project.export_records(records=config['records'], events= config['events'].keys(), forms=[form])

        form_df = pandas.DataFrame(redcapData)  # Change to pandas dataframe
        
        # Remove column
        form_df.drop(columns=['redcap_event_name'], inplace=True)

        # Rename column
        form_df.rename({'record_id': 'participant_id'}, axis='columns', inplace=True)
        
        # Reorder Columns
        form_fields = [ field for field in form_df.columns if field != 'participant_id']
        # print form_fields
        form_df = form_df.reindex(columns=['participant_id'] + sorted(form_fields))


        # add 'sub' to the id
        for idx, participant_id in enumerate(form_df.participant_id):
            form_df.at[idx, 'participant_id'] = 'sub-' + participant_id.upper()
            
        # Reaplcea nan with 'n/a'
        form_df.replace(r'^\s*$', 'n/a', regex=True, inplace = True)


        # get final directory
        phenotype_dir = os.path.join(config['bids_root'], 'phenotype')
        phenotype_label = config['forms'][form]['label']


        # Create phenotype dir if it doesn't exists
        if not os.path.exists(phenotype_dir): os.makedirs(phenotype_dir)
        form_df.to_csv(os.path.join(phenotype_dir, phenotype_label + '.tsv'), sep = '\t', index=False)
