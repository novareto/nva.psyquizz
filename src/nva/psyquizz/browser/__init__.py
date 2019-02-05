from uvclight import Page as BasePage
from zope.component.hooks import getSite


class Page(BasePage):

    def namespace(self):
        ns = BasePage.namespace(self)
        site = getSite()
        ns['config'] = site.configuration 
        return ns
