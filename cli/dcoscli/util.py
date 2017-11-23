import sys

from functools import wraps

import docopt

from dcos import emitting

emitter = emitting.FlatEmitter()


def decorate_docopt_usage(func):
    """Handle DocoptExit exception

    :param func: function
    :type func: function
    :return: wrapped function
    :rtype: function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except docopt.DocoptExit as e:
            emitter.publish("Invalid subcommand usage\n")
            emitter.publish(e)
            return 1
        return result
    return wrapper


def confirm(prompt, yes):
    """
    :param prompt: message to display to the terminal
    :type prompt: str
    :param yes: whether to assume that the user responded with yes
    :type yes: bool
    :returns: True if the user responded with yes; False otherwise
    :rtype: bool
    """

    if yes:
        return True
    else:
        count = 0
        while count < 3:
            sys.stdout.write('{} [yes/no] '.format(prompt))
            sys.stdout.flush()
            response = _read_response().lower()
            if response == 'yes' or response == 'y':
                return True
            elif response == 'no' or response == 'n':
                return False
            else:
                msg = "'{}' is not a valid response.".format(response)
                emitter.publish(msg)
                count += 1
        return False


def confirm_text(prompt, confirmation_text):
    """
    :param prompt: message to display to the terminal
    :type prompt: str
    :param expected_text: The text to compare user input to.
    :type expected_text: str
    :returns: True if the user replies with the expected text; False otherwise
    :rtype: bool
    """

    count = 0
    while count < 3:
        sys.stdout.write('{}: '.format(prompt))
        sys.stdout.flush()
        response = _read_response()
        if response == confirmation_text:
            return True
        else:
            msg = "Expected '{}'. You supplied '{}'.".format(
                confirmation_text,
                response
            )
            emitter.publish(msg)
            count += 1
    return False


def choicelist(choices, msg='Please choose: '):
    """
    Allow to pick an item from a choicelist. For example :

        Please choose a login provider for your linked cluster:
        1) dcos-uid-password
        2) saml-sp-initiated
        (1-2): [...]

    :param choices: choices for the list
    :type choices: list of str
    :returns: the chosen item
    :rtype: str
    """

    emitter.publish(msg)
    for i, choice in enumerate(choices):
        emitter.publish('{}) {}'.format(i+1, choice))

    # Write to stdout directly not to have a new line.
    sys.stdout.write('({}-{}): '.format(1, len(choices)))
    sys.stdout.flush()

    try:
        chosen_id = int(_read_response())
    except ValueError:
        return None

    return choices[chosen_id-1] if len(choices) >= chosen_id else None


def _read_response():
    """
    :returns: The content of STDIN
    :rtype: str
    """
    return sys.stdin.readline().strip()
