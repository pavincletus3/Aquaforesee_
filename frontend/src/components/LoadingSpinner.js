import React from "react";
import { Loader2 } from "lucide-react";

const LoadingSpinner = ({
  size = "medium",
  message = "Loading...",
  className = "",
}) => {
  const sizeClasses = {
    small: "w-4 h-4",
    medium: "w-6 h-6",
    large: "w-8 h-8",
  };

  const textSizeClasses = {
    small: "text-sm",
    medium: "text-base",
    large: "text-lg",
  };

  return (
    <div
      className={`flex flex-col items-center justify-center space-y-2 ${className}`}
    >
      <Loader2
        className={`${sizeClasses[size]} animate-spin text-primary-600`}
      />
      {message && (
        <p className={`${textSizeClasses[size]} text-gray-600 animate-pulse`}>
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;
