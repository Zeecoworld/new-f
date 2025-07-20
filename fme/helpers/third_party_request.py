from django.conf import settings
from fme.helpers.request_utils import make_request_for_usable_resp, make_request_for_resp_status

def termii_request(url, request_info):
    request_info = request_info or {}
    # headers = request_info.pop('headers', {})
    # request_info = { **request_info, "headers":headers}
    resp_data = {"status":424, "message":"Unable to reach service"}
    data = request_info.pop('data', None)
    resp =  make_request_for_usable_resp(url, data, request_info)
    return resp



# 200	OK: Request was successful.
# 400	Bad Request: Indicates that the server cannot or will not process the request due to something that is perceived to be a client error
# 401	Unauthorized: No valid API key provided
# 403	Forbidden: The API key doesn't have permissions to perform the request.
# 404	Not Found: The requested resource doesn't exist.
# 405	Method Not allowed: The selected http method is not allowed
# 422	Unprocessable entity: indicates that the server understands the content type of the request entity, and the syntax of the request entity is correct, but it was unable to process the contained instructions
# 429	Too Many Requests: Indicates the user has sent too many requests in a given amount of time
# 5xx	Server Errors: Something went wrong on Termii's end
