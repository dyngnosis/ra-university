# This python script uses OpenAI GPT to generate content for the course
# The name of the couerse is provided by the command line argument -c
# The name of the output file is provided by the command line argument -f
# the subject depth is controlled by the command line argument -d
# created by Jeremy Richards for RAU

import json #remove?
import openai
import time
import argparse
import pprint
import random
from collections import OrderedDict
from openai.error import ServiceUnavailableError
import moo_bot

def get_course_chapters(f):
    query = f'This comprehensive online university course covering the field of {f} would includes the chapters:'
    x = openai.Completion.create(
        model="text-davinci-003",
        prompt=query,
        max_tokens=500,
        temperature=0
    )
    # category_sub_categories = list(
    #     filter(None, x['choices'][0]['text'].splitlines()))
    # # turn this into a dict
    sub_category_dict = OrderedDict()
    for sub_category in filter(None, x['choices'][0]['text'].splitlines()):
        sub_category_dict[sub_category] = OrderedDict()
    # pprint.pprint(sub_category_dict)
    return sub_category_dict


def get_chapter_lessons(course_name, chapter):
    query = f'Welcome to this online university course on {course_name}, This chapter, {chapter}, includes the following lessons:'
    x = openai.Completion.create(
        model="text-davinci-003",
        prompt=query,
        max_tokens=1024,
        temperature=0
    )
    # category_sub_categories = list(
    #     filter(None, x['choices'][0]['text'].splitlines()))
    # # turn this into a dict
    sub_category_dict = OrderedDict()
    for sub_category in filter(None, x['choices'][0]['text'].splitlines()):
        sub_category_dict[sub_category] = OrderedDict()
    # pprint.pprint(sub_category_dict)
    return sub_category_dict


def get_key_concepts(course, chapter, lesson):
    query = f'The key concepts in the lesson {lesson} in the chapter {chapter} in the course {course} are:'
    print(query)
    x = openai.Completion.create(
        model="text-davinci-003",
        prompt=query,
        max_tokens=500,
        temperature=0
    )
    key_concepts_dict = OrderedDict()
    for key_concept in filter(None, x['choices'][0]['text'].splitlines()):
        key_concepts_dict[key_concept] = OrderedDict()
        # pprint.pprint(key_concepts_dict)
    return key_concepts_dict


def get_keyconcept_details(key_concept, course, chapter, lesson):
    #query = f'Describe the concept of "{key_concept}" in the context of in as much detail as possible'
    query = f'The following paragraph describes the concept of "{key_concept}" in a lesson on {lesson} from the chapter called {chapter} in the study of {course}:'
    x = openai.Completion.create(
        model="text-davinci-003",
        prompt=query,
        max_tokens=3000,
        temperature=0
    )
    print(x['choices'][0]['text'])
    # key_concepts_dict = OrderedDict()
    # for key_concept in filter(None, x['choices'][0]['text'].splitlines()):
    #     key_concepts_dict[key_concept] = OrderedDict()
    #     # print.pprint(key_concepts_dict)
    return x['choices'][0]['text']


def make_quiz(course, chapter, lesson):
    q = """
        Here is a simple acceptable GIFT multiple choice format:
        // Course: grants tomb, Chapter: burial Lesson: burial location
        ::Grants tomb::Who is buried in Grant's tomb in New York City? {
        =Grant
        ~No one
        ~Napoleon
        ~Churchill
        ~Mother Teresa
        }
        //Course: The lightbulb, Chapter: history Lesson: who invented the lightbulb
        ::History of the Lightbulb::Who invented the lightbulb? {
        =Thomas Edison
        ~Nicola Tesla
        ~Albert Einstein
        ~Einstein
        ~Charles Babbage
        }

        Rules for GIFT multple choice format:
        each question should start and end with :: followed by the question.
        A curly brace opens the area for possible solutions.  
        The right answer starts with the equal sign(=) and wrong answers start with ~
        remember to include wrong answers and add a new line between each question.

    """
    a = f'Using the above information, create 2 questions for a course on {course} in a chapter on {chapter} where the lesson focues on {lesson} '
    print(a)
    # TODO add a try to catch:
    #     Exception has occurred: ServiceUnavailableError
    # The server is overloaded or not ready yet.
    #   File "/home/gpu/code/rau/gen_content.py", line 114, in make_quiz
    #     x = openai.Completion.create(
    #   File "/home/gpu/code/rau/gen_content.py", line 155, in main
    #     make_quiz(course_name, chapter, key_concept_details))
    #   File "/home/gpu/code/rau/gen_content.py", line 166, in <module>
    #     main()
    result = []

    try:
        x = openai.Completion.create(
            model="text-davinci-003",
            prompt=q+a,
            max_tokens=1000,
            temperature=0
        )
        print(x['choices'][0]['text'])
        return x['choices'][0]['text']
    # catch the exception, wait for 10 seconds and try agai
    except ServiceUnavailableError:
        time.sleep(10)
        print("ServiceUnavailableError, waiting 10 seconds and trying again")
        make_quiz(course, chapter, lesson)

    except Exception as e:
        print(e)
    return result


def gen_lesson_intro(course, chapter, lesson, concepts):
    """This function accepts the detail required to generate a lesson intro"""
    result = []
    q = f"Given the course {course}, the chapter {chapter}, the lesson {lesson} and the key concepts {concepts}, generate a lesson intro:"

    try:
        x = openai.Completion.create(
            model="text-davinci-003",
            prompt=q,
            max_tokens=3000,
            temperature=0
        )
    except ServiceUnavailableError:
        time.sleep(10)
        print("ServiceUnavailableError, waiting 10 seconds and trying again")
        gen_lesson_intro(course, chapter, lesson, concepts)

    except Exception as e:
        print(e)
    return result


def get_course_description(course, chapters):

    description = ""
    if chapters == "description":
        pass
    else:
        query = f'Write an interesting and fun introduction to a course on on {course} where the course focuses on on the following chapters:{chapters}'
        x = openai.Completion.create(
            model="text-davinci-003",
            prompt=query,
            max_tokens=500,
            temperature=0
        )
        description = x['choices'][0]['text']

    return description


def get_lesson_description(course, chapter, lesson):
    description = ""
    try:
        query = f'The following is a lesson on {lesson} from a chapter called "{chapter}"'
        x = openai.Completion.create(
            model="text-davinci-003",
            prompt=query,
            max_tokens=1000,
            temperature=0
        )
        description = x['choices'][0]['text']
        print(description)
    except ServiceUnavailableError:
        time.sleep(10)
        print("ServiceUnavailableError, waiting 10 seconds and trying again")
        description = get_lesson_description(course, chapter, lesson)
    return description
 

def get_chapter_description(chapter, lessons):
    if lessons == "description":
        pass
    else:
        query = f'Write an interesting and fun introduction to a chapter on on {chapter} where the chapter focuses on on the following lessons:{lessons}'
        x = openai.Completion.create(
            model="text-davinci-003",
            prompt=query,
            max_tokens=3000,
            temperature=0
        )
        return x['choices'][0]['text']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--course_name", default="Pokemon 101", help="course name")
    parser.add_argument("-f", "--filename", default="Pokemon-content-v3.json",
                        help="filename to write content to")
    parser.add_argument("-c", "--cat", default="Pokemon",
                        help="High level category name")
    parser.add_argument("-s", "--sname", default="fut-davinci3",
                        help="Short category name")
    args = parser.parse_args()

    filename = args.filename  # output file
    course_name = args.course_name
    course = OrderedDict()
    course['name'] = args.course_name
    course['sname'] = args.sname
    course['cat'] = args.cat

    # we ask gpt for a list of chapters that would be in a course on "course_name"
    chapters = (get_course_chapters(course_name))
    #using the chapters as input we generate a course description
    course["description"] = get_course_description(
        course_name, chapters.keys())
    print("course description: ", course["description"])
    for chapter in chapters.keys():
        #get the lessons that would be in the chapter
        course[chapter] = (get_chapter_lessons(course_name, chapter))
        #now that we have the lessons we generate a description for the chapter
        course[chapter]["description"] = get_chapter_description(chapter,
                                                                course[chapter].keys())
        print("chapter description: ", course[chapter]["description"])

        for lesson in course[chapter].keys():
            #skip the key that contains the description of the chapter
            if lesson == "description":
                pass
            else:
                course[chapter][lesson]["description"] = get_lesson_description(
                    course_name, chapter, " ".join(course[chapter][lesson].keys()))
                print("lesson description: ",
                      course[chapter][lesson]["description"])

                key_concepts = course[chapter][lesson] = (
                    get_key_concepts(course_name, chapter, lesson))

                for key_concept in key_concepts.keys():
                    if key_concept == "description":
                        pass
                    else:
                        # put key concept details in each of the concept dicts and also assign the concept to a variable so we can generate a quiz with it
                        course[chapter][lesson][key_concept] = (
                            get_keyconcept_details(key_concept, course_name, chapter, lesson))
                        #MAKE QUIZ QUESTIONS
                        # lesson_quiz.append(
                        #     make_quiz(course_name, chapter, " ".join(course[chapter][lesson][key_concept].keys())))  # TODO enhance quiz to use the len of concepts to determine number of questions

                    # print(course)
                #         course[chapter][lesson]["description"] = get_lesson_description(
                #             course_name, chapter, " ".join(course[chapter][lesson][key_concept].keys()))
                # course[chapter][lesson]["quiz"] = lesson_quiz
                with open(filename, 'w') as outfile:
                    json.dump(course, outfile)
                # pprint.pprint(course)


if __name__ == "__main__":
    main()
