import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter import scrolledtext
import subprocess
import threading
import os
import sys
import requests
import json
import base64
from PIL import Image, ImageTk
import io
import time
import platform
from functools import partial

class PlanktonAIApp:
    def __init__(self, master):
        self.master = master
        master.title("Sistema de Reconhecimento de Plâncton com IA")
        master.geometry("900x700")
        master.configure(bg='#f0f0f0')
        
        # Variáveis
        self.process = None
        self.server_url = "http://localhost:5000"
        self.current_image_path = None
        self.current_image = None
        self.tooltips = {}
        self.model_info = None
        self.last_prediction_time = None
        
        # Configuração do estilo
        self.setup_styles()
        
        # Criação da interface
        self.create_widgets()
        
        # Verifica se o servidor já está rodando
        self.check_server_status()
    
    def setup_styles(self):
        """Configura os estilos da interface."""
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'light': '#ecf0f0',
            'dark': '#34495e',
            'info': '#00bcd4'
        }
        
        # Configuração do estilo para ttk widgets
        style = ttk.Style()
        style.configure("TProgressbar", thickness=10, troughcolor='#f0f0f0', 
                       background=self.colors['secondary'])
    
    def create_widgets(self):
        """Cria todos os widgets da interface."""
        # Frame principal
        main_frame = tk.Frame(self.master, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="🦠 Sistema de Reconhecimento de Plâncton com IA",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Frame do servidor
        self.create_server_frame(main_frame)
        
        # Frame da IA
        self.create_ai_frame(main_frame)
        
        # Frame de logs
        self.create_log_frame(main_frame)
        
        # Frame de informações do modelo
        self.create_model_info_frame(main_frame)
        
        # Barra de status
        self.create_status_bar(self.master)
    
    def create_server_frame(self, parent):
        """Cria o frame de controle do servidor."""
        server_frame = tk.LabelFrame(
            parent, 
            text="Controle do Servidor Flask",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary'],
            padx=10,
            pady=10
        )
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status do servidor
        status_frame = tk.Frame(server_frame, bg='#f0f0f0')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            status_frame, 
            text="Status:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            status_frame, 
            text="Servidor parado",
            fg=self.colors['danger'],
            bg='#f0f0f0',
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Indicador de atividade
        self.activity_indicator = tk.Label(
            status_frame,
            text="⚪",  # Círculo vazio
            font=('Arial', 10),
            bg='#f0f0f0'
        )
        self.activity_indicator.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.activity_indicator, "Indicador de atividade do servidor")
        
        # Botões do servidor
        button_frame = tk.Frame(server_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        self.start_button = tk.Button(
            button_frame,
            text="🚀 Iniciar Servidor",
            command=self.start_server,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ Parar Servidor",
            command=self.stop_server,
            bg=self.colors['danger'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.check_button = tk.Button(
            button_frame,
            text="🔍 Verificar Status",
            command=self.check_server_status,
            bg=self.colors['secondary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        self.check_button.pack(side=tk.LEFT)
    
    def create_ai_frame(self, parent):
        """Cria o frame de funcionalidades da IA."""
        ai_frame = tk.LabelFrame(
            parent, 
            text="Reconhecimento de Plâncton com IA",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary'],
            padx=10,
            pady=10
        )
        ai_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame superior (imagem e controles)
        top_frame = tk.Frame(ai_frame, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame da imagem
        image_frame = tk.Frame(top_frame, bg='#f0f0f0')
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas para exibir a imagem
        self.image_canvas = tk.Canvas(
            image_frame,
            width=300,
            height=300,
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.image_canvas.pack(pady=(0, 10))
        
        # Label para informações da imagem
        self.image_info_label = tk.Label(
            image_frame,
            text="Nenhuma imagem selecionada",
            font=('Arial', 8),
            bg='#f0f0f0',
            fg=self.colors['dark']
        )
        self.image_info_label.pack(pady=(0, 10))
        
        # Botões para manipulação de imagem
        button_frame = tk.Frame(image_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        # Botão para selecionar imagem
        self.select_image_button = tk.Button(
            button_frame,
            text="📁 Selecionar Imagem",
            command=self.select_image,
            bg=self.colors['secondary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        self.select_image_button.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(self.select_image_button, "Selecionar uma imagem de plâncton para classificação")
        
        # Botão para limpar imagem
        self.clear_image_button = tk.Button(
            button_frame,
            text="🗑️ Limpar",
            command=self.clear_image,
            bg=self.colors['danger'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.clear_image_button.pack(side=tk.LEFT)
        self.create_tooltip(self.clear_image_button, "Limpar a imagem atual")
        
        # Frame dos resultados
        results_frame = tk.Frame(top_frame, bg='#f0f0f0')
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        tk.Label(
            results_frame,
            text="Resultados da Classificação:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary']
        ).pack(anchor=tk.W)
        
        # Área de resultados
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            width=40,
            font=('Courier', 9),
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Botão para classificar
        self.classify_button = tk.Button(
            results_frame,
            text="🔬 Classificar Plâncton",
            command=self.classify_image,
            bg=self.colors['warning'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.classify_button.pack()
    
    def create_log_frame(self, parent):
        """Cria o frame de logs do servidor."""
        log_frame = tk.LabelFrame(
            parent, 
            text="Logs do Servidor",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary'],
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.X)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=('Courier', 8),
            bg='black',
            fg='green',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.log_text.pack(fill=tk.X)
    
    def log_message(self, message, level="INFO"):
        """Adiciona uma mensagem ao log."""
        colors = {
            "INFO": "green",
            "ERROR": "red",
            "WARNING": "yellow",
            "SUCCESS": "cyan"
        }
        
        self.log_text.insert(tk.END, f"[{level}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()
    
    def start_server(self):
        """Inicia o servidor Flask."""
        if self.process is None:
            flask_script_path = os.path.abspath("flask_server.py")
            
            if not os.path.exists(flask_script_path):
                messagebox.showerror("Erro", f"Arquivo {flask_script_path} não encontrado!")
                return
            
            try:
                self.process = subprocess.Popen(
                    [sys.executable, flask_script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                self.status_label.config(text="Servidor iniciando...", fg=self.colors['warning'])
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                self.log_message("Iniciando servidor Flask...", "INFO")
                
                # Inicia thread para ler output
                threading.Thread(target=self.read_output, daemon=True).start()
                
                # Verifica se o servidor está rodando após alguns segundos
                self.master.after(3000, self.check_server_after_start)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao iniciar servidor: {e}")
                self.log_message(f"Erro ao iniciar servidor: {e}", "ERROR")
    
    def stop_server(self):
        """Para o servidor Flask."""
        if self.process:
            self.process.terminate()
            self.process = None
            self.status_label.config(text="Servidor parado", fg=self.colors['danger'])
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.classify_button.config(state=tk.DISABLED)
            self.log_message("Servidor parado", "INFO")
    
    def read_output(self):
        """Lê o output do processo Flask."""
        if not self.process:
            return
        
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_message(line.strip(), "INFO")
                if self.process.poll() is not None:
                    break
        except Exception as e:
            self.log_message(f"Erro ao ler output: {e}", "ERROR")
    
    def check_server_after_start(self):
        """Verifica o status do servidor após inicialização."""
        self.check_server_status()
    
    def check_server_status(self):
        """Verifica se o servidor está rodando."""
        try:
            # Atualizar indicador de atividade
            self.activity_indicator.config(text="🔄")  # Símbolo de atualização
            self.master.update_idletasks()
            
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.status_label.config(
                    text=f"Servidor ativo - {data.get('message', 'OK')}", 
                    fg=self.colors['success']
                )
                self.classify_button.config(state=tk.NORMAL if self.current_image_path else tk.DISABLED)
                self.log_message("Servidor está ativo e respondendo", "SUCCESS")
                self.activity_indicator.config(text="🟢")  # Círculo verde
                
                # Atualizar informações do modelo se disponíveis
                if data.get('model_info') and not self.model_info:
                    self.model_info = data.get('model_info')
                    self.get_model_info()
                    
            else:
                self.status_label.config(text="Servidor com problemas", fg=self.colors['warning'])
                self.classify_button.config(state=tk.DISABLED)
                self.activity_indicator.config(text="🟠")  # Círculo laranja
                
        except requests.exceptions.RequestException:
            self.status_label.config(text="Servidor não acessível", fg=self.colors['danger'])
            self.classify_button.config(state=tk.DISABLED)
            self.activity_indicator.config(text="🔴")  # Círculo vermelho
            
        # Atualizar barra de status
        self.update_status_bar(f"Última verificação: {time.strftime('%H:%M:%S')}")
    
    def select_image(self):
        """Abre diálogo para selecionar uma imagem."""
        file_types = [
            ("Todas as Imagens", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp *.heic *.heif *.raw *.svg *.psd"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("GIF", "*.gif"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff"),
            ("WebP", "*.webp"),
            ("HEIC/HEIF", "*.heic *.heif"),
            ("RAW", "*.raw"),
            ("SVG", "*.svg"),
            ("PSD", "*.psd"),
            ("Todos os arquivos", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem de plâncton",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.log_message(f"Imagem selecionada: {os.path.basename(file_path)}", "INFO")
            
            # Habilita o botão de classificar se o servidor estiver ativo
            if "ativo" in self.status_label.cget("text"):
                self.classify_button.config(state=tk.NORMAL)
    
    def display_image(self, image_path):
        """Exibe a imagem selecionada no canvas."""
        try:
            # Abre e redimensiona a imagem
            image = Image.open(image_path)
            
            # Calcula o tamanho para manter a proporção
            canvas_width = 300
            canvas_height = 300
            
            img_width, img_height = image.size
            ratio = min(canvas_width/img_width, canvas_height/img_height)
            
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Converte para PhotoImage
            self.current_image = ImageTk.PhotoImage(image)
            
            
            self.image_canvas.delete("all")
            
            
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=self.current_image)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")
            self.log_message(f"Erro ao carregar imagem: {e}", "ERROR")
    
    def classify_image(self):
        """Envia a imagem para classificação."""
        if not self.current_image_path:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro!")
            return
        
        try:
            self.log_message("Enviando imagem para classificação...", "INFO")
            self.classify_button.config(state=tk.DISABLED, text="Classificando...")
            
            # Mostrar barra de progresso
            progress_window = tk.Toplevel(self.master)
            progress_window.title("Classificando imagem")
            progress_window.geometry("300x100")
            progress_window.resizable(False, False)
            progress_window.transient(self.master)
            progress_window.grab_set()
            
            tk.Label(
                progress_window, 
                text="Processando imagem e classificando...",
                font=('Arial', 10),
                pady=10
            ).pack()
            
            progress = ttk.Progressbar(
                progress_window, 
                orient="horizontal",
                length=250, 
                mode="indeterminate"
            )
            progress.pack(pady=10)
            progress.start(10)
            
            # Iniciar tempo para medir performance
            start_time = time.time()
            
            # Executar classificação em uma thread separada
            def do_classification():
                try:
                    with open(self.current_image_path, 'rb') as f:
                        files = {'file': f}
                        response = requests.post(f"{self.server_url}/predict", files=files, timeout=30)
                    
                    # Calcular tempo de processamento
                    elapsed_time = time.time() - start_time
                    self.last_prediction_time = elapsed_time
                    
                    # Atualizar UI na thread principal
                    self.master.after(0, lambda: self.process_classification_result(response, progress_window))
                    
                except Exception as e:
                    self.master.after(0, lambda: self.handle_classification_error(e, progress_window))
            
            threading.Thread(target=do_classification, daemon=True).start()
            
        except Exception as e:
            error_msg = f"Erro inesperado: {e}"
            messagebox.showerror("Erro", error_msg)
            self.log_message(error_msg, "ERROR")
            self.classify_button.config(state=tk.NORMAL, text="🔬 Classificar Plâncton")
    
    def process_classification_result(self, response, progress_window):
        """Processa o resultado da classificação."""
        try:
            progress_window.destroy()
            
            if response.status_code == 200:
                result = response.json()
                print(f"Resultado da classificação: {result}")  # Depuração
                
                if result.get('success', False):
                    prediction = result.get('prediction', {})
                    self.display_results(result)
                    
                    # Verificar extensão do arquivo original
                    original_ext = os.path.splitext(self.current_image_path)[1].lower().replace('.', '')
                    format_info = ""
                    
                    # Verificar se o formato precisou ser convertido
                    if original_ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
                        format_info = f" (Formato {original_ext.upper()} convertido automaticamente)"
                    
                    # Verificar se o resultado tem informação de cache
                    cache_info = ""
                    if prediction.get('cached', False):
                        cache_info = " (resultado do cache)"
                        self.log_message("Resultado obtido do cache!", "INFO")
                    
                    self.log_message(f"Classificação concluída em {self.last_prediction_time:.2f} segundos{cache_info}{format_info}", "SUCCESS")
                    
                    # Atualizar barra de status
                    self.update_status_bar(f"Última classificação: {prediction.get('predicted_class', 'Desconhecido')} ({prediction.get('confidence', 0):.2%})")
                else:
                    error_msg = f"Erro na classificação: {result.get('error', 'Erro desconhecido')}"
                    messagebox.showerror("Erro", error_msg)
                    self.log_message(error_msg, "ERROR")
            else:
                error_msg = f"Erro na resposta do servidor: {response.status_code} - {response.text}"
                messagebox.showerror("Erro", error_msg)
                self.log_message(error_msg, "ERROR")
        except Exception as e:
            self.log_message(f"Erro ao processar resultado: {e}", "ERROR")
        finally:
            self.classify_button.config(state=tk.NORMAL, text="🔬 Classificar Plâncton")
    
    def handle_classification_error(self, error, progress_window):
        """Trata erros durante a classificação."""
        try:
            progress_window.destroy()
        except:
            pass
            
        if isinstance(error, requests.exceptions.RequestException):
            error_msg = f"Erro de conexão: {error}"
        else:
            error_msg = f"Erro inesperado: {error}"
            
        messagebox.showerror("Erro", error_msg)
        self.log_message(error_msg, "ERROR")
        self.classify_button.config(state=tk.NORMAL, text="🔬 Classificar Plâncton")
    
    def display_results(self, result):
        """Exibe os resultados da classificação."""
        self.results_text.delete(1.0, tk.END)
        
        if result.get('success'):
            prediction = result['prediction']
            
            # Aplicar formatação com cores
            self.results_text.tag_configure("title", font=("Arial", 10, "bold"), foreground=self.colors['primary'])
            self.results_text.tag_configure("subtitle", font=("Arial", 9, "bold"), foreground=self.colors['secondary'])
            self.results_text.tag_configure("highlight", foreground=self.colors['success'], font=("Arial", 10, "bold"))
            self.results_text.tag_configure("warning", foreground=self.colors['warning'])
            self.results_text.tag_configure("danger", foreground=self.colors['danger'])
            self.results_text.tag_configure("info", foreground=self.colors['info'])
            
            # Resultado principal
            self.results_text.insert(tk.END, "=== RESULTADO DA CLASSIFICAÇÃO ===\n\n", "title")
            self.results_text.insert(tk.END, "Classe Predita: ", "subtitle")
            self.results_text.insert(tk.END, f"{prediction['predicted_class']}\n", "highlight")
            
            # Confiança com formatação baseada no valor
            confidence = prediction['confidence']
            self.results_text.insert(tk.END, "Confiança: ", "subtitle")
            
            confidence_tag = "highlight" if confidence > 0.7 else ("warning" if confidence > 0.4 else "danger")
            self.results_text.insert(tk.END, f"{confidence:.2%}\n\n", confidence_tag)
            
            # Tempo de processamento se disponível
            if 'time_ms' in prediction:
                self.results_text.insert(tk.END, f"Tempo: {prediction['time_ms']:.2f}ms")
                if prediction.get('cached', False):
                    self.results_text.insert(tk.END, " (resultado em cache)\n\n", "info")
                else:
                    self.results_text.insert(tk.END, "\n\n")
            else:
                self.results_text.insert(tk.END, f"Tempo: {self.last_prediction_time:.2f}s\n\n")
            
            # Todas as probabilidades
            self.results_text.insert(tk.END, "=== TODAS AS PROBABILIDADES ===\n\n", "title")
            
            all_preds = prediction['all_predictions']
            sorted_preds = sorted(all_preds.items(), key=lambda x: x[1], reverse=True)
            
            for class_name, probability in sorted_preds:
                bar_length = int(probability * 20)  
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                # Escolher cor baseada na probabilidade
                prob_tag = "highlight" if probability > 0.7 else ("warning" if probability > 0.4 else "")
                
                self.results_text.insert(tk.END, f"{class_name:<15} ")
                self.results_text.insert(tk.END, f"{bar} {probability:.2%}\n", prob_tag)
            
            # Informações adicionais
            self.results_text.insert(tk.END, f"\n=== INFORMAÇÕES ===\n\n", "title")
            self.results_text.insert(tk.END, f"Arquivo: {os.path.basename(result.get('filename', 'N/A'))}\n")
            
            # Interpretação do resultado
            self.results_text.insert(tk.END, "Interpretação: ", "subtitle")
            if confidence > 0.8:
                interpretation = "Alta confiança - Resultado muito provável"
                interp_tag = "highlight"
            elif confidence > 0.6:
                interpretation = "Confiança moderada - Resultado provável"
                interp_tag = "info"
            elif confidence > 0.4:
                interpretation = "Baixa confiança - Resultado incerto"
                interp_tag = "warning"
            else:
                interpretation = "Confiança muito baixa - Resultado duvidoso"
                interp_tag = "danger"
            
            self.results_text.insert(tk.END, f"{interpretation}\n", interp_tag)
            
            # Adicionar sugestão se a confiança for baixa
            if confidence < 0.6:
                self.results_text.insert(tk.END, "\nSugestão: ", "subtitle")
                self.results_text.insert(tk.END, "Considere usar uma imagem com melhor qualidade ou iluminação para obter resultados mais precisos.\n", "warning")
            
        else:
            self.results_text.insert(tk.END, "ERRO NA CLASSIFICAÇÃO\n\n", "danger")
            self.results_text.insert(tk.END, f"Detalhes: {result}\n")

    def create_model_info_frame(self, parent):
        """Cria o frame de informações do modelo."""
        model_frame = tk.LabelFrame(
            parent, 
            text="Informações do Modelo",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg=self.colors['primary'],
            padx=10,
            pady=10
        )
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Conteúdo do frame
        self.model_info_text = scrolledtext.ScrolledText(
            model_frame,
            height=4,
            font=('Courier', 8),
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.model_info_text.pack(fill=tk.X)
        
        # Botão para atualizar informações do modelo
        refresh_button = tk.Button(
            model_frame,
            text="🔄 Atualizar Informações",
            command=self.get_model_info,
            bg=self.colors['secondary'],
            fg='white',
            font=('Arial', 9),
            padx=10,
            pady=2
        )
        refresh_button.pack(pady=(5, 0), anchor=tk.E)
        self.create_tooltip(refresh_button, "Atualizar informações do modelo de IA")
    
    def create_status_bar(self, parent):
        """Cria a barra de status na parte inferior da janela."""
        status_bar = tk.Frame(parent, bg=self.colors['dark'], height=25)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Informações do sistema
        system_info = f"Sistema: {platform.system()} {platform.release()}"
        system_label = tk.Label(
            status_bar,
            text=system_info,
            bg=self.colors['dark'],
            fg='white',
            font=('Arial', 8),
            padx=10
        )
        system_label.pack(side=tk.LEFT)
        
        # Status atual
        self.status_bar_label = tk.Label(
            status_bar,
            text="Pronto",
            bg=self.colors['dark'],
            fg='white',
            font=('Arial', 8),
            padx=10
        )
        self.status_bar_label.pack(side=tk.RIGHT)
    
    def update_status_bar(self, message):
        """Atualiza a mensagem na barra de status."""
        self.status_bar_label.config(text=message)
    
    def create_tooltip(self, widget, text):
        """Cria um tooltip para um widget."""
        tooltip_id = str(id(widget))
        
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Criar uma janela top level
            self.tooltips[tooltip_id] = tk.Toplevel(widget)
            self.tooltips[tooltip_id].wm_overrideredirect(True)
            self.tooltips[tooltip_id].wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                self.tooltips[tooltip_id], 
                text=text, 
                background="#ffffe0", 
                relief="solid", 
                borderwidth=1,
                font=("Arial", 8),
                padx=5,
                pady=2
            )
            label.pack()
        
        def leave(event):
            if tooltip_id in self.tooltips:
                self.tooltips[tooltip_id].destroy()
                del self.tooltips[tooltip_id]
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def clear_image(self):
        """Limpa a imagem atual."""
        self.current_image_path = None
        self.current_image = None
        self.image_canvas.delete("all")
        self.image_info_label.config(text="Nenhuma imagem selecionada")
        self.clear_image_button.config(state=tk.DISABLED)
        self.classify_button.config(state=tk.DISABLED)
        self.log_message("Imagem removida", "INFO")
    
    def get_model_info(self):
        """Obtém informações sobre o modelo de IA."""
        try:
            self.model_info_text.delete(1.0, tk.END)
            self.model_info_text.insert(tk.END, "Obtendo informações do modelo...")
            
            # Verificar se o servidor está ativo
            if "ativo" not in self.status_label.cget("text"):
                self.model_info_text.delete(1.0, tk.END)
                self.model_info_text.insert(tk.END, "Servidor não está ativo. Inicie o servidor para obter informações do modelo.")
                return
            
            # Fazer requisição para obter classes suportadas
            response = requests.get(f"{self.server_url}/classes", timeout=5)
            
            if response.status_code == 200:
                classes_data = response.json()
                
                # Fazer requisição para obter status do servidor (que inclui info do modelo)
                status_response = requests.get(f"{self.server_url}/status", timeout=5)
                status_data = status_response.json() if status_response.status_code == 200 else {}
                
                # Limpar e inserir informações
                self.model_info_text.delete(1.0, tk.END)
                
                # Informações do modelo
                model_info = status_data.get('model_info', {})
                if model_info:
                    self.model_info_text.insert(tk.END, f"Modelo: {model_info.get('name', 'Desconhecido')}\n")
                    self.model_info_text.insert(tk.END, f"Parâmetros: {model_info.get('parameters', 'N/A')}\n")
                    self.model_info_text.insert(tk.END, f"Dispositivo: {model_info.get('device', 'CPU')}\n")
                
                # Classes suportadas
                classes = classes_data.get('classes', [])
                if classes:
                    self.model_info_text.insert(tk.END, f"Classes suportadas ({len(classes)}): {', '.join(classes)}\n")
                
                # Estatísticas de cache se disponíveis
                cache_stats = model_info.get('cache_stats', {})
                if cache_stats:
                    self.model_info_text.insert(tk.END, f"Cache: {cache_stats.get('hits', 0)} acertos, {cache_stats.get('misses', 0)} falhas, {cache_stats.get('size', 0)} itens")
                
                self.log_message("Informações do modelo atualizadas", "SUCCESS")
            else:
                self.model_info_text.delete(1.0, tk.END)
                self.model_info_text.insert(tk.END, "Erro ao obter informações do modelo.")
                self.log_message("Erro ao obter informações do modelo", "ERROR")
                
        except Exception as e:
            self.model_info_text.delete(1.0, tk.END)
            self.model_info_text.insert(tk.END, f"Erro: {str(e)}")
            self.log_message(f"Erro ao obter informações do modelo: {e}", "ERROR")
    
    def select_image(self):
        """Abre diálogo para selecionar uma imagem."""
        file_types = [
            ("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("Todos os arquivos", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem de plâncton",
            filetypes=file_types
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.log_message(f"Imagem selecionada: {os.path.basename(file_path)}", "INFO")
            
            # Atualizar informações da imagem
            try:
                img = Image.open(file_path)
                img_size = os.path.getsize(file_path) / 1024  # KB
                self.image_info_label.config(
                    text=f"{os.path.basename(file_path)} | {img.width}x{img.height} | {img_size:.1f} KB"
                )
            except Exception as e:
                self.image_info_label.config(text=f"Erro ao ler informações: {e}")
            
            # Habilitar botões
            self.clear_image_button.config(state=tk.NORMAL)
            if "ativo" in self.status_label.cget("text"):
                self.classify_button.config(state=tk.NORMAL)

def main():
    """Função principal."""
    root = tk.Tk()
    app = PlanktonAIApp(root)
    
    # Configurar ícone da aplicação se disponível
    try:
        # Tentar usar um ícone se existir no sistema
        root.iconbitmap("plankton_icon.ico")
    except:
        pass
    
    def on_closing():
        if app.process:
            app.stop_server()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
