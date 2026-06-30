"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const [gatewayOnline, setGatewayOnline] = useState<boolean | null>(null);

  // Background interval polling task to monitor FastAPI health every 5 seconds
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
    { id: "dashboard", label: "Auditing Dashboard", icon: "📊" },
    { id: "ingestion", label: "Policy Ingestion Hub", icon: "📥" },
    { id: "audit", label: "Live Audit Console", icon: "⚡" },
  ];

  return (
    <nav className="hidden md:flex flex-col h-screen w-64 border-r border-outline-variant bg-surface-dim sticky top-0 left-0 z-50 flex-shrink-0">
      {/* Brand Header */}
      <div className="p-container-padding border-b border-outline-variant flex items-center gap-component-gap">
        <div className="w-10 h-10 rounded bg-primary-container border border-primary flex items-center justify-center">
          <span className="text-xl text-primary font-bold">🛡️</span>
        </div>
        <div>
          <h1 className="font-display-lg text-lg font-bold text-on-surface leading-tight tracking-tight">
            ReguDrift AI
          </h1>
          <p className="font-label-caps text-[10px] text-on-surface-variant tracking-wider uppercase">
            Institutional Oversight
          </p>
        </div>
      </div>

      {/* Navigation tabs */}
      <div className="flex-1 overflow-y-auto py-container-padding px-4 flex flex-col gap-unit">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-component-gap px-density-medium py-3 rounded-none text-left font-label-caps text-xs border-l-4 transition-all focus:outline-none ${
                isActive
                  ? "bg-surface-container-high border-primary text-primary font-bold"
                  : "border-transparent text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Gateway status & Integrity check footer */}
      <div className="mt-auto border-t border-outline-variant p-container-padding flex flex-col gap-component-gap">
        <div className="flex items-center gap-2 px-density-medium py-2 border border-outline-variant rounded bg-surface-container-lowest">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              gatewayOnline === true
                ? "bg-emerald-500 animate-pulse"
                : gatewayOnline === false
                ? "bg-rose-500 animate-ping"
                : "bg-amber-500"
            }`}
          ></div>
          <span className="font-label-caps text-[10px] text-on-surface-variant">
            Gateway Status: {gatewayOnline === true ? "Online" : gatewayOnline === false ? "Offline" : "Polling"}
          </span>
        </div>
        <div className="flex items-center gap-2 px-density-medium py-2 rounded bg-surface-container-high border-l-4 border-primary">
          <span className="text-sm">🔒</span>
          <span className="font-label-caps text-[10px] text-primary">System Secure</span>
        </div>
      </div>
    </nav>
  );
}
