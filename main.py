import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

class ImageCanvas(tk.Canvas):
    def __init__(self, parent, img, coord_text):
        self.parent = parent
        self.coord_text = coord_text
        self.original_img = img
        self.img = img
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.rectangles = [] 
        self.rect_coords = []  
        self.undo_stack = []  
        self.redo_stack = []  
        self.scale = 1.0
        self.drawing_mode = False
        self.drawing_count = 0
        
        super().__init__(parent, width=self.img.width, height=self.img.height, scrollregion=(0, 0, self.img.width, self.img.height))
        self.create_image(0, 0, anchor='nw', image=self.tk_img)
        
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.vbar = tk.Scrollbar(parent, orient='vertical', command=self.yview)
        self.hbar = tk.Scrollbar(parent, orient='horizontal', command=self.xview)
        self.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        
        self.hbar.pack(side='bottom', fill='x')
        self.vbar.pack(side='right', fill='y')
        self.pack(side='left', expand=True, fill='both')
        
        self.bind_all("<Control-plus>", self.zoom_in)
        self.bind_all("<Control-minus>", self.zoom_out)

        self.create_buttons()

    def create_buttons(self):

        self.zoom_in_btn = tk.Button(self.parent, image=zoom_in_icon, command=self.zoom_in)
        self.zoom_in_btn.place(relx=0.05, rely=0.05, anchor='nw')

        self.zoom_out_btn = tk.Button(self.parent, image=zoom_out_icon, command=self.zoom_out)
        self.zoom_out_btn.place(relx=0.15, rely=0.05, anchor='nw')

        self.draw_btn = tk.Button(self.parent, image=draw_icon, command=self.toggle_drawing_mode)
        self.draw_btn.place(relx=0.25, rely=0.05, anchor='nw')
        
        self.undo_btn = tk.Button(self.parent, image=undo_icon, command=self.undo)
        self.undo_btn.place(relx=0.35, rely=0.05, anchor='nw')
        
        self.redo_btn = tk.Button(self.parent, image=redo_icon, command=self.redo)
        self.redo_btn.place(relx=0.45, rely=0.05, anchor='nw')

    def on_button_press(self, event):
        if self.drawing_mode:
            self.start_x = self.canvasx(event.x)
            self.start_y = self.canvasy(event.y)
            self.rect = self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')
        
    def on_mouse_drag(self, event):
        if self.drawing_mode:
            cur_x = self.canvasx(event.x)
            cur_y = self.canvasy(event.y)
            self.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        if self.drawing_mode:
            end_x = self.canvasx(event.x)
            end_y = self.canvasy(event.y)
            self.rect_coords.append((self.start_x, self.start_y, end_x, end_y))
            
            rect_left = min(self.start_x, end_x)
            rect_bottom = max(self.start_y, end_y)
            
            text_x = rect_left - 5 
            text_y = rect_bottom - 5
            
            self.drawing_count += 1
            
            text_id_border = self.create_text(text_x, text_y, text=str(self.drawing_count), font=('Arial', 12, 'bold'), anchor='sw', fill='black')
            text_id_fill = self.create_text(text_x, text_y, text=str(self.drawing_count), font=('Arial', 12, 'bold'), anchor='sw', fill='yellow')
            
            text_bbox = self.bbox(text_id_border)
            
            if text_bbox[1] < rect_bottom:
                text_y += (rect_bottom - text_bbox[1] + 5)
            
            self.coords(text_id_border, text_x, text_y)
            self.coords(text_id_fill, text_x, text_y)
            
            self.tag_lower(text_id_fill, text_id_border)
            
            self.rectangles.append((self.rect, text_id_border, text_id_fill))
            
            coords_str = f"{self.drawing_count}:({int(self.start_x)}, {int(self.start_y)}, {int(end_x)}, {int(end_y)})\n"
            print(f"Coordenadas trazadas en la imagen: {coords_str}")
            self.coord_text.config(state=tk.NORMAL)
            self.coord_text.insert(tk.END, coords_str)
            self.coord_text.see(tk.END)
            self.coord_text.config(state=tk.DISABLED)
            
            self.undo_stack.append((self.rect, text_id_border, text_id_fill, (self.start_x, self.start_y, end_x, end_y)))
            if len(self.undo_stack) > 5:
                self.undo_stack.pop(0) 
            self.redo_stack.clear()

    def zoom_in(self, event=None):
        self.scale *= 1.1
        self.update_image()

    def zoom_out(self, event=None):
        self.scale /= 1.1
        self.update_image()

    def update_image(self):
        width, height = int(self.original_img.width * self.scale), int(self.original_img.height * self.scale)
        self.img = self.original_img.resize((width, height), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.config(scrollregion=(0, 0, width, height))
        self.create_image(0, 0, anchor='nw', image=self.tk_img)

    def toggle_drawing_mode(self):
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.config(cursor="cross")
            self.coord_text.config(state=tk.NORMAL)
        else:
            self.config(cursor="arrow")
            self.coord_text.config(state=tk.DISABLED)
    
    def undo(self):
        if self.undo_stack:
            rect, text_id_border, text_id_fill, coords = self.undo_stack.pop()
            self.redo_stack.append((rect, text_id_border, text_id_fill, coords))
            if len(self.redo_stack) > 5:
                self.redo_stack.pop(0)  # Limita el historial de redo a los últimos 5 dibujos
            self.delete(rect)
            self.delete(text_id_border)
            self.delete(text_id_fill)
            self.drawing_count -= 1
            self.coord_text.config(state=tk.NORMAL)
            self.coord_text.delete('1.0', tk.END)
            for count, coords in enumerate(self.rect_coords[:self.drawing_count], start=1):
                coords_str = f"{count}:({int(coords[0])}, {int(coords[1])}, {int(coords[2])}, {int(coords[3])})\n"
                self.coord_text.insert(tk.END, coords_str)
            self.coord_text.see(tk.END)
            self.coord_text.config(state=tk.DISABLED)
            self.rectangles.pop()
            self.rect_coords.pop()

    def redo(self):
        if self.redo_stack:
            _, _, _, coords = self.redo_stack.pop()
            rect = self.create_rectangle(coords[0], coords[1], coords[2], coords[3], outline='red')
            self.drawing_count += 1

            rect_left = min(coords[0], coords[2])
            rect_bottom = max(coords[1], coords[3])

            text_x = rect_left - 5 
            text_y = rect_bottom - 5
            
            text_id_border = self.create_text(text_x, text_y, text=str(self.drawing_count), font=('Arial', 12, 'bold'), anchor='sw', fill='black')
            text_id_fill = self.create_text(text_x, text_y, text=str(self.drawing_count), font=('Arial', 12, 'bold'), anchor='sw', fill='yellow')

            text_bbox = self.bbox(text_id_border)

            if text_bbox[1] < rect_bottom:
                text_y += (rect_bottom - text_bbox[1] + 5)

            self.coords(text_id_border, text_x, text_y)
            self.coords(text_id_fill, text_x, text_y)

            self.tag_lower(text_id_fill, text_id_border)

            self.rectangles.append((rect, text_id_border, text_id_fill))
            self.rect_coords.append(coords)

            self.undo_stack.append((rect, text_id_border, text_id_fill, coords))
            if len(self.undo_stack) > 5:
                self.undo_stack.pop(0) 

            coords_str = f"{self.drawing_count}:({int(coords[0])}, {int(coords[1])}, {int(coords[2])}, {int(coords[3])})\n"
            self.coord_text.config(state=tk.NORMAL)
            self.coord_text.insert(tk.END, coords_str)
            self.coord_text.see(tk.END)
            self.coord_text.config(state=tk.DISABLED)

def open_image(img_path=None):
    global canvas, coord_text
    if not img_path:
        img_path = filedialog.askopenfilename()
    if img_path:
        img = Image.open(img_path)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        img.thumbnail((screen_width, screen_height), Image.LANCZOS)
        for widget in root.winfo_children():
            widget.destroy()
        
        coord_text_frame = tk.Frame(root)
        coord_text_frame.pack(side='bottom', fill='x', pady=10)
        coord_text = tk.Text(coord_text_frame, height=4, wrap='word')
        coord_text.pack(side='left', fill='both', expand=True)
        coord_scroll = tk.Scrollbar(coord_text_frame, command=coord_text.yview)
        coord_scroll.pack(side='right', fill='y')
        coord_text.config(yscrollcommand=coord_scroll.set)
        
        canvas = ImageCanvas(root, img, coord_text)
        root.geometry(f"{img.width}x{img.height + 100}")

def on_drop(event):
    file_path = event.data
    if os.path.isfile(file_path):
        open_image(file_path)

root = TkinterDnD.Tk()
root.title("Screenshot Tagger")
root.geometry("400x300")

label = tk.Label(root, text="Arrastra o abre una imagen", font=("Arial", 24))
label.pack(pady=20)

open_button = tk.Button(root, text="Abrir", command=open_image)
open_button.pack(pady=10)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

try:
    zoom_in_img = Image.open("screenshot_tagger/image/zoom_in_icon.png").resize((30, 30), Image.LANCZOS)
    zoom_in_icon = ImageTk.PhotoImage(zoom_in_img)
    
    zoom_out_img = Image.open("screenshot_tagger/image/zoom_out_icon.png").resize((30, 30), Image.LANCZOS)
    zoom_out_icon = ImageTk.PhotoImage(zoom_out_img)
    
    draw_img = Image.open("screenshot_tagger/image/draw_icon.png").resize((30, 30), Image.LANCZOS)
    draw_icon = ImageTk.PhotoImage(draw_img)

    redo_img = Image.open("screenshot_tagger/image/redo_icon.png").resize((30, 30), Image.LANCZOS)
    redo_icon = ImageTk.PhotoImage(redo_img)

    undo_img = Image.open("screenshot_tagger/image/undo_icon.png").resize((30, 30), Image.LANCZOS)
    undo_icon = ImageTk.PhotoImage(undo_img)

except Exception as e:
    print(f"Error loading icons: {e}")
    root.destroy()
    exit(1)

root.mainloop()
