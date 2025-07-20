import json, requests
from django.conf import settings
from requests.exceptions import HTTPError, Timeout
from django.core.serializers.json import DjangoJSONEncoder


def prepare_request_params(url, data, options):
    """ prepare request parameters (kwargs) """
    kwargs = {'timeout':settings.GENERAL_REQUEST_TIMEOUT, 'url':url}
    method = options['method'] if options.get('method') else 'GET'
    headers = options['headers'] if options.get('headers') else {}
    default_headers = {} if options.get('files') else {'Content-Type':'application/json'}
    default_headers.update({'Accept':'application/json'})
    kwargs['headers'] = {**default_headers, **headers} if method != "GET" else headers
    if options.get('files'): # check for multipart request
        kwargs['files'] = options['files']
    else:
        kwargs['data'] = data
        if data and kwargs['headers'].get('Content-Type') == 'application/json':
            kwargs['data'] = json.dumps(data, cls=DjangoJSONEncoder)
    if options.get('kwargs'): # check for other options to pass to request
        kwargs.update(options.pop('kwargs'))
    return method, kwargs

def check_response_error_status(resp):
    """ check response error status """
    resp_has_error, error_msg = True, ''
    try:
        resp.raise_for_status()
        resp_has_error = False
    except Timeout as time_err:
        error_msg = f'{time_err}'
        print('A time out error occurred while making request:', time_err)
    except HTTPError as http_err:
        error_msg = f'{http_err}'
        print('An http error occurred while making request:', http_err)
    except Exception as general_err:
        error_msg = f'{general_err}'
        print('An error occurred while making request:', general_err)
    if error_msg:
        settings.NOTIFICATION_ERROR = {'request_error': error_msg}
    return resp_has_error

def make_request_for_full_resp_error(url, data=None, options={}):
    """ make request and return full response and error status """
    method, kwargs = prepare_request_params(url, data, options)
    resp_has_error = True
    resp = {}
    try:
        resp = requests.request(method, **kwargs)
        resp_has_error = check_response_error_status(resp)
    except Exception as error:
        print('An error occurred while making request:', error) #, file=sys.stderr)
    return resp, resp_has_error

def make_request_for_full_resp(url, data=None, options={}):
    """ make request, log and return full response """
    resp, _ = make_request_for_full_resp_error(url, data, options)
    return resp

def make_request_for_resp_status(url, data=None, options={}):
    """ make request and return response with status """
    resp_data = None
    resp_status = None
    resp = make_request_for_full_resp(url, data, options)
    try:
        resp_status = resp.status_code
        resp_data = resp.json()
    except Exception as e:
        text = resp.text if hasattr(resp, 'text') else ''
        # error_msg = f'{e}->{text}' if text else f'{e}'
        print('An error occurred while processing response:', e, '| ', text)
    return resp_data, resp_status

def make_request_for_usable_resp(url, data=None, options={}):
    """ make request and return only usable response"""
    resp, resp_status = make_request_for_resp_status(url, data, options)
    resp_data = None
    if resp and resp_status in (200, 201, 202):
        resp_data = resp
    else:
        print('unusable request response: ', resp)
    return resp_data
