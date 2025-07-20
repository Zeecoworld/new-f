from rest_framework import serializers, status
from rest_framework.exceptions import APIException, ValidationError

class ValidationError422(APIException):
    """ ValidationError422 """
    status_code = status.HTTP_400_BAD_REQUEST

class BaseSerializer(serializers.Serializer):
    """ BaseSerializer """

    # def is_valid(self, *, raise_exception=False):
    #     try:
    #         return super().is_valid(raise_exception=raise_exception)
    #     except ValidationError as err:
    #         def format_error(detail):
    #             errors = ""
    #             for i in detail:
    #                 if not isinstance(detail[i], list):
    #                     errors += format_error(detail[i])
    #                 for err_msg in detail[i]:
    #                     errors += f"{i}: {err_msg}, "
    #             return errors
    #         raise ValidationError422(detail=f"{format_error(err.detail)}")

class PaginationParamSerializer(BaseSerializer):
    page_size = serializers.IntegerField(min_value=1, required=False)
