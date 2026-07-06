import pandas as pd
import streamlit as st
import datetime

df=pd.read_csv('data/habit.csv')
if df['Habit'].isna().any():
    df=df.dropna(subset='Habit')
    df.to_csv('habit.csv',index=False)
def option_menu():
    st.title('Habit Tracker')
    option = st.selectbox(
        "Please Select an Option",
        ("Add a new habit to track", "Log completion of a habit", "View habit streaks and statistics","Edit or remove habits","View all habits"),
    )
    st.write("You selected:", option)
    return option

def new_habit():
    global df
    Habit_name = st.text_input("Habit name:", placeholder="Please enter the habit name")
    Frequency = st.selectbox(
        "Please Select an Option",
        ("Daily", "Weekly", "Monthly","Yearly"),
    )
    Target_goal=st.text_input("Target Goal:", placeholder="Number of repititions")
    Category=st.text_input("Category:", placeholder="(Health, Productivity, Learning, etc.)")
    date = st.date_input("Start date: ", value=None)
    """
    Making the user input the habit details
    """
    if st.button('Save Habit'):
        if Habit_name in df['Habit']:
            st.write('The habit is already in the data base')
        else:
            new_row={'Habit':Habit_name,'Frequency':Frequency,'Target_Goal':Target_goal,'Category':Category,'Start_Date':date,'Completion':pd.NaT}
            df=pd.concat([df,pd.DataFrame([new_row])],ignore_index=True)
            df.to_csv('data/habit.csv',index=False)
            st.success('Habit Saved!', icon="✅")
            st.rerun()
        
def completion():
    global df
    radio_selection = st.radio(
        "Which habit was completed?",
        df['Habit'].unique(),
        index=None,
    )
    if radio_selection:
        matching_row = df[df['Habit'] == radio_selection].iloc[0]
        habit_start=pd.to_datetime(matching_row['Start_Date']).date()
        if habit_start>datetime.date.today():
            st.write(f"This habit's start date {habit_start} is in the future. You can't log completions until it starts")
            return
        completion_date = st.date_input("Completion date", value=None, min_value=habit_start, max_value=datetime.date.today())
        completion_time = st.time_input("Completion time", value=None)
        """
        new_row is initialized as None first so that clicking Submit before both
        date and time are filled in doesn't crash with a NameError; the button
        below only proceeds if it actually got built.
        """
        new_row=None
        if completion_date and completion_time:
            completion_timestamp = datetime.datetime.combine(completion_date, completion_time)
            new_row={'Habit':radio_selection,
                     'Frequency':matching_row['Frequency'],
                     'Target_Goal':matching_row['Target_Goal'],
                     'Category':matching_row['Category'],
                     'Start_Date':matching_row['Start_Date'],
                     'Completion':completion_timestamp}
        """
        For each completion a new row is formed in the csv, and since only the completion is the updated value, all others are just copied 
        """
        if st.button('Submit'):
            if new_row is not None:
                df=pd.concat([df,pd.DataFrame([new_row])],ignore_index=True)
                df.to_csv('data/habit.csv',index=False)
                st.success('Status Updated!', icon="✅")
            else:
                st.warning("Please select both a completion date and time before submitting.")


def stats():
    global df
    highest_rate = -1
    best_habit = ""
    
    for single in df['Habit'].unique():
        try:
            streak=0
            best_streak=0
            successful_periods = 0
            Start_Date=pd.to_datetime(df[df['Habit']==single]['Start_Date'].iloc[0]).date()
            today=datetime.date.today()
            total_days_passed=(today-Start_Date).days+1 #inclusive, so saturday-saturday will equal 1
            Target=int(df.loc[df['Habit']==single ,'Target_Goal'].iloc[0])
            Freq=df.loc[df['Habit']==single ,'Frequency'].iloc[0]
            Habit_completion_full=pd.to_datetime(df[df['Habit']==single]['Completion'].iloc[1:])
            Habit_completion_dates=Habit_completion_full.dt.normalize()
            if Freq=='Daily':
                total_periods=max(1,total_days_passed)
                for count in Habit_completion_dates.value_counts():
                    if count>=Target:
                        streak+=1
                        best_streak=max(best_streak,streak)
                        successful_periods+=1
                    else:
                        best_streak=max(best_streak,streak)
                        streak=0
                    
            elif Freq=='Weekly':
                total_periods=max(1,total_days_passed//7)
                weeks=Habit_completion_dates.dt.to_period('W')
                for count in weeks.value_counts():
                    if count>=Target:
                        streak+=1
                        best_streak=max(best_streak,streak)
                        successful_periods+=1
                    else:
                        best_streak=max(best_streak,streak)
                        streak=0
            
            elif Freq=='Monthly':
                total_periods=max(1,total_days_passed//30)
                months=Habit_completion_dates.dt.to_period('M')
                for count in months.value_counts():
                    if count>=Target:
                        streak+=1
                        best_streak=max(best_streak,streak)
                        successful_periods+=1
                    else:
                        best_streak=max(best_streak,streak)
                        streak=0
                    
            elif Freq=='Yearly':
                total_periods=max(1,total_days_passed//365)
                years=Habit_completion_dates.dt.to_period('Y')
                for count in years.value_counts():
                    if count>=Target:
                        streak+=1
                        best_streak=max(best_streak,streak)
                        successful_periods+=1
                    else:
                        best_streak=max(best_streak,streak)
                        streak=0
            """
            As the Frequency is inputted as either (Daily/Weekly/Monthly/Yearly) each one needs to convert the date to the appropiate format
            example: Frequency=='Monthly', inputted Completion date is 4/7/2026
                     dt.period('M') will change this format to 7/2026
                     this will make it easier for value_counts() to count how many times a month the user completed.
                     
            For the completion rate calculation, the total days passed from the start date of the habit to the current date of the machine gets computed first.
            After that the variable total_periods takes the bigger number between 1 (1 because if you started on the same day), or the total days passed divided 
            by the days in the frequency (Monthly has 30 days...etc). 
            for example: total_days_passed from Saturday to the same Saturday is object 0 (.days) will make change it to integer 0 (+1) so the same day is inclusive
            so it equates to 1. let's say it is for the daily so total_period=1, if the target was 2, but the user only recorded once, the successful periods is             0. so for the completion rate=(0/1)*100 would be 0%
            """
            completion_rate=(successful_periods/total_periods)*100
            if completion_rate>100:
                completion_rate=100

            if completion_rate > highest_rate:
                highest_rate = completion_rate
                best_habit = single
                
            """
            to get the best habit, heighest_rate=-1 and best_habit="" were initialized. so the habit in the first loop will always have a completion_rate higher             than the height_rate even if it is 0% as the heighest_rate is -1. after that in each iteration it will compare and pick the better one.
            
            """
            st.write(f"{single} streak: {streak} | Best Streak: {best_streak} | Completion Rate: {completion_rate}%")
            
            total_logs = len(Habit_completion_dates)
            st.write(f"* Calendar History: {total_logs} total completion entries recorded.")
            if best_streak >= 5:
                st.write("* Achievement Unlocked: Gold Level status reached.")
            elif best_streak >= 2:
                st.write("* Achievement Unlocked: Silver Level status reached.")
            else:
                st.write("* Achievement Unlocked: Bronze Level status reached.")

            if today not in Habit_completion_full.dt.date.values:
                st.toast(f"Reminder: Complete your '{single}' habit today!")
                st.write("* Reminder Alert: This habit is still pending for today.")
            else:
                st.write("* Reminder Alert: Completed for today.")


            if total_logs > 0:
                morning_count = (Habit_completion_full.dt.hour < 12).sum()
                evening_count = total_logs - morning_count
                if morning_count >= evening_count:
                    st.write("* Optimal Time: Your best completion performance happens in the Morning.")
                else:
                    st.write("* Optimal Time: Your best completion performance happens in the Evening.")
            else:
                st.write("* Optimal Time: Not enough data yet.")

            st.write("---")
            """
            Optimal Time is when most completions for
            this habit happened before noon, it's a Morning habit, otherwise Evening.
            """
        except Exception as e:
            st.error(f"Something went wrong while computing stats for '{single}'. Error details below:")
            st.exception(e)
        
    if best_habit != "":
        st.write("### Habit Stacking Suggestion:")
        st.write(f"Your most successful habit is **{best_habit}**.")
        if df['Habit'].nunique()>1:
            other_habit=df[df['Habit']!=best_habit].sample()
            st.write(f"Try linking your routines: Right after you finish {best_habit}, immediately do {other_habit['Habit'].iloc[0]}.")
        else:
            st.write("Register a new habit to access this feature")
        


def modify():
    global df
    radio_selection = st.radio(
        "Which habit to modify?",
        df['Habit'].unique(),
        index=None,
    )


    if radio_selection:
        choices=['Habit_Name']+list(df.columns[1:])+['Delete_Habit']
        details = st.multiselect(
            "Which detail to modify?",
            choices,
            default=None,
        )
        Habit_to_modify = df[df['Habit'] == radio_selection]
        Habit_Name=Habit_to_modify['Habit'].iloc[0]
        Frequency=Habit_to_modify['Frequency'].iloc[0]
        Target_Goal=Habit_to_modify['Target_Goal'].iloc[0]
        Category=Habit_to_modify['Category'].iloc[0]
        Start_Date=Habit_to_modify['Start_Date'].iloc[0]
        habit_start=pd.to_datetime(Start_Date).date()
        first_log_row=None
        Completion=None
        if details:
            if 'Delete_Habit' in details:
                if st.button('Delete',radio_selection):
                    df=df[df['Habit']!=radio_selection]
                    df.to_csv('data/habit.csv',index=False)
                    st.success('Habit Deleted!', icon="✅")
                    st.rerun()
                return
            if 'Habit_Name' in details:
                Habit_Name=st.text_input("Habit name:", placeholder="Please enter the habit name")
            if 'Frequency' in details:
                Frequency = st.text_input("Frequency:", placeholder="(Daily, Weekly, Monthly)")
            if 'Target_Goal' in details:
                Target_Goal=st.text_input("Target Goal:", placeholder="Number of repititions")
            if 'Category' in details:
                Category=st.text_input("Category:", placeholder="(Health, Productivity, Learning, etc.)")
            if 'Start_Date' in details:
                Start_Date = st.date_input("Start date: ", value=None)
            if 'Completion' in details:
                completion_list=list(Habit_to_modify['Completion'].iloc[1:])
                option = st.selectbox(
                    "Please select the completion date you want to edit",
                    (completion_list),
                    )
                if option:
                    new_completion_date = st.date_input("Completion date", value=None, min_value=habit_start, max_value=datetime.date.today())
                    new_completion_time = st.time_input("Completion time", value=None)
                    if new_completion_date and new_completion_time:
                        Completion = datetime.datetime.combine(new_completion_date, new_completion_time)
                        """
                        Find the row that actually matches the completion value the
                        user picked in the dropdown, rather than assuming it's always
                        the first logged completion (index[1]). This way, editing the
                        3rd logged completion actually edits the 3rd row, not the 1st.
                        """
                        first_log_row = Habit_to_modify[Habit_to_modify['Completion'] == option].index[0]
                    
            
        if st.button('Submit'):
            """
            Guard: if the user is changing Start_Date, make sure it isn't later
            than any completion already logged for this habit. Otherwise stats()
            would end up crediting completions that happened "before tracking
            started", inflating the completion rate in a misleading way.
            """
            existing_completions = pd.to_datetime(Habit_to_modify['Completion'].iloc[1:]).dropna()
            block_save = False
            if Start_Date is not None and len(existing_completions) > 0:
                earliest_completion = existing_completions.min().date()
                if Start_Date > earliest_completion:
                    st.warning(
                        f"Can't set the start date to {Start_Date} — this habit already has a "
                        f"completion logged on {earliest_completion}, which is before that. "
                        f"Please pick a start date on or before {earliest_completion}."
                    )
                    block_save = True

            if not block_save:
                if Start_Date is not None:
                    df.loc[df['Habit']==radio_selection,'Start_Date']=Start_Date
                df.loc[df['Habit']==radio_selection,'Frequency']=Frequency
                df.loc[df['Habit']==radio_selection,'Target_Goal']=Target_Goal
                df.loc[df['Habit']==radio_selection,'Category']=Category
                """
                Same guard for Completion: only write if both a target row was
                resolved AND a real timestamp was built, so leaving the new
                date/time blank doesn't silently wipe an existing log entry.
                """
                if first_log_row is not None and Completion is not None:
                    df.loc[first_log_row, 'Completion'] = Completion
                df.loc[df['Habit']==radio_selection,'Habit']=Habit_Name
                df.to_csv('data/habit.csv',index=False)
                st.success('Status Updated!', icon="✅")
                st.rerun()


def All():
    global df
    st.write('All Habits')
    st.dataframe(df['Habit'].unique())
    st.write('The whole dataset')
    st.dataframe(df)