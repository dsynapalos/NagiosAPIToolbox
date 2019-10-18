from docx.enum.text import *
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.table import *
import clients as CL
import main as M
import DOCXFunctions as DF


def constructDocument(index, template):
    new_document = M.DIRECTORY + '/' + template + '.docx'

    '''
    Preface
    '''

    new_document.paragraphs[0].add_run().add_picture(M.depPath + '/images/image1.png', width=Cm(10.6))
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.br(new_document, 1)

    runT = new_document.add_paragraph().add_run(CL.Clients[CL.Clients.keys()[index]])
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    runT.font.size = Pt(28)
    runT.bold = True

    runD = new_document.add_paragraph().add_run(startDate + ' - ' + endDate)
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    runD.font.size = Pt(28)
    runD.bold = True

    DF.br(new_document, 3)

    runC = new_document.add_paragraph().add_run(vr.Recipients[m.Client]['Client'])
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    runC.font.size = Pt(22)
    runC.font.name = 'Calibri Light'

    DF.br(new_document, 1)

    new_document.add_paragraph().add_run().add_picture(m.depPath + '/images/image2.png', width=Cm(3))
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.br(new_document, 1)

    new_document.add_paragraph().add_run(toDate)
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.br(new_document, 1)

    new_document.add_paragraph().add_run(vr.Category)
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    DF.br(new_document, 4)

    par = new_document.add_paragraph()
    par.add_run('Classification: ')
    runB = par.add_run(vr.Classification)
    runB.bold = True
    new_document.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    new_document.add_page_break()