import itertools
import json
import pandas as pd
import pendulum
import re
import requests
import xmltodict  # for troubleshooting

from collections import OrderedDict
from furl import furl
from xml.dom.minidom import parseString, Node


Audience_list = ["Audience", "Doctoral", "Masters", "Undergraduate"]

Category_list = [
    "Assessment_Evaluation",
    "Early_Childhood",
    "ELL_Bilingual",
    "Global_Perspectives",
    "Higher_Ed",
    "History",
    "Interdisciplinary",
    "K12",
    "Language_Arts_Education",
    "Math_Education",
    "Methods",
    "Out-of-School_Learning",
    "Philosophy",
    "Policy_Economics",
    "Psychology",
    "Race_Culture_Class",
    "Science_Education",
    "Service_Learning",
    "Sociology_Anthropology",
    "Special_Education",
    "Teaching",
    "Technology",
]

Program_list = [
    "CARDCOURSES",
    "CTE-PhD",
    "DAPS",
    "DAPS-Core_Courses",
    "DAPS-Courses_by_DAPS_Faculty",
    "EDS",
    "EDS_Required",
    "EDS_Statistics_Intro",
    "EDS_Statistics_Adv",
    "EDS_NLP_Intro",
    "EDS_NLP_Adv",
    "EDS_Networks_Intro",
    "EDS_Networks_Adv",
    "EDS_Causal_Intro",
    "EDS_Causal_Adv",
    "EDS_Measurement_Intro",
    "EDS_Measurement_Adv",
    "EDS_EFSLANG",
    "EDS_LearningAnalytics_Intro",
    "EDS_LearningAnalytics_Adv",
    "ICE-MA",
    "ICE-MA-Recommended",
    "ICE-PhD-SHIPS",
    "IEPA-MA",
    "IEPA-MA-Recommended",
    "IEPA-Policy",
    "ICE_IEPA-Required_Courses",
    "ICE_IEPA-Research_Methods",
    "ICE_IEPA-306_Series",
    "LDT",
    "LDT-Design_of_Learning_Experiences",
    "LDT-Design_Process",
    "LDT-Evaluation_and_Research_Methods",
    "LDT-Learning_Content",
    "LDT-Learning_Theories",
    "LDT-Perspectives_on_Technology",
    "LDT-Recommended_Electives",
    "LSTD",
    "MA_JD",
    "MA_JD-Cross-Creditable_Courses",
    "MA_JD-Inquiry",
    "MA_JD-History",
    "MA_JD-Organizations",
    "MA_JD-Policy",
    "MA_MBA",
    "MA_MBA-Cross-listed_Courses",
    "MA_MBA-Education_Data_Science",
    "MA_MBA-Ed_Tech",
    "MA_MBA-Global_Ed",
    "MA_MBA-POLS",
    "MA_MPP-Standard",
    "MA_MPP-Quant_Focus_I",
    "MA_MPP-Quant_Focus_II",
    "MA_MPP-High_End_Quant",
    "MA_MPP-Math_Light",
    "MA_MPP-Other_Methods",
    "POLS_Seminar",
    "POLS-Standard",
    "POLS-Quant_Focus_I",
    "POLS-Quant_Focus_II",
    "POLS-High_End_Quant",
    "POLS-Math_Light",
    "POLS-Other_Methods",
    "POLS-Policy_Requirement",
    "POLS-Organization_Requirement",
    "RILE",
    "RILE-Issues_in_race_in_education",
    "RILE-Linguistic_diversity_and_identity",
    "RILE-Studies_of_inequality_and_schooling",
    "SHIPS",
    "SHIPS-Higher_Ed",
    "STEP",
    "STEP-Elementary",
    "STEP-Secondary",
    "UG_Honors",
    "UG_Minor",
    "UG_Minor-Educational_Technology",
    "UG_Minor-Education_Research_and_Policy",
    "UG_Minor-Foundational",
    "UG_Minor-Teaching_and_Learning",
    "UG_Minor-Core",
]


# Python program to illustrate the intersection
# of two lists
# https://www.geeksforgeeks.org/python-intersection-two-lists/
# https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/
def intersection(lst1, lst2):
    # Use of hybrid method
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    res = list(OrderedDict.fromkeys(lst3))
    return res


def set_id_attribute(parent, attribute_name="id"):
    if parent.nodeType == Node.ELEMENT_NODE:
        if parent.hasAttribute(attribute_name):
            parent.setIdAttribute(attribute_name)
    for child in parent.childNodes:
        set_id_attribute(child, attribute_name)


def remove_whitespace(node):
    if node.nodeType == Node.TEXT_NODE:
        if node.nodeValue.strip() == "":
            node.nodeValue = ""
    for child in node.childNodes:
        remove_whitespace(child)


# https://codefather.tech/blog/check-if-python-string-contains-number/
# https://stackoverflow.com/questions/5577501/how-to-tell-if-string-starts-with-a-number-with-python
def containsNumber(value):
    return any([char.isdigit() for char in value])


def pretty_print_time(time):
    dt = pendulum.from_format(time, "HH:mm:ss A")
    new = dt.format("h:mm A")
    time_list = new.split()
    ampm = time_list[1].lower()
    corrected = time_list[0] + ampm
    return corrected


def military_time(time):
    dt = pendulum.from_format(time, "HH:mm:ss A")
    new = dt.format("HHmm")
    return new


# https://stackoverflow.com/questions/63370387/python3-sort-array-into-specific-order
def day_priority(element):
    if element == "Monday":
        return -7
    if element == "Tuesday":
        return -6
    if element == "Wednesday":
        return -5
    if element == "Thursday":
        return -4
    if element == "Friday":
        return -3
    if element == "Saturday":
        return -2
    if element == "Sunday":
        return -1
    return ord(element)


def quarter_priority(element):
    if "Autumn" in element:
        return -5
    if "Winter" in element:
        return -4
    if "Spring" in element:
        return -3
    if "Summer" in element:
        return -2
    return ord(element)


def quarter_priority_nested(element):
    season = element["term"]
    if element["sectionNumber"]:
        sectionNumber = int(element["sectionNumber"])
    else:
        sectionNumber = 0
    if "Autumn" in season:
        s = -500
    if "Winter" in season:
        s = -400
    if "Spring" in season:
        s = -300
    if "Summer" in season:
        s = -200
    ordering = s + sectionNumber
    return ordering


def single_course_dictionary_course_response(course, request_url_string):
    code = days = description = endTime = format_of_course = grading = location = (
        section_units
    ) = startTime = subject = title = unitsMin = unitsMax = year = ""

    days_list_global = []
    instructors_list = []
    instructors_list_global = []
    tags_list = []
    term_list = []
    tempSectionsList = []

    code = course.getElementsByTagName("code")[0].firstChild.nodeValue
    subject = course.getElementsByTagName("subject")[0].firstChild.nodeValue

    year = course.getElementsByTagName("year")[0].firstChild.nodeValue
    title = course.getElementsByTagName("title")[0].firstChild.nodeValue
    # description = course.getElementsByTagName("description")[0].firstChild.nodeValue
    if course.getElementsByTagName("description")[0]:
        if course.getElementsByTagName("description")[0].firstChild:
            description = course.getElementsByTagName("description")[
                0
            ].firstChild.nodeValue
        else:
            description = ""
    else:
        description = ""

    grading = course.getElementsByTagName("grading")[0].firstChild.nodeValue
    # print("*")
    # print()
    # print("Subject: " + subject)
    # print("code: " + code)
    # print("title: " + title)
    # print("year: " + year)
    # print("grading: " + grading)
    # print("*")
    # print("description: " + description)
    # print("*")
    # print()
    sectionsList = course.getElementsByTagName("sections")
    for sectionsNode in sectionsList:
        if sectionsNode.nodeType == Node.ELEMENT_NODE:
            sections = sectionsNode
            sList = sections.getElementsByTagName("section")

            for sNode in sList:
                tempSection = {}
                if sNode.nodeType == Node.ELEMENT_NODE:
                    # reset the instructors list
                    instructors_list = []

                    section = sNode

                    section_subject = section.getElementsByTagName("subject")[
                        0
                    ].firstChild.nodeValue
                    tempSection["subject"] = section_subject

                    section_code = section.getElementsByTagName("code")[
                        0
                    ].firstChild.nodeValue
                    tempSection["code"] = section_code

                    term = section.getElementsByTagName("term")[0].firstChild.nodeValue

                    term_list.append(term)
                    tempSection["term"] = term

                    format_of_course = section.getElementsByTagName("component")[
                        0
                    ].firstChild.nodeValue
                    tempSection["format_of_course"] = format_of_course

                    sectionNumber = section.getElementsByTagName("sectionNumber")[
                        0
                    ].firstChild.nodeValue
                    tempSection["sectionNumber"] = sectionNumber

                    if section.getElementsByTagName("units")[0].firstChild:

                        section_units = section.getElementsByTagName("units")[
                            0
                        ].firstChild.nodeValue
                        maxmin_units = section_units.split("-")
                        if len(maxmin_units) == 1:
                            unitsMin = maxmin_units[0]
                            unitsMax = maxmin_units[0]
                        else:
                            unitsMin = maxmin_units[0]
                            unitsMax = maxmin_units[1]
                        tempSection["section_units"] = section_units
                        tempSection["unitsMin"] = unitsMin
                        tempSection["unitsMax"] = unitsMax

                    # print("term: " + term)
                    # print("format_of_course: " + format_of_course)
                    # print("section_units: " + section_units)
                    schedulesList = section.getElementsByTagName("schedules")
                    for schedulesNode in schedulesList:
                        # print(" *  scheduleNode  * ")
                        if schedulesNode.nodeType == Node.ELEMENT_NODE:
                            schedules = schedulesNode
                            schedList = schedules.getElementsByTagName("schedule")

                            for schedNode in schedList:
                                if schedNode.nodeType == Node.ELEMENT_NODE:
                                    schedule = schedNode
                                    if section.getElementsByTagName("days")[
                                        0
                                    ].firstChild:
                                        days = section.getElementsByTagName("days")[
                                            0
                                        ].firstChild.nodeValue

                                    if section.getElementsByTagName("startTime")[
                                        0
                                    ].firstChild:
                                        startTime = section.getElementsByTagName(
                                            "startTime"
                                        )[0].firstChild.nodeValue

                                        startTime = pretty_print_time(startTime)
                                        tempSection["startTime"] = startTime

                                    if section.getElementsByTagName("endTime")[
                                        0
                                    ].firstChild:
                                        endTime = section.getElementsByTagName(
                                            "endTime"
                                        )[0].firstChild.nodeValue
                                        endTime = pretty_print_time(endTime)
                                        tempSection["endTime"] = endTime

                                    if section.getElementsByTagName("location")[
                                        0
                                    ].firstChild:
                                        location = section.getElementsByTagName(
                                            "location"
                                        )[0].firstChild.nodeValue
                                        tempSection["location"] = location

                                    # remove carriage returns and tabs, Monday \t\n Wednesday case somewhere...
                                    if days:
                                        days = days.strip()
                                    # print(startTime)
                                    # print(endTime)
                                    # https://www.digitalocean.com/community/tutorials/python-remove-spaces-from-string
                                    s = days
                                    days_split_list = s.split()
                                    days = " ".join(days_split_list)
                                    # print(len(days))
                                    # print(days)
                                    # print(location)
                                    tempSection["days"] = days
                                    days_list_global.append(days_split_list)

                                    instructorsList = (
                                        # section.getElementsByTagName(
                                        schedule.getElementsByTagName("instructors")
                                    )
                                    for instructorsNode in instructorsList:
                                        # print(" *  instructorsNode  * ")
                                        if (
                                            instructorsNode.nodeType
                                            == Node.ELEMENT_NODE
                                        ):
                                            instructors = instructorsNode
                                            instructorList = (
                                                instructors.getElementsByTagName(
                                                    "instructor"
                                                )
                                            )

                                            for instructorNode in instructorList:
                                                if (
                                                    instructorNode.nodeType
                                                    == Node.ELEMENT_NODE
                                                ):
                                                    instructor = instructorNode
                                                    # instructor_name = (
                                                    #    instructor.getElementsByTagName(
                                                    #        "name"
                                                    #    )[0].firstChild.nodeValue
                                                    # )
                                                    first_name = (
                                                        instructor.getElementsByTagName(
                                                            "firstName"
                                                        )[0].firstChild.nodeValue
                                                    )
                                                    last_name = (
                                                        instructor.getElementsByTagName(
                                                            "lastName"
                                                        )[0].firstChild.nodeValue
                                                    )
                                                    instructor_name = f"{first_name.title()} {last_name.title()}"
                                                    # print("instructor_name")
                                                    instructors_list.append(
                                                        instructor_name
                                                    )
                                                    instructors_list_global.append(
                                                        instructor_name
                                                    )

                                    # print(instructors_list)
                                    instructors_string = ""
                                    if len(instructors_list) > 0:
                                        temp_instructors_list = []
                                        for item in instructors_list:
                                            if item not in temp_instructors_list:
                                                temp_instructors_list.append(item)
                                        instructors_string = "; ".join(
                                            str(e) for e in temp_instructors_list
                                        )
                                        tempSection["instructor_name"] = (
                                            instructors_string
                                        )

                    # https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
                    if "section_units" in tempSection:
                        tempSectionsList.append(tempSection)
                    # print(tempSectionsList)
            temp_term_list = []
            for item in term_list:
                if item not in temp_term_list:
                    temp_term_list.append(item)
            term = sorted(temp_term_list, key=quarter_priority)

    # print()
    tagsList = course.getElementsByTagName("tags")
    for tagsNode in tagsList:
        if tagsNode.nodeType == Node.ELEMENT_NODE:
            tags = tagsNode
            tagList = tags.getElementsByTagName("tag")

            for tagNode in tagList:
                if tagNode.nodeType == Node.ELEMENT_NODE:
                    tag = tagNode
                    name = tag.getElementsByTagName("name")[0].firstChild.nodeValue
                    organization = tag.getElementsByTagName("organization")[
                        0
                    ].firstChild.nodeValue
                    if organization == "EDUC":
                        # print(name)
                        tags_list.append(name)
                    elif organization == "CARDCOURSES" and name == "educ":
                        tags_list.append(organization)

    if len(instructors_list_global) > 0:
        # remove duplicates
        # https://www.digitalocean.com/community/tutorials/get-unique-values-from-a-list-in-python
        temp_instructors_list = []
        for item in instructors_list_global:
            if item not in temp_instructors_list:
                temp_instructors_list.append(item)
        # instructors_string = "; ".join(str(e) for e in temp_instructors_list)
        temp_instructors_list.sort()
        instructors_list_global = temp_instructors_list

    tags_string = ""
    resultant_program_list = []
    resultant_category_list = []
    resultant_audience_list = []
    if len(tags_list) > 0:
        # print(tags_list)
        tags_string = "; ".join(str(e) for e in tags_list)
        resultant_program_list = intersection(tags_list, Program_list)
        resultant_category_list = intersection(tags_list, Category_list)
        resultant_audience_list = intersection(tags_list, Audience_list)
        resultant_program_list.sort()
        resultant_category_list.sort()
        resultant_audience_list.sort(reverse=True)
        # print(tags_string)

    if len(days_list_global) > 0:

        temp_days_list = []
        for item in days_list_global:
            if item not in temp_days_list:
                temp_days_list.append(item)

        # https://stackabuse.com/python-how-to-flatten-list-of-lists/
        flat_list = list(itertools.chain(*temp_days_list))
        unique_list = list(set(flat_list))
        days_list_global = sorted(unique_list, key=day_priority)

    if len(tempSectionsList) > 0:
        tempSectionsList = sorted(
            tempSectionsList,
            key=lambda x: quarter_priority_nested(x),
            reverse=False,
        )

    request_url_temp = furl(request_url_string)
    request_url_temp.remove(["totalSubjectSearch"]).url
    request_url_temp.remove(["q"]).url
    request_url_temp.add({"q": subject + code}).url
    request_url_string_new = str(request_url_temp)

    explorecourses_url = request_url_string_new.replace("&view=xml-20200810", "catalog")
    if explorecourses_url and subject == "EDUC":
        coursediscovery_url = f"https://coursediscovery.gse.stanford.edu/node/courses/{subject.lower()}-{code.lower()}-2024-2025"
    else:
        coursediscovery_url = ""

    dictionary = {
        "subject": subject,
        "code": code,
        "title": title,
        "year": year,
        "grading": grading,
        "description": description,
        "term": term,
        "format_of_course": format_of_course,
        "section_units": section_units,
        "unitsMin": unitsMin,
        "unitsMax": unitsMax,
        "days": days_list_global,
        "instructors": instructors_list_global,
        "tags": tags_string,
        "sections": tempSectionsList,
        "explorecourses_url": explorecourses_url,
        "explorecourses_xml": request_url_string_new,
        "coursediscovery_url": coursediscovery_url,
        "section_count": len(tempSectionsList),
        "course_offered": len(tempSectionsList) > 0,
        "course_valid": type(len(tempSectionsList)) == int,
    }

    dictionary["program"] = []
    dictionary["category"] = []
    dictionary["audience"] = []
    if resultant_program_list:
        dictionary["program"] = resultant_program_list
    if resultant_category_list:
        dictionary["category"] = resultant_category_list
    if resultant_audience_list:
        dictionary["audience"] = resultant_audience_list

    return dictionary


def concise_course_dictionary_course_response(course, request_url_string):
    code = days = description = endTime = format_of_course = grading = location = (
        section_units
    ) = startTime = subject = title = unitsMin = unitsMax = year = ""

    course_times_list_global = []
    days_list_global = []
    instructors_list = []
    instructors_list_global = []
    tags_list = []
    term_list = []
    tempSectionsList = []
    units_range = []

    code = course.getElementsByTagName("code")[0].firstChild.nodeValue
    subject = course.getElementsByTagName("subject")[0].firstChild.nodeValue

    year = course.getElementsByTagName("year")[0].firstChild.nodeValue
    title = course.getElementsByTagName("title")[0].firstChild.nodeValue
    # description = course.getElementsByTagName("description")[0].firstChild.nodeValue
    if course.getElementsByTagName("description")[0]:
        if course.getElementsByTagName("description")[0].firstChild:
            description = course.getElementsByTagName("description")[
                0
            ].firstChild.nodeValue
        else:
            description = ""
    else:
        description = ""

    grading = course.getElementsByTagName("grading")[0].firstChild.nodeValue
    # print("*")
    # print()
    # print("Subject: " + subject)
    # print("code: " + code)
    # print("title: " + title)
    # print("year: " + year)
    # print("grading: " + grading)
    # print("*")
    # print("description: " + description)
    # print("*")
    # print()
    sectionsList = course.getElementsByTagName("sections")
    for sectionsNode in sectionsList:
        if sectionsNode.nodeType == Node.ELEMENT_NODE:
            sections = sectionsNode
            sList = sections.getElementsByTagName("section")

            for sNode in sList:
                tempSection = {}
                if sNode.nodeType == Node.ELEMENT_NODE:
                    # reset the instructors list
                    instructors_list = []

                    section = sNode

                    section_subject = section.getElementsByTagName("subject")[
                        0
                    ].firstChild.nodeValue
                    tempSection["subject"] = section_subject

                    section_code = section.getElementsByTagName("code")[
                        0
                    ].firstChild.nodeValue
                    tempSection["code"] = section_code

                    term = section.getElementsByTagName("term")[0].firstChild.nodeValue

                    term_list.append(term)
                    tempSection["term"] = term

                    format_of_course = section.getElementsByTagName("component")[
                        0
                    ].firstChild.nodeValue
                    tempSection["format_of_course"] = format_of_course

                    sectionNumber = section.getElementsByTagName("sectionNumber")[
                        0
                    ].firstChild.nodeValue
                    tempSection["sectionNumber"] = sectionNumber

                    if section.getElementsByTagName("units")[0].firstChild:

                        section_units = section.getElementsByTagName("units")[
                            0
                        ].firstChild.nodeValue
                        maxmin_units = section_units.split("-")
                        if len(maxmin_units) == 1:
                            unitsMin = maxmin_units[0]
                            unitsMax = maxmin_units[0]
                            units_range = [int(unitsMin)]
                        else:
                            unitsMin = maxmin_units[0]
                            unitsMax = maxmin_units[1]
                            # https://www.geeksforgeeks.org/python-create-list-of-numbers-with-given-range/
                            units_range = list(range(int(unitsMin), int(unitsMax) + 1))
                        tempSection["section_units"] = section_units
                        tempSection["unitsMin"] = unitsMin
                        tempSection["unitsMax"] = unitsMax

                    # print("term: " + term)
                    # print("format_of_course: " + format_of_course)
                    # print("section_units: " + section_units)
                    schedulesList = section.getElementsByTagName("schedules")
                    for schedulesNode in schedulesList:
                        # print(" *  scheduleNode  * ")
                        if schedulesNode.nodeType == Node.ELEMENT_NODE:
                            schedules = schedulesNode
                            schedList = schedules.getElementsByTagName("schedule")

                            for schedNode in schedList:
                                if schedNode.nodeType == Node.ELEMENT_NODE:
                                    schedule = schedNode
                                    if section.getElementsByTagName("days")[
                                        0
                                    ].firstChild:
                                        days = section.getElementsByTagName("days")[
                                            0
                                        ].firstChild.nodeValue

                                    if section.getElementsByTagName("startTime")[
                                        0
                                    ].firstChild:
                                        startTime = section.getElementsByTagName(
                                            "startTime"
                                        )[0].firstChild.nodeValue

                                        startTimeMil = military_time(startTime)
                                        startTime = pretty_print_time(startTime)
                                        tempSection["startTime"] = startTime

                                    if section.getElementsByTagName("endTime")[
                                        0
                                    ].firstChild:
                                        endTime = section.getElementsByTagName(
                                            "endTime"
                                        )[0].firstChild.nodeValue
                                        endTimeMil = military_time(endTime)
                                        endTime = pretty_print_time(endTime)
                                        tempSection["endTime"] = endTime

                                        # https://stackoverflow.com/questions/39298054/generating-15-minute-time-interval-array-in-python
                                        # 10 minute intervals
                                        # https://j0qnt6ghyd.execute-api.us-west-2.amazonaws.com/dev/course_total_subject_search/acct
                                        # https://j0qnt6ghyd.execute-api.us-west-2.amazonaws.com/dev/course/acct313
                                        # 1:15 - 2:35, levels out to 1:20 to 2:30
                                        course_times_list = (
                                            pd.DataFrame(
                                                columns=["NULL"],
                                                index=pd.date_range(
                                                    "2016-09-01T00:00:00Z",
                                                    "2016-09-01T23:59:00Z",
                                                    freq="10min",
                                                ),
                                            )
                                            .between_time(startTimeMil, endTimeMil)
                                            .index.strftime("%H%M")
                                            .tolist()
                                        )
                                        # https://www.geeksforgeeks.org/python-converting-all-strings-in-list-to-integers/
                                        course_times_list = list(
                                            map(int, course_times_list)
                                        )

                                        course_times_list_global.append(
                                            course_times_list
                                        )

                                    if section.getElementsByTagName("location")[
                                        0
                                    ].firstChild:
                                        location = section.getElementsByTagName(
                                            "location"
                                        )[0].firstChild.nodeValue
                                        tempSection["location"] = location

                                    # remove carriage returns and tabs, Monday \t\n Wednesday case somewhere...
                                    if days:
                                        days = days.strip()
                                    # print(startTime)
                                    # print(endTime)
                                    # https://www.digitalocean.com/community/tutorials/python-remove-spaces-from-string
                                    s = days
                                    days_split_list = s.split()
                                    days = " ".join(days_split_list)
                                    # print(len(days))
                                    # print(days)
                                    # print(location)
                                    tempSection["days"] = days
                                    days_list_global.append(days_split_list)

                                    instructorsList = (
                                        # section.getElementsByTagName(
                                        schedule.getElementsByTagName("instructors")
                                    )
                                    for instructorsNode in instructorsList:
                                        # print(" *  instructorsNode  * ")
                                        if (
                                            instructorsNode.nodeType
                                            == Node.ELEMENT_NODE
                                        ):
                                            instructors = instructorsNode
                                            instructorList = (
                                                instructors.getElementsByTagName(
                                                    "instructor"
                                                )
                                            )

                                            for instructorNode in instructorList:
                                                if (
                                                    instructorNode.nodeType
                                                    == Node.ELEMENT_NODE
                                                ):
                                                    instructor = instructorNode
                                                    # instructor_name = (
                                                    #    instructor.getElementsByTagName(
                                                    #        "name"
                                                    #    )[0].firstChild.nodeValue
                                                    # )
                                                    first_name = (
                                                        instructor.getElementsByTagName(
                                                            "firstName"
                                                        )[0].firstChild.nodeValue
                                                    )
                                                    last_name = (
                                                        instructor.getElementsByTagName(
                                                            "lastName"
                                                        )[0].firstChild.nodeValue
                                                    )
                                                    instructor_name = f"{first_name.title()} {last_name.title()}"
                                                    # print("instructor_name")
                                                    instructors_list.append(
                                                        instructor_name
                                                    )
                                                    instructors_list_global.append(
                                                        instructor_name
                                                    )

                                    # print(instructors_list)
                                    instructors_string = ""
                                    if len(instructors_list) > 0:
                                        temp_instructors_list = []
                                        for item in instructors_list:
                                            if item not in temp_instructors_list:
                                                temp_instructors_list.append(item)
                                        instructors_string = "; ".join(
                                            str(e) for e in temp_instructors_list
                                        )
                                        tempSection["instructor_name"] = (
                                            instructors_string
                                        )

                    # https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
                    if "section_units" in tempSection:
                        tempSectionsList.append(tempSection)
                    # print(tempSectionsList)
            temp_term_list = []
            for item in term_list:
                if item not in temp_term_list:
                    temp_term_list.append(item)
            term = sorted(temp_term_list, key=quarter_priority)

            # https://stackoverflow.com/questions/34214139/python-keep-only-letters-in-string
            term_exclusive = list(
                map(lambda string: "".join(filter(str.isalpha, string)), term)
            )

    # print()
    tagsList = course.getElementsByTagName("tags")
    for tagsNode in tagsList:
        if tagsNode.nodeType == Node.ELEMENT_NODE:
            tags = tagsNode
            tagList = tags.getElementsByTagName("tag")

            for tagNode in tagList:
                if tagNode.nodeType == Node.ELEMENT_NODE:
                    tag = tagNode
                    name = tag.getElementsByTagName("name")[0].firstChild.nodeValue
                    organization = tag.getElementsByTagName("organization")[
                        0
                    ].firstChild.nodeValue
                    if organization == "EDUC":
                        # print(name)
                        tags_list.append(name)
                    elif organization == "CARDCOURSES" and name == "educ":
                        tags_list.append(organization)

    if len(instructors_list_global) > 0:
        # remove duplicates
        # https://www.digitalocean.com/community/tutorials/get-unique-values-from-a-list-in-python
        temp_instructors_list = []
        for item in instructors_list_global:
            if item not in temp_instructors_list:
                temp_instructors_list.append(item)
        temp_instructors_list.sort()
        # instructors_string = "; ".join(str(e) for e in temp_instructors_list)
        instructors_list_global = temp_instructors_list

    tags_string = ""
    resultant_program_list = []
    resultant_category_list = []
    resultant_audience_list = []
    if len(tags_list) > 0:
        # print(tags_list)
        tags_string = "; ".join(str(e) for e in tags_list)
        resultant_program_list = intersection(tags_list, Program_list)
        resultant_category_list = intersection(tags_list, Category_list)
        resultant_audience_list = intersection(tags_list, Audience_list)
        resultant_program_list.sort()
        resultant_category_list.sort()
        resultant_audience_list.sort(reverse=True)
        # print(tags_string)

    if len(days_list_global) > 0:

        temp_days_list = []
        for item in days_list_global:
            if item not in temp_days_list:
                temp_days_list.append(item)

        # https://stackabuse.com/python-how-to-flatten-list-of-lists/
        flat_list = list(itertools.chain(*temp_days_list))
        unique_list = list(set(flat_list))
        days_list_global = sorted(unique_list, key=day_priority)

    # five part list showing availability of
    # Early Morning (Before 10am) -> 800 - 1000 A
    # Morning (10am - 12pm) -> 1000 - 1200 B
    # Lunchtime (12pm - 2pm) -> 1200 - 1400 C
    # Afternoon (2pm - 5pm) -> 1400 - 1700 D
    # Evening (After 5pm)  -> 1700 - 2200 E
    # https://stackoverflow.com/questions/19211828/using-any-and-all-to-check-if-a-list-contains-one-set-of-values-or-another
    course_times_availability = {}
    if len(course_times_list_global) > 0:
        temp_c_list = []
        for item in course_times_list_global:
            if item not in temp_c_list:
                temp_c_list.append(item)

        # https://stackabuse.com/python-how-to-flatten-list-of-lists/
        flat_list_c = list(itertools.chain(*temp_c_list))
        # remove duplicates
        res = list(OrderedDict.fromkeys(flat_list_c))
        course_times_list_global = sorted(res)
        A = any(x < 1000 for x in course_times_list_global)
        B = any((x >= 1000 and x < 1200) for x in course_times_list_global)
        C = any((x >= 1200 and x < 1400) for x in course_times_list_global)
        D = any((x >= 1400 and x < 1700) for x in course_times_list_global)
        E = any((x >= 1700) for x in course_times_list_global)

        # Early Morning (Before 10am) -> 800 - 1000 A
        # Morning (10am - 12pm) -> 1000 - 1200 B
        # Lunchtime (12pm - 2pm) -> 1200 - 1400 C
        # Afternoon (2pm - 5pm) -> 1400 - 1700 D
        # Evening (After 5pm)  -> 1700 - 2200 E

        course_times_availability = {
            "0800 - 1000": A,
            "1000 - 1200": B,
            "1200 - 1400": C,
            "1400 - 1700": D,
            "1700 - 2200": E,
        }

    # if len(tempSectionsList) > 0:
    #    tempSectionsList = sorted(
    #        tempSectionsList,
    #        key=lambda x: quarter_priority_nested(x),
    #        reverse=False,
    #    )

    request_url_temp = furl(request_url_string)
    request_url_temp.remove(["totalSubjectSearch"]).url
    request_url_temp.remove(["q"]).url
    request_url_temp.add({"q": subject + code}).url
    request_url_string_new = str(request_url_temp)

    explorecourses_url = request_url_string_new.replace("&view=xml-20200810", "catalog")
    if explorecourses_url and subject == "EDUC":
        coursediscovery_url = f"https://coursediscovery.gse.stanford.edu/node/courses/{subject.lower()}-{code.lower()}-2024-2025"
    else:
        coursediscovery_url = ""

    dictionary = {
        "subject": subject,
        "code": code,
        "title": title,
        "year": year,
        "grading": grading,
        "description": description,
        "term": term,
        "term_exclusive": term_exclusive,
        "format_of_course": format_of_course,
        "section_units": section_units,
        "units_range": units_range,
        "unitsMin": unitsMin,
        "unitsMax": unitsMax,
        "days": days_list_global,
        "course_times": course_times_list_global,
        "course_times_availability": course_times_availability,
        "instructors": instructors_list_global,
        "tags": tags_string,
        "sections": tempSectionsList,
        "explorecourses_url": explorecourses_url,
        "explorecourses_xml": request_url_string_new,
        "coursediscovery_url": coursediscovery_url,
        "section_count": len(tempSectionsList),
        "course_offered": len(tempSectionsList) > 0,
        "course_valid": type(len(tempSectionsList)) == int,
    }

    dictionary["program"] = []
    dictionary["category"] = []
    dictionary["audience"] = []
    if resultant_program_list:
        dictionary["program"] = resultant_program_list
    if resultant_category_list:
        dictionary["category"] = resultant_category_list
    if resultant_audience_list:
        dictionary["audience"] = resultant_audience_list

    return dictionary


def concise_course_dictionary_course_response_wilson(course, request_url_string):
    code = days = description = endTime = format_of_course = grading = location = (
        section_units
    ) = startTime = subject = title = unitsMin = unitsMax = year = ""

    course_times_list_global = []
    days_list_global = []
    instructors_list = []
    instructors_list_global = []
    tags_list = []
    term_list = []
    tempSectionsList = []
    units_range = []

    code = course.getElementsByTagName("code")[0].firstChild.nodeValue
    subject = course.getElementsByTagName("subject")[0].firstChild.nodeValue

    year = course.getElementsByTagName("year")[0].firstChild.nodeValue
    title = course.getElementsByTagName("title")[0].firstChild.nodeValue
    # description = course.getElementsByTagName("description")[0].firstChild.nodeValue
    if course.getElementsByTagName("description")[0]:
        if course.getElementsByTagName("description")[0].firstChild:
            description = course.getElementsByTagName("description")[
                0
            ].firstChild.nodeValue
        else:
            description = ""
    else:
        description = ""

    grading = course.getElementsByTagName("grading")[0].firstChild.nodeValue
    # print("*")
    # print()
    # print("Subject: " + subject)
    # print("code: " + code)
    # print("title: " + title)
    # print("year: " + year)
    # print("grading: " + grading)
    # print("*")
    # print("description: " + description)
    # print("*")
    # print()
    sectionsList = course.getElementsByTagName("sections")
    for sectionsNode in sectionsList:
        if sectionsNode.nodeType == Node.ELEMENT_NODE:
            sections = sectionsNode
            sList = sections.getElementsByTagName("section")

            for sNode in sList:
                tempSection = {}
                if sNode.nodeType == Node.ELEMENT_NODE:
                    # reset the instructors list
                    instructors_list = []

                    section = sNode

                    section_subject = section.getElementsByTagName("subject")[
                        0
                    ].firstChild.nodeValue
                    tempSection["subject"] = section_subject

                    section_code = section.getElementsByTagName("code")[
                        0
                    ].firstChild.nodeValue
                    tempSection["code"] = section_code

                    term = section.getElementsByTagName("term")[0].firstChild.nodeValue

                    term_list.append(term)
                    tempSection["term"] = term

                    format_of_course = section.getElementsByTagName("component")[
                        0
                    ].firstChild.nodeValue
                    tempSection["format_of_course"] = format_of_course

                    sectionNumber = section.getElementsByTagName("sectionNumber")[
                        0
                    ].firstChild.nodeValue
                    tempSection["sectionNumber"] = sectionNumber

                    if section.getElementsByTagName("units")[0].firstChild:

                        section_units = section.getElementsByTagName("units")[
                            0
                        ].firstChild.nodeValue
                        maxmin_units = section_units.split("-")
                        if len(maxmin_units) == 1:
                            unitsMin = maxmin_units[0]
                            unitsMax = maxmin_units[0]
                            units_range = [int(unitsMin)]
                        else:
                            unitsMin = maxmin_units[0]
                            unitsMax = maxmin_units[1]
                            # https://www.geeksforgeeks.org/python-create-list-of-numbers-with-given-range/
                            units_range = list(range(int(unitsMin), int(unitsMax) + 1))
                        tempSection["section_units"] = section_units
                        tempSection["unitsMin"] = unitsMin
                        tempSection["unitsMax"] = unitsMax

                    # print("term: " + term)
                    # print("format_of_course: " + format_of_course)
                    # print("section_units: " + section_units)
                    schedulesList = section.getElementsByTagName("schedules")
                    for schedulesNode in schedulesList:
                        # print(" *  scheduleNode  * ")
                        if schedulesNode.nodeType == Node.ELEMENT_NODE:
                            schedules = schedulesNode
                            schedList = schedules.getElementsByTagName("schedule")

                            for schedNode in schedList:
                                if schedNode.nodeType == Node.ELEMENT_NODE:
                                    schedule = schedNode
                                    if section.getElementsByTagName("days")[
                                        0
                                    ].firstChild:
                                        days = section.getElementsByTagName("days")[
                                            0
                                        ].firstChild.nodeValue

                                    if section.getElementsByTagName("startTime")[
                                        0
                                    ].firstChild:
                                        startTime = section.getElementsByTagName(
                                            "startTime"
                                        )[0].firstChild.nodeValue

                                        startTimeMil = military_time(startTime)
                                        startTime = pretty_print_time(startTime)
                                        tempSection["startTime"] = startTime

                                    if section.getElementsByTagName("endTime")[
                                        0
                                    ].firstChild:
                                        endTime = section.getElementsByTagName(
                                            "endTime"
                                        )[0].firstChild.nodeValue
                                        endTimeMil = military_time(endTime)
                                        endTime = pretty_print_time(endTime)
                                        tempSection["endTime"] = endTime

                                        # https://stackoverflow.com/questions/39298054/generating-15-minute-time-interval-array-in-python
                                        # 10 minute intervals
                                        # https://j0qnt6ghyd.execute-api.us-west-2.amazonaws.com/dev/course_total_subject_search/acct
                                        # https://j0qnt6ghyd.execute-api.us-west-2.amazonaws.com/dev/course/acct313
                                        # 1:15 - 2:35, levels out to 1:20 to 2:30
                                        course_times_list = (
                                            pd.DataFrame(
                                                columns=["NULL"],
                                                index=pd.date_range(
                                                    "2016-09-01T00:00:00Z",
                                                    "2016-09-01T23:59:00Z",
                                                    freq="10min",
                                                ),
                                            )
                                            .between_time(startTimeMil, endTimeMil)
                                            .index.strftime("%H%M")
                                            .tolist()
                                        )
                                        # https://www.geeksforgeeks.org/python-converting-all-strings-in-list-to-integers/
                                        course_times_list = list(
                                            map(int, course_times_list)
                                        )

                                        course_times_list_global.append(
                                            course_times_list
                                        )

                                    if section.getElementsByTagName("location")[
                                        0
                                    ].firstChild:
                                        location = section.getElementsByTagName(
                                            "location"
                                        )[0].firstChild.nodeValue
                                        tempSection["location"] = location

                                    # remove carriage returns and tabs, Monday \t\n Wednesday case somewhere...
                                    if days:
                                        days = days.strip()
                                    # print(startTime)
                                    # print(endTime)
                                    # https://www.digitalocean.com/community/tutorials/python-remove-spaces-from-string
                                    s = days
                                    days_split_list = s.split()
                                    days = " ".join(days_split_list)
                                    # print(len(days))
                                    # print(days)
                                    # print(location)
                                    tempSection["days"] = days
                                    days_list_global.append(days_split_list)

                                    instructorsList = (
                                        # section.getElementsByTagName(
                                        schedule.getElementsByTagName("instructors")
                                    )
                                    for instructorsNode in instructorsList:
                                        # print(" *  instructorsNode  * ")
                                        if (
                                            instructorsNode.nodeType
                                            == Node.ELEMENT_NODE
                                        ):
                                            instructors = instructorsNode
                                            instructorList = (
                                                instructors.getElementsByTagName(
                                                    "instructor"
                                                )
                                            )

                                            for instructorNode in instructorList:
                                                if (
                                                    instructorNode.nodeType
                                                    == Node.ELEMENT_NODE
                                                ):
                                                    instructor = instructorNode
                                                    # instructor_name = (
                                                    #    instructor.getElementsByTagName(
                                                    #        "name"
                                                    #    )[0].firstChild.nodeValue
                                                    # )
                                                    first_name = (
                                                        instructor.getElementsByTagName(
                                                            "firstName"
                                                        )[0].firstChild.nodeValue
                                                    )
                                                    last_name = (
                                                        instructor.getElementsByTagName(
                                                            "lastName"
                                                        )[0].firstChild.nodeValue
                                                    )
                                                    instructor_name = f"{first_name.title()} {last_name.title()}"
                                                    # print("instructor_name")
                                                    instructors_list.append(
                                                        instructor_name
                                                    )
                                                    instructors_list_global.append(
                                                        instructor_name
                                                    )

                                    # print(instructors_list)
                                    instructors_string = ""
                                    if len(instructors_list) > 0:
                                        temp_instructors_list = []
                                        for item in instructors_list:
                                            if item not in temp_instructors_list:
                                                temp_instructors_list.append(item)
                                        instructors_string = "; ".join(
                                            str(e) for e in temp_instructors_list
                                        )
                                        tempSection["instructor_name"] = (
                                            instructors_string
                                        )

                    # https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
                    if "section_units" in tempSection:
                        tempSectionsList.append(tempSection)
                    # print(tempSectionsList)
            temp_term_list = []
            for item in term_list:
                if item not in temp_term_list:
                    temp_term_list.append(item)
            term = sorted(temp_term_list, key=quarter_priority)

            # https://stackoverflow.com/questions/34214139/python-keep-only-letters-in-string
            term_exclusive = list(
                map(lambda string: "".join(filter(str.isalpha, string)), term)
            )

    # print()
    tagsList = course.getElementsByTagName("tags")
    for tagsNode in tagsList:
        if tagsNode.nodeType == Node.ELEMENT_NODE:
            tags = tagsNode
            tagList = tags.getElementsByTagName("tag")

            for tagNode in tagList:
                if tagNode.nodeType == Node.ELEMENT_NODE:
                    tag = tagNode
                    name = tag.getElementsByTagName("name")[0].firstChild.nodeValue
                    organization = tag.getElementsByTagName("organization")[
                        0
                    ].firstChild.nodeValue
                    if organization == "EDUC":
                        # print(name)
                        tags_list.append(name)
                    elif organization == "CARDCOURSES" and name == "educ":
                        tags_list.append(organization)

    if len(instructors_list_global) > 0:
        # remove duplicates
        # https://www.digitalocean.com/community/tutorials/get-unique-values-from-a-list-in-python
        temp_instructors_list = []
        for item in instructors_list_global:
            if item not in temp_instructors_list:
                temp_instructors_list.append(item)
        temp_instructors_list.sort()
        # instructors_string = "; ".join(str(e) for e in temp_instructors_list)
        instructors_list_global = temp_instructors_list

    tags_string = ""
    resultant_program_list = []
    resultant_category_list = []
    resultant_audience_list = []
    if len(tags_list) > 0:
        # print(tags_list)
        tags_string = "; ".join(str(e) for e in tags_list)
        resultant_program_list = intersection(tags_list, Program_list)
        resultant_category_list = intersection(tags_list, Category_list)
        resultant_audience_list = intersection(tags_list, Audience_list)
        resultant_program_list.sort()
        resultant_category_list.sort()
        resultant_audience_list.sort(reverse=True)
        # print(tags_string)

    if len(days_list_global) > 0:

        temp_days_list = []
        for item in days_list_global:
            if item not in temp_days_list:
                temp_days_list.append(item)

        # https://stackabuse.com/python-how-to-flatten-list-of-lists/
        flat_list = list(itertools.chain(*temp_days_list))
        unique_list = list(set(flat_list))
        days_list_global = sorted(unique_list, key=day_priority)

    # five part list showing availability of
    # Early Morning (Before 10am) -> 800 - 1000 A
    # Morning (10am - 12pm) -> 1000 - 1200 B
    # Lunchtime (12pm - 2pm) -> 1200 - 1400 C
    # Afternoon (2pm - 5pm) -> 1400 - 1700 D
    # Evening (After 5pm)  -> 1700 - 2200 E
    # https://stackoverflow.com/questions/19211828/using-any-and-all-to-check-if-a-list-contains-one-set-of-values-or-another
    course_times_availability = {}
    if len(course_times_list_global) > 0:
        temp_c_list = []
        for item in course_times_list_global:
            if item not in temp_c_list:
                temp_c_list.append(item)

        # https://stackabuse.com/python-how-to-flatten-list-of-lists/
        flat_list_c = list(itertools.chain(*temp_c_list))
        # remove duplicates
        res = list(OrderedDict.fromkeys(flat_list_c))
        course_times_list_global = sorted(res)
        A = any(x < 1000 for x in course_times_list_global)
        B = any((x >= 1000 and x < 1200) for x in course_times_list_global)
        C = any((x >= 1200 and x < 1400) for x in course_times_list_global)
        D = any((x >= 1400 and x < 1700) for x in course_times_list_global)
        E = any((x >= 1700) for x in course_times_list_global)

        # Early Morning (Before 10am) -> 800 - 1000 A
        # Morning (10am - 12pm) -> 1000 - 1200 B
        # Lunchtime (12pm - 2pm) -> 1200 - 1400 C
        # Afternoon (2pm - 5pm) -> 1400 - 1700 D
        # Evening (After 5pm)  -> 1700 - 2200 E

        course_times_availability = {
            "0800 - 1000": A,
            "1000 - 1200": B,
            "1200 - 1400": C,
            "1400 - 1700": D,
            "1700 - 2200": E,
        }

    # if len(tempSectionsList) > 0:
    #    tempSectionsList = sorted(
    #        tempSectionsList,
    #        key=lambda x: quarter_priority_nested(x),
    #        reverse=False,
    #    )

    request_url_temp = furl(request_url_string)
    request_url_temp.remove(["totalSubjectSearch"]).url
    request_url_temp.remove(["q"]).url
    request_url_temp.add({"q": subject + code}).url
    request_url_string_new = str(request_url_temp)

    explorecourses_url = request_url_string_new.replace("&view=xml-20200810", "catalog")
    if explorecourses_url and subject == "EDUC":
        coursediscovery_url = f"https://coursediscovery.gse.stanford.edu/node/courses/{subject.lower()}-{code.lower()}-2024-2025"
    else:
        coursediscovery_url = ""

    dictionary = {
        "subject": subject,
        "code": code,
        "title": title,
        "year": year,
        "grading": grading,
        "description": description,
        "term": term,
        "term_exclusive": term_exclusive,
        "format_of_course": format_of_course,
        "section_units": section_units,
        "units_range": units_range,
        "unitsMin": unitsMin,
        "unitsMax": unitsMax,
        "days": days_list_global,
        "course_times": course_times_list_global,
        "course_times_availability": course_times_availability,
        "instructors": instructors_list_global,
        "tags": tags_string,
        "sections": tempSectionsList,
        "explorecourses_url": explorecourses_url,
        "explorecourses_xml": request_url_string_new,
        "coursediscovery_url": coursediscovery_url,
        "section_count": len(tempSectionsList),
        "course_offered": len(tempSectionsList) > 0,
        "course_valid": type(len(tempSectionsList)) == int,
    }

    dictionary["program"] = []
    dictionary["category"] = []
    dictionary["audience"] = []
    if resultant_program_list:
        dictionary["program"] = resultant_program_list
    if resultant_category_list:
        dictionary["category"] = resultant_category_list
    if resultant_audience_list:
        dictionary["audience"] = resultant_audience_list

    return dictionary


def xml_to_dictionary(**params):
    # https://stackoverflow.com/questions/15301999/default-arguments-with-args-and-kwargs
    # https://stackoverflow.com/a/64926425
    defaultParams = {
        # "academicYear": "20222023",
        # "academicYear": "20232024",
        "academicYear": "20242025",
        "view": "xml-20200810",
        "totalSubjectSearch": 0,
    }

    params = {**defaultParams, **params}

    courseQueryName = params["q"]
    totalSubjectSearch = params["totalSubjectSearch"]
    sanitized_course = courseQueryName.replace("+", "").replace(" ", "")
    dictionary = {
        "subject": sanitized_course,
        "course_offered": False,
        "course_valid": False,
    }

    # if containsNumber(params["q"]) and not params["q"][0].isdigit():
    response = requests.get("https://explorecourses.stanford.edu/search", params=params)
    # request_url = response.url
    # https://stackoverflow.com/questions/43607870/how-to-change-values-of-url-query-in-python
    # https://github.com/gruns/furl
    request_url = furl(response.url)
    request_url.remove(["q"]).url
    request_url.add({"q": sanitized_course}).url
    request_url_string = str(request_url)

    # print(response.content)
    dict_data = xmltodict.parse(response.content)
    # print(dict_data)
    # print(json.dumps(dict_data, indent=2))

    xml_string = response.content.decode("UTF-8")
    document = parseString(xml_string)
    set_id_attribute(document)
    remove_whitespace(document)
    document.normalize()

    # print(document)

    nList = document.getElementsByTagName("courses")
    # print(nList)

    course_dictionary_list = []
    for cNode in nList:
        if cNode.nodeType == Node.ELEMENT_NODE:
            # print("helldasfo")
            courses = cNode
            cList = courses.getElementsByTagName("course")
            # ensure cList not empty, valid response given from API call
            if not cList:
                # safeguard
                return dictionary

            my_str = sanitized_course

            # https://bobbyhadz.com/blog/python-split-string-into-text-and-number
            my_list = list(filter(None, re.split(r"(\d+)", my_str)))

            sanitized_course_subject = my_list[0]
            if len(my_list) > 2:
                sanitized_course_code = my_list[1] + my_list[2]
            elif len(my_list) == 2:
                sanitized_course_code = my_list[1]
            elif len(my_list) == 1:
                sanitized_course_code = ""
            # exit()

            # cList_first_response = [cList[0]]
            # print(cList)
            #
            # for nNode in cList_first_response:
            for nNode in cList:

                # adsf
                if nNode.nodeType == Node.ELEMENT_NODE:
                    # print(nNode)
                    course = nNode
                    # subject = code = ""
                    if course.getElementsByTagName("subject")[0].firstChild:
                        subject = course.getElementsByTagName("subject")[
                            0
                        ].firstChild.nodeValue
                    if course.getElementsByTagName("code")[0].firstChild:
                        code = course.getElementsByTagName("code")[
                            0
                        ].firstChild.nodeValue

                    # print(subject)
                    # print(code)
                    # exit()

                    if "::" in sanitized_course or (
                        totalSubjectSearch and subject == sanitized_course_subject
                    ):
                        single_course_dictionary = (
                            concise_course_dictionary_course_response(
                                course, request_url_string
                            )
                        )
                        if single_course_dictionary["course_offered"]:
                            course_dictionary_list.append(single_course_dictionary)

                    else:
                        second_conditional = code == sanitized_course_code
                        if subject == sanitized_course_subject and second_conditional:
                            single_course_dictionary = (
                                single_course_dictionary_course_response(
                                    course, request_url_string
                                )
                            )
                            return single_course_dictionary

    if totalSubjectSearch or "::" in sanitized_course:
        now = pendulum.now("America/Los_Angeles")
        time_generation_epoch = now.int_timestamp
        time_generation_readable = str(now.format("YYYY-MM-DD HH:mm"))
        object = {
            "cached_time_generation_epoch": time_generation_epoch,
            "cached_time_generation_readable": time_generation_readable,
            "course_dictionary_list": course_dictionary_list,
            "course_count": len(course_dictionary_list),
        }
        return object
    else:
        return dictionary


def xml_to_dictionary_tagz(**params):
    # https://stackoverflow.com/questions/15301999/default-arguments-with-args-and-kwargs
    # https://stackoverflow.com/a/64926425
    defaultParams = {
        # "academicYear": "20222023",
        # "academicYear": "20232024",
        "academicYear": "20242025",
        "view": "xml-20200810",
        "totalSubjectSearch": 0,
    }

    params = {**defaultParams, **params}

    courseQueryName = params["q"]
    totalSubjectSearch = params["totalSubjectSearch"]
    sanitized_course = courseQueryName.replace("+", "").replace(" ", "")
    dictionary = {
        "subject": sanitized_course,
        "course_offered": False,
        "course_valid": False,
    }

    # if containsNumber(params["q"]) and not params["q"][0].isdigit():
    response = requests.get("https://explorecourses.stanford.edu/search", params=params)
    # request_url = response.url
    # https://stackoverflow.com/questions/43607870/how-to-change-values-of-url-query-in-python
    # https://github.com/gruns/furl
    request_url = furl(response.url)
    request_url.remove(["q"]).url
    request_url.add({"q": sanitized_course}).url
    request_url_string = str(request_url)

    # print(response.content)
    dict_data = xmltodict.parse(response.content)
    # print(dict_data)
    # print(json.dumps(dict_data, indent=2))

    xml_string = response.content.decode("UTF-8")
    document = parseString(xml_string)
    set_id_attribute(document)
    remove_whitespace(document)
    document.normalize()

    # print(document)

    nList = document.getElementsByTagName("courses")
    # print(nList)

    course_dictionary_list = []
    for cNode in nList:
        if cNode.nodeType == Node.ELEMENT_NODE:
            # print("helldasfo")
            courses = cNode
            cList = courses.getElementsByTagName("course")
            # ensure cList not empty, valid response given from API call
            if not cList:
                # safeguard
                return dictionary

            my_str = sanitized_course

            # https://bobbyhadz.com/blog/python-split-string-into-text-and-number
            my_list = list(filter(None, re.split(r"(\d+)", my_str)))

            sanitized_course_subject = my_list[0]
            if len(my_list) > 2:
                sanitized_course_code = my_list[1] + my_list[2]
            elif len(my_list) == 2:
                sanitized_course_code = my_list[1]
            elif len(my_list) == 1:
                sanitized_course_code = ""
            # exit()

            # cList_first_response = [cList[0]]
            # print(cList)
            #
            # for nNode in cList_first_response:
            for nNode in cList:

                # adsf
                if nNode.nodeType == Node.ELEMENT_NODE:
                    # print(nNode)
                    course = nNode
                    # subject = code = ""
                    if course.getElementsByTagName("subject")[0].firstChild:
                        subject = course.getElementsByTagName("subject")[
                            0
                        ].firstChild.nodeValue
                    if course.getElementsByTagName("code")[0].firstChild:
                        code = course.getElementsByTagName("code")[
                            0
                        ].firstChild.nodeValue

                    # print(subject)
                    # print(code)
                    # exit()

                    if "::" in sanitized_course or (
                        totalSubjectSearch and subject == sanitized_course_subject
                    ):
                        single_course_dictionary = (
                            concise_course_dictionary_course_response_wilson(
                                course, request_url_string
                            )
                        )
                        # if single_course_dictionary["course_offered"]:
                        #    course_dictionary_list.append(single_course_dictionary)
                        course_dictionary_list.append(single_course_dictionary)

                    else:
                        second_conditional = code == sanitized_course_code
                        if subject == sanitized_course_subject and second_conditional:
                            single_course_dictionary = (
                                single_course_dictionary_course_response(
                                    course, request_url_string
                                )
                            )
                            return single_course_dictionary

    if totalSubjectSearch or "::" in sanitized_course:
        now = pendulum.now("America/Los_Angeles")
        time_generation_epoch = now.int_timestamp
        time_generation_readable = str(now.format("YYYY-MM-DD HH:mm"))
        object = {
            "cached_time_generation_epoch": time_generation_epoch,
            "cached_time_generation_readable": time_generation_readable,
            "course_dictionary_list": course_dictionary_list,
            "course_count": len(course_dictionary_list),
        }
        return object
    else:
        return dictionary


# json_object = json.dumps(dictionary, indent=2)
# print(json_object)

if __name__ == "__main__":

    params = {
        # "q": "EDUC101",  # no day time nor location
        # "academicYear": "20222023",
        "academicYear": "20242025",
        # "q": "EDUC147",  # L or not L
        "q": "EDUC::LDT",  # L or not L
        # "q": "EDUC147",  # L or not L
    }

    params2 = {
        # "q": "EDUC101",  # no day time nor location
        # "academicYear": "20222023",
        "academicYear": "20242025",
        # "q": "EDUC147",  # L or not L
        "q": "EDUC::LDT",  # L or not L
        # "q": "EDUC147",  # L or not L
    }

    # params = {
    #    "q": "EDUC",
    #    "totalSubjectSearch": 1,
    # }

    dictionary = xml_to_dictionary_tagz(**params2)
    json_object = json.dumps(dictionary, indent=2)
    print(json_object)
