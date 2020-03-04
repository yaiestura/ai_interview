from app import app, db
from app.models import User, UserData, Statistics
import io
import os
import re
import datetime
from datetime import datetime
import json
import sys
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image, Paragraph, Spacer, SimpleDocTemplate, Table, TableStyle, LongTable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle as PS
from reportlab.platypus.flowables import TopPadder
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.units import cm, mm, inch
import PIL

class PageNumCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):

        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):

        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):

        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):

        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 10)
        self.drawRightString(195 * mm, 10 * mm, page)

class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        apply(SimpleDocTemplate.__init__, (self, filename), kw)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            if style == 'Heading2':
                self.notify('TOCEntry', (1, text, self.page))

def generate_report(username):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{username}/reports'
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    url = directory + '/report_' + username  + '.pdf'


    styles = getSampleStyleSheet()
    centered = PS(name='centered',
        fontSize=14,
        leading=16,
        alignment=1,
        spaceAfter=10)

    bold = PS(
        name='bold',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16)

    centered_bold = PS(name='centered_bold',
        fontSize=14,
        fontName='Helvetica-Bold',
        leading=16,
        alignment=1,
        spaceAfter=10)

    h2 = PS(name='Heading2',
        fontSize=12,
        leading=14)


    Report = []
    
    # Title

    logo = Image('app/utils/hse_logo.jpeg', 1 * inch, 1 * inch)
    Report.append(logo)
    Report.append(Spacer(1, 12))
    Report.append(Spacer(1, 12))
    Report.append(Paragraph('AI Interview Tool, HSE', centered_bold))
    Report.append(Spacer(1, 12))
    Report.append(Spacer(1, 12))
    Report.append(Paragraph(f'Report for user: {username}', centered_bold))
    Report.append(Spacer(1, 12))
    Report.append(Spacer(1, 12))

    # im = Image(img_url, 5 * inch, 3 * inch)
    # Report.append(im)
    # Report.append(Spacer(1, 12))
    # Report.append(Spacer(1, 12))
    curr_time = str(datetime.now()).split(".")[0]
    Report.append(Paragraph(f'Time of Report creation: {curr_time}', centered))


    Report.append(PageBreak())

    styleN = styles['Normal']
    styleN.wordWrap = 'CJK'

    # Resume
    Report.append(Paragraph('Resume Analysis', centered_bold))

    Report.append(PageBreak())

    # CV
    Report.append(Paragraph('Motivational Letter Analysis', centered_bold))


    # Audio
    Report.append(Paragraph('Audio Analysis', centered_bold))


    Report.append(PageBreak())

    # Statistics
    Report.append(Paragraph('Statistics Analysis', centered_bold))

    # content_exists = True if os.path.exists("app/resume/res_data.txt") else False
    # score_exists = True if os.path.exists("app/resume/res_score.txt") else False
    # if content_exists:
    #     with open("app/resume/res_data.txt", "r") as f:
    #         content = f.read()
    # if score_exists:
    #     with open("app/resume/res_score.txt", "r") as f:
    #         score = f.read()

    # data_proccessed = [[Paragraph(cell, styleN) for cell in row] for row in data]

    # table = LongTable(data_proccessed, colWidths=['30%', '70%'])
    # table.setStyle(TableStyle([('BOX',(0,0),(-1,-1),1,colors.black),
    #                     ('GRID',(0,0),(-1,-1),0.5,colors.black),
    #                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #                     ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
    #                     ('ALIGN', (0, 0), (-1, -0), 'CENTER')]))
    # Report.append(table)
    # Report.append(Spacer(1, 12))

    doc = SimpleDocTemplate(url)
    doc.multiBuild(Report, canvasmaker=PageNumCanvas)

    return url

