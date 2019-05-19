from rolepermissions.roles import AbstractUserRole

watch_lead_modules = 'watch_lead_modules'


class Lead(AbstractUserRole):
    available_permissions = {
        watch_lead_modules: True
    }


watch_client_modules = 'watch_client_modules'


class Client(AbstractUserRole):
    available_permissions = {
        watch_lead_modules: True,
        watch_client_modules: True,
    }


watch_member_modules = 'watch_member_modules'
access_cohorts = 'access_cohorts'
access_forum = 'access_forum'


class Member(AbstractUserRole):
    available_permissions = {
        watch_lead_modules: True,
        watch_client_modules: True,
        watch_member_modules: True,
        access_cohorts: True,
        access_forum: True,
    }
