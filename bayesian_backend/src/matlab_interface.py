# src/matlab_interface.py

"""Module to interface with MATLAB simulations."""

import matlab.engine
from typing import Tuple, List

def start_matlab_engine() -> matlab.engine.MatlabEngine:
    """
    Starts the MATLAB engine.

    Returns:
        matlab.engine.MatlabEngine: An instance of the MATLAB engine.
    """
    eng = matlab.engine.start_matlab()
    eng.addpath("matlab/", nargout=0)
    return eng

def run_simulation(
    eng: matlab.engine.MatlabEngine, kp: float, ki: float
) -> Tuple[List[float], List[float]]:
    """
    Runs the MATLAB simulation with given KP and KI values.

    Args:
        eng (matlab.engine.MatlabEngine): MATLAB engine instance.
        kp (float): Proportional gain.
        ki (float): Integral gain.

    Returns:
        Tuple[List[float], List[float]]: Tuple of setpoint and actual timeseries data.
    """
    # Set parameters in MATLAB workspace
    eng.workspace['KP'] = kp
    eng.workspace['KI'] = ki

    # Run the simulation
    eng.eval("out = sim('simulink_model');", nargout=0)

    # Retrieve data
    setpoint = eng.workspace['out'].get('setpoint').tolist()
    actual = eng.workspace['out'].get('actual').tolist()

    return setpoint, actual
