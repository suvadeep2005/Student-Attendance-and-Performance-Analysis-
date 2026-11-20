import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

#page configuration
st.set_page_config(page_title="Student Attendance and Performance Analysis", layout="wide")
st.title("🎓 Student Attendance and Performance Analysis")

with st.sidebar:

    st.header("📁 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    st.markdown("---")

    selected = option_menu(
        menu_title="Menu",
        options=[
            "Raw Data",
            "Search Student",
            "Student Attendance",
            "Subject Analysis",
            "Pass/Fail",
            "Student Result",
            "Topper",
            "Pivot Table",
        ],
        icons=[
            "table",
            "search",
            "calendar-check",
            "bar-chart",
            "check-circle",
            "book",
            "trophy",
            "grid",
        ],
        menu_icon="menu-button-wide",
        default_index=0
    )
if uploaded_file is None:
    st.warning("please upload a csv file to continue...")
    st.stop()  
df=pd.read_csv(uploaded_file)

if selected=="Raw Data":
    st.subheader("Raw Data")
    st.dataframe(df)
elif selected == "Search Student":
    st.subheader("Search Student")
    search_query = st.text_input("Enter Student ID or First/Last Name:")
    if search_query:
        result = df[
            df["Student_ID"].astype(str).str.contains(search_query, case=False, na=False) |
            df["First_Name"].astype(str).str.contains(search_query, case=False, na=False) |
            df["Last_Name"].astype(str).str.contains(search_query, case=False, na=False)
        ]
        
        if not result.empty:
            st.dataframe(result)
        else:
            st.warning("No matching student found.")

elif selected == "Student Attendance":
    st.subheader("Student Attendance Analysis")
    
    avg_attendance = df["Attendance (%)"].mean()
    min_attendance = df["Attendance (%)"].min()
    max_attendance = df["Attendance (%)"].max()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Attendance", f"{avg_attendance:.2f}%")
    col2.metric("Highest Attendance", f"{max_attendance:.2f}%")
    col3.metric("Lowest Attendance", f"{min_attendance:.2f}%")
    
    st.divider()

    threshold = st.slider("Filter students with attendance below (%):", 0, 100, 75)
    low_attendance_df = df[df["Attendance (%)"] < threshold]
    
    st.write(f"Students below {threshold}% attendance ({len(low_attendance_df)} found):")
    st.dataframe(low_attendance_df[["Student_ID", "First_Name", "Last_Name", "Department", "Attendance (%)"]])
    st.subheader("Average Attendance by Department")
    dept_attendance = df.groupby("Department")["Attendance (%)"].mean()
    st.bar_chart(dept_attendance)

elif selected == "Subject Analysis":
    st.subheader("Subject / Assessment Analysis")
    
    att_index = list(df.columns).index("Attendance (%)")
    subject_cols = list(df.columns)[att_index + 1:]
    
    selected_subject = st.selectbox("Select Subject / Exam:", subject_cols)
    
    if pd.api.types.is_numeric_dtype(df[selected_subject]):
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Score", f"{df[selected_subject].mean():.2f}")
        col2.metric("Highest Score", f"{df[selected_subject].max():.2f}")
        col3.metric("Lowest Score", f"{df[selected_subject].min():.2f}")
        
        st.divider()
        st.subheader(f"Average {selected_subject} Score by Department")
        dept_avg = df.groupby("Department")[selected_subject].mean()
        st.bar_chart(dept_avg)
    else:
        st.subheader(f"{selected_subject} Distribution")
        grade_counts = df[selected_subject].value_counts()
        st.bar_chart(grade_counts)

elif selected == "Pass/Fail":
    st.subheader("Pass / Fail Analysis")

    df["Status"] = df["Grade"].apply(lambda g: "Fail" if str(g).strip().upper() == "F" else "Pass")

    total_students = len(df)
    pass_count = (df["Status"] == "Pass").sum()
    fail_count = (df["Status"] == "Fail").sum()
    pass_rate = (pass_count / total_students) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Passed", pass_count)
    col2.metric("Total Failed", fail_count)
    col3.metric("Pass Percentage", f"{pass_rate:.2f}%")

    st.divider()

    st.subheader("Overall Pass vs Fail Count")
    st.bar_chart(df["Status"].value_counts())

    filter_status = st.radio("View Students:", ["All", "Pass", "Fail"], horizontal=True)
    if filter_status == "All":
        st.dataframe(df[["Student_ID", "First_Name", "Last_Name", "Department", "Grade", "Status"]])
    else:
     st.dataframe(df[df["Status"] == filter_status][["Student_ID", "First_Name", "Last_Name", "Department", "Grade", "Status"]])
        
elif selected == "Student Result":
    st.subheader("Individual Student Report Card")
    

    student_list = df["Student_ID"] + " - " + df["First_Name"] + " " + df["Last_Name"]
    selected_student = st.selectbox("Select Student:", student_list)
    
    
    student_id = selected_student.split(" - ")[0]
    student_row = df[df["Student_ID"] == student_id].iloc[0]
    
    
    st.markdown(f"### {student_row['First_Name']} {student_row['Last_Name']} ({student_id})")
    st.write(f"**Department:** {student_row['Department']} | **Gender:** {student_row['Gender']} | **Age:** {student_row['Age']}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Attendance", f"{student_row['Attendance (%)']:.2f}%")
    col2.metric("Final Grade", student_row["Grade"])
    status = "Fail" if str(student_row["Grade"]).strip().upper() == "F" else "Pass"
    col3.metric("Result Status", status)
    
    st.divider()
    
    
    st.subheader("Score Breakdown")
    att_index = list(df.columns).index("Attendance (%)")
    numeric_cols = [col for col in df.columns[att_index + 1:] if pd.api.types.is_numeric_dtype(df[col])]
    
    scores_df = pd.DataFrame({
        "Subject / Exam": numeric_cols,
        "Score": [student_row[col] for col in numeric_cols]
    })
    
    st.dataframe(scores_df, hide_index=True)
    st.bar_chart(scores_df.set_index("Subject / Exam"))

elif selected == "Topper":
    st.subheader("Top Performers & Leaderboard")
    
    
    att_index = list(df.columns).index("Attendance (%)")
    numeric_cols = [col for col in df.columns[att_index + 1:] if pd.api.types.is_numeric_dtype(df[col])]
    
    
    df["Average_Score"] = df[numeric_cols].mean(axis=1)
    
    
    overall_topper = df.sort_values(by="Average_Score", ascending=False).iloc[0]
    st.success(
        f"🏆 **Overall Topper:** {overall_topper['First_Name']} {overall_topper['Last_Name']} "
        f"({overall_topper['Student_ID']}) — **{overall_topper['Department']}** | "
        f"Average Score: **{overall_topper['Average_Score']:.2f}**"
    )
    
    st.divider()
    
    
    top_n = st.slider("Number of Top Students to Display:", 3, 20, 5)
    top_students = df.sort_values(by="Average_Score", ascending=False).head(top_n)
    
    st.subheader(f"Top {top_n} Students Overall")
    display_cols = ["Student_ID", "First_Name", "Last_Name", "Department", "Average_Score", "Grade"]
    st.dataframe(top_students[display_cols], hide_index=True)
    
    st.divider()
    
    st.subheader("Department-Wise Toppers")
    dept_toppers = df.loc[df.groupby("Department")["Average_Score"].idxmax()]
    st.dataframe(dept_toppers[display_cols], hide_index=True)

elif selected == "Pivot Table":
    st.subheader("Interactive Pivot Table")
    
    cat_cols = ["Department", "Gender", "Grade"]
    num_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col != "Age"]

    col1, col2, col3, col4 = st.columns(4)
    index_col = col1.selectbox("Rows (Group By):", cat_cols, index=0)
    columns_col = col2.selectbox("Columns (Optional):", ["None"] + cat_cols, index=1)
    values_col = col3.selectbox("Values to Summarize:", num_cols, index=0)
    agg_func = col4.selectbox("Calculation:", ["mean", "max", "min", "count"], index=0)
    
    if columns_col == "None":
        pivot = pd.pivot_table(df, index=index_col, values=values_col, aggfunc=agg_func)
    else:
        pivot = pd.pivot_table(df, index=index_col, columns=columns_col, values=values_col, aggfunc=agg_func)
    
    st.dataframe(pivot.round(2))
    st.bar_chart(pivot)






