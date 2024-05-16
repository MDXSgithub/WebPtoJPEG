# File: convert_webp_to_jpeg_gui.py

import os
import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, UnidentifiedImageError
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_webp_to_jpeg(webp_path, output_dir, overwrite=False):
    """
    Convert a .webp image to .jpeg format and save it to the specified output directory.

    Args:
        webp_path (str): Path to the .webp file to be converted.
        output_dir (str): Directory where the converted .jpeg file will be saved.
        overwrite (bool): Whether to overwrite existing files.

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    try:
        if not os.path.isfile(webp_path):
            logging.error(f"File not found: {webp_path}")
            return False

        logging.info(f"Opening image: {webp_path}")
        img = Image.open(webp_path)

        if img.format.lower() != 'webp':
            logging.error(f"File format is not .webp: {webp_path}")
            return False

        original_size = img.size
        logging.info(f"Original image size: {original_size}")

        img = img.convert("RGB")
        jpeg_filename = os.path.splitext(os.path.basename(webp_path))[0] + '.jpeg'
        jpeg_path = os.path.join(output_dir, jpeg_filename)

        if os.path.exists(jpeg_path):
            if overwrite:
                logging.info(f"Overwriting existing file: {jpeg_path}")
            else:
                logging.info(f"File already exists and overwrite is disabled: {jpeg_path}")
                return True

        img.save(jpeg_path, 'JPEG')
        logging.info(f"Saved JPEG image to: {jpeg_path}")

        converted_img = Image.open(jpeg_path)
        converted_size = converted_img.size

        if original_size == converted_size:
            logging.info(f"Size verified for {jpeg_path}: {converted_size}")
        else:
            logging.warning(f"Size mismatch for {jpeg_path}: original {original_size}, converted {converted_size}")

        return True
    except FileNotFoundError:
        logging.error(f"File not found error: {webp_path}")
    except UnidentifiedImageError:
        logging.error(f"Cannot identify image file: {webp_path}")
    except PermissionError:
        logging.error(f"Permission denied for file {webp_path}")
    except OSError as e:
        logging.error(f"OS error for file {webp_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error for {webp_path}: {e}")
    return False


class WebpToJpegConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebP to JPEG Converter")

        self.source_files = []
        self.output_dir = ''
        self.overwrite = tk.BooleanVar()
        self.cancel_flag = threading.Event()

        self.create_widgets()

    def create_widgets(self):
        # Source files selection
        self.source_label = tk.Label(self.root, text="Source Files:")
        self.source_label.grid(row=0, column=0, padx=10, pady=5)

        self.source_button = tk.Button(self.root, text="Select Files", command=self.select_source_files)
        self.source_button.grid(row=0, column=1, padx=10, pady=5)

        # Output directory selection
        self.output_label = tk.Label(self.root, text="Output Directory:")
        self.output_label.grid(row=1, column=0, padx=10, pady=5)

        self.output_button = tk.Button(self.root, text="Select Directory", command=self.select_output_directory)
        self.output_button.grid(row=1, column=1, padx=10, pady=5)

        # Overwrite option
        self.overwrite_check = tk.Checkbutton(self.root, text="Overwrite Existing Files", variable=self.overwrite)
        self.overwrite_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Convert button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.start_conversion)
        self.convert_button.grid(row=3, column=0, padx=10, pady=5)

        # Cancel button
        self.cancel_button = tk.Button(self.root, text="Cancel", command=self.cancel_conversion)
        self.cancel_button.grid(row=3, column=1, padx=10, pady=5)

        # Clear log button
        self.clear_log_button = tk.Button(self.root, text="Clear Log", command=self.clear_log)
        self.clear_log_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        # Log area
        self.log_area = scrolledtext.ScrolledText(self.root, width=50, height=10, state='disabled')
        self.log_area.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    def select_source_files(self):
        try:
            files = filedialog.askopenfilenames(filetypes=[("WebP files", "*.webp")])
            if files:
                valid_files = [f for f in files if f.lower().endswith('.webp')]
                invalid_files = set(files) - set(valid_files)
                if invalid_files:
                    messagebox.showwarning("Invalid Files",
                                           f"These files are not .webp and were skipped: {', '.join(invalid_files)}")
                self.source_files = valid_files
                self.log(f"Selected source files: {', '.join(self.source_files)}")
        except Exception as e:
            self.log(f"Error selecting files: {e}")

    def select_output_directory(self):
        try:
            directory = filedialog.askdirectory()
            if directory:
                self.output_dir = directory
                self.log(f"Selected output directory: {self.output_dir}")
        except Exception as e:
            self.log(f"Error selecting output directory: {e}")

    def start_conversion(self):
        self.cancel_flag.clear()
        self.convert_thread = threading.Thread(target=self.convert_files)
        self.convert_thread.start()

    def convert_files(self):
        if not self.source_files:
            messagebox.showerror("Error", "No source files selected.")
            self.log("Conversion failed: No source files selected.")
            return

        if not self.output_dir:
            messagebox.showerror("Error", "No output directory selected.")
            self.log("Conversion failed: No output directory selected.")
            return

        success_count = 0
        error_count = 0
        total_files = len(self.source_files)
        self.progress["maximum"] = total_files

        for index, webp_file in enumerate(self.source_files):
            if self.cancel_flag.is_set():
                self.log("Conversion cancelled by user.")
                messagebox.showinfo("Cancelled", "Conversion process was cancelled.")
                break
            try:
                if convert_webp_to_jpeg(webp_file, self.output_dir, self.overwrite.get()):
                    success_count += 1
                    self.log(f"Successfully converted: {webp_file}")
                else:
                    error_count += 1
                    self.log(f"Failed to convert: {webp_file}")
            except Exception as e:
                error_count += 1
                self.log(f"Error converting {webp_file}: {e}")

            self.progress["value"] = index + 1
            self.root.update_idletasks()

        self.log(f"Conversion completed: {success_count} successful, {error_count} errors")
        if not self.cancel_flag.is_set():
            messagebox.showinfo("Conversion Completed",
                                f"Conversion completed: {success_count} successful, {error_count} errors")

        self.auto_save_log()

    def cancel_conversion(self):
        self.cancel_flag.set()
        self.log("Cancellation requested...")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

    def auto_save_log(self):
        try:
            log_content = self.log_area.get("1.0", tk.END)
            if log_content.strip():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_filename = f"conversion_log_{timestamp}.txt"
                log_path = os.path.join(self.output_dir, log_filename)
                with open(log_path, 'w') as log_file:
                    log_file.write(log_content)
                self.log(f"Log automatically saved to {log_path}")
        except Exception as e:
            self.log(f"Error saving log: {e}")

    def clear_log(self):
        self.log_area.config(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state='disabled')
        self.log("Log cleared.")


if __name__ == "__main__":
    root = tk.Tk()
    app = WebpToJpegConverterApp(root)
    root.mainloop()
