import datetime

class DataConv:


    @staticmethod
    def data_hoje():
        data_hoje = datetime.datetime.now()
        data = datetime.date(day=data_hoje.day, month=data_hoje.month, year=data_hoje.year)

        return data
