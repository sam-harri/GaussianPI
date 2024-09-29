import logging
import os
import sys

import matplotlib.pyplot as plt

from matlab_interface import initialize_matlab_engine, run_simulation
from optimizer import run_optimization


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Initialize variables
    model_name = "Lab_1_Closed_Loop_v1"
    data_dir = "data/"

    # Ensure necessary directories exist
    os.makedirs("data/simulation_runs", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # Initialize MATLAB engine
    try:
        eng = initialize_matlab_engine(matlab_path="../matlab")
    except Exception as e:
        logging.error(f"Initialization error: {e}")
        sys.exit(1)

    # Run optimization
    optimization_result = run_optimization(
        eng, model_name, n_trials=50, results_csv_path=data_dir
    )

    best_params = optimization_result["best_params"]
    best_loss = optimization_result["best_loss"]
    logging.info(
        f"Best Parameters: KC={best_params['KC']:.4f}, KI={best_params['KI']:.4f}"
    )
    logging.info(f"Best Loss: {best_loss:.6f}")

    # Rerun simulation with best parameters
    try:
        logging.info("Running simulation with best parameters...")
        df_best = run_simulation(eng, model_name, best_params["KC"], best_params["KI"])

        # Save best simulation data
        filename = (
            f"data/best_KC-{best_params['KC']:.4f}_KI-{best_params['KI']:.4f}.csv"
        )
        df_best.write_csv(filename)
        logging.info(f"Best result data saved to '{filename}'.")

        # Plot results
        plt.figure()
        plt.plot(df_best["Time"], df_best["Actual"], label="Actual")
        plt.plot(df_best["Time"], df_best["Setpoint"], label="Setpoint")
        plt.xlabel("Time")
        plt.ylabel("Output")
        plt.title("PID Controller Response with Best Parameters")
        plt.legend()
        plt.show()
    except Exception as e:
        logging.error(f"Error during final simulation or plotting: {e}")


if __name__ == "__main__":
    main()
