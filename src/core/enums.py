from enum import StrEnum


class ViewAction(StrEnum):
    LIST = "list"
    RETRIEVE = "retrieve"
    CREATE = "create"
    UPDATE = "update"
    PARTIAL_UPDATE = "partial_update"


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
