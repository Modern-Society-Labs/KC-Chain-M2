/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      'xs': '475px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
    extend: {
      colors: {
        // Locale Network Ecosystem Colors (matching ecosystem design)
        'locale-blue': '#3b82f6',
        'locale-blue-dark': '#2563eb',
        'locale-purple': '#8b5cf6',
        'locale-indigo': '#3b82f6',
        'locale-gray': '#64748b',
        'locale-gray-light': '#f1f5f9',
        'locale-gray-dark': '#334155',
        'locale-bg': '#f8fafc',
        
        // Accent Colors
        'accent-cyan': '#06b6d4',
        'accent-green': '#10b981',
        'accent-yellow': '#f59e0b',
        'accent-purple': '#8b5cf6',
        
        // Status Colors
        'status-success': '#10b981',
        'status-warning': '#f59e0b',
        'status-error': '#ef4444',
        'status-info': '#3b82f6',
        
        // Device status colors (updated)
        'device-active': '#10b981',
        'device-idle': '#06b6d4',
        'device-error': '#ef4444',
        'device-offline': '#64748b',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['IBM Plex Mono', 'Consolas', 'monospace'],
      },
      fontSize: {
        'h1': ['36px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['24px', { lineHeight: '1.3', fontWeight: '500' }],
        'body': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
        'caption': ['12px', { lineHeight: '1.4', fontWeight: '300' }],
      },
      borderRadius: {
        'locale': '8px',
        'card': '12px',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'locale': '0 2px 8px rgba(59, 130, 246, 0.1)',
        'device-active': '0 0 20px rgba(16, 185, 129, 0.3)',
      },
      animation: {
        'data-flow': 'dataFlow 1s ease-in-out infinite alternate',
        'wave': 'wave 2s ease-in-out infinite',
      },
      keyframes: {
        dataFlow: {
          '0%': { opacity: '0.5', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        wave: {
          '0%, 100%': { transform: 'scaleY(1)' },
          '50%': { transform: 'scaleY(1.1)' },
        }
      },
      backgroundImage: {
        'locale-gradient': 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
        'hero-gradient': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        'card-gradient': 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        'data-gradient': 'linear-gradient(135deg, #06b6d4 0%, #10b981 100%)',
        'community-gradient': 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
      }
    },
  },
  plugins: [],
} 