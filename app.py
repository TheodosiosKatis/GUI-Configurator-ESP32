import customtkinter as ctk
from tkinter import filedialog, messagebox
import serial
import serial.tools.list_ports
import threading

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTGO T-Call ESP32 Configuration")
        self.root.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.port_var = ctk.StringVar()
        self.baud_rate = 115200
        self.serial_connection = None
        self.mqtt_tls_var = ctk.BooleanVar()
        self.show_password = False
        self.stop_event = threading.Event()  # Event to signal threads to stop

        self.create_widgets()

    def create_widgets(self):
        # Font settings
        label_font = ("Arial", 16)
        entry_font = ("Arial", 14)
        button_font = ("Arial", 14)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(main_frame, width=350)  # Increase width
        left_frame.pack(side="left", fill="y", expand=False, padx=20, pady=20)
        left_frame.pack_propagate(False)

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        right_frame.pack_propagate(False)

        # MQTT Parameters
        mqtt_frame = ctk.CTkFrame(left_frame)
        mqtt_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(mqtt_frame, text="MQTT Parameters", font=label_font).pack(pady=10)

        ctk.CTkLabel(mqtt_frame, text="Broker:", font=label_font).pack(pady=5)
        self.mqtt_broker_entry = ctk.CTkEntry(mqtt_frame, font=entry_font, width=300)  # Increase width
        self.mqtt_broker_entry.pack(pady=5)

        ctk.CTkLabel(mqtt_frame, text="Port:", font=label_font).pack(pady=5)
        self.mqtt_port_entry = ctk.CTkEntry(mqtt_frame, font=entry_font, width=300)  # Increase width
        self.mqtt_port_entry.pack(pady=5)

        self.mqtt_tls_check = ctk.CTkCheckBox(mqtt_frame, text="MQTT TLS", font=label_font, variable=self.mqtt_tls_var, command=self.toggle_tls)
        self.mqtt_tls_check.pack(pady=5)

        self.mqtt_ca_label = ctk.CTkLabel(mqtt_frame, text="CA Certificate Content:", font=label_font)  # Add CA certificate label
        self.mqtt_ca_label.pack(pady=5)
        self.mqtt_ca_label.pack_forget()  # Hide initially

        self.mqtt_ca_entry = ctk.CTkEntry(mqtt_frame, font=entry_font, width=300)  # Add CA certificate content field
        self.mqtt_ca_entry.pack(pady=5)
        self.mqtt_ca_entry.pack_forget()  # Hide initially

        ctk.CTkLabel(mqtt_frame, text="Publish Topic:", font=label_font).pack(pady=5)
        self.mqtt_topic_pub_entry = ctk.CTkEntry(mqtt_frame, font=entry_font, width=300)  # Increase width
        self.mqtt_topic_pub_entry.pack(pady=5)

        ctk.CTkLabel(mqtt_frame, text="Subscribe Topic:", font=label_font).pack(pady=5)
        self.mqtt_topic_sub_entry = ctk.CTkEntry(mqtt_frame, font=entry_font, width=300)  # Increase width
        self.mqtt_topic_sub_entry.pack(pady=5)

        ctk.CTkLabel(mqtt_frame, text="User:", font=label_font).pack(pady=5)
        self.mqtt_user_entry = ctk.CTkEntry(mqtt_frame, font=entry_font, width=300)  # Increase width
        self.mqtt_user_entry.pack(pady=5)

        ctk.CTkLabel(mqtt_frame, text="Password:", font=label_font).pack(pady=5)
        password_frame = ctk.CTkFrame(mqtt_frame)
        password_frame.pack(pady=5)
        self.mqtt_password_entry = ctk.CTkEntry(password_frame, show="*", font=entry_font, width=250)  # Increase width
        self.mqtt_password_entry.pack(side="left")
        self.toggle_password_button = ctk.CTkButton(password_frame, text="Show", font=button_font, command=self.toggle_password, width=50)
        self.toggle_password_button.pack(side="left")

        self.save_mqtt_button = ctk.CTkButton(mqtt_frame, text="Save", font=button_font, command=self.save_mqtt, width=300)  # Increase width
        self.save_mqtt_button.pack(pady=10)

        # WiFi Configuration
        wifi_frame = ctk.CTkFrame(right_frame)
        wifi_frame.pack(pady=10, padx=20, fill="x", expand=False)

        ctk.CTkLabel(wifi_frame, text="WiFi Configuration", font=label_font).pack(pady=10)

        ctk.CTkLabel(wifi_frame, text="SSID:", font=label_font).pack(pady=5)
        self.ssid_entry = ctk.CTkEntry(wifi_frame, font=entry_font, width=250)
        self.ssid_entry.pack(pady=5)

        ctk.CTkLabel(wifi_frame, text="Password:", font=label_font).pack(pady=5)
        wifi_password_frame = ctk.CTkFrame(wifi_frame)
        wifi_password_frame.pack(pady=5)
        self.password_entry = ctk.CTkEntry(wifi_password_frame, show="*", font=entry_font, width=200)
        self.password_entry.pack(side="left")
        self.toggle_wifi_password_button = ctk.CTkButton(wifi_password_frame, text="Show", font=button_font, command=self.toggle_wifi_password, width=50)
        self.toggle_wifi_password_button.pack(side="left")

        self.save_wifi_button = ctk.CTkButton(wifi_frame, text="Save", font=button_font, command=self.save_wifi, width=250)
        self.save_wifi_button.pack(pady=10)

        # Device Connection
        conn_frame = ctk.CTkFrame(right_frame)
        conn_frame.pack(pady=10, padx=20, fill="x", expand=False)

        ctk.CTkLabel(conn_frame, text="Device Connection", font=label_font).pack(pady=10)

        self.search_button = ctk.CTkButton(conn_frame, text="Search Devices", font=button_font, command=self.search_devices, width=250)
        self.search_button.pack(pady=5)

        ctk.CTkLabel(conn_frame, text="Select Port:", font=label_font).pack(pady=5)
        self.port_dropdown = ctk.CTkComboBox(conn_frame, variable=self.port_var, font=entry_font, width=250)
        self.port_dropdown.pack(pady=5)

        self.connect_button = ctk.CTkButton(conn_frame, text="Connect", font=button_font, command=self.connect_device, width=250)
        self.connect_button.pack(pady=5)

        self.disconnect_button = ctk.CTkButton(conn_frame, text="Disconnect", font=button_font, command=self.disconnect_device, width=250)
        self.disconnect_button.pack(pady=5)

        # Connection status indicator
        self.connection_status = ctk.CTkLabel(conn_frame, text="", width=20, height=20, corner_radius=10, fg_color="red")
        self.connection_status.pack(pady=5)

        # Serial monitor
        self.serial_monitor = ctk.CTkTextbox(right_frame, width=400, height=300)  # Increased height
        self.serial_monitor.pack(pady=10, padx=20, fill="both", expand=True)

    def toggle_tls(self):
        if self.mqtt_tls_var.get():
            self.mqtt_ca_label.pack(pady=5, after=self.mqtt_tls_check)
            self.mqtt_ca_entry.pack(pady=5, after=self.mqtt_ca_label)
        else:
            self.mqtt_ca_label.pack_forget()
            self.mqtt_ca_entry.pack_forget()

    def _on_mouse_wheel(self, event):
        self.root.children['!ctkframe'].children['!ctkcanvas'].yview_scroll(int(-1 * (event.delta / 120)), "units")

    def search_devices(self):
        ports = list(serial.tools.list_ports.comports())
        port_list = [port.device for port in ports]
        self.port_dropdown.configure(values=port_list)

        if port_list:
            self.port_dropdown.set(port_list[0])
        else:
            messagebox.showwarning("No Devices", "No devices found!")

    def connect_device(self):
        selected_port = self.port_var.get()
        if not selected_port:
            messagebox.showwarning("Select Port", "Please select a port!")
            return

        try:
            self.serial_connection = serial.Serial(selected_port, self.baud_rate)
            self.connection_status.configure(fg_color="green")
            self.stop_event.clear()  # Clear the stop event
            self.start_serial_monitor()
            messagebox.showinfo("Connected", f"Connected to {selected_port}")
        except Exception as e:
            self.connection_status.configure(fg_color="red")
            messagebox.showerror("Connection Error", str(e))

    def disconnect_device(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.stop_event.set()  # Signal threads to stop
            self.serial_connection.close()
            self.connection_status.configure(fg_color="red")
            messagebox.showinfo("Disconnected", "Device disconnected")
        else:
            messagebox.showwarning("Not Connected", "No device is connected")

    def save_mqtt(self):
        if self.serial_connection and self.serial_connection.is_open:
            broker = self.mqtt_broker_entry.get().strip()
            port = self.mqtt_port_entry.get().strip()
            mqtt_user = self.mqtt_user_entry.get().strip()
            mqtt_pass = self.mqtt_password_entry.get().strip()
            pub_topic = self.mqtt_topic_pub_entry.get().strip()
            sub_topic = self.mqtt_topic_sub_entry.get().strip()
            tls = 1 if self.mqtt_tls_var.get() else 0
            ca_content = self.mqtt_ca_entry.get().strip()

            self.serial_connection.write(f"BROKER:{broker}\n".encode())
            self.serial_connection.write(f"PORT:{port}\n".encode())
            self.serial_connection.write(f"MQTTUSER:{mqtt_user}\n".encode())
            self.serial_connection.write(f"MQTTPASS:{mqtt_pass}\n".encode())
            self.serial_connection.write(f"PUBTOPIC:{pub_topic}\n".encode())
            self.serial_connection.write(f"SUBTOPIC:{sub_topic}\n".encode())
            self.serial_connection.write(f"TLS:{tls}\n".encode())
            if tls:
                self.serial_connection.write(f"CA_CONTENT:{ca_content}\n".encode())

            messagebox.showinfo("Saved", "MQTT parameters saved to the device")
        else:
            messagebox.showerror("Not Connected", "Device is not connected")

    def save_wifi(self):
        if self.serial_connection and self.serial_connection.is_open:
            ssid = self.ssid_entry.get().strip()
            password = self.password_entry.get().strip()

            self.serial_connection.write(f"SSID:{ssid}\n".encode())
            self.serial_connection.write(f"PASSWORD:{password}\n".encode())

            messagebox.showinfo("Saved", "WiFi credentials are saved to the device")
            threading.Thread(target=self.check_wifi_status).start()
        else:
            messagebox.showerror("Not Connected", "Device is not connected")

    def check_wifi_status(self):
        try:
            self.serial_connection.timeout = 30  # Set timeout for reading response
            response = self.serial_connection.read_until(b'\n').decode().strip()
            if response == "WIFI_CONNECTED":
                messagebox.showinfo("WiFi Connection", "Successfully connected to WiFi")
            elif response == "WIFI_CONNECTION_FAILED":
                messagebox.showerror("WiFi Connection", "Failed to connect to WiFi")
            else:
                print(f"Unknown response from device: {response}")
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Error reading from serial: {str(e)}")

    def start_serial_monitor(self):
        threading.Thread(target=self.update_serial_monitor, daemon=True).start()

    '''
    def update_serial_monitor(self):
        try:
            while self.serial_connection and self.serial_connection.is_open:
                if self.stop_event.is_set():  # Check for stop event
                    break
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    self.serial_monitor.insert("end", line + "\n")
                    self.serial_monitor.see("end")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    '''        
    def update_serial_monitor(self):
        try:
            skip_lines = 0  # Counter for lines to skip

            while self.serial_connection and self.serial_connection.is_open:
                if self.stop_event.is_set():  # Check for stop event
                    break
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()

                    if skip_lines > 0:  # If we are skipping lines
                        skip_lines -= 1
                        continue

                    if line.startswith("ets"):
                        skip_lines = 9  # Skip this line and the next 8 lines
                        continue

                    self.serial_monitor.insert("end", line + "\n")
                    self.serial_monitor.see("end")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    

    def toggle_password(self):
        if self.show_password:
            self.mqtt_password_entry.configure(show="*")
            self.toggle_password_button.configure(text="Show")
        else:
            self.mqtt_password_entry.configure(show="")
            self.toggle_password_button.configure(text="Hide")
        self.show_password = not self.show_password

    def toggle_wifi_password(self):
        if self.show_password:
            self.password_entry.configure(show="*")
            self.toggle_wifi_password_button.configure(text="Show")
        else:
            self.password_entry.configure(show="")
            self.toggle_wifi_password_button.configure(text="Hide")
        self.show_password = not self.show_password

    def on_closing(self):
        self.stop_event.set()  # Signal threads to stop
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SerialApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()