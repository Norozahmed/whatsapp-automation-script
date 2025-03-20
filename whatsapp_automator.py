import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pywhatkit as pwk
import threading
from datetime import datetime
from queue import Queue

class WhatsAppAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional WhatsApp Automator")
        self.root.geometry("600x500")
        
        # Configuration defaults
        self.tab_close = tk.BooleanVar(value=True)
        self.close_time = tk.IntVar(value=10)
        self.is_group = tk.BooleanVar(value=False)
        
        self.log_queue = Queue()  # Queue for logging messages
        
        self.create_widgets()
        
        # Start checking the log queue
        self.check_log_queue()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Fields
        ttk.Label(main_frame, text="Recipient/Group ID:").grid(row=0, column=0, sticky=tk.W)
        self.recipient_entry = ttk.Entry(main_frame, width=30)
        self.recipient_entry.grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Message:").grid(row=1, column=0, sticky=tk.W)
        self.message_entry = ttk.Entry(main_frame, width=30)
        self.message_entry.grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Schedule Time (HH:MM):").grid(row=2, column=0, sticky=tk.W)
        self.time_entry = ttk.Entry(main_frame, width=10)
        self.time_entry.grid(row=2, column=1, pady=5, sticky=tk.W)

        # Image Attachment
        ttk.Label(main_frame, text="Image Path:").grid(row=3, column=0, sticky=tk.W)
        self.image_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.image_path, width=25).grid(row=3, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="Browse", command=self.browse_image).grid(row=3, column=1, sticky=tk.E)

        # Additional Options
        ttk.Checkbutton(main_frame, text="Send to Group", variable=self.is_group).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(main_frame, text="Close Tab After Sending", variable=self.tab_close).grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
        # Control Buttons
        ttk.Button(main_frame, text="Schedule Message", command=self.validate_inputs).grid(row=6, column=0, pady=15)
        ttk.Button(main_frame, text="Send Now", command=self.send_immediately).grid(row=6, column=1, pady=15)

        # Log Console
        self.log_console = tk.Text(main_frame, height=8, width=50)
        self.log_console.grid(row=7, column=0, columnspan=2, pady=10)

    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        self.image_path.set(path)

    def validate_inputs(self):
        recipient = self.recipient_entry.get()
        message = self.message_entry.get()
        time_str = self.time_entry.get()
        
        try:
            schedule_time = datetime.strptime(time_str, "%H:%M")
            current_time = datetime.now()
            
            if schedule_time < current_time:
                raise ValueError("Scheduled time must be in the future")
                
            if not recipient.startswith("+"):
                raise ValueError("Invalid recipient format. Use international format (+XX...)")
                
            self.log("Validation successful. Scheduling message...")
            self.schedule_message(schedule_time.hour, schedule_time.minute)
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.log(f"Error: {str(e)}")

    def schedule_message(self, hour=None, minute=None):
        threading.Thread(target=self.send_message_threadsafe_wrapper,
                         args=(hour,
                               minute)).start()

    def send_message_threadsafe_wrapper(self,
                                        hour=None,
                                        minute=None):
        recipient = self.recipient_entry.get()
        message = self.message_entry.get()
        image_path = self.image_path.get()
        
        if hour is not None and minute is not None:
            if self.is_group.get():
                # Note: pywhatkit does not support sending to groups
                pass
            else:
                pwk.sendwhatmsg(
                    phone_no=recipient,
                    message=message,
                    time_hour=hour,
                    time_min=minute,
                    tab_close=True,
                    close_time=10
                )
        else:
            if self.is_group.get():
                # Note: pywhatkit does not support sending to groups instantly
                pass
            else:
                pwk.sendwhatmsg_instantly(
                    phone_no=recipient,
                    
                    message=message,
                    tab_close=True,
                    close_time=10
                )
        
        if image_path:
            try:
                pwk.sendwhats_image(
                    receiver=recipient,
                    img_path=image_path,
                    caption=message,
                    tab_close=True
                )
                self.log_queue.put("Image sent successfully!")
            except Exception as e:
                self.log_queue.put(f"Error sending image: {str(e)}")
        
        self.log_queue.put("Message scheduled successfully!")

    def send_immediately(self):
        if messagebox.askyesno("Confirmation", "Send message immediately?"):
            threading.Thread(target=self.send_message_threadsafe_wrapper).start()

    def log(self, message):
        self.log_queue.put(message)

    def check_log_queue(self):
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get()
                self.log_console.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
                self.log_console.see(tk.END)
        except Exception as e:
            print(f"Error checking log queue: {e}")
        finally:
            self.root.after(100, self.check_log_queue)  # Check every 100ms

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppAutomationApp(root)
    root.mainloop()
