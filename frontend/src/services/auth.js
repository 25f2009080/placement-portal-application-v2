import api from "./api";

export function login(credentials) {
    return api.post("/api/login", credentials);
}

export function registerStudent(data) {
    return api.post("/api/register/student", data);
}

export function registerCompany(data) {
    return api.post("/api/register/company", data);
}