class XRayError(Exception):
    def __init__(self, details):
        self.details = details

class UserExistsError(XRayError):
    def __init__(self, details, email):
        self.email = email
        super(UserExistsError, self).__init__(details)

class EmailExistsError(XRayError):
    def __init__(self, details, email):
        self.email = email
        super(EmailExistsError, self).__init__(details)

class EmailNotFoundError(XRayError):
    def __init__(self, details, email):
        self.email = email
        super(EmailNotFoundError, self).__init__(details)

class InboundNotFoundError(XRayError):
    def __init__(self, details, inbound_tag):
        self.inbound_tag = inbound_tag
        super(InboundNotFoundError, self).__init__(details)

class InboundAlreadyExistsError(XRayError):
    def __init__(self, details, inbound_tag):
        self.inbound_tag = inbound_tag
        super(InboundAlreadyExistsError, self).__init__(details)

class AddressAlreadyInUseError(XRayError):
    def __init__(self, details, port):
        self.port = port
        super(AddressAlreadyInUseError, self).__init__(details)

class NotSupportProtocolError(XRayError):
    def __init__(self, details):
        super(NotSupportProtocolError, self).__init__(details)