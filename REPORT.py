from fpdf import FPDF
from datetime import date

# Sample data
patient_name = "XYZ"
age = 35
contact_no = "+923325525605"
paragraph_text1 = (
    "Based on the imaging findings, there are no significant abnormal findings identified on this brain MRI exam. The overall brain anatomy is normal"
)
paragraph_text2 = (
    "Based on the imaging findings, there are significant abnormal findings identified on this brain MRI exam. The overall brain anatomy is abnormal"
)
date = date.today()
doctor_name = "Dr. XYZ"

# Create a PDF report class inheriting from FPDF
class Report(FPDF):
    def header(self):
        # Set up the header
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Patient Report", ln=True, align="C")

    def footer(self):
        # Set up the footer
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        # Set up the chapter title
        self.set_font("Arial", "B", 12)
        self.ln(10)
        self.cell(0, 10, title, ln=True)

    def chapter_body(self, body):
        # Set up the chapter body
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def patient_details(self, patient_id, age, contact_no):
        # Set up the patient details section
        self.chapter_title("Patient Details")
        self.chapter_body(f"Patient ID: {patient_id}")
        #self.chapter_body(f"Age: {age}")
        #self.chapter_body(f"Contact No: {contact_no}")

    def paragraph_section(self, text):
        # Set up the paragraph section
        self.chapter_title("Report Details")
        self.chapter_body(text)
        
    def findings_section(self, image_names):
        # Set up the paragraph section
        self.chapter_title("Findings")
        self.chapter_body(f"MRI with Abnormality: {image_names}")

    def signature_section(self, date, doctor_name):
        # Set up the signature section
        self.ln(20)
        self.cell(0, 10, f"Date: {date}", ln=True)
        self.cell(0, 10, f"Doctor's Signature: {doctor_name}", ln=True)


def generate_report(image_name, current_dir):
    patient_id = ""
    i = len(current_dir)
    while i > 0:
        if current_dir[i-1] == "/":
            break
        #s2 = ''.join(("P",s2))
        patient_id = ''.join( ( str(current_dir[i-1]), str(patient_id) ) )
        i-=1
    ''' Create a new PDF report '''
    pdf = Report()
    pdf.add_page()

    ''' Add the patient details '''
    pdf.patient_details(patient_id, age, contact_no)

    ''' Add the paragraph section '''
    if image_name:
        paragraph_text2 = (
            "Based on the imaging findings, there are significant abnormal findings identified in "+str(len(image_name))+" slices of this brain MRI exam from "
            +str(image_name[0])+" till "+str(image_name[-1])+". The overall brain anatomy is abnormal"
        )
        pdf.paragraph_section(paragraph_text2)
    else:
        paragraph_text1 = (
            "Based on the imaging findings, there are no significant abnormal findings identified on this brain MRI exam. The overall brain anatomy is normal"
        )
        pdf.paragraph_section(paragraph_text1)
    
    '''Add findings section'''
    pdf.findings_section(image_name)

    ''' Add the signature section '''
    pdf.signature_section(date, doctor_name)

    ''' Save the PDF report '''
    pdf.output("Reports/patient_"+str(patient_id)+"_report_"+str(date)+".pdf")