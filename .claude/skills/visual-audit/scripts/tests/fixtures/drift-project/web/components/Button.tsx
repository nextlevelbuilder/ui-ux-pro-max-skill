// FIXTURE: canonical web button (clean). Participates in component.duplicate-implementation
// together with CtaButton.tsx. Icon import: lucide-react (icon.mixed-libraries with CtaButton.tsx).
import React from 'react';
import { ArrowRight } from 'lucide-react';

type Props = { label: string; onClick: () => void };

export function Button({ label, onClick }: Props) {
  return (
    <button className="btn-primary" onClick={onClick}>
      {label}
      <ArrowRight size={20} />
    </button>
  );
}
