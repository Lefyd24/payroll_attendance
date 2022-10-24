import base64
from ast import For
from distutils.log import error
from time import time
import openpyxl as xl
import os
import pandas as pd
from warnings import filterwarnings
from datetime import datetime
import time
from colorama import Fore, Style, Back
import streamlit as st
import streamlit.components.v1 as components
import fnmatch
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_option_menu import option_menu
from streamlit_disqus import st_disqus

from prlWages import wages
from prlAttendance import analysis
from cardlink import cardlink_auto


st.set_page_config("Project Automator", "/Users/lefterisfthenos/Desktop/Python Projects/YNS/Picture 1.png" , layout='wide')


filterwarnings("ignore")

#! pattern for daily attendances

with open("style.css") as style:
    st.markdown(f"<style>{style.read()}</style>", unsafe_allow_html=True)

#! ################ THEMING ################################

@st.experimental_memo
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
img = get_img_as_base64("Picture 1.png")
img_sidebar = get_img_as_base64("lindos.webp")
img_new = get_img_as_base64("nnew.webp")
#header {{visibility: hidden;}}
page_bg_img = f"""
<style>
##MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: 15%;
background-position: 100% 2%;
background-repeat: no-repeat;
background-attachment: fixed;
}}

[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img_new}");
background-size: 80%;
background-position: -180% 70%; 
background-repeat: no-repeat;
background-attachment: fixed;
}}
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

login = check_password()
if login:
    #! ################ PAGES ################################
    sb = st.sidebar
    #sb.header("CHOOSE PROJECT")
    proj_option = option_menu(menu_title=None,
                              options=["Home", "Payroll", "Accounting"],
                              icons = ["bi bi-house", "bi bi-currency-exchange", "bi bi-book"],
                              orientation="horizontal")
    #project = sb.selectbox("Options", options=["Home","Accounting","Payroll"])
    if proj_option != "Home":
        sb.header("B.I. AUTOMATOR")
    else:
        #sb.header("Process Automator")
        pass
    if proj_option == "Home":
        sb.error("Home")
    elif proj_option == "Payroll":
        task = sb.selectbox("Choose Task",
                            options=["Payroll Attendance", "Payroll Wages"])
        if task == "Payroll Attendance":
            st.title("Payroll Attendance Files' Processor")
            st.info("You need to delete the file 'Payroll_Attendance.xlsx' from the folder, before you begin the process, otherwise the program will eventually crash.")
            files = st.file_uploader("Upload the Daily Attendance files of the day.\nFiles must be named as 'HLCode - HLName- Daily Attendance_22xxxx.xlsx'  ", type=["xls", "xlsx", "xlsm"], accept_multiple_files=True,label_visibility='visible')
            if files:
                filenames = [file.name for file in files]
                filenames_set = set(filenames)
                if len(filenames) != len(filenames_set):
                    st.warning("Warning - You've uploaded duplicate files! Please check them again before running the process.")
                else:
                    submit = st.button("Begin the process")
                    if submit:
                        skipped_files, time_spent = analysis(files)
                        if skipped_files:
                            st.error(f"Warning - The following files were not valid:")
                            st.dataframe(pd.DataFrame(list(skipped_files)))
                        elif time_spent == 0:
                            pass
                        else:
                            st.download_button("Press to download PayrollAttendance.xlsx",
                                               data=open("Payroll_Attendance.xlsx", 'rb'),
                                               file_name="PayrollAttendance.xlsx")

                        st.success(f'Time Spent: {round(time_spent,2)}"')
        elif task == "Payroll Wages":
            st.title("Payroll Wages Files' Processor")
            files = st.file_uploader(
                "Upload the final month's wages xlsx file",
                type=["xls", "xlsx", "xlsm"], accept_multiple_files=True)
            if files:
                filenames = [file.name for file in files]
                filenames_set = set(filenames)
                if len(filenames) != len(filenames_set):
                    st.warning(
                        "Warning - You've uploaded duplicate files! Please check them again before running the process.")
                else:
                    submit = st.button("Begin the process")
                    if submit:
                        time_spent = wages(files)
                        if time_spent != 0:
                            st.success(f'Time Spent: {round(time_spent, 2)}"')
                            st.info("In case you cannot download the file, please run the process again.")
                            st.download_button("Press to download PayrollWages.xlsx",
                                               data=open("PayrollWages.xlsx", 'rb'), file_name="PayrollWages.xlsx")
                        else:
                            pass
            #st.dataframe(cursor.fetchall())
    elif proj_option == "Accounting":
        st.info("This page is currently locked.")
        #cardlink.cardlink_auto()

    else:
        pass
