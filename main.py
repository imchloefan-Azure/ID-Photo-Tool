import tkinter as tk
from tkinter import filedialog, messagebox
from rembg import remove
from PIL import Image, ImageOps
import io
import cv2
import numpy as np
import os

class IDPhotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ID Photo Tool")
        self.root.geometry("500x400")
        
        self.label = tk.Label(root, text="Select a photo (.jpg / .png)", font=("Arial", 14))
        self.label.pack(pady=40)
        
        self.btn_select = tk.Button(root, text="Select & Process", command=self.process_image, height=2, width=20, bg="#0078D7", fg="white")
        self.btn_select.pack(pady=10)
        
        self.status_label = tk.Label(root, text="Ready", fg="gray")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

    def process_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if not file_path:
            return
        
        self.status_label.config(text="Processing... Please wait")
        self.root.update()

        try:
            with open(file_path, "rb") as input_file:
                input_data = input_file.read()
            
            output_data = remove(input_data)
            img_rgba = Image.open(io.BytesIO(output_data)).convert("RGBA")
            
            img_rgb_cv = cv2.cvtColor(np.array(img_rgba.convert("RGB")), cv2.COLOR_RGB2BGR)
            
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(img_rgb_cv, 1.1, 5, minSize=(50, 50))

            if len(faces) == 0:
                final_img = self.simple_resize(img_rgba)
            else:
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                final_img = self.smart_crop(img_rgba, x, y, w, h)

            white_bg = Image.new("RGBA", final_img.size, "WHITE")
            white_bg.paste(final_img, (0, 0), final_img)
            final_jpg = white_bg.convert("RGB")

            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")], initialfile="id_photo.jpg")
            if save_path:
                final_jpg.save(save_path, quality=95)
                self.status_label.config(text="Success!")
                messagebox.showinfo("Success", "Photo saved successfully!")
            else:
                self.status_label.config(text="Canceled")

        except Exception as e:
            self.status_label.config(text="Error occurred")
            messagebox.showerror("Error", str(e))

    def smart_crop(self, img, fx, fy, fw, fh):
        target_w, target_h = 358, 441
        target_ratio = target_w / target_h
        
        crop_w = fw * 2.2
        crop_h = crop_w / target_ratio
        
        center_x = fx + fw / 2
        crop_y = fy - (fh * 0.8) 
        
        left = center_x - crop_w / 2
        top = crop_y
        
        # Canvas method to prevent distortion
        canvas = Image.new("RGBA", (int(crop_w), int(crop_h)), (255, 255, 255, 0))
        canvas.paste(img, (int(-left), int(-top)), img)
        
        return canvas.resize((target_w, target_h), Image.Resampling.LANCZOS)

    def simple_resize(self, img):
        return ImageOps.fit(img, (358, 441), method=Image.Resampling.LANCZOS)

if __name__ == "__main__":
    root = tk.Tk()
    app = IDPhotoApp(root)
    root.mainloop()
