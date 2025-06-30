import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import requests
import io
import threading
import os
from datetime import datetime

class FaceGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Генератор лиц")
        root.geometry("650x750") 

        self.current_image = None
        self.current_photo = None
        

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=20)
        

        self.create_gender_radiobuttons()

        self.create_age_radiobuttons()

        self.create_smile_radiobuttons()
        

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.generate_btn = ttk.Button(
            button_frame, 
            text="Сгенерировать", 
            command=self.start_generation_thread,
            width=15
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        

        self.save_btn = ttk.Button(
            button_frame,
            text="Сохранить",
            command=self.save_image,
            width=15,
            state=tk.DISABLED 
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        

        self.loading_label = tk.Label(root, text="", font=('Arial', 10))
        self.loading_label.pack()
        

        self.server_url = "https://06c6-34-127-78-215.ngrok-free.app/generate"
        
    def create_gender_radiobuttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill='x', padx=20, pady=10)
        
        label = ttk.Label(frame, text="Пол:", width=10, anchor='w')
        label.pack(side='left')

        self.gender = tk.DoubleVar(value=0.0)

        options_frame = ttk.Frame(frame)
        options_frame.pack(side='left', padx=10)


        genders = [("Случайно", 0.0), ("Мужской", 3.0), ("Женский", -3.0)]
        for text, value in genders:
            rb = ttk.Radiobutton(
                options_frame, 
                text=text, 
                variable=self.gender, 
                value=value
            )
            rb.pack(side='left', padx=5)

    def create_age_radiobuttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill='x', padx=20, pady=10)
        
        label = ttk.Label(frame, text="Возраст:", width=10, anchor='w')
        label.pack(side='left')

        self.age = tk.DoubleVar(value=0.0)

        options_frame = ttk.Frame(frame)
        options_frame.pack(side='left', padx=10)


        age_options = [
            ("Случайно", 0.0),
            ("До 18 лет", -3),
            ("18–45 лет", 0.8),
            ("Более 45 лет", 3.0)
        ]
        for text, value in age_options:
            rb = ttk.Radiobutton(
                options_frame, 
                text=text, 
                variable=self.age, 
                value=value
            )
            rb.pack(side='left', padx=5)

    def create_smile_radiobuttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill='x', padx=20, pady=10)
        
        label = ttk.Label(frame, text="Улыбка:", width=10, anchor='w')
        label.pack(side='left')

        self.smile = tk.DoubleVar(value=0.0)

        options_frame = ttk.Frame(frame)
        options_frame.pack(side='left', padx=10)

        smile_options = [
            ("Случайно", 0.0),
            ("Грустный", -3.0),
            ("Слабая улыбка", -1.5),
            ("Сильная улыбка", 3.0)
        ]
        for text, value in smile_options:
            rb = ttk.Radiobutton(
                options_frame, 
                text=text, 
                variable=self.smile, 
                value=value
            )
            rb.pack(side='left', padx=5)


    def create_slider(self, label_text, var_name, from_, to_):
        frame = ttk.Frame(self.root)
        frame.pack(fill='x', padx=20, pady=10)
        
        label = ttk.Label(frame, text=label_text, width=10, anchor='w')
        label.pack(side='left')
        
        var = tk.DoubleVar(value=0.0)
        setattr(self, var_name, var)
        
        slider = ttk.Scale(
            frame,
            from_=from_,
            to=to_,
            orient='horizontal',
            variable=var,
            length=400
        )
        slider.pack(side='right', padx=10)
        
    def start_generation_thread(self):
        """Запускает генерацию в отдельном потоке"""
        self.loading_label.config(text="Генерация изображения...", fg='blue')
        self.generate_btn.config(state="disabled")
        self.save_btn.config(state="disabled") 
        
        thread = threading.Thread(target=self.generate)
        thread.start()
        

        self.check_thread(thread)
        
    def check_thread(self, thread):
        """Проверяет завершение потока"""
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread(thread))
        else:
            self.loading_label.config(text="")
            self.generate_btn.config(state="normal")
        
    def generate(self):
        try:

            params = {
                'age': self.age.get(),
                'gender': self.gender.get(),
                'smile': self.smile.get()
            }
            

            response = requests.post(
                self.server_url,
                json=params,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:

                image_data = io.BytesIO(response.content)
                img = Image.open(image_data)
                

                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                img = img.resize((350, 350), Image.LANCZOS) 
                

                self.current_image = img.copy()
                

                self.root.after(0, lambda: self.show_image(img))
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка", 
                    f"Сервер вернул ошибку: {response.status_code}\n{response.text}"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка", 
                f"Произошла ошибка: {str(e)}"
            ))
    
    def show_image(self, img):
        self.current_photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.current_photo)
        self.save_btn.config(state=tk.NORMAL)  
    
    def save_image(self):
        if self.current_image is None:
            messagebox.showwarning("Предупреждение", "Нет изображения для сохранения")
            return
            

        default_filename = f"face_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("JPEG файлы", "*.jpg"), ("Все файлы", "*.*")],
            initialfile=default_filename
        )
        
        if filepath:
            try:
                ext = os.path.splitext(filepath)[1].lower()
                if ext == '.jpg' or ext == '.jpeg':
                    self.current_image.save(filepath, 'JPEG', quality=95)
                else:
                    self.current_image.save(filepath, 'PNG')
                
                messagebox.showinfo("Успех", f"Изображение сохранено как:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceGeneratorApp(root)
    root.mainloop()
