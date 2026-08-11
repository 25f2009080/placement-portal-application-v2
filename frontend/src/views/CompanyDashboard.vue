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


async function fetchCompanyProfile(showError = true) {
    try {
        const response = await api.get("/api/company/profile");

        company.value = response.data.company;
        loadProfileForm();

    } catch (err) {
        console.error("Failed to load company profile:", err);

        if (showError) {
            error.value =
                err.response?.data?.message ||
                "Failed to load company profile.";
        }
    } finally {
        loading.value = false;
    }
}


async function fetchJobs(showError = true) {
    jobsLoading.value = true;

    try {
        const response = await api.get("/api/company/jobs");

        jobs.value = response.data.jobs;

    } catch (err) {
        console.error("Failed to load jobs:", err);

        if (showError) {
            error.value =
                err.response?.data?.message ||
                "Failed to load jobs.";
        }
    } finally {
        jobsLoading.value = false;
    }
}

async function viewApplicants(job, showError = true) {
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
        console.error("Failed to load applicants:", err);

        if (showError) {
            error.value =
                err.response?.data?.message ||
                "Failed to load applicants.";
        }
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update application.";
        return;
    }

    // The status update succeeded. A refresh failure must not
    // turn the successful action into a false error.
    await viewApplicants(selectedJob.value, false);
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to schedule interview.";
        return;
    }

    await viewApplicants(selectedJob.value, false);
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update final status.";
        return;
    }

    await viewApplicants(selectedJob.value, false);
}


async function markAsPlaced(application) {
    error.value = "";
    success.value = "";

    try {
        const response = await api.put(
            `/api/company/applications/${application.id}/placed`
        );

        success.value = response.data.message;

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to mark applicant as placed.";
        return;
    }

    await viewApplicants(selectedJob.value, false);
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update company profile.";
        return;
    }

    // Profile update succeeded. Refresh separately so a refresh
    // failure cannot report the successful update as failed.
    await fetchCompanyProfile(false);
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to create job.";
        return;
    }

    await fetchJobs(false);
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to update job.";
        return;
    }

    await fetchJobs(false);
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

    } catch (err) {
        error.value =
            err.response?.data?.message ||
            "Failed to change job status.";
        return;
    }

    await fetchJobs(false);
}



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

            try {
                await downloadExport();

                exportLoading.value = false;
                exportStatus.value =
                    "CSV export completed successfully.";

                success.value =
                    `Export completed. ${response.data.records || 0} records exported.`;
            } catch (err) {
                console.error("Export generated but download failed:", err);

                exportLoading.value = false;
                exportStatus.value = "";

                error.value =
                    err.response?.data?.message ||
                    "Export was generated, but the CSV could not be downloaded.";
            }

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
    <div class="bg-light min-vh-100">
        <nav class="navbar navbar-dark bg-dark shadow-sm">
            <div class="container-fluid px-3 px-md-4">
                <div>
                    <span class="navbar-brand fw-bold">
                        Placement Portal
                    </span>
                    <span class="text-white-50 d-none d-md-inline">
                        Company Dashboard
                    </span>
                </div>

                <div class="d-flex align-items-center gap-3">
                    <span class="text-white small">
                        {{ user.username }}
                        <span class="text-white-50">
                            · {{ user.role }}
                        </span>
                    </span>

                    <LogoutButton />
                </div>
            </div>
        </nav>

        <main class="container-fluid px-3 px-md-4 py-4">
            <div class="mb-4">
                <h1 class="fw-bold mb-1">
                    Company Dashboard
                </h1>

                <p class="text-muted mb-0">
                    Manage your company profile, placement drives and applicants.
                </p>
            </div>

            <div
                v-if="error"
                class="alert alert-danger alert-dismissible fade show"
                role="alert"
            >
                {{ error }}

                <button
                    type="button"
                    class="btn-close"
                    @click="error = ''"
                ></button>
            </div>

            <div
                v-if="success"
                class="alert alert-success alert-dismissible fade show"
                role="alert"
            >
                {{ success }}

                <button
                    type="button"
                    class="btn-close"
                    @click="success = ''"
                ></button>
            </div>

            <section class="mb-4">
                <div class="card border-0 shadow-sm">
                    <div
                        class="card-header bg-white border-0 p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3"
                    >
                        <div>
                            <h2 class="h5 fw-bold mb-1">
                                Company Profile
                            </h2>

                            <p class="text-muted small mb-0">
                                Your registered company information
                            </p>
                        </div>

                        <button
                            v-if="company && !loading && !editing"
                            class="btn btn-outline-primary"
                            @click="startEditing"
                        >
                            Edit Profile
                        </button>
                    </div>

                    <div class="card-body p-4">
                        <div
                            v-if="loading"
                            class="text-center py-5"
                        >
                            <div
                                class="spinner-border text-primary mb-3"
                                role="status"
                            ></div>

                            <p class="text-muted mb-0">
                                Loading company profile...
                            </p>
                        </div>

                        <div
                            v-else-if="company && !editing"
                            class="row g-4"
                        >
                            <div class="col-12 col-md-6 col-xl-4">
                                <div class="profile-item">
                                    <div class="text-muted small">
                                        Company ID
                                    </div>

                                    <div class="fw-semibold">
                                        {{ company.company_id }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 col-md-6 col-xl-4">
                                <div class="profile-item">
                                    <div class="text-muted small">
                                        Company Name
                                    </div>

                                    <div class="fw-semibold">
                                        {{ company.name }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 col-md-6 col-xl-4">
                                <div class="profile-item">
                                    <div class="text-muted small">
                                        Industry
                                    </div>

                                    <div class="fw-semibold">
                                        {{ company.industry }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 col-md-6 col-xl-4">
                                <div class="profile-item">
                                    <div class="text-muted small">
                                        Location
                                    </div>

                                    <div class="fw-semibold">
                                        {{ company.location }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 col-md-6 col-xl-4">
                                <div class="profile-item">
                                    <div class="text-muted small">
                                        Website
                                    </div>

                                    <div class="fw-semibold text-break">
                                        {{ company.website || "Not provided" }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 col-md-6 col-xl-4">
                                <div class="profile-item">
                                    <div class="text-muted small">
                                        HR Contact
                                    </div>

                                    <div class="fw-semibold">
                                        {{ company.hr_name }}
                                    </div>

                                    <div class="small text-muted text-break">
                                        {{ company.hr_email }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="profile-item">
                                    <div class="text-muted small mb-1">
                                        Description
                                    </div>

                                    <div>
                                        {{ company.description || "Not provided" }}
                                    </div>
                                </div>
                            </div>

                            <div class="col-12 col-md-6">
                                <div
                                    class="profile-item d-flex justify-content-between align-items-center"
                                >
                                    <span class="text-muted small">
                                        Approval Status
                                    </span>

                                    <span
                                        class="badge"
                                        :class="
                                            company.approved
                                                ? 'text-bg-success'
                                                : 'text-bg-warning'
                                        "
                                    >
                                        {{
                                            company.approved
                                                ? "Approved"
                                                : "Pending"
                                        }}
                                    </span>
                                </div>
                            </div>

                            <div class="col-12 col-md-6">
                                <div
                                    class="profile-item d-flex justify-content-between align-items-center"
                                >
                                    <span class="text-muted small">
                                        Account Status
                                    </span>

                                    <span
                                        class="badge"
                                        :class="
                                            company.is_active
                                                ? 'text-bg-success'
                                                : 'text-bg-secondary'
                                        "
                                    >
                                        {{
                                            company.is_active
                                                ? "Active"
                                                : "Inactive"
                                        }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <form
                            v-else-if="company && editing"
                            @submit.prevent="updateCompanyProfile"
                        >
                            <div class="row g-3">
                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Company Name
                                    </label>

                                    <input
                                        v-model="form.name"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Industry
                                    </label>

                                    <input
                                        v-model="form.industry"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Location
                                    </label>

                                    <input
                                        v-model="form.location"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Website
                                    </label>

                                    <input
                                        v-model="form.website"
                                        type="text"
                                        class="form-control"
                                    >
                                </div>

                                <div class="col-12">
                                    <label class="form-label fw-semibold">
                                        Description
                                    </label>

                                    <textarea
                                        v-model="form.description"
                                        class="form-control"
                                        rows="4"
                                    ></textarea>
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        HR Name
                                    </label>

                                    <input
                                        v-model="form.hr_name"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        HR Email
                                    </label>

                                    <input
                                        v-model="form.hr_email"
                                        type="email"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 d-flex gap-2 pt-2">
                                    <button
                                        type="submit"
                                        class="btn btn-primary"
                                    >
                                        Save Changes
                                    </button>

                                    <button
                                        type="button"
                                        class="btn btn-outline-secondary"
                                        @click="cancelEditing"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </section>

            <section>
                <div
                    class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-3 mb-3"
                >
                    <div>
                        <h2 class="h4 fw-bold mb-1">
                            Placement Drives
                        </h2>

                        <p class="text-muted mb-0">
                            Create and manage your recruitment drives.
                        </p>
                    </div>

                    <div class="d-flex flex-wrap gap-2">
                        <button
                            v-if="!creatingJob"
                            class="btn btn-primary"
                            @click="startCreatingJob"
                        >
                            Create Placement Drive
                        </button>

                        <button
                            class="btn btn-success"
                            @click="startExport"
                            :disabled="exportLoading"
                        >
                            <span
                                v-if="exportLoading"
                                class="spinner-border spinner-border-sm me-2"
                            ></span>

                            {{
                                exportLoading
                                    ? "Exporting..."
                                    : "Export Application History"
                            }}
                        </button>

                        <button
                            class="btn btn-outline-primary"
                            @click="startPlacementReport"
                            :disabled="reportLoading"
                        >
                            <span
                                v-if="reportLoading"
                                class="spinner-border spinner-border-sm me-2"
                            ></span>

                            {{
                                reportLoading
                                    ? "Generating..."
                                    : "Generate Placement Report"
                            }}
                        </button>
                    </div>
                </div>

                <div
                    v-if="exportStatus"
                    class="alert alert-info"
                >
                    {{ exportStatus }}
                </div>

                <div
                    v-if="reportStatus"
                    class="alert alert-info"
                >
                    {{ reportStatus }}
                </div>

                <div
                    v-if="creatingJob"
                    class="card border-0 shadow-sm mb-4"
                >
                    <div class="card-header bg-white border-0 p-4">
                        <h3 class="h5 fw-bold mb-1">
                            {{
                                editingJob
                                    ? "Edit Placement Drive"
                                    : "Create Placement Drive"
                            }}
                        </h3>

                        <p class="text-muted small mb-0">
                            {{
                                editingJob
                                    ? "Update the details of this placement drive."
                                    : "Add a new placement opportunity for students."
                            }}
                        </p>
                    </div>

                    <div class="card-body p-4">
                        <form
                            @submit.prevent="
                                editingJob
                                    ? updateJob()
                                    : createJob()
                            "
                        >
                            <div class="row g-3">
                                <div class="col-12 col-lg-6">
                                    <label class="form-label fw-semibold">
                                        Job Title
                                    </label>

                                    <input
                                        v-model="jobForm.title"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-lg-6">
                                    <label class="form-label fw-semibold">
                                        Location
                                    </label>

                                    <input
                                        v-model="jobForm.location"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12">
                                    <label class="form-label fw-semibold">
                                        Description
                                    </label>

                                    <textarea
                                        v-model="jobForm.description"
                                        class="form-control"
                                        rows="4"
                                        required
                                    ></textarea>
                                </div>

                                <div class="col-12 col-md-6 col-xl-3">
                                    <label class="form-label fw-semibold">
                                        Salary
                                    </label>

                                    <input
                                        v-model="jobForm.salary"
                                        type="number"
                                        min="0"
                                        step="0.01"
                                        class="form-control"
                                    >
                                </div>

                                <div class="col-12 col-md-6 col-xl-3">
                                    <label class="form-label fw-semibold">
                                        Experience
                                    </label>

                                    <input
                                        v-model="jobForm.experience"
                                        type="text"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-md-6 col-xl-3">
                                    <label class="form-label fw-semibold">
                                        Minimum CGPA
                                    </label>

                                    <input
                                        v-model="jobForm.min_cgpa"
                                        type="number"
                                        min="0"
                                        max="10"
                                        step="0.01"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 col-md-6 col-xl-3">
                                    <label class="form-label fw-semibold">
                                        Application Limit
                                    </label>

                                    <input
                                        v-model="jobForm.application_limit"
                                        type="number"
                                        min="1"
                                        class="form-control"
                                    >
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Required Skills
                                    </label>

                                    <textarea
                                        v-model="jobForm.skills_required"
                                        class="form-control"
                                        rows="3"
                                        required
                                    ></textarea>
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Benefits
                                    </label>

                                    <textarea
                                        v-model="jobForm.benefits"
                                        class="form-control"
                                        rows="3"
                                    ></textarea>
                                </div>

                                <div class="col-12 col-md-6">
                                    <label class="form-label fw-semibold">
                                        Application Deadline
                                    </label>

                                    <input
                                        v-model="jobForm.deadline"
                                        type="date"
                                        class="form-control"
                                        required
                                    >
                                </div>

                                <div class="col-12 d-flex gap-2 pt-2">
                                    <button
                                        type="submit"
                                        class="btn btn-primary"
                                    >
                                        {{
                                            editingJob
                                                ? "Save Changes"
                                                : "Create Drive"
                                        }}
                                    </button>

                                    <button
                                        type="button"
                                        class="btn btn-outline-secondary"
                                        @click="cancelJobForm"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <div
                    v-if="jobsLoading"
                    class="card border-0 shadow-sm"
                >
                    <div class="card-body text-center py-5">
                        <div
                            class="spinner-border text-primary mb-3"
                            role="status"
                        ></div>

                        <p class="text-muted mb-0">
                            Loading placement drives...
                        </p>
                    </div>
                </div>

                <div
                    v-else-if="jobs.length === 0"
                    class="card border-0 shadow-sm"
                >
                    <div class="card-body text-center py-5">
                        <h3 class="h5 fw-semibold">
                            No placement drives found
                        </h3>

                        <p class="text-muted mb-3">
                            Create your first placement drive to start receiving applications.
                        </p>

                        <button
                            class="btn btn-primary"
                            @click="startCreatingJob"
                        >
                            Create Placement Drive
                        </button>
                    </div>
                </div>

                <div
                    v-else
                    class="row g-4"
                >
                    <div
                        v-for="job in jobs"
                        :key="job.id"
                        class="col-12 col-xl-6"
                    >
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-body p-4">
                                <div
                                    class="d-flex justify-content-between align-items-start gap-3 mb-3"
                                >
                                    <div>
                                        <h3 class="h5 fw-bold mb-1">
                                            {{ job.title }}
                                        </h3>

                                        <p class="text-muted small mb-0">
                                            {{ job.location }}
                                        </p>
                                    </div>

                                    <span
                                        class="badge"
                                        :class="{
                                            'text-bg-success':
                                                job.status === 'Active',
                                            'text-bg-secondary':
                                                job.status === 'Closed',
                                            'text-bg-danger':
                                                job.status === 'Rejected',
                                            'text-bg-warning':
                                                job.status === 'Pending',
                                            'text-bg-dark':
                                                job.status === 'Inactive'
                                        }"
                                    >
                                        {{ job.status }}
                                    </span>
                                </div>

                                <div class="row g-3 small mb-4">
                                    <div class="col-6">
                                        <div class="text-muted">
                                            Salary
                                        </div>

                                        <div class="fw-semibold">
                                            {{ job.salary ?? "Not specified" }}
                                        </div>
                                    </div>

                                    <div class="col-6">
                                        <div class="text-muted">
                                            Experience
                                        </div>

                                        <div class="fw-semibold">
                                            {{ job.experience }}
                                        </div>
                                    </div>

                                    <div class="col-6">
                                        <div class="text-muted">
                                            Minimum CGPA
                                        </div>

                                        <div class="fw-semibold">
                                            {{ job.min_cgpa }}
                                        </div>
                                    </div>

                                    <div class="col-6">
                                        <div class="text-muted">
                                            Application Limit
                                        </div>

                                        <div class="fw-semibold">
                                            {{
                                                job.application_limit ??
                                                "No limit"
                                            }}
                                        </div>
                                    </div>

                                    <div class="col-12">
                                        <div class="text-muted">
                                            Deadline
                                        </div>

                                        <div class="fw-semibold">
                                            {{ job.deadline }}
                                        </div>
                                    </div>

                                    <div class="col-12">
                                        <div class="text-muted">
                                            Required Skills
                                        </div>

                                        <div class="fw-semibold text-break">
                                            {{ job.skills_required }}
                                        </div>
                                    </div>

                                    <div class="col-12">
                                        <div class="text-muted">
                                            Benefits
                                        </div>

                                        <div class="fw-semibold text-break">
                                            {{ job.benefits || "Not specified" }}
                                        </div>
                                    </div>
                                </div>

                                <div class="d-flex flex-wrap gap-2">
                                    <button
                                        v-if="
                                            job.status !== 'Rejected' &&
                                            job.status !== 'Inactive'
                                        "
                                        class="btn btn-outline-primary btn-sm"
                                        @click="startEditingJob(job)"
                                    >
                                        Edit
                                    </button>

                                    <button
                                        v-if="
                                            job.status === 'Active' ||
                                            job.status === 'Closed'
                                        "
                                        class="btn btn-outline-secondary btn-sm"
                                        @click="changeJobStatus(job)"
                                    >
                                        {{
                                            job.status === "Active"
                                                ? "Close Drive"
                                                : "Reopen Drive"
                                        }}
                                    </button>

                                    <button
                                        class="btn btn-primary btn-sm"
                                        @click="viewApplicants(job)"
                                    >
                                        View Applicants
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section
                v-if="selectedJob"
                class="mt-5"
            >
                <div class="card border-0 shadow-sm">
                    <div
                        class="card-header bg-dark text-white p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3"
                    >
                        <div>
                            <h2 class="h5 fw-bold mb-1">
                                Applicants
                            </h2>

                            <p class="small text-white-50 mb-0">
                                {{ selectedJob.title }}
                            </p>
                        </div>

                        <button
                            class="btn btn-outline-light btn-sm"
                            @click="closeApplicants"
                        >
                            Close
                        </button>
                    </div>

                    <div class="card-body p-4">
                        <div
                            v-if="applicationsLoading"
                            class="text-center py-5"
                        >
                            <div
                                class="spinner-border text-primary mb-3"
                                role="status"
                            ></div>

                            <p class="text-muted mb-0">
                                Loading applicants...
                            </p>
                        </div>

                        <div
                            v-else-if="applications.length === 0"
                            class="text-center py-5"
                        >
                            <h3 class="h5 fw-semibold">
                                No students have applied yet.
                            </h3>

                            <p class="text-muted mb-0">
                                Applications will appear here once students apply.
                            </p>
                        </div>

                        <div
                            v-else
                            class="row g-4"
                        >
                            <div
                                v-for="application in applications"
                                :key="application.id"
                                class="col-12"
                            >
                                <div class="card border">
                                    <div class="card-body p-4">
                                        <div
                                            class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4"
                                        >
                                            <div>
                                                <h3 class="h5 fw-bold mb-1">
                                                    {{ application.student.name }}
                                                </h3>

                                                <p class="text-muted mb-0">
                                                    {{ application.student.student_id }}
                                                    <span class="mx-1">·</span>
                                                    {{ application.student.department }}
                                                </p>
                                            </div>

                                            <span
                                                class="badge align-self-start"
                                                :class="{
                                                    'text-bg-primary':
                                                        application.status === 'Applied',
                                                    'text-bg-warning':
                                                        application.status === 'Shortlisted',
                                                    'text-bg-info':
                                                        application.status === 'Interview',
                                                    'text-bg-success':
                                                        application.status === 'Offer' ||
                                                        application.status === 'Placed',
                                                    'text-bg-danger':
                                                        application.status === 'Rejected'
                                                }"
                                            >
                                                {{ application.status }}
                                            </span>
                                        </div>

                                        <div class="row g-3 small mb-4">
                                            <div class="col-6 col-md-3">
                                                <div class="text-muted">
                                                    CGPA
                                                </div>

                                                <div class="fw-semibold">
                                                    {{ application.student.cgpa }}
                                                </div>
                                            </div>

                                            <div class="col-6 col-md-3">
                                                <div class="text-muted">
                                                    Phone
                                                </div>

                                                <div class="fw-semibold">
                                                    {{ application.student.phone }}
                                                </div>
                                            </div>

                                            <div class="col-12 col-md-6">
                                                <div class="text-muted">
                                                    Applied At
                                                </div>

                                                <div class="fw-semibold">
                                                    {{ formatUTCDateTime(application.applied_at) }}
                                                </div>
                                            </div>

                                            <div class="col-12 col-md-6">
                                                <div class="text-muted">
                                                    Skills
                                                </div>

                                                <div class="fw-semibold text-break">
                                                    {{
                                                        application.student.skills ||
                                                        "Not provided"
                                                    }}
                                                </div>
                                            </div>

                                            <div class="col-12 col-md-6">
                                                <div class="text-muted">
                                                    Education
                                                </div>

                                                <div class="fw-semibold text-break">
                                                    {{
                                                        application.student.education ||
                                                        "Not provided"
                                                    }}
                                                </div>
                                            </div>
                                        </div>

                                        <div class="mb-4">
                                            <button
                                                v-if="application.student.resume"
                                                class="btn btn-outline-primary btn-sm"
                                                @click="viewResume(application)"
                                            >
                                                View Resume
                                            </button>
                                        </div>

                                        <div
                                            v-if="application.status === 'Applied'"
                                            class="border-top pt-4"
                                        >
                                            <h4 class="h6 fw-bold">
                                                Application Review
                                            </h4>

                                            <label class="form-label small fw-semibold">
                                                Feedback
                                            </label>

                                            <textarea
                                                v-model="feedback[application.id]"
                                                class="form-control mb-3"
                                                rows="3"
                                                placeholder="Enter feedback"
                                            ></textarea>

                                            <div class="d-flex flex-wrap gap-2">
                                                <button
                                                    class="btn btn-success"
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
                                                    class="btn btn-outline-danger"
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
                                        </div>

                                        <div
                                            v-else-if="
                                                application.status === 'Shortlisted' ||
                                                application.status === 'Interview'
                                            "
                                            class="border-top pt-4"
                                        >
                                            <div class="mb-4">
                                                <div class="text-muted small">
                                                    Feedback
                                                </div>

                                                <div>
                                                    {{
                                                        application.remarks ||
                                                        "None"
                                                    }}
                                                </div>
                                            </div>

                                            <div
                                                v-if="
                                                    application.interview_datetime
                                                "
                                            >
                                                <h4 class="h6 fw-bold mb-3">
                                                    Interview Details
                                                </h4>

                                                <div class="row g-3 small mb-4">
                                                    <div class="col-12 col-md-4">
                                                        <div class="text-muted">
                                                            Date & Time
                                                        </div>

                                                        <div class="fw-semibold">
                                                            {{
                                                                formatLocalDateTime(
                                                                    application.interview_datetime
                                                                )
                                                            }}
                                                        </div>
                                                    </div>

                                                    <div class="col-12 col-md-4">
                                                        <div class="text-muted">
                                                            Mode
                                                        </div>

                                                        <div class="fw-semibold">
                                                            {{
                                                                application.interview_mode
                                                            }}
                                                        </div>
                                                    </div>

                                                    <div
                                                        v-if="
                                                            application.interview_location
                                                        "
                                                        class="col-12 col-md-4"
                                                    >
                                                        <div class="text-muted">
                                                            Location / Link
                                                        </div>

                                                        <div class="fw-semibold text-break">
                                                            {{
                                                                application.interview_location
                                                            }}
                                                        </div>
                                                    </div>

                                                    <div
                                                        v-if="
                                                            application.interview_notes
                                                        "
                                                        class="col-12"
                                                    >
                                                        <div class="text-muted">
                                                            Notes
                                                        </div>

                                                        <div class="fw-semibold">
                                                            {{
                                                                application.interview_notes
                                                            }}
                                                        </div>
                                                    </div>
                                                </div>

                                                <div
                                                    v-if="
                                                        application.status ===
                                                        'Interview'
                                                    "
                                                    class="alert alert-info"
                                                >
                                                    Interview scheduled.
                                                </div>

                                                <div class="border-top pt-4">
                                                    <h4 class="h6 fw-bold mb-3">
                                                        Final Decision
                                                    </h4>

                                                    <label class="form-label small fw-semibold">
                                                        Company Feedback
                                                    </label>

                                                    <textarea
                                                        v-model="
                                                            feedback[
                                                                application.id
                                                            ]
                                                        "
                                                        class="form-control mb-3"
                                                        rows="3"
                                                        placeholder="Enter feedback"
                                                    ></textarea>

                                                    <label class="form-label small fw-semibold">
                                                        Offer Letter (PDF)
                                                    </label>

                                                    <input
                                                        :key="
                                                            offerLetterInputKey[
                                                                application.id
                                                            ] || 0
                                                        "
                                                        type="file"
                                                        accept=".pdf,application/pdf"
                                                        class="form-control mb-2"
                                                        @change="
                                                            selectOfferLetter(
                                                                application,
                                                                $event
                                                            )
                                                        "
                                                    >

                                                    <div
                                                        v-if="
                                                            offerLetter[
                                                                application.id
                                                            ]
                                                        "
                                                        class="small text-success mb-2"
                                                    >
                                                        Selected:
                                                        {{
                                                            offerLetter[
                                                                application.id
                                                            ].name
                                                        }}
                                                    </div>

                                                    <div class="form-text mb-3">
                                                        PDF only, maximum 5 MB.
                                                        Required when issuing the offer.
                                                    </div>

                                                    <div class="d-flex flex-wrap gap-2">
                                                        <button
                                                            class="btn btn-success"
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
                                                            class="btn btn-outline-danger"
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
                                                </div>
                                            </div>

                                            <div
                                                v-else-if="
                                                    application.status ===
                                                    'Shortlisted'
                                                "
                                            >
                                                <div
                                                    class="alert alert-warning mb-4"
                                                >
                                                    No interview scheduled yet.
                                                </div>

                                                <h4 class="h6 fw-bold mb-3">
                                                    Schedule Interview
                                                </h4>

                                                <div class="row g-3">
                                                    <div class="col-12 col-md-6">
                                                        <label class="form-label small fw-semibold">
                                                            Interview Date & Time
                                                        </label>

                                                        <input
                                                            type="datetime-local"
                                                            class="form-control"
                                                            v-model="
                                                                getInterviewForm(
                                                                    application
                                                                ).interview_datetime
                                                            "
                                                        >
                                                    </div>

                                                    <div class="col-12 col-md-6">
                                                        <label class="form-label small fw-semibold">
                                                            Interview Mode
                                                        </label>

                                                        <select
                                                            class="form-select"
                                                            v-model="
                                                                getInterviewForm(
                                                                    application
                                                                ).interview_mode
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

                                                    <div class="col-12">
                                                        <label class="form-label small fw-semibold">
                                                            Location / Meeting Link
                                                        </label>

                                                        <input
                                                            type="text"
                                                            class="form-control"
                                                            v-model="
                                                                getInterviewForm(
                                                                    application
                                                                ).interview_location
                                                            "
                                                        >
                                                    </div>

                                                    <div class="col-12">
                                                        <label class="form-label small fw-semibold">
                                                            Interview Notes
                                                        </label>

                                                        <textarea
                                                            class="form-control"
                                                            rows="3"
                                                            v-model="
                                                                getInterviewForm(
                                                                    application
                                                                ).interview_notes
                                                            "
                                                            placeholder="Additional interview instructions"
                                                        ></textarea>
                                                    </div>

                                                    <div class="col-12">
                                                        <button
                                                            class="btn btn-primary"
                                                            @click="
                                                                scheduleInterview(
                                                                    application
                                                                )
                                                            "
                                                        >
                                                            Schedule Interview
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div
                                            v-else
                                            class="border-top pt-4"
                                        >
                                            <div class="mb-3">
                                                <div class="text-muted small">
                                                    Feedback
                                                </div>

                                                <div>
                                                    {{
                                                        application.remarks ||
                                                        "None"
                                                    }}
                                                </div>
                                            </div>

                                            <div
                                                v-if="
                                                    application.status ===
                                                    'Offer'
                                                "
                                                class="d-flex flex-column gap-3"
                                            >
                                                <div
                                                    class="alert alert-success mb-0"
                                                >
                                                    Offer issued.
                                                </div>

                                                <button
                                                    class="btn btn-success align-self-start"
                                                    @click="
                                                        markAsPlaced(
                                                            application
                                                        )
                                                    "
                                                >
                                                    Mark as Placed
                                                </button>
                                            </div>

                                            <div
                                                v-else-if="
                                                    application.status ===
                                                    'Placed'
                                                "
                                                class="alert alert-success mb-0"
                                            >
                                                Final Result: Placed
                                            </div>

                                            <div
                                                v-else-if="
                                                    application.status ===
                                                    'Rejected'
                                                "
                                                class="alert alert-danger mb-0"
                                            >
                                                Final Result: Rejected
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<style scoped>
.profile-item {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.75rem;
    padding: 1rem;
    height: 100%;
}

.card {
    border-radius: 0.9rem;
}

.form-control,
.form-select {
    border-radius: 0.6rem;
}

.btn {
    border-radius: 0.55rem;
}

.badge {
    font-weight: 600;
}

@media (max-width: 767.98px) {
    main {
        overflow-x: hidden;
    }
}
</style>