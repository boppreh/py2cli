import sys
import re
from inspect import signature, Signature, _empty

class Args(object):
    """
    Class for storing arguments provided by the user and interactively calling
    functions with them.
    """
    def __init__(self, argv):
        """
        Creates a new Args instance from a list of command line arguments.
        """
        self.args = []
        self.kwargs = {}

        arguments = argv[1:]
        while len(arguments):
            arg = arguments.pop(0)
            if arg.startswith('-'):
                if '=' in arg:
                    key, value = re.match('--?(\w+)=(.+)', arg).groups()
                else:
                    key, value = arg.replace('-', ''), arguments.pop(0)
                self.kwargs[key] = value
            else:
                self.args.append(arg)

        self.official_args = {}

    def request(self, name, description='', default=_empty):
        """
        Returns a specific argument, interactively prompting the user for items
        if it doesn't exist.
        """
        if name in self.kwargs:
            return self.kwargs[name]
        elif name[0] in self.kwargs:
            return self.kwargs[name[0]]
        elif len(self.args):
            return self.args.pop(0)
        else:
            return self.request_interactive(name, description, default)

    def request_interactive(self, name, description='', default=_empty):
        """
        Requests a value by prompting the user.
        """
        name = name.replace('_', ' ').title()
        if description:
            prompt = '{} ({}): '.format(name, description)
        else:
            prompt = '{}: '.format(name)

        if default is _empty:
            return input(prompt)
        else:
            return self._prompt_for_value(prompt, default)

    def _prompt_for_value(self, prompt, default=_empty):
        """
        Displays a prompt to the user and returns the evaluated result,
        possibly returning an empty value if the user didn't type anything.
        """
        result = input(prompt + '(default: {}) '.format(default))
        if result == '':
            return default
        else:
            try:
                return eval(result)
            except (SyntaxError, NameError):
                return result

    def ensure_exists(self, name, description='', default=_empty):
        """
        Ensures a given argument exists, possibly prompting the user to enter 
        it.
        """
        self.official_args[name] = self.request(name, description, default)

    def apply(self, function):
        """
        Apply the arguments that have been ensured to exist to a given
        function.
        """
        return function(**self.official_args)

if __name__ == '__main__':
    from os import path

    args = Args(sys.argv)

    script = args.request('file', 'Python file to be executed')
    if not '.py' in script:
        script += '.py'
    assert path.exists(script), 'Script file {} does not exist'.format(script)

    sys.path.append(path.dirname(script))
    script_name = path.splitext(path.basename(script))[0]

    function_name = args.request('function', 'function to be called')
    module = __import__(script_name)
    function = getattr(module, function_name)

    parameters = signature(function).parameters
    for param_name, param in parameters.items():
        if '*' in param_name:
            continue

        if param.annotation is not Signature.empty:
            annotation = param.annotation
        else:
            annotation = ''
        args.ensure_exists(param_name, annotation, param.default)

    print('')

    result = args.apply(function)
    if result is not None:
        print(result)