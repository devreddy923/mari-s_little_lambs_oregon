import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
from dateutil.relativedelta import relativedelta

# Set Streamlit to always use dark mode and wide mode
st.set_page_config(page_title="Mari's Little Lambs", layout="wide")

# Inject custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@200&display=swap');

    html, body, h1, h2, h3, h4, h5, h6, div, span, p, .stButton>button, .stFileUploader, .stTextInput>div>div>input {
        font-family: 'Nunito', sans-serif;
        font-weight: 200;
    }

    .title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 20px;
    }

    .metric-box {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        margin: 15px;
        background-color: transparent;
        border-radius: 10px;
        border: 2px solid;  
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        flex: 1 1 22%; 
        min-height: 150px; 
    }

    .metric-box h4 {
        margin: 0;
        font-size: 1em;
    }

    .metric-box p {
        font-size: 1.5em;
        font-weight: bold;
        color: #4CAF50;
        margin: 5px 0 0 0;
        align-self: center;
    }

    .availability-yes, .availability-no {
        font-size: 1.5em;
        font-weight: bold;
    }

    .availability-yes {
        color: green;
    }

    .availability-no {
        color: red;
    }

    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: black;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    .horizontal-table {
        width: 100%;
        border-collapse: collapse;
        text-align: center;
        margin: 0 auto;
    }

    .horizontal-table th, .horizontal-table td {
        padding: 10px;
        text-align: center;
        border: 1px solid #ddd;
    }

    .horizontal-table th {
        background-color: transparent;
        font-weight: bold;  /* Bold header text */
        font-family: 'Nunito', sans-serif; /* Ensure Nunito font */
    }

    .horizontal-table td {
        background-color: transparent;
        color: white;
        font-weight: bold;  /* Bold cell text */
        font-size: 1.2em; /* Increase the font size */
        font-family: 'Nunito', sans-serif; /* Ensure Nunito font */
    }

    .dark-mode .horizontal-table th, .dark-mode .horizontal-table td.table-header {
        color: white !important;  /* Change to white for dark mode */
    }

    .light-mode .horizontal-table th, .light-mode .horizontal-table td.table-header {
        color: black !important;  /* Change to black for light mode */
    }

    .calendar {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        margin: 20px 0;
    }

    .calendar-day {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        position: relative;
        background-color: #222;
        color: white;
        border: 1px solid #555;
    }

    .calendar-day:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    .calendar-header {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        margin: 20px 0;
        font-weight: bold;
        text-align: center;
    }

    .no-data {
        background-color: lightgray;
        color: #888;
    }

    .weekend {
        background-color: lightgray;
    }

    .red {
        background-color: red;
    }

    .green {
        background-color: green;
    }

    .centered {
        text-align: center;
        margin: 0 auto;
    }

    .metric-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 40px; /* Increase the gap between metric boxes */
    }

    .metric-container .metric-box {
        margin-bottom: 30px; /* Increase vertical spacing between rows */
    }

    .spacing-row {
        margin-bottom: 40px; /* Increase vertical spacing between rows of metrics */
    }

    /* Explicitly targeting the specific header */
    .horizontal-table th.kids-in-class-header {
        font-weight: bold;  /* Bold header text */
        font-family: 'Nunito', sans-serif; /* Ensure Nunito font */
    }

    .dark-mode .horizontal-table th.kids-in-class-header, .dark-mode .horizontal-table th.table-header {
        color: white !important;  /* Change to white for dark mode */
    }

    .light-mode .horizontal-table th.kids-in-class-header, .light-mode .horizontal-table th.table-header {
        color: black !important;  /* Change to black for light mode */
    }

    </style>
    """, unsafe_allow_html=True)

# Inject JavaScript to change the colors dynamically
st.markdown("""
    <script>
    function setTableHeaderColors() {
        const headers = document.querySelectorAll('.horizontal-table th, .horizontal-table td.table-header');
        const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        headers.forEach(header => {
            if (theme === 'dark') {
                header.style.color = 'white';
            } else {
                header.style.color = 'black';
            }
        });
    }
    document.addEventListener('DOMContentLoaded', setTableHeaderColors);
    document.addEventListener('click', setTableHeaderColors);  // Adjust colors on interaction
    </script>
    """, unsafe_allow_html=True)

# Define the classes and their age ranges
classes = {
    'Infants': (0, 1),
    'Wobblers': (1, 2),
    'Older Toddlers': (2, 3),
    'Preschool': (3, 5)
}

class Student:
    def __init__(self, name, date_of_birth, schedule, program_type, start_date=None):
        self.name = name
        self.date_of_birth = datetime.combine(date_of_birth, datetime.min.time())  # Convert date to datetime
        self.level = self.calculate_level_by_dob()
        self.schedule = schedule
        self.program_type = program_type
        self.start_date = start_date
        self.existing_student = False
        self.promotion_date = None

    def calculate_level_by_dob(self):
        age = (datetime.now() - self.date_of_birth).days / 365.25
        for level, (min_age, max_age) in enumerate(classes.values(), start=1):
            if min_age <= age < max_age:
                return level
        return None  # Return None if age does not fall into any range

    def get_class_name(self):
        age = (datetime.now() - self.date_of_birth).days / 365.25
        for class_name, (min_age, max_age) in classes.items():
            if min_age <= age < max_age:
                return class_name
        return "Graduated"  # Indicates the child has graduated out of daycare

    def __str__(self):
        date_of_birth_str = self.date_of_birth.strftime('%Y-%m-%d')
        return (f"Student(Name: {self.name}, Date of Birth: {date_of_birth_str}, Level: {self.level}, "
                f"Schedule: {self.schedule}, Program Type: {self.program_type}, Start Date: {self.start_date}, "
                f"Class: {self.get_class_name()})")

class Classroom:
    def __init__(self, capacity_levels):
        self.capacity_levels = capacity_levels
        self.level_queues = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
        self.level_promotedQueues = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
        self.level_promotedQueues2 = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
        self.students = []
        self.graduated_students = []

    def read_existing_data(self, active_df, hold_df):
        active_df = active_df[['First Name', 'Dob', 'Room', 'Time Schedule', 'Tags', 'Admission Date']]
        active_df = active_df.rename(
            columns={'First Name': 'Name', 'Dob': 'DoB', 'Room': 'Room', 'Time Schedule': 'Schedule',
                     'Tags': 'Program Type', 'Admission Date': 'Start Date'})
        active_df['Program Type'] = active_df['Program Type'].str.contains('FlexEd').map(
            {True: 'Flexible', False: 'Fixed'})

        hold_df = hold_df[['First Name', 'Dob', 'Room', 'Time Schedule', 'Tags', 'Admission Date']]
        hold_df = hold_df.rename(
            columns={'First Name': 'Name', 'Dob': 'DoB', 'Room': 'Room', 'Time Schedule': 'Schedule',
                     'Tags': 'Program Type', 'Admission Date': 'Admission Date'})
        hold_df['Program Type'] = hold_df['Program Type'].str.contains('FlexEd').map({True: 'Flexible', False: 'Fixed'})

        def convert_days(schedule):
            day_mapping = {
                'M': 'Monday',
                'T': 'Tuesday',
                'W': 'Wednesday',
                'Th': 'Thursday',
                'F': 'Friday'}

            days = schedule.split(', ')
            full_day_names = []

            for day in days:
                day_abbr = day.split(' ')[0]
                if day_abbr in day_mapping:
                    full_day_names.append(day_mapping[day_abbr])

            return ','.join(full_day_names)

        active_df['Schedule'] = active_df['Schedule'].apply(convert_days)
        active_df['Schedule'] = active_df['Schedule'].apply(lambda x: x.split(','))
        hold_df['Schedule'] = hold_df['Schedule'].apply(convert_days)
        hold_df['Schedule'] = hold_df['Schedule'].apply(lambda x: x.split(','))

        for _, row in active_df.iterrows():
            if pd.notna(row['DoB']):
                student = Student(row['Name'], datetime.strptime(str(row['DoB']), '%Y-%m-%d %H:%M:%S'),
                                  row['Schedule'], row['Program Type'],
                                  datetime.strptime(str(row['Start Date']), '%Y-%m-%d %H:%M:%S'))
                student.promotion_date = self.calculate_promotion_date(student)
                student.existing_student = True
                self.students.append(student)

        for _, row in hold_df.iterrows():
            if pd.notna(row['DoB']) and pd.notna(row['Admission Date']):
                student = Student(row['Name'], datetime.strptime(str(row['DoB']), '%Y-%m-%d %H:%M:%S'),
                                  row['Schedule'], row['Program Type'],
                                  datetime.strptime(str(row['Admission Date']), '%Y-%m-%d %H:%M:%S'))
                student.promotion_date = self.calculate_promotion_date(student)
                self.level_queues[student.level].append(student)

    def calculate_daily_strength(self):
        daily_strength = {
            "Monday": {1: 0, 2: 0, 3: 0, 4: 0},
            "Tuesday": {1: 0, 2: 0, 3: 0, 4: 0},
            "Wednesday": {1: 0, 2: 0, 3: 0, 4: 0},
            "Thursday": {1: 0, 2: 0, 3: 0, 4: 0},
            "Friday": {1: 0, 2: 0, 3: 0, 4: 0}
        }

        for student in self.students:
            if student.existing_student and student.schedule is not None:
                for day in student.schedule:
                    for level in range(1, 5):
                        if student.level == level:
                            daily_strength[day.strip()][level] += 1

        df = pd.DataFrame(daily_strength)
        return df

    def kpi_calculate(self, level):
        total_active_students = [0] * 4
        total_hold_students = [0] * 4
        graduating_soon = [0] * 4
        admitted_recent = [0] * 4
        i = 0
        j = 0
        k = 0
        for student in self.students:
            if student.level == level:
                i += 1
                total_active_students[level - 1] = i
                if student.promotion_date <= (datetime.now() + timedelta(60)):
                    j += 1
                    graduating_soon[level - 1] = j
                if student.promotion_date >= (datetime.now() + timedelta(300)):
                    j += 1
                    graduating_soon[level - 1] = j
                if student.start_date >= (datetime.now() - timedelta(60)):
                    k += 1
                    admitted_recent[level - 1] = k
        total_hold_students[level - 1] = len(self.level_queues[level])

        return total_active_students, total_hold_students, graduating_soon, admitted_recent

    def apply_for_admission(self, applicant, preferred_joining_date=None):
        slot_found = False
        schedule = applicant.schedule
        if preferred_joining_date is None:
            preferred_joining_date = datetime.now()

        preferred_joining_date = datetime.combine(preferred_joining_date, datetime.min.time())  # Ensure datetime type
        self.update_members(preferred_joining_date, None)
        level = applicant.level
        flexible_students = [student for student in self.students if
                             student.existing_student and student.level == level and student.program_type == "Flexible"]

        if self.can_join_level(schedule, level):
            slot_found = True
            return preferred_joining_date, schedule, False
        elif flexible_students:
            slot_found = True
            return (datetime.now() + timedelta(32)), schedule, True
        else:
            next_dates_list = self.calculate_next_possible_dates(level, preferred_joining_date)
            next_dates_list_sorted = sorted(next_dates_list)
            prev_date = None
            for next_date in next_dates_list_sorted:
                current_age = (next_date - applicant.date_of_birth).days / 365
                if current_age > self.get_age_limit(applicant.level):
                    break
                self.update_members(next_date, None)
                if self.can_join_level(schedule, level):
                    slot_found = True
                    break
                prev_date = next_date
            if slot_found:
                return next_date, schedule, False
            else:
                return False, False, False

    def update_members(self, preferred_joining_date, level):
        if level is None:
            for level in range(1, 5):
                self.promote_students(level, preferred_joining_date)
                self.update_waiting_list(level)
                self.admit_students_from_waiting(level, preferred_joining_date)
        else:
            self.promote_students(level, preferred_joining_date)
            self.update_waiting_list(level)
            self.admit_students_from_waiting(level, preferred_joining_date)

    def promote_students(self, level, preferred_joining_date):
        for student in self.students:
            if student.existing_student and student.level == level and preferred_joining_date >= student.promotion_date:
                next_level = student.level + 1
                schedule = student.schedule
                if next_level < 4 and self.can_join_level(schedule, next_level):
                    student.level = next_level
                    student.promotion_date = self.calculate_promotion_date(student, student.promotion_date)
                elif next_level < 4:
                    student.level = next_level
                    student.start_date = student.promotion_date
                    student.promotion_date = self.calculate_promotion_date(student, student.promotion_date)
                    self.level_promotedQueues[student.level].append(student)
                    self.students.remove(student)
                elif student.level == 4 and preferred_joining_date >= student.promotion_date:
                    self.students.remove(student)
                    self.graduated_students.append(student)

    def update_waiting_list(self, level):
        if len(self.level_promotedQueues[level]) > 0:
            self.level_promotedQueues[level] = sorted(self.level_promotedQueues[level], key=lambda x: x.start_date)
            self.level_promotedQueues[level] = deque(self.level_promotedQueues[level])
        if len(self.level_queues[level]) > 0:
            self.level_queues[level] = sorted(self.level_queues[level], key=lambda x: x.start_date)
            self.level_queues[level] = deque(self.level_queues[level])

    def admit_students_from_waiting(self, level, preferred_joining_date):
        while ((self.calculate_daily_strength().loc[level] != 0).all()):
            if len(self.level_promotedQueues[level]) > 0:
                student = self.level_promotedQueues[level].popleft()
                schedule = student.schedule
                if self.can_join_level(schedule, level):
                    self.students.append(student)
                else:
                    self.level_promotedQueues2[level].append(student)
            elif len(self.level_queues[level]) > 0:
                student = self.level_queues[level].popleft()
                schedule = student.schedule
                if student.start_date <= preferred_joining_date and self.can_join_level(schedule, level):
                    student.existing_student = True
                    student.promotion_date = self.calculate_promotion_date(student, student.start_date)
                    self.students.append(student)
                else:
                    self.level_promotedQueues2[level].append(student)
            else:
                break
        self.level_promotedQueues[level].extend(self.level_promotedQueues2[level])

    def can_join_level(self, schedule, level):
        level_capacity = self.capacity_levels[level - 1]
        for day in schedule:
            students_in_level = sum(1 for student in self.students if
                                    student.level == level and student.schedule and day.lower() in [d.lower() for d in
                                                                                                    student.schedule])
            if students_in_level >= level_capacity:
                return False
        return True

    def calculate_level(self, dob):
        age = (datetime.now() - dob).days / 365
        if 0 <= age < 1:
            return 1
        elif 1 <= age < 2:
            return 2
        elif 2 <= age < 3:
            return 3
        elif 3 <= age <= 5:
            return 4
        else:
            return None

    def calculate_next_possible_dates(self, level, preferred_joining_date):
        nextPromotedDates = []
        if level > 2:
            nextPromotedDates.extend(student.promotion_date for student in self.students if
                                     student.level == level - 2 and student.promotion_date >= preferred_joining_date and student.promotion_date is not None)
            nextPromotedDates.extend(student.promotion_date for student in self.level_queues[level - 2] if
                                     student.promotion_date >= preferred_joining_date and student.promotion_date is not None)
        if level > 1:
            nextPromotedDates.extend(student.promotion_date for student in self.students if
                                     student.level == level - 1 and student.promotion_date >= preferred_joining_date and student.promotion_date is not None)
            nextPromotedDates.extend(student.promotion_date for student in self.level_queues[level - 1] if
                                     student.promotion_date >= preferred_joining_date and student.promotion_date is not None)

        nextPromotedDates.extend(student.promotion_date for student in self.students if
                                 student.level == level and student.promotion_date >= preferred_joining_date and student.promotion_date is not None)
        nextPromotedDates.extend(student.promotion_date for student in self.level_queues[level] if
                                 student.promotion_date >= preferred_joining_date and student.promotion_date is not None)
        return nextPromotedDates

    def calculate_promotion_date(self, student, inputDate=datetime.now(), promotion_date=None):
        if promotion_date is None:
            current_level_age_limit = self.get_age_limit(student.level)
            next_level_age_limit = self.get_age_limit(student.level + 1) if student.level < 4 else 5
            current_age = (inputDate - student.date_of_birth).days / 365
            promotion_date = student.date_of_birth + relativedelta(years=current_level_age_limit)
        return promotion_date

    def get_age_limit(self, level):
        if level == 1:
            return 1
        elif level == 2:
            return 2
        elif level == 3:
            return 3
        elif level == 4:
            return 5

    def printStudent(self, level):
        for student in self.students:
            if student.level == level:
                print(student.name)
                print(str(student.date_of_birth))
                print(student.existing_student)
                print(str(student.promotion_date))
                print("-------------------******************-------------------")


def get_correct_class_by_age(age):
    if age is None:
        return None
    if 0 <= age < 1:
        return 'Infants'
    elif 1 <= age < 2:
        return 'Wobblers'
    elif 2 <= age < 3:
        return 'Older Toddlers'
    elif 3 <= age < 5:
        return 'Preschool'
    else:
        return 'Graduated'  # Indicates the child has graduated out of daycare


def is_scheduled_to_attend(schedule, current_date):
    if pd.isna(schedule):
        return False
    day_mapping = {
        'M': 'Monday',
        'T': 'Tuesday',
        'W': 'Wednesday',
        'Th': 'Thursday',
        'F': 'Friday',
        'S': 'Saturday',
        'Su': 'Sunday'
    }
    schedule_days = [day_mapping.get(day.strip(), day) for day in schedule.replace(' (am,pm)', '').split(',')]
    day_of_week = current_date.strftime('%A')
    return day_of_week in schedule_days


def refined_simulate_three_months_with_graduation_and_schedule(start_date, active_df, hold_df):
    results = []
    start_date = pd.to_datetime(start_date, format='%d-%m-%Y')
    end_date = start_date + pd.DateOffset(months=3)
    date_range = pd.date_range(start=start_date, end=end_date)

    for current_date in date_range:
        daily_capacities = {class_name: 0 for class_name in classes.keys()}
        graduations = []
        admissions = []
        attendance_log = {class_name: [] for class_name in classes.keys()}

        # Ensure Dob column is datetime
        active_df['Dob'] = pd.to_datetime(active_df['Dob'], errors='coerce')

        active_df['Age'] = (current_date - active_df['Dob']).dt.days / 365.25
        active_df['Current Class'] = active_df['Age'].apply(get_correct_class_by_age)
        active_df['Next Class'] = active_df['Age'].apply(lambda age: get_correct_class_by_age(age + 1 / 365.25))
        active_df['Attending'] = active_df.apply(lambda row: is_scheduled_to_attend(row['Time Schedule'], current_date),
                                                 axis=1)

        for _, row in active_df[active_df['Attending']].iterrows():
            if row['Current Class'] and row['Current Class'] != 'Graduated':
                daily_capacities[row['Current Class']] += 1
                if row['Next Class'] and row['Next Class'] != row['Current Class'] and row['Next Class'] != 'Graduated':
                    graduations.append((row['First Name'], row['Last Name'], row['Current Class'], row['Next Class']))
                attendance_log[row['Current Class']].append(f"{row['First Name']} {row['Last Name']}")

        hold_df['Admission Age'] = (current_date - hold_df['Dob']).dt.days / 365.25
        hold_df['Admission Class'] = hold_df['Admission Age'].apply(get_correct_class_by_age)
        new_admissions = hold_df[
            (hold_df['Admission Date'] <= current_date) & (hold_df['Admission Date'] >= start_date)]

        for _, row in new_admissions.iterrows():
            if row['Admission Class'] and row['Admission Class'] != 'Graduated':
                daily_capacities[row['Admission Class']] += 1
                admissions.append((row['First Name'], row['Last Name'], row['Admission Class']))
                active_df = pd.concat([active_df, row.to_frame().T], ignore_index=True)
                hold_df = hold_df.drop(index=row.name)

        results.append({
            'Date': current_date,
            'Capacities': daily_capacities,
            'Graduations': graduations,
            'Admissions': admissions,
            'Attendance': {class_name: ", ".join(attendance_log[class_name]) if attendance_log[class_name] else "None"
                           for class_name in classes.keys()}
        })

    return results


st.markdown('<div class="title">Mari\'s Little Lambs Availability Date Calculator</div>', unsafe_allow_html=True)

# Define session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'input'


def switch_page(page):
    st.session_state.page = page


if st.session_state.page == 'input':
    # Container for centering content
    st.markdown('<div class="center">', unsafe_allow_html=True)

    with st.form(key='availability_form'):
        st.markdown("<div class='input-container'>", unsafe_allow_html=True)

        # Inputs
        name = st.text_input("Name", value="John")
        dob = st.date_input("Date of Birth", value=datetime(2023, 1, 9))
        schedule = st.multiselect("Select Schedule", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                                  default=['Monday', 'Wednesday'])
        program_type = st.selectbox("Select Program Type", ['Fixed', 'Flexible'], index=0)
        joining_date = st.date_input("Preferred Joining Date", value=datetime.now().date())

        # File uploads
        active_file = st.file_uploader("Upload Active Excel File", type=["xlsx"])
        hold_file = st.file_uploader("Upload Hold Excel File", type=["xlsx"])
        fte_file = st.file_uploader("Upload FTE Excel File", type=["xlsx"])

        st.markdown("</div>", unsafe_allow_html=True)

        button_spacer_left, button_col, button_spacer_right = st.columns([4, 1, 4])
        with button_col:
            submit_button = st.form_submit_button("Check Availability")

    st.markdown("</div>", unsafe_allow_html=True)

    if submit_button:
        if not (active_file and hold_file and fte_file):
            st.error("Not all 3 files are uploaded. Please upload all the required files.")
        else:
            active_df = pd.read_excel(active_file)
            hold_df = pd.read_excel(hold_file)

            active_df.columns = active_df.iloc[3]
            hold_df.columns = hold_df.iloc[3]

            active_df = active_df.drop([0, 1, 2, 3]).reset_index(drop=True)
            hold_df = hold_df.drop([0, 1, 2, 3]).reset_index(drop=True)

            active_df = active_df.dropna(axis=1, how='all')
            hold_df = hold_df.dropna(axis=1, how='all')

            active_df['Dob'] = pd.to_datetime(active_df['Dob'], errors='coerce')
            hold_df['Dob'] = pd.to_datetime(hold_df['Dob'], errors='coerce')
            hold_df['Admission Date'] = pd.to_datetime(hold_df['Admission Date'], errors='coerce')

            # Initialize classroom with student capacity for each level
            capacity_levels = [8, 8, 7, 20]
            classroom = Classroom(capacity_levels)
            classroom.read_existing_data(active_df, hold_df)

            # Create new applicant
            new_applicant = Student(name, dob, schedule, program_type)

            total_active_students, total_hold_students, graduating_soon, admitted_recent = classroom.kpi_calculate(
                new_applicant.level)
            next_available_date, schedule, flexible = classroom.apply_for_admission(new_applicant, joining_date)

            # FTE calculation
            fte_df = pd.read_excel(fte_file, skiprows=2, header=1)
            fte_df = fte_df.reset_index()
            level_dict = {'Infants': 1, 'Wobblers': 2, 'Older Toddlers': 3, 'Preschool': 4}
            fte_df['Room'] = fte_df['Room'].map(level_dict)
            fte_df = fte_df[fte_df['Room'] == new_applicant.level]
            fte_count = (fte_df['Total'].sum())
            # fte_count = (fte_df['Total'][new_applicant.level].mean() * classroom.capacity_levels[new_applicant.level])

            if next_available_date is not False:
                next_available_date = datetime.combine(next_available_date, datetime.min.time())  # Ensure datetime type
                joining_date = datetime.combine(joining_date, datetime.min.time())  # Ensure datetime type
                waittime = (next_available_date - joining_date).days
            else:
                waittime = 365
            if next_available_date > joining_date:
                availability = "No"
            else:
                availability = "Yes"

            # Store results in session state
            st.session_state.results = {
                "Class": new_applicant.get_class_name(),
                "Total Active Students": sum(total_active_students),
                "Total Students in Hold": sum(total_hold_students),
                "Total Capacity of Class": classroom.capacity_levels[new_applicant.level - 1],
                "Students Graduating Soon": sum(graduating_soon),
                "Students Admitted Recently": sum(admitted_recent),
                "FTE": round(fte_count, 2),
                "Avg Wait Time in Days": waittime,  # Changed label
                "Availability": availability,
                "Soonest Available Date": next_available_date.date(),  # Display only the date
                "Schedule Requested": schedule
            }

            # Run the simulation
            start_date = datetime.now().strftime('%d-%m-%Y')  # Use the current date as the start date
            class_name = new_applicant.get_class_name()  # Get the correct class name based on the student's age

            simulation_results = refined_simulate_three_months_with_graduation_and_schedule(start_date, active_df, hold_df)

            final_data = []
            for result in simulation_results:
                graduations = result['Graduations']
                admissions = result['Admissions']
                attendance = result['Attendance'][class_name]

                graduation_sentences = []
                admission_sentences = []

                for grad in graduations:
                    if grad[2] == class_name:
                        graduation_sentences.append(f"{grad[0]} {grad[1]} graduated from {grad[2]} to {grad[3]}")
                    elif grad[3] == class_name:
                        graduation_sentences.append(f"{grad[0]} {grad[1]} graduated into {grad[3]} from {grad[2]}")
                    elif grad[3] == 'Graduated':
                        graduation_sentences.append(f"{grad[0]} {grad[1]} graduated out of daycare from {grad[2]}")

                for adm in admissions:
                    if adm[2] == class_name:
                        admission_sentences.append(f"{adm[0]} {adm[1]} was admitted to {adm[2]}")

                final_data.append({
                    'Date': result['Date'].strftime('%Y-%m-%d'),
                    'Day of Week': result['Date'].strftime('%A'),
                    f"Kids in Class for {class_name}": result['Capacities'][class_name],  # Changed label
                    'Graduations': " | ".join(graduation_sentences) if graduation_sentences else "None",
                    'Admissions': " | ".join(admission_sentences) if admission_sentences else "None",
                    'Attendance': attendance
                })

            final_df = pd.DataFrame(final_data)

            # Store simulation results in session state
            st.session_state.simulation_results = final_df
            st.session_state.start_date = datetime.now()  # Save start_date in session state
            st.session_state.active_df = active_df
            st.session_state.hold_df = hold_df
            st.session_state.fte_df = fte_df

            # Switch to the output page immediately
            st.session_state.page = 'output'
            st.experimental_rerun()

elif st.session_state.page == 'output':

    st.markdown('<div class="title centered">Availability Results</div>', unsafe_allow_html=True)

    results = st.session_state.results
    simulation_results = st.session_state.simulation_results
    start_date = st.session_state.start_date  # Retrieve start_date from session state
    active_df = st.session_state.active_df
    hold_df = st.session_state.hold_df
    fte_df = st.session_state.fte_df

    metrics = [
        {"label": "Class", "value": results["Class"]},
        {"label": "Total Active Students", "value": results["Total Active Students"]},
        {"label": "Total Students in Hold", "value": results["Total Students in Hold"]},
        {"label": "Total Capacity of Class", "value": results["Total Capacity of Class"]},
        {"label": "Students Graduating Soon", "value": results["Students Graduating Soon"]},
        {"label": "Students Admitted Recently", "value": results["Students Admitted Recently"]},
        {"label": "FTE", "value": results["FTE"]},
        {"label": "Avg Wait Time in Days", "value": results["Avg Wait Time in Days"]}  # Changed label
    ]

    availability_metrics = [
        {"label": "Availability for the Requested Date", "value": results["Availability"]},
        {"label": "Soonest Available Date", "value": results["Soonest Available Date"]},
        {"label": "Schedule Requested", "value": ", ".join(results["Schedule Requested"])}
    ]

    # Display metrics in rows using st.columns
    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, metric in enumerate(metrics):
        with cols[i % 4]:
            st.markdown(f"""
            <div class='metric-box centered'>
                <h4>{metric['label']}</h4>
                <p>{metric['value']}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='spacing-row'></div>", unsafe_allow_html=True)  # Add a spacing row

    availability_cols = st.columns(3)
    for i, metric in enumerate(availability_metrics):
        with availability_cols[i]:
            st.markdown(f"""
            <div class='metric-box centered'>
                <h4>{metric['label']}</h4>
                <p>{metric['value']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Generate the schedule table for the first Monday to Friday
    schedule_table_data = simulation_results.head(7)  # Get the first 7 days

    # Filter out weekends
    schedule_table_data = schedule_table_data[schedule_table_data['Day of Week'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]

    # Prepare the table data
    class_name = results["Class"]
    capacity_column = f"Kids in Class for {class_name}"  # Changed label
    max_capacity = results["Total Capacity of Class"]

    table_data = {
        "Day": ["Kids in Class"],
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
    }

    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        if day in schedule_table_data['Day of Week'].values:
            day_data = schedule_table_data[schedule_table_data['Day of Week'] == day]
            capacity = day_data[capacity_column].values[0]
            attendance = day_data['Attendance'].values[0]
            graduations = day_data['Graduations'].values[0]
            admissions = day_data['Admissions'].values[0]
            color = 'red' if capacity == max_capacity else 'green'

            table_data[day].append(f'<div class="tooltip" style="color: {color};"><b>{capacity}</b><span class="tooltiptext">Attendance: {attendance}<br>Graduations: {graduations}<br>Admissions: {admissions}</span></div>')
        else:
            table_data[day].append('')

    schedule_df = pd.DataFrame(table_data)

    # Generate table with inline styles for headers
    schedule_html = f"""
    <h3 class='centered'>Schedule Availability</h3>
    <table class='horizontal-table centered'>
        <thead>
            <tr>
                <th class="table-header">Day</th>
                {" ".join([f'<th class="table-header">{day}</th>' for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']])}
            </tr>
        </thead>
        <tbody>
            <tr>
                <th class="table-header">Kids in Class</th>
                {" ".join([f'<td>{table_data[day][0]}</td>' for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']])}
            </tr>
        </tbody>
    </table>
    """

    st.markdown(schedule_html, unsafe_allow_html=True)

    # Generate the 3-month calendar view
    def generate_calendar(start_date, class_name, simulation_results, max_capacity):
        calendar_html = ""
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i in range(3):
            month_start = start_date + relativedelta(months=i)
            month_end = month_start + relativedelta(day=31)
            calendar_html += f"<div><h3 class='centered'>{month_start.strftime('%B %Y')}</h3><div class='calendar-header centered'>"
            for day in days_of_week:
                calendar_html += f"<div class='calendar-day'>{day[:3]}</div>"
            calendar_html += "</div><div class='calendar centered'>"

            first_day_of_month = month_start.replace(day=1).weekday()
            for _ in range(first_day_of_month):
                calendar_html += "<div class='calendar-day no-data'></div>"

            day = month_start.replace(day=1)
            while day <= month_end:
                if day.weekday() == 0 and day.day != 1:
                    calendar_html += "</div><div class='calendar centered'>"
                color_class = ""
                tooltip_text = ""
                if day < start_date or day.weekday() >= 5:
                    color_class = "no-data"
                else:
                    sim_result = simulation_results[simulation_results['Date'] == day.strftime('%Y-%m-%d')]
                    if not sim_result.empty:
                        capacity = sim_result.iloc[0][f"Kids in Class for {class_name}"]  # Changed label
                        attendance = sim_result.iloc[0]['Attendance']
                        graduations = sim_result.iloc[0]['Graduations']
                        admissions = sim_result.iloc[0]['Admissions']
                        color_class = "green" if capacity < max_capacity else "red"
                        tooltip_text = f"Capacity: {capacity}<br>Attendance: {attendance}<br>Graduations: {graduations}<br>Admissions: {admissions}"

                calendar_html += f"<div class='calendar-day {color_class}'><div class='tooltip'>{day.day}<span class='tooltiptext'>{tooltip_text}</span></div></div>"
                day += timedelta(days=1)

            calendar_html += "</div></div>"
        return calendar_html

    calendar_html = generate_calendar(start_date, class_name, simulation_results, max_capacity)
    st.markdown(calendar_html, unsafe_allow_html=True)

    # Display the uploaded Excel files
    st.markdown("<h3 class='centered'>Uploaded Excel Files</h3>", unsafe_allow_html=True)
    st.markdown("<h4 class='centered'>Active Students Data:</h4>", unsafe_allow_html=True)
    st.dataframe(active_df)

    st.markdown("<h4 class='centered'>Hold Students Data:</h4>", unsafe_allow_html=True)
    st.dataframe(hold_df)

    st.markdown("<h4 class='centered'>FTE Data:</h4>", unsafe_allow_html=True)
    st.dataframe(fte_df)
