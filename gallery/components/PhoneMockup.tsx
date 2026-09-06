"use client";

import React from "react";

interface PhoneMockupProps {
  children: React.ReactNode;
}

export function PhoneMockup({ children }: PhoneMockupProps) {
  return (
    <div className="flex items-center justify-center py-4">
      {/* iPhone outer frame */}
      <div
        className="relative bg-gray-900 rounded-[44px] p-3 shadow-2xl"
        style={{ width: "300px" }}
      >
        {/* Notch / Dynamic Island */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 z-20">
          <div className="bg-gray-900 rounded-b-2xl px-6 pt-0 pb-1.5">
            <div className="w-20 h-5 bg-black rounded-full" />
          </div>
        </div>

        {/* Screen bezel */}
        <div className="rounded-[32px] overflow-hidden bg-white dark:bg-gray-950 relative">
          {/* Status bar */}
          <div className="flex items-center justify-between px-6 pt-3 pb-1 text-[10px] font-semibold relative z-10">
            <span className="text-gray-900 dark:text-gray-100">9:41</span>
            <div className="flex items-center gap-1">
              {/* Signal */}
              <svg
                width="14"
                height="10"
                viewBox="0 0 14 10"
                className="text-gray-900 dark:text-gray-100"
              >
                <rect x="0" y="7" width="2.5" height="3" rx="0.5" fill="currentColor" />
                <rect x="3.5" y="5" width="2.5" height="5" rx="0.5" fill="currentColor" />
                <rect x="7" y="2.5" width="2.5" height="7.5" rx="0.5" fill="currentColor" />
                <rect x="10.5" y="0" width="2.5" height="10" rx="0.5" fill="currentColor" />
              </svg>
              {/* WiFi */}
              <svg
                width="12"
                height="10"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-gray-900 dark:text-gray-100"
              >
                <path d="M1.42 9a16 16 0 0121.16 0" />
                <path d="M5 12.55a11 11 0 0114.08 0" />
                <path d="M8.53 16.11a6 6 0 016.95 0" />
                <circle cx="12" cy="20" r="1" fill="currentColor" />
              </svg>
              {/* Battery */}
              <div className="flex items-center">
                <div className="w-5 h-2.5 border border-current rounded-sm relative">
                  <div className="absolute inset-0.5 bg-current rounded-[1px]" />
                </div>
                <div className="w-0.5 h-1 bg-current rounded-r-sm" />
              </div>
            </div>
          </div>

          {/* Content area */}
          <div
            className="overflow-y-auto"
            style={{ height: "540px" }}
          >
            {children}
          </div>

          {/* Home indicator */}
          <div className="flex justify-center pb-2 pt-1">
            <div className="w-28 h-1 bg-gray-400 dark:bg-gray-600 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
