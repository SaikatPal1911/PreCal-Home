import React from 'react';
import { Link } from 'react-router-dom';

interface BrandLogoProps {
  size?: 'sm' | 'md' | 'lg';
  inverse?: boolean;
  className?: string;
}

const sizes = {
  sm: { icon: 'w-6 h-6 rounded-md', text: 'text-base' },
  md: { icon: 'w-8 h-8 rounded-lg', text: 'text-xl' },
  lg: { icon: 'w-9 h-9 rounded-xl', text: 'text-2xl' },
};

export const BrandLogo: React.FC<BrandLogoProps> = ({ size = 'md', inverse = false, className = '' }) => {
  const scale = sizes[size];
  const textColor = inverse ? 'text-white' : 'text-charcoal-800';
  const accentColor = inverse ? 'text-sage-400' : 'text-sage-600';

  return (
    <Link to="/" className={`flex items-center gap-2 ${className}`} aria-label="PreCal Home">
      <img src="/precal-mark.svg" alt="" className={`${scale.icon} flex-shrink-0`} />
      <span className={`font-display font-bold ${scale.text} ${textColor}`}>
        PreCal <span className={accentColor}>Home</span>
      </span>
    </Link>
  );
};