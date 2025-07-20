from rest_framework import status
from rest_framework.response import  Response
from rest_framework.exceptions import APIException

STATUSES = {
    200:status.HTTP_200_OK,
    201:status.HTTP_201_CREATED,
    202:status.HTTP_202_ACCEPTED,
}

class ErrorOccurred(APIException):
    status_code = 201
    default_code = "An error occurred"
    default_detail = "An error has occurred, and we are actively working to resolve it. We apologize for any inconvenience and will provide an update soon."


def response(data):
    status_code = data.get("status")
    try:
        status_code = int(status_code)
    except Exception as err:
        print("The status has to be numeric:", err)
        status_code = 400
    entity = data.get("data")
    if (entity or isinstance(entity, list)) and status_code in range(200, 227): # also check for empty list
        if status_code == 204:
            resp = Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            status_code = status_code if status_code in STATUSES.keys() else 200
            data.pop("status")
            resp = Response(data, status=STATUSES[status_code])
        return resp
    else:
        if status_code == 403:
            return Response(
                {
                    "error": "Forbidden",
                    "message": "Your account type does not have access to this system.",
                    "detail": "Only Administrators, Mentors, and Facilitators can access this system."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        ErrorOccurred.status_code = status_code
        ErrorOccurred.default_code = data.get("message")
        ErrorOccurred.default_detail = data.get("message")
        raise ErrorOccurred()
