import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

file_name = 'STATIC_1.csv'
file_folder = '../test_data/'
file_path = file_folder + file_name  # Replace 'path_to_your_file.csv' with your file path
name_without_extension = file_name.split('.')[0]

PSI_TO_ATM = 0.068046
FUEL_MASS = user_input = float(input("Please enter engine fuel mass in kg: "))

column_names = ['Ms', 'Status', 'F', 'ADC']
data = pd.read_csv(file_path, sep="\t", header=0, names=column_names)

# use first column as cero time
data['Ms'] -= data.loc[0, 'Ms']
# convert to seconds
data['Ms'] = data['Ms'] / 1000
# create a column for delta time
data['Delta'] = data['Ms'].diff().fillna(0)

# create a column converting g t kg
data['KgF'] = data['F'] / 1000
data['N'] = data['KgF'] * 9.8
# data['ADC'] = data['ADC'].astype(int)
data['PSI'] = (data['ADC'] * 2000) / 1023
data['ATM'] = data['PSI'] * PSI_TO_ATM

data['Delta'] = data['Delta'].round(4)
data['F'] = data['F'].round(2)
data['PSI'] = data['PSI'].round(2)
data['ATM'] = data['ATM'].round(4)

def get_ignition_index(col_name):
    ignition_index = None
    counter = 0
    exception_happen = False
    for index, row in data.iterrows():
        if index > 0:
            if row[col_name] > data.loc[index - 1, col_name]:
                counter += 1
            else:
                counter = 0

            if counter == 4:
                ignition_index = index - 6
                break
            elif counter == 3:
                exception_happen = True

            if exception_happen and counter == 2:
                counter = 0
                exception_happen = False
    return ignition_index

def get_burnout_index(col_name, threeshold, start_index):
    for index, row in data.iloc[start_index:].iterrows():
        if row[col_name] < threeshold:
            return index -1

def classify_motor(thrust):
    if thrust <= 2.5:
        return 'A'
    elif thrust <= 5.0:
        return 'B'
    elif thrust <= 10.0:
        return 'C'
    elif thrust <= 20.0:
        return 'D'
    elif thrust <= 40.0:
        return 'E'
    elif thrust <= 80.0:
        return 'F'
    elif thrust <= 160.0:
        return 'G'
    elif thrust <= 320.0:
        return 'H'
    elif thrust <= 640.0:
        return 'I'
    elif thrust <= 1280.0:
        return 'J'
    elif thrust <= 2560.0:
        return 'K'
    elif thrust <= 5120.0:
        return 'L'
    elif thrust <= 10240.0:
        return 'M'
    elif thrust <= 20480.0:
        return 'N'
    else:
        return 'O'

ignition_index = get_ignition_index('ADC')
burnout_index = get_burnout_index('F', 0, data['F'].idxmax())
average_time_interval = data['Delta'].mean()
burn_time = data.loc[burnout_index]['Ms'] - data.loc[ignition_index]['Ms']
total_thrust =  data.iloc[ignition_index:burnout_index + 1]['N'].sum()
total_impulse = total_thrust * average_time_interval
specific_impulse = (total_impulse / FUEL_MASS) / 9.8
peak_pressure = data['ATM'].max()
peak_thrust = data['N'].max()
average_pressure = data['ATM'].iloc[ignition_index: burnout_index + 1].mean()
max_pressure_increase = data['ATM'].iloc[ignition_index: burnout_index + 1].diff().max()
max_pressure_drop = data['Ms'].iloc[ignition_index: burnout_index + 1].diff().min()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
# Force
ax1.plot(data['Ms'].iloc[ignition_index:burnout_index], data['N'].iloc[ignition_index:burnout_index], marker='o', linestyle='-', color='blue')
ax1.set_xlabel('Time')
ax1.set_ylabel('N')
ax1.set_title('Force vs Time')
ax1.grid(True)

# Pressure
ax2.plot(data['Ms'].iloc[ignition_index:burnout_index], data['ATM'].iloc[ignition_index:burnout_index], marker='o', linestyle='-', color='blue')
ax2.set_xlabel('Time')
ax2.set_ylabel('ATM')
ax2.set_title('Pressure vs Time')
ax2.grid(True)

plt.tight_layout()

# PDF file name
pdf_file = "graficos.pdf"
pdf_file = file_folder + name_without_extension + '_PERFORMANCE.pdf'

info_text = (
    f'Propellant Mass: {0.015} kg\n'
    f'Engine ignition at: {data.loc[ignition_index]["Ms"]} s\n'
    f'Engine shutdown at: {data.loc[burnout_index]["Ms"]} s\n'
    f'Burn time: {burn_time.round(3)} s\n'
    f'Average interval: {(average_time_interval * 1000).round(2)} ms\n'
    f'Peak Pressure: {peak_pressure.round(3)} atm - {(peak_pressure / PSI_TO_ATM).round(3) } psi\n'
    f'Average Pressure: {average_pressure.round(3)} atm - {(average_pressure / PSI_TO_ATM ).round(3)} psi\n'
    f'Max Pressure increment: {max_pressure_increase.round(3)} atm - {(max_pressure_increase / PSI_TO_ATM ).round(3)} psi\n'
    f'Max Pressure drop: {max_pressure_drop.round(3)} atm - {(max_pressure_drop / PSI_TO_ATM ).round(3)} psi\n'
    f'Thrust: {total_thrust} N\n'
    f'Peak Thrust:: {peak_thrust.round(3)} N\n'
    f'Total impulse: {total_impulse.round(2)} Ns\n'
    f'Specific impulse: {specific_impulse.round(2)} s\n'
    f'Motor Classification: {classify_motor(total_impulse)}'
)

print(info_text)

if os.path.exists(pdf_file):
    os.remove(pdf_file)

pdf = canvas.Canvas(pdf_file, pagesize=A4)

# Set up title font and style
pdf.setFont("Helvetica-Bold", 16)
text = "Rocket Engine Analysis"
text_width = pdf.stringWidth(info_text)

# Center the title on the page
pdf.drawCentredString(A4[0] / 2, A4[1] - 50, text)

# Add the information text
pdf.setFont("Helvetica", 12)
text_object = pdf.beginText(50, A4[1] - 100)
text_object.setTextOrigin(50, A4[1] - 100)
text_object.setFont("Helvetica", 12)

for line in info_text.split('\n'):
    text_object.textLine(line)

pdf.drawText(text_object)

# Save Matplotlib figure to a file and add it to the PDF
fig.savefig("temp_image.png", bbox_inches="tight")
pdf.drawImage("temp_image.png", 50, 50, width=480, height=480)

pdf.save()

plt.close(fig)

if os.path.exists("./temp_image.png"):
    os.remove("./temp_image.png")
