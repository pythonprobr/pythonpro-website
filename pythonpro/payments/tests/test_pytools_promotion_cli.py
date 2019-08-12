from django.core.management import call_command


def test_pytools_command(mocker):
    mock = mocker.patch(
        'pythonpro.payments.management.commands.pytools_promotion.user_facade.run_pytools_promotion_campaign')
    call_command('pytools_promotion')
    mock.assert_called_once_with()
