from app import app, db
from flask_login import current_user
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

def generate_report(data):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/reports'
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    url = directory + current_user + ':' + str(datetime.datetime.now().time()) + '.pdf'

    ip = str(data['camInfo']['ip'])
    port = str(data['camInfo']['port'])
    cam = 'Device Under Test: ' + ip + ':' + port
    mycam = ONVIFCamera(ip, int(port), str(data['camInfo']['username']), str(data['camInfo']['password']))
    device_info = mycam.devicemgmt.GetDeviceInformation()
    manufacturer = 'Manufacturer: {}\n'.format(device_info.Manufacturer)
    model = 'Model: {}\n'.format(device_info.Model)
    firmware = 'Firmware Version: {}\n'.format(device_info.FirmwareVersion)
    serial = 'Serial Number: {}\n'.format(device_info.SerialNumber)
    hardware = 'Hardware ID: {}\n'.format(device_info.HardwareId)
    test_time = 'Report generated: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    testsResults = data['runnedTests']
    img_url = '.' + data['camInfo']['snapshot_url']
    url = 'reports/' + ip + ':' + port + '.' + str(datetime.now().strftime('%Y-%m-%d:%H:%M:%S')) + '.pdf'
    print_cam_response = data['printResponses']

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

    def define_nvt_class(cam):
        types = []
        profiles = []
        scopes = cam.devicemgmt.GetScopes()
        for item in scopes:
            groupe = re.findall(r'onvif:\/\/www\.onvif\.org\/(.*)\/(.*)', item.ScopeItem)
            if groupe[0][0] == 'type':
                types.append(str(groupe[0][1]).capitalize())
            if groupe[0][0] == 'Profile' or groupe[0][0] == 'profile':
                profiles.append(str(groupe[0][1]).capitalize())
        profiles_verdict = (", ".join(profiles)) if len(profiles) > 0 else 'Not Specified'
        return 'Device Class: {}; Profiles: {}'.format((", ".join(types)), profiles_verdict)

    Report = []

    Report.append(Paragraph('ONVIF COMPLIANCE TESTER', centered_bold))
    Report.append(Spacer(1, 12))
    Report.append(Spacer(1, 12))
    im = Image(img_url, 5 * inch, 3 * inch)
    Report.append(im)
    Report.append(Spacer(1, 12))
    Report.append(Spacer(1, 12))
    Report.append(Paragraph('REPORT DATASHEET', centered_bold))
    Report.append(Spacer(1, 12))
    Report.append(Spacer(1, 12))
    Report.append(Paragraph(cam, centered))
    Report.append(Paragraph(define_nvt_class(mycam), centered))
    Report.append(Paragraph(test_time, centered))
    Report.append(Spacer(1, 12))
    Report.append(Paragraph(manufacturer, centered))
    Report.append(Paragraph(model, centered))
    Report.append(Paragraph(serial, centered))
    Report.append(Paragraph(firmware, centered))
    Report.append(Paragraph(hardware, centered))
    logo = Image(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png'))
    Report.append(TopPadder(logo))
    Report.append(PageBreak())

    Report.append(Paragraph('<b>Table of contents</b>', centered))

    toc = TableOfContents()
    toc.levelStyles = [
        PS(fontName='Times-Bold', fontSize=14, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=10, leading=16),
        PS(fontSize=12, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=5, leading=12),
    ]
    Report.append(toc)
    Report.append(PageBreak())

    styleN = styles['Normal']
    styleN.wordWrap = 'CJK'

    def doHeading(text, sty):
        from hashlib import sha1
        bn = sha1(text + sty.name).hexdigest()
        h = Paragraph(text + '<a name="%s"/>' % bn, sty)
        h._bookmarkName = bn
        Report.append(h)

    for item in testsResults.keys():

        doHeading('{} Service Features'.format(item.capitalize()), h2)
        Report.append(Spacer(1, 12))

        data = []
        data.append(['Features', 'Description'])

        for response in testsResults[item]:
            if response['data']['result']['supported'] == False:
                report = 'Not Supported'
            else:
                try:
                    response['data']['result']['report']
                    report = response['data']['result']['report']
                except:
                    report = 'Supported'

            data.append([response['data']['result']['report_name'], report.replace('\n', '<br/>')])

        data_proccessed = [[Paragraph(cell, styleN) for cell in row] for row in data]

        table = LongTable(data_proccessed, colWidths=['30%', '70%'])
        table.setStyle(TableStyle([('BOX',(0,0),(-1,-1),1,colors.black),
                            ('GRID',(0,0),(-1,-1),0.5,colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                            ('ALIGN', (0, 0), (-1, -0), 'CENTER')]))
        Report.append(table)
        Report.append(Spacer(1, 12))

    def printResponses(testsResults):

        for item in testsResults.keys():

            doHeading('{} Service Responses'.format(item.capitalize()), h2)
            Report.append(Spacer(1, 12))

            for response in testsResults[item]:
                if response["data"]["name"]:
                    ptext = "Test:  " + str(response["data"]["name"])
                else:
                    ptext = "Test: " + "NameError"
                if response["data"]["result"]["supported"]:
                    flag = response["data"]["result"]["supported"]
                    if (flag == False):
                        sutext = str(response["data"]["name"] + ' is not supported')
                    else:
                        sutext = str(response["data"]["name"] + ' is supported')
                else:
                    sutext = str(response["data"]["result"]["report"])
                if response["data"]["result"]["response"]:
                    rtext = "Response: " + str(json.dumps(response["data"]["result"]["response"].replace('\n', '<br/>').replace('\"', '').replace(' ', '    '),
                    sort_keys=True, indent=4))
                else:
                    rtext = "Response: " + "None"
                Report.append(Paragraph(ptext, h2))
                Report.append(Spacer(1, 8))
                if (sutext is not None):
                    Report.append(Paragraph("<font size=10>%s</font>" % ptext, styles["Normal"], bulletText=u'\u25cf'))
                    Report.append(Spacer(1, 8))
                if ((response["data"]["result"]["response"]) or (len(response["data"]["result"]["response"]) != 0)):
                    Report.append(Paragraph("<font size=10>%s</font>" % rtext, styles["Normal"], bulletText=u'\u25cf'))
                    Report.append(Spacer(1, 8))
                Report.append(Spacer(1, 12))

    if(print_cam_response == True):
        Report.append(PageBreak())
        printResponses(testsResults)
        Report.append(PageBreak())

    doc = MyDocTemplate(url, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    doc.multiBuild(Report, canvasmaker=PageNumCanvas)

    return url

