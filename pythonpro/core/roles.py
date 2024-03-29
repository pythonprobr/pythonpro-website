from rolepermissions.roles import AbstractUserRole

watch_lead_modules = 'watch_lead_modules'
access_forum = 'access_forum'


class Lead(AbstractUserRole):
    available_permissions = {
        access_forum: True,
        watch_lead_modules: True
    }


watch_cientist_modules = 'watch_cientist_modules'


class DataScientist(AbstractUserRole):
    available_permissions = {
        access_forum: True,
        watch_lead_modules: True,
        watch_cientist_modules: True,
    }


watch_client_modules = 'watch_client_modules'


class Client(AbstractUserRole):
    available_permissions = {
        access_forum: True,
        watch_lead_modules: True,
        watch_client_modules: True,
    }


watch_webdev_modules = 'watch_webdev_modules'


class Webdev(AbstractUserRole):
    available_permissions = {
        access_forum: True,
        watch_lead_modules: True,
        watch_client_modules: True,
        watch_webdev_modules: True,
    }


watch_fellow_modules = 'watch_fellow_modules'


class Fellow(AbstractUserRole):
    available_permissions = {
        access_forum: True,
        watch_lead_modules: True,
        watch_client_modules: True,
        watch_fellow_modules: True,
    }


watch_bootcamp_modules = 'watch_bootcamp_modules'
access_cohorts = 'access_cohorts'


class Bootcamper(AbstractUserRole):
    available_permissions = {
        access_forum: True,
        watch_lead_modules: True,
        watch_client_modules: True,
        watch_webdev_modules: True,
        watch_bootcamp_modules: True,
        access_cohorts: True,
    }


watch_pythonista_modules = 'watch_pythonista_modules'


class Pythonista(AbstractUserRole):
    available_permissions = {
        watch_pythonista_modules: True,
        access_forum: True,
    }


watch_member_modules = 'watch_member_modules'


class Member(AbstractUserRole):
    available_permissions = {
        watch_pythonista_modules: True,
        watch_webdev_modules: True,
        watch_lead_modules: True,
        watch_client_modules: True,
        watch_member_modules: True,
        watch_bootcamp_modules: True,
        access_cohorts: True,
        access_forum: True,
    }
