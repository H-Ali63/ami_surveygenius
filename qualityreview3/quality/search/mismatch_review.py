
import io
import datetime

import xlsxwriter
from django.http import HttpResponse
from django.views.generic import TemplateView

from .models import QualityReview, QualityReviewMismatch


class MisMatch(TemplateView):
    def __init__(self):
        pass



    def get(self,request):

        print(request.GET,"<<<<<request:::")
        auditor_name = request.GET["quality_auditor_name"]
        auditor_start_date = datetime.datetime.strptime(str(request.GET["auditor_start_date"]), "%Y-%m-%d")
        auditor_end_date = datetime.datetime.strptime(str(request.GET["auditor_end_date"]), "%Y-%m-%d")
        misObj = QualityReviewMismatch.objects.filter(quality_auditor=auditor_name,auditor_date__range=[auditor_start_date,auditor_end_date])

        return self.export_mismatch(misObj,auditor_name)


    def post(self,request):
        pass



    def export_mismatch(self,misObj,auditor_name):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('output')

        row = 0
        col = 0

        # worksheet.write(0, 0, "Date")
        worksheet.write(0, 1, "Uid")
        worksheet.write(0, 2, "project_name")
        worksheet.write(0, 3, "surveyor_name")
        worksheet.write(0, 4, "fr_name")
        worksheet.write(0, 5, "interview_date")
        worksheet.write(0, 6, "interview_duration")
        worksheet.write(0, 7, "auditor_date")
        worksheet.write(0, 8, "review")

        row = row + 1
        col = 0
        for miss in misObj:
            worksheet.write(row, 1, str(miss.uid))
            worksheet.write(row, 2, str(miss.project_name))
            worksheet.write(row, 3, str(miss.surveyor_name))
            worksheet.write(row, 4, str(miss.fr_name))
            worksheet.write(row, 5, str(miss.interview_date))
            worksheet.write(row, 6, str(miss.interview_duration))
            worksheet.write(row, 7, str(miss.auditor_date))
            worksheet.write(row, 8, str(miss.review))

            row = row + 1

        workbook.close()
        output.seek(0)

        response = HttpResponse(content_type='text/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment filename=' + str(auditor_name) + '.xlsx'
        import gc
        gc.collect()

        return response
