import pandas as pd


def example_function(arg1, argN):
    r"""
    One line no more that 80 character explaining very shortly what the function does

    More detailed explanation about the function,
    can have several lines

    Parameters
    ----------
    arg1 : str or list(str)
        description of arg1
        Default: <default value here>.

    ...

    argN : str or list(str)
        description of argN
        Default: <default value here>.

    Returns
    -------
    :class:`pandas.DataFrame<frame>`
        here comes the description
    (In case of no return, you can write what the function changes, e.g. updates
    `variable_x` with `y`.)

    Notes
    -----
    You can cite the references below using [1]_ or [2]_  add maths equations like this:

    .. math:: P=\frac{1}{8}\cdot\rho_{hub}\cdot d_{rotor}^{2}
        \cdot\pi\cdot v_{wind}^{3}\cdot cp\left(v_{wind}\right)

    with:
        P: power [W], :math:`\rho`: density [kg/m³], d: diameter [m],
        v: wind speed [m/s], cp: power coefficient

    References
    ----------
    .. [1] paper 1
    .. [2] paper 2

    Examples
    --------
    # Here you can write some basic python code that is tested with pytest
    >>> import src.C2_economic_functions as e_funcs
    >>> CAPEX = e_funcs.capex_from_investment(
    ...    investment_t0=220000, lifetime=20, project_life=20,
    ...    discount_factor=0.1, tax=0.15)
    >>> round(CAPEX, 7)
    253000.0

    """
    return pd.DataFrame(...)
