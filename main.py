from writer import Writer
import time
import datetime as dt
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import numpy as np
import NetFT

record = False
timeOffset = time.time()

def update(frame):

    F = sensor.getForce()

    Fx = F[0] / 416666
    Fy = F[1] / 416666
    Fz = F[2] / 416666

    elapsed_time = time.time() - timeOffset
    print(f"{Fx}, {Fy}, {Fz}")
    Ft = np.sqrt(Fx**2 + Fy**2 + Fz**2)

    fx_values.append(Fx)
    fy_values.append(Fy)
    fz_values.append(Fz)
    xs.append(elapsed_time)
    ys.append([Ft, Fx, Fy, Fz])

    if record:
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

    print(f"t:{xs[-1]:.1f} s, m:{ys[-1]:.3f} g, dm:{d_kgs:.2f} %, recording: {record}")

    ax.clear()

    ax.plot(xs, ys, label=f'F_t: {Ft:.3f} N')
    ax.plot(xs, fx_values, label=f'F_x: {Fx:.3f} N')
    ax.plot(xs, fy_values, label=f'F_y: {Fy:.3f} N')
    ax.plot(xs, fz_values, label=f'F_z: {Fz:.3f} N')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=4)


    ax.set_title('Force Components over Time')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Force [N]')

    return ax,

def start_recording(event):
    global record, timeOffset, xs, ys, fx_values, fy_values, fz_values, tms, F_N
    xs = []
    ys = []
    fx_values = []
    fy_values = []
    fz_values = []

    print("Start Recording button clicked.")
    timeOffset = time.time()
    record = True
    print(record, timeOffset)

def stop_recording(event):
    global record
    print("Stop Recording button clicked.")
    record = False
    print(record)

def tare(event):
    global sensor
    sensor.tare()

    print("Tare completed.")
    

try:
    # Initialization
    sensor = NetFT.Sensor('192.168.1.1')
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

    plt.subplots_adjust(right=0.75)

    # Add buttons on the right side
    ax_button_start = plt.axes([0.87, 0.8, 0.1, 0.075])
    btn_start = Button(ax_button_start, 'StartRec')
    btn_start.on_clicked(start_recording)

    ax_button_stop = plt.axes([0.87, 0.7, 0.1, 0.075])
    btn_stop = Button(ax_button_stop, 'StopRec')
    btn_stop.on_clicked(stop_recording)

    ax_button_tare = plt.axes([0.87, 0.6, 0.1, 0.075])
    btn_tare = Button(ax_button_tare, 'Tare')
    btn_tare.on_clicked(tare)

    plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=.12, left=.1, right=0.85)
    plt.show()


except Exception as e:
    print(f"Error: {e}")

