class datencheck(object):

    """ Check all data for requirements and Errors
    """

    def __init__(self):
        # create place to store evetual error messages
        self.message = []

        # for each part of the input data initialize the check
        self.check_teachers()
        self.check_tandems()
        self.check_partners()
        self.check_mainteacher()
        self.check_curriculums()
        self.check_rooms()
        self.check_hoursperday()
        self.check_guidelines()
        self.check_unavailable_teachers()

    def check_teachers(self):
        """ Here we want to check if
        beides im model
            - no teacher has negative hours or subjects that don't exist
            In case of an error, write something in the self.message
        """
        for teacher in Teacher.objects.all():
            if Stunden < 0:
                self.message.append("Lehrer " + teacher + " hat eine negative Stundenzahl")

    def check_tandems(self):
        """ Here we want to check if
        ---
            - there should be only one main tandem entered per class, only for existing classes
            - the entered tandem should exist in the teachers list
            - only for existing classes
        """
        for tandem in Tandem.objects.all():
            if tandem not in Teacher.objects.all():
                self.message.append("Lehrer " + tandem + " existiert nicht und kann deshalb kein Tandem sein")
            if Klasse not in Klasse.objects.all():
                self.message.append("Klasse " + Klasse + " existiert nicht und kann deshalb kein Tandem haben")
        for klasse in Klasse.objects.all():
            for tandem in Tandem.objects.get(klasse):
                if "," in tandem:
                    self.message.append("Klasse " + klasse + " hat mehr als einen Haupttandemlehrer zugewiesen")

    def check_partners(self):
        """ Here we want to check if
        ---
            - the entered partners should exist in the teachers list
            - only for existing classes
        """
        for partner in Tandem.objects.all():
            if tandem not in Teacher.objects.all():
                self.message.append("Lehrer " + tandem + " existiert nicht und kann deshalb kein Tandem sein")
            if Klasse not in Klasse.objects.all():
                self.message.append("Klasse " + Klasse + " existiert nicht und kann deshalb keine Partner haben")

    def check_mainteacher(self):
        """ Here we want to check if
        ---
            - there should be only one main teacher entered per class
            - the entered teacher should exist in the teachers list
            - only for existing classes
        """

    def check_curriculums(self):
        """ Here we want to check if
            - each classes curriculum has to add up to the sum of hours per day of the class
            - curriculum only for existing classes ---
        """

    def check_rooms(self):
        """ Here we want to check if
            - Hours of the special room needed per week (from curriculum) must not exceed total free capacity of the room (eher nicht)
        """

    def check_hoursperday(self):
        """ Here we want to check if
        im model
            - no class can have more than 8 hours per day from Mo to Do and not more than 6 on Fr
            - only for existing classes
        """

    def check_guidelines(self):
        """ Here we want to check if
            - entered teacher has to exist in the list----
            - teacher has to be not blocked in the time he was entered (muss rein)
            - if teacher and subject are entered together, teacher has to be able to teach the subject (muss rein)
            - entered subject has to be part of the classes check_curriculum (muss rein)
            - entered subject has to exist----
        """
    def check_unavailable_teachers(self):
        """ Here we want to check if
            - entered teacher has to exist in the teacher list
            - teacher cannot be unavailable if the was entered in the guidlines that hour oben
        """
