<script setup>
import { ref, onMounted } from "vue";
import LogoutButton from "../components/LogoutButton.vue";
import api from "../services/api";
import { getCurrentUser } from "../services/authService";

const user = getCurrentUser();

const company = ref(null);
const jobs = ref([]);

const selectedJob = ref(null);
const applications = ref([]);
const applicationsLoading = ref(false);

const feedback = ref({});
const interviewForm = ref({});

const offerLetter = ref({});
const offerLetterInputKey = ref({});

const loading = ref(true);
const jobsLoading = ref(true);

const error = ref("");
const success = ref("");

const editing = ref(false);
const creatingJob = ref(false);
const editingJob = ref(null);

const exportLoading = ref(false);
const exportStatus = ref("");
const exportTaskId = ref(null);
let exportPollTimer = null;

const reportLoading = ref(false);
const reportStatus = ref("");
const reportTaskId = ref(null);
let reportPollTimer = null;

const form = ref({
    name: "",
    industry: "",
    location: "",
    website: "",
    description: "",
    hr_name: "",
    hr_email: ""
});

const jobForm = ref({
    title: "",
    description: "",
    location: "",
    salary: "",
    experience: "",
    skills_required: "",
    benefits: "",
    min_cgpa: "",
    deadline: "",
    application_limit: ""
});


function loadProfileForm() {
    form.value = {
        name: company.value.name,
        industry: company.value.industry,
        location: company.value.location,
        website: company.value.website || "",
        description: company.value.description || "",
        hr_name: company.value.hr_name,
        hr_email: company.value.hr_email
    };
}


async function fetchCompanyProfile() {
    try {
        const response = await api.get("/api/company/profile");

        company.value = response.data.company;
        loadProfileForm();

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to load company profile.";
    } finally {
        loading.value = false;
    }
}


async function fetchJobs() {
    jobsLoading.value = true;

    try {
        const response = await api.get("/api/company/jobs");

        jobs.value = response.data.jobs;

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to load jobs.";
    } finally {
        jobsLoading.value = false;
    }
}

async function viewApplicants(job) {
    error.value = "";
    success.value = "";

    selectedJob.value = job;
    applications.value = [];
    applicationsLoading.value = true;

    try {
        const response = await api.get(
            `/api/company/jobs/${job.id}/applications`
        );

        applications.value = response.data.applications;

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to load applicants.";
    } finally {
        applicationsLoading.value = false;
    }
}


function closeApplicants() {
    selectedJob.value = null;
    applications.value = [];
    feedback.value = {};
    interviewForm.value = {};
    offerLetter.value = {};
    offerLetterInputKey.value = {};
}


async function updateApplicationStatus(
    application,
    status
) {
    error.value = "";
    success.value = "";

    const remarks =
        feedback.value[application.id] || "";

    if (
        status === "Rejected" &&
        !remarks.trim()
    ) {
        error.value =
            "Feedback is required when rejecting an applicant.";
        return;
    }

    try {
        const response = await api.put(
            `/api/company/applications/${application.id}/status`,
            {
                status: status,
                remarks: remarks
            }
        );

        success.value = response.data.message;

        await viewApplicants(selectedJob.value);

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update application.";
    }
}


async function viewResume(application) {
    error.value = "";

    try {
        const response = await api.get(
            `/api/company/applications/${application.id}/resume`,
            {
                responseType: "blob"
            }
        );

        const fileURL = URL.createObjectURL(
            response.data
        );

        window.open(fileURL, "_blank");

        setTimeout(() => {
            URL.revokeObjectURL(fileURL);
        }, 60000);

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to open resume.";
    }
}

function formatUTCDateTime(value) {
    if (!value) {
        return "-";
    }

    const utcValue =
        value.endsWith("Z") ? value : `${value}Z`;

    const date = new Date(utcValue);

    if (isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short"
    });
}


function formatLocalDateTime(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short"
    });
}


function getInterviewForm(application) {
    if (!interviewForm.value[application.id]) {
        interviewForm.value[application.id] = {
            interview_datetime: "",
            interview_mode: "Online",
            interview_location: "",
            interview_notes: ""
        };
    }

    return interviewForm.value[application.id];
}


async function scheduleInterview(application) {
    error.value = "";
    success.value = "";

    const form = getInterviewForm(application);

    if (!form.interview_datetime) {
        error.value = "Interview date and time are required.";
        return;
    }

    try {
        const response = await api.put(
            `/api/company/applications/${application.id}/interview`,
            {
                interview_datetime:
                    form.interview_datetime,
                interview_mode:
                    form.interview_mode,
                interview_location:
                    form.interview_location,
                interview_notes:
                    form.interview_notes
            }
        );

        success.value = response.data.message;

        await viewApplicants(selectedJob.value);

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to schedule interview.";
    }
}


function selectOfferLetter(application, event) {
    const file = event.target.files[0];

    if (!file) {
        offerLetter.value[application.id] = null;
        return;
    }

    const extension = file.name
        .split(".")
        .pop()
        .toLowerCase();

    if (extension !== "pdf") {
        error.value =
            "Offer letter must be a PDF file.";

        event.target.value = "";
        offerLetter.value[application.id] = null;
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        error.value =
            "Offer letter must be smaller than 5 MB.";

        event.target.value = "";
        offerLetter.value[application.id] = null;
        return;
    }

    error.value = "";
    offerLetter.value[application.id] = file;
}


async function updateFinalStatus(
    application,
    status
) {
    error.value = "";
    success.value = "";

    const remarks =
        feedback.value[application.id] || "";

    if (
        status === "Rejected" &&
        !remarks.trim()
    ) {
        error.value =
            "Feedback is required when rejecting an applicant.";
        return;
    }

    if (
        status === "Offer" &&
        !offerLetter.value[application.id]
    ) {
        error.value =
            "Please upload the offer letter PDF before issuing the offer.";
        return;
    }

    try {
        let response;

        if (status === "Offer") {
            const formData = new FormData();

            formData.append("status", status);
            formData.append("remarks", remarks);
            formData.append(
                "offer_letter",
                offerLetter.value[application.id]
            );

            response = await api.put(
                `/api/company/applications/${application.id}/final-status`,
                formData
            );
        } else {
            response = await api.put(
                `/api/company/applications/${application.id}/final-status`,
                {
                    status: status,
                    remarks: remarks
                }
            );
        }

        success.value = response.data.message;

        offerLetter.value[application.id] = null;
        offerLetterInputKey.value[application.id] =
            (offerLetterInputKey.value[application.id] || 0) + 1;

        await viewApplicants(selectedJob.value);

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update final status.";
    }
}


async function markAsPlaced(application) {
    error.value = "";
    success.value = "";

    try {
        const response = await api.put(
            `/api/company/applications/${application.id}/placed`
        );

        success.value = response.data.message;

        await viewApplicants(selectedJob.value);

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to mark applicant as placed.";
    }
}


function startEditing() {
    error.value = "";
    success.value = "";
    editing.value = true;
}


function cancelEditing() {
    error.value = "";
    success.value = "";

    loadProfileForm();

    editing.value = false;
}


async function updateCompanyProfile() {
    error.value = "";
    success.value = "";

    try {
        const response = await api.put(
            "/api/company/profile",
            form.value
        );

        success.value = response.data.message;

        editing.value = false;

        await fetchCompanyProfile();

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update company profile.";
    }
}


function resetJobForm() {
    jobForm.value = {
        title: "",
        description: "",
        location: "",
        salary: "",
        experience: "",
        skills_required: "",
        benefits: "",
        min_cgpa: "",
        deadline: "",
        application_limit: ""
    };
}


function startCreatingJob() {
    error.value = "";
    success.value = "";

    resetJobForm();

    editingJob.value = null;
    creatingJob.value = true;
}


function cancelJobForm() {
    resetJobForm();

    creatingJob.value = false;
    editingJob.value = null;

    error.value = "";
}


async function createJob() {
    error.value = "";
    success.value = "";

    try {
        const response = await api.post(
            "/api/company/jobs",
            jobForm.value
        );

        success.value = response.data.message;

        creatingJob.value = false;

        resetJobForm();

        await fetchJobs();

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to create job.";
    }
}


function startEditingJob(job) {
    error.value = "";
    success.value = "";

    editingJob.value = job.id;
    creatingJob.value = true;

    jobForm.value = {
        title: job.title,
        description: job.description,
        location: job.location,
        salary: job.salary ?? "",
        experience: job.experience ?? "",
        skills_required: job.skills_required ?? "",
        benefits: job.benefits ?? "",
        min_cgpa: job.min_cgpa ?? "",
        deadline: job.deadline,
        application_limit: job.application_limit ?? ""
    };
}


async function updateJob() {
    error.value = "";
    success.value = "";

    try {
        const response = await api.put(
            `/api/company/jobs/${editingJob.value}`,
            jobForm.value
        );

        success.value = response.data.message;

        creatingJob.value = false;
        editingJob.value = null;

        resetJobForm();

        await fetchJobs();

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update job.";
    }
}


async function changeJobStatus(job) {
    error.value = "";
    success.value = "";

    const newStatus =
        job.status === "Active"
            ? "Closed"
            : "Active";

    try {
        const response = await api.put(
            `/api/company/jobs/${job.id}/status`,
            {
                status: newStatus
            }
        );

        success.value = response.data.message;

        await fetchJobs();

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to change job status.";
    }
}


/* =========================
   CSV EXPORT
   ========================= */

async function startExport() {

    exportLoading.value = true;
    exportStatus.value = "Starting export...";
    error.value = "";
    success.value = "";

    try {

        const response = await api.post(
            "/api/company/export-history"
        );

        exportTaskId.value =
            response.data.task_id;

        exportStatus.value =
            "Export started. Preparing your CSV...";

        pollExportStatus();

    } catch (err) {

        exportLoading.value = false;
        exportStatus.value = "";

        error.value =
            err.response?.data?.message ||
            "Failed to start CSV export.";
    }
}


function pollExportStatus() {

    if (exportPollTimer) {
        clearTimeout(exportPollTimer);
    }

    exportPollTimer = setTimeout(
        checkExportStatus,
        1000
    );
}


async function checkExportStatus() {

    if (!exportTaskId.value) {
        return;
    }

    try {

        const response = await api.get(
            `/api/company/export-history/status/${exportTaskId.value}`
        );

        const status = response.data.status;

        if (
            status === "PENDING" ||
            status === "STARTED"
        ) {

            exportStatus.value =
                "Export is still being prepared...";

            pollExportStatus();

            return;
        }

        if (status === "SUCCESS") {

            exportStatus.value =
                "Export completed. Downloading...";

            await downloadExport();

            exportLoading.value = false;

            exportStatus.value =
                "CSV export completed successfully.";

            success.value =
                `Export completed. ${response.data.records || 0} records exported.`;

            return;
        }

        exportLoading.value = false;
        exportStatus.value = "";

        error.value =
            response.data.message ||
            "CSV export failed.";

    } catch (err) {

        exportLoading.value = false;
        exportStatus.value = "";

        error.value =
            err.response?.data?.message ||
            "Failed to check export status.";
    }
}


async function downloadExport() {

    const response = await api.get(
        `/api/company/export-history/download/${exportTaskId.value}`,
        {
            responseType: "blob"
        }
    );

    const blob = new Blob(
        [response.data],
        {
            type: "text/csv"
        }
    );

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    const disposition =
        response.headers["content-disposition"];

    if (disposition) {

        const filenameMatch =
            disposition.match(
                /filename="?([^"]+)"?/
            );

        if (filenameMatch) {
            link.download = filenameMatch[1];
        }
    }

    if (!link.download) {
        link.download =
            "company_application_history.csv";
    }

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
}


async function startPlacementReport() {

    reportLoading.value = true;
    reportStatus.value = "Starting report generation...";
    error.value = "";
    success.value = "";

    try {

        const response = await api.post(
            "/api/company/placement-report"
        );

        reportTaskId.value =
            response.data.task_id;

        reportStatus.value =
            "Report generation started...";

        pollPlacementReport();

    } catch (err) {

        reportLoading.value = false;
        reportStatus.value = "";

        error.value =
            err.response?.data?.message ||
            "Failed to start placement report.";
    }
}


function pollPlacementReport() {

    if (reportPollTimer) {
        clearTimeout(reportPollTimer);
    }

    reportPollTimer = setTimeout(
        checkPlacementReport,
        1000
    );
}


async function checkPlacementReport() {

    if (!reportTaskId.value) {
        return;
    }

    try {

        const response = await api.get(
            `/api/company/placement-report/status/${reportTaskId.value}`
        );

        const status = response.data.status;

        if (
            status === "PENDING" ||
            status === "STARTED"
        ) {

            reportStatus.value =
                "Generating placement report...";

            pollPlacementReport();

            return;
        }

        if (status === "SUCCESS") {

            reportStatus.value =
                "Report generated successfully.";

            reportLoading.value = false;

            success.value =
                `Report generated. ${response.data.total_applications || 0} applications and ${response.data.total_placements || 0} placements included.`;

            openPlacementReport();

            return;
        }

        reportLoading.value = false;
        reportStatus.value = "";

        error.value =
            response.data.message ||
            "Placement report generation failed.";

    } catch (err) {

        reportLoading.value = false;
        reportStatus.value = "";

        error.value =
            err.response?.data?.message ||
            "Failed to check report status.";
    }
}


async function openPlacementReport() {

    try {

        const response = await api.get(
            `/api/company/placement-report/download/${reportTaskId.value}`,
            {
                responseType: "blob"
            }
        );

        const blob = new Blob(
            [response.data],
            {
                type: "text/html"
            }
        );

        const url =
            window.URL.createObjectURL(blob);

        window.open(
            url,
            "_blank"
        );

        setTimeout(() => {
            window.URL.revokeObjectURL(url);
        }, 60000);

    } catch (err) {

        error.value =
            err.response?.data?.message ||
            "Failed to open placement report.";
    }
}


onMounted(() => {
    fetchCompanyProfile();
    fetchJobs();
});
</script>


<template>

    <div>

        <h1>Company Dashboard</h1>

        <h3>Welcome, {{ user.username }}</h3>

        <p>Role: {{ user.role }}</p>

        <hr>



        <p v-if="error">
            {{ error }}
        </p>

        <p v-if="success">
            {{ success }}
        </p>



        <h2>Company Profile</h2>

        <p v-if="loading">
            Loading company profile...
        </p>



        <div
            v-if="company && !loading && !editing"
        >

            <p>
                <strong>Company ID:</strong>
                {{ company.company_id }}
            </p>

            <p>
                <strong>Name:</strong>
                {{ company.name }}
            </p>

            <p>
                <strong>Industry:</strong>
                {{ company.industry }}
            </p>

            <p>
                <strong>Location:</strong>
                {{ company.location }}
            </p>

            <p>
                <strong>Website:</strong>
                {{ company.website || "Not provided" }}
            </p>

            <p>
                <strong>Description:</strong>
                {{ company.description || "Not provided" }}
            </p>

            <p>
                <strong>HR Name:</strong>
                {{ company.hr_name }}
            </p>

            <p>
                <strong>HR Email:</strong>
                {{ company.hr_email }}
            </p>

            <p>
                <strong>Status:</strong>
                {{ company.approved ? "Approved" : "Pending" }}
            </p>

            <p>
                <strong>Account:</strong>
                {{ company.is_active ? "Active" : "Inactive" }}
            </p>

            <button @click="startEditing">
                Edit Profile
            </button>

        </div>



        <div
            v-if="company && !loading && editing"
        >

            <form @submit.prevent="updateCompanyProfile">

                <div>
                    <label>Company Name</label>
                    <input
                        v-model="form.name"
                        type="text"
                        required
                    >
                </div>

                <div>
                    <label>Industry</label>
                    <input
                        v-model="form.industry"
                        type="text"
                        required
                    >
                </div>

                <div>
                    <label>Location</label>
                    <input
                        v-model="form.location"
                        type="text"
                        required
                    >
                </div>

                <div>
                    <label>Website</label>
                    <input
                        v-model="form.website"
                        type="text"
                    >
                </div>

                <div>
                    <label>Description</label>
                    <textarea
                        v-model="form.description"
                    ></textarea>
                </div>

                <div>
                    <label>HR Name</label>
                    <input
                        v-model="form.hr_name"
                        type="text"
                        required
                    >
                </div>

                <div>
                    <label>HR Email</label>
                    <input
                        v-model="form.hr_email"
                        type="email"
                        required
                    >
                </div>

                <button type="submit">
                    Save Changes
                </button>

                <button
                    type="button"
                    @click="cancelEditing"
                >
                    Cancel
                </button>

            </form>

        </div>


        <hr>



        <h2>Placement Drives</h2>

        <div class="dashboard-actions">

            <button
                v-if="!creatingJob"
                @click="startCreatingJob"
            >
                Create Placement Drive
            </button>

            <button
                class="export-button"
                @click="startExport"
                :disabled="exportLoading"
            >
                {{
                    exportLoading
                        ? "Exporting..."
                        : "Export Application History"
                }}
            </button>

            <button
                class="report-button"
                @click="startPlacementReport"
                :disabled="reportLoading"
            >
                {{
                    reportLoading
                        ? "Generating..."
                        : "Generate Placement Report"
                }}
            </button>

        </div>

        <p
            v-if="exportStatus"
            class="export-status"
        >
            {{ exportStatus }}
        </p>

        <p
            v-if="reportStatus"
            class="report-status"
        >
            {{ reportStatus }}
        </p>



        <div v-if="creatingJob">

            <h3>
                {{
                    editingJob
                        ? "Edit Placement Drive"
                        : "Create Placement Drive"
                }}
            </h3>

            <form
                @submit.prevent="
                    editingJob
                        ? updateJob()
                        : createJob()
                "
            >

                <div>
                    <label>Job Title</label>
                    <input
                        v-model="jobForm.title"
                        type="text"
                        required
                    >
                </div>


                <div>
                    <label>Description</label>
                    <textarea
                        v-model="jobForm.description"
                        required
                    ></textarea>
                </div>


                <div>
                    <label>Location</label>
                    <input
                        v-model="jobForm.location"
                        type="text"
                        required
                    >
                </div>


                <div>
                    <label>Salary</label>
                    <input
                        v-model="jobForm.salary"
                        type="number"
                        min="0"
                        step="0.01"
                    >
                </div>


                <div>
                    <label>Experience</label>
                    <input
                        v-model="jobForm.experience"
                        type="text"
                        required
                    >
                </div>


                <div>
                    <label>Required Skills</label>
                    <textarea
                        v-model="jobForm.skills_required"
                        required
                    ></textarea>
                </div>


                <div>
                    <label>Benefits</label>
                    <textarea
                        v-model="jobForm.benefits"
                    ></textarea>
                </div>


                <div>
                    <label>Minimum CGPA</label>
                    <input
                        v-model="jobForm.min_cgpa"
                        type="number"
                        min="0"
                        max="10"
                        step="0.01"
                        required
                    >
                </div>


                <div>
                    <label>Application Deadline</label>
                    <input
                        v-model="jobForm.deadline"
                        type="date"
                        required
                    >
                </div>


                <div>
                    <label>Application Limit</label>
                    <input
                        v-model="jobForm.application_limit"
                        type="number"
                        min="1"
                    >
                </div>


                <br>

                <button type="submit">
                    {{
                        editingJob
                            ? "Save Changes"
                            : "Create Drive"
                    }}
                </button>

                <button
                    type="button"
                    @click="cancelJobForm"
                >
                    Cancel
                </button>

            </form>

        </div>


        <br>



        <div>

            <h3>My Placement Drives</h3>

            <p v-if="jobsLoading">
                Loading placement drives...
            </p>

            <p
                v-else-if="jobs.length === 0"
            >
                No placement drives found.
            </p>


            <div
                v-for="job in jobs"
                :key="job.id"
            >

                <hr>

                <h4>{{ job.title }}</h4>

                <p>
                    <strong>Status:</strong>
                    {{ job.status }}
                </p>

                <p>
                    <strong>Location:</strong>
                    {{ job.location }}
                </p>

                <p>
                    <strong>Salary:</strong>
                    {{ job.salary ?? "Not specified" }}
                </p>

                <p>
                    <strong>Experience:</strong>
                    {{ job.experience }}
                </p>

                <p>
                    <strong>Required Skills:</strong>
                    {{ job.skills_required }}
                </p>

                <p>
                    <strong>Benefits:</strong>
                    {{ job.benefits || "Not specified" }}
                </p>

                <p>
                    <strong>Minimum CGPA:</strong>
                    {{ job.min_cgpa }}
                </p>

                <p>
                    <strong>Deadline:</strong>
                    {{ job.deadline }}
                </p>

                <p>
                    <strong>Application Limit:</strong>
                    {{ job.application_limit ?? "No limit" }}
                </p>

                <button
                    v-if="
                        job.status !== 'Rejected' &&
                        job.status !== 'Inactive'
                    "
                    @click="startEditingJob(job)"
                >
                    Edit
                </button>


                <button
                    v-if="
                        job.status === 'Active' ||
                        job.status === 'Closed'
                    "
                    @click="changeJobStatus(job)"
                >
                    {{
                        job.status === "Active"
                            ? "Close Drive"
                            : "Reopen Drive"
                    }}
                </button>

                <button @click="viewApplicants(job)">
                    View Applicants
                </button>

            </div>

        </div>
        

        <div v-if="selectedJob">

            <hr>

            <h2>
                Applicants for {{ selectedJob.title }}
            </h2>

            <button @click="closeApplicants">
                Close Applicants
            </button>

            <p v-if="applicationsLoading">
                Loading applicants...
            </p>

            <p
                v-else-if="applications.length === 0"
            >
                No students have applied yet.
            </p>


            <div
                v-for="application in applications"
                :key="application.id"
            >

                <hr>

                <h3>
                    {{ application.student.name }}
                </h3>

                <p>
                    <strong>Student ID:</strong>
                    {{ application.student.student_id }}
                </p>

                <p>
                    <strong>Department:</strong>
                    {{ application.student.department }}
                </p>

                <p>
                    <strong>CGPA:</strong>
                    {{ application.student.cgpa }}
                </p>

                <p>
                    <strong>Phone:</strong>
                    {{ application.student.phone }}
                </p>

                <p>
                    <strong>Skills:</strong>
                    {{ application.student.skills || "Not provided" }}
                </p>

                <p>
                    <strong>Education:</strong>
                    {{ application.student.education || "Not provided" }}
                </p>

                <p>
                    <strong>Applied At:</strong>
                    {{ formatUTCDateTime(application.applied_at) }}
                </p>

                <p>
                    <strong>Status:</strong>
                    {{ application.status }}
                </p>


                <button
                    v-if="application.student.resume"
                    @click="viewResume(application)"
                >
                    View Resume
                </button>



                <div
                    v-if="application.status === 'Applied'"
                >

                    <div>
                        <label>
                            Feedback
                        </label>

                        <br>

                        <textarea
                            v-model="feedback[application.id]"
                            placeholder="Enter feedback"
                        ></textarea>
                    </div>

                    <br>

                    <button
                        @click="
                            updateApplicationStatus(
                                application,
                                'Shortlisted'
                            )
                        "
                    >
                        Shortlist
                    </button>

                    <button
                        @click="
                            updateApplicationStatus(
                                application,
                                'Rejected'
                            )
                        "
                    >
                        Reject
                    </button>

                </div>



                <div
                    v-else-if="application.status === 'Shortlisted' || application.status === 'Interview'"
                >

                    <p>
                        <strong>Feedback:</strong>
                        {{ application.remarks || "None" }}
                    </p>

                    <hr>

                    <h4>Interview</h4>


                    <div
                        v-if="application.interview_datetime"
                    >

                        <p>
                            <strong>Date & Time:</strong>
                            {{ formatLocalDateTime(application.interview_datetime) }}
                        </p>

                        <p>
                            <strong>Mode:</strong>
                            {{ application.interview_mode }}
                        </p>

                        <p
                            v-if="application.interview_location"
                        >
                            <strong>Location / Link:</strong>
                            {{ application.interview_location }}
                        </p>

                        <p
                            v-if="application.interview_notes"
                        >
                            <strong>Notes:</strong>
                            {{ application.interview_notes }}
                        </p>

                        <hr>

                        <h4>Final Decision</h4>

                        <div>
                            <label>
                                Company Feedback
                            </label>

                            <br>

                            <textarea
                                v-model="feedback[application.id]"
                                placeholder="Enter feedback"
                            ></textarea>
                        </div>

                        <br>

                        <div>
                            <label>
                                Offer Letter (PDF)
                            </label>

                            <br>

                            <input
                                :key="
                                    offerLetterInputKey[application.id] || 0
                                "
                                type="file"
                                accept=".pdf,application/pdf"
                                @change="
                                    selectOfferLetter(
                                        application,
                                        $event
                                    )
                                "
                            >

                            <p
                                v-if="offerLetter[application.id]"
                            >
                                Selected:
                                {{ offerLetter[application.id].name }}
                            </p>

                            <small>
                                PDF only, maximum 5 MB.
                                Required when issuing the offer.
                            </small>
                        </div>

                        <br>

                        <button
                            @click="
                                updateFinalStatus(
                                    application,
                                    'Offer'
                                )
                            "
                        >
                            Select
                        </button>

                        <button
                            @click="
                                updateFinalStatus(
                                    application,
                                    'Rejected'
                                )
                            "
                        >
                            Reject
                        </button>

                    </div>



                    <div v-else-if="application.status === 'Shortlisted'">

                        <p>
                            No interview scheduled yet.
                        </p>

                        <div>
                            <label>
                                Interview Date & Time
                            </label>

                            <br>

                            <input
                                type="datetime-local"
                                v-model="
                                    getInterviewForm(application)
                                        .interview_datetime
                                "
                            >
                        </div>

                        <br>

                        <div>
                            <label>
                                Interview Mode
                            </label>

                            <br>

                            <select
                                v-model="
                                    getInterviewForm(application)
                                        .interview_mode
                                "
                            >
                                <option value="Online">
                                    Online
                                </option>

                                <option value="Offline">
                                    Offline
                                </option>
                            </select>
                        </div>

                        <br>

                        <div>
                            <label>
                                Location / Meeting Link
                            </label>

                            <br>

                            <input
                                type="text"
                                v-model="
                                    getInterviewForm(application)
                                        .interview_location
                                "
                            >
                        </div>

                        <br>

                        <div>
                            <label>
                                Interview Notes
                            </label>

                            <br>

                            <textarea
                                v-model="
                                    getInterviewForm(application)
                                        .interview_notes
                                "
                                placeholder="Additional interview instructions"
                            ></textarea>
                        </div>

                        <br>

                        <button
                            @click="
                                scheduleInterview(application)
                            "
                        >
                            Schedule Interview
                        </button>

                    </div>

                    <div v-else-if="application.status === 'Interview'">
                        <p>
                            <strong>Interview:</strong>
                            Scheduled
                        </p>
                    </div>

                </div>


                <div v-else>

                    <p>
                        <strong>Feedback:</strong>
                        {{ application.remarks || "None" }}
                    </p>

                    <p v-if="application.status === 'Offer'">
                        <strong>Final Result:</strong>
                        Offer Issued
                    </p>

                    <button
                        v-if="application.status === 'Offer'"
                        @click="markAsPlaced(application)"
                    >
                        Mark as Placed
                    </button>

                    <p v-else-if="application.status === 'Placed'">
                        <strong>Final Result:</strong>
                        Placed
                    </p>

                    <p v-else-if="application.status === 'Rejected'">
                        <strong>Final Result:</strong>
                        Rejected
                    </p>

                </div>

            </div>

        </div>

        <br>

        <LogoutButton />

    </div>

</template>


<style scoped>

.dashboard-actions {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

.export-button {
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    background: #198754;
    color: white;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
}

.export-button:hover {
    opacity: 0.9;
}

.export-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.export-status {
    padding: 10px 14px;
    background: #e7f1ff;
    color: #084298;
    border-radius: 6px;
    margin-bottom: 20px;
}

.report-button {
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    background: #0d6efd;
    color: white;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
}

.report-button:hover {
    opacity: 0.9;
}

.report-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.report-status {
    padding: 10px 14px;
    background: #e7f1ff;
    color: #084298;
    border-radius: 6px;
    margin-bottom: 20px;
}

</style>