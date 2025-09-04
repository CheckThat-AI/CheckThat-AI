import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface MaintenanceBannerProps {
  className?: string;
}

export const MaintenanceBanner: React.FC<MaintenanceBannerProps> = ({ 
  className = "" 
}) => {
  return (
    <div className={`bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-4 ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="text-amber-800 dark:text-amber-200 font-medium mb-1">
            Temporary Maintenance Notice
          </p>
          <p className="text-amber-700 dark:text-amber-300 leading-relaxed">
            Our backend infrastructure is under active migration to a postgres database. 
            Please check back in 24hrs. We apologize for the inconvenience. 
            Meanwhile try our <span className="font-semibold">Guest mode</span> with access to free models.
          </p>
        </div>
      </div>
    </div>
  );
};
