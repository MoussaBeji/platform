class defaultEntitys():
    """Return list of the default entitys"""

    def __init__(self):
        pass

    def GetEntitys(self):
        list =[]
        number = dict()
        number['name'] = "NUMBER"
        number['value_set'] = []
        list.append(number)

        TIME = dict()
        TIME['name'] = "TIME"
        TIME['value_set'] = []
        list.append(TIME)

        DATE = dict()
        DATE['name'] = "DATE"
        DATE['value_set'] = []
        list.append(DATE)

        COUNTRY = dict()
        COUNTRY['name'] = "COUNTRY"
        COUNTRY['value_set'] = []
        list.append(COUNTRY)

        EMAIL = dict()
        EMAIL['name'] = "EMAIL"
        EMAIL['value_set'] = []
        list.append(EMAIL)

        PHONE = dict()
        PHONE['name'] = "PHONE"
        PHONE['value_set'] = []
        list.append(PHONE)

        URL = dict()
        URL['name'] = "URL"
        URL['value_set'] = []
        list.append(URL)

        ZIPCODE = dict()
        ZIPCODE['name'] = "ZIPCODE"
        ZIPCODE['value_set'] = []
        list.append(ZIPCODE)

        PERSON = dict()
        PERSON['name'] = "PERSON"
        PERSON['value_set'] = []
        list.append(PERSON)

        AGE = dict()
        AGE['name'] = "AGE"
        AGE['value_set'] = []
        list.append(AGE)

        DURATION = dict()
        DURATION['name'] = "DURATION"
        DURATION['value_set'] = []
        list.append(DURATION)

        PERCENT = dict()
        PERCENT['name'] = "PERCENT"
        PERCENT['value_set'] = []
        list.append(PERCENT)

        WHEIGHT = dict()
        WHEIGHT['name'] = "WHEIGHT"
        WHEIGHT['value_set'] = []
        list.append(WHEIGHT)

        LENGH = dict()
        LENGH['name'] = "LENGH"
        LENGH['value_set'] = []
        list.append(LENGH)




        return list