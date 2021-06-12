import os
import random
from typing import List
import sqlite3
from lxml.etree import Element
from campus_api import CampusApi


class Course:
    def __init__(self):
        self.id = None
        self.title = None
        self.semester = None
        self.start_date = None
        self.end_date = None
        self.semester_hours = None
        self.type = None  # e.g. Exercises
        self.language = None
        self.ilias_link = None
        # self.registration_info = None
        # root.xpath(".//...") --> registrationAvailable OR registrationInfoStatus

        self.description = None
        self.objective = None
        self.prerequisite = None
        self.further_info = None

        self.institution = None
        self.lecturers = []  # as list

        # dummy slot values, binary values
        self.ml = None
        self.engineering = None
        self.politics = None
        self.literature = None
        self.culture = None

    def fill_slot_values(self, slot_values: List[str]):
        self.ml = slot_values[0]
        self.engineering = slot_values[1]
        self.politics = slot_values[2]
        self.literature = slot_values[3]
        self.culture = slot_values[4]

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'semester': self.semester,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'semester_hours': self.semester_hours,
            'type': self.type,
            'language': self.language,
            'ilias_link': self.ilias_link,
            'description': self.description,
            'objective': self.objective,
            'prerequisite': self.prerequisite,
            'extra_info': self.further_info,
            'institution': self.institution,
            'lecturers': ', '.join(self.lecturers),
            'machine_learning': self.ml,
            'engineering': self.engineering,
            'politics': self.politics,
            'literature': self.literature,
            'culture': self.culture
        }


def get_course_info(xml: Element) -> Course:
    course = Course()
    for element in xml.xpath('resource/content/cpCourseDetailDto')[0].getchildren():
        if element.tag == 'cpCourseDto':
            for child in element:
                if child.tag == 'id':
                    course.id = child.text

                elif child.tag == 'semesterDto':
                    course.start_date = child.xpath('startOfAcademicSemester/value')[0].text
                    course.end_date = child.xpath('endOfAcademicSemester/value')[0].text
                    course.semester = child.xpath("semesterDesignation")[0].xpath(".//translation[@lang='en']")[0].text
                    if not course.semester:  # if no info in lang@en tag
                        course.semester = child.xpath("semesterDesignation")[0].xpath(
                            ".//translation[@lang='de']")[0].text

                elif child.tag == 'courseTitle':
                    course.title = child.xpath(".//translation[@lang='en']")[0].text
                    if not course.title:
                        course.title = child.xpath(".//translation[@lang='de']")[0].text

                elif child.tag == 'organisationResponsibleDto':
                    course.institution = child.xpath(".//translation[@lang='en']")[0].text
                    if not course.institution:
                        course.institution = child.xpath(".//translation[@lang='de']")[0].text

                elif child.tag == 'courseTypeDto':
                    course.type = child.xpath(".//courseTypeName")[0].xpath(
                        ".//translation[@lang='en']")[0].text
                    if not course.type:
                        course.type = child.xpath(".//courseTypeName")[0].xpath(
                            ".//translation[@lang='de']")[0].text

                elif child.tag == 'courseLanguageDtos':
                    course.language = child.xpath(".//translation[@lang='en']")[0].text
                    if not course.language:
                        course.language = child.xpath(".//translation[@lang='de']")[0].text

                elif child.tag == 'lectureships':
                    first_name = child.xpath(".//firstName")[0].text
                    last_name = child.xpath(".//lastName")[0].text
                    course.lecturers.append(first_name + ' ' + last_name)

                elif child.tag == 'courseNormConfigs':
                    course.semester_hours = child.xpath("value")[0].text

        elif element.tag == 'cpCourseDescriptionDto':
            for child in element:
                if child.tag == 'courseContent':
                    course.description = child.xpath(".//translation[@lang='en']")[0].text
                    if not course.description:
                        course.description = child.xpath(".//translation[@lang='de']")[0].text

                elif child.tag == 'previousKnowledge':
                    course.prerequisite = child.xpath(".//translation[@lang='en']")[0].text
                    if not course.prerequisite:
                        course.prerequisite = child.xpath(".//translation[@lang='de']")[0].text

                elif child.tag == 'courseObjective':
                    course.objective = child.xpath(".//translation[@lang='en']")[0].text
                    if not course.objective:
                        course.objective = child.xpath(".//translation[@lang='de']")[0].text

                elif child.tag == 'additionalInformation':
                    if child.xpath(".//recommendedLiterature"):
                        course.further_info = child.xpath(".//recommendedLiterature")[0].xpath(
                            ".//translation[@lang='en']")[0].text
                        if not course.further_info:
                            course.further_info = child.xpath(".//recommendedLiterature")[0].xpath(
                                ".//translation[@lang='de']")[0].text

                    elif child.xpath(".//courseUrlDtoList"):
                        if 'ILIAS' in child.xpath(".//courseUrlDtoList/name/value")[0].text:
                            course.ilias_link = child.xpath(".//courseUrlDtoList/url")[0].text

    # now insert dummy slot values into course
    slots = []
    for i in range(5):
        n = random.randint(0, 1)
        slots.append('true' if n == 1 else 'false')
    course.fill_slot_values(slots)
    return course


def create_table():
    """
    Create table in the SQL database
    :return: None
    """
    sql = """CREATE TABLE IF NOT EXISTS campus_courses ( id INTEGER PRIMARY KEY,
                                                        title TEXT NOT NULL,
                                                        lecturers TEXT,
                                                        semester TEXT,
                                                        start_date TEXT,
                                                        end_date TEXT,
                                                        semester_hours TEXT,
                                                        type TEXT,
                                                        language TEXT,
                                                        ilias_link TEXT,
                                                        description TEXT,
                                                        objective TEXT,
                                                        prerequisite TEXT,
                                                        institution TEXT,
                                                        extra_info TEXT,
                                                        machine_learning TEXT,
                                                        engineering TEXT,
                                                        politics TEXT,
                                                        literature TEXT,
                                                        culture TEXT
                                                        )"""

    cursor.execute(sql)
    connection.commit()  # commit changes


def insert_data_to_db(course: Course):
    columns = []  # list of column names with values to insert into the table
    info = ()  # a set of corresponding values of the fields

    course = course.to_dict()
    for key, value in course.items():
        if not value:  # if no info, then fill in with 'na'
            value = 'na'

        columns.append(key)
        info += (value,)

    data = ['?'] * len(info)  # placeholders in the sql string
    sql = 'INSERT OR IGNORE INTO campus_courses (' + ','.join(columns) + ') VALUES (' + ','.join(data) + ')'
    cursor.execute(sql, info)  # finally add values into the table
    connection.commit()  # commit the changes


if __name__ == "__main__":

    # create an SQL database
    # db_path = '../resources/databases/campus_courses.db'
    db_path = '../resources/databases/dummy_courses.db'
    connection = sqlite3.connect(os.path.join(os.getcwd(), db_path))  # establish a connection
    cursor = connection.cursor()  # create the cursor object
    create_table()

    # retrieve courses from the api in batch
    api = CampusApi(30)
    batch = api.get_next_batch_of_courses()
    courses_count = 0

    while batch is not None:
        courses_count += len(batch)
        print('Processed {} courses'.format(courses_count))
        for course_xml in batch:
            # turn course xml into Course object and insert into the sql db
            insert_data_to_db(get_course_info(xml=course_xml))
        # batch = api.get_next_batch_of_courses()
        batch = None
    print('Done with {} courses'.format(courses_count))
