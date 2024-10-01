import matplotlib.pyplot as plt
import polars as pl

trial0_df = pl.read_csv("data/FirstTankPI_Run3/KC-0.3889_KI-0.0186_trial-0.csv")
trial1_df = pl.read_csv("data/FirstTankPI_Run3/KC-0.1579_KI-0.0495_trial-1.csv")
trial2_df = pl.read_csv("data/FirstTankPI_Run3/KC-0.1001_KI-0.0454_trial-2.csv")

plt.figure(figsize=(12, 6))
plt.plot(trial2_df["Time"], trial1_df["Actual"], label="Trial 2")
plt.plot(trial1_df["Time"], trial1_df["Actual"], label="Trial 1")
plt.plot(trial0_df["Time"], trial0_df["Actual"], label="Trial 0")
plt.plot(trial0_df["Time"], trial0_df["Setpoint"], label="Trial 0")
plt.xlabel("Time (s)")
plt.ylabel("Actual")
plt.legend()
plt.show()
