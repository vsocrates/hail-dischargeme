from preprocessing import *


def create_pt_prompt_per_service(discharge_row, prompts, 
                                 edstays, 
                                 demos_in, triage_in, transfers_in, diags_in, procs_in, prescriptions_in, labs_in, microbio_in):
    """
    Creates a prompt for each transfer service according to the transfers table with all structured information gathered during that service.
    This function was originally written to be used with the pandas.apply() function, but can be used in a loop as well.

    :param discharge_row: a row of the dataframe from the discharges table
    :param prompts: the prompts written to create soap notes from a CSV file
    
    :param demos_in: pts table
    :param triage_in: triage table
    :param transfers_in: transfers table
    :param diags_in: diagnoses_icd table (merged with d_icd_diagnoses)
    :param procs_in: procedures_icd table (merged with d_icd_procedures)
    :param prescriptions_in: prescriptions table
    :param labs_in: labevents table
    :param microbio_in: microbiologyevents table
    
    :return: returns a list of service-level prompts to send to GPT to create SOAP notes. 
    
    """
    demos = get_demos(discharge_row['subject_id'], demos_in)
    if demos.empty:
        age = r"[UNKNOWN AGE]"
        sex = r"[UNKNOWN SEX]"
    else:
        age = demos['anchor_age']
        sex = demos['gender']

    pt_edstays = edstays[edstays['hadm_id'] == discharge_row['hadm_id']]

    ccs = []
    for stay_id in pt_edstays['stay_id'].tolist():
        triage_info = get_triage_info(stay_id, triage_in)
        ccs.append(triage_info['chiefcomplaint'].squeeze())
        
    chief_complaints = ", ".join(ccs)

    # transfers with dates
    transfers = get_transfers(discharge_row['hadm_id'], transfers_in)

    # get stay admission diagnoses
    diags = get_diags(discharge_row['hadm_id'], diags_in)

    init_prompt = prompts.loc[prompts['prompt_name'] == "SOAP_header", "prompt"].squeeze()
    init_prompt = init_prompt.replace(r"{{age}}", str(age))
    init_prompt = init_prompt.replace(r"{{sex}}", sex)
    init_prompt = init_prompt.replace(r"{{chief_complaints}}", chief_complaints)
    init_prompt = init_prompt.replace(r"{{adm_diags}}", ', '.join(diags['long_title']))
    
    transfer_service_prompts = []

    for index, row in transfers.iterrows():        
        if row['eventtype'] == "discharge":
             transfer_service_prompts.append("")
        else:
            procs = get_procs_within_service(discharge_row['hadm_id'], row, procs_in)
            # med_orders = get_med_orders_within_service(discharge_row['hadm_id'], row)
            prescriptions = get_prescriptions_within_service(discharge_row['hadm_id'], row, prescriptions_in)
            labs = get_labs_within_service(discharge_row['hadm_id'], row, labs_in)
            microbio = get_microbio_within_service(discharge_row['hadm_id'], row, microbio_in)

            procs_str = "None" if procs.shape[0] == 0 else ', '.join(procs['long_title'].tolist()) 
            prescriptions_str = "None" if prescriptions.shape[0] == 0 else ', '.join(prescriptions['text'].tolist())
            labs_str = "None" if labs.shape[0] == 0 else ', '.join(labs['text'].tolist())
            microbio_str = "None" if microbio.shape[0] == 0 else ', '.join(microbio['text'].tolist())

            within_service_prompt = prompts.loc[prompts['prompt_name'] == 'SOAP_data', "prompt"].squeeze()
            within_service_prompt = within_service_prompt.replace(r"{{ward}}", row['careunit'])
            within_service_prompt = (within_service_prompt + 
                                     "\n\nProcedures (ordered by priority):\n----------------------------\n" + procs_str + 
                                     "\n\nMedications (ordered chronologically):\n----------------------------\n" + prescriptions_str + 
                                     "\n\nLabs:\n----------------------------\n" + labs_str + 
                                     "\n\nMicrobio Cultures:\n----------------------------\n" + microbio_str )
                            
            
            full_prompt = init_prompt + within_service_prompt
            transfer_service_prompts.append(full_prompt)
    
    return transfer_service_prompts
    


def create_pt_prompt_per_day(discharge_row, prompts, 
                             edstays,                              
                             demos_in, triage_in, transfers_in, diags_in, procs_in, prescriptions_in, labs_in, microbio_in):
    """
    Creates a prompt for each day that the patient is in the hospital (from ED arrival to discharge) with all structured information gathered during that day.
    This function was originally written to be used with the pandas.apply() function, but can be used in a loop as well.

    TODO: Still working on this - Vimig

    :param discharge_row: a row of the dataframe from the discharges table
    :param prompts: the prompts written to create soap notes from a CSV file
    
    :param demos_in: pts table
    :param triage_in: triage table
    :param transfers_in: transfers table
    :param diags_in: diagnoses_icd table (merged with d_icd_diagnoses)
    :param procs_in: procedures_icd table (merged with d_icd_procedures)
    :param prescriptions_in: prescriptions table
    :param labs_in: labevents table
    :param microbio_in: microbiologyevents table
    
    :return: returns a list of day-by-day prompts to send to GPT to create daily SOAP notes. 
    
    """

    demos = get_demos(discharge_row['subject_id'])
    if demos.empty:
        age = r"[UNKNOWN AGE]"
        sex = r"[UNKNOWN SEX]"
    else:
        age = demos['anchor_age']
        sex = demos['gender']

    pt_edstays = edstays[edstays['hadm_id'] == discharge_row['hadm_id']]

    ccs = []
    for stay_id in pt_edstays['stay_id'].tolist():
        triage_info = get_triage_info(stay_id)
        ccs.append(triage_info['chiefcomplaint'].squeeze())
        
    chief_complaints = ", ".join(ccs)

    if sex:
        pronoun = ["he","his"] if sex == "M" else ['she',"her"]
    else:
        pronoun = ["they", "their"]

    # transfers with dates
    transfers = get_transfers(discharge_row['hadm_id'])

    # get stay admission diagnoses
    diags = get_diags(discharge_row['hadm_id'])

    init_prompt = f"___ is a {age} year old {sex} that initially presented to the ED with {chief_complaints}. By the end of {pronoun[1]} hospital stay, {pronoun[0]} was given the following diagnoses: {', '.join(diags['long_title'])} in order of importance to this admission. "
    transfer_service_prompts = []

    for index, row in transfers.iterrows():
        if row['eventtype'] == "discharge":
             transfer_service_prompts.append("")
        else:
            # split time in this ward into days. 
            service_date_ranges = pd.date_range(start=row['intime'], end=row['outtime'])
            
            for previous, current in zip(service_date_ranges.tolist(), service_date_ranges[1:].tolist()):
                print(previous, current) 
            # TODO VIMIG: finish creating the per-day SOAP note

            within_service_prompt = f"The patient was transferred and stayed in the {row['careunit']} ward between {row['intime']} and {row['outtime']}. ___ received "
            
            procs = get_procs_within_service(discharge_row['hadm_id'], row)
            # med_orders = get_med_orders_within_service(discharge_row['hadm_id'], row)
            prescriptions = get_prescriptions_within_service(discharge_row['hadm_id'], row)
            labs = get_labs_within_service(discharge_row['hadm_id'], row)
            microbio = get_microbio_within_service(discharge_row['hadm_id'], row)
            
            within_service_prompt = within_service_prompt + f"the following procedures (ordered by priority): {', '.join(procs['long_title'].tolist())}.\n------------------------\n{pronoun[0]} also received the following medications (ordered chronologically) during the service: {', '.join(prescriptions['text'].tolist())}. \n------------------------\nThe following labs were also drawn during the service: {', '.join(labs['text'].tolist())}. \n------------------------\nThe physician also ordered the following microbiology cultures during the service: {', '.join(microbio['text'].tolist())}. "
            
            full_prompt = init_prompt + within_service_prompt + f"Given this information, please generate a progress note for this patient for their care during this part of their hospital course staying in the {row['careunit']} ward. Be SPECIFIC to the conditions, any abnormal labs, vitals, or procedures that were conducted, and significant medications as they relate to the hospital course."
            transfer_service_prompts.append(full_prompt)

    transfers['service_prompts'] = transfer_service_prompts
    
    return transfers
    


def create_brief_hospital_course_prompts(discharge_row, soap_notes, prompts, 
                                         edstays, radiology, 
                                         demos_in, triage_in, transfers_in, diags_in,
                                         shots=None):
    """
    Loop over the discharge instructions file in the challenge data. We include any additional examples we might want to include using the `shots` variable. 
    Creates a prompt for each transfer service according to the transfers table with all structured information gathered during that service.
    This function was originally written to be used with the pandas.apply() function, but can be used in a loop as well.

    :param discharge_row: a row of the dataframe from the discharges table
    :param prompts: the prompts written to create soap notes from a CSV file
    
    :param demos_in: pts table
    :param triage_in: triage table
    :param transfers_in: transfers table
    :param diags_in: diagnoses_icd table (merged with d_icd_diagnoses)
    :param procs_in: procedures_icd table (merged with d_icd_procedures)
    :param prescriptions_in: prescriptions table
    :param labs_in: labevents table
    :param microbio_in: microbiologyevents table
    
    :return: returns a list of service-level prompts to send to GPT to create SOAP notes. 
    
    """

    '''
    '''

    pt_edstays = edstays[edstays['hadm_id'] == discharge_row['hadm_id']]

    demos = get_demos(discharge_row['subject_id'], demos_in)
    if demos.empty:
        age = r"[UNKNOWN AGE]"
        sex = r"[UNKNOWN SEX]"
    else:
        age = demos['anchor_age']
        sex = demos['gender']

    ccs = []
    for stay_id in pt_edstays['stay_id'].tolist():
        # TODO: Drop in Triage Vitals/Pain Scale, etc. Currently only using CCs
        triage_info = get_triage_info(stay_id, triage_in)
        ccs.append(triage_info['chiefcomplaint'].squeeze())
        
    chief_complaints = ", ".join(ccs)    
    
    transfers = get_transfers(discharge_row['hadm_id'], transfers_in)
    transfers = transfers[~transfers['careunit'].isna()]
    careunits = transfers['careunit'].tolist()
    
    # transfers with dates
    tranfers = get_transfers(discharge_row['hadm_id'], transfers_in)
    diags = get_diags(discharge_row['hadm_id'], diags_in)

    # get GPT-created SOAP Notes
    soap_notes = get_soap_notes(discharge_row['hadm_id'], soap_notes)
    # get radiology reports
    radiology_reps = get_radiology_reports(discharge_row['hadm_id'], radiology)
    if shots:
        # age
        # sex
        # chief_complaints
        # wards
        # nshot
        prompt = prompts.loc[prompts['prompt_name'] == "bhc_prompt_n_shot", "prompt"].squeeze()
        prompt = prompt.replace(r"{{age}}", str(age))
        prompt = prompt.replace(r"{{sex}}", sex)
        prompt = prompt.replace(r"{{chief_complaints}}", chief_complaints)
        prompt = prompt.replace(r"{{wards}}", ", ".join(careunits))

        nshot_str = ""
        for idx, shot in enumerate(shots):
            nshot_str += f"Example {idx + 1}: {shot}"
            nshot_str += "\n-------------\n"
        
        prompt = prompt.replace(r"{{nshot}}", nshot_str)
        # f"___ is a {age} year old {sex} presenting to the ED with {chief_complaints}. Over the course of {pronoun[1]} hospital course, ___ started at {careunits[0]} and then visited {', '.join(careunits[1:])}. Over the course of their hospital stay, {pronoun[0]} was given the following diagnoses: {', '.join(diags['long_title'])} in order of importance to this admission.\n----------------------------------------------------The patient received the following radiology consult reports:{'----------------'.join(radiology_reps['text'].tolist())}.\n----------------------------------------------------Please use the following SOAP notes from the patient's complete hospital course to create a brief hospital course summary. Break down the hospital course summary by condition starting with a #: {'----------------'.join(soap_notes['gpt_SOAP_note'].tolist())}"
    else:
        # only support one shot right now
        prompt = prompts.loc[prompts['prompt_name'] == "bhc_prompt_zero_shot", "prompt"].squeeze()
        prompt = prompt.replace(r"{{age}}", str(age))
        prompt = prompt.replace(r"{{sex}}", sex)
        prompt = prompt.replace(r"{{chief_complaints}}", chief_complaints)
        prompt = prompt.replace(r"{{wards}}", ", ".join(careunits))        
        # f"___ is a {age} year old {sex} presenting to the ED with {chief_complaints}. Over the course of {pronoun[1]} hospital course, ___ started at {careunits[0]} and then visited {', '.join(careunits[1:])}. Over the course of their hospital stay, {pronoun[0]} was given the following diagnoses: {', '.join(diags['long_title'])} in order of importance to this admission.\n----------------------------------------------------The patient received the following radiology consult reports:{'----------------'.join(radiology_reps['text'].tolist())}.\n----------------------------------------------------Please use the following SOAP notes from the patient's complete hospital course to create a brief hospital course summary. Break down the hospital course summary by condition starting with a #: {'----------------'.join(soap_notes['gpt_SOAP_note'].tolist())} Use the following brief hospital course as an example: {shots[0]}"
    diags_str = "None" if diags.shape[0] == 0 else ', '.join(diags['long_title'].tolist()) 
    
    # radiology_reports_str = "None" if radiology_reps.shape[0] == 0 else '\n----------------\n'.join(radiology_reps['text'].tolist())

    # create radiology reports string
    radiology_reports_str = ""
    if radiology_reps.shape[0] == 0:
        radiology_reports_str = "None"
    else:
        for idx, radiology_report in enumerate(radiology_reps['text'].tolist()):
            radiology_reports_str += f"Radiology Report #{idx + 1}: {radiology_report}"
            radiology_reports_str += "\n-------------\n"
    
    # create SOAP NOTEs string
    soap_notes_str = ""
    if soap_notes.shape[0] == 0:
        soap_notes_str = "None"
    else:
        for idx, soap_note in enumerate(soap_notes['gpt_SOAP_note'].tolist()):
            soap_notes_str += f"SOAP NOTE #{idx + 1}: {soap_note}"
            soap_notes_str += "\n-------------\n"
    
    prompt = (prompt + 
             "\n\nDiagnoses (ordered by priority):\n----------------------------\n" + diags_str + 
             "\n\nRadiology Reports:\n----------------------------\n" + radiology_reports_str + 
             "\n\nDaily SOAP Notes:\n----------------------------\n" + soap_notes_str
             )

    
    return prompt
    