import React from 'react';

export const PageTransition = ({ children }) => {
  return (
    <div className="animate-fadeIn">
      {children}
    </div>
  );
};

// Add this to your CSS or tailwind config for the animation
// @keyframes fadeIn {
//   from { opacity: 0; transform: translateY(10px); }
//   to { opacity: 1; transform: translateY(0); }
// }
