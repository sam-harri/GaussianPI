# src/loss_function.py

"""Module to calculate the loss function."""

from typing import List

def calculate_loss(setpoint: List[float], actual: List[float]) -> float:
    """
    Calculates the integral of the absolute error between setpoint and actual data.

    Args:
        setpoint (List[float]): The desired setpoint timeseries data.
        actual (List[float]): The actual timeseries data from the simulation.

    Returns:
        float: The calculated loss value.
    """
    error = [abs(s - a) for s, a in zip(setpoint, actual)]
    loss = sum(error)  # Assuming uniform time steps

    return loss
