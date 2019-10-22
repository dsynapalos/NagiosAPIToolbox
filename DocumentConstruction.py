from docx import Document, opc
from docx.enum.text import *
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.table import *
import clients as CL
import main as M
from datetime import datetime
import DOCXFunctions as DF


def constructDocument(index, dates, template):
    start_day, start_month, end_day, end_month = [item for item in dates]
    new_document = Document(template)

    '''
    Preface
    '''

    new_document.add_paragraph().add_run().add_picture(CL.company_logo, width=Cm(12.7))
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.line_brake(new_document, 1)

    new_document.add_paragraph().add_run(CL.report_type).font.name = 'Cambria'
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.line_brake(new_document, 2)

    new_document.add_paragraph().add_run(CL.Clients[index]['TITLE']).font.name = 'Cambria'
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.line_brake(new_document, 2)

    new_document.add_paragraph().add_run(str(datetime.now().strftime('%d/%m/%Y'))).font.name = 'Cambria'
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.line_brake(new_document, 2)

    new_document.add_paragraph().add_run(CL.report_desc).font.name = 'Cambria'
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.line_brake(new_document, 6)

    new_document.add_paragraph().add_run(CL.classify).font.name = 'Cambria'
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    new_document.add_page_break()

    '''
    Contacts
    '''



    new_document.save('demo.docx')

