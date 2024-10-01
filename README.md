# PI Controller Optimization Using Bayesian Optimization

## Overview

This project implements a **PI (Proportional-Integral) Controller** optimization framework using **Bayesian Optimization**. The key goal is to automatically tune the PI controller parameters \( K_C \) and \( K_I \) for a given simulation model, minimizing the control error in closed-loop simulations. The optimization is performed using the **Optuna** library for Bayesian optimization, interfacing with **MATLAB** simulations via Python's `matlab.engine`. 

The framework simulates a variety of bump tests, noise, and perturbations to accurately evaluate the controller's performance. The objective function is based on the integral of the absolute difference between the setpoint and the actual response, calculated as:

$$
\text{Objective Function} = \int |Y_{\text{setpoint}}(t) - Y_{\text{actual}}(t)| \, dt
$$

This minimizes the overall error over time, ensuring the best possible PI tuning for robust and efficient control.

---

## Parameter Configuration

The model parameters and experiment settings can be adjusted by modifying the following values in `main.py`:

```python
def main():
    # Initialize variables
    model_name = "Lab_1_Closed_Loop_v1"
    study_name = "tank1_pi_overnight"
    
    # create data_dir/study_name directory if it does not exist
    if not os.path.exists(f"data/{study_name}"):
        os.makedirs(f"data/{study_name}")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname).1s %(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"data/{study_name}/logfile.log"),
        ],
    )
```
Here:

`model_name` refers to the MATLAB model used for the simulation.  
`study_name` refers to the name of the specific experiment or study being conducted, used for data organization.

### Multi Node Training

1. **Database Connection String

A database is required to store and share optimization results across multiple nodes. You need to provide the connection string in a `.env` file located at the root of the `bayesian_backend` directory. The environment variable should be named `DATABASE_URL`

Example `.env` file:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

2. **Storage Configuration**

Ensure that the `storage` argument in `optuna.create_study()` is set correctly in the optimization function, which loads the database connection string from the environment variable. Additionally, the `load_if_exists` argument must be set to True to continue an existing study or create a new one if it doesn't exist. These can be found in the `run_optimization` function of `src/optimizer.py`

```python
def run_optimization(
    eng: Any,
    model_name: str,
    n_trials: int = 50,
    data_dir: str = "data/",
    study_name: Optional[str] = None,
) -> Dict[str, Any]:
    
    study = optuna.create_study(
        direction="minimize",
        study_name=study_name,
        storage=os.getenv("DATABASE_URL"),  # Load database URL from .env
        load_if_exists=True,  # Continue from existing study if available
    )
```

### Modifying the Search Space

To adjust the search space for the PI controller parameters, update the ranges in the `objective` function within `src/optimizers.py`:

```python
def objective(
    trial: optuna.trial.Trial,
    eng: Any,
    model_name: str,
    trial_data_dir: str,
) -> float:
    
    KC = trial.suggest_float("KC", 0.05, 0.5)  # Proportional Gain
    KI = trial.suggest_float("KI", 0.003, 0.05)  # Integral Gain
```

Adjust the upper and lower bounds of KC and KI as needed to explore different control parameter ranges.

## Simulation
The simulation is divided into two key models:

1. **Closed-Loop Simulation**: Control loop containing the physical process, the setpoint signal, and backpropagated error
![Closed Loop Simulink Model](docs/simulink_main.png)

2. **Physical Simulator**: The physical system simulation
![Physical Process Simulink Model](docs/simulink_process.png)

During each optimization trial, the PI controller is subjected to a series of bump tests, noise injections, and perturbations to simulate real-world disturbances.

## Results
Each run stores the results in the `data/{study_name}/` directory:

- **Per-Trial Data**: The data for each trial is stored in CSV files, named according to the controller parameters for that run:

```bash
data/{study_name}/KC-{KC_value}_KI-{KI_value}_trial-{trial_num}.csv
```

- **Optimization History**: A comprehensive history of all optimization trials is stored at:
```bash
data/{study_name}/optimization_history.csv
```

- **Logs**: Logs detailing each simulation and optimization step are stored at:
```bash
data/{study_name}/logfile.log
```
- **Contour Plot**: A contour plot representing the objective function's response to the PI parameters is generated in HTML format:
```bash
data/{study_name}/contour_plot.html
```
![Objective Function Contour Plot](docs/contour.png)

## Running the Project
Follow the steps below to set up and run the project:
1. **Navigate to the Python section:**
```bash
cd bayesian_backend
```

2. **Create a virtual environment:**

Ensure UV is installed, if not run `pip install uv`

```bash
uv venv
```

3. **Activate the Virtual Environment**
```bash
source .venv/bin/activate
```

3. **Run the optimization script**
```bash
uv run src/main.py
```