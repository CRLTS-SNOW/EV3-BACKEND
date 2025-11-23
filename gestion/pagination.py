# gestion/pagination.py
from rest_framework.pagination import PageNumberPagination

class OptimizedPageNumberPagination(PageNumberPagination):
    """
    Paginación optimizada para grandes volúmenes de datos.
    Incluye información adicional para mejor rendimiento en frontend.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        from rest_framework.response import Response
        
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

