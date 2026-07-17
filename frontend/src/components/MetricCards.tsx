"use client";

import React from "react";
import { AnalyticsHistoryPoint } from "@/lib/api";

interface MetricCardsProps {
  healthScore?: number;
  activeGuidelines?: number;
  criticalGaps?: number;
  statusText?: string;
  hasAudited?: boolean;
  historyData?: AnalyticsHistoryPoint[];
}

export default function MetricCards({
  healthScore = 45,
  activeGuidelines = 142,
  criticalGaps = 12,
  statusText = "Drift Detected",
  hasAudited = false,
  historyData = [],
}: MetricCardsProps) {
  const circumference = 251.2;
  const strokeDashoffset = circumference - (healthScore / 100) * circumference;

  const getHealthColor = () => {
    if (healthScore >= 90) return "text-success";
    if (healthScore >= 70) return "text-warning";
    return "text-error";
  };

  const getHealthGlow = () => {
    if (healthScore >= 90) return "shadow-[0_0_15px_rgba(16,185,129,0.15)]";
    if (healthScore >= 70) return "shadow-[0_0_15px_rgba(251,188,5,0.15)]";
    return "shadow-[0_0_15px_rgba(244,63,94,0.15)]";
  };

  const renderSparkline = () => {
    const width = 200;
    const height = 45;
    const padding = 4;

    if (!historyData || historyData.length < 2) {
      const mockPoints = "4,35 40,28 80,40 120,15 160,32 196,25";
      return (
        <svg className="w-full h-12 overflow-visible" viewBox={`0 0 ${width} ${height}`}>
          <polyline
            fill="none"
            stroke="#8B5CF6" 
            strokeWidth="2"
            points={mockPoints}
            className="drop-shadow-[0_0_6px_rgba(139,92,246,0.6)]"
          />
          <path
            d={`M4,${height} L${mockPoints} L196,${height} Z`}
            fill="url(#violetGradient)"
            opacity="0.15"
          />
          <defs>
            <linearGradient id="violetGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8B5CF6" />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      );
    }

    const pointsCount = historyData.length;
    const coordinates = historyData.map((pt, idx) => {
      const x = (idx / (pointsCount - 1)) * (width - 2 * padding) + padding;
      const y = height - padding - (pt.global_health_score / 100) * (height - 2 * padding);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    const pointsStr = coordinates.join(" ");

    return (
      <svg className="w-full h-12 overflow-visible" viewBox={`0 0 ${width} ${height}`}>
        <polyline
          fill="none"
          stroke="#8B5CF6"
          strokeWidth="2"
          points={pointsStr}
          className="drop-shadow-[0_0_6px_rgba(139,92,246,0.6)]"
        />
        <path
          d={`M${padding},${height} L${pointsStr} L${width - padding},${height} Z`}
          fill="url(#violetGradient)"
          opacity="0.2"
        />
      </svg>
    );
  };

  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
      
      {}
      <div className={`bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-5 flex flex-col relative transition-all duration-300 hover:border-primary/30 ${getHealthGlow()}`}>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-mono tracking-widest text-on-surface-variant uppercase font-bold">
            Compliance Index
          </h2>
          <span className={`text-[10px] font-mono font-bold ${getHealthColor()}`}>
            ● {statusText.toUpperCase()}
          </span>
        </div>
        
        <div className="flex-grow flex items-center justify-center py-2">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                className="text-surface-bright"
                cx="50"
                cy="50"
                fill="transparent"
                r="40"
                stroke="currentColor"
                strokeWidth="7"
              ></circle>
              <circle
                className={getHealthColor()}
                cx="50"
                cy="50"
                fill="transparent"
                r="40"
                stroke="currentColor"
                strokeDasharray={`${circumference}`}
                strokeDashoffset={`${strokeDashoffset}`}
                strokeWidth="7"
                strokeLinecap="round"
              ></circle>
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-3xl font-bold font-mono text-on-surface tracking-tighter">
                {healthScore}
                <span className="text-xs text-on-surface-variant">%</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {}
      <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-5 flex flex-col transition-all duration-300 hover:border-primary/30 shadow-[0_0_15px_rgba(0,240,255,0.05)]">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-mono tracking-widest text-on-surface-variant uppercase font-bold">
            Guidelines Evaluated
          </h2>
          <span className="text-primary text-xs font-mono font-bold">ACTIVE</span>
        </div>
        
        <div className="flex-grow flex flex-col justify-center py-4">
          <div className="text-5xl font-bold font-mono text-on-surface tracking-tighter mb-1">
            {activeGuidelines}
          </div>
          <span className="text-[10px] font-mono text-on-surface-variant uppercase tracking-wider">
            Across 12 Frameworks
          </span>
        </div>
        
        <div className="mt-auto pt-2">
          <div className="w-full bg-surface-bright h-1 rounded-full overflow-hidden">
            <div className="bg-primary h-full w-[92%] shadow-[0_0_8px_#00F0FF]"></div>
          </div>
        </div>
      </div>

      {}
      <div className="bg-surface/85 backdrop-blur-md border border-outline-variant rounded-xl p-5 flex flex-col transition-all duration-300 hover:border-secondary/30 shadow-[0_0_15px_rgba(139,92,246,0.05)]">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-[10px] font-mono tracking-widest text-on-surface-variant uppercase font-bold">
            Historical Trend
          </h2>
          <span className="text-secondary text-xs font-mono font-bold">TIMELINE</span>
        </div>
        
        <div className="flex-grow flex flex-col justify-center py-2">
          {renderSparkline()}
        </div>
        
        <div className="mt-auto flex justify-between items-center text-[10px] font-mono text-on-surface-variant uppercase tracking-wider">
          <span>Total runs logs</span>
          <span className="text-secondary font-bold font-mono">
            {historyData.length > 0 ? `${historyData.length} entries` : "6 simulated"}
          </span>
        </div>
      </div>

    </section>
  );
}
