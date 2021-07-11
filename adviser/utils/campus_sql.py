import os
import re
import pickle
from typing import List
from tqdm import tqdm

import sqlite3
from lxml.etree import Element
from campus_api import CampusApi
from nltk.corpus import stopwords
from collections import Counter


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
        self.topics = []
        self.values = []

    def topics_to_dict(self) -> dict:
        mapping = {}
        for topic, value in zip(self.topics, self.values):
            mapping[topic] = value
        return mapping

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'semester': self.semester,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'semester_hours': self.semester_hours,
            'type': self.type,
            'language_taught': self.language,
            'ilias_link': self.ilias_link,
            'description': self.description,
            'objective': self.objective,
            'prerequisite': self.prerequisite,
            'extra_info': self.further_info,
            'institution': self.institution,
            'lecturers': ', and '.join(self.lecturers),
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
    return course


def get_topics_for_course(course: Course, topics: list) -> list:
    values = []
    for topic in topics:
        values.append('true') if check_topic_exists(course, topic) else values.append('false')
    assert len(topics) == len(values)
    return values


def check_topic_exists(course: Course, topic: str) -> bool:
    search_fields = [course.title, course.description, course.objective, course.prerequisite,
                     course.further_info, course.institution]
    for field in search_fields:
        if field and re.search(topic.replace('_', ' ').lower(), field.lower()):
            return True
    return False


def create_table(topics: list):
    sql = """CREATE TABLE IF NOT EXISTS campus_courses ( id INTEGER PRIMARY KEY,
                                                        title TEXT NOT NULL,
                                                        lecturers TEXT,
                                                        semester TEXT,
                                                        start_date TEXT,
                                                        end_date TEXT,
                                                        semester_hours TEXT,
                                                        type TEXT,
                                                        language_taught TEXT,
                                                        ilias_link TEXT,
                                                        description TEXT,
                                                        objective TEXT,
                                                        prerequisite TEXT,
                                                        institution TEXT,
                                                        extra_info TEXT
                                                        )"""

    cursor.execute(sql)
    connection.commit()  # commit changes

    # add topic columns into table
    topic_count = 0
    for topic in topics:
        try:
            cursor.execute('''ALTER TABLE campus_courses ADD COLUMN ''' + topic.lower() + ''' TEXT''')
            connection.commit()  # commit changes
            topic_count += 1
        except sqlite3.OperationalError as e:
            print('Topic ERROR:', topic.lower())
            print("count", topic_count)
            print(e)
            pass


def insert_course_to_db(course: Course) -> int:
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
    return cursor.lastrowid


def insert_topics_to_course(course, topics, course_id):
    values = get_topics_for_course(course, topics)
    course.topics = topics
    course.values = values

    mapping = course.topics_to_dict()
    for topic, value in mapping.items():
        sql = 'UPDATE campus_courses SET ' + topic + ' = ? WHERE id = ?'
        cursor.execute(sql, (value, course_id))
        connection.commit()


def insert_data_to_db(courses: List[Course], topics):
    for course in tqdm(courses):
        course_id = insert_course_to_db(course)
        insert_topics_to_course(course, topics, course_id)


def remove_stopwords(title: str, en_sw, de_sw) -> list:
    title = re.sub("[!#$%&\\'()*+,-./:;<=>?@^_`{|}~]", '', title)
    title = [word for word in title.strip().split() if word.lower() not in en_sw]
    return [word for word in title if word.lower() not in de_sw]


def remove_numbers(text) -> str:
    return re.sub('\\d+', '', text).strip()


def remove_non_words(text) -> str:
    return re.sub(u'^\\W+|\\W+$', '', text).strip()


def clean_ngrams(ngram: str, en_sw, de_sw) -> list:
    ngram = remove_numbers(ngram)
    ngram = remove_non_words(ngram)
    return remove_stopwords(ngram, en_sw, de_sw)


def get_ngrams(title: list) -> Counter:
    count = Counter()
    count.update(title)   # add unigrams
    count.update(['_'.join(title[i:i + 2]) for i in range(0, len(title) - 1)])  # add bigrams
    count.update(['_'.join(title[i:i + 3]) for i in range(0, len(title) - 2)])  # add bigrams
    return count


def write_topics(topics: Counter):
    out = [topic + "\t" + str(count) for topic, count in topics.most_common()]
    with open(path_to_topic_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(out))


def save_courses(courses: List[Course]):
    with open(path_to_courses_file, 'wb') as file:
        pickle.dump(courses, file)


def load_courses() -> List[Course]:
    print('Loading courses .....')
    with open(path_to_courses_file, 'rb') as file:
        data = pickle.load(file)
    return data


def load_topics() -> list:
    topics = []
    sql_keys = ['foreign']
    with open(path_to_topic_file, 'r', encoding='utf-8') as file:
        for line in file:
            if len(line.strip().split('\t')) == 2:
                ngrams, count = line.strip().split('\t')
                if ngrams.lower() not in sql_keys:
                    topics.append(ngrams.strip().lower())
    return list(set(topics))  # remove duplicates


def download_courses_and_topics():
    # retrieve courses from the api in batch
    print('Access to api for downloading courses ....')
    api = CampusApi(30)
    batch = api.get_next_batch_of_courses()

    topics = Counter()
    en_sw = stopwords.words('english')
    de_sw = stopwords.words('german')

    courses: List[Course] = []
    courses_count = 0

    while batch is not None:
        courses_count += len(batch)
        print('Processed {} courses'.format(courses_count))
        for course_xml in batch:
            # turn course xml into Course object and insert into the sql db
            course = get_course_info(xml=course_xml)
            topics.update(get_ngrams(clean_ngrams(course.title, en_sw, de_sw)))  # from title
            topics.update(get_ngrams(clean_ngrams(course.institution, en_sw, de_sw)))  # from institution
            courses.append(course)

            # insert_data_to_db(get_course_info(xml=course_xml))
        batch = api.get_next_batch_of_courses()

    if not os.path.exists(path_to_topic_file):
        write_topics(topics)
    save_courses(courses)
    print('Done with {} courses'.format(courses_count))
    return courses


if __name__ == "__main__":

    # db_path = '../resources/databases/campus_courses.db'
    db_path = '../resources/databases/campus_courses.db'
    path_to_courses_file = '../resources/databases/courses.pk'
    path_to_topic_file = '../resources/databases/topics_350.txt'

    all_courses = load_courses() if os.path.exists(path_to_courses_file) else download_courses_and_topics()
    final_topics = load_topics()  # get topics
    print("Total topics: ", len(final_topics))

    # SQD database management
    connection = sqlite3.connect(os.path.join(os.getcwd(), db_path))  # establish a connection
    cursor = connection.cursor()  # create the cursor object

    print('Create and insert data into table...')
    create_table(final_topics)
    insert_data_to_db(all_courses, final_topics)
