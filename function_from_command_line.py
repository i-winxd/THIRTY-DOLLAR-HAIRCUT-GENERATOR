import argparse
import inspect
from typing import Any, Callable


def my_function(a: int, b: str, c: float = 0.0) -> Any:
    """Sample docstring"""
    print(f"a: {a}, b: {b}, c: {c}")


def run_function_from_cmdline(func):
    # Get the function's docstring
    doc = inspect.getdoc(func)

    # Create the argparse.ArgumentParser with the docstring as the description
    parser = argparse.ArgumentParser(description=doc)

    # Get the function's signature
    sig = inspect.signature(func)

    # Add arguments to the parser based on the function's parameters
    for name, param in sig.parameters.items():
        help_str = func.param_descriptions.get(name, None)
        if param.default is not param.empty:
            # The parameter has a default value, so it's optional
            parser.add_argument(f'--{name}', type=param.annotation, default=param.default, help=help_str)
        else:
            # The parameter doesn't have a default value, so it's required
            parser.add_argument(name, type=param.annotation, help=help_str)

    # Parse the command line arguments
    args = parser.parse_args()

    # Call the function with the parsed arguments
    func(**vars(args))

if __name__ == "__main__":
    run_function_from_cmdline(my_function)
