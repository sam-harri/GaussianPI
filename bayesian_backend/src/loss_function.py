import logging

import numpy as np
import polars as pl


def compute_loss(df: pl.DataFrame) -> float:
    """
    Computes the loss as the integral of the absolute error between actual and setpoint data.

    Parameters
    ----------
        df : pl.DataFrame
            DataFrame containing 'Time', 'Actual', and 'Setpoint' columns.

    Returns
    -------
        float: Computed loss value.
    """
    try:
        error = (df["Actual"] - df["Setpoint"]).abs()
        time = df["Time"]

        # Use the trapezoidal rule for numerical integration
        loss = np.trapz(error.to_numpy(), x=time.to_numpy())
        return loss
    except Exception as e:
        logging.error(f"Error computing loss: {e}")
        raise
