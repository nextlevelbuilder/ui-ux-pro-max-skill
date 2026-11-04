// FIXTURE: duplicate of Button.tsx with a different body + Tailwind arbitrary values.
import React from 'react';
import { ChevronRightIcon } from '@heroicons/react/24/solid'; // icon.mixed-libraries (lucide + heroicons)

export const CtaButton = ({ label, onClick }: { label: string; onClick: () => void }) => (
  <button
    onClick={onClick}
    className="rounded-[7px] bg-[#1E88E5] text-[15px] px-[18px] text-white" // radius 7, color #1E88E5, font 15, spacing 18
    style={{ transitionDuration: '337ms', color: '#FFFFFF' }} // duration 337; #FFFFFF is in palette
  >
    {label}
    <ChevronRightIcon className="h-5 w-5" />
  </button>
);
