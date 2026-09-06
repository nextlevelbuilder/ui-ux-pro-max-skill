"use client";

import React, { useState } from "react";

interface UIControlsShowcaseProps {
  accentColor: string;
  secondaryColor: string;
  borderRadius: string;
  boxShadow: string;
  backdropFilter?: string;
  fontFamily?: string;
  fontWeight?: string;
  border?: string;
  textShadow?: string;
  letterSpacing?: string;
  isDark: boolean;
}

export function UIControlsShowcase({
  accentColor,
  secondaryColor,
  borderRadius,
  boxShadow,
  backdropFilter,
  fontFamily,
  fontWeight,
  border,
  textShadow,
  letterSpacing,
  isDark,
}: UIControlsShowcaseProps) {
  const [toggle1, setToggle1] = useState(true);
  const [toggle2, setToggle2] = useState(false);
  const [check1, setCheck1] = useState(true);
  const [check2, setCheck2] = useState(false);
  const [radio, setRadio] = useState<"a" | "b">("a");
  const [slider, setSlider] = useState(65);

  const bg = isDark ? "#1a1a2e" : "#ffffff";
  const textPrimary = isDark ? "#f1f5f9" : "#1e293b";
  const textSecondary = isDark ? "#94a3b8" : "#64748b";
  const surfaceBg = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.03)";
  const borderColor = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)";
  const halfRadius = `calc(${borderRadius} / 2)`;

  const baseFont: React.CSSProperties = {
    fontFamily,
    fontWeight,
    textShadow,
    letterSpacing,
  };

  return (
    <div
      style={{
        background: bg,
        color: textPrimary,
        padding: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        fontSize: "13px",
        lineHeight: 1.4,
        minHeight: "100%",
        ...baseFont,
      }}
    >
      {/* 1. Buttons */}
      <Section label="Buttons" textSecondary={textSecondary}>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          <button
            style={{
              background: accentColor,
              color: "#fff",
              border: "none",
              borderRadius: halfRadius,
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: 600,
              boxShadow,
              cursor: "pointer",
              ...baseFont,
            }}
          >
            Primary
          </button>
          <button
            style={{
              background: secondaryColor,
              color: "#fff",
              border: "none",
              borderRadius: halfRadius,
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              ...baseFont,
            }}
          >
            Secondary
          </button>
          <button
            style={{
              background: "transparent",
              color: accentColor,
              border: `1.5px solid ${accentColor}`,
              borderRadius: halfRadius,
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              ...baseFont,
            }}
          >
            Outline
          </button>
        </div>
      </Section>

      {/* 2. Text Input */}
      <Section label="Text Input" textSecondary={textSecondary}>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <input
            type="text"
            placeholder="Placeholder text..."
            style={{
              background: surfaceBg,
              color: textPrimary,
              border: border || `1px solid ${borderColor}`,
              borderRadius: halfRadius,
              padding: "8px 12px",
              fontSize: "13px",
              outline: "none",
              width: "100%",
              boxSizing: "border-box",
              ...baseFont,
            }}
          />
          <input
            type="text"
            value="Filled input"
            readOnly
            style={{
              background: surfaceBg,
              color: textPrimary,
              border: border || `1px solid ${accentColor}44`,
              borderRadius: halfRadius,
              padding: "8px 12px",
              fontSize: "13px",
              outline: "none",
              width: "100%",
              boxSizing: "border-box",
              ...baseFont,
            }}
          />
        </div>
      </Section>

      {/* 3. Toggle Switch */}
      <Section label="Toggle" textSecondary={textSecondary}>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <ToggleSwitch
            on={toggle1}
            onToggle={() => setToggle1(!toggle1)}
            accentColor={accentColor}
            borderRadius={borderRadius}
          />
          <ToggleSwitch
            on={toggle2}
            onToggle={() => setToggle2(!toggle2)}
            accentColor={accentColor}
            borderRadius={borderRadius}
          />
        </div>
      </Section>

      {/* 4. Checkbox */}
      <Section label="Checkbox" textSecondary={textSecondary}>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <CheckboxItem
            checked={check1}
            onToggle={() => setCheck1(!check1)}
            label="Checked option"
            accentColor={accentColor}
            halfRadius={halfRadius}
            textPrimary={textPrimary}
            baseFont={baseFont}
          />
          <CheckboxItem
            checked={check2}
            onToggle={() => setCheck2(!check2)}
            label="Unchecked option"
            accentColor={accentColor}
            halfRadius={halfRadius}
            textPrimary={textPrimary}
            baseFont={baseFont}
          />
        </div>
      </Section>

      {/* 5. Radio Button */}
      <Section label="Radio" textSecondary={textSecondary}>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <RadioItem
            selected={radio === "a"}
            onSelect={() => setRadio("a")}
            label="Option A"
            accentColor={accentColor}
            textPrimary={textPrimary}
            baseFont={baseFont}
          />
          <RadioItem
            selected={radio === "b"}
            onSelect={() => setRadio("b")}
            label="Option B"
            accentColor={accentColor}
            textPrimary={textPrimary}
            baseFont={baseFont}
          />
        </div>
      </Section>

      {/* 6. Card */}
      <Section label="Card" textSecondary={textSecondary}>
        <div
          style={{
            background: surfaceBg,
            borderRadius,
            boxShadow,
            border: border || `1px solid ${borderColor}`,
            overflow: "hidden",
            backdropFilter,
            WebkitBackdropFilter: backdropFilter,
          }}
        >
          <div
            style={{
              height: "64px",
              background: `linear-gradient(135deg, ${accentColor}44, ${secondaryColor}44)`,
            }}
          />
          <div style={{ padding: "10px 12px" }}>
            <div
              style={{
                fontSize: "13px",
                fontWeight: 600,
                marginBottom: "4px",
                ...baseFont,
              }}
            >
              Card Title
            </div>
            <div
              style={{
                fontSize: "11px",
                color: textSecondary,
                ...baseFont,
              }}
            >
              A short description of this card with some preview text.
            </div>
          </div>
        </div>
      </Section>

      {/* 7. Badge / Tag */}
      <Section label="Badges" textSecondary={textSecondary}>
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
          {["Design", "UI/UX", "Style", "Modern"].map((tag) => (
            <span
              key={tag}
              style={{
                background: `${accentColor}22`,
                color: accentColor,
                padding: "3px 10px",
                borderRadius: "999px",
                fontSize: "11px",
                fontWeight: 500,
                ...baseFont,
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      </Section>

      {/* 8. Slider */}
      <Section label="Slider" textSecondary={textSecondary}>
        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "6px",
              fontSize: "11px",
              color: textSecondary,
            }}
          >
            <span>0</span>
            <span style={{ color: accentColor, fontWeight: 600 }}>
              {slider}
            </span>
            <span>100</span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            value={slider}
            onChange={(e) => setSlider(Number(e.target.value))}
            style={{
              width: "100%",
              accentColor,
              cursor: "pointer",
            }}
          />
        </div>
      </Section>

      {/* 9. Navigation Bar */}
      <Section label="Nav Bar" textSecondary={textSecondary}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            alignItems: "center",
            background: surfaceBg,
            borderRadius: halfRadius,
            padding: "8px 0",
            border: border || `1px solid ${borderColor}`,
          }}
        >
          <NavIcon
            label="Home"
            active
            accentColor={accentColor}
            textSecondary={textSecondary}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4"
          />
          <NavIcon
            label="Search"
            accentColor={accentColor}
            textSecondary={textSecondary}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
          <NavIcon
            label="Heart"
            accentColor={accentColor}
            textSecondary={textSecondary}
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
          <NavIcon
            label="Profile"
            accentColor={accentColor}
            textSecondary={textSecondary}
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
          />
        </div>
      </Section>
    </div>
  );
}

/* --- Sub-components --- */

function Section({
  label,
  textSecondary,
  children,
}: {
  label: string;
  textSecondary: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div
        style={{
          fontSize: "10px",
          fontWeight: 600,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: textSecondary,
          marginBottom: "6px",
        }}
      >
        {label}
      </div>
      {children}
    </div>
  );
}

function ToggleSwitch({
  on,
  onToggle,
  accentColor,
  borderRadius,
}: {
  on: boolean;
  onToggle: () => void;
  accentColor: string;
  borderRadius: string;
}) {
  const trackRadius =
    borderRadius && parseInt(borderRadius) > 20 ? "999px" : "12px";
  return (
    <button
      onClick={onToggle}
      style={{
        width: "44px",
        height: "24px",
        borderRadius: trackRadius,
        background: on ? accentColor : "rgba(128,128,128,0.3)",
        border: "none",
        position: "relative",
        cursor: "pointer",
        transition: "background 0.2s",
        flexShrink: 0,
      }}
    >
      <div
        style={{
          width: "18px",
          height: "18px",
          borderRadius: trackRadius,
          background: "#fff",
          position: "absolute",
          top: "3px",
          left: on ? "23px" : "3px",
          transition: "left 0.2s",
          boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
        }}
      />
    </button>
  );
}

function CheckboxItem({
  checked,
  onToggle,
  label,
  accentColor,
  halfRadius,
  textPrimary,
  baseFont,
}: {
  checked: boolean;
  onToggle: () => void;
  label: string;
  accentColor: string;
  halfRadius: string;
  textPrimary: string;
  baseFont: React.CSSProperties;
}) {
  return (
    <label
      style={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        cursor: "pointer",
        fontSize: "13px",
        color: textPrimary,
        ...baseFont,
      }}
    >
      <div
        onClick={(e) => {
          e.preventDefault();
          onToggle();
        }}
        style={{
          width: "18px",
          height: "18px",
          borderRadius: `min(${halfRadius}, 4px)`,
          border: checked
            ? `2px solid ${accentColor}`
            : "2px solid rgba(128,128,128,0.4)",
          background: checked ? accentColor : "transparent",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          transition: "all 0.15s",
          cursor: "pointer",
        }}
      >
        {checked && (
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#fff"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
      {label}
    </label>
  );
}

function RadioItem({
  selected,
  onSelect,
  label,
  accentColor,
  textPrimary,
  baseFont,
}: {
  selected: boolean;
  onSelect: () => void;
  label: string;
  accentColor: string;
  textPrimary: string;
  baseFont: React.CSSProperties;
}) {
  return (
    <label
      style={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        cursor: "pointer",
        fontSize: "13px",
        color: textPrimary,
        ...baseFont,
      }}
      onClick={(e) => {
        e.preventDefault();
        onSelect();
      }}
    >
      <div
        style={{
          width: "18px",
          height: "18px",
          borderRadius: "50%",
          border: selected
            ? `2px solid ${accentColor}`
            : "2px solid rgba(128,128,128,0.4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          transition: "all 0.15s",
        }}
      >
        {selected && (
          <div
            style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: accentColor,
            }}
          />
        )}
      </div>
      {label}
    </label>
  );
}

function NavIcon({
  label,
  active,
  accentColor,
  textSecondary,
  d,
}: {
  label: string;
  active?: boolean;
  accentColor: string;
  textSecondary: string;
  d: string;
}) {
  const color = active ? accentColor : textSecondary;
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "2px",
      }}
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d={d} />
      </svg>
      <span style={{ fontSize: "9px", color }}>{label}</span>
    </div>
  );
}
