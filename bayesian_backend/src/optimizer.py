# src/optimizer.py

import logging
from typing import Any, Dict

import optuna
import polars as pl

from matlab_interface import run_simulation
from loss_function import compute_loss


def objective(
    trial: optuna.trial.Trial,
    eng: Any,
    model_name: str,
    results_df: pl.DataFrame,
    data_dir: str,
) -> float:
    """
    Objective function for Bayesian optimization using Optuna.

    Parameters
    ----------
    trial (optuna.trial.Trial)
        Optuna trial object.
    eng : matlab.engine.MatlabEngine
        MATLAB engine instance.
    model_name : str
        Name of the Simulink model.
    results_df : pl.DataFrame
        DataFrame to store optimization results.
    data_dir : str
        Path to the CSV file for storing results.

    Returns
    -------
        float: Loss value to minimize.
    """
    KC = trial.suggest_float("KC", 0.03, 3)
    KI = trial.suggest_float("KI", 0.0005, 0.5)

    try:
        df_simulation = run_simulation(eng, model_name, KC, KI)
        loss = compute_loss(df_simulation)

        # Append results to the DataFrame
        new_row = pl.DataFrame(
            {"Trial": [trial.number], "KC": [KC], "KI": [KI], "Loss": [loss]}
        )
        results_df = pl.concat([results_df, new_row], how="vertical")

        # Save the DataFrame to CSV
        results_df.write_csv(f"{data_dir}/optimization_history.csv")
        logging.info(
            f"Trial {trial.number}: KC={KC:.4f}, KI={KI:.4f}, Loss={loss:.6f}."
        )

        # Save individual simulation data
        simulation_filename = (
            f"{data_dir}/KC-{KC:.4f}_KI-{KI:.4f}_trial-{trial.number}.csv"
        )
        df_simulation.write_csv(simulation_filename)
        logging.info(f"Simulation data saved to '{simulation_filename}'.")

        return loss
    except Exception as e:
        logging.error(f"Objective function failed at trial {trial.number}: {e}")
        return float("inf")


def run_optimization(
    eng: Any, model_name: str, n_trials: int = 50, data_dir: str = "data/"
) -> Dict[str, Any]:
    """
    Runs the Bayesian optimization using Optuna.

    Parameters
    ----------
    eng : matlab.engine.MatlabEngine
        MATLAB engine instance.
    model_name : str
        Name of the Simulink model.
    n_trials : int, default=50
        Number of optimization trials.
    results_csv_path (str):
        Path to the CSV file for storing results.

    Returns:
        Dict[str, Any]: Dictionary containing the best parameters and loss.
    """
    # Initialize the results DataFrame
    results_df = pl.DataFrame(columns=["Trial", "KC", "KI", "Loss"])

    # Create the study
    study = optuna.create_study(direction="minimize")
    logging.info("Starting optimization...")

    # Define the objective function wrapper
    def wrapped_objective(trial):
        return objective(trial, eng, model_name, results_df, data_dir)

    # Run the optimization
    study.optimize(wrapped_objective, n_trials=n_trials)
    logging.info("Optimization completed.")

    # Get the best parameters and loss
    best_params = study.best_params
    best_loss = study.best_value

    return {"best_params": best_params, "best_loss": best_loss}
