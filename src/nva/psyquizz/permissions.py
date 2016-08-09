from grokcore.security import name, Permission


class ManageCompany(Permission):
    name('manage.company')


class ManageSchool(Permission):
    name('manage.school')
