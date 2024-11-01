from rest_framework.pagination import PageNumberPagination


class DefaultProductPagination(PageNumberPagination):
    page_size = 10