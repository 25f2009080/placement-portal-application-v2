<script setup>
import { ref, onMounted } from "vue";
import LogoutButton from "../components/LogoutButton.vue";
import api from "../services/api";

const student = ref(null);
const jobs = ref([]);
const applications = ref([]);

const loading = ref(true);
const jobsLoading = ref(false);
const applicationsLoading = ref(false);
const saving = ref(false);

const errorMessage = ref("");
const successMessage = ref("");

const isEditing = ref(false);

const search = ref("");
const applyingJobId = ref(null);

const resumeFile = ref(null);
const resumeUploading = ref(false);
const resumeInput = ref(null);

const exportLoading = ref(false);
const exportStatus = ref("");
const exportTaskId = ref(null);
let exportPollTimer = null;

const editForm = ref({
    name: "",
    department: "",
    phone: "",
    cgpa: "",
    skills: "",
    education: "",
    experience: ""
});

const loadProfile = async () => {
    loading.value = true;
    errorMessage.value = "";

    try {
        const response = await api.get("/api/student/profile");

        student.value = response.data.student;

        editForm.value = {
            name: student.value.name || "",
            department: student.value.department || "",
            phone: student.value.phone || "",
            cgpa: student.value.cgpa ?? "",
            skills: student.value.skills || "",
            education: student.value.education || "",
            experience: student.value.experience || ""
        };
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load student profile.";
    } finally {
        loading.value = false;
    }
};

const loadJobs = async () => {
    jobsLoading.value = true;
    errorMessage.value = "";

    try {
        const params = {};

        if (search.value.trim()) {
            params.search = search.value.trim();
        }

        const response = await api.get(
            "/api/student/jobs",
            { params }
        );

        jobs.value = response.data.jobs;
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load jobs.";
    } finally {
        jobsLoading.value = false;
    }
};

const loadApplications = async () => {
    applicationsLoading.value = true;
    errorMessage.value = "";

    try {
        const response = await api.get(
            "/api/student/applications"
        );

        applications.value = response.data.applications;
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load applications.";
    } finally {
        applicationsLoading.value = false;
    }
};

const applyForJob = async (job) => {
    if (!job.can_apply) {
        return;
    }

    applyingJobId.value = job.id;
    errorMessage.value = "";
    successMessage.value = "";

    try {
        const response = await api.post(
            `/api/student/jobs/${job.id}/apply`
        );

        successMessage.value =
            response.data.message ||
            "Application submitted successfully.";

        await loadJobs();
        await loadApplications();
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to submit application.";
    } finally {
        applyingJobId.value = null;
    }
};

const selectResume = (event) => {
    const file = event.target.files[0];

    if (!file) {
        resumeFile.value = null;
        return;
    }

    const allowedExtensions = ["pdf", "doc", "docx"];

    const extension = file.name
        .split(".")
        .pop()
        .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        errorMessage.value =
            "Only PDF, DOC and DOCX files are allowed.";

        event.target.value = "";
        resumeFile.value = null;
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        errorMessage.value =
            "Resume must be smaller than 5 MB.";

        event.target.value = "";
        resumeFile.value = null;
        return;
    }

    errorMessage.value = "";
    resumeFile.value = file;
};

const uploadResume = async () => {
    if (!resumeFile.value) {
        errorMessage.value =
            "Please select a resume first.";
        return;
    }

    resumeUploading.value = true;
    errorMessage.value = "";
    successMessage.value = "";

    const formData = new FormData();

    formData.append(
        "resume",
        resumeFile.value
    );

    try {
        const response = await api.post(
            "/api/student/profile/resume",
            formData
        );

        successMessage.value =
            response.data.message ||
            "Resume uploaded successfully.";

        resumeFile.value = null;

        if (resumeInput.value) {
            resumeInput.value.value = "";
        }

        await loadProfile();
    } catch (error) {
        if (error.response?.status === 413) {
            errorMessage.value =
                "Resume is too large. Maximum size is 5 MB.";
        } else {
            errorMessage.value =
                error.response?.data?.message ||
                "Failed to upload resume.";
        }
    } finally {
        resumeUploading.value = false;
    }
};

const viewResume = async () => {
    errorMessage.value = "";

    try {
        const response = await api.get(
            "/api/student/profile/resume",
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
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to open resume.";
    }
};

const viewOfferLetter = async (application) => {
    errorMessage.value = "";

    try {
        const response = await api.get(
            `/api/student/applications/${application.id}/offer-letter`,
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
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to open offer letter.";
    }
};

const clearSearch = () => {
    search.value = "";

    loadJobs();
};

const startEditing = () => {
    successMessage.value = "";
    errorMessage.value = "";

    editForm.value = {
        name: student.value.name || "",
        department: student.value.department || "",
        phone: student.value.phone || "",
        cgpa: student.value.cgpa ?? "",
        skills: student.value.skills || "",
        education: student.value.education || "",
        experience: student.value.experience || ""
    };

    isEditing.value = true;
};

const cancelEditing = () => {
    isEditing.value = false;
    errorMessage.value = "";
};

const saveProfile = async () => {
    saving.value = true;
    errorMessage.value = "";
    successMessage.value = "";

    try {
        const response = await api.put(
            "/api/student/profile",
            {
                name: editForm.value.name,
                department: editForm.value.department,
                phone: editForm.value.phone,
                cgpa: editForm.value.cgpa,
                skills: editForm.value.skills,
                education: editForm.value.education,
                experience: editForm.value.experience
            }
        );

        student.value = response.data.student;

        editForm.value = {
            name: student.value.name || "",
            department: student.value.department || "",
            phone: student.value.phone || "",
            cgpa: student.value.cgpa ?? "",
            skills: student.value.skills || "",
            education: student.value.education || "",
            experience: student.value.experience || ""
        };

        isEditing.value = false;
        successMessage.value = "Profile updated successfully.";
    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to update profile.";
    } finally {
        saving.value = false;
    }
};

const getStatusClass = (status) => {
    switch (status) {
        case "Applied":
            return "text-bg-info";
        case "Shortlisted":
            return "text-bg-warning";
        case "Interview":
            return "text-bg-primary";
        case "Offer":
            return "text-bg-success";
        case "Placed":
            return "text-bg-success";
        case "Rejected":
            return "text-bg-danger";
        default:
            return "text-bg-secondary";
    }
};

const formatUTCDateTime = (value) => {
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
};

const formatLocalDateTime = (value) => {
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
};

const startExport = async () => {
    exportLoading.value = true;
    exportStatus.value = "Starting export...";
    errorMessage.value = "";
    successMessage.value = "";

    try {
        const response = await api.post(
            "/api/student/export-history"
        );

        exportTaskId.value = response.data.task_id;

        exportStatus.value =
            "Export started. Preparing your CSV...";

        pollExportStatus();
    } catch (error) {
        exportLoading.value = false;
        exportStatus.value = "";

        errorMessage.value =
            error.response?.data?.message ||
            "Failed to start CSV export.";
    }
};

const pollExportStatus = () => {
    if (exportPollTimer) {
        clearTimeout(exportPollTimer);
    }

    exportPollTimer = setTimeout(
        checkExportStatus,
        1000
    );
};

const checkExportStatus = async () => {
    if (!exportTaskId.value) {
        return;
    }

    try {
        const response = await api.get(
            `/api/student/export-history/status/${exportTaskId.value}`
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

            successMessage.value =
                `Export completed. ${response.data.records || 0} records exported.`;

            return;
        }

        exportLoading.value = false;
        exportStatus.value = "";

        errorMessage.value =
            response.data.message ||
            "CSV export failed.";
    } catch (error) {
        exportLoading.value = false;
        exportStatus.value = "";

        errorMessage.value =
            error.response?.data?.message ||
            "Failed to check export status.";
    }
};

const downloadExport = async () => {
    const response = await api.get(
        `/api/student/export-history/download/${exportTaskId.value}`,
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
        link.download = "application_history.csv";
    }

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
};

onMounted(async () => {
    await loadProfile();
    await loadJobs();
    await loadApplications();
});
</script>

<template>
    <div class="bg-light min-vh-100">

        <nav class="navbar navbar-dark bg-primary shadow-sm">
            <div class="container-fluid px-3 px-md-5">

                <div>
                    <span class="navbar-brand fw-bold mb-0">
                        Placement Portal
                    </span>

                    <div
                        v-if="student"
                        class="text-white-50 small"
                    >
                        Student Dashboard
                    </div>
                </div>

                <LogoutButton />

            </div>
        </nav>

        <main class="container-fluid px-3 px-md-5 py-4">

            <div
                v-if="errorMessage"
                class="alert alert-danger alert-dismissible"
                role="alert"
            >
                {{ errorMessage }}
            </div>

            <div
                v-if="successMessage"
                class="alert alert-success"
                role="alert"
            >
                {{ successMessage }}
            </div>

            <div
                v-if="loading"
                class="card border-0 shadow-sm"
            >
                <div class="card-body text-center py-5">
                    <div
                        class="spinner-border text-primary mb-3"
                        role="status"
                    ></div>
                    <p class="mb-0 text-muted">
                        Loading profile...
                    </p>
                </div>
            </div>

            <div v-else>

                <div
                    v-if="student && !isEditing"
                    class="card border-0 shadow-sm mb-4"
                >

                    <div class="card-header bg-white border-0 pt-4 px-4">

                        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">

                            <div>
                                <h2 class="h4 fw-bold mb-1">
                                    My Profile
                                </h2>

                                <p class="text-muted mb-0">
                                    View and manage your placement profile
                                </p>
                            </div>

                            <button
                                class="btn btn-primary"
                                @click="startEditing"
                            >
                                Edit Profile
                            </button>

                        </div>

                    </div>

                    <div class="card-body p-4">

                        <div class="row g-3">

                            <div class="col-md-6">
                                <div class="profile-card">
                                    <small class="text-muted d-block">
                                        Student ID
                                    </small>
                                    <strong>
                                        {{ student.student_id || "-" }}
                                    </strong>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="profile-card">
                                    <small class="text-muted d-block">
                                        Name
                                    </small>
                                    <strong>
                                        {{ student.name || "-" }}
                                    </strong>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="profile-card">
                                    <small class="text-muted d-block">
                                        Department
                                    </small>
                                    <strong>
                                        {{ student.department || "-" }}
                                    </strong>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="profile-card">
                                    <small class="text-muted d-block">
                                        Email
                                    </small>
                                    <strong>
                                        {{ student.email || "-" }}
                                    </strong>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="profile-card">
                                    <small class="text-muted d-block">
                                        Phone
                                    </small>
                                    <strong>
                                        {{ student.phone || "-" }}
                                    </strong>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="profile-card">
                                    <small class="text-muted d-block">
                                        CGPA
                                    </small>
                                    <strong>
                                        {{ student.cgpa ?? "-" }}
                                    </strong>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="profile-card">
                                    <small class="text-muted d-block mb-1">
                                        Skills
                                    </small>
                                    <p class="mb-0 text-break">
                                        {{ student.skills || "-" }}
                                    </p>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="profile-card">
                                    <small class="text-muted d-block mb-1">
                                        Education
                                    </small>
                                    <p class="mb-0 text-break">
                                        {{ student.education || "-" }}
                                    </p>
                                </div>
                            </div>

                            <div class="col-12">
                                <div class="profile-card">
                                    <small class="text-muted d-block mb-1">
                                        Experience
                                    </small>
                                    <p class="mb-0 text-break">
                                        {{ student.experience || "No experience needed" }}
                                    </p>
                                </div>
                            </div>

                            <div class="col-12">

                                <div class="profile-card">

                                    <small class="text-muted d-block mb-2">
                                        Resume
                                    </small>

                                    <div
                                        v-if="student.resume"
                                        class="alert alert-success d-flex justify-content-between align-items-center flex-wrap gap-2 mb-0"
                                    >
                                        <span>
                                            <i class="bi bi-file-earmark-check me-2"></i>
                                            Resume uploaded
                                        </span>

                                        <button
                                            type="button"
                                            class="btn btn-sm btn-outline-success"
                                            @click="viewResume"
                                        >
                                            View Resume
                                        </button>
                                    </div>

                                    <div
                                        v-else
                                        class="alert alert-warning mb-0"
                                    >
                                        No resume uploaded
                                    </div>

                                    <div class="mt-3 pt-3 border-top">

                                        <input
                                            ref="resumeInput"
                                            type="file"
                                            class="form-control"
                                            accept=".pdf,.doc,.docx"
                                            @change="selectResume"
                                        />

                                        <div
                                            v-if="resumeFile"
                                            class="small text-muted mt-2"
                                        >
                                            Selected:
                                            {{ resumeFile.name }}
                                        </div>

                                        <div class="d-flex align-items-center gap-3 mt-3 flex-wrap">

                                            <button
                                                type="button"
                                                class="btn btn-success"
                                                @click="uploadResume"
                                                :disabled="
                                                    !resumeFile ||
                                                    resumeUploading
                                                "
                                            >
                                                {{
                                                    resumeUploading
                                                        ? "Uploading..."
                                                        : student.resume
                                                            ? "Update Resume"
                                                            : "Upload Resume"
                                                }}
                                            </button>

                                            <small class="text-muted">
                                                PDF, DOC or DOCX — maximum 5 MB
                                            </small>

                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                <div
                    v-if="student && isEditing"
                    class="card border-0 shadow-sm mb-4"
                >

                    <div class="card-header bg-white border-0 pt-4 px-4">

                        <h2 class="h4 fw-bold mb-1">
                            Edit Profile
                        </h2>

                        <p class="text-muted mb-0">
                            Update your placement profile information
                        </p>

                    </div>

                    <div class="card-body p-4">

                        <form @submit.prevent="saveProfile">

                            <div class="row g-3">

                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Student ID
                                    </label>

                                    <input
                                        :value="student.student_id"
                                        type="text"
                                        class="form-control"
                                        disabled
                                    />
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Email
                                    </label>

                                    <input
                                        :value="student.email"
                                        type="email"
                                        class="form-control"
                                        disabled
                                    />
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Name
                                    </label>

                                    <input
                                        v-model="editForm.name"
                                        type="text"
                                        class="form-control"
                                        required
                                    />
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Department
                                    </label>

                                    <input
                                        v-model="editForm.department"
                                        type="text"
                                        class="form-control"
                                        required
                                    />
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        Phone
                                    </label>

                                    <input
                                        v-model="editForm.phone"
                                        type="text"
                                        class="form-control"
                                        required
                                    />
                                </div>

                                <div class="col-md-6">
                                    <label class="form-label fw-semibold">
                                        CGPA
                                    </label>

                                    <input
                                        v-model="editForm.cgpa"
                                        type="number"
                                        min="0"
                                        max="10"
                                        step="0.01"
                                        class="form-control"
                                        required
                                    />
                                </div>

                                <div class="col-12">
                                    <label class="form-label fw-semibold">
                                        Skills
                                    </label>

                                    <textarea
                                        v-model="editForm.skills"
                                        rows="3"
                                        class="form-control"
                                        placeholder="Example: Python, C, SQL, Vue"
                                    ></textarea>
                                </div>

                                <div class="col-12">
                                    <label class="form-label fw-semibold">
                                        Education
                                    </label>

                                    <textarea
                                        v-model="editForm.education"
                                        rows="3"
                                        class="form-control"
                                        placeholder="Enter your educational details"
                                    ></textarea>
                                </div>

                                <div class="col-12">
                                    <label class="form-label fw-semibold">
                                        Experience
                                    </label>

                                    <textarea
                                        v-model="editForm.experience"
                                        rows="4"
                                        class="form-control"
                                        placeholder="Experience Summary"
                                    ></textarea>
                                </div>

                            </div>

                            <div class="d-flex gap-2 mt-4">

                                <button
                                    type="submit"
                                    class="btn btn-success"
                                    :disabled="saving"
                                >
                                    {{
                                        saving
                                            ? "Saving..."
                                            : "Save Changes"
                                    }}
                                </button>

                                <button
                                    type="button"
                                    class="btn btn-secondary"
                                    @click="cancelEditing"
                                    :disabled="saving"
                                >
                                    Cancel
                                </button>

                            </div>

                        </form>

                    </div>

                </div>

                <div class="card border-0 shadow-sm mb-4">

                    <div class="card-header bg-white border-0 pt-4 px-4">

                        <h2 class="h4 fw-bold mb-1">
                            Placement Drives
                        </h2>

                        <p class="text-muted mb-0">
                            Find and apply for available placement opportunities
                        </p>

                    </div>

                    <div class="card-body p-4">

                        <div class="bg-light rounded-3 p-3 p-md-4 mb-4">

                            <div class="row g-3 align-items-end">

                                <div class="col-md-9">
                                    <label class="form-label fw-semibold">
                                        Search Placement Drives
                                    </label>

                                    <input
                                        v-model="search"
                                        type="text"
                                        class="form-control"
                                        placeholder="Search by company, position or skill"
                                        @keyup.enter="loadJobs"
                                    />
                                </div>

                                <div class="col-md-3">

                                    <div class="d-flex gap-2">

                                        <button
                                            type="button"
                                            class="btn btn-primary flex-fill"
                                            @click="loadJobs"
                                        >
                                            Search
                                        </button>

                                        <button
                                            type="button"
                                            class="btn btn-outline-secondary"
                                            @click="clearSearch"
                                        >
                                            Reset
                                        </button>

                                    </div>

                                </div>

                            </div>

                        </div>

                        <div
                            v-if="jobsLoading"
                            class="text-center py-5"
                        >
                            <div
                                class="spinner-border text-primary mb-3"
                                role="status"
                            ></div>

                            <p class="text-muted mb-0">
                                Loading placement drives...
                            </p>
                        </div>

                        <div
                            v-else-if="jobs.length === 0"
                            class="text-center py-5"
                        >
                            <div class="display-6 text-muted mb-2">
                                <i class="bi bi-briefcase"></i>
                            </div>

                            <h5>
                                No placement drives found
                            </h5>

                            <p class="text-muted mb-0">
                                Try changing your search criteria.
                            </p>
                        </div>

                        <div
                            v-else
                            class="row g-4"
                        >

                            <div
                                v-for="job in jobs"
                                :key="job.id"
                                class="col-xl-6"
                            >

                                <div class="card h-100 border shadow-sm job-card">

                                    <div class="card-body p-4">

                                        <div class="d-flex justify-content-between align-items-start gap-3 mb-3">

                                            <div>

                                                <h3 class="h5 fw-bold mb-1">
                                                    {{ job.title }}
                                                </h3>

                                                <div class="text-primary fw-semibold">
                                                    {{ job.company.name }}
                                                </div>

                                            </div>

                                            <span class="badge text-bg-success">
                                                {{ job.status }}
                                            </span>

                                        </div>

                                        <div class="row g-2 small mb-4">

                                            <div class="col-md-6">
                                                <div class="job-detail">
                                                    <span class="text-muted">
                                                        Location
                                                    </span>
                                                    <strong>
                                                        {{ job.location || "-" }}
                                                    </strong>
                                                </div>
                                            </div>

                                            <div class="col-md-6">
                                                <div class="job-detail">
                                                    <span class="text-muted">
                                                        Salary
                                                    </span>
                                                    <strong>
                                                        <span
                                                            v-if="job.salary !== null"
                                                        >
                                                            ₹{{ job.salary }}
                                                        </span>
                                                        <span v-else>
                                                            Not specified
                                                        </span>
                                                    </strong>
                                                </div>
                                            </div>

                                            <div class="col-md-6">
                                                <div class="job-detail">
                                                    <span class="text-muted">
                                                        Experience
                                                    </span>
                                                    <strong>
                                                        {{ job.experience || "-" }}
                                                    </strong>
                                                </div>
                                            </div>

                                            <div class="col-md-6">
                                                <div class="job-detail">
                                                    <span class="text-muted">
                                                        Minimum CGPA
                                                    </span>
                                                    <strong>
                                                        {{ job.min_cgpa ?? "No minimum" }}
                                                    </strong>
                                                </div>
                                            </div>

                                            <div class="col-md-6">
                                                <div class="job-detail">
                                                    <span class="text-muted">
                                                        Deadline
                                                    </span>
                                                    <strong>
                                                        {{ job.deadline }}
                                                    </strong>
                                                </div>
                                            </div>

                                            <div class="col-md-6">
                                                <div class="job-detail">
                                                    <span class="text-muted">
                                                        Applications
                                                    </span>
                                                    <strong>
                                                        {{ job.application_count }}
                                                        <span v-if="job.application_limit">
                                                            / {{ job.application_limit }}
                                                        </span>
                                                        <span v-else>
                                                            / Unlimited
                                                        </span>
                                                    </strong>
                                                </div>
                                            </div>

                                        </div>

                                        <div class="border-top pt-3 mb-3">

                                            <h6 class="fw-bold">
                                                Description
                                            </h6>

                                            <p class="text-muted mb-0 text-break">
                                                {{ job.description || "-" }}
                                            </p>

                                        </div>

                                        <div class="border-top pt-3 mb-3">

                                            <h6 class="fw-bold">
                                                Required Skills
                                            </h6>

                                            <p class="text-muted mb-0 text-break">
                                                {{ job.skills_required || "-" }}
                                            </p>

                                        </div>

                                        <div class="border-top pt-3 mb-3">

                                            <h6 class="fw-bold">
                                                Benefits
                                            </h6>

                                            <p class="text-muted mb-0 text-break">
                                                {{ job.benefits || "-" }}
                                            </p>

                                        </div>

                                        <div class="border-top pt-3 mb-4">

                                            <h6 class="fw-bold">
                                                Company
                                            </h6>

                                            <p class="mb-1">
                                                {{ job.company.name }}
                                            </p>

                                            <p
                                                v-if="job.company.industry"
                                                class="text-muted small mb-1"
                                            >
                                                Industry:
                                                {{ job.company.industry }}
                                            </p>

                                            <p
                                                v-if="job.company.location"
                                                class="text-muted small mb-0"
                                            >
                                                Location:
                                                {{ job.company.location }}
                                            </p>

                                        </div>

                                        <div>

                                            <div
                                                v-if="job.already_applied"
                                                class="alert alert-info mb-0 text-center fw-semibold"
                                            >
                                                Already Applied
                                            </div>

                                            <div
                                                v-else-if="!job.cgpa_eligible"
                                                class="alert alert-danger mb-0 text-center fw-semibold"
                                            >
                                                CGPA requirement not met
                                            </div>

                                            <div
                                                v-else-if="job.application_limit_reached"
                                                class="alert alert-warning mb-0 text-center fw-semibold"
                                            >
                                                Application limit reached
                                            </div>

                                            <div v-else>

                                                <div class="alert alert-success text-center fw-semibold mb-2">
                                                    You are Eligible to apply
                                                </div>

                                                <button
                                                    class="btn btn-primary w-100"
                                                    @click="applyForJob(job)"
                                                    :disabled="applyingJobId === job.id"
                                                >
                                                    {{
                                                        applyingJobId === job.id
                                                            ? "Applying..."
                                                            : "Apply now"
                                                    }}
                                                </button>

                                            </div>

                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                <div class="card border-0 shadow-sm mb-4">

                    <div class="card-header bg-white border-0 pt-4 px-4">

                        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">

                            <div>
                                <h2 class="h4 fw-bold mb-1">
                                    My Applications
                                </h2>

                                <p class="text-muted mb-0">
                                    Track the progress of your applications
                                </p>
                            </div>

                            <button
                                class="btn btn-success"
                                @click="startExport"
                                :disabled="exportLoading"
                            >
                                {{
                                    exportLoading
                                        ? "Exporting..."
                                        : "Export Application History"
                                }}
                            </button>

                        </div>

                    </div>

                    <div class="card-body p-4">

                        <div
                            v-if="exportStatus"
                            class="alert alert-primary"
                        >
                            {{ exportStatus }}
                        </div>

                        <div
                            v-if="applicationsLoading"
                            class="text-center py-5"
                        >
                            <div
                                class="spinner-border text-primary mb-3"
                                role="status"
                            ></div>

                            <p class="text-muted mb-0">
                                Loading applications...
                            </p>
                        </div>

                        <div
                            v-else-if="applications.length === 0"
                            class="text-center py-5"
                        >
                            <div class="display-6 text-muted mb-2">
                                <i class="bi bi-file-earmark-text"></i>
                            </div>

                            <h5>
                                No applications yet
                            </h5>

                            <p class="text-muted mb-0">
                                Your submitted applications will appear here.
                            </p>
                        </div>

                        <div
                            v-else
                            class="d-flex flex-column gap-4"
                        >

                            <div
                                v-for="application in applications"
                                :key="application.id"
                                class="card border shadow-sm"
                            >

                                <div class="card-body p-4">

                                    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">

                                        <div>

                                            <h3 class="h5 fw-bold mb-1">
                                                {{ application.job.title }}
                                            </h3>

                                            <p class="text-primary fw-semibold mb-0">
                                                {{
                                                    application.company
                                                        ? application.company.name
                                                        : "Company unavailable"
                                                }}
                                            </p>

                                        </div>

                                        <span
                                            class="badge rounded-pill fs-6 px-3 py-2"
                                            :class="
                                                getStatusClass(
                                                    application.status
                                                )
                                            "
                                        >
                                            {{ application.status }}
                                        </span>

                                    </div>

                                    <div class="bg-light rounded-3 p-3 mb-4">

                                        <div class="row g-3 small">

                                            <div class="col-md-6">
                                                <span class="text-muted d-block">
                                                    Location
                                                </span>

                                                <strong>
                                                    {{
                                                        application.job.location || "-"
                                                    }}
                                                </strong>
                                            </div>

                                            <div class="col-md-6">
                                                <span class="text-muted d-block">
                                                    Salary
                                                </span>

                                                <strong>
                                                    <span
                                                        v-if="
                                                            application.job.salary !== null
                                                        "
                                                    >
                                                        ₹{{ application.job.salary }}
                                                    </span>

                                                    <span v-else>
                                                        Not specified
                                                    </span>
                                                </strong>
                                            </div>

                                            <div class="col-md-6">
                                                <span class="text-muted d-block">
                                                    Experience
                                                </span>

                                                <strong>
                                                    {{
                                                        application.job.experience || "-"
                                                    }}
                                                </strong>
                                            </div>

                                            <div class="col-md-6">
                                                <span class="text-muted d-block">
                                                    Applied On
                                                </span>

                                                <strong>
                                                    {{
                                                        formatUTCDateTime(
                                                            application.applied_at
                                                        )
                                                    }}
                                                </strong>
                                            </div>

                                            <div class="col-md-6">
                                                <span class="text-muted d-block">
                                                    Last Updated
                                                </span>

                                                <strong>
                                                    {{
                                                        formatUTCDateTime(
                                                            application.updated_at
                                                        )
                                                    }}
                                                </strong>
                                            </div>

                                            <div class="col-md-6">
                                                <span class="text-muted d-block">
                                                    Job Deadline
                                                </span>

                                                <strong>
                                                    {{
                                                        application.job.deadline || "-"
                                                    }}
                                                </strong>
                                            </div>

                                        </div>

                                    </div>

                                    <div
                                        v-if="application.company"
                                        class="border-top pt-3 mb-3"
                                    >

                                        <h4 class="h6 fw-bold">
                                            Company Information
                                        </h4>

                                        <p class="mb-1">
                                            <strong>Name:</strong>
                                            {{ application.company.name }}
                                        </p>

                                        <p
                                            v-if="application.company.industry"
                                            class="mb-1"
                                        >
                                            <strong>Industry:</strong>
                                            {{ application.company.industry }}
                                        </p>

                                        <p
                                            v-if="application.company.location"
                                            class="mb-1"
                                        >
                                            <strong>Location:</strong>
                                            {{ application.company.location }}
                                        </p>

                                        <p
                                            v-if="application.company.website"
                                            class="mb-0 text-break"
                                        >
                                            <strong>Website:</strong>
                                            {{ application.company.website }}
                                        </p>

                                    </div>

                                    <div
                                        v-if="application.remarks"
                                        class="alert alert-warning"
                                    >

                                        <h4 class="h6 fw-bold">
                                            Company Feedback
                                        </h4>

                                        <p class="mb-0">
                                            {{ application.remarks }}
                                        </p>

                                    </div>

                                    <div
                                        v-if="
                                            application.interview &&
                                            application.interview.datetime
                                        "
                                        class="alert alert-primary"
                                    >

                                        <h4 class="h6 fw-bold">
                                            Interview Schedule
                                        </h4>

                                        <div class="d-flex flex-column gap-2">

                                            <div>
                                                <strong>
                                                    Date & Time:
                                                </strong>

                                                {{
                                                    formatLocalDateTime(
                                                        application.interview.datetime
                                                    )
                                                }}
                                            </div>

                                            <div
                                                v-if="
                                                    application.interview.mode
                                                "
                                            >
                                                <strong>
                                                    Mode:
                                                </strong>

                                                {{
                                                    application.interview.mode
                                                }}
                                            </div>

                                            <div
                                                v-if="
                                                    application.interview.location
                                                "
                                            >
                                                <strong>
                                                    Location / Link:
                                                </strong>

                                                {{
                                                    application.interview.location
                                                }}
                                            </div>

                                            <div
                                                v-if="
                                                    application.interview.notes
                                                "
                                            >
                                                <strong>
                                                    Notes:
                                                </strong>

                                                {{
                                                    application.interview.notes
                                                }}
                                            </div>

                                        </div>

                                    </div>

                                    <div
                                        v-else-if="
                                            application.status ===
                                            'Shortlisted'
                                        "
                                        class="alert alert-warning"
                                    >
                                        Interview has not been scheduled yet.
                                    </div>

                                    <div
                                        v-if="
                                            application.status ===
                                            'Offer'
                                        "
                                        class="alert alert-success"
                                    >

                                        <h4 class="h6 fw-bold">
                                            🎉 Offer Received!
                                        </h4>

                                        <p>
                                            You have received an offer for this
                                            placement opportunity.
                                        </p>

                                        <div
                                            v-if="
                                                application.placement &&
                                                application.placement.offer_letter
                                            "
                                            class="border-top pt-3 mt-3"
                                        >

                                            <strong>
                                                Offer Letter
                                            </strong>

                                            <p class="small mt-1">
                                                Your offer letter is available.
                                            </p>

                                            <button
                                                type="button"
                                                class="btn btn-outline-success"
                                                @click="
                                                    viewOfferLetter(application)
                                                "
                                            >
                                                View Offer Letter
                                            </button>

                                        </div>

                                    </div>

                                    <div
                                        v-if="
                                            application.status ===
                                            'Placed'
                                        "
                                        class="alert alert-success"
                                    >

                                        <h4 class="h6 fw-bold">
                                            🎉 Congratulations! You are Placed.
                                        </h4>

                                        <p>
                                            Your placement has been confirmed.
                                        </p>

                                        <div
                                            v-if="application.placement"
                                            class="border-top pt-3 mt-3"
                                        >

                                            <p class="mb-2">
                                                <strong>
                                                    Position:
                                                </strong>

                                                {{
                                                    application.placement.position || "-"
                                                }}
                                            </p>

                                            <p class="mb-2">
                                                <strong>
                                                    Salary:
                                                </strong>

                                                <span
                                                    v-if="
                                                        application.placement.salary !== null
                                                    "
                                                >
                                                    ₹{{ application.placement.salary }}
                                                </span>

                                                <span v-else>
                                                    Not specified
                                                </span>
                                            </p>

                                            <p
                                                v-if="
                                                    application.placement.joining_date
                                                "
                                                class="mb-3"
                                            >
                                                <strong>
                                                    Joining Date:
                                                </strong>

                                                {{
                                                    application.placement.joining_date
                                                }}
                                            </p>

                                            <div
                                                v-if="
                                                    application.placement.offer_letter
                                                "
                                            >

                                                <strong>
                                                    Offer Letter
                                                </strong>

                                                <p class="small mt-1">
                                                    Your offer letter is available.
                                                </p>

                                                <button
                                                    type="button"
                                                    class="btn btn-outline-success"
                                                    @click="
                                                        viewOfferLetter(application)
                                                    "
                                                >
                                                    View Offer Letter
                                                </button>

                                            </div>

                                        </div>

                                    </div>

                                    <div
                                        v-if="
                                            application.status ===
                                            'Rejected'
                                        "
                                        class="alert alert-danger"
                                    >

                                        <h4 class="h6 fw-bold">
                                            Application Rejected
                                        </h4>

                                        <p class="mb-0">
                                            Your application was not selected
                                            for this opportunity.
                                        </p>

                                    </div>

                                    <div
                                        v-if="
                                            application.status ===
                                            'Interview'
                                        "
                                        class="alert alert-primary"
                                    >
                                        Your interview has been scheduled.
                                        Please attend the interview at the
                                        scheduled date and time.
                                    </div>

                                    <div
                                        v-if="
                                            application.status ===
                                            'Applied'
                                        "
                                        class="alert alert-light border"
                                    >
                                        Your application is currently under
                                        review by the company.
                                    </div>

                                    <div
                                        v-if="
                                            application.status ===
                                            'Shortlisted'
                                        "
                                        class="alert alert-warning mb-0"
                                    >
                                        You have been shortlisted. Please check
                                        the interview details above.
                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </main>

    </div>
</template>

<style scoped>
.profile-card {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.75rem;
    padding: 1rem;
    height: 100%;
}

.profile-card strong {
    color: #212529;
}

.job-card {
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.job-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1) !important;
}

.job-detail {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    background: #f8f9fa;
    border-radius: 0.5rem;
    padding: 0.7rem;
    height: 100%;
}

.job-detail strong {
    overflow-wrap: anywhere;
}

.card {
    border-radius: 0.75rem;
}

textarea {
    resize: vertical;
}

@media (max-width: 576px) {
    main {
        padding-top: 1rem !important;
    }
}
</style>