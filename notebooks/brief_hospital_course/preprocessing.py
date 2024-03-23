import pandas as pd 

# create initial input text prompt
def get_demos(subject_id, pts):
    # has gender, anchor-age, date-of-death if exists
    return pts[pts['subject_id'] == subject_id].squeeze()
    
def get_transfers(hadm_id, transfers):
    return transfers[transfers['hadm_id'] == hadm_id].sort_values("intime").squeeze()

def get_triage_info(stay_id, triage):
    return triage[triage['stay_id'] == stay_id]
    
def get_procs(hadm_id, procs):
    adm_procs = procs[procs['hadm_id'] == hadm_id]
    return adm_procs.sort_values("seq_num")

def get_diags(hadm_id, diags):
    adm_diags = diags[diags['hadm_id'] == hadm_id]
    return adm_diags.sort_values("seq_num")

def get_med_orders(hadm_id, med_orders):
    med_admin = med_orders[(med_orders['hadm_id'] == hadm_id) & (med_orders['event_txt'] == "Administered")]
    med_admin['admin_text'] = med_admin['medication'] + " at " + med_admin['charttime'].dt.strftime('%B %d, %Y, %r')
    return med_admin

def get_prescriptions(hadm_id, prescriptions):
    adm_prescriptions = prescriptions[(prescriptions['hadm_id'] == hadm_id)]
    
def get_labs(hadm_id, labs):
    adm_labs = labs[(labs['hadm_id'] == hadm_id)]

def get_microbio(hadm_id, microbio):
    adm_microbio = microbio[(microbio['hadm_id'] == hadm_id)]


def get_med_orders_within_service(hadm_id, transfer_event, med_orders):
    med_admin = med_orders[(med_orders['hadm_id'] == hadm_id) & (med_orders['event_txt'] == "Administered")]
    med_admin = med_admin.sort_values("emar_seq")
    
    adm_diags_in_unit = med_admin[(med_admin['charttime'] > transfer_event['intime'])
                                & (med_admin['charttime'] < transfer_event['outtime'])]

    # adm_diags_in_unit['admin_text'] = adm_diags_in_unit['medication'] + " at " + adm_diags_in_unit['charttime'].dt.strftime('%B %d, %Y, %r')
    
    return adm_diags_in_unit

def get_procs_within_service(hadm_id, transfer_event, procs):
    adm_procs = procs[procs['hadm_id'] == hadm_id]
    adm_procs = adm_procs.sort_values("seq_num")
    
    adm_procs_in_unit = adm_procs[(adm_procs['chartdate'] > transfer_event['intime'])
                                & (adm_procs['chartdate'] < transfer_event['outtime'])]
    return adm_procs_in_unit


def get_prescriptions_within_service(hadm_id, transfer_event, prescriptions):
    adm_prescriptions = prescriptions[(prescriptions['hadm_id'] == hadm_id)]
    # adm_prescriptions['text'] = adm_prescriptions['drug'] + " " + adm_prescriptions['prod_strength']
    adm_prescriptions_in_unit = adm_prescriptions[(adm_prescriptions['starttime'] > transfer_event['intime'])
                                & (adm_prescriptions['starttime'] < transfer_event['outtime'])]
    return adm_prescriptions_in_unit
    
def get_labs_within_service(hadm_id, transfer_event, labs):
    adm_labs = labs[(labs['hadm_id'] == hadm_id)]
    adm_labs = adm_labs[(adm_labs['charttime'] > transfer_event['intime'])
                                & (adm_labs['charttime'] < transfer_event['outtime'])]
    return adm_labs
    
def get_microbio_within_service(hadm_id, transfer_event, microbio):
    adm_microbio = microbio[(microbio['hadm_id'] == hadm_id)]
    # TODO: we need to do something because chartdate is required, but charttime isn't, so what do we do when we don't have times? 
    adm_microbio = adm_microbio[(adm_microbio['chartdate'] > transfer_event['intime'])
                                & (adm_microbio['chartdate'] < transfer_event['outtime'])]
    return adm_microbio


#####################
# TODO VIMIG: check methods to pull data by day
def get_med_orders_within_day(hadm_id, day_window):
    med_admin = med_orders[(med_orders['hadm_id'] == hadm_id) & (med_orders['event_txt'] == "Administered")]
    med_admin = med_admin.sort_values("emar_seq")
    
    adm_diags_in_unit = med_admin[(med_admin['charttime'] > day_window[0])
                                & (med_admin['charttime'] < day_window[1])]

    # adm_diags_in_unit['admin_text'] = adm_diags_in_unit['medication'] + " at " + adm_diags_in_unit['charttime'].dt.strftime('%B %d, %Y, %r')
    
    return adm_diags_in_unit

def get_procs_within_day(hadm_id, day_window):
    adm_procs = procs[procs['hadm_id'] == hadm_id]
    adm_procs = adm_procs.sort_values("seq_num")
    
    adm_procs_in_unit = adm_procs[(adm_procs['chartdate'] > day_window[0])
                                & (adm_procs['chartdate'] < day_window[1])]
    return adm_procs_in_unit


def get_prescriptions_within_day(hadm_id, day_window):
    adm_prescriptions = prescriptions[(prescriptions['hadm_id'] == hadm_id)]
    # adm_prescriptions['text'] = adm_prescriptions['drug'] + " " + adm_prescriptions['prod_strength']
    adm_prescriptions_in_unit = adm_prescriptions[(adm_prescriptions['starttime'] > day_window[0])
                                & (adm_prescriptions['starttime'] < day_window[1])]
    return adm_prescriptions_in_unit
    
def get_labs_within_day(hadm_id, day_window):
    adm_labs = labs[(labs['hadm_id'] == hadm_id)]
    adm_labs = adm_labs[(adm_labs['charttime'] > day_window[0])
                                & (adm_labs['charttime'] < day_window[1])]
    return adm_labs
    
def get_microbio_within_day(hadm_id, day_window):
    adm_microbio = microbio[(microbio['hadm_id'] == hadm_id)]
    # TODO: we need to do something because chartdate is required, but charttime isn't, so what do we do when we don't have times? 
    adm_microbio = adm_microbio[(adm_microbio['chartdate'] > day_window[0])
                                & (adm_microbio['chartdate'] < day_window[1])]
    return adm_microbio

# create initial input text prompt
def get_soap_notes(hadm_id, soap_notes):
    return soap_notes[soap_notes['hadm_id'] == hadm_id]

def get_radiology_reports(hadm_id, radiology):
    adm_radiology = radiology[radiology['hadm_id'] == hadm_id]
    return adm_radiology.sort_values("note_seq")


