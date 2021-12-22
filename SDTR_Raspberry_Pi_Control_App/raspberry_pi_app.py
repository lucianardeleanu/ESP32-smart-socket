# Imports 
import os
import can
from tkinter import *
from threading import Thread

# ============== GLOBAL VARIABLES INITIALISATION =============
received_voltage = ""
received_current = ""
received_power = ""
received_humidity = 0

#=============== CAN DRIVER INITIALISATION ===================
# Initialise CAN driver 
os.system("sudo ip link set can0 up type can bitrate 250000")

# Initialise bus inteface
bus=can.interface.Bus(channel='can0', bustype='socketcan_native')
#=============================================================

#=============== WINDOW INITIALISATION =======================

# Init a window object
window = Tk()

# Give to our window a nice title
window.title("Testare Proiect SDTR")

# Set window size
window.geometry("800x600")

# ============================================================

# ----------------- CAN MESSAGES DEFINITION ------------------
priza_on_msg = can.Message(arbitration_id=0x01, data=[1, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
priza_off_msg = can.Message(arbitration_id=0x01, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)

# ------------------------------------------------------------


# ---- Define welcome labels -----
welcome_label = Label(window, font=("Arial Bold", 16), text="Bine ati venit in aplicatia de configurare a prizei inteligente!")
welcome_label.place(relx=0.5, rely=0.05, anchor='center')

author_label = Label(window, font=("Arial", 12), text="Ardeleanu Lucian, Universitatea Transilvania, Brasov")
author_label.place(relx=0.5, rely=0.12, anchor='center')


# ---- Define window buttons ----
first_button = Button(window, font=("Arial", 20), text="Porneste Priza", command=lambda: bus.send(priza_on_msg))
first_button.place(relx=0.20, rely=0.22, anchor='center')

second_button = Button(window, font=("Arial", 20), text="Opreste Priza", command=lambda: bus.send(priza_off_msg))
second_button.place(relx=0.80, rely=0.22, anchor='center')

def extern_loop_function():
    
    global received_voltage
    
    try: 
        # Receive a message from bus 
        received_message = bus.recv(None)
        
        # Conver received message in bytes 
        list_of_bytes = list(received_message.data)
        
        # if a message has been arrived
        if received_message.arbitration_id == 0x01:
            
            # print it on screen 
            received_voltage = str(list_of_bytes[-2]) + "." + str(list_of_bytes[-1])
            
            # Show label on screen 
            voltage_label = Label(window, font=("Arial", 14), text="   " + "Tensiunea Prizei: " + received_voltage + "      ")
            voltage_label.place(relx=0.20, rely=0.33, anchor='center')

                
        # if a message has been arrived
        if received_message.arbitration_id == 0x02:
            
            # print it on screen 
            received_current = str(list_of_bytes[-2]) + "." + str(list_of_bytes[-1])
            
            # Show label on screen 
            label_current = Label(window, font=("Arial", 14), text= "   " + "Curentul prin priza: " + received_current + "      ")
            label_current.place(relx=0.20, rely=0.40, anchor='center')
            
        # if a message has been arrived
        if received_message.arbitration_id == 0x03:
            
            # print it on screen 
            received_power = str(list_of_bytes[-2]) + "." + str(list_of_bytes[-1])
            
            # Show label on screen 
            label_power = Label(window, font=("Arial", 14), text= "   " + "Puterea Activa: " + received_power + "      ")
            label_power.place(relx=0.20, rely=0.47, anchor='center')
            
        # if a message has been arrived
        if received_message.arbitration_id == 0x04:
            
            # print it on screen 
            received_humid = str(list_of_bytes[-1])
              
            # Show label on screen 
            humid_label = Label(window, font=("Arial", 14), text= "   " + "Umiditatea: " + received_humid + "      ")
            humid_label.place(relx=0.20, rely=0.54, anchor='center')
                

                
    except:
        pass
    else:
        pass
    
        
    window.after(50, lambda: extern_loop_function())


if __name__ == "__main__":
    
    window.after(50, lambda: extern_loop_function())
    window.mainloop()
    
    

        

    
    
    
    

    

