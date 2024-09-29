# src/optimizer.py

"""Module to perform Bayesian Optimization using Optuna."""

import optuna
from typing import Any
from matlab_interface import start_matlab_engine, run_simulation
from loss_function import calculate_loss

def objective(trial: optuna.Trial) -> float:
    """
    Objective function for Optuna optimization.

    Args:
        trial (optuna.Trial): An Optuna trial object.

    Returns:
        float: The loss value to minimize.
    """
    kp = trial.suggest_float("kp", 0.0, 10.0)
    ki = trial.suggest_float("ki", 0.0, 10.0)

    # Run MATLAB simulation
    eng = start_matlab_engine()
    setpoint, actual = run_simulation(eng, kp, ki)
    eng.quit()

    # Calculate loss
    loss = calculate_loss(setpoint, actual)

    return loss

def optimize_pid(n_trials: int = 50) -> Any:
    """
    Runs the optimization process.

    Args:
        n_trials (int): Number of optimization trials.

    Returns:
        Any: The optimization result.
    """
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    print(f"Best parameters: {study.best_params}")
    print(f"Best loss: {study.best_value}")

    return study
