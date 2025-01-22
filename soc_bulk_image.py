# MIT License
#
# Copyright (c) 2025 UG_4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class BulkImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Image Cropper")
        self.root.geometry("800x600")

        self.images = []
        self.cropped_images = []
        self.canvas_list = []
        self.rectangles = []
        self.scaling_factors = []

        self.upload_button = tk.Button(root, text="Upload Images", command=self.upload_images)
        self.upload_button.pack(pady=20)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=10)

        self.canvas_canvas = tk.Canvas(self.canvas_frame)
        self.canvas_scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas_canvas.yview)
        self.canvas_canvas.config(yscrollcommand=self.canvas_scrollbar.set)

        self.canvas_scrollbar.pack(side="right", fill="y")
        self.canvas_canvas.pack(side="left", fill="both", expand=True)
        self.scrollable_frame = tk.Frame(self.canvas_canvas)
        self.canvas_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.crop_button = tk.Button(root, text="Crop Images", command=self.crop_images, state=tk.DISABLED)
        self.crop_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Save Cropped Images", command=self.save_images, state=tk.DISABLED)
        self.save_button.pack(pady=10)

    def upload_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_paths:
            return

        for canvas in self.canvas_list:
            canvas.destroy()
        self.canvas_list.clear()
        self.rectangles.clear()
        self.scaling_factors.clear()

        self.images = [Image.open(path) for path in file_paths]

        max_width = 300

        for img in self.images:
            width_percentage = max_width / float(img.width)
            new_height = int((float(img.height) * float(width_percentage)))
            img_resized = img.resize((max_width, new_height))

            scaling_factor = img.width / max_width

            self.scaling_factors.append(scaling_factor)

            canvas = tk.Canvas(self.scrollable_frame, width=max_width, height=new_height)
            canvas.pack(pady=10)

            canvas_image = ImageTk.PhotoImage(img_resized)
            canvas.create_image(0, 0, anchor=tk.NW, image=canvas_image)
            canvas.image = canvas_image

            self.canvas_list.append(canvas)
            self.rectangles.append(None)

            canvas.bind("<ButtonPress-1>", lambda event, idx=len(self.canvas_list) - 1: self.on_mouse_press(event, idx))
            canvas.bind("<B1-Motion>", lambda event, idx=len(self.canvas_list) - 1: self.on_mouse_drag(event, idx))
            canvas.bind("<ButtonRelease-1>", lambda event, idx=len(self.canvas_list) - 1: self.on_mouse_release(event, idx))

        self.scrollable_frame.update_idletasks()
        self.canvas_canvas.config(scrollregion=self.canvas_canvas.bbox("all"))

        self.crop_button.config(state=tk.NORMAL)

    def on_mouse_press(self, event, idx):
        self.rectangles[idx] = (event.x, event.y, event.x, event.y)
        self.redraw_rectangle(idx)

    def on_mouse_drag(self, event, idx):
        if self.rectangles[idx]:
            start_x, start_y, _, _ = self.rectangles[idx]
            self.rectangles[idx] = (start_x, start_y, event.x, event.y)
            self.redraw_rectangle(idx)

    def on_mouse_release(self, event, idx):
        if self.rectangles[idx]:
            start_x, start_y, end_x, end_y = self.rectangles[idx]

            start_x = min(max(start_x, 0), self.images[idx].width)
            start_y = min(max(start_y, 0), self.images[idx].height)
            end_x = min(max(end_x, 0), self.images[idx].width)
            end_y = min(max(end_y, 0), self.images[idx].height)

            start_x = int(start_x * self.scaling_factors[idx])
            start_y = int(start_y * self.scaling_factors[idx])
            end_x = int(end_x * self.scaling_factors[idx])
            end_y = int(end_y * self.scaling_factors[idx])

            self.rectangles[idx] = (start_x, start_y, end_x, end_y)
            self.redraw_rectangle(idx)

    def redraw_rectangle(self, idx):
        canvas = self.canvas_list[idx]
        canvas.delete("rect")

        start_x, start_y, end_x, end_y = self.rectangles[idx]

        canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="red", tag="rect")

    def crop_images(self):
        self.cropped_images = []

        for idx, img in enumerate(self.images):
            start_x, start_y, end_x, end_y = self.rectangles[idx]

            if None in (start_x, start_y, end_x, end_y):
                messagebox.showerror("Error", "Please define a crop area for all images.")
                return

            cropped_img = img.crop((start_x, start_y, end_x, end_y))

            cropped_img.show()

            self.cropped_images.append(cropped_img)

        messagebox.showinfo("Success", "Images cropped successfully!")
        self.save_button.config(state=tk.NORMAL)

    def save_images(self):
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        for i, img in enumerate(self.cropped_images):
            try:
                img_path = os.path.join(output_dir, f"cropped_image_{i + 1}.png")
                img.save(img_path, "PNG")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save cropped image {i}. Error: {e}")
                return

        messagebox.showinfo("Success", f"Cropped images have been saved to {output_dir}.")

root = tk.Tk()
app = BulkImageCropper(root)
root.mainloop()