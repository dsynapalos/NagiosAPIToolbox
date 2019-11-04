import os
import re
from datetime import datetime, timedelta
import win32com.client
import docx
from docx import Document
from docx.enum.dml import *
from docx.enum.table import *
from docx.enum.text import *
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, RGBColor
import pandas as pd
import numpy as np
import main as m
import matplotlib.pyplot as plt

from docx.enum.table import *


#Edited from https://stackoverflow.com/questions/32992457/update-the-toc-table-of-content-of-ms-word-docx-documents-with-python
def update_toc(docx_file):
    word = win32com.client.DispatchEx("Word.Application")
    try:
        doc = word.Documents.Open(docx_file)
        doc.TablesOfContents(1).Update()
        doc.Close(SaveChanges=True)
    finally:
        word.Quit()
        del word

#Edited from https://stackoverflow.com/questions/47666642/adding-an-hyperlink-in-msword-by-using-python-docx
def add_hyperlink(paragraph, text, url):
    # This gets access to the document.xml.rels file and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )

    # Create a w:r element and a new w:rPr element
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')

    # Join all the xml elements together add add the required text to the w:r element
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)

    # Create a new Run object and add the hyperlink into it
    r = paragraph.add_run()
    r._r.append(hyperlink)

    # A workaround for the lack of a hyperlink style (doesn't go purple after using the link)
    # Delete this if using a template that has the hyperlink style in it
    r.font.color.theme_color = MSO_THEME_COLOR_INDEX.HYPERLINK
    r.font.underline = True

    return hyperlink

#Edited from https://stackoverflow.com/questions/55572685/how-set-direction-of-table-of-content-in-docx-files-uisng-python-docx
def create_Toc(cr_document):

    cont = cr_document.add_heading('Table of Contents', 8)
    cont.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    paragraph = cr_document.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')  # creates a new element
    fldChar.set(qn('w:fldCharType'), 'begin')  # sets attribute on element
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')  # sets attribute on element
    instrText.text = 'TOC \\o "1-4" \\h \\z \\u'  # change 1-4 depending on heading levels you need

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:t')
    fldChar3.text = "Right-click to update field."
    fldChar2.append(fldChar3)

    fldChar4 = OxmlElement('w:fldChar')
    fldChar4.set(qn('w:fldCharType'), 'end')

    r_element = run._r
    r_element.append(fldChar)
    r_element.append(instrText)
    r_element.append(fldChar2)
    r_element.append(fldChar4)

    cr_document.add_page_break()


def line_brake(doc, n):
    for i in range(0, n):
        doc.add_paragraph()