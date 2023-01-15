# open the c.json file and then write the course content to the moodle server

import json
import requests
import sys
import os
import pprint
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import urllib.parse
import argparse

#For generating images
from diffusers import StableDiffusionPipeline
import torch
#for generating file names
import uuid

pipe = StableDiffusionPipeline.from_pretrained(
	"CompVis/stable-diffusion-v1-4", 
	use_auth_token=True
).to("cuda")




def gen_image_chapter(lesson, chapter):
    prompt = f"A picture representing the {lesson}, chapter {chapter}"
    with torch.cuda.amp.autocast(True):
        image = pipe(prompt).images[0]
    fname = uuid.uuid4().hex        
    image.save(f"/var/www/html/images/{fname}.png")
    image_html = "<img src=\"/images/"+fname+".png\" alt=\""+fname+"\" />"
    return image_html

def gen_image_lesson(concept, lesson, chapter):
    prompt = f"A picture representing the concept {concept}, in the context of the {lesson}, chapter {chapter}"
    with torch.cuda.amp.autocast(True):
        image = pipe(prompt).images[0]
    fname = uuid.uuid4().hex        
    image.save(f"/var/www/html/images/{fname}.png")
    image_html = "<img src=\"/images/"+fname+".png\" alt=\""+fname+"\" />"
    return image_html



def get_categories(msession):
    # get the categories from the moodle server
    """
    GET /moodle/course/management.php HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Referer: http://192.168.0.23/moodle/admin/search.php
    Connection: close
    Cookie: MoodleSession=4e8ckg8apb1qkgpf6i5vtsd9pl; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1
"""
    url = 'http://192.168.0.23/moodle/course/management.php'
    headers = {
        "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    r = requests.get(url, headers=headers)
    return r.text

def create_category(cookie, skey, category_name, description, id=0, parent=0):
    """
    POST /moodle/course/editcategory.php HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 329
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/course/editcategory.php?parent=0
    Cookie: MoodleSession=fujjsbhtj7rs2cnjntobt67qb5; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1

    id=0&sesskey=cElMAGR7N7&_qf__core_course_editcategory_form=1&parent=0&name=Business&idnumber=&description_editor%5Btext%5D=%3Cp+dir%3D%22ltr%22+style%3D%22text-align%3A+left%3B%22%3EThis+is+the+description%3Cbr%3E%3C%2Fp%3E&description_editor%5Bformat%5D=1&description_editor%5Bitemid%5D=468198521111&submitbutton=Create+category
    """
    n = 10
    random_int = ''.join(["{}".format(randint(0, 9)) for num in range(0, n)])
    data = f"id={id}&sesskey={skey}&_qf__core_course_editcategory_form=1&parent={parent}&name={category_name}&idnumber=&description_editor%5Btext%5D={description}&description_editor%5Bformat%5D=1&description_editor%5Bitemid%5D={random_int}&submitbutton=Create+category"
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Cookie": f"MoodleSession={cookie}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    url = "http://192.168.0.23/moodle/course/editcategory.php"
    response = requests.post(url, data=data, headers=headers)
    print(response.status_code)
    print(f"\n{data}\n")
    return response

def file_upload(msession, skey, filename, content, itemid, repoid='5', env='filepicker', client_id='63a5cdc42aac3'):
    #TODO: NOT IMPLEMENTED
    """
    POST /moodle/repository/repository_ajax.php?action=upload HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: multipart/form-data; boundary=---------------------------109495435834671807661362521041
    Content-Length: 6069
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/mod/lesson/import.php?id=1337&pageid=0
    Cookie: MoodleSession=ettnad827r86kcetmukb6tdmgk; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1
    """

    top_data = f"""
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="repo_upload_file"; filename="{filename}"
    Content-Type: application/octet-stream

    {content}"""

    bottom_data = f"""-----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="title"


    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="author"

    Jeremy Richards
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="license"

    unknown
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="itemid"

    {randid}
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="repo_id"

    {repoid}
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="p"


    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="page"


    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="env"

    {env}
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="sesskey"

    {skey}
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="client_id"

    {client_id}
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="itemid"

     {randid}
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="maxbytes"

    -1
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="areamaxbytes"

    -1
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="ctx_id"

    1407
    -----------------------------109495435834671807661362521041
    Content-Disposition: form-data; name="savepath"

    /
    -----------------------------109495435834671807661362521041--"""

    headers = {"Content-Type": "multipart/form-data; boundary=---------------------------109495435834671807661362521041",
               "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    url = "http://192.168.0.23/moodle/repository/repository_ajax.php?action=upload"
    response = requests.post(url, data=top_data + bottom_data, headers=headers)
    print(response.text)
    return response

def create_course(msession, skey, category_id, course_name, course_sname, course_description, visible="1", id=0, category=0):
    """
    POST /moodle/course/edit.php HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 1309
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/course/edit.php?category=2&returnto=catmanage
    Cookie: MoodleSession=fujjsbhtj7rs2cnjntobt67qb5; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1

    returnto=catmanage&returnurl=http%3A%2F%2F192.168.0.23%2Fmoodle%2Fcourse%2Fmanagement.php%3Fcategoryid%3D2&mform_isexpanded_id_descriptionhdr=1&addcourseformatoptionshere=&id=&sesskey=cElMAGR7N7&_qf__course_edit_form=1&mform_isexpanded_id_general=1&mform_isexpanded_id_courseformathdr=0&mform_isexpanded_id_appearancehdr=0&mform_isexpanded_id_filehdr=0&mform_isexpanded_id_completionhdr=0&mform_isexpanded_id_groups=0&mform_isexpanded_id_rolerenaming=0&mform_isexpanded_id_tagshdr=0&fullname=Full+course+name2&shortname=CS102&category=2&visible=1&startdate%5Bday%5D=21&startdate%5Bmonth%5D=12&startdate%5Byear%5D=2022&startdate%5Bhour%5D=0&startdate%5Bminute%5D=0&enddate%5Bday%5D=21&enddate%5Bmonth%5D=12&enddate%5Byear%5D=2023&enddate%5Bhour%5D=0&enddate                                  %5Bminute%5D=0&enddate%5Benabled%5D=1&idnumber=&summary_editor%5Btext%5D=Course+Summ&summary_editor%5Bformat%5D=1&summary_editor%5Bitemid%5D=686262990&overviewfiles_filemanager=350623279&format=topics&numsections=4&hiddensections=1&coursedisplay=0&lang=&newsitems=5&showgrades=1&showreports=0&showactivitydates=1&maxbytes=0&enablecompletion=1&showcompletionconditions=1&groupmode=0&groupmodeforce=0&defaultgroupingid=0&role_1=&role_2=&role_3=&role_4=&role_5=&role_6=&role_7=&role_8=&tags=_qf__force_multiselect_submission&saveanddisplay=Save+and+display
    """

    data = f"returnto=catmanage&returnurl=http%3A%2F%2F192.168.0.23%2Fmoodle%2Fcourse%2Fmanagement.php%3Fcategoryid%3D2&mform_isexpanded_id_descriptionhdr=1&addcourseformatoptionshere=&id=&sesskey={skey}&_qf__course_edit_form=1&mform_isexpanded_id_general=1&mform_isexpanded_id_courseformathdr=0&mform_isexpanded_id_appearancehdr=0&mform_isexpanded_id_filehdr=0&mform_isexpanded_id_completionhdr=0&mform_isexpanded_id_groups=0&mform_isexpanded_id_rolerenaming=0&mform_isexpanded_id_tagshdr=0&fullname={course_name}&shortname={course_sname}&category={category_id}&visible={visible}&startdate%5Bday%5D=21&startdate%5Bmonth%5D=12&startdate%5Byear%5D=2022&startdate%5Bhour%5D=0&startdate%5Bminute%5D=0&enddate%5Bday%5D=21&enddate%5Bmonth%5D=12&enddate%5Byear%5D=2023&enddate%5Bhour%5D=0&enddate%5Bminute%5D=0&enddate%5Benabled%5D=1&idnumber=&summary_editor%5Btext%5D={course_description}&summary_editor%5Bformat%5D=1&summary_editor%5Bitemid%5D=86262990&overviewfiles_filemanager=350623279&format=topics&numsections=4&hiddensections=1&coursedisplay=0&lang=&newsitems=5&showgrades=1&showreports=0&showactivitydates=1&maxbytes=0&enablecompletion=1&showcompletionconditions=1&groupmode=0&groupmodeforce=0&defaultgroupingid=0&role_1=&role_2=&role_3=&role_4=&role_5=&role_6=&role_7=&role_8=&tags=_qf__force_multiselect_submission&saveanddisplay=Save+and+display"

    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    url = "http://192.168.0.23/moodle/course/edit.php"
    print(data)
    response = requests.post(url, data=data, headers=headers)
    print(response.status_code)
    return response

def create_chapter(msession, skey, course_id, chapter_name):
    """
    POST /moodle/course/modedit.php HTTP/1.1
    Host:
    """
    return

def add_resource(msession, skey, name, description, course_id, section_id, module_num, resource_type="lesson", mediafile="74023563"):
    """
    POST /moodle/course/modedit.php HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 1701
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/course/modedit.php?add=lesson&type=&course=2&section=1&return=0&sr=0
    Cookie: MoodleSession=fujjsbhtj7rs2cnjntobt67qb5; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1
    ##e={course_id}&coursemodule=&section={section_id}&module={module_num}&modulename={resource_type}&insta
    width=640&height=480&bgcolor=%23FFFFFF&mediawidth=640&mediaheight=480&mediaclose=0&dependency=0&timespent=0&completed=0&gradebetterthan=0&allowofflineattempts=0&completionunlocked=1&course=2&coursemodule=&section=1&module=15&modulename=lesson&instance=&addson&update=0&return=0&sr=0&sesskey=cElMAGR7N7&_qf__mod_lesson_mod_form=1&mform_showmore_id_appearancehdr=0&mform_showmore_id_availabilityhdr=0&mform_showmore_id_flowcontrol=0&mform_showmore_id_modstandardgrade=0&mform_isexpanded_id_general=1&mform_isexpanded_id_appearancehdr=0&mform_isexpanded_id_availabilityhdr=0&mform_isexpanded_id_flowcontrol=0&mform_isexpanded_id_modstandardgrade=0&mform_isexpanded_id_modstandardelshdr=0&mform_isexpanded_id_availabilityconditionsheader=0&mform_isexpanded_id_activitycompletionheader=0&mform_isexpanded_id_tagshdr=0&mform_isexpanded_id_competenciessection=0&name=New+Lesson+One+Name&introeditor%5Btext%5D=%3Cp+dir%3D%22ltr%22+style%3D%22text-align%3A+left%3B%22%3ENew+Lesson+One+Description%3Cbr%3E%3C%2Fp%3E&introeditor%5Bformat%5D=1&introeditor%5Bitemid%5D=486972635&showdescription=0&mediafile=74023563&ongoing=0&displayleftif=0&slideshow=0&maxanswers=5&feedback=0&activitylink=0&progressbar=0&displayleft=0&usepassword=0&modattempts=0&review=0&maxattempts=1&nextpagedefault=0&maxpages=1&grade%5Bmodgrade_type%5D=point&grade%5Bmodgrade_point%5D=100&gradecat=1&gradepass=&practice=0&custom=1&minquestions=0&retake=0&visible=1&cmidnumber=&lang=&groupmode=0&availabilityconditionsjson=%7B%22op%22%3A%22%26%22%2C%22c%22%3A%5B%5D%2C%22showc%22%3A%5B%5D%7D&completion=1&tags=_qf__force_multiselect_submission&competencies=_qf__force_multiselect_submission&competency_rule=0&submitbutton=Save+and+display
    """

    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    url = "http://192.168.0.23/moodle/course/modedit.php"
    data = f'width=640&height=480&bgcolor=%23FFFFFF&mediawidth=640&mediaheight=480&mediaclose=0&dependency=0&timespent=0&completed=0&gradebetterthan=0&allowofflineattempts=0&completionunlocked=1&course={course_id}&coursemodule=&section={section_id}&module={module_num}&modulename={resource_type}&instance=&add=lesson&update=0&return=0&sr=0&sesskey={skey}&_qf__mod_lesson_mod_form=1&mform_showmore_id_appearancehdr=0&mform_showmore_id_availabilityhdr=0&mform_showmore_id_flowcontrol=0&mform_showmore_id_modstandardgrade=0&mform_isexpanded_id_general=1&mform_isexpanded_id_appearancehdr=0&mform_isexpanded_id_availabilityhdr=0&mform_isexpanded_id_flowcontrol=0&mform_isexpanded_id_modstandardgrade=0&mform_isexpanded_id_modstandardelshdr=0&mform_isexpanded_id_availabilityconditionsheader=0&mform_isexpanded_id_activitycompletionheader=0&mform_isexpanded_id_tagshdr=0&mform_isexpanded_id_competenciessection=0&name={name}&introeditor%5Btext%5D={description}&introeditor%5Btext%5D=%3Cp+dir%3D%22ltr%22+style%3D%22text-align%3A+left%3B%22%3E{description}%3Cbr%3E%3C%2Fp%3E&introeditor%5Bformat%5D=1&introeditor%5Bitemid%5D=139426687&showdescription=0&mediafile=636140103&ongoing=0&displayleftif=0&slideshow=0&maxanswers=5&feedback=0&activitylink=0&progressbar=0&displayleft=0&usepassword=0&modattempts=0&review=0&maxattempts=1&nextpagedefault=0&maxpages=1&grade%5Bmodgrade_type%5D=point&grade%5Bmodgrade_point%5D=100&gradecat=22&gradepass=&practice=0&custom=1&minquestions=0&retake=0&visible=1&cmidnumber=&lang=&groupmode=0&availabilityconditionsjson=%7B%22op%22%3A%22%26%22%2C%22c%22%3A%5B%5D%2C%22showc%22%3A%5B%5D%7D&completion=1&tags=_qf__force_multiselect_submission&competencies=_qf__force_multiselect_submission&competency_rule=0&submitbutton2=Save+and+display'
    response = requests.post(url, headers=headers, data=data)
    #image_html = "%21%3C%2Fp%3E%3Cp%3E%3Cimg+src%3D%22%2Fimages%2Fconcept.jpg%22+alt%3D%22%22+role%3D%22presentation%22+class%3D%22atto_image_button_text-bottom%22+width%3D%22512%22+height%3D%22512%22%3E"
    #return image_html
    print(data)

    return response

def add_lesson_content(msession, skey, lesson_id, pageid, firstpage, qtype, title, contents):
    """
    POST /moodle/mod/lesson/editpage.php HTTP/1.1
    Host: 192.168.0.23il
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 899
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/mod/lesson/editpage.php?id=22&pageid=0&qtype=20&firstpage=1
    Cookie: MoodleSession=fujjsbhtj7rs2cnjntobt67qb5; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1

    returnto=http%3A%2F%2F192.168.0.23%2Fmoodle%2Fmod%2Flesson%2Fedit.php
    %3Fid%3D22%23lesson-0&
    id=22&
    pageid=0&
    firstpage=1&
    qtype=20&
    sesskey=cElMAGR7N7&
    _qf__lesson_add_page_form_branchtable=1&
    mform_isexpanded_id_qtypeheading=1&
    mform_isexpanded_id_headeranswer0=1&
    mform_isexpanded_id_headeranswer1=0&
    mform_isexpanded_id_headeranswer2=0&
    mform_isexpanded_id_headeranswer3=0&
    mform_isexpanded_id_headeranswer4=0&
    ## lesson_title
    title=Lesson+Content+Page+Title&
    contents_editor%5Btext%5D=%3Cp+dir%3D%22ltr%22+style%3D%22text-align%3A+left%3B%22%3EXXXXXXPAGE______CONTENTS______XXXXXXXX%3Cbr%3E%3C%2Fp%3E&
    contents_editor%5Bformat%5D=1&
    contents_editor%5Bitemid%5D=803713859&
    layout=1&
    display=1&
    answer_editor%5B0%5D=Content+1+Description&
    jumpto%5B0%5D=0&answer_editor%5B1%5D=&
    jumpto%5B1%5D=-1&answer_editor%5B2%5D=&
    jumpto%5B2%5D=-1&answer_editor%5B3%5D=&
    jumpto%5B3%5D=-1&answer_editor%5B4%5D=&
    jumpto%5B4%5D=-1&submitbutton=Save+page
    """

    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    url = "http://192.168.0.23/moodle/mod/lesson/editpage.php"
    data = f'returnto=http%3A%2F%2F192.168.0.23%2Fmoodle%2Fmod%2Flesson%2Fedit.php%3Fid%3D22%23lesson-0&id={lesson_id}&pageid={pageid}&firstpage={firstpage}&qtype={qtype}&'
    data += f'sesskey={skey}&_qf__lesson_add_page_form_branchtable=1&mform_isexpanded_id_qtypeheading=1&mform_isexpanded_id_headeranswer0=1&mform_isexpanded_id_headeranswer1=0&mform_isexpanded_id_headeranswer2=0&mform_isexpanded_id_headeranswer3=0&mform_isexpanded_id_headeranswer4=0&'
    data += f'title={title}&contents_editor%5Btext%5D={contents}&contents_editor%5Bformat%5D=1&contents_editor%5Bitemid%5D=803713859&layout=1&display=1&answer_editor%5B0%5D=Content+1+Description&jumpto%5B0%5D=0&answer_editor%5B1%5D=&jumpto%5B1%5D=-1&answer_editor%5B2%5D=&jumpto%5B2%5D=-1&answer_editor%5B3%5D=&jumpto%5B3%5D=-1&answer_editor%5B4%5D=&jumpto%5B4%5D=-1&submitbutton=Save+page'

    response = requests.post(url, headers=headers, data=data)
    print(data)
    return response

def get_cat_id(course_name, msession):
    """Get the course id from the course name"""
    soup = BeautifulSoup(get_categories(msession), features="lxml")
    # this class is associated with the course name links and it has the cat_id in the href
    links = soup.find_all(class_='float-left categoryname aalink')
    # class float-left categoryname aalink
    categories = {}
    for link in links:
        # extract category name text and categoryid from html
        # <a class="float-left categoryname aalink" href="http://192.168.0.23/moodle/course/management.php?categoryid=2">Computer Science</a>
        cat_name = link.text
        print(cat_name)
        cat_id = link['href'].split('=')[1]
        categories[cat_name] = cat_id
    try:
        return int(categories[course_name])
    except KeyError:
        return None

def get_courses(msession, course_sname, cat_id):
    """Get the course list"""
    # get the categories from the moodle server
    """
    GET /moodle/course/management.php?categoryid=2 HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Connection: close
    Referer: http://192.168.0.23/moodle/course/management.php
    Cookie: MoodleSession=ettnad827r86kcetmukb6tdmgk; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1
    """
    url = f'http://192.168.0.23/moodle/course/management.php?categoryid={cat_id}'
    headers = {
        "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    r = requests.get(url, headers=headers)
    print(r.text)
    return r.text

def get_course_id(msession, course_name, cat_id):
    """
    get thhe course Id by requesting a page with the cat ID and then looking for the course name
    a class="text-break col pl-0 mb-2 coursename aalink" href="http://192.168.0.23/moodle/course/management.php?categoryid=2&amp;courseid=19">OpenAI GPT</a>
    """
    courses = get_courses(msession, course_name, cat_id)
    soup = BeautifulSoup(courses, features="lxml")
    links = soup.find_all(class_='text-break col pl-0 mb-2 coursename aalink')
    course_dict = {}
    id = None
    for link in links:
        # extract course name text and courseid from html
        print(link.text)
        print(course_name)
        if link.text == course_name:
            print("found course")
            id = link['href'].split('=')[2]
    return id

def get_lessons(msession, cid):
    """Get the lessons from the course
    GET /moodle/course/view.php?id=52 HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/course/modedit.php
    Cookie: MoodleSession=ettnad827r86kcetmukb6tdmgk; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD
    Upgrade-Insecure-Requests: 1

    """
    url = f'http://192.168.0.23/moodle/course/view.php?id={cid}'
    headers = {"Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    r = requests.get(url, headers=headers)
    # use beautiful soul to find the 'aalink stretched-link' class a href's and extract the lesson id
    #  <a href="http://192.168.0.23/moodle/mod/lesson/view.php?id=1776" class=" aalink stretched-link" onclick="">        <span class="instancename">4. Using OpenAI GPT for Natural Language Processing <span class="accesshide "> Lesson</span></span>    </a>
    soup = BeautifulSoup(r.text, features="lxml")
    links = soup.find_all(class_='aalink stretched-link')
    lessons = {}
    for link in links:
        lesson_name = link.text.split("Lesson")[0]
        lesson_name = lesson_name.strip()
        #<a href="http://192.168.0.23/moodle/mod/lesson/view.php?id=1776
        lesson_id = link['href'].split('=')[1]
        lessons[lesson_name] = lesson_id
    return lessons

def get_lesson_id(msession, lesson_name, cid):
    """Get the lesson id from the lesson name"""
    lessons = get_lessons(msession, cid)
    #lesson_name = f" {lesson_name}  ."
    try:
        return int(lessons[lesson_name])
    except KeyError:
        return None

def update_inplace(msession,skey, arg_itemid, arg_component, arg_itemtype, arg_value,methodname='core_update_inplace_editable', index=0):
    """Update the lesson inplace
    POST /moodle/lib/ajax/service.php?sesskey=ae0Dko8V16&info=core_update_inplace_editable HTTP/1.1
    Host: 192.168.0.23
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Language: en-CA,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/json
    X-Requested-With: XMLHttpRequest
    Content-Length: 155
    Origin: http://192.168.0.23
    Connection: close
    Referer: http://192.168.0.23/moodle/course/view.php?id=69
    Cookie: MoodleSession=ceon26p515h0608ftfupliludb; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD

    [{"index":0,"methodname":"core_update_inplace_editable","args":{"itemid":"772","component":"format_topics","itemtype":"sectionnamenl","value":"YYYYYYYY"}}]
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    url = f"http://192.168.0.23/moodle/lib/ajax/service.php?sesskey={skey}&info=core_update_inplace_editable"
    data = f'[{{"index":{index},"methodname":"{methodname}","args":{{"itemid":"{arg_itemid}","component":"{arg_component}","itemtype":"{arg_itemtype}","value":"{arg_value}"}}}}]'
    response = requests.post(url, headers=headers, data=data)
    
    print(data)

def get_topic_ids(msession, skey, cid):
    """Get the topic ids for the course"""
    url = f'http://192.168.0.23/moodle/course/view.php?id={cid}'
    headers = {"Cookie": f"MoodleSession={msession}; MOODLEID1_=%25E0%2526%257D%25BA6%2518%25E6%257D%25FD"}
    r = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(r.text, features="lxml")
    #use beautiful soup to find class "sectionname course-content-item d-flex align-self-stretch align-items-center mb-0"
    matches = soup.find_all(class_='sectionname course-content-item d-flex align-self-stretch align-items-center mb-0')
    topics = []
    for m in matches:
        #skip data-number="0" since it is the "General section"
        if m.get('data-number') == '0':
            continue
        print(m.get('data-number'), m.get('data-id'))
        topics.append(m.get('data-id'))
    return topics
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file", default="Pokemon-content.json", help="The source course file to read from")
    args = parser.parse_args()
    source_file = args.file
    #TODO implement function to authenticate and get the session keys
    msession = 'ceon26p515h0608ftfupliludb'
    #this is used for some admin operations
    skey = 'ae0Dko8V16'
    gen_image_setting = True
    #gen_image("a big ole donuit")
    #exit()

    with open(source_file) as f:
        data = json.load(f)
        course_name = data["name"]
        course_sname = data["sname"]
        course_category = data["cat"]
        course_description = data["description"]

        # get the course category name
        cat_id = get_cat_id(course_category, msession)
        if cat_id is None:
            print("creating category")
            #TODO #Create Category Description text
            create_category(msession, skey, course_category, "Placeholder Description", id=0, parent=0)
            cat_id = get_cat_id(course_category, msession)
            if cat_id is None:
                print("Error creating category")
                exit()
    # create the category
    
        # check to see if the corse exists
        print(f"categoryid {cat_id} found, checking to see if course exists")
        if get_course_id(msession, course_sname, cat_id) == True:
            print("course exists")
            # if it does, delete it
        print("creating course")
        # def create_course(cookie, category_id, course_name, course_sname, course_description, visible="1", id=0, category=0):
        create_course(msession, skey, cat_id, course_name,
                    urllib.parse.quote(course_sname), urllib.parse.quote(course_description))
        cid = get_course_id(msession, course_name, cat_id)
        print(cid)
        if cid is None:
            print("Error creating course")
            exit()
        section_id = 1  # chapter counter to drive the section id, skip 0 because its "General"
        
        #Lets write each chapter
        for chapter in data.keys():
            if chapter == "description":
                print("description", data["description"])
                is_lesson = False
                is_description = True
            elif chapter == "quiz":
                print("quiz", chapter)
                is_lesson = False
            elif chapter == "name":
                course_name = data["name"]
                is_lesson = False
                pass
            elif chapter == "sname":
                course_sname = data["sname"]
                is_lesson = False
                pass
            elif chapter == "cat":
                course_category = data["cat"]
                is_lesson = False
                pass
            else:
                # create a chapter in course using the id.
                # user data[chapter]["description"] for the description
                # use the key as the chapter name
                # loop through the lessons


                print("chapter", chapter)
                description = f"<p dir=\"ltr\">{data[chapter]['description']}</p>"
                chapter_description = data[chapter]["description"]


                if gen_image_setting == True:
                    #image_html = gen_image_concept(concept, "pokemon", chapter)
                    image_html = gen_image_chapter(chapter, course_name)
                    description = description + image_html
                print(description)
                for lesson in data[chapter].keys():
                    if lesson == "description":
                        is_lesson = False
                        is_description = True
                    elif lesson == "quiz":
                        is_lesson = False
                        is_quiz = True
                        pass

                    else:
                        is_lesson = True
                        print("lesson", lesson)
                        # create a bold html string containing the lesson name
                        header = f"<p dir=\"ltr\" style=\"text-align: left;\"><strong>{lesson}</strong></p>"
                        lesson_html = gen_image_lesson(lesson, chapter, course_name)
                        header += lesson_html
                        
                        # create html string containing the lesson description
                        # create html string containing the lesson content
                        # create a lesson in the chapter for this course
                        # create lesson in chapter using data[chapter][lesson]["description"]
                        lesson_data = []
                        lesson_data.append(header)
                        for XXX in data[chapter][lesson]:
                            if XXX == "description":
                                pass
                            elif XXX == "quiz":
                                pass
                            else:
                                # concept_content = "<br>".join(
                                #     data[chapter][lesson][XXX].keys())
                                # print(concept_content)

                                lesson_data.append(data[chapter][lesson][XXX].strip())

                        lesson_data_joined = "<p>".join(lesson_data)

                    if is_lesson:
                        add_resource(msession, skey, urllib.parse.quote(lesson), urllib.parse.quote(description), cid, section_id,
                                    "15", resource_type="lesson", mediafile="74023563")
                        
                        lid = get_lesson_id(msession, lesson, cid)
                        #add_lesson_content(msession, skey, id, pageid, firstpage, qtype, title, contents):
                        add_lesson_content(msession, skey,lid, "0", "1", "20", header, lesson_data_joined.encode('utf-8'))

                        #create a gift file from the data in ["quiz"]
                        #gift = data[chapter]["quiz"]
                        #print(gift)
                section_id += 1
        chapter_ids = get_topic_ids(msession, skey, cid)
        print(data.keys())

        #now lets rename the sections to the chapter names
        chapter_index = 0
        for chapter_name in data.keys():
            if chapter_name == "description":
                pass
            elif chapter_name == "quiz":
                pass
            elif chapter_name == "name":
                pass
            elif chapter_name == "sname":
                pass
            elif chapter_name == "cat":
                pass
            else:
                update_inplace(msession,skey, arg_itemid=chapter_ids[chapter_index], arg_component="format_topics", arg_itemtype="sectionnamenl", arg_value=chapter_name, methodname='core_update_inplace_editable', index=0)
                chapter_index += 1


if __name__ == "__main__":
    main()
