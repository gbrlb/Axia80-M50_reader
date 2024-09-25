from writer import Writer
import time
import datetime as dt
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import NetFT


def update(frame):

    F = sensor.getForce()

    Fx = F[0] / 416666
    Fy = F[1] / 416666
    Fz = F[2] / 416666


    elapsed_time = time.time() - timeOffset
    print(f"{Fx}, {Fy}, {Fz}")
    Ft = np.sqrt(Fx**2 + Fy**2 + Fz**2)

    xs.append(elapsed_time)
    ys.append(Ft)
    fx_values.append(Fx)
    fy_values.append(Fy)
    fz_values.append(Fz)
    writer.update(xs, ys)
    tms.append(elapsed_time)
    F_N.append(Ft)

    sample_index = int(sample_time_min * 60 / 5)
    d_kgs = 0
    if len(F_N) > sample_index:
        m_i = F_N[-sample_index]
        m_f = F_N[-1]
        if m_i == 0:
            m_i = 0.00001
        d_kgs = (m_i - m_f) / m_i * 100

    print(f"t:{xs[-1]:.1f} s, m:{ys[-1]:.3f} g, dm:{d_kgs:.2f} %")

    ax.clear()

    ax.plot(xs, ys, label=f'F_t: {Ft:.3f} N')
    ax.plot(xs, fx_values, label=f'F_x: {Fx:.3f} N')
    ax.plot(xs, fy_values, label=f'F_y: {Fy:.3f} N')
    ax.plot(xs, fz_values, label=f'F_z: {Fz:.3f} N')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=4)


    ax.set_title('Force Components over Time')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Force [N]')

    return ax,

try:
    # Initialization
    sensor = NetFT.Sensor('192.168.1.1')
    timeOffset = time.time()
    sample_time_min = 15
    Path("output").mkdir(parents=True, exist_ok=True)
    timestamped = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    writer = Writer(f'output/recording-{timestamped}.csv')
    writer.run()

    xs = []
    ys = []
    fx_values = []
    fy_values = []
    fz_values = []
    tms = [0]
    F_N = [0.0]

    fig, ax = plt.subplots(figsize=(10, 8))
    animation = FuncAnimation(fig, update, interval=200, save_count=100)

    plt.show()

except Exception as e:
    print(f"Error: {e}")