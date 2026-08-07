import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

import AdminDashboard from "../views/AdminDashboard.vue";
import CompanyDashboard from "../views/CompanyDashboard.vue";
import StudentDashboard from "../views/StudentDashboard.vue";

import NotFound from "../views/NotFound.vue";

const routes = [
    {
        path: "/",
        component: HomeView,
    },
    {
        path: "/login",
        component: LoginView,
    },
    {
        path: "/register",
        component: RegisterView,
    },
    {
        path: "/admin",
        component: AdminDashboard,
    },
    {
        path: "/company",
        component: CompanyDashboard,
    },
    {
        path: "/student",
        component: StudentDashboard,
    },
    {
        path: "/:pathMatch(.*)*",
        component: NotFound,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;