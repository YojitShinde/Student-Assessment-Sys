import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter import font, Text, Button, Frame, Tk, Checkbutton, BooleanVar
import os
# import mysql.connector
# from mysql.connector import Error
from peer_comparison import compare_files
from plagiarism_check import check_plagiarism
from ai_content import detect_ai_content
from ocr import perform_ocr, save_ocr_result
# from sentence_transformers import SentenceTransformer, util
# import re
from ans_eval import evaluate_answers
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

class StudentAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Assessment System")
        
        # Increase window size for better layout
        self.root.geometry("800x600")
        self.root.config(bg="#f4f4f9")
        
        # Store uploaded file paths
        self.assignment_file_paths = []
        self.submission_files = []
        self.answer_key_file = ""
        self.format_key_file = ""
        
        self.label_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=10, weight="normal")
        self.text_font = font.Font(family="Courier New", size=10)
        
        self.create_widgets()

    def create_widgets(self):
        # Main title
        self.title_label = tk.Label(
            self.root, 
            text="Student Assessment System",
            font=("Helvetica", 24, "bold"),
            bg="#f4f4f9",
            fg="#2c3e50"
        )
        self.title_label.pack(pady=20)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=10)

        # Create tabs
        self.answer_tab = ttk.Frame(self.notebook)
        self.assignment_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.answer_tab, text='Answer Verification')
        self.notebook.add(self.assignment_tab, text='Assignment Verification')

        # Setup both tabs
        self.setup_answer_tab()
        self.setup_assignment_tab()

    def setup_assignment_tab(self):
        # Upload frame
        upload_frame = ttk.LabelFrame(self.assignment_tab, text="Upload Files", padding=20)
        upload_frame.pack(fill='x', padx=20, pady=10)

        # File upload button
        ttk.Button(
            upload_frame,
            text="Upload Assignment Files",
            command=self.upload_assignment_file,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # OCR button
        ttk.Button(
            upload_frame,
            text="Convert to Text (OCR)",
            command=self.perform_ocr_conversion,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # Checkbox frame for verification options
        checkbox_frame = ttk.LabelFrame(self.assignment_tab, text="Verification Options", padding=10)
        checkbox_frame.pack(fill='x', padx=20, pady=10)

        # Checkboxes
        self.checkbox_var = BooleanVar()
        self.online_var = BooleanVar()
        self.ai_var = BooleanVar()

        ttk.Checkbutton(
            checkbox_frame,
            text="Compare Peer-to-Peer",
            variable=self.checkbox_var
        ).pack(side='left', padx=10)

        ttk.Checkbutton(
            checkbox_frame,
            text="Plagiarism Check",
            variable=self.online_var
        ).pack(side='left', padx=10)

        ttk.Checkbutton(
            checkbox_frame,
            text="Detect AI-Generated Content",
            variable=self.ai_var
        ).pack(side='left', padx=10)

        # Button frame for all buttons
        button_frame = ttk.Frame(self.assignment_tab)
        button_frame.pack(fill='x', padx=20, pady=10)

        # Generate and Download buttons (left side)
        ttk.Button(
            button_frame,
            text="Generate Report",
            command=self.generate_assignment_report,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Download Report",
            command=self.download_assignment_report,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # Clear Log and Reset buttons (right side)
        ttk.Button(
            button_frame,
            text="Reset",
            command=self.clear_log_screen,
            style='Accent.TButton'
        ).pack(side='right', padx=5)

        ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.erase_log,
            style='Accent.TButton'
        ).pack(side='right', padx=5)

        # Log area
        log_frame = ttk.LabelFrame(self.assignment_tab, text="Processing Log", padding=20)
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.log_area = Text(
            log_frame,
            height=10,
            width=50,
            font=self.text_font,
            wrap="word",
            bg='white',
            fg='black'
        )
        self.log_area.pack(fill='both', expand=True)

    def setup_answer_tab(self):
        # OCR frame
        ocr_frame = ttk.LabelFrame(self.answer_tab, text="OCR Conversion", padding=20)
        ocr_frame.pack(fill='x', padx=20, pady=10)

        # File upload button
        ttk.Button(
            ocr_frame,
            text="Upload Answer Files",
            command=self.upload_answer_files,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # OCR button
        ttk.Button(
            ocr_frame,
            text="Convert to Text (OCR)",
            command=self.convert_answers_ocr,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # Frame for file uploads
        upload_frame = ttk.LabelFrame(self.answer_tab, text="Upload Files", padding=20)
        upload_frame.pack(fill='x', padx=20, pady=10)

        # Student Answers upload section
        submission_frame = ttk.Frame(upload_frame)
        submission_frame.pack(fill='x', pady=5)
        
        ttk.Label(submission_frame, text="Student Answers:", font=self.label_font).pack(side='left')
        self.submission_label = ttk.Label(submission_frame, text="No files selected", font=self.text_font)
        self.submission_label.pack(side='left', padx=10)
        ttk.Button(
            submission_frame,
            text="Choose Files",
            command=self.upload_submissions,
            style='Accent.TButton'
        ).pack(side='right')

        # Answer key upload section
        key_frame = ttk.Frame(upload_frame)
        key_frame.pack(fill='x', pady=5)
        
        ttk.Label(key_frame, text="Answer Key:", font=self.label_font).pack(side='left')
        self.answer_key_label = ttk.Label(key_frame, text="No file selected", font=self.text_font)
        self.answer_key_label.pack(side='left', padx=10)
        ttk.Button(
            key_frame,
            text="Choose File",
            command=self.upload_answer_key,
            style='Accent.TButton'
        ).pack(side='right')

        # Checkbox frame for verification options
        checkbox_frame = ttk.LabelFrame(self.answer_tab, text="Verification Options", padding=10)
        checkbox_frame.pack(fill='x', padx=20, pady=10)

        # Checkboxes for answer verification
        self.answer_peer_var = BooleanVar()
        self.answer_plag_var = BooleanVar()
        self.answer_ai_var = BooleanVar()

        ttk.Checkbutton(
            checkbox_frame,
            text="Compare Peer-to-Peer",
            variable=self.answer_peer_var
        ).pack(side='left', padx=10)

        ttk.Checkbutton(
            checkbox_frame,
            text="Plagiarism Check",
            variable=self.answer_plag_var
        ).pack(side='left', padx=10)

        ttk.Checkbutton(
            checkbox_frame,
            text="Detect AI-Generated Content",
            variable=self.answer_ai_var
        ).pack(side='left', padx=10)

        # Button frame
        button_frame = ttk.Frame(self.answer_tab)
        button_frame.pack(fill='x', padx=20, pady=10)

        # Evaluate and Download buttons (left side)
        ttk.Button(
            button_frame,
            text="Evaluate Answers",
            command=self.evaluate_submission,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Download Report",
            command=self.download_answer_report,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # Reset and Clear Log buttons (right side)
        ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_answer_tab,
            style='Accent.TButton'
        ).pack(side='right', padx=5)

        ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_answer_log,
            style='Accent.TButton'
        ).pack(side='right', padx=5)

        # Report section
        report_frame = ttk.LabelFrame(self.answer_tab, text="Evaluation Report", padding=20)
        report_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.report_text = Text(
            report_frame,
            height=10,
            width=50,
            font=self.text_font,
            wrap="word",
            bg='white',
            fg='black'
        )
        self.report_text.pack(fill='both', expand=True)

    # Methods from the original UI
    def upload_assignment_file(self):
        file_paths = filedialog.askopenfilenames(title="Select Assignment Files", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

        for file_path in file_paths:
            if file_path not in self.assignment_file_paths:
                self.assignment_file_paths.append(file_path)
                self.log_area.insert(tk.END, f"Uploaded: {os.path.basename(file_path)}\n")
            else:
                self.log_area.insert(tk.END, f"File already uploaded: {os.path.basename(file_path)}\n")

        if not self.assignment_file_paths:
            self.log_area.insert(tk.END, "No files were selected.\n")

    def upload_submissions(self):
        """Handle multiple student answer uploads"""
        file_paths = filedialog.askopenfilenames(
            title="Select Student Answer Files",
            filetypes=(("Text Files", "*.txt"), ("PDF Files", "*.pdf"), ("All Files", "*.*"))
        )
        if file_paths:
            self.submission_files = list(file_paths)  # Store all paths
            num_files = len(file_paths)
            self.submission_label.config(text=f"{num_files} file{'s' if num_files > 1 else ''} selected")

    def upload_answer_key(self):
        file_path = filedialog.askopenfilename(
            filetypes=(("Text Files", "*.txt"), ("PDF Files", "*.pdf"), ("All Files", "*.*"))
        )
        if file_path:
            self.answer_key_file = file_path
            self.answer_key_label.config(text=os.path.basename(file_path))

    # Existing methods from previous implementation
    def generate_assignment_report(self):
        if not self.assignment_file_paths:
            self.log_area.insert(tk.END, "Error: No assignment files uploaded.\n")
            return
    
        self.log_area.insert(tk.END, "\nGenerating new report...\n")
    
        try:
            # Peer-to-peer comparison
            if self.checkbox_var.get():
                if len(self.assignment_file_paths) < 2:
                    self.log_area.insert(tk.END, "\nError: At least two files are required for peer-to-peer comparison.\n")
                else:
                    results = compare_files(self.assignment_file_paths)
                    self.log_area.insert(tk.END, "\n=== Peer-to-Peer Comparison Results ===\n")
                
                    for files, similarity in results.items():
                        if len(files) == 2:
                            file1, file2 = files
                            self.log_area.insert(tk.END, f"Comparing:\n - File 1: {os.path.basename(file1)}\n")
                            self.log_area.insert(tk.END, f" - File 2: {os.path.basename(file2)}\n")
                            self.log_area.insert(tk.END, f" - Similarity: {similarity * 100:.2f}%\n")
                        else:
                            self.log_area.insert(tk.END, "Unexpected result structure in peer comparison.\n")
        
            # Plagiarism check
            if self.online_var.get():
                plagiarism_results = check_plagiarism(self.assignment_file_paths)
                self.log_area.insert(tk.END, "\n=== Plagiarism Check Results ===\n")
                for file_path, result in plagiarism_results.items():
                    self.log_area.insert(tk.END, f"\n{os.path.basename(file_path)}:\n{result}\n")
        
            # AI content detection
            if self.ai_var.get():
                ai_results = detect_ai_content(self.assignment_file_paths)
                self.log_area.insert(tk.END, "\n=== AI Content Detection Results ===\n")
                for file_path, result in ai_results.items():
                    filename = os.path.basename(file_path)
                    if result['status'] == 'success':
                        self.log_area.insert(tk.END, f"\n{filename}:\n")
                        self.log_area.insert(tk.END, f"- AI Content: {result['ai_percentage']}%\n")
                        self.log_area.insert(tk.END, f"- Content Length: {result['content_length']} characters\n")
                    else:
                        self.log_area.insert(tk.END, f"\n{filename}: Error - {result['error_message']}\n")
    
        except Exception as e:
            self.log_area.insert(tk.END, f"Error: An issue occurred during the report generation. Details: {e}\n")


    def evaluate_submission(self):
        """Evaluate all student answers against the answer key"""
        if not self.submission_files or not self.answer_key_file:
            messagebox.showerror("Error", "Please upload both student answers and answer key!")
            return

        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "Evaluation Results:\n" + "="*50 + "\n\n")

        # Basic answer evaluation
        for student_file in self.submission_files:
            result = evaluate_answers(student_file, self.answer_key_file)
            
            filename = os.path.basename(student_file)
            if result["status"] == "success":
                self.report_text.insert(tk.END, f"File: {filename}\n")
                self.report_text.insert(tk.END, f"Score: {result['overall_score']:.1f}%\n")
                self.report_text.insert(tk.END, "-"*50 + "\n\n")
            else:
                self.report_text.insert(tk.END, f"Error evaluating {filename}: {result['message']}\n\n")

        # Additional verifications
        if self.answer_peer_var.get():
            if len(self.submission_files) < 2:
                self.report_text.insert(tk.END, "\nError: At least two files needed for peer comparison.\n")
            else:
                results = compare_files(self.submission_files)
                self.report_text.insert(tk.END, "\n=== Peer-to-Peer Comparison ===\n")
                for files, similarity in results.items():
                    file1, file2 = files
                    self.report_text.insert(tk.END, 
                        f"{os.path.basename(file1)} vs {os.path.basename(file2)}: {similarity*100:.1f}%\n")

        if self.answer_plag_var.get():
            self.report_text.insert(tk.END, "\n=== Plagiarism Check ===\n")
            for file in self.submission_files:
                result = check_plagiarism([file])
                self.report_text.insert(tk.END, f"\n{os.path.basename(file)}:\n{result[file]}\n")

        if self.answer_ai_var.get():
            self.report_text.insert(tk.END, "\n=== AI Content Detection ===\n")
            for file in self.submission_files:
                result = detect_ai_content([file])
                filename = os.path.basename(file)
                if result[file]['status'] == 'success':
                    self.report_text.insert(tk.END, 
                        f"\n{filename}:\nAI Content: {result[file]['ai_percentage']}%\n")
                else:
                    self.report_text.insert(tk.END, 
                        f"\n{filename}: Error - {result[file]['error_message']}\n")

    def clear_log_screen(self):
        self.log_area.delete(1.0, tk.END)
        self.assignment_file_paths = []
        self.checkbox_var.set(False)
        self.log_area.insert(tk.END, "App resetted...\n")

    def erase_log(self):
        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, "Log cleared...\n")

    def perform_ocr_conversion(self):
        if not self.assignment_file_paths:
            self.log_area.insert(tk.END, "Error: No files uploaded for OCR conversion.\n")
            return
        
        self.log_area.insert(tk.END, "\nStarting OCR conversion...\n")
        
        for file_path in self.assignment_file_paths:
            if not file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                self.log_area.insert(tk.END, f"Skipping {os.path.basename(file_path)}: Not an image file\n")
                continue
            
            filename = os.path.basename(file_path)
            self.log_area.insert(tk.END, f"\nProcessing: {filename}\n")
            
            text, error = perform_ocr(file_path, lambda msg: self.log_area.insert(tk.END, msg))
            
            if error:
                self.log_area.insert(tk.END, f"Error processing {filename}: {error}\n")
                continue
            
            if text:
                output_path = os.path.splitext(file_path)[0] + "_ocr.txt"
                if save_ocr_result(text, output_path):
                    self.log_area.insert(tk.END, f"OCR result saved to: {os.path.basename(output_path)}\n")
                else:
                    self.log_area.insert(tk.END, f"Error saving OCR result for {filename}\n")
            else:
                self.log_area.insert(tk.END, f"No text extracted from {filename}\n")
        
        self.log_area.insert(tk.END, "\nOCR conversion completed!\n")

    def clear_answer_log(self):
        """Clear the answer evaluation log"""
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "Log cleared...\n")

    def reset_answer_tab(self):
        """Reset the answer verification tab"""
        self.report_text.delete(1.0, tk.END)
        self.submission_files = []
        self.answer_key_file = ""
        self.answer_files_for_ocr = []  # Clear OCR files
        self.submission_label.config(text="No files selected")
        self.answer_key_label.config(text="No file selected")
        self.answer_peer_var.set(False)
        self.answer_plag_var.set(False)
        self.answer_ai_var.set(False)
        self.report_text.insert(tk.END, "Answer verification resetted...\n")

    def generate_pdf_report(self, content, module_name):
        """Generate PDF report from content"""
        try:
            # Create downloads directory if it doesn't exist
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{module_name}_report_{timestamp}.pdf"
            filepath = os.path.join(downloads_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom style for content
            content_style = ParagraphStyle(
                'CustomStyle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=10
            )
            
            # Create elements list
            elements = []
            
            # Add title
            title = Paragraph(f"Student Assessment Report - {module_name}", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add timestamp
            date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            elements.append(date_text)
            elements.append(Spacer(1, 20))
            
            # Add content
            for line in content.split('\n'):
                if line.strip():
                    p = Paragraph(line, content_style)
                    elements.append(p)
                    elements.append(Spacer(1, 5))
            
            # Build PDF
            doc.build(elements)
            
            return filepath
            
        except Exception as e:
            return None

    def download_answer_report(self):
        """Download Answer Verification report"""
        content = self.report_text.get(1.0, tk.END)
        if content.strip():
            filepath = self.generate_pdf_report(content, "Answer_Verification")
            if filepath:
                messagebox.showinfo("Success", f"Report downloaded to:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to generate report")
        else:
            messagebox.showwarning("Warning", "No content to download")

    def download_assignment_report(self):
        """Download Assignment Verification report"""
        content = self.log_area.get(1.0, tk.END)
        if content.strip():
            filepath = self.generate_pdf_report(content, "Assignment_Verification")
            if filepath:
                messagebox.showinfo("Success", f"Report downloaded to:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to generate report")
        else:
            messagebox.showwarning("Warning", "No content to download")

    def upload_answer_files(self):
        """Upload files for OCR conversion"""
        file_paths = filedialog.askopenfilenames(
            title="Select Answer Files for OCR", 
            filetypes=[
                ("Image files", "*.jpg;*.jpeg;*.png;*.bmp"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )

        if file_paths:
            self.answer_files_for_ocr = list(file_paths)
            num_files = len(file_paths)
            self.report_text.insert(tk.END, f"Uploaded {num_files} file(s) for OCR conversion\n")

    def convert_answers_ocr(self):
        """Convert uploaded answer files to text using OCR"""
        if not hasattr(self, 'answer_files_for_ocr') or not self.answer_files_for_ocr:
            messagebox.showerror("Error", "Please upload files for OCR conversion first!")
            return
        
        self.report_text.insert(tk.END, "\nStarting OCR conversion...\n")
        
        for file_path in self.answer_files_for_ocr:
            if not file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.pdf')):
                self.report_text.insert(tk.END, f"Skipping {os.path.basename(file_path)}: Unsupported file format\n")
                continue
            
            filename = os.path.basename(file_path)
            self.report_text.insert(tk.END, f"\nProcessing: {filename}\n")
            
            text, error = perform_ocr(file_path, lambda msg: self.report_text.insert(tk.END, msg))
            
            if error:
                self.report_text.insert(tk.END, f"Error processing {filename}: {error}\n")
                continue
            
            if text:
                output_path = os.path.splitext(file_path)[0] + "_ocr.txt"
                if save_ocr_result(text, output_path):
                    self.report_text.insert(tk.END, f"OCR result saved to: {os.path.basename(output_path)}\n")
                else:
                    self.report_text.insert(tk.END, f"Error saving OCR result for {filename}\n")
            else:
                self.report_text.insert(tk.END, f"No text extracted from {filename}\n")
        
        self.report_text.insert(tk.END, "\nOCR conversion completed!\n")

# Configure style
def configure_styles():
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Helvetica', 10))
    return style

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    style = configure_styles()
    app = StudentAssessmentApp(root)
    root.mainloop()