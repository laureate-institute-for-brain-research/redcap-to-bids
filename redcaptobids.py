# -*- coding:utf-8 -*-

# Convert RedCap Exports to BIDS format
import sys
import redcap
import json
import pandas
import os

import requests

# disable https InsecureRestsWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    
    print "============================================"
    print "Reading Config File"
    config = read_config_file()
    for key in config:
        print key,': ',config[key]
    print "============================================"

    # events = config['events'].keys()

    project = redcap.Project(sys.argv[1], sys.argv[2], verify_ssl=False)
    meta_data = project.export_metadata()

    # records = project.export_users(format='json')
    # all_froms = records[0]['forms']
    # for form in all_froms:
    #     print form

    # Get All Instruments
    
    data = {
        'token': sys.argv[2],
        'content': 'instrument',
        'format': 'json',
        'returnFormat': 'json'
    }
    r = requests.post(sys.argv[1], data=data)
    instrument_map = {}
    for instrument in r.json():
        # print instrument
        instrument_map[instrument['instrument_name']] = instrument['instrument_label']

    forms = instrument_map.keys()

    # If there exists a form's key and it's not blank, then use it
    if 'forms' in config:
        try:
            forms = config['forms'].keys()
        except AttributeError:
            print "EXPORTING ALL instruments"

    
    
    for form in forms:
        print 'Exporting %s...' % form
        # print project.export_metadata(forms = form)
        redcapData = project.export_records(records=config['records'], events= config['events'].keys(), forms=[form])

        form_df = pandas.DataFrame(redcapData)  # Change to pandas dataframe
        
        # Rename the redcap_event_name to mapping

        for event in config['events']:
            # form_df._replace(event, config['events'][event], inplace=True)
            form_df['redcap_event_name'] = form_df['redcap_event_name'].str.replace(event, config['events'][event])


        # form_df.replace('G', 1, inplace=True)
        # form_df.drop(columns=['redcap_event_name'], inplace=True)

        # Delete any completed column names
        for colname in form_df.columns:
            if 'complete' in colname:
                form_df.drop(columns=[colname], inplace=True)

        # Rename column
        form_df.rename({'record_id': 'participant_id'}, axis='columns', inplace=True)
        form_df.rename({'redcap_event_name': 'session'}, axis='columns', inplace=True)
        
        
        # Reorder Columns
        form_fields = [ field for field in form_df.columns if field != 'participant_id']
        # print form_fields
        form_df = form_df.reindex(columns=['participant_id'] + sorted(form_fields))


        # add 'sub' to the id
        for idx, participant_id in enumerate(form_df.participant_id):
            form_df.at[idx, 'participant_id'] = 'sub-' + participant_id.upper()
        
        # add 'timepoints' column
        # if len(config['events'].keys()) == 1:
        #     ses_label = config['events'][config['events'].keys()[0]]
        #     ses_events = [ses_label for x in form_df.participant_id]
        #     form_df['session'] = ses_events
        # else:
        #     print 'more than 1 event'

        # Reaplcea nan with 'n/a'
        form_df.replace(r'^\s*$', 'n/a', regex=True, inplace = True)


        # get final directory
        phenotype_dir = os.path.join(config['bids_root'], 'phenotype')
        try:
            phenotype_label = config['forms'][form]['label']
        except (KeyError,TypeError):
            # If there isn't a label, use the unieq form id
            phenotype_label = form


        # Create phenotype dir if it doesn't exists
        if not os.path.exists(phenotype_dir): os.makedirs(phenotype_dir)
        form_df.to_csv(os.path.join(phenotype_dir, phenotype_label + '.tsv'), sep='\t', index=False)    

        # SideCar
        print 'Making SideCar %s'% form

        # print project.export_project_info()

        manual_sidecar = {}

        for elm in meta_data:
            # print elm
            if elm['field_name'] in form_fields:
                manual_sidecar[elm['field_name']] = {
                    "Description": elm['field_label'],
                    "Levels": elm['select_choices_or_calculations']
                }    
        # print meta_data

        # Add Measurement Tool Description'
        manual_sidecar['MeasurementToolMetadata'] = {}
        try:
            measurement_tool_description = config['forms'][form]['Description']
            manual_sidecar['MeasurementToolMetadata'] = {}
            manual_sidecar['MeasurementToolMetadata']['Description'] = measurement_tool_description
        except (KeyError, TypeError):
            # If there isn't a label, use the unieq form id
            manual_sidecar['MeasurementToolMetadata']['Description'] = instrument_map[form]
            pass
        
        try:
            measurement_tool_term_url = config['forms'][form]['TermURL']
            
            manual_sidecar['MeasurementToolMetadata']['TermURL'] = measurement_tool_term_url
        except (KeyError, TypeError):
            # If there isn't a label, use the unieq form id
            pass
           
        
        # md_df = pandas.DataFrame(meta_data)
        #sidecar_df = pandas.DataFrame(meta_data)  # Change to pandas dataframe

        # md_df.to_csv(os.path.join(phenotype_dir, phenotype_label + '.csv'), index=False) 
        with open(os.path.join(phenotype_dir, phenotype_label + '.json'), 'w+') as json_file:
            json.dump(manual_sidecar, json_file, indent=4, sort_keys=True)
        #sidecar_df.to_csv(os.path.join(phenotype_dir, phenotype_label + '.json'), sep='\t', index=False)
