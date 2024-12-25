import nltk
nltk.download('stopwords')
nltk.download('punkt')
import os
from supabase import create_client
import streamlit as st
import pandas as pd
import base64, random
import time, datetime
import sys
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
os.environ['PAFY_BACKEND'] = "internal"
import pafy
import plotly.express as px
import re

# Supabase configuration
supabase_url = "https://duiomhgeqricsyjmeamr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1aW9taGdlcXJpY3N5am1lYW1yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ5NDczNTMsImV4cCI6MjA1MDUyMzM1M30.VRVw8jQLSQ3IzWhb2NonPHEQ2Gwq-k7WjvHB3WcLe48"
supabase = create_client(supabase_url, supabase_key)


def connect_db():
    """Create and return Supabase client."""
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None
    
def check():
    """Check if the user is logged in and fetch user details."""
    if not st.session_state.get("logged_in"):
        st.warning("Please log in first.")
        return None
    
    if st.session_state.get("user_type", "").lower() != "user":
        st.error("Access denied. This page is for users only.")
        return None
    
    user_email = st.session_state.get("email")
    try:
        response = supabase.table('users').select("*").eq('email', user_email).execute()
        if response.data:
            return response.data[0]  # Return the first matching user
        else:
            st.error("User details not found.")
    except Exception as e:
        st.error(f"Error fetching user details: {e}")
    
    return None

def display_user_dashboard(user):
    """Display the user dashboard."""
    st.subheader("User Dashboard")
    st.write(f"Welcome, {user['username']}!")
    st.write("Your Profile:")
    st.write(f"Full Name: {user['full_name']}")
    st.write(f"Email: {user['email']}")

def extract_keywords_from_resume(resume_text):
    keywords = []
    patterns = [r"\b(Developer|Engineer|Manager|Tutor|Designer|Analyst)\b", 
                r"\b(Python|Java|SQL|Teaching|Communication|Leadership)\b"]
    for pattern in patterns:
        keywords.extend(re.findall(pattern, resume_text, re.IGNORECASE))
    return set(keywords)

def recommend_jobs_from_database(keywords, reco_field):
    """Query Supabase to fetch jobs matching reco_field and keywords."""
    try:
        # Convert keywords to lowercase for case-insensitive matching
        keyword_list = [kw.lower() for kw in keywords]
        
        # Query jobs table
        response = supabase.table('job_listings').select("*").execute()
        
        # Filter results in Python (since Supabase doesn't support REGEXP)
        recommended_jobs = []
        for job in response.data:
            if job['job_subject'].lower() == reco_field.lower():
                # Check if any keyword matches the required_skills
                if any(kw in job['required_skills'].lower() for kw in keyword_list):
                    recommended_jobs.append({
                        'job_title': job['job_title'],
                        'job_subject': job['job_subject'],
                        'location': f"{job['city']}, {job['state']}",
                        'required_skills': job['required_skills']
                    })
                    
        return recommended_jobs
    except Exception as e:
        st.error(f"Error querying database: {e}")
        return []

def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

def insert_data(user_id, name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    """Insert user data into the user_data table in Supabase."""
    try:
        data = {
            'user_id': user_id,
            'Name': name,
            'Email_ID': email,
            'resume_score': str(res_score),
            'Timestamp': timestamp,
            'Page_no': str(no_of_pages),
            'Predicted_Field': reco_field,
            'User_level': cand_level,
            'Actual_skills': skills,
            'Recommended_skills': recommended_skills,
            'Recommended_courses': courses
        }
        
        response = supabase.table('user_data').insert(data).execute()
        if not response.data:
            st.error("Failed to insert data")
    except Exception as e:
        st.error(f"Error inserting data: {e}")

def run():
    # Create upload directory if it doesn't exist
    upload_dir = './Uploaded_Resumes'
    os.makedirs(upload_dir, exist_ok=True)
    
    user_id = check()  # Call check to verify login and get user_id
    if user_id is None:
        return
        
    display_user_dashboard(user_id)
    st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload your resume, and get smart recommendations</h5>''',
                    unsafe_allow_html=True)
    
    pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
    if pdf_file is not None:
        try:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
                
            # Generate a unique filename to avoid conflicts
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{pdf_file.name}"
            save_image_path = os.path.join(upload_dir, safe_filename)
            
            # Save the uploaded file
            try:
                with open(save_image_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                
                # Verify file exists before proceeding
                if not os.path.exists(save_image_path):
                    st.error("Failed to save the uploaded file.")
                    return
                    
                show_pdf(save_image_path)
                resume_data = ResumeParser(save_image_path).get_extracted_data()
                
                if resume_data:
                    # Rest of your existing code remains the same
                    resume_text = pdf_reader(save_image_path)
                    
                    st.header("**Resume Analysis**")
                    st.success("Hello "+ resume_data['name'])
                    st.subheader("**Your Basic info**")
                    try:
                        st.text('Name: '+resume_data['name'])
                        st.text('Email: ' + resume_data['email'])
                        st.text('Contact: ' + resume_data['mobile_number'])
                        st.text('Resume pages: '+str(resume_data['no_of_pages']))
                    except:
                        pass
                    # Extract keywords from the uploaded resume
                    keywords = extract_keywords_from_resume(pdf_reader(save_image_path))
                    job_recommendations = recommend_jobs_from_database(keywords, reco_field)
                    
                    # In Check.py, replace the apply button section with this:
                    st.subheader("Job Recommendation 💼")
                    if job_recommendations:
                        for job in job_recommendations:
                            st.markdown(f"""
                            **Job Title:** {job['job_title']}  
                            **Subject Area:** {job['job_subject']}  
                            **Location:** {job['location']}  
                            **Required Skills:** {job['required_skills']}  
                            """)
                            if st.button(f"Apply for {job['job_title']}", key=f"apply_{job['job_title']}"):
                                # Set session state variables for job details
                                try:
                                    st.session_state['selected_job_title'] = job['job_title']
                                    st.session_state['selected_job_subject'] = job['job_subject']
                                    st.session_state['selected_job_location'] = job['location']
                                    st.session_state['selected_job_skills'] = job['required_skills']
                                    
                                    # Change the page in session state
                                    st.session_state['page'] = "apply"
                                    st.rerun()  # Replace experimental_rerun() with rerun()
                                except Exception as e:
                                    st.error(f"Error switching page: {e}")
                    else:
                        st.warning("No matching jobs found.")
                    cand_level = ''
                    if resume_data['no_of_pages'] == 1:
                        cand_level = "Fresher"
                        st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                    elif resume_data['no_of_pages'] == 2:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif resume_data['no_of_pages'] >=3:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)

                    # st.subheader("**Skills Recommendation💡**")
                    ## Skill shows
                    keywords = st_tags(label='### Your Current Skills',
                    text='See our skills recommendation below',
                        value=resume_data['skills'],key = '1  ')
                    
                    ##  keywords
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                                'javascript', 'angular js', 'c#', 'flask', 'C++']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                
                    # Normalize resume skills
                    resume_skills = [skill.lower().strip() for skill in resume_data['skills']]
                    recommended_skills = []
                    reco_field = ''
                    rec_course = ''
                    ## Courses recommendation
                    for i in resume_data['skills']:
                        ## Data science recommendation
                        if i.lower() in ds_keyword:
                            print(i.lower())
                            reco_field = 'Data Science'
                            st.success("** Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '2')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ds_course)
                            break

                        ## Web development recommendation
                        elif i.lower() in web_keyword:
                            print(i.lower())
                            reco_field = 'Web Development'
                            st.success("** Our analysis says you are looking for Web Development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '3')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(web_course)
                            break

                        ## Android App Development
                        elif i.lower() in android_keyword:
                            print(i.lower())
                            reco_field = 'Android Development'
                            st.success("** Our analysis says you are looking for Android App Development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '4')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(android_course)
                            break

                        ## IOS App Development
                        elif i.lower() in ios_keyword:
                            print(i.lower())
                            reco_field = 'IOS Development'
                            st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                            recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '5')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ios_course)
                            break

                        ## Ui-UX Recommendation
                        elif i.lower() in uiux_keyword:
                            print(i.lower())
                            reco_field = 'UI-UX Development'
                            st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '6')
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                            rec_course = course_recommender(uiux_course)
                            break

                    ## Insert into table
                    ts = time.time()
                    cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    timestamp = str(cur_date+'_'+cur_time)

                    ### Resume writing recommendation
                    st.subheader("**Resume Tips & Ideas💡**")
                    resume_score = 0
                    if 'Objective' in resume_text:
                        resume_score = resume_score+20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                    if 'Declaration'  in resume_text:
                        resume_score = resume_score + 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration/h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)

                    if 'Hobbies' or 'Interests'in resume_text:
                        resume_score = resume_score + 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                    if 'Achievements' in resume_text:
                        resume_score = resume_score + 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                    if 'Projects' in resume_text:
                        resume_score = resume_score + 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                    st.subheader("**Resume Score📝**")
                    st.markdown(
                        """
                        <style>
                            .stProgress > div > div > div > div {
                                background-color: #d73b5c;
                            }
                        </style>""",
                        unsafe_allow_html=True,
                    )
                    my_bar = st.progress(0)
                    score = 0
                    for percent_complete in range(resume_score):
                        score +=1
                        time.sleep(0.1)
                        my_bar.progress(percent_complete + 1)
                    st.success('** Your Resume Writing Score: ' + str(score)+'**')
                    st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")
                    st.balloons()

                    insert_data(user_id, resume_data['name'], resume_data['email'], 0, timestamp,
                                resume_data['no_of_pages'], reco_field, cand_level, str(resume_data['skills']),
                                str(recommended_skills), str(rec_course))
                    
                    ## Resume writing video
                    st.header("**Bonus Video for Resume Writing Tips💡**")
                    resume_vid = random.choice(resume_videos)
                    res_vid_title = fetch_yt_video(resume_vid)
                    st.subheader("✅ **"+res_vid_title+"**")
                    st.video(resume_vid)

                    ## Interview Preparation Video
                    st.header("**Bonus Video for Interview Tips💡**")
                    interview_vid = random.choice(interview_videos)
                    int_vid_title = fetch_yt_video(interview_vid)
                    st.subheader("✅ **" + int_vid_title + "**")
                    st.video(interview_vid)
            except Exception as e:
                st.error(f"Error saving file: {str(e)}")
                return
                
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
            return
        
        finally:
            # Cleanup: Remove the temporary file after processing
            try:
                if 'save_image_path' in locals() and os.path.exists(save_image_path):
                    os.remove(save_image_path)
            except Exception as e:
                st.warning(f"Warning: Could not remove temporary file: {str(e)}")

                
if __name__ == "__main__":
    run()