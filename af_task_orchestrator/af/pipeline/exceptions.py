class DpoException(Exception):
    pass


class AnalysisError(Exception):
    pass


class RequiredAnalysisRequest(DpoException):
    pass


class InvalidAnalysisRequest(DpoException):
    pass


class FileParseException(Exception):
    pass


class InvalidFilePath(Exception):
    pass
