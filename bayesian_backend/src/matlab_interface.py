import logging
from typing import Any, Dict

import numpy as np
import polars as pl
import matlab.engine


def initialize_matlab_engine(matlab_path: str = ".") -> matlab.engine.MatlabEngine:
    """
    Initializes the MATLAB engine and sets the working directory.

    Parameters
    ----------
    matlab_path : str, default='.'
        Path to the MATLAB working directory.

    Returns
    -------
        matlab.engine.MatlabEngine: An instance of the MATLAB engine.
    """
    try:
        logging.info("Starting MATLAB engine...")
        eng = matlab.engine.start_matlab()
        eng.cd(matlab_path)
        logging.info(
            f"MATLAB engine initialized. Current directory set to '{matlab_path}'."
        )
        return eng
    except Exception as e:
        logging.error(f"Error initializing MATLAB engine: {e}")
        raise


def run_simulation(
    eng: matlab.engine.MatlabEngine, model_name: str, KC: float, KI: float
) -> pl.DataFrame:
    """
    Runs the Simulink model with the given KC and KI parameters.

    Parameters
    ----------
    eng : matlab.engine.MatlabEngine
        MATLAB engine instance.
    model_name : str
        Name of the Simulink model to run.
    KC : float
        Proportional gain for PID controller.
    KI : float
        Integral gain for PID controller.

    Returns
    -------
        pl.DataFrame: DataFrame containing 'Time', 'Actual', and 'Setpoint' data.
    """
    try:
        eng.workspace["KC"] = KC
        eng.workspace["KI"] = KI

        # Load the model if not already loaded
        loaded_models = eng.eval("Simulink.allBlockDiagrams", nargout=1)
        if model_name not in loaded_models:
            eng.load_system(model_name)
            logging.info(f"Loaded Simulink model '{model_name}'.")

        # Run the simulation
        eng.eval(f"out = sim('{model_name}')", nargout=0)
        eng.eval("data = struct(out)", nargout=0)
        data: Dict[Any, Any] = eng.workspace["data"]

        # Extract simulation data
        actual_data = np.array(data["Data"]["ActualSimOut"]).flatten()
        setpoint_data = np.array(data["Data"]["SetpointSimOut"]).flatten()
        time_data = np.array(data["Data"]["tout"]).flatten()

        # Find the minimum length of the three arrays
        min_length = min(len(actual_data), len(setpoint_data), len(time_data))

        # Trim all arrays to the minimum length
        actual_data = actual_data[:min_length]
        setpoint_data = setpoint_data[:min_length]
        time_data = time_data[:min_length]

        # Create a Polars DataFrame
        df = pl.DataFrame(
            {"Time": time_data, "Actual": actual_data, "Setpoint": setpoint_data}
        )

        return df

    except Exception as e:
        logging.error(f"Simulation error with KC={KC}, KI={KI}: {e}")
        raise
