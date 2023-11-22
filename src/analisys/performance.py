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

# no es necesario, pero es una buena practica
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
data['KgF'] = data['KgF']
# data['ADC'] = data['ADC'].astype(int)
data['PSI'] = (data['ADC'] * 2000) / 1023
data['ATM'] = data['PSI'] * 0.068046

data['Delta'] = data['Delta'].round(4)
data['F'] = data['F'].round(2)
data['PSI'] = data['PSI'].round(2)
data['ATM'] = data['ATM'].round(4)

# print(data.head())

def get_ignition_index(col_name):
    ignition_index = None
    # Variable para mantener el recuento de incrementos consecutivos
    counter = 0
    # Booleano para registrar si se permitió una excepción
    exception_happen = False
    for index, row in data.iterrows():
        if index > 0:
            # Verifica si el valor actual es mayor que el anterior
            if row[col_name] > data.loc[index - 1, col_name]:
                counter += 1
            else:
                # Reinicia el counter si no hay un incremento
                counter = 0

            # Si hay cinco incrementos consecutivos, almacena la fila
            if counter == 4:
                ignition_index = index - 6
                break  # Puedes eliminar esto si quieres encontrar todos los casos
            elif counter == 3:
                # Si hay tres incrementos, permite una excepción
                exception_happen = True

            # Si el siguiente valor no es mayor pero se permitió una excepción
            # cuenta esto como un incremento adicional y reinicia el counter
            if exception_happen and counter == 2:
                counter = 0
                exception_happen = False
    return ignition_index

def get_burnout_index(col_name, threeshold, start_index):
    # print("Start index", start_index)
    for index, row in data.iloc[start_index:].iterrows():
        if row[col_name] < threeshold:
            return index -1

def classify_motor(thrust):
    if thrust <= 1.25:
        return 'A'
    elif thrust <= 2.5:
        return 'B'
    elif thrust <= 5.0:
        return 'C'
    elif thrust <= 10.0:
        return 'D'
    elif thrust <= 20.0:
        return 'E'
    elif thrust <= 40.0:
        return 'F'
    elif thrust <= 80.0:
        return 'G'
    elif thrust <= 160.0:
        return 'H'
    elif thrust <= 320.0:
        return 'I'
    elif thrust <= 640.0:
        return 'J'
    elif thrust <= 1280.0:
        return 'K'
    elif thrust <= 2560.0:
        return 'L'
    elif thrust <= 5120.0:
        return 'M'
    elif thrust <= 10240.0:
        return 'N'
    else:
        return 'O'

ignition_index = get_ignition_index('ADC')
burnout_index = get_burnout_index('F', 0, data['F'].idxmax())
average_time_interval = data['Delta'].mean()
burn_time = data.loc[burnout_index]['Ms'] - data.loc[ignition_index]['Ms']
total_thrust =  data.iloc[ignition_index:burnout_index + 1]['KgF'].sum() * 9.8
total_impulse = total_thrust * average_time_interval
specific_impulse = (total_impulse / 0.015) / 9.8
peak_pressure = data['ATM'].max()
peak_thrust = data['KgF'].max()


print('Engine ignition at:', data.loc[ignition_index]['Ms'], 's')
print('Engine shutdown at:', data.loc[burnout_index]['Ms'], 's')
print('Peak Pressure:', peak_pressure.round(3), 'atm')
print('Peak Thrust:', peak_pressure.round(3), 'KgF')
print('Burn time:', peak_thrust.round(3), 's')
print('Average interval:', (average_time_interval * 1000).round(2), 'ms')
print('Thrust:', total_thrust, 'N')
print('Total impulse:', total_impulse.round(2), 'N*s')
print('Specific impulse:', specific_impulse.round(2), 'N*s')
print('Motor Classification:', classify_motor(total_impulse))

# new_file = file_folder + name_without_extension + '_Calcs.csv'

# # Guardando el DataFrame en un nuevo archivo CSV
# data.to_csv(new_file, sep='\t', index=False) 

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
# Graficar Fuerza_1
ax1.plot(data['Ms'].iloc[ignition_index:burnout_index], data['F'].iloc[ignition_index:burnout_index], marker='o', linestyle='-', color='blue')
ax1.set_xlabel('Time')
ax1.set_ylabel('KgF')
ax1.set_title('Force vs Time')
ax1.grid(True)

ax2.plot(data['Ms'].iloc[ignition_index:burnout_index], data['ATM'].iloc[ignition_index:burnout_index], marker='o', linestyle='-', color='blue')
ax2.set_xlabel('Time')
ax2.set_ylabel('ATM')
ax2.set_title('Pressure vs Time')
ax2.grid(True)

plt.tight_layout()

# Nombre del archivo PDF
pdf_file = "graficos.pdf"
pdf_file = file_folder + name_without_extension + '_PERFORMANCE.pdf'

info_text = (
    f'Engine ignition at: {data.loc[ignition_index]["Ms"]} s\n'
    f'Engine shutdown at: {data.loc[burnout_index]["Ms"]} s\n'
    f'Peak Pressure: {peak_pressure.round(3)} atm\n'
    f'Peak Thrust:: {peak_thrust.round(3)} KgF\n'
    f'Burn time: {burn_time.round(3)} s\n'
    f'Average interval: {(average_time_interval * 1000).round(2)} ms\n'
    f'Thrust: {total_thrust} N\n'
    f'Total impulse: {total_impulse.round(2)} N*s\n'
    f'Specific impulse: {specific_impulse.round(2)} N*s\n'
    f'Motor Classification: {classify_motor(total_impulse)}'
)

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
pdf.drawImage("temp_image.png", 50, 50, width=400, height=400)

# Close the PDF
pdf.save()

plt.close(fig)  # Close the Matplotlib figure to prevent display in notebook

if os.path.exists("./temp_image.png"):
    os.remove("./temp_image.png")