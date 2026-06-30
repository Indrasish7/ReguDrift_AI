"use client";

import React from "react";

interface MetricCardsProps {
  healthScore?: number;
  activeGuidelines?: number;
  criticalGaps?: number;
  statusText?: string;
  hasAudited?: boolean;
}

export default function MetricCards({
  healthScore = 75,
  activeGuidelines = 142,
  criticalGaps = 12,
  statusText = "Drift Detected",
  hasAudited = false,
}: MetricCardsProps) {
  // Compute SVG dash offset for the circle progress (radius is 40, so circumference is 2 * pi * 40 = 251.2)
  const circumference = 251.2;
  const strokeDashoffset = circumference - (healthScore / 100) * circumference;

  // Status color codes based on health
  const getHealthColor = () => {
    if (healthScore >= 90) return "text-emerald-500";
    if (healthScore >= 70) return "text-amber-500";
    return "text-red-500";
  };

  const getHealthBorder = () => {
    if (healthScore >= 90) return "hover:border-emerald-500/50";
    if (healthScore >= 70) return "hover:border-amber-500/50";
    return "hover:border-red-500/50";
  };

  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-component-gap lg:gap-gutter">
      {/* Card 1: Global Compliance Health Score */}
      <div
        className={`bg-surface-container border border-outline-variant rounded p-container-padding flex flex-col relative overflow-hidden transition-all duration-300 ${getHealthBorder()}`}
      >
        <div
          className={`absolute top-0 left-0 w-full h-1 ${
            healthScore >= 90 ? "bg-emerald-500" : healthScore >= 70 ? "bg-amber-500" : "bg-red-500"
          }`}
        ></div>
        <div className="flex justify-between items-start mb-4">
          <h2 className="font-label-caps text-xs text-on-surface-variant uppercase tracking-wider">
            Global Compliance Health Score
          </h2>
          <span className={`text-sm ${getHealthColor()}`}>⚠️</span>
        </div>
        <div className="flex-grow flex items-center justify-center py-4">
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                className="text-surface-container-highest"
                cx="50"
                cy="50"
                fill="transparent"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
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
                strokeWidth="8"
              ></circle>
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="font-display-lg text-3xl font-bold text-on-surface">
                {healthScore}
                <span className="text-sm text-on-surface-variant">%</span>
              </span>
            </div>
          </div>
        </div>
        <div className="mt-auto pt-4 border-t border-outline-variant flex justify-between items-center">
          <span className={`font-body-sm text-xs ${getHealthColor()} flex items-center gap-1`}>
            {hasAudited ? "⬇️ -5% from last audit" : "Baseline verification"}
          </span>
          <span className="font-label-caps text-[10px] text-on-surface-variant uppercase">
            Status: {statusText}
          </span>
        </div>
      </div>

      {/* Card 2: Active Guidelines */}
      <div className="bg-surface-container border border-outline-variant rounded p-container-padding flex flex-col hover:border-outline transition-colors duration-300">
        <div className="flex justify-between items-start mb-4">
          <h2 className="font-label-caps text-xs text-on-surface-variant uppercase tracking-wider">
            Active Guidelines Tracked
          </h2>
          <span className="text-on-surface-variant text-sm">📋</span>
        </div>
        <div className="flex-grow flex flex-col justify-center py-6">
          <div className="font-display-lg text-5xl leading-none font-bold text-on-surface mb-2 tracking-tighter">
            {activeGuidelines}
          </div>
          <div className="font-body-sm text-xs text-on-surface-variant">
            Across 12 regulatory frameworks
          </div>
        </div>
        <div className="mt-auto pt-4 border-t border-outline-variant">
          <div className="w-full bg-surface-container-highest h-1 rounded-full overflow-hidden">
            <div className="bg-primary h-full w-[92%]"></div>
          </div>
          <div className="flex justify-between mt-2">
            <span className="font-label-caps text-[10px] text-on-surface-variant uppercase">Coverage</span>
            <span className="font-label-caps text-[10px] text-primary">92%</span>
          </div>
        </div>
      </div>

      {/* Card 3: Critical Drift Gaps */}
      <div className="bg-surface-container border border-outline-variant rounded p-container-padding flex flex-col hover:border-red-500/50 transition-colors duration-300">
        <div className="flex justify-between items-start mb-4">
          <h2 className="font-label-caps text-xs text-on-surface-variant uppercase tracking-wider">
            Critical Drift Gaps Detected
          </h2>
          <span className="text-red-500 text-sm">🚨</span>
        </div>
        <div className="flex-grow flex flex-col justify-center items-start">
          <div className="inline-flex items-center justify-center bg-red-500/10 border border-red-500/30 text-red-500 px-4 py-2 rounded">
            <span className="font-display-lg text-4xl leading-none font-bold tracking-tighter">
              {criticalGaps}
            </span>
          </div>
          <div className="font-body-sm text-xs text-on-surface-variant mt-3 flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
            <span>{criticalGaps > 0 ? `${criticalGaps} Requires immediate action` : "System aligned"}</span>
          </div>
        </div>
        <div className="mt-auto pt-4 border-t border-outline-variant flex gap-2">
          <button className="flex-grow border border-outline-variant bg-surface hover:bg-surface-container-high text-on-surface font-label-caps text-xs py-2 rounded transition-colors text-center focus:outline-none">
            View List
          </button>
          <button className="flex-grow border border-primary text-primary hover:bg-primary/10 font-label-caps text-xs py-2 rounded transition-colors text-center focus:outline-none">
            Triage
          </button>
        </div>
      </div>
    </section>
  );
}
