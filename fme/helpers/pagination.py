from rest_framework.pagination import PageNumberPagination

class PaginationHandlerMixin(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    # max_page_size = 50

    
    def get_paginated_response(self, data):
        return {
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,
            'current': self.page.number,
            'entity': data
        }
