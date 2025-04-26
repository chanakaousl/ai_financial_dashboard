/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#0284c7',
                    700: '#0369a1',
                    800: '#075985',
                    900: '#0c4a6e',
                    950: '#082f49',
                },
                finance: {
                    green: '#10B981',
                    red: '#EF4444',
                    blue: '#3B82F6',
                    yellow: '#F59E0B',
                    purple: '#8B5CF6',
                },
            },
            fontFamily: {
                sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
            },
            borderRadius: {
                'xl': '0.75rem',
                '2xl': '1rem',
                '3xl': '1.5rem',
            },
            boxShadow: {
                card: '0 2px 5px 0 rgba(0, 0, 0, 0.05)',
                'card-hover': '0 4px 15px 0 rgba(0, 0, 0, 0.1)',
                'card-dark': '0 2px 5px 0 rgba(0, 0, 0, 0.3)',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
        },
    },
    plugins: [],
} 