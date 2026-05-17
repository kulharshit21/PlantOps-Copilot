import {
  Activity,
  Bot,
  ClipboardList,
  Factory,
  Gauge,
  LayoutDashboard,
  ShieldCheck,
  Siren,
  Wrench,
} from "lucide-react";

export type UserRole = "technician" | "reliability_engineer" | "supervisor" | "admin";

export type DemoUser = {
  name: string;
  email: string;
  role: UserRole;
  organization: string;
  plant: string;
};

export type StatusTone = "healthy" | "watch" | "high" | "critical" | "neutral";

export const roleLabels: Record<UserRole, string> = {
  technician: "Technician",
  reliability_engineer: "Reliability Engineer",
  supervisor: "Supervisor",
  admin: "Admin",
};

export const demoUsers: DemoUser[] = [
  {
    name: "Ravi Technician",
    email: "ravi.technician@example.com",
    role: "technician",
    organization: "Northstar Manufacturing",
    plant: "Pune Plant A",
  },
  {
    name: "Meera Reliability",
    email: "meera.reliability@example.com",
    role: "reliability_engineer",
    organization: "Northstar Manufacturing",
    plant: "Pune Plant A",
  },
  {
    name: "Asha Supervisor",
    email: "asha.supervisor@example.com",
    role: "supervisor",
    organization: "Northstar Manufacturing",
    plant: "Pune Plant A",
  },
  {
    name: "Nikhil Admin",
    email: "nikhil.admin@example.com",
    role: "admin",
    organization: "Northstar Manufacturing",
    plant: "Pune Plant A",
  },
];

export const defaultDemoUser = demoUsers[2];

export const navigationItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/assets", label: "Assets", icon: Factory },
  { href: "/incidents", label: "Incidents", icon: Siren },
  { href: "/copilot", label: "Copilot", icon: Bot },
  { href: "/work-orders", label: "Work orders", icon: ClipboardList },
  { href: "/observability", label: "Ops health", icon: Gauge },
  { href: "/security", label: "Security proof", icon: ShieldCheck },
];

export const roleNavigation: Record<UserRole, string[]> = {
  technician: ["/dashboard", "/assets", "/incidents", "/copilot", "/work-orders"],
  reliability_engineer: [
    "/dashboard",
    "/assets",
    "/incidents",
    "/copilot",
    "/observability",
  ],
  supervisor: [
    "/dashboard",
    "/assets",
    "/incidents",
    "/copilot",
    "/work-orders",
    "/observability",
    "/security",
  ],
  admin: [
    "/dashboard",
    "/assets",
    "/incidents",
    "/copilot",
    "/work-orders",
    "/observability",
    "/security",
  ],
};

export const assets = [
  {
    id: "L2-SPINDLE-01",
    name: "Line 2 Spindle",
    line: "Line 2",
    status: "Critical",
    tone: "critical" as StatusTone,
    risk: 87,
    signal: "Torque + vibration",
    owner: "Asha Supervisor",
  },
  {
    id: "L1-PUMP-03",
    name: "Coolant Pump 3",
    line: "Line 1",
    status: "Watch",
    tone: "watch" as StatusTone,
    risk: 41,
    signal: "Pressure drift",
    owner: "Ravi Technician",
  },
  {
    id: "L3-CONVEYOR-02",
    name: "Packaging Conveyor",
    line: "Line 3",
    status: "Healthy",
    tone: "healthy" as StatusTone,
    risk: 18,
    signal: "Nominal",
    owner: "Ravi Technician",
  },
];

export const incidents = [
  {
    title: "High spindle torque and vibration",
    asset: "Line 2 Spindle",
    severity: "High Risk",
    tone: "high" as StatusTone,
    time: "2h ago",
    summary: "Operator reported vibration; torque and tool wear trending upward.",
  },
  {
    title: "Coolant pump pressure drift",
    asset: "Coolant Pump 3",
    severity: "Watch",
    tone: "watch" as StatusTone,
    time: "5h ago",
    summary: "Flow stable, pressure below normal operating band.",
  },
];

export const workOrders = [
  {
    title: "Inspect Line 2 spindle vibration and tool wear",
    asset: "Line 2 Spindle",
    priority: "Urgent",
    status: "Draft",
    due: "Next shift",
  },
  {
    title: "Verify coolant pump pressure sensor",
    asset: "Coolant Pump 3",
    priority: "Medium",
    status: "Review",
    due: "Tomorrow",
  },
];

export const systemStatus = [
  { label: "API health", value: "Online", tone: "healthy" as StatusTone },
  { label: "RAG mode", value: "Seed demo", tone: "watch" as StatusTone },
  { label: "LLM fallback", value: "Armed", tone: "healthy" as StatusTone },
  { label: "RLS posture", value: "Enabled", tone: "healthy" as StatusTone },
];

export const quickActions = [
  {
    title: "Run spindle triage",
    description: "Ask the main demo question with cited SOP evidence.",
    icon: Bot,
    href: "/copilot",
  },
  {
    title: "Review work order",
    description: "Open AI draft for supervisor approval.",
    icon: Wrench,
    href: "/work-orders",
  },
  {
    title: "Show security proof",
    description: "Explain RLS, roles, and no-secret posture.",
    icon: ShieldCheck,
    href: "/security",
  },
  {
    title: "Check ops health",
    description: "Inspect latency, fallback, and service signals.",
    icon: Activity,
    href: "/observability",
  },
];
