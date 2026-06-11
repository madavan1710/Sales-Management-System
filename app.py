import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db_connection import get_connection

st.set_page_config(page_title="Sales Management System", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Database Connection
conn = get_connection()

# User Login Authentication
if not st.session_state.logged_in:

    st.title("Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor = conn.cursor()

        cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=%s
        AND password=%s
        """,
        (username, password)
        )

        user = cursor.fetchone()

        if user:
            st.success("login Successful")

            st.session_state.logged_in = True

            st.session_state.role = user[4]

            st.session_state.branch_id = user[3]

            st.rerun()

        else:

            st.error("Invalid Username or Password")

    st.stop()

# Page title
st.title("Sales Management System")

# Sidebar for LOGOUT 
st.sidebar.write(
        f"Role: {st.session_state.role}"
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.rerun()

# Side bar Navigation
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Customer Sales",
        "Branches", 
        "Payments",
        "Add Sales",
        "Add Payment",
        "Reports"
        
    ]
)

# CUSTOMER SALES
if menu == "Customer Sales":

    st.subheader("Customer Sales Details")

    # Super Admin View
    if st.session_state.role == "Super Admin":

        branches = pd.read_sql(
            "SELECT branch_id, branch_name FROM branches",
            conn
        )

        products = pd.read_sql(
            """
            SELECT DISTINCT product_name
            FROM customer_sales
            ORDER BY product_name
            """,
            conn
        )

        min_max_dates = pd.read_sql(
            """
            SELECT
                MIN(date) AS min_date,
                MAX(date) AS max_date
            FROM customer_sales
            """,
            conn
        )

        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

        with filter_col1:
            selected_branch = st.selectbox(
                "Select Branch",
                ["All Branches"] + branches["branch_name"].tolist()
            )

        with filter_col2:
            selected_product = st.selectbox(
                "Select Product",
                ["All Products"] + products["product_name"].tolist()
            )

        with filter_col3:
            from_date = st.date_input(
                "From Date",
                value=min_max_dates["min_date"][0],
                format="DD/MM/YYYY"
            )

        with filter_col4:
            to_date = st.date_input(
                "To Date",
                value=min_max_dates["max_date"][0],
                format="DD/MM/YYYY"
            )

        # Dynamic Filter
        filters = []
        if selected_branch != "All Branches":
            branch_id = branches[
                branches["branch_name"] == selected_branch
            ]["branch_id"].iloc[0]

            filters.append(
                f"branch_id = {branch_id}"
            )

        if selected_product != "All Products":
            filters.append(
                f"product_name = '{selected_product}'"
            )

        filters.append(
            f"date BETWEEN '{from_date}' AND '{to_date}'"
        )

        where_clause = " AND ".join(filters)

        # KPI Queries for Super Admin
        total_sales = pd.read_sql(
            f"""
            SELECT SUM(gross_sales) AS total
            FROM customer_sales
            WHERE {where_clause}
            """,
            conn
        )

        total_received = pd.read_sql(
            f"""
            SELECT SUM(received_amount) AS total
            FROM customer_sales
            WHERE {where_clause}
            """,
            conn
        )

        total_pending = pd.read_sql(
            f"""
            SELECT SUM(pending_amount) AS total
            FROM customer_sales
            WHERE {where_clause}
            """,
            conn
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Sales",
            f"₹ {total_sales.iloc[0,0]:,.2f}"
        )

        col2.metric(
            "Total Received",
            f"₹ {total_received.iloc[0,0]:,.2f}"
        )

        col3.metric(
            "Total Pending",
            f"₹ {total_pending.iloc[0,0]:,.2f}"
        )

        query = f"""
        SELECT *
        FROM customer_sales
        WHERE {where_clause}
        """

    # Branch Admin View
    else:

        products = pd.read_sql(
            """
            SELECT DISTINCT product_name
            FROM customer_sales
            ORDER BY product_name
            """,
            conn
        )

        min_max_dates = pd.read_sql(
            f"""
            SELECT
                MIN(date) AS min_date,
                MAX(date) AS max_date
            FROM customer_sales
            WHERE branch_id = {st.session_state.branch_id}
            """,
            conn
        )

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            selected_product = st.selectbox(
                "Select Product",
                ["All Products"] + products["product_name"].tolist()
            )

        with filter_col2:
            from_date = st.date_input(
                "From Date",
                value=min_max_dates["min_date"][0],
                format="DD/MM/YYYY"
            )

        with filter_col3:
            to_date = st.date_input(
                "To Date",
                value=min_max_dates["max_date"][0],
                format="DD/MM/YYYY"
            )

        filters = [
            f"branch_id = {st.session_state.branch_id}"
        ]

        if selected_product != "All Products":
            filters.append(
                f"product_name = '{selected_product}'"
            )

        filters.append(
            f"date BETWEEN '{from_date}' AND '{to_date}'"
        )

        where_clause = " AND ".join(filters)

        # KPI Queries for Admin
        total_sales = pd.read_sql(
            f"""
            SELECT COALESCE(SUM(gross_sales),0) AS total
            FROM customer_sales
            WHERE {where_clause}
            """,
            conn
        )

        total_received = pd.read_sql(
            f"""
            SELECT COALESCE(SUM(received_amount),0) AS total
            FROM customer_sales
            WHERE {where_clause}
            """,
            conn
        )

        total_pending = pd.read_sql(
            f"""
            SELECT COALESCE(SUM(pending_amount),0) AS total
            FROM customer_sales
            WHERE {where_clause}
            """,
            conn
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Sales",
            f"₹ {total_sales.iloc[0,0]:,.2f}"
        )

        col2.metric(
            "Total Received",
            f"₹ {total_received.iloc[0,0]:,.2f}"
        )

        col3.metric(
            "Total Pending",
            f"₹ {total_pending.iloc[0,0]:,.2f}"
        )

        query = f"""
        SELECT *
        FROM customer_sales
        WHERE {where_clause}
        """

    df = pd.read_sql(query, conn)

    st.dataframe(df)

# BRANCHES
elif menu == "Branches":

    st.subheader("Branches Details")

    if st.session_state.role == "Super Admin":

        query = "SELECT * FROM branches"

    else:

        query = f"""
        SELECT *
        FROM branches
        WHERE branch_id =
        {st.session_state.branch_id}
        """

    df = pd.read_sql(query, conn)

    st.dataframe(df)

# PAYMENTS
elif menu == "Payments":

    st.subheader("Payment Details")

    if st.session_state.role == "Super Admin":

        query = """
        SELECT *
        FROM payment_splits
        """

    else:

        query = f"""
        SELECT ps.*
        FROM payment_splits ps
        JOIN customer_sales cs
        ON ps.sale_id = cs.sale_id
        WHERE cs.branch_id =
        {st.session_state.branch_id}
        """

    df = pd.read_sql(query, conn)

    st.dataframe(df)

# ADD SALES FORM

elif menu == "Add Sales":

    st.subheader("Add New Sales Entry")

    if st.session_state.role == "Super Admin":

        branches = pd.read_sql(
            "SELECT branch_id, branch_name FROM branches",
            conn
        )

    else:
        branches = pd.read_sql(
            f"""
            SELECT branch_id, branch_name 
            FROM branches
            WHERE branch_id = {st.session_state.branch_id}
            """,
            conn
        )

    with st.form("sales_form"):

        if st.session_state.role == "Super Admin":

            branch = st.selectbox(
            "Branch",
            branches["branch_name"]
            )

        else:

            branch = branches["branch_name"].iloc[0]

            st.text_input(
                "Branch",
                value=branch,
                disabled=True
            )

        sale_date = st.date_input(
            "Joining Date"
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        mobile = st.text_input(
            "Mobile Number"
        )

        product = st.text_input(
            "Product Name"
        )

        gross_sales = st.number_input(
            "Gross Sales",
            min_value=0.0
        )

        status = st.selectbox(
            "Status",
            ["Open","Close"]
        )

        submit = st.form_submit_button(
            "Add Sale"
        )

        if submit:

            branch_id = branches[
                branches["branch_name"] == branch
            ]["branch_id"].iloc[0]

            cursor = conn.cursor()

            cursor.execute(
            """
            INSERT INTO customer_sales
            (
                branch_id,
                date,
                name,
                mobile_number,
                product_name,
                gross_sales,
                status
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                branch_id,
                sale_date,
                customer_name,
                mobile,
                product,
                gross_sales,
                status
            )
            )

            conn.commit()

            st.success(
                "Sale Added Successfully"
            )

# ADD PAYMENT FORM

elif menu == "Add Payment":

    st.subheader("Add Payment Split")

    sales = pd.read_sql(
        """
        SELECT
        sale_id,
        name
        FROM customer_sales
        """,
        conn
    )

    with st.form("payment_form"):

        sale_id = st.selectbox(
            "Sale ID",
            sales["sale_id"]
        )

        payment_date = st.date_input(
            "Payment Date"
        )

        amount_paid = st.number_input(
            "Amount Paid",
            min_value=0.0
        )

        payment_method = st.selectbox(
            "Payment Method",
            ["Cash","UPI","Card"]
        )

        submit = st.form_submit_button(
            "Add Payment"
        )

        if submit:

            cursor = conn.cursor()

            cursor.execute(
            """
            INSERT INTO payment_splits
            (
                sale_id,
                payment_date,
                amount_paid,
                payment_method
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            (
                sale_id,
                payment_date,
                amount_paid,
                payment_method
            )
            )

            conn.commit()

            st.success(
                "Payment Added Successfully"
            )

# REPORTS
elif menu == "Reports":

    st.subheader("Reports & Analytics")

# Basic Queries

    st.header("Basic Queries")

    st.subheader("All Branches")

    query1 = "SELECT * FROM branches;"

    df1 = pd.read_sql(query1, conn)

    st.dataframe(df1)

    st.subheader("All Customer Sales")

    query2 = "SELECT * FROM customer_sales;"

    df2 = pd.read_sql(query2, conn)

    st.dataframe(df2)

    st.subheader("All Payment Splits")

    query3 = "SELECT * FROM payment_splits;"

    df3 = pd.read_sql(query3, conn)

    st.dataframe(df3)

    st.subheader("Open Status Sales")

    query4 = """

    SELECT*
    FROM customer_sales
    WHERE status = 'Open';
    """

    df4 = pd.read_sql(query4, conn)

    st.dataframe(df4)

#Aggregation Queries 

    st.header("Aggregation Queries")

    st.subheader("Total Gross Sales")

    query5 = """
    SELECT
    SUM(gross_sales) AS total_gross_sales
    FROM customer_sales;
    """

    df5 = pd.read_sql(query5, conn)

    st.dataframe(df5)

    st.subheader("Total Received Amount")

    query6 = """
    SELECT
    SUM(received_amount) AS total_received
    FROM customer_sales;
    """

    df6 = pd.read_sql(query6, conn)

    st.dataframe(df6)

    st.subheader("Total Pending Amount")

    query7 = """
    SELECT
    SUM(pending_amount) AS total_pending
    FROM customer_sales;
    """

    df7 = pd.read_sql(query7, conn)

    st.dataframe(df7)

    st.subheader("Average Sales")

    query8 = """
    SELECT
    AVG(gross_sales) AS average_sales
    FROM customer_sales;
    """

    df8 = pd.read_sql(query8, conn)

    st.dataframe(df8)

# Join Queries

    st.header("Join Queries")

    st.subheader("Sales With Branch Details")

    query9 = """
    SELECT
    cs.sale_id,
    b.branch_name,
    cs.name,
    cs.product_name,
    cs.gross_sales

    FROM customer_sales cs

    JOIN branches b
    ON cs.branch_id=b.branch_id;
    """

    df9 = pd.read_sql(query9, conn)

    st.dataframe(df9)

    st.subheader("Customer Payment Details")

    query10 = """
    SELECT
    cs.sale_id,
    cs.name,
    ps.amount_paid,
    ps.payment_method

    FROM customer_sales cs

    JOIN payment_splits ps
    ON cs.sale_id=ps.sale_id;
    """

    df10 = pd.read_sql(query10, conn)

    st.dataframe(df10)

    st.subheader("Branch Wise Total Sales")

    query11 = """
    SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_sales

    FROM branches b

    JOIN customer_sales cs
    ON b.branch_id=cs.branch_id

    GROUP BY b.branch_name;
    """

    df11 = pd.read_sql(query11, conn)

    st.dataframe(df11)

    st.subheader("Customer Product Payment Details")

    query12 = """
    SELECT
    cs.sale_id,
    cs.name AS customer_name,
    cs.product_name,
    ps.payment_method,
    ps.amount_paid

    FROM customer_sales cs

    JOIN payment_splits ps
    ON cs.sale_id = ps.sale_id;
    """

    df12 = pd.read_sql(query12, conn)

    st.dataframe(df12)

# FINANCIAL QUERIES

    st.header("Financial Queries")

    st.subheader("Pending Amount Greater Than 5000")

    query13 = """
    SELECT *
    FROM customer_sales
    WHERE pending_amount > 5000;
    """

    df13 = pd.read_sql(query13, conn)

    st.dataframe(df13)

    st.subheader("Top 3 Highest Sales")

    query14 = """
    SELECT *
    FROM customer_sales
    ORDER BY gross_sales DESC
    LIMIT 3;
    """

    df14 = pd.read_sql(query14, conn)

    st.dataframe(df14)

    st.subheader("Highest Performing Branch")

    query15 = """
    SELECT
    b.branch_name,
    SUM(cs.gross_sales) AS total_sales

    FROM branches b

    JOIN customer_sales cs
    ON b.branch_id = cs.branch_id

    GROUP BY b.branch_name

    ORDER BY total_sales DESC

    LIMIT 1;
    """

    df15 = pd.read_sql(query15, conn)

    st.dataframe(df15)

    st.header("Charts")

    st.subheader("Branch Wise Total Sales")

    st.bar_chart(
        df11.set_index("branch_name")
    )

    st.subheader("Payment Method Summary")

    payment_chart = pd.read_sql(
    """
    SELECT
    payment_method,
    SUM(amount_paid) AS total_amount
    FROM payment_splits
    GROUP BY payment_method
    """,
    conn
    )

    st.dataframe(payment_chart)

    fig, ax = plt.subplots()

    ax.pie(
        payment_chart["total_amount"],
        labels=payment_chart["payment_method"],
        autopct="%1.1f%%"
    )

    ax.set_title("Payment Method Distribution")

    st.pyplot(fig)

    st.subheader("Open vs Close Status")

    status_chart = pd.read_sql(
    """
    SELECT
    status,
    COUNT(*) AS total
    FROM customer_sales
    GROUP BY status
    """,
    conn
    )

    st.dataframe(status_chart)

    st.bar_chart(
        status_chart.set_index("status")
    )

#Close Database connection
conn.close()