from os import path
from string import Template


class Resources:

    def __init__(self, path):
        self.path = path

    def __contains__(self, name):
        fpath = path.join(self.path, name)
        return path.isfile(fpath)

    def __getitem__(self, name):
        if name in self:
            return path.join(self.path, name)
        raise NameError('%s is unknown.' % name)

    def get(self, name):
        try:
            return self[name]
        except NameError:
            return None

    def get_file(self, name, mode='rb'):
        fpath = self[name]
        return open(fpath, mode)

    def get_template(self, name, encoding='utf-8'):
        fpath = self[name]
        with open(fpath, 'r') as fd:
            data = unicode(fd.read(), encoding)
            template = Template(data.encode(encoding))
        return template
