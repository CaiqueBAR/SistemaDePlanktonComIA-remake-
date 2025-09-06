import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys

class FlaskAppRunner:
    def __init__(self, master):
        self.master = master
        master.title("Flask Server Controller")

        self.status_label = tk.Label(master, text="Servidor parado", fg="red")
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(master, text="Iniciar servidor Flask", command=self.start_server)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Parar servidor Flask", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.process = None

    def start_server(self):
        if self.process is None:
            # Ajuste aqui o caminho para seu arquivo Flask principal
            flask_script_path = os.path.abspath("flask_server.py")  # coloque o nome do seu script com o Flask aqui

            if not os.path.exists(flask_script_path):
                messagebox.showerror("Erro", f"Arquivo {flask_script_path} não encontrado!")
                return

            # Executa o script Flask num processo separado
            self.process = subprocess.Popen([sys.executable, flask_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.status_label.config(text="Servidor rodando na porta 5000", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Opcional: mostrar log do Flask no terminal da interface (de forma simples)
            threading.Thread(target=self.read_output, daemon=True).start()

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.status_label.config(text="Servidor parado", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def read_output(self):
        if not self.process:
            return
        for line in self.process.stdout:
            print(line.decode(), end='')  # printa log do Flask no console

root = tk.Tk()
app = FlaskAppRunner(root)
root.mainloop()

