Here is the complete set of files, designed as per your brief.

I've structured the color system and mock data in `src/lib/utils.ts` to be easily swappable with real Convex data later. I've also created helper functions for generating Tailwind color classes based on agent, project, status, and priority, ensuring consistency and adherence to the TMNT theme. All components use `lucide-react` for icons and are built with React + Tailwind CSS.

---

=== FILE: src/lib/utils.ts ===
```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// --- Utility function for Tailwind CSS class merging ---
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Interfaces ---

export type AgentStatus = "active" | "idle" | "error" | "offline";
export type ProjectName = "Brinc" | "Cerebro" | "Mana Capital" | "Personal" | "Fleet";
export type Priority = "P0" | "P1" | "P2" | "P3";
export type TaskStatus = "Inbox" | "Assigned" | "In Progress" | "Review" | "Done" | "Blocked";
export type ActivityType = "task" | "edit" | "status" | "heartbeat" | "memory" | "deploy" | "message";

export interface Agent {
  id: string;
  name: string;
  emoji: string;
  color: string; // Hex color for agent's signature color
  role: string;
  status: AgentStatus;
  currentTask: string;
  lastSeen: string;
  kingdomTheme?: string;
  project?: ProjectName;
  subAgents?: { emoji: string; name: string; level: string }[];
}

export interface Project {
  id: string;
  name: ProjectName;
  emoji: string;
  colorTone: string; // Tailwind color name like 'red', 'blue', 'orange', 'emerald'
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  project: ProjectName;
  priority: Priority;
  assignees: { id: string; name: string; emoji: string }[];
  dueDate?: string;
  status: TaskStatus;
}

export interface Activity {
  id: string;
  agentId: string;
  agentName: string;
  agentEmoji: string;
  agentColor: string;
  timestamp: string;
  type: ActivityType;
  title: string;
  body?: string;
  project?: ProjectName;
}

export interface Stat {
  id: string;
  title: string;
  value: string;
  description: string;
  icon?: React.ReactNode;
}

// --- Constants: Agent & Project Configurations ---

export const AGENTS_CONFIG: Agent[] = [
  {
    id: "molty",
    name: "Molty",
    emoji: "🦎",
    color: "#4CAF50", // Green
    role: "Fleet Coordinator",
    status: "active",
    currentTask: "Coordinating fleet operations",
    lastSeen: "2 min ago",
    kingdomTheme: "Leadership & Strategy",
    project: "Fleet",
    subAgents: [
      { emoji: "✨", name: "Spark", level: "L3" },
      { emoji: "🧭", name: "Compass", level: "L2" },
      { emoji: "⚡", name: "Jolt", level: "L1" },
    ],
  },
  {
    id: "raphael",
    name: "Raphael",
    emoji: "🔴",
    color: "#EF4444", // Red
    role: "Brinc Sales Lead",
    status: "active",
    currentTask: "Negotiating Brinc partnership",
    lastSeen: "5 min ago",
    kingdomTheme: "Sales & Growth",
    project: "Brinc",
    subAgents: [
      { emoji: "🤝", name: "Connect", level: "L3" },
      { emoji: "💰", name: "Dealflow", level: "L2" },
    ],
  },
  {
    id: "leonardo",
    name: "Leonardo",
    emoji: "🔵",
    color: "#3B82F6", // Blue
    role: "Venture Builder",
    status: "idle",
    currentTask: "Reviewing Cerebro project proposals",
    lastSeen: "15 min ago",
    kingdomTheme: "Innovation & Ventures",
    project: "Cerebro",
    subAgents: [
      { emoji: "💡", name: "IdeaGen", level: "L3" },
      { emoji: "🏗️", name: "Blueprint", level: "L2" },
    ],
  },
  {
    id: "donatello",
    name: "Donatello",
    emoji: "🟣",
    color: "#8B5CF6", // Purple
    role: "R&D (pending)",
    status: "offline",
    currentTask: "Developing new AI models",
    lastSeen: "1 day ago",
    kingdomTheme: "Research & Development",
    project: "Cerebro",
    subAgents: [
      { emoji: "🧪", name: "Synth", level: "L3" },
      { emoji: "⚙️", name: "Logic", level: "L2" },
    ],
  },
  {
    id: "michelangelo",
    name: "Michelangelo",
    emoji: "🟠",
    color: "#F97316", // Orange
    role: "Capital (pending)",
    status: "active",
    currentTask: "Sourcing for Mana Capital",
    lastSeen: "10 min ago",
    kingdomTheme: "Capital & Funding",
    project: "Mana Capital",
    subAgents: [
      { emoji: "📈", name: "MarketScout", level: "L3" },
      { emoji: "💸", name: "FundFlow", level: "L2" },
    ],
  },
  {
    id: "april",
    name: "April",
    emoji: "📰",
    color: "#EAB308", // Yellow
    role: "Personal Asst (pending)",
    status: "idle",
    currentTask: "Organizing human commander's schedule",
    lastSeen: "30 min ago",
    kingdomTheme: "Personal Assistance",
    project: "Personal",
    subAgents: [
      { emoji: "🗓️", name: "Scheduler", level: "L3" },
      { emoji: "✍️", name: "Draft", level: "L2" },
    ],
  },
  {
    id: "guillermo",
    name: "Guillermo",
    emoji: "👤",
    color: "#D4A017", // Gold (Special accent)
    role: "Human Commander",
    status: "active",
    currentTask: "Overseeing fleet operations",
    lastSeen: "Now",
    kingdomTheme: "Human Oversight",
    project: "Personal",
    subAgents: [], // Human Commander doesn't have sub-agents in this context
  },
];

export const PROJECTS_CONFIG: Project[] = [
  { id: "brinc", name: "Brinc", emoji: "🔴", colorTone: "red" },
  { id: "cerebro", name: "Cerebro", emoji: "🧠", colorTone: "blue" },
  { id: "mana-capital", name: "Mana Capital", emoji: "🟠", colorTone: "orange" },
  { id: "personal", name: "Personal", emoji: "🙂", colorTone: "emerald" },
  { id: "fleet", name: "Fleet", emoji: "🐢", colorTone: "green" }, // Using green for Fleet
];

// --- Navigation Items ---

export const NAV_ITEMS = [
  { id: "dojo", href: "/", emoji: "🏠", label: "The Dojo", description: "Dashboard" },
  { id: "sewer", href: "/sewer", emoji: "🕳️", label: "The Sewer", description: "Activity Feed" },
  { id: "war-room", href: "/war-room", emoji: "🗺️", label: "War Room", description: "Task Board" },
  { id: "tracker", href: "/tracker", emoji: "🐢", label: "Turtle Tracker", description: "Agent Status" },
  { id: "calendar", href: "/calendar", emoji: "🗓️", label: "Shell Calendar", description: "Timeline" },
  { id: "vault", href: "/vault", emoji: "📚", label: "The Vault", description: "Memory Browser" },
  { id: "pizza", href: "/pizza", emoji: "🍕", label: "Pizza Tracker", description: "Metrics" },
];

// --- UI Palette & Color Helper Functions ---

// Brand Accent (TMNT Green)
export const BRAND_ACCENT_COLOR = "emerald-500";

// Status Colors
export const STATUS_COLORS: Record<AgentStatus, string> = {
  active: "green-500",
  idle: "amber-500",
  error: "red-500",
  offline: "gray-400",
};

// Priority Colors
export const PRIORITY_COLORS: Record<Priority, string> = {
  P0: "red-500",
  P1: "orange-500",
  P2: "blue-500",
  P3: "gray-400",
};

export function getAgentTextColorClass(agentId: string): string {
  const agent = AGENTS_CONFIG.find((a) => a.id === agentId);
  return agent ? `text-[${agent.color}]` : "text-gray-900";
}

export function getAgentBgColorClass(agentId: string): string {
  const agent = AGENTS_CONFIG.find((a) => a.id === agentId);
  return agent ? `bg-[${agent.color}]` : "bg-gray-200";
}

export function getProjectBgColorClass(projectName: ProjectName): string {
  const project = PROJECTS_CONFIG.find((p) => p.name === projectName);
  return project ? `bg-${project.colorTone}-100` : "bg-gray-100";
}

export function getProjectTextColorClass(projectName: ProjectName): string {
  const project = PROJECTS_CONFIG.find((p) => p.name === projectName);
  return project ? `text-${project.colorTone}-700` : "text-gray-700";
}

export function getProjectBorderColorClass(projectName: ProjectName): string {
  const project = PROJECTS_CONFIG.find((p) => p.name === projectName);
  return project ? `border-${project.colorTone}-200` : "border-gray-200";
}

export function getStatusColorClass(status: AgentStatus): string {
  const color = STATUS_COLORS[status];
  return color ? `text-${color}` : "text-gray-900";
}

export function getStatusBgColorClass(status: AgentStatus): string {
  const color = STATUS_COLORS[status];
  return color ? `bg-${color}` : "bg-gray-200";
}

export function getPriorityBgColorClass(priority: Priority): string {
  const color = PRIORITY_COLORS[priority];
  return color ? `bg-${color}` : "bg-gray-200";
}

export function getPriorityTextColorClass(priority: Priority): string {
  const color = PRIORITY_COLORS[priority];
  return color ? `text-${color}` : "text-gray-900";
}

// --- Mock Data ---

export const MOCK_STATS: Stat[] = [
  {
    id: "fleet-status",
    title: "Fleet Status",
    value: "3/6 Active",
    description: "Agents currently online",
  },
  {
    id: "in-progress",
    title: "In Progress",
    value: "12 Tasks",
    description: "Active tasks across the fleet",
  },
  {
    id: "awaiting-review",
    title: "Awaiting Review",
    value: "4 Tasks",
    description: "Ready for human commander",
  },
  {
    id: "done-this-week",
    title: "Done This Week",
    value: "28 Tasks",
    description: "Completed since Monday",
  },
];

export const MOCK_TASKS: Task[] = [
  {
    id: "task-1",
    title: "Finalize Brinc partnership agreement",
    description: "Review legal terms and send for e-signature.",
    project: "Brinc",
    priority: "P0",
    assignees: [
      { id: "raphael", name: "Raphael", emoji: "🔴" },
      { id: "guillermo", name: "Guillermo", emoji: "👤" },
    ],
    dueDate: "Today",
    status: "In Progress",
  },
  {
    id: "task-2",
    title: "Draft Cerebro project scope for Q3",
    description: "Outline key objectives and deliverables for next quarter.",
    project: "Cerebro",
    priority: "P1",
    assignees: [{ id: "leonardo", name: "Leonardo", emoji: "🔵" }],
    dueDate: "Fri, Jul 26",
    status: "Assigned",
  },
  {
    id: "task-3",
    title: "Research new AI model architectures",
    description: "Explore transformer variants and their applications.",
    project: "Cerebro",
    priority: "P2",
    assignees: [{ id: "donatello", name: "Donatello", emoji: "🟣" }],
    dueDate: "Mon, Jul 29",
    status: "Inbox",
  },
  {
    id: "task-4",
    title: "Prepare Mana Capital investor brief",
    description: "Summarize recent market trends and investment opportunities.",
    project: "Mana Capital",
    priority: "P0",
    assignees: [{ id: "michelangelo", name: "Michelangelo", emoji: "🟠" }],
    dueDate: "Today",
    status: "In Progress",
  },
  {
    id: "task-5",
    title: "Schedule human commander's weekly sync",
    description: "Find available slots for Molty, Raphael, and Leonardo.",
    project: "Personal",
    priority: "P1",
    assignees: [{ id: "april", name: "April", emoji: "📰" }],
    dueDate: "Thu, Jul 25",
    status: "Assigned",
  },
  {
    id: "task-6",
    title: "Review Molty's fleet coordination report",
    description: "Provide feedback on agent assignments and resource allocation.",
    project: "Fleet",
    priority: "P0",
    assignees: [{ id: "guillermo", name: "Guillermo", emoji: "👤" }],
    dueDate: "Today",
    status: "Review",
  },
  {
    id: "task-7",
    title: "Update agent status definitions",
    description: "Clarify criteria for 'idle' vs 'offline'.",
    project: "Fleet",
    priority: "P2",
    assignees: [{ id: "molty", name: "Molty", emoji: "🦎" }],
    dueDate: "Wed, Jul 31",
    status: "Done",
  },
  {
    id: "task-8",
    title: "Integrate new data source for market analysis",
    description: "Connect to Bloomberg API for real-time stock data.",
    project: "Mana Capital",
    priority: "P1",
    assignees: [{ id: "michelangelo", name: "Michelangelo", emoji: "🟠" }],
    dueDate: "Fri, Aug 2",
    status: "In Progress",
  },
  {
    id: "task-9",
    title: "Develop new sales pitch for Brinc",
    description: "Focus on ROI and long-term partnership benefits.",
    project: "Brinc",
    priority: "P1",
    assignees: [{ id: "raphael", name: "Raphael", emoji: "🔴" }],
    dueDate: "Mon, Aug 5",
    status: "Assigned",
  },
];

export const MOCK_ACTIVITY: Activity[] = [
  {
    id: "act-1",
    agentId: "molty",
    agentName: "Molty",
    agentEmoji: "🦎",
    agentColor: "#4CAF50",
    timestamp: "2 min ago",
    type: "status",
    title: "Fleet status updated",
    body: "Molty assigned Task-6 to Guillermo for review.",
    project: "Fleet",
  },
  {
    id: "act-2",
    agentId: "raphael",
    agentName: "Raphael",
    agentEmoji: "🔴",
    agentColor: "#EF4444",
    timestamp: "5 min ago",
    type: "task",
    title: "Started working on Task-1",
    body: "Finalizing Brinc partnership agreement.",
    project: "Brinc",
  },
  {
    id: "act-3",
    agentId: "leonardo",
    agentName: "Leonardo",
    agentEmoji: "🔵",
    agentColor: "#3B82F6",
    timestamp: "15 min ago",
    type: "heartbeat",
    title: "Agent heartbeat",
    body: "Reviewing Cerebro project proposals.",
    project: "Cerebro",
  },
  {
    id: "act-4",
    agentId: "molty",
    agentName: "Molty",
    agentEmoji: "🦎",
    agentColor: "#4CAF50",
    timestamp: "20 min ago",
    type: "deploy",
    title: "Deployed new coordination module",
    body: "Improved task assignment logic.",
    project: "Fleet",
  },
  {
    id: "act-5",
    agentId: "michelangelo",
    agentName: "Michelangelo",
    agentEmoji: "🟠",
    agentColor: "#F97316",
    timestamp: "30 min ago",
    type: "memory",
    title: "Accessed market analysis memory",
    body: "Retrieved latest trends for Mana Capital.",
    project: "Mana Capital",
  },
  {
    id: "act-6",
    agentId: "raphael",
    agentName: "Raphael",
    agentEmoji: "🔴",
    agentColor: "#EF4444",
    timestamp: "45 min ago",
    type: "message",
    title: "Sent message to Guillermo",
    body: "Regarding Brinc contract clause.",
    project: "Brinc",
  },
  {
    id: "act-7",
    agentId: "april",
    agentName: "April",
    agentEmoji: "📰",
    agentColor: "#EAB308",
    timestamp: "1 hour ago",
    type: "edit",
    title: "Updated human commander's calendar",
    body: "Added new meeting with Brinc team.",
    project: "Personal",
  },
  {
    id: "act-8",
    agentId: "molty",
    agentName: "Molty",
    agentEmoji: "🦎",
    agentColor: "#4CAF50",
    timestamp: "1 hour ago",
    type: "task",
    title: "Completed Task-7",
    body: "Agent status definitions clarified.",
    project: "Fleet",
  },
  {
    id: "act-9",
    agentId: "leonardo",
    agentName: "Leonardo",
    agentEmoji: "🔵",
    agentColor: "#3B82F6",
    timestamp: "2 hours ago",
    type: "status",
    title: "Agent changed status to idle",
    body: "Awaiting new tasks from Cerebro.",
    project: "Cerebro",
  },
  {
    id: "act-10",
    agentId: "guillermo",
    agentName: "Guillermo",
    agentEmoji: "👤",
    agentColor: "#D4A017",
    timestamp: "3 hours ago",
    type: "edit",
    title: "Reviewed Task-6",
    body: "Provided feedback to Molty.",
    project: "Fleet",
  },
];

export const MOCK_AGENTS_COMPACT = AGENTS_CONFIG.filter(a => a.id !== "guillermo").map(agent => ({
  id: agent.id,
  name: agent.name,
  emoji: agent.emoji,
  color: agent.color,
  status: agent.status,
  currentTask: agent.currentTask,
  lastSeen: agent.lastSeen,
}));

export const MOCK_AGENTS_FULL = AGENTS_CONFIG; // All agents with full details

export const MOCK_KANBAN_COLUMNS: TaskStatus[] = [
  "Inbox",
  "Assigned",
  "In Progress",
  "Review",
  "Done",
  "Blocked",
];
```
=== END FILE ===

=== FILE: src/app/globals.css ===
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden; /* Prevent body scroll, let specific areas scroll */
}

body {
  font-family: 'Inter', sans-serif;
  @apply bg-gray-50 text-gray-900;
}
```
=== END FILE ===

=== FILE: src/app/layout.tsx ===
```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TMNT Mission Control",
  description: "Fleet dashboard for AI agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen bg-gray-50 text-gray-900">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
```
=== END FILE ===

=== FILE: src/components/layout/sidebar.tsx ===
```typescript
"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn, NAV_ITEMS, BRAND_ACCENT_COLOR } from "@/lib/utils";
import { Settings } from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col border-r border-gray-200 bg-white">
      {/* Logo Area */}
      <div className="flex items-center gap-3 p-6 pb-4">
        <span className="text-3xl">🐢</span>
        <div className="flex flex-col">
          <h1 className="text-xl font-bold text-gray-900">Mission Control</h1>
          <p className="text-xs text-gray-500">TMNT Fleet Operations</p>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1 px-4 py-4">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.id}
              href={item.href}
              className={cn(
                "group flex flex-col gap-0.5 rounded-lg p-3 transition-colors duration-200",
                isActive
                  ? `bg-${BRAND_ACCENT_COLOR}/10 text-${BRAND_ACCENT_COLOR} font-semibold`
                  : "text-gray-700 hover:bg-gray-100",
              )}
            >
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "text-xl",
                    isActive ? `text-${BRAND_ACCENT_COLOR}` : "text-gray-500",
                  )}
                >
                  {item.emoji}
                </span>
                <span className="text-sm">{item.label}</span>
              </div>
              <p
                className={cn(
                  "ml-9 text-xs",
                  isActive ? `text-${BRAND_ACCENT_COLOR}/70` : "text-gray-400 group-hover:text-gray-500",
                )}
              >
                {item.description}
              </p>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4">
        <Link
          href="/settings"
          className={cn(
            "group flex items-center gap-3 rounded-lg p-3 text-sm transition-colors duration-200",
            pathname === "/settings"
              ? `bg-${BRAND_ACCENT_COLOR}/10 text-${BRAND_ACCENT_COLOR} font-semibold`
              : "text-gray-700 hover:bg-gray-100",
          )}
        >
          <Settings
            className={cn(
              "h-5 w-5",
              pathname === "/settings" ? `text-${BRAND_ACCENT_COLOR}` : "text-gray-500",
            )}
          />
          Splinter's Den
        </Link>
        <p className="mt-2 text-center text-xs text-gray-400">v0.1.0-alpha</p>
      </div>
    </aside>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/badge.tsx ===
```typescript
import React from "react";
import { cn, getAgentTextColorClass, getAgentBgColorClass, getProjectTextColorClass, getProjectBgColorClass, getStatusTextColorClass, getStatusBgColorClass, getPriorityTextColorClass, getPriorityBgColorClass, AgentStatus, ProjectName, Priority } from "@/lib/utils";

interface BadgeProps {
  type: "agent" | "project" | "status" | "priority";
  variant: string; // Agent ID, Project Name, Status, Priority
  children?: React.ReactNode;
  className?: string;
}

export function Badge({ type, variant, children, className }: BadgeProps) {
  let colorClasses = "";
  let textContent = children || variant;

  switch (type) {
    case "agent":
      colorClasses = cn(getAgentBgColorClass(variant), getAgentTextColorClass(variant), "bg-opacity-10 text-opacity-80");
      break;
    case "project":
      colorClasses = cn(getProjectBgColorClass(variant as ProjectName), getProjectTextColorClass(variant as ProjectName));
      break;
    case "status":
      colorClasses = cn(getStatusBgColorClass(variant as AgentStatus), getStatusTextColorClass(variant as AgentStatus), "bg-opacity-10 text-opacity-80");
      break;
    case "priority":
      colorClasses = cn(getPriorityBgColorClass(variant as Priority), getPriorityTextColorClass(variant as Priority), "bg-opacity-10 text-opacity-80");
      break;
    default:
      colorClasses = "bg-gray-100 text-gray-700";
      break;
  }

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        colorClasses,
        className,
      )}
    >
      {textContent}
    </span>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/page-header.tsx ===
```typescript
import React from "react";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export function PageHeader({ title, subtitle, className }: PageHeaderProps) {
  return (
    <div className={cn("mb-6", className)}>
      <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
      {subtitle && <p className="mt-1 text-lg text-gray-600">{subtitle}</p>}
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/stat-card.tsx ===
```typescript
import React from "react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string;
  description: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatCard({ title, value, description, icon, className }: StatCardProps) {
  return (
    <div className={cn("flex flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      <p className="mt-1 text-3xl font-semibold text-gray-900">{value}</p>
      <p className="mt-2 text-sm text-gray-500">{description}</p>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/agent-card.tsx ===
```typescript
import React from "react";
import { cn, Agent, AgentStatus, getAgentTextColorClass, getStatusBgColorClass, getStatusTextColorClass } from "@/lib/utils";
import { Badge } from "./badge";

interface AgentCardProps {
  agent: Agent;
  variant?: "compact" | "full";
  className?: string;
}

export function AgentCard({ agent, variant = "full", className }: AgentCardProps) {
  const agentColorClass = getAgentTextColorClass(agent.id);
  const statusBgColorClass = getStatusBgColorClass(agent.status);
  const statusTextColorClass = getStatusTextColorClass(agent.status);

  if (variant === "compact") {
    return (
      <div className={cn("flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-3 shadow-sm", className)}>
        <span className="text-2xl">{agent.emoji}</span>
        <div className="flex-1">
          <p className={cn("text-sm font-medium", agentColorClass)}>
            {agent.name}
          </p>
          <p className="text-xs text-gray-500 truncate">{agent.currentTask}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={cn("h-2 w-2 rounded-full", statusBgColorClass)} />
          <p className="text-xs text-gray-400">{agent.lastSeen}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col rounded-xl border border-gray-200 bg-white p-6 shadow-sm", className)}>
      {/* Header */}
      <div className="flex items-center gap-4">
        <span className="text-4xl">{agent.emoji}</span>
        <div className="flex-1">
          <h3 className={cn("text-xl font-bold", agentColorClass)}>{agent.name}</h3>
          <p className="text-sm text-gray-600">{agent.role}</p>
        </div>
        <Badge type="status" variant={agent.status as AgentStatus} className={cn(statusBgColorClass, statusTextColorClass, "bg-opacity-10 text-opacity-80 capitalize")}>
          {agent.status}
        </Badge>
      </div>

      {/* Info Rows */}
      <div className="mt-5 space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Kingdom Theme:</span>
          <span className="font-medium text-gray-700">{agent.kingdomTheme || "N/A"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Project:</span>
          <span className="font-medium text-gray-700">{agent.project || "N/A"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Current Task:</span>
          <span className="font-medium text-gray-700 truncate max-w-[200px]">{agent.currentTask || "N/A"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Last Heartbeat:</span>
          <span className="font-medium text-gray-700">{agent.lastSeen}</span>
        </div>
      </div>

      {/* Sub-agents Section */}
      {agent.subAgents && agent.subAgents.length > 0 && (
        <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-4">
          <h4 className="mb-3 text-sm font-semibold text-gray-700">
            Sub-agents ({agent.subAgents.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {agent.subAgents.map((sub, index) => (
              <SubAgentChip key={index} emoji={sub.emoji} name={sub.name} level={sub.level} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

interface SubAgentChipProps {
  emoji: string;
  name: string;
  level: string;
}

export function SubAgentChip({ emoji, name, level }: SubAgentChipProps) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 text-xs font-medium text-gray-700 shadow-sm border border-gray-200">
      <span className="text-base">{emoji}</span>
      {name}
      <span className="ml-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{level}</span>
    </span>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/activity-item.tsx ===
```typescript
import React from "react";
import { cn, Activity, getAgentBgColorClass, getAgentTextColorClass, getProjectBgColorClass, getProjectTextColorClass } from "@/lib/utils";
import { FileText, Edit, RefreshCw, Heart, Brain, Rocket, MessageSquare } from "lucide-react";
import { Badge } from "./badge";

interface ActivityItemProps {
  activity: Activity;
  className?: string;
}

const ActivityIconMap: Record<Activity["type"], React.ReactNode> = {
  task: <FileText className="h-4 w-4" />,
  edit: <Edit className="h-4 w-4" />,
  status: <RefreshCw className="h-4 w-4" />,
  heartbeat: <Heart className="h-4 w-4" />,
  memory: <Brain className="h-4 w-4" />,
  deploy: <Rocket className="h-4 w-4" />,
  message: <MessageSquare className="h-4 w-4" />,
};

export function ActivityItem({ activity, className }: ActivityItemProps) {
  const agentBgClass = getAgentBgColorClass(activity.agentId);
  const agentTextColorClass = getAgentTextColorClass(activity.agentId);

  return (
    <div className={cn("flex items-start gap-4 py-4", className)}>
      {/* Agent Avatar */}
      <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xl", agentBgClass, "bg-opacity-20")}>
        {activity.agentEmoji}
      </div>

      {/* Content */}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <p className={cn("text-sm font-semibold", agentTextColorClass)}>
            {activity.agentName}
          </p>
          <span className="text-xs text-gray-400">•</span>
          <p className="text-xs text-gray-500">{activity.timestamp}</p>
          {activity.project && (
            <Badge type="project" variant={activity.project} className="ml-2" />
          )}
        </div>
        <div className="mt-1 flex items-start gap-2">
          <div className="shrink-0 text-gray-500">
            {ActivityIconMap[activity.type]}
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-gray-800">{activity.title}</h4>
            {activity.body && <p className="mt-0.5 text-sm text-gray-600">{activity.body}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/task-card.tsx ===
```typescript
import React from "react";
import { cn, Task, getAgentBgColorClass } from "@/lib/utils";
import { Badge } from "./badge";
import { MoreHorizontal } from "lucide-react";

interface TaskCardProps {
  task: Task;
  className?: string;
}

export function TaskCard({ task, className }: TaskCardProps) {
  return (
    <div className={cn("rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-all duration-200 hover:border-gray-300 hover:shadow-md", className)}>
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <Badge type="priority" variant={task.priority}>{task.priority}</Badge>
          <Badge type="project" variant={task.project}>{task.project}</Badge>
        </div>
        <button className="text-gray-400 hover:text-gray-600">
          <MoreHorizontal className="h-5 w-5" />
        </button>
      </div>
      <h3 className="mt-3 text-sm font-semibold text-gray-900">{task.title}</h3>
      {task.description && (
        <p className="mt-1 text-xs text-gray-600 line-clamp-2">{task.description}</p>
      )}
      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center -space-x-1">
          {task.assignees.map((assignee) => (
            <div
              key={assignee.id}
              className={cn("flex h-6 w-6 items-center justify-center rounded-full border border-white text-sm", getAgentBgColorClass(assignee.id), "bg-opacity-20")}
              title={assignee.name}
            >
              {assignee.emoji}
            </div>
          ))}
        </div>
        {task.dueDate && <span className="font-medium">{task.dueDate}</span>}
      </div>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/filter-bar.tsx ===
```typescript
import React from "react";
import { cn } from "@/lib/utils";

interface FilterBarProps<T extends string> {
  filters: { label: string; value: T }[];
  activeFilter: T;
  onFilterChange: (value: T) => void;
  className?: string;
}

export function FilterBar<T extends string>({ filters, activeFilter, onFilterChange, className }: FilterBarProps<T>) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {filters.map((filter) => (
        <button
          key={filter.value}
          onClick={() => onFilterChange(filter.value)}
          className={cn(
            "rounded-full px-4 py-2 text-sm font-medium transition-colors duration-200",
            activeFilter === filter.value
              ? "bg-emerald-500 text-white shadow-sm"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200",
          )}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/kanban-column.tsx ===
```typescript
import React from "react";
import { cn } from "@/lib/utils";

interface KanbanColumnProps {
  title: string;
  count: number;
  children: React.ReactNode;
  className?: string;
}

export function KanbanColumn({ title, count, children, className }: KanbanColumnProps) {
  return (
    <div className={cn("flex h-full w-80 shrink-0 flex-col rounded-xl bg-gray-100 p-4", className)}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <span className="rounded-full bg-gray-200 px-3 py-1 text-sm font-medium text-gray-600">{count}</span>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto pr-2 custom-scrollbar">
        {children}
      </div>
      {/* Custom scrollbar styles for overflow-y-auto */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: #d1d5db; /* gray-300 */
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background-color: #9ca3af; /* gray-400 */
        }
      `}</style>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/modal.tsx ===
```typescript
import React from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  className?: string;
}

export function Modal({ isOpen, onClose, title, children, className }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 p-4">
      <div className={cn("relative w-full max-w-lg rounded-xl bg-white p-6 shadow-xl", className)}>
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900">{title}</h3>
          <button onClick={onClose} className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="mt-6">
          {children}
        </div>
      </div>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/health-bar.tsx ===
```typescript
import React from "react";
import { cn, Agent, getStatusBgColorClass } from "@/lib/utils";

interface HealthBarProps {
  agents: Agent[];
  className?: string;
}

export function HealthBar({ agents, className }: HealthBarProps) {
  const totalAgents = agents.length;
  if (totalAgents === 0) {
    return (
      <div className={cn("h-4 w-full rounded-full bg-gray-200", className)}>
        <div className="h-full w-full rounded-full bg-gray-300 text-center text-xs text-gray-500 leading-4">No agents</div>
      </div>
    );
  }

  return (
    <div className={cn("flex h-4 w-full overflow-hidden rounded-full bg-gray-200", className)}>
      {agents.map((agent) => {
        const statusClass = getStatusBgColorClass(agent.status);
        return (
          <div
            key={agent.id}
            className={cn("h-full", statusClass)}
            style={{ width: `${100 / totalAgents}%` }}
            title={`${agent.name}: ${agent.status}`}
          />
        );
      })}
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/components/ui/placeholder-screen.tsx ===
```typescript
import React from "react";
import { cn, BRAND_ACCENT_COLOR } from "@/lib/utils";

interface PlaceholderScreenProps {
  emoji: string;
  title: string;
  description: string;
  className?: string;
}

export function PlaceholderScreen({ emoji, title, description, className }: PlaceholderScreenProps) {
  return (
    <div className={cn("flex h-full flex-col items-center justify-center text-center p-8", className)}>
      <span className={cn("text-8xl", `text-${BRAND_ACCENT_COLOR}`)}>{emoji}</span>
      <h2 className="mt-6 text-3xl font-bold text-gray-900">{title}</h2>
      <p className="mt-3 text-lg text-gray-600">{description}</p>
      <p className="mt-8 text-sm text-gray-500">
        This feature is currently under development by Donatello's R&D team.
        <br />
        Stay tuned for updates from the Shell Calendar!
      </p>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/app/page.tsx ===
```typescript
import React from "react";
import { PageHeader } from "@/components/ui/page-header";
import { StatCard } from "@/components/ui/stat-card";
import { TaskCard } from "@/components/ui/task-card";
import { AgentCard } from "@/components/ui/agent-card";
import { ActivityItem } from "@/components/ui/activity-item";
import { MOCK_STATS, MOCK_TASKS, MOCK_AGENTS_COMPACT, MOCK_ACTIVITY, Priority } from "@/lib/utils";
import { Activity, Clock, CheckCircle, ListTodo } from "lucide-react";

export default function DojoPage() {
  const priorityTasks = MOCK_TASKS.filter(
    (task) => task.priority === "P0" || task.priority === "P1",
  ).sort((a, b) => {
    const priorityOrder: Record<Priority, number> = { P0: 0, P1: 1, P2: 2, P3: 3 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  const recentActivity = MOCK_ACTIVITY.slice(0, 10); // Last 10 items

  return (
    <div className="container mx-auto p-8">
      <PageHeader
        title="🏠 The Dojo"
        subtitle="Your command center overview. At a glance: is the fleet healthy? What needs attention?"
      />

      {/* Stats Row */}
      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title={MOCK_STATS[0].title}
          value={MOCK_STATS[0].value}
          description={MOCK_STATS[0].description}
          icon={<ListTodo className="h-6 w-6" />}
        />
        <StatCard
          title={MOCK_STATS[1].title}
          value={MOCK_STATS[1].value}
          description={MOCK_STATS[1].description}
          icon={<Clock className="h-6 w-6" />}
        />
        <StatCard
          title={MOCK_STATS[2].title}
          value={MOCK_STATS[2].value}
          description={MOCK_STATS[2].description}
          icon={<Activity className="h-6 w-6" />}
        />
        <StatCard
          title={MOCK_STATS[3].title}
          value={MOCK_STATS[3].value}
          description={MOCK_STATS[3].description}
          icon={<CheckCircle className="h-6 w-6" />}
        />
      </div>

      {/* Three-column Grid */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Left: Priority Tasks */}
        <div className="lg:col-span-1">
          <h2 className="mb-4 text-xl font-semibold text-gray-900">🎯 Priority Tasks</h2>
          <div className="space-y-4">
            {priorityTasks.length > 0 ? (
              priorityTasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))
            ) : (
              <p className="text-gray-500">No priority tasks at the moment.</p>
            )}
          </div>
        </div>

        {/* Center: Fleet */}
        <div className="lg:col-span-1">
          <h2 className="mb-4 text-xl font-semibold text-gray-900">🐢 Fleet</h2>
          <div className="space-y-4">
            {MOCK_AGENTS_COMPACT.map((agent) => (
              <AgentCard key={agent.id} agent={agent} variant="compact" />
            ))}
          </div>
        </div>

        {/* Right: Recent Activity */}
        <div className="lg:col-span-1">
          <h2 className="mb-4 text-xl font-semibold text-gray-900">🕳️ Recent Activity</h2>
          <div className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))
            ) : (
              <p className="p-4 text-gray-500">No recent activity.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/app/war-room/page.tsx ===
```typescript
"use client";

import React, { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { FilterBar } from "@/components/ui/filter-bar";
import { KanbanColumn } from "@/components/ui/kanban-column";
import { TaskCard } from "@/components/ui/task-card";
import { Modal } from "@/components/ui/modal";
import { MOCK_TASKS, MOCK_KANBAN_COLUMNS, PROJECTS_CONFIG, AGENTS_CONFIG, ProjectName, Priority, TaskStatus } from "@/lib/utils";
import { Plus } from "lucide-react";

export default function WarRoomPage() {
  const [activeProjectFilter, setActiveProjectFilter] = useState<ProjectName | "All">("All");
  const [isNewTaskModalOpen, setIsNewTaskModalOpen] = useState(false);

  const projectFilters = [
    { label: "All", value: "All" as const },
    ...PROJECTS_CONFIG.map((p) => ({ label: p.name, value: p.name })),
  ];

  const filteredTasks = MOCK_TASKS.filter((task) => {
    if (activeProjectFilter === "All") return true;
    return task.project === activeProjectFilter;
  });

  const getTasksByStatus = (status: TaskStatus) => {
    return filteredTasks.filter((task) => task.status === status);
  };

  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, you'd send this data to Convex
    console.log("New task created!");
    setIsNewTaskModalOpen(false);
  };

  return (
    <div className="flex h-full flex-col p-8">
      {/* Top Bar */}
      <div className="mb-6 flex items-center justify-between">
        <PageHeader
          title="🗺️ War Room"
          subtitle="Kanban-style task board. The shared brain for fleet work."
          className="mb-0"
        />
        <div className="flex items-center gap-4">
          <FilterBar
            filters={projectFilters}
            activeFilter={activeProjectFilter}
            onFilterChange={(value) => setActiveProjectFilter(value)}
          />
          <button
            onClick={() => setIsNewTaskModalOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-emerald-600"
          >
            <Plus className="h-4 w-4" />
            New Task
          </button>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto pb-4">
        <div className="flex h-full gap-6">
          {MOCK_KANBAN_COLUMNS.map((status) => {
            const tasksInColumn = getTasksByStatus(status);
            return (
              <KanbanColumn key={status} title={status} count={tasksInColumn.length}>
                {tasksInColumn.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </KanbanColumn>
            );
          })}
        </div>
      </div>

      {/* New Task Modal */}
      <Modal
        isOpen={isNewTaskModalOpen}
        onClose={() => setIsNewTaskModalOpen(false)}
        title="Create New Task"
      >
        <form onSubmit={handleCreateTask} className="space-y-4">
          <div>
            <label htmlFor="title" className="mb-1 block text-sm font-medium text-gray-700">
              Title
            </label>
            <input
              type="text"
              id="title"
              className="w-full rounded-md border border-gray-300 p-2 text-gray-900 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-500 focus:ring-opacity-50"
              placeholder="Task title"
              required
            />
          </div>
          <div>
            <label htmlFor="description" className="mb-1 block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="description"
              rows={3}
              className="w-full rounded-md border border-gray-300 p-2 text-gray-900 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-500 focus:ring-opacity-50"
              placeholder="Detailed description of the task"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="project" className="mb-1 block text-sm font-medium text-gray-700">
                Project
              </label>
              <select
                id="project"
                className="w-full rounded-md border border-gray-300 p-2 text-gray-900 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-500 focus:ring-opacity-50"
                required
              >
                {PROJECTS_CONFIG.map((p) => (
                  <option key={p.id} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="priority" className="mb-1 block text-sm font-medium text-gray-700">
                Priority
              </label>
              <select
                id="priority"
                className="w-full rounded-md border border-gray-300 p-2 text-gray-900 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-500 focus:ring-opacity-50"
                required
              >
                {["P0", "P1", "P2", "P3"].map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label htmlFor="assignees" className="mb-1 block text-sm font-medium text-gray-700">
              Assignees
            </label>
            <select
              id="assignees"
              multiple
              className="w-full rounded-md border border-gray-300 p-2 text-gray-900 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-500 focus:ring-opacity-50"
            >
              {AGENTS_CONFIG.filter(a => a.id !== "guillermo").map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.emoji} {agent.name}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">Hold Cmd/Ctrl to select multiple</p>
          </div>
          <div>
            <label htmlFor="dueDate" className="mb-1 block text-sm font-medium text-gray-700">
              Due Date
            </label>
            <input
              type="date"
              id="dueDate"
              className="w-full rounded-md border border-gray-300 p-2 text-gray-900 shadow-sm focus:border-emerald-500 focus:ring focus:ring-emerald-500 focus:ring-opacity-50"
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => setIsNewTaskModalOpen(false)}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-emerald-600"
            >
              Create Task
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/app/sewer/page.tsx ===
```typescript
"use client";

import React, { useState } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { FilterBar } from "@/components/ui/filter-bar";
import { ActivityItem } from "@/components/ui/activity-item";
import { MOCK_ACTIVITY, AGENTS_CONFIG, PROJECTS_CONFIG, ProjectName } from "@/lib/utils";

export default function SewerPage() {
  const [activeAgentFilter, setActiveAgentFilter] = useState<string | "All">("All");
  const [activeProjectFilter, setActiveProjectFilter] = useState<ProjectName | "All">("All");

  const agentFilters = [
    { label: "All", value: "All" as const },
    ...AGENTS_CONFIG.filter(a => a.id !== "guillermo").map((a) => ({ label: a.emoji + " " + a.name, value: a.id })),
  ];

  const projectFilters = [
    { label: "All", value: "All" as const },
    ...PROJECTS_CONFIG.map((p) => ({ label: p.emoji + " " + p.name, value: p.name })),
  ];

  const filteredActivity = MOCK_ACTIVITY.filter((activity) => {
    const agentMatch = activeAgentFilter === "All" || activity.agentId === activeAgentFilter;
    const projectMatch = activeProjectFilter === "All" || activity.project === activeProjectFilter;
    return agentMatch && projectMatch;
  });

  return (
    <div className="container mx-auto p-8">
      <PageHeader
        title="🕳️ The Sewer"
        subtitle="Real-time log of everything happening. The pulse of the fleet."
      />

      {/* Filter Bar */}
      <div className="mb-6 flex flex-wrap items-start gap-4">
        <div>
          <h3 className="mb-2 text-sm font-medium text-gray-700">Filter by Agent:</h3>
          <FilterBar
            filters={agentFilters}
            activeFilter={activeAgentFilter}
            onFilterChange={(value) => setActiveAgentFilter(value)}
            className="flex-wrap"
          />
        </div>
        <div>
          <h3 className="mb-2 text-sm font-medium text-gray-700">Filter by Project:</h3>
          <FilterBar
            filters={projectFilters}
            activeFilter={activeProjectFilter}
            onFilterChange={(value) => setActiveProjectFilter(value)}
            className="flex-wrap"
          />
        </div>
      </div>

      {/* Activity Stream */}
      <div className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        {filteredActivity.length > 0 ? (
          filteredActivity.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} />
          ))
        ) : (
          <p className="p-4 text-gray-500">No activity matching your filters.</p>
        )}
      </div>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/app/tracker/page.tsx ===
```typescript
import React from "react";
import { PageHeader } from "@/components/ui/page-header";
import { AgentCard } from "@/components/ui/agent-card";
import { HealthBar } from "@/components/ui/health-bar";
import { MOCK_AGENTS_FULL } from "@/lib/utils";

export default function TurtleTrackerPage() {
  const agentsWithoutHuman = MOCK_AGENTS_FULL.filter(agent => agent.id !== "guillermo");

  return (
    <div className="container mx-auto p-8">
      <PageHeader
        title="🐢 Turtle Tracker"
        subtitle="Fleet roster with detailed agent cards. Monitor their status and current operations."
      />

      {/* Fleet Health Bar */}
      <div className="mb-8">
        <h2 className="mb-3 text-xl font-semibold text-gray-900">Fleet Health</h2>
        <HealthBar agents={agentsWithoutHuman} className="h-6" />
        <p className="mt-2 text-sm text-gray-500">
          <span className="inline-block h-3 w-3 rounded-full bg-green-500 mr-1"></span> Active
          <span className="inline-block h-3 w-3 rounded-full bg-amber-500 ml-4 mr-1"></span> Idle
          <span className="inline-block h-3 w-3 rounded-full bg-red-500 ml-4 mr-1"></span> Error
          <span className="inline-block h-3 w-3 rounded-full bg-gray-400 ml-4 mr-1"></span> Offline
        </p>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {MOCK_AGENTS_FULL.map((agent) => (
          <AgentCard key={agent.id} agent={agent} variant="full" />
        ))}
      </div>
    </div>
  );
}
```
=== END FILE ===

=== FILE: src/app/calendar/page.tsx ===
```typescript
import React from "react";
import { PlaceholderScreen } from "@/components/ui/placeholder-screen";

export default function ShellCalendarPage() {
  return (
    <PlaceholderScreen
      emoji="🗓️"
      title="Shell Calendar"
      description="Timeline view of tasks and agent schedules. Coming Soon!"
    />
  );
}
```
=== END FILE ===

=== FILE: src/app/vault/page.tsx ===
```typescript
import React from "react";
import { PlaceholderScreen } from "@/components/ui/placeholder-screen";

export default function TheVaultPage() {
  return (
    <PlaceholderScreen
      emoji="📚"
      title="The Vault"
      description="A searchable browser for agent memories and knowledge. Coming Soon!"
    />
  );
}
```
=== END FILE ===

=== FILE: src/app/pizza/page.tsx ===
```typescript
import React from "react";
import { PlaceholderScreen } from "@/components/ui/placeholder-screen";

export default function PizzaTrackerPage() {
  return (
    <PlaceholderScreen
      emoji="🍕"
      title="Pizza Tracker"
      description="Detailed metrics and performance analytics for the fleet. Coming Soon!"
    />
  );
}
```
=== END FILE ===

=== FILE: src/app/settings/page.tsx ===
```typescript
import React from "react";
import { PlaceholderScreen } from "@/components/ui/placeholder-screen";

export default function SplintersDenPage() {
  return (
    <PlaceholderScreen
      emoji="⚙️"
      title="Splinter's Den"
      description="Configure fleet settings, agent parameters, and user preferences. Coming Soon!"
    />
  );
}
```
=== END FILE ===