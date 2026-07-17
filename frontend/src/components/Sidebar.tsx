"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  role: string;
  setRole: (role: string) => void;
}

export default function Sidebar({ activeTab, setActiveTab, role, setRole }: SidebarProps) {
  const [gatewayOnline, setGatewayOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await api.getHealth();
        if (health && health.status === "healthy") {
          setGatewayOnline(true);
        } else {
          setGatewayOnline(false);
        }
      } catch (err) {
        setGatewayOnline(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: "dashboard", label: "Operations HUD", icon: "📊" },
    { id: "ingestion", label: "Policy Ingestion", icon: "📥" },
    { id: "audit", label: "Audit Console", icon: "⚡" },
  ];

  return (
    <header className="w-full h-16 border-b border-outline-variant bg-surface/80 backdrop-blur-md px-gutter flex items-center justify-between sticky top-0 z-50 shadow-md">
      
      {}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-background border border-primary/50 flex items-center justify-center shadow-[0_0_10px_rgba(0,240,255,0.2)]">
          <span className="text-base text-primary font-bold">🛡️</span>
        </div>
        <div className="hidden sm:block">
          <h1 className="text-sm font-bold text-on-surface leading-tight tracking-tight uppercase">
            ReguDrift AI
          </h1>
          <p className="text-[9px] text-secondary font-mono tracking-widest uppercase">
            SOC Console
          </p>
        </div>
      </div>

      {}
      <div className="flex items-center gap-component-gap">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs transition-all duration-200 focus:outline-none font-medium ${
                isActive
                  ? "bg-primary/10 text-primary border border-primary/30 shadow-[0_0_8px_rgba(0,240,255,0.08)]"
                  : "text-on-surface-variant hover:bg-surface-bright hover:text-on-surface border border-transparent"
              }`}
            >
              <span>{item.icon}</span>
              <span className="hidden md:inline">{item.label}</span>
            </button>
          );
        })}
      </div>

      {}
      <div className="flex items-center gap-4">
        {}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 border border-outline-variant rounded-full bg-background text-[10px] text-on-surface-variant">
          <div
            className={`w-1.5 h-1.5 rounded-full ${
              gatewayOnline === true
                ? "bg-success shadow-[0_0_6px_rgba(16,185,129,0.6)] animate-pulse"
                : gatewayOnline === false
                ? "bg-error shadow-[0_0_6px_rgba(244,63,94,0.6)] animate-ping"
                : "bg-warning animate-pulse"
            }`}
          ></div>
          <span className="font-mono text-[9px]">
            {gatewayOnline === true ? "GW ONLINE" : gatewayOnline === false ? "GW OFFLINE" : "GW POLLING"}
          </span>
        </div>

        {}
        <div className="flex items-center bg-background border border-outline-variant p-0.5 rounded-full">
          <button
            onClick={() => setRole("Auditor")}
            className={`px-3 py-1 text-[10px] font-mono uppercase rounded-full transition-all focus:outline-none ${
              role === "Auditor"
                ? "bg-secondary text-white font-bold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="Read-Only Auditor"
          >
            Auditor
          </button>
          <button
            onClick={() => setRole("SecOps_Admin")}
            className={`px-3 py-1 text-[10px] font-mono uppercase rounded-full transition-all focus:outline-none ${
              role === "SecOps_Admin"
                ? "bg-primary text-background font-bold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="Full Write Administrator"
          >
            Admin
          </button>
        </div>
      </div>

    </header>
  );
}
