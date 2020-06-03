from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pythonpro.core.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    first_name = models.CharField(_('first name'), max_length=30)
    email = models.EmailField(_('email address'), unique=True, error_messages={
        'unique': _("A user with that username already exists."),
    })
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    source = models.CharField(_('source'), max_length=255, default='unknown')

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.get_short_name()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UserInteraction(models.Model):
    """
    Class representing User important interactions on platform. The goal is to extract metrics about user behaviour
    """



    class Meta:
        indexes = [
            models.Index(fields=['user', 'creation']),
            models.Index(fields=['category', '-creation']),
        ]
        verbose_name = 'Histórico de Usuário'
        verbose_name_plural = 'Históricos de Usuários'

    BECOME_DATA_SCIENTIST = 'BECOME_DATA_SCIENTIST'
    BECOME_LEAD = 'BECOME_LEAD'
    ACTIVATED = 'ACTIVATED'
    CLIENT_LP = 'CLIENT_LP'
    CLIENT_CHECKOUT = 'CLIENT_CHECKOUT'
    CLIENT_CHECKOUT_FORM = 'CLIENT_CHECKOUT_FORM'
    CLIENT_BOLETO = 'CLIENT_BOLETO'
    BECOME_CLIENT = 'BECOME_CLIENT'
    MEMBER_LP = 'MEMBER_LP'
    MEMBER_CHECKOUT = 'MEMBER_CHECKOUT'
    MEMBER_CHECKOUT_FORM = 'MEMBER_CHECKOUT_FORM'
    MEMBER_BOLETO = 'MEMBER_BOLETO'
    WAITING_LIST = 'WAITING_LIST'
    BECOME_MEMBER = 'BECOME_MEMBER'
    WEBDEV_CHECKOUT_FORM = 'WEBDEV_CHECKOUT_FORM'
    BECOME_WEBDEV = 'BECOME_WEBDEV'
    LAUNCH_LP = 'LAUNCH_LP'
    LAUNCH_SUBSCRIPTION = 'LAUNCH_SUBSCRIPTION'
    CPL1 = 'CPL1'
    CPL2 = 'CPL2'
    CPL3 = 'CPL3'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
        max_length=32,
        choices=(
            (
                (BECOME_LEAD, 'User become Lead'),
                (ACTIVATED, 'User Watched first video class'),
                (CLIENT_LP, 'User visited Client Landing Page'),
                (CLIENT_CHECKOUT, 'User clicked on Client checkout button'),
                (CLIENT_CHECKOUT_FORM, 'User Filled Client Checkout form'),
                (CLIENT_BOLETO, 'User generated a Client Boleto'),
                (BECOME_CLIENT, 'User become Client'),
                (MEMBER_LP, 'User visited Member Landing Page'),
                (MEMBER_CHECKOUT, 'User clicked on Member checkout Button'),
                (MEMBER_CHECKOUT_FORM, 'User Filled Member Checkout form'),
                (WEBDEV_CHECKOUT_FORM, 'User Filled Webdev Checkout form'),
                (MEMBER_BOLETO, 'User generate Member Boleto'),
                (WAITING_LIST, 'User subscribed to Waiting List'),
                (BECOME_MEMBER, 'User Become Member'),
                (BECOME_WEBDEV, 'User Become Webdev'),
                (LAUNCH_LP, 'User visited Launch Landing Page'),
                (LAUNCH_SUBSCRIPTION, 'User subscribed to launch'),
                (CPL1, 'User Visited CPL1'),
                (CPL2, 'User Visited CPL2'),
                (CPL3, 'User Visited CPL3'),
                (BECOME_DATA_SCIENTIST, 'User Become Data Scientist'),
            )
        )
    )
    source = models.CharField(blank=True, null=True, max_length=32, help_text='Traffic source origin')
