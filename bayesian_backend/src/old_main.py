from typing import Any, Dict
import matlab.engine
from matlab.engine import MatlabEngine
import polars as pl
import matplotlib.pyplot as plt
import numpy as np


def run_simulink_model(KC, KI):
    # Start MATLAB engine
    eng: MatlabEngine = matlab.engine.start_matlab()

    # Change MATLAB's current directory to the folder containing the .slx file
    eng.cd("../matlab")

    # Load your Simulink model (replace 'your_model_name' with the actual name of your .slx file without the extension)
    eng.load_system("Lab_1_Closed_Loop_v1")

    eng.workspace["KC"] = KC
    eng.workspace["KI"] = KI

    eng.eval("out=sim('Lab_1_Closed_Loop_v1')", nargout=0)
    eng.eval("data = struct(out)", nargout=0)
    data: Dict[Any] = eng.workspace["data"]

    # Flatten the arrays
    actual_data = np.array(data["Data"]["ActualSimOut"]).flatten()
    setpoint_data = np.array(data["Data"]["SetpointSimOut"]).flatten()
    time_data = np.array(data["Data"]["tout"]).flatten()

    # Find the minimum length of the three arrays
    min_length = min(len(actual_data), len(setpoint_data), len(time_data))

    # Trim all arrays to the minimum length
    actual_data = actual_data[:min_length]
    setpoint_data = setpoint_data[:min_length]
    time_data = time_data[:min_length]

    print(f"Time : {len(time_data)}")
    print(f"Setpoint : {len(setpoint_data)}")
    print(f"Actual : {len(actual_data)}")
    df = pl.DataFrame(
        {"Time": time_data, "Actual": actual_data, "Setpoint": setpoint_data}
    )

    df.write_csv(f"data/KC-{KC}_KI-{KI}.csv")

    plt.plot(time_data, actual_data)
    plt.plot(time_data, setpoint_data)
    plt.show()

    # # Close the Simulink model without saving changes
    # eng.close_system('Lab_1_Closed_Loop_v1', 0)

    # # Stop MATLAB engine
    # eng.quit()

    # # Return the outputs
    # return output_data1, output_data2


if __name__ == "__main__":
    KC = 0.3  # Set your KC value
    KI = 0.005  # Set your KI value

    # Run the model and retrieve outputs
    run_simulink_model(KC, KI)

    # Now you can work with output_data1 and output_data2 in Python
    # print("Output 1:", output_data1)
    # print("Output 2:", output_data2)

    # optimize_pid(n_trials=50) #/mnt/c/Program Files/MATLAB/R2024b/bin/glnxa64
    # export LD_LIBRARY_PATH='/mnt/c/Program Files/MATLAB/R2024b/bin/glnxa64'
    # echo $LD_LIBRARY_PATH

    # export PATH=$HOME/AppData/Roaming/Python/Python312/Scripts:$PATH
