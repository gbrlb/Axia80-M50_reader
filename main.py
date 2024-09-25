from writer import Writer
import time
import datetime as dt
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import socket
import struct
import numpy as np

# Constants for the commands
COMMAND_STOP = 0x0000
COMMAND_START_REALTIME = 0x0002
COMMAND_START_BUFFERED = 0x0003
COMMAND_RESET_LATCH = 0x0041
COMMAND_SET_BIAS = 0x0042

# RDT command header
COMMAND_HEADER = 0x1234

# ATI NET-FT
ATI_ADDRESS = ('192.168.1.1', 49152)

# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(ATI_ADDRESS)
print('Socket opened')

sample_time_min = 15

def send_rdt_command(command):
    rdt_request = struct.pack('!HHI', COMMAND_HEADER, command, 2)  # Sample count set to 0
    sock.send(rdt_request)
    # print(f"Sent RDT command: {command:#04x}")


def update(frame):
    send_rdt_command(2)
    rawdata = sock.recv(1024)
    data = struct.unpack('!IIIiiiiii', rawdata)[3:]
    data = [data[i] - mean[i] for i in range(6)]

    Fx = data[0] / 416666
    Fy = data[1] / 416666
    Fz = data[2] / 416666
    Tx = data[3] / 416666
    Ty = data[4] / 416666
    Tz = data[5] / 416666

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

    ax.plot(xs, ys, label='F_t')
    ax.plot(xs, fx_values, label='F_x')
    ax.plot(xs, fy_values, label='F_y')
    ax.plot(xs, fz_values, label='F_z')

    ax.set_title('Force Components over Time')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Force [N]')
    ax.legend()

    # send_rdt_command(COMMAND_STOP)
    return ax,

try:
    # Initialization
    timeOffset = time.time()
    mean = [0] * 6
    # send_rdt_command(COMMAND_SET_BIAS)
    # send_rdt_command(COMMAND_START_REALTIME)

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

    plt.title("Force Components over Time")

    animation = FuncAnimation(fig, update, interval=200, save_count=100)
    plt.show()

except Exception as e:
    print(f"Error: {e}")
    send_rdt_command(COMMAND_STOP)