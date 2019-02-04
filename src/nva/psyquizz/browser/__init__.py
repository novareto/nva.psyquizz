from uvclight import Page as BasePage
from zope.component.hooks import getSite


class Page(BasePage):

    def namespace(self):
        ns = BasePage.namespace(self)
        ns['site'] = getSite()
        ns['title'] = self.request.environment['customer.title']
        return ns
