from queueing import get_channel


def request_vault_appraisal(vault_number: int):
    get_channel('appraisal_requests')\
        .basic_publish(exchange='', routing_key='appraisal_request', body=str(vault_number))

