import streamlit as st
from datetime import date, datetime
import pandas as pd
import qrcode
from io import BytesIO


# ============================================================
# DIRECTORATE OF TOURISM SERVICES
# OFFICE AUTOMATION SYSTEM - PHASE 1
# ============================================================

st.set_page_config(
    page_title="Directorate of Tourism Services",
    page_icon="🏛️",
    layout="wide"
)


# ============================================================
# OFFICIAL FEE STRUCTURE
# ============================================================

FEES = {
    "Grant of Licence": 45000,
    "Renewal Fees": 20000,
    "Field of Operation Fees": 25000,
    "Endorsement Fees": 5000,
    "Late Fees": 5000,
}


# ============================================================
# DEMO USERS
# ============================================================

USERS = {
    "controller": {
        "password": "controller123",
        "role": "Controller",
        "name": "Controller"
    },

    "tnt": {
        "password": "tnt123",
        "role": "T&T",
        "name": "T&T Section"
    },

    "inspector1": {
        "password": "demo123",
        "role": "Inspector",
        "name": "Inspector Demo"
    },

    "inspector2": {
        "password": "demo123",
        "role": "Inspector",
        "name": "Inspector 2"
    },

    "inspector3": {
        "password": "demo123",
        "role": "Inspector",
        "name": "Inspector 3"
    },
}


# ============================================================
# DOCUMENT CHECKLIST
# ============================================================

COMMON_DOCS = [
    "Application on prescribed Form-I",
    "Bank Certificate",
    "Balance Sheet",
    "Valid NTN Certificate",
    "Sketch map of premises",
    "Attested Rent / Lease Agreement & CNIC of Landlord",
    "List of staff with CNIC, qualifications & experience",
    "Particulars of Owner / Partners / Directors",
    "800 C.C. Car documents in owner's name",
    "Bank Guarantee",
]


EXTRA_DOCS = {

    "Sole Proprietorship": [],

    "Partnership": [
        "Registration Certificate from Registrar of Firms",
        "Partnership Deed & Share Composition",
    ],

    "Directorship (Company)": [
        "Memorandum of Association",
        "Certificate of Incorporation",
    ],
}


# ============================================================
# SESSION STATE
# ============================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "login_mode" not in st.session_state:
    st.session_state.login_mode = None

if "events" not in st.session_state:
    st.session_state.events = []

if "checklists" not in st.session_state:
    st.session_state.checklists = {}

if "letters" not in st.session_state:
    st.session_state.letters = {}

if "challans" not in st.session_state:
    st.session_state.challans = {}


# ============================================================
# DUMMY DATA
# ============================================================

if "cases" not in st.session_state:

    st.session_state.cases = [

        {
            "file": "T&T-001",
            "agency": "ABC Travels",
            "type": "Sole Proprietorship",
            "owner": "Ali Khan",
            "address": "Karachi",
            "contact": "0300-1111111",

            "licence": "",
            "status": "Documents Checking",

            "inspector": "",
            "marked": "",

            "report": "",
            "report_date": "",
            "decision": "",

            "challan": "Not Generated",

            "licence_from": "",
            "valid_to": "",
        },

        {
            "file": "T&T-002",
            "agency": "XYZ Travels",
            "type": "Partnership",
            "owner": "Sara Ahmed",
            "address": "Karachi",
            "contact": "0300-2222222",

            "licence": "",
            "status": "Waiting for Paid Challan",

            "inspector": "",
            "marked": "",

            "report": "",
            "report_date": "",
            "decision": "",

            "challan": "Paid",

            "licence_from": "",
            "valid_to": "",
        },

        {
            "file": "T&T-003",
            "agency": "City Tours",
            "type": "Directorship (Company)",
            "owner": "Usman Raza",
            "address": "Karachi",
            "contact": "0300-3333333",

            "licence": "",
            "status": "Inspection Due",

            "inspector": "Inspector Demo",
            "marked": "2026-08-25",

            "report": "",
            "report_date": "",
            "decision": "",

            "challan": "Paid",

            "licence_from": "",
            "valid_to": "",
        },

        {
            "file": "T&T-004",
            "agency": "Pak International Travels",
            "type": "Partnership",
            "owner": "Hina Malik",
            "address": "Karachi",
            "contact": "0300-4444444",

            "licence": "TT-004",
            "status": "Expired",

            "inspector": "",
            "marked": "",

            "report": "",
            "report_date": "",
            "decision": "",

            "challan": "Not Generated",

            "licence_from": "2025-05-15",
            "valid_to": "2026-05-14",
        },
    ]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_case(file_no):

    for case in st.session_state.cases:

        if case["file"] == file_no:
            return case

    return None


def required_documents(case):

    return COMMON_DOCS + EXTRA_DOCS[case["type"]]


def get_checklist(file_no):

    if file_no not in st.session_state.checklists:

        case = get_case(file_no)

        st.session_state.checklists[file_no] = {
            document: False
            for document in required_documents(case)
        }

    return st.session_state.checklists[file_no]


def log_event(file_no, event):

    st.session_state.events.append({

        "File No.": file_no,

        "Date / Time":
            datetime.now().strftime("%Y-%m-%d %H:%M"),

        "Event": event
    })


def calculate_late_fee(years):

    return int(years) * FEES["Late Fees"]


def licence_status(case):

    if case["status"] == "Cancelled":

        return "Cancelled"

    if case.get("valid_to"):

        try:

            expiry = date.fromisoformat(
                case["valid_to"]
            )

            if date.today() > expiry:

                return "Expired"

            return "Active"

        except:

            pass

    return case["status"]


def generate_qr(text):

    qr = qrcode.make(text)

    buffer = BytesIO()

    qr.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


# ============================================================
# LETTER GENERATOR
# ============================================================

def generate_letter(
    letter_type,
    case,
    missing_documents=None
):

    missing_documents = missing_documents or []

    if letter_type == "Short of Documents":

        body = """
The following documents are incomplete / missing:

"""

        for number, document in enumerate(
            missing_documents,
            start=1
        ):

            body += (
                f"{number}. {document}\n"
            )

    elif letter_type == "Police Clearance Letter":

        body = f"""
Police Clearance / Character Verification
is requested in respect of:

M/s {case['agency']}

Address:
{case['address']}
"""

    elif letter_type == "Verification of Bank Certificate":

        body = f"""
Kindly verify the Bank Certificate submitted by:

M/s {case['agency']}

Address:
{case['address']}

and communicate confirmation to this office.
"""

    elif letter_type == "Verification of Bank Guarantee":

        body = f"""
Kindly verify the Bank Guarantee submitted by:

M/s {case['agency']}

Address:
{case['address']}

and communicate confirmation to this office.
"""

    elif letter_type == "Licence Approval Letter":

        body = f"""
The case of M/s {case['agency']}
is submitted for approval and grant of
Travel Agency Licence.
"""

    else:

        body = ""

    return f"""
DIRECTORATE OF TOURISM SERVICES
GOVERNMENT OF SINDH


File No.: {case['file']}

Date: {date.today().strftime('%d-%m-%Y')}


SUBJECT: {letter_type.upper()}


M/s {case['agency']}

Address:
{case['address']}


{body}


Assistant Controller
T&T Section
Directorate of Tourism Services
"""


# ============================================================
# CHALLAN GENERATOR
# ============================================================

def generate_challan(
    case,
    purpose,
    include_field=False,
    include_endorsement=False,
    years_late=0
):

    grant_fee = 0
    renewal_fee = 0
    field_fee = 0
    endorsement_fee = 0
    late_fee = 0


    if purpose == "Fresh Licence":

        grant_fee = FEES["Grant of Licence"]


    elif purpose == "Renewal":

        renewal_fee = FEES["Renewal Fees"]

        if include_field:

            field_fee = FEES["Field of Operation Fees"]

        if include_endorsement:

            endorsement_fee = FEES["Endorsement Fees"]

        if years_late > 0:

            late_fee = calculate_late_fee(
                years_late
            )


    total = (
        grant_fee
        + renewal_fee
        + field_fee
        + endorsement_fee
        + late_fee
    )


    challan = f"""
PROVINCIAL TREASURY CHALLAN
(T.R-6)


DIRECTORATE OF TOURISM SERVICES
GOVERNMENT OF SINDH


File No.:
{case['file']}


Travel Agency:
{case['agency']}


Address:
{case['address']}


Purpose:
{purpose}


--------------------------------------------

Grant of Licence Fees:
Rs. {grant_fee:,}


Renewal Fees:
Rs. {renewal_fee:,}


Field of Operation Fees:
Rs. {field_fee:,}


Endorsement Fees:
Rs. {endorsement_fee:,}


Late Fees:
Rs. {late_fee:,}


--------------------------------------------

TOTAL PAYABLE:

Rs. {total:,}


--------------------------------------------


Late Fee Rule:

Rs. 5,000 per overdue renewal year.


D.D.O CODE NO. KQ-0741


Date:
{date.today().strftime('%d-%m-%Y')}


Tenderer Signature:
____________________________


Bank / Treasury:
____________________________
"""

    return challan, total


# ============================================================
# DIGITAL LICENCE
# ============================================================

def generate_licence(case):

    return f"""
FORM II

(REINFORCING RULE 3(1)
OF TRAVEL AGENCIES RULES, 1977)


FORM OF LICENCE


DEPARTMENT OF TOURIST SERVICES

Government of Pakistan


Licence No.:
{case['licence']}


M/s / Messrs:
{case['agency']}


Address:
{case['address']}


Owner / Representative:
{case['owner']}


This licence is electronically generated
through the DTS Office Automation System.


Valid From:
{case['licence_from']}


Valid To:
{case['valid_to']}


Status:
{licence_status(case)}


Signature of Controller:

____________________________
"""


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.user:

    st.markdown(
        """
        <style>

        .hero {

            padding: 45px 20px;

            text-align: center;

            border-bottom:
                1px solid #dddddd;

            margin-bottom: 30px;
        }

        .hero h1 {

            font-size: 40px;
        }

        .hero p {

            font-size: 18px;
        }

        </style>

        <div class="hero">

            <h1>
            🏛️ Directorate of Tourism Services
            </h1>

            <p>
            Government of Sindh
            </p>

            <p>
            Office Automation Portal
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.subheader("Select Portal")


    col1, col2, col3 = st.columns(3)


    if col1.button(
        "🔐 Controller Login",
        use_container_width=True
    ):

        st.session_state.login_mode = "Controller"


    if col2.button(
        "📋 T&T Login",
        use_container_width=True
    ):

        st.session_state.login_mode = "T&T"


    if col3.button(
        "👨‍💼 Inspector Login",
        use_container_width=True
    ):

        st.session_state.login_mode = "Inspector"


    if st.session_state.login_mode:

        st.divider()

        role = st.session_state.login_mode

        st.subheader(
            f"{role} Login"
        )


        with st.form("login_form"):

            username = st.text_input(
                "Username"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            login = st.form_submit_button(
                "Login"
            )


        if login:

            user = USERS.get(username)

            if (
                user
                and user["password"] == password
                and user["role"] == role
            ):

                st.session_state.user = username

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )


        st.caption(
            """
Demo:

Controller:
controller / controller123

T&T:
tnt / tnt123

Inspector:
inspector1 / demo123
"""
        )


    st.stop()


# ============================================================
# USER INFORMATION
# ============================================================

current_user = USERS[
    st.session_state.user
]

role = current_user["role"]

display_name = current_user["name"]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🏛️ DTS Automation"
)

st.sidebar.write(
    f"Logged in as: **{display_name}**"
)


if st.sidebar.button("Logout"):

    st.session_state.user = None

    st.rerun()


# ============================================================
# INSPECTOR PANEL
# ============================================================

if role == "Inspector":

    st.title(
        "👨‍💼 Inspector Panel"
    )


    my_files = [

        case

        for case in st.session_state.cases

        if case["inspector"] == display_name
    ]


    pending = [

        case

        for case in my_files

        if case["status"]
        in [
            "Inspection Due",
            "Deficiency / Re-Inspection"
        ]
    ]


    submitted = [

        case

        for case in my_files

        if case["report_date"]
    ]


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "My Files",
        len(my_files)
    )


    col2.metric(
        "Pending Inspection",
        len(pending)
    )


    col3.metric(
        "Reports Submitted",
        len(submitted)
    )


    tab1, tab2 = st.tabs(
        [
            "📂 Inspection Queue",
            "✅ Submitted Reports"
        ]
    )


    # --------------------------------------------------------
    # INSPECTION QUEUE
    # --------------------------------------------------------

    with tab1:

        search = st.text_input(
            "Search Agency / File"
        )


        for case in sorted(
            pending,
            key=lambda x: x["marked"],
            reverse=True
        ):

            if search:

                searchable = (
                    case["agency"]
                    + " "
                    + case["file"]
                ).lower()

                if search.lower() not in searchable:

                    continue


            with st.container(
                border=True
            ):

                st.subheader(
                    f"{case['agency']} "
                    f"— {case['file']}"
                )


                st.write(
                    f"""
**Inspection Marked:**
{case['marked']}

**Status:**
{case['status']}

**Challan:**
{case['challan']}
"""
                )


                st.write(
                    f"""
Owner:
{case['owner']}

Address:
{case['address']}

Contact:
{case['contact']}
"""
                )


                decision = st.radio(

                    "Inspection Decision",

                    [
                        "Recommend for Licence",
                        "Not Recommended / Deficiency"
                    ],

                    key="decision_" + case["file"]
                )


                report = st.text_area(

                    "Inspection Report / Deficiency",

                    key="report_" + case["file"]
                )


                if st.button(

                    "Submit Inspection Report",

                    key="submit_" + case["file"]
                ):

                    case["decision"] = decision

                    case["report"] = report

                    case["report_date"] = (
                        datetime.now()
                        .strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    )


                    if (
                        decision
                        == "Recommend for Licence"
                    ):

                        case["status"] = (
                            "Recommended for Licence"
                        )

                    else:

                        case["status"] = (
                            "Deficiency / Re-Inspection"
                        )


                    log_event(

                        case["file"],

                        f"{display_name}: "
                        f"{decision}"
                    )


                    st.success(
                        "Inspection report submitted."
                    )

                    st.rerun()


    # --------------------------------------------------------
    # SUBMITTED REPORTS
    # --------------------------------------------------------

    with tab2:

        rows = []


        for case in submitted:

            rows.append({

                "File":
                    case["file"],

                "Agency":
                    case["agency"],

                "Inspection Marked":
                    case["marked"],

                "Decision":
                    case["decision"],

                "Report Submitted":
                    case["report_date"],

                "Status":
                    case["status"]
            })


        st.dataframe(

            pd.DataFrame(rows),

            use_container_width=True,

            hide_index=True
        )


    st.stop()


# ============================================================
# CONTROLLER PANEL
# ============================================================

if role == "Controller":

    menu = st.sidebar.radio(

        "Controller Menu",

        [
            "Dashboard",
            "Complete Records",
            "Inspection Assignment",
            "Inspection Reports",
            "Licence Records",
            "Case History"
        ]
    )


    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    if menu == "Dashboard":

        st.title(
            "Controller Dashboard"
        )


        cases = st.session_state.cases


        col1, col2, col3, col4, col5 = st.columns(5)


        col1.metric(
            "Total Cases",
            len(cases)
        )


        col2.metric(
            "Inspection Due",

            sum(
                x["status"]
                == "Inspection Due"

                for x in cases
            )
        )


        col3.metric(
            "Recommended",

            sum(
                x["status"]
                == "Recommended for Licence"

                for x in cases
            )
        )


        col4.metric(
            "Active Licences",

            sum(
                licence_status(x)
                == "Active"

                for x in cases
            )
        )


        col5.metric(
            "Expired",

            sum(
                licence_status(x)
                == "Expired"

                for x in cases
            )
        )


        st.subheader(
            "Inspector Workload"
        )


        inspectors = [

            user["name"]

            for user in USERS.values()

            if user["role"] == "Inspector"
        ]


        workload = []


        for inspector in inspectors:

            workload.append({

                "Inspector":
                    inspector,

                "Pending Files":

                    sum(

                        x["inspector"] == inspector

                        and x["status"]
                        in [
                            "Inspection Due",
                            "Deficiency / Re-Inspection"
                        ]

                        for x in cases
                    ),

                "Reports Submitted":

                    sum(

                        x["inspector"] == inspector

                        and bool(x["report_date"])

                        for x in cases
                    )
            })


        st.dataframe(

            pd.DataFrame(workload),

            use_container_width=True,

            hide_index=True
        )


    # --------------------------------------------------------
    # COMPLETE RECORDS
    # --------------------------------------------------------

    elif menu == "Complete Records":

        st.title(
            "Complete Office Records"
        )


        df = pd.DataFrame(
            st.session_state.cases
        )


        df["Licence Status"] = df.apply(
            licence_status,
            axis=1
        )


        status_filter = st.selectbox(

            "Status",

            ["All"]
            + sorted(
                df["status"].unique()
            )
        )


        inspector_filter = st.selectbox(

            "Inspector",

            ["All"]
            + sorted(
                [
                    user["name"]

                    for user in USERS.values()

                    if user["role"]
                    == "Inspector"
                ]
            )
        )


        if status_filter != "All":

            df = df[
                df["status"]
                == status_filter
            ]


        if inspector_filter != "All":

            df = df[
                df["inspector"]
                == inspector_filter
            ]


        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True
        )


    # --------------------------------------------------------
    # INSPECTION ASSIGNMENT
    # --------------------------------------------------------

    elif menu == "Inspection Assignment":

        st.title(
            "Mark / Assign Inspection"
        )


        file_no = st.selectbox(

            "Select File",

            [
                x["file"]

                for x in st.session_state.cases
            ]
        )


        case = get_case(file_no)


        inspectors = [

            user["name"]

            for user in USERS.values()

            if user["role"] == "Inspector"
        ]


        inspector = st.selectbox(

            "Assign Inspector",

            inspectors
        )


        if st.button(
            "Mark Inspection"
        ):

            case["inspector"] = inspector

            case["marked"] = (
                date.today().isoformat()
            )

            case["status"] = (
                "Inspection Due"
            )


            log_event(

                file_no,

                f"Controller marked inspection "
                f"for {inspector} on "
                f"{case['marked']}"
            )


            st.success(
                f"""
Inspection marked on
{case['marked']}

Assigned to:
{inspector}
"""
            )


        st.info(

            f"""
Current Inspector:
{case['inspector'] or 'Not Assigned'}

Inspection Date:
{case['marked'] or 'Not Marked'}
"""
        )


    # --------------------------------------------------------
    # INSPECTION REPORTS
    # --------------------------------------------------------

    elif menu == "Inspection Reports":

        st.title(
            "Inspection Reports"
        )


        reports = [

            x

            for x in st.session_state.cases

            if x["report_date"]
        ]


        for case in reports:

            with st.container(
                border=True
            ):

                st.subheader(
                    f"{case['agency']} "
                    f"— {case['file']}"
                )


                st.write(

                    f"""
Inspector:
**{case['inspector']}**

Decision:
**{case['decision']}**

Submitted:
**{case['report_date']}**
"""
                )


                st.text_area(

                    "Inspection Report",

                    case["report"],

                    height=180,

                    key="view_"
                    + case["file"]
                )


    # --------------------------------------------------------
    # LICENCE RECORDS
    # --------------------------------------------------------

    elif menu == "Licence Records":

        st.title(
            "Licence Records"
        )


        for case in st.session_state.cases:

            if not case["licence"]:

                continue


            status = licence_status(
                case
            )


            if status == "Expired":

                st.markdown(
                    f"""
                    <div style="
                    background:#ead7c5;
                    padding:15px;
                    border-radius:8px;
                    margin-bottom:10px;">
                    🟤 <b>
                    {case['agency']}
                    —
                    {case['licence']}
                    —
                    EXPIRED
                    </b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            elif status == "Cancelled":

                st.markdown(
                    f"""
                    <div style="
                    background:#f4cccc;
                    padding:15px;
                    border-radius:8px;
                    margin-bottom:10px;">
                    🔴 <b>
                    {case['agency']}
                    —
                    {case['licence']}
                    —
                    CANCELLED
                    </b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            else:

                st.success(
                    f"""
                    🟢 {case['agency']}
                    —
                    {case['licence']}
                    —
                    {status}
                    """
                )


            st.caption(

                f"""
Valid From:
{case.get('licence_from', '—')}

Valid To:
{case.get('valid_to', '—')}
"""
            )


    # --------------------------------------------------------
    # CASE HISTORY
    # --------------------------------------------------------

    else:

        st.title(
            "Case History"
        )


        file_no = st.selectbox(

            "Select File",

            [
                x["file"]

                for x in st.session_state.cases
            ]
        )


        events = [

            event

            for event in st.session_state.events

            if event["File No."]
            == file_no
        ]


        st.dataframe(

            pd.DataFrame(events),

            use_container_width=True,

            hide_index=True
        )


# ============================================================
# T&T PANEL
# ============================================================

else:

    menu = st.sidebar.radio(

        "T&T Menu",

        [
            "Dashboard",
            "Fresh Case Registration",
            "Document Checklist",
            "Letters",
            "Challan",
            "Licence Generation",
            "Record Search",
            "Case History"
        ]
    )


    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    if menu == "Dashboard":

        st.title(
            "T&T Section Dashboard"
        )


        cases = st.session_state.cases


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Total Cases",
            len(cases)
        )


        col2.metric(

            "Documents Checking",

            sum(

                x["status"]
                == "Documents Checking"

                for x in cases
            )
        )


        col3.metric(

            "Inspection Due",

            sum(

                x["status"]
                == "Inspection Due"

                for x in cases
            )
        )


        col4.metric(

            "Licences",

            sum(
                bool(x["licence"])
                for x in cases
            )
        )


        st.dataframe(

            pd.DataFrame(cases),

            use_container_width=True,

            hide_index=True
        )


    # --------------------------------------------------------
    # FRESH CASE REGISTRATION
    # --------------------------------------------------------

    elif menu == "Fresh Case Registration":

        st.title(
            "Register Fresh Travel Agency Case"
        )


        with st.form(
            "new_case"
        ):

            file_no = st.text_input(
                "File Number"
            )

            agency = st.text_input(
                "Travel Agency Name"
            )

            business_type = st.selectbox(

                "Business Type",

                list(EXTRA_DOCS.keys())
            )

            owner = st.text_input(
                "Owner / Partners / Directors"
            )

            address = st.text_input(
                "Address"
            )

            contact = st.text_input(
                "Contact"
            )


            submit = st.form_submit_button(
                "Register Fresh Case"
            )


        if submit:

            if not file_no or not agency:

                st.error(
                    "File Number and Agency Name are required."
                )

            elif any(
                x["file"] == file_no
                for x in st.session_state.cases
            ):

                st.error(
                    "File number already exists."
                )

            else:

                st.session_state.cases.append({

                    "file": file_no,

                    "agency": agency,

                    "type": business_type,

                    "owner": owner,

                    "address": address,

                    "contact": contact,

                    "licence": "",

                    "status":
                        "Documents Checking",

                    "inspector": "",

                    "marked": "",

                    "report": "",

                    "report_date": "",

                    "decision": "",

                    "challan":
                        "Not Generated",

                    "licence_from": "",

                    "valid_to": "",
                })


                get_checklist(
                    file_no
                )


                log_event(

                    file_no,

                    "Fresh case registered / "
                    "Daak received"
                )


                st.success(
                    "Fresh case registered."
                )


    # --------------------------------------------------------
    # DOCUMENT CHECKLIST
    # --------------------------------------------------------

    elif menu == "Document Checklist":

        st.title(
            "📋 Required Documents Checklist"
        )


        file_no = st.selectbox(

            "Select File",

            [
                x["file"]

                for x in st.session_state.cases
            ]
        )


        case = get_case(
            file_no
        )


        checklist = get_checklist(
            file_no
        )


        st.info(

            f"""
Agency:
{case['agency']}

Business Type:
{case['type']}
"""
        )


        for document in list(
            checklist.keys()
        ):

            checklist[document] = st.checkbox(

                document,

                value=checklist[document],

                key=(
                    "document_"
                    + file_no
                    + "_"
                    + document
                )
            )


        missing = [

            document

            for document, checked
            in checklist.items()

            if not checked
        ]


        if missing:

            st.warning(

                f"{len(missing)} "
                "document(s) missing."
            )


            if st.button(
                "Generate Short of Documents Letter"
            ):

                st.session_state.letters[

                    (
                        "Short of Documents",
                        file_no
                    )

                ] = generate_letter(

                    "Short of Documents",

                    case,

                    missing
                )


                log_event(

                    file_no,

                    "Short of Documents "
                    "letter generated"
                )


                st.success(
                    "Letter generated."
                )


        else:

            st.success(
                "All required documents received."
            )


            case["status"] = (
                "Documents Complete"
            )


            st.subheader(
                "Verification Letters"
            )


            col1, col2, col3 = st.columns(3)


            if col1.button(
                "Police Clearance Letter"
            ):

                st.session_state.letters[

                    (
                        "Police Clearance Letter",
                        file_no
                    )

                ] = generate_letter(

                    "Police Clearance Letter",

                    case
                )


                log_event(

                    file_no,

                    "Police Clearance "
                    "letter generated"
                )


                st.success(
                    "Police Clearance letter generated."
                )


            if col2.button(
                "Bank Certificate Verification"
            ):

                st.session_state.letters[

                    (
                        "Verification of Bank Certificate",
                        file_no
                    )

                ] = generate_letter(

                    "Verification of Bank Certificate",

                    case
                )


                log_event(

                    file_no,

                    "Bank Certificate "
                    "Verification generated"
                )


                st.success(
                    "Bank Certificate verification generated."
                )


            if col3.button(
                "Bank Guarantee Verification"
            ):

                st.session_state.letters[

                    (
                        "Verification of Bank Guarantee",
                        file_no
                    )

                ] = generate_letter(

                    "Verification of Bank Guarantee",

                    case
                )


                log_event(

                    file_no,

                    "Bank Guarantee "
                    "Verification generated"
                )


                st.success(
                    "Bank Guarantee verification generated."
                )


        st.divider()


        st.markdown(
            "### Vehicle Verification"
        )


        st.markdown(
            "[Open Sindh Excise Vehicle Search]"
            "(https://excise.gos.pk/vehicle/vehicle_search)"
        )


    # --------------------------------------------------------
    # LETTERS
    # --------------------------------------------------------

    elif menu == "Letters":

        st.title(
            "📄 Letters — Edit / Print"
        )


        file_no = st.selectbox(

            "Select File",

            [
                x["file"]

                for x in st.session_state.cases
            ]
        )


        case = get_case(
            file_no
        )


        letter_type = st.selectbox(

            "Letter Type",

            [
                "Short of Documents",

                "Police Clearance Letter",

                "Verification of Bank Certificate",

                "Verification of Bank Guarantee",

                "Licence Approval Letter"
            ]
        )


        key = (
            letter_type,
            file_no
        )


        if key not in st.session_state.letters:

            missing = [

                d

                for d, checked
                in get_checklist(
                    file_no
                ).items()

                if not checked
            ]


            st.session_state.letters[key] = (
                generate_letter(
                    letter_type,
                    case,
                    missing
                )
            )


        edited_letter = st.text_area(

            "Edit Letter",

            st.session_state.letters[key],

            height=500
        )


        st.session_state.letters[key] = (
            edited_letter
        )


        st.download_button(

            "🖨️ Print / Download Letter",

            edited_letter,

            file_name=(
                f"{file_no}_"
                f"{letter_type.replace(' ', '_')}.txt"
            ),

            mime="text/plain"
        )


        if st.button(
            "📧 Email Letter"
        ):

            st.info(
                "Email integration will be "
                "connected in the production phase."
            )


    # --------------------------------------------------------
    # CHALLAN
    # --------------------------------------------------------

    elif menu == "Challan":

        st.title(
            "💰 Challan Generation"
        )


        file_no = st.selectbox(

            "Select File",

            [
                x["file"]

                for x in st.session_state.cases
            ]
        )


        case = get_case(
            file_no
        )


        purpose = st.selectbox(

            "Challan Purpose",

            [
                "Fresh Licence",
                "Renewal"
            ]
        )


        # ====================================================
        # FRESH
        # ====================================================

        if purpose == "Fresh Licence":

            st.success(

                f"""
Grant of Licence Fees:

Rs. {FEES['Grant of Licence']:,}
"""
            )


            st.metric(

                "Total Challan",

                f"Rs. {FEES['Grant of Licence']:,}"
            )


            challan_text, total = (
                generate_challan(
                    case,
                    "Fresh Licence"
                )
            )


        # ====================================================
        # RENEWAL
        # ====================================================

        else:

            st.info(

                f"""
Renewal Fees:

Rs. {FEES['Renewal Fees']:,}
"""
            )


            field_operation = st.checkbox(

                f"""
Field of Operation Fees
— Rs. {FEES['Field of Operation Fees']:,}
"""
            )


            endorsement = st.checkbox(

                f"""
Endorsement Fees
— Rs. {FEES['Endorsement Fees']:,}
"""
            )


            expired = (
                licence_status(case)
                == "Expired"
            )


            years_late = 0


            if expired:

                st.warning(

                    """
🟤 This licence is EXPIRED.

Late fee will be automatically
calculated at Rs. 5,000 per
overdue renewal year.
"""
                )


                years_late = st.number_input(

                    "Overdue Renewal Years",

                    min_value=1,

                    max_value=20,

                    value=1,

                    step=1
                )


                automatic_late_fee = (
                    calculate_late_fee(
                        years_late
                    )
                )


                st.metric(

                    "Automatic Late Fee",

                    f"Rs. {automatic_late_fee:,}"
                )


            else:

                st.success(
                    "Licence is not expired."
                )


            challan_text, total = (
                generate_challan(

                    case,

                    "Renewal",

                    include_field=
                        field_operation,

                    include_endorsement=
                        endorsement,

                    years_late=
                        years_late
                )
            )


            st.metric(

                "TOTAL PAYABLE",

                f"Rs. {total:,}"
            )


        # ====================================================
        # EDIT CHALLAN
        # ====================================================

        edited_challan = st.text_area(

            "Edit Challan",

            challan_text,

            height=500
        )


        if st.button(
            "Generate / Save Challan"
        ):

            case["challan"] = (
                "Generated"
            )


            st.session_state.challans[
                file_no
            ] = edited_challan


            log_event(

                file_no,

                f"Challan generated — "
                f"Total Rs. {total:,}"
            )


            st.success(
                "Challan generated and saved."
            )


        st.download_button(

            "🖨️ Print / Download Challan",

            edited_challan,

            file_name=
                f"{file_no}_Challan.txt",

            mime="text/plain"
        )


    # --------------------------------------------------------
    # LICENCE GENERATION
    # --------------------------------------------------------

    elif menu == "Licence Generation":

        st.title(
            "🪪 Digital Licence Generation"
        )


        candidates = [

            x

            for x in st.session_state.cases

            if x["status"]
            == "Recommended for Licence"
        ]


        if not candidates:

            st.info(

                """
No case is currently
recommended for licence.
"""
            )

        else:

            file_no = st.selectbox(

                "Recommended Case",

                [
                    x["file"]
                    for x in candidates
                ]
            )


            case = get_case(
                file_no
            )


            licence_number = st.text_input(

                "Licence Number"
            )


            valid_from = st.date_input(

                "Valid From",

                date.today()
            )


            valid_to = st.date_input(

                "Valid To",

                date(

                    valid_from.year + 1,

                    valid_from.month,

                    valid_from.day
                )
            )


            if st.button(
                "Generate Digital Licence"
            ):

                case["licence"] = (
                    licence_number
                )

                case["licence_from"] = (
                    valid_from.isoformat()
                )

                case["valid_to"] = (
                    valid_to.isoformat()
                )

                case["status"] = "Active"


                log_event(

                    file_no,

                    "Licence generated"
                )


                st.success(
                    "Digital Licence Generated."
                )


                st.code(
                    generate_licence(case)
                )


                qr_data = (

                    "DTS-LICENCE|"
                    + licence_number
                    + "|"
                    + case["agency"]
                    + "|"
                    + case["address"]
                    + "|"
                    + case["owner"]
                    + "|"
                    + str(valid_from)
                    + "|"
                    + str(valid_to)
                )


                st.image(

                    generate_qr(qr_data),

                    caption=
                        "Digital Licence QR Code"
                )


    # --------------------------------------------------------
    # RECORD SEARCH
    # --------------------------------------------------------

    elif menu == "Record Search":

        st.title(
            "🔎 Record Search / Filter"
        )


        df = pd.DataFrame(
            st.session_state.cases
        )


        df["Licence Status"] = df.apply(
            licence_status,
            axis=1
        )


        search = st.text_input(

            """
Search Agency / File /
Licence / Owner
"""
        )


        status = st.selectbox(

            "Status",

            [
                "All"
            ]
            + sorted(
                df["status"].unique()
            )
        )


        if search:

            mask = df.astype(
                str
            ).apply(

                lambda column:

                column.str.contains(

                    search,

                    case=False,

                    na=False
                )

            ).any(axis=1)


            df = df[mask]


        if status != "All":

            df = df[
                df["status"]
                == status
            ]


        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True
        )


    # --------------------------------------------------------
    # CASE HISTORY
    # --------------------------------------------------------

    else:

        st.title(
            "Case History"
        )


        file_no = st.selectbox(

            "Select File",

            [
                x["file"]

                for x in st.session_state.cases
            ]
        )


        events = [

            event

            for event in st.session_state.events

            if event["File No."]
            == file_no
        ]


        st.dataframe(

            pd.DataFrame(events),

            use_container_width=True,

            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    """
Directorate of Tourism Services —
Office Automation Prototype

Fee Structure:
Grant of Licence Rs.45,000 |
Renewal Rs.20,000 |
Field of Operation Rs.25,000 |
Endorsement Rs.5,000 |
Late Fee Rs.5,000 per overdue year
"""
)
