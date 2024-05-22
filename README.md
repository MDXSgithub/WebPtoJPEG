A tool that can batch convert WebP image files to multiple formats including JPEG, PNG, GIF, TIFF, and PDF. This tool is ideal for users who generate images in WebP format using tools like DALLE and need to convert them to more commonly used formats at scale.

Features
Batch conversion of WebP images to JPEG, PNG, GIF, TIFF, and PDF.
Simple graphical user interface (GUI) for easy use.
Option to overwrite existing files.
Progress tracking and logging of the conversion process.
Automatic log saving.

Requirements
Python 3.x
Pillow library
Tkinter library (usually included with Python installations)

Installation
Ensure you have Python 3.x installed.
Install the required libraries using pip:
pip install pillow

Troubleshooting
PDF Conversion Issue
If you encounter an issue where the log states that PDF conversion failed but the PDF file is created, this is likely due to a false positive error message. 
The script has been to check after completion - but with this file open sometimes reports as failed. PDF asset does generate.

Common Errors
File not found: Ensure the selected files are valid WebP files.
Permission denied: Check file and directory permissions.
Unidentified image file: Ensure the selected files are correctly formatted WebP images.
