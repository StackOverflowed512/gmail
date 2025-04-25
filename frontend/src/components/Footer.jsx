import React from 'react';
import branding from '../config/branding'; // Create this config file

function Footer() {
  return (
    <footer className="bg-[#181818] text-[#B3B3B3] py-4 mt-auto">
      <div className="container mx-auto px-4">
        <div className="border-t border-[#333333] pt-4 flex flex-col items-center gap-2 text-sm">
          {/* Logo placeholder - will be shown when branding.logoPath is set */}
          {branding.logoPath && (
            <img 
              src={branding.logoPath}
              alt={`${branding.companyName} Logo`}
              className="h-8 mb-2"
            />
          )}
          
          {/* Company information */}
          <div className="text-center">
            <span className="text-[#FFFFFF] font-medium">
              {branding.companyName}
            </span>
            <div className="text-xs mt-1">
              {branding.legalText && (
                <span className="block">{branding.legalText}</span>
              )}
              <a 
                href={branding.websiteUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-[#FFFFFF] transition-colors"
              >
                {branding.websiteDisplay}
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;