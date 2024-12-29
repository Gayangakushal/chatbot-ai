import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from huggingface_hub import InferenceClient
from datetime import datetime
from tkinter import messagebox
import time

class LoadingDots(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg='#f0f0f0', highlightthickness=0, height=20)
        self.dots = []
        self.running = False
        
        # Create dots
        for i in range(3):
            dot = self.create_oval(10+i*20, 8, 20+i*20, 18, fill='#4a90e2')
            self.dots.append(dot)
    
    def animate(self):
        if not self.running:
            return
        
        for i, dot in enumerate(self.dots):
            # Create bounce animation
            def bounce(dot, delay):
                time.sleep(delay)
                for y in [6, 4, 2, 0, -2, -4, -6, -4, -2, 0, 2, 4, 6]:
                    if not self.running:
                        return
                    self.move(dot, 0, y)
                    time.sleep(0.05)
            
            thread = threading.Thread(target=bounce, args=(dot, i*0.2))
            thread.daemon = True
            thread.start()
        
        if self.running:
            self.after(1000, self.animate)
    
    def start(self):
        self.running = True
        self.animate()
    
    def stop(self):
        self.running = False

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(height=40, highlightthickness=0, bg='#f0f0f0')
        self.text = text
        self.command = command
        self.width = 100  # Default width
        
        # Draw initial button state
        self.draw_rounded_button('#4a90e2')
        self.button_text = self.create_text(50, 20, text=text, fill='white', font=('Segoe UI', 10, 'bold'))
        
        # Bind events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def draw_rounded_button(self, color):
        # Clear previous drawings
        self.delete("button")
        
        radius = 20  # Corner radius
        width = self.width
        height = 40
        
        # Create rounded rectangle using arcs and lines
        # Top left corner
        self.create_arc(0, 0, radius*2, radius*2, 
                       start=90, extent=90, fill=color, outline=color, tags="button")
        # Top right corner
        self.create_arc(width-radius*2, 0, width, radius*2, 
                       start=0, extent=90, fill=color, outline=color, tags="button")
        # Bottom left corner
        self.create_arc(0, height-radius*2, radius*2, height, 
                       start=180, extent=90, fill=color, outline=color, tags="button")
        # Bottom right corner
        self.create_arc(width-radius*2, height-radius*2, width, height, 
                       start=270, extent=90, fill=color, outline=color, tags="button")
        
        # Center rectangles
        self.create_rectangle(radius, 0, width-radius, height, 
                            fill=color, outline=color, tags="button")
        self.create_rectangle(0, radius, width, height-radius, 
                            fill=color, outline=color, tags="button")
    
    def on_enter(self, event):
        self.draw_rounded_button('#357abd')
    
    def on_leave(self, event):
        self.draw_rounded_button('#4a90e2')
    
    def on_click(self, event):
        self.draw_rounded_button('#2a5885')
    
    def on_release(self, event):
        self.draw_rounded_button('#4a90e2')
        self.command()

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat Application")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Custom styles
        self.setup_styles()
        self.setup_gui()
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('Chat.TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 12, 'bold'),
                           background='#f0f0f0')
        self.style.configure('Config.TLabelframe',
                           background='#ffffff',
                           padding=10)
        self.style.configure('Config.TLabelframe.Label',
                           font=('Segoe UI', 10, 'bold'),
                           background='#f0f0f0')
        
    def setup_gui(self):
        # Main container with gradient background
        main_frame = ttk.Frame(self.root, style='Chat.TFrame', padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Chat.TFrame')
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="AI Chat Assistant",
                 style='Header.TLabel').pack(side="left")
        
        # API Configuration
        config_frame = ttk.LabelFrame(main_frame,
                                    text="Configuration",
                                    style='Config.TLabelframe',
                                    padding="10")
        config_frame.pack(fill="x", pady=(0, 20))
        
        # API Key
        api_frame = ttk.Frame(config_frame)
        api_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(api_frame, 
                 text="API Key:",
                 font=('Segoe UI', 9)).pack(side="left", padx=5)
        self.api_key = ttk.Entry(api_frame, width=50, show="•")
        self.api_key.pack(side="left", padx=5)
        
        # Model selection
        model_frame = ttk.Frame(config_frame)
        model_frame.pack(fill="x")
        
        ttk.Label(model_frame,
                 text="Model:",
                 font=('Segoe UI', 9)).pack(side="left", padx=5)
        self.model_var = tk.StringVar(value="meta-llama/Llama-3.2-3B-Instruct")
        self.model_combo = ttk.Combobox(model_frame,
                                      textvariable=self.model_var,
                                      width=40,
                                      state="readonly")
        self.model_combo['values'] = (
            "meta-llama/Llama-3.2-3B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "Qwen/Qwen2.5-72B-Chat"
        )
        self.model_combo.pack(side="left", padx=5)
        
        # Chat area
        chat_frame = ttk.Frame(main_frame, style='Chat.TFrame')
        chat_frame.pack(fill="both", expand=True)
        
        # Chat display with custom styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            height=20,
            background='#ffffff',
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill="both", expand=True)
        
        # Configure message styling
        self.chat_display.tag_configure('user',
                                      foreground='#2c3e50',
                                      font=('Segoe UI', 10, 'bold'),
                                      spacing1=10,
                                      spacing3=5)
        self.chat_display.tag_configure('assistant',
                                      foreground='#27ae60',
                                      font=('Segoe UI', 10),
                                      spacing1=10,
                                      spacing3=5)
        self.chat_display.tag_configure('time',
                                      foreground='#95a5a6',
                                      font=('Segoe UI', 8))
        
        # Loading animation
        self.loading_dots = LoadingDots(chat_frame)
        self.loading_dots.pack(pady=5)
        self.loading_dots.pack_forget()
        
        # Input area with modern styling
        input_frame = ttk.Frame(main_frame, style='Chat.TFrame')
        input_frame.pack(fill="x", pady=(10, 0))
        
        self.message_input = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            height=4,
            background='#ffffff',
            padx=10,
            pady=5
        )
        self.message_input.pack(fill="x", side="left", expand=True, padx=(0, 10))
        
        # Modern send button
        self.send_button = ModernButton(
            input_frame,
            text="Send",
            command=self.send_message,
        )
        self.send_button.pack(side="right")
        
        # Key bindings
        self.message_input.bind('<Control-Return>', lambda e: self.send_message())
        
        # Status bar with modern styling
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            foreground='#7f8c8d',
            padding=(5, 2)
        )
        self.status_bar.pack(fill="x", pady=(10, 0))
        
        # Initialize message history
        self.message_history = []
        
    def add_message_to_display(self, role, content):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'time')
        self.chat_display.insert(tk.END, f"{role}: ", role.lower())
        self.chat_display.insert(tk.END, f"{content}\n\n")
        self.chat_display.see(tk.END)
        
    def send_message(self):
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        api_key = self.api_key.get()
        if not api_key:
            messagebox.showerror("Error", "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")
            return
        
        # Show loading animation
        self.send_button.configure(state="disabled")
        self.message_input.configure(state="disabled")
        self.loading_dots.pack()
        self.loading_dots.start()
        self.status_var.set("Thinking...")
        
        # Add user message
        self.add_message_to_display("User", message)
        self.message_input.delete("1.0", tk.END)
        
        # Update history
        self.message_history.append({
            "role": "user",
            "content": message
        })
        
        # Start AI response thread
        thread = threading.Thread(target=self.get_ai_response, args=(api_key, message))
        thread.daemon = True
        thread.start()
        
    def get_ai_response(self, api_key, message):
        try:
            client = InferenceClient(api_key=api_key)
            
            stream = client.chat.completions.create(
                model=self.model_var.get(),
                messages=self.message_history,
                max_tokens=500,
                stream=True
            )
            
            response_parts = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_parts.append(content)
                    self.root.after(0, self.update_assistant_response, content)
            
            complete_response = "".join(response_parts)
            self.message_history.append({
                "role": "assistant",
                "content": complete_response
            })
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.root.after(0, self.cleanup_after_response)
            
    def cleanup_after_response(self):
        self.loading_dots.stop()
        self.loading_dots.pack_forget()
        self.send_button.configure(state="normal")
        self.message_input.configure(state="normal")
        self.message_input.focus()
        self.status_var.set("Ready")
        
    def update_assistant_response(self, content):
        if not hasattr(self, 'current_response_started'):
            self.current_response_started = True
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'time')
            self.chat_display.insert(tk.END, "Assistant: ", 'assistant')
        
        self.chat_display.insert(tk.END, content)
        self.chat_display.see(tk.END)
        
        if content.endswith('\n'):
            self.current_response_started = False
            self.chat_display.insert(tk.END, "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()