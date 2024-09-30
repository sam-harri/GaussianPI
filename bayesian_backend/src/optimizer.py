import logging
from typing import Any, Dict, Optional
import time
import os

import optuna
import polars as pl
from plotly.io import show, write_html
from dotenv import load_dotenv

from matlab_interface import run_simulation
from loss_function import compute_loss


load_dotenv()


def objective(
    trial: optuna.trial.Trial,
    eng: Any,
    model_name: str,
    trial_data_dir: str,
) -> float:
    """
    Objective function for Bayesian optimization using Optuna.

    Parameters
    ----------
    trial : optuna.trial.Tria
        Optuna trial object.
    eng : matlab.engine.MatlabEngine
        MATLAB engine instance.
    model_name : str
        Name of the Simulink model.
    trial_data_dir : str
        Path to the CSV file for storing results.
    Returns
    -------
        float: Loss value to minimize.
    """
    KC = trial.suggest_float("KC", 0.05, 0.5)
    KI = trial.suggest_float("KI", 0.005, 0.05)

    try:
        logging.info(
            f"Starting Objective for trial {trial.number}, using KC={KC:.4f}, KI={KI:.4f}"
        )
        # Time the simulation
        start_sim_time = time.time()  # Record start time for simulation
        df_simulation = run_simulation(eng, model_name, KC, KI, trial.number)
        end_sim_time = time.time()  # Record end time for simulation

        # Calculate and log simulation time in minutes and seconds
        sim_time_seconds = end_sim_time - start_sim_time
        sim_minutes, sim_seconds = divmod(sim_time_seconds, 60)
        logging.info(
            f"Simulation  for trial {trial.number} completed in {int(sim_minutes)} minutes and {sim_seconds:.2f} seconds"
        )

        # Time the loss computation
        start_loss_time = time.time()  # Record start time for loss computation
        loss = compute_loss(df_simulation)
        end_loss_time = time.time()  # Record end time for loss computation

        # Calculate and log loss computation time in seconds
        loss_time_seconds = end_loss_time - start_loss_time
        logging.info(
            f"Loss function for trial {trial.number} completed in {loss_time_seconds:.2f} seconds"
        )

        # Append results to the DataFrame
        new_row = pl.DataFrame(
            {"Trial": [trial.number], "KC": [KC], "KI": [KI], "Loss": [loss]}
        )
        results_df = pl.read_csv(
            f"{trial_data_dir}/optimization_history.csv",
            schema={
                "Trial": pl.Int64,
                "KC": pl.Float64,
                "KI": pl.Float64,
                "Loss": pl.Float64,
            },
        )
        logging.info(f"Results DataFrame: {results_df.head()}")
        logging.info(f"Results DataFrame: {new_row.head()}")
        results_df = pl.concat([results_df, new_row], how="vertical")

        # Save the DataFrame to CSV
        results_df.write_csv(f"{trial_data_dir}/optimization_history.csv")
        logging.info(
            f"Trial {trial.number}: KC={KC:.4f}, KI={KI:.4f}, Loss={loss:.6f}."
        )

        # Save individual simulation data
        simulation_filename = (
            f"{trial_data_dir}/KC-{KC:.4f}_KI-{KI:.4f}_trial-{trial.number}.csv"
        )
        df_simulation.write_csv(simulation_filename)

        return loss
    except Exception as e:
        logging.exception(f"Objective function failed at trial {trial.number}: {e}")
        return float("inf")


def run_optimization(
    eng: Any,
    model_name: str,
    n_trials: int = 50,
    data_dir: str = "data/",
    study_name: Optional[str] = None,
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
    data_dir: str, default='data/'
        Path to the CSV file for storing results.
    study_name : Optional[str], default=None
        Name of the Optuna study.

    Returns:
        Dict[str, Any]: Dictionary containing the best parameters and loss.
    """
    study = optuna.create_study(
        direction="minimize",
        study_name=study_name,
        storage=os.getenv("DATABASE_URL"),
        load_if_exists=True,
    )

    # Create and save empty results DataFrame
    results_df = pl.DataFrame(
        schema={
            "Trial": pl.Int64,
            "KC": pl.Float64,
            "KI": pl.Float64,
            "Loss": pl.Float64,
        }
    )
    results_df.write_csv(f"{data_dir}/{study_name}/optimization_history.csv")

    # Create the study
    logging.info("Starting optimization...")

    # Define the objective function wrapper
    def wrapped_objective(trial):
        return objective(trial, eng, model_name, f"{data_dir}/{study_name}")

    # Run the optimization
    study.optimize(wrapped_objective, n_trials=n_trials)
    logging.info("Optimization completed.")

    # Get the best parameters and loss
    best_params = study.best_params
    best_loss = study.best_value

    fig = optuna.visualization.plot_contour(study, params=["KC", "KI"])
    show(fig)
    write_html(fig, f"{data_dir}/{study_name}/contour_plot.html")

    return {"best_params": best_params, "best_loss": best_loss}
