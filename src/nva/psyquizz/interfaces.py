# -*- coding: utf-8 -*-

from cromlech.browser import exceptions
from siguvtheme.uvclight import IDGUVRequest


class IQuizzLayer(IDGUVRequest):
    pass


class ICompanyRequest(IQuizzLayer):
    pass


class IRegistrationRequest(IQuizzLayer):
    pass


class IAnonymousRequest(IQuizzLayer):
    pass


class QuizzAlreadyCompleted(exceptions.HTTPForbidden):
    pass


class QuizzClosed(exceptions.HTTPForbidden):
    pass
